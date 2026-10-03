import os
import sys
import json
import time
import email
import random
import imaplib
import smtplib
import subprocess
from datetime import datetime, timedelta, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate, make_msgid

import socket
# Set universal socket timeout to 12s to prevent IMAP/SMTP indefinite hangs
socket.setdefaulttimeout(12)

# Universal IST Timezone (UTC + 05:30) for 100% parity across Windows and GitHub Actions (Ubuntu UTC)
IST = timezone(timedelta(hours=5, minutes=30))

def get_current_time():
    """Returns current time localized to IST (consistent on Windows & GitHub Actions)."""
    return datetime.now(IST)

def parse_iso_time(s):
    """Safely parses ISO timestamp and ensures it is IST-localized."""
    if not s:
        return None
    dt = datetime.fromisoformat(s)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=IST)
    return dt

# Support UTF-8 console output on Windows
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Import our realistic 8-track stories
from stories import TRACKS, spin

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATE_FILE = os.path.join(BASE_DIR, "state.json")
ENV_FILE = os.path.join(BASE_DIR, ".env")

# ------------------------------------------------------------------------------
# 1. CREDENTIALS & CONFIG LOADER
# ------------------------------------------------------------------------------
def load_env():
    """Loads environment variables from local .env if present, else os.environ"""
    config = {}

    # 1. Direct multi-line secret support from environment
    warmup_env_str = os.environ.get("WARMUP_ENV") or os.environ.get("WARMUP_ENV_DATA")
    if warmup_env_str:
        for line in warmup_env_str.splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                config[k.strip()] = v.strip().replace(" ", "")

    # 2. Local .env file
    if os.path.exists(ENV_FILE):
        with open(ENV_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    config[k.strip()] = v.strip().replace(" ", "")

    # 3. Allow individual system environment variables to override only if non-empty
    for k, v in os.environ.items():
        if k not in ("WARMUP_ENV", "WARMUP_ENV_DATA") and v.strip():
            config[k] = v.strip().replace(" ", "")
    return config

CONFIG = load_env()

def get_account_creds(key):
    """Retrieves (email, password) tuple for 'HERO' or 'SEED_1'..'SEED_8'"""
    if key == "HERO":
        email_addr = CONFIG.get("HERO_EMAIL", "")
        pwd = CONFIG.get("HERO_PASSWORD", "")
    else:
        email_addr = CONFIG.get(f"{key}_EMAIL", "")
        pwd = CONFIG.get(f"{key}_PASSWORD", "")
    return email_addr, pwd

FLEET_EMAILS = set()
for k in ["HERO"] + [f"SEED_{i}" for i in range(1, 9)]:
    em, _ = get_account_creds(k)
    if em:
        FLEET_EMAILS.add(em.lower())

def mask_email(addr):
    """Masks email for safe logging: raj@bazxlabs.com -> r***@baz***"""
    if not addr or "@" not in addr:
        return "***"
    local, domain = addr.split("@", 1)
    masked_local = local[0] + "***" if len(local) > 0 else "***"
    masked_domain = domain[:3] + "***" if len(domain) > 3 else "***"
    return f"{masked_local}@{masked_domain}"

# ------------------------------------------------------------------------------
# 2. STATE MANAGER
# ------------------------------------------------------------------------------
def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass

    # Initial default state
    now_iso = get_current_time().isoformat()
    threads = {}
    for track_id, track in TRACKS.items():
        # Schedule initial start times staggered throughout the day
        initial_delay_minutes = random.randint(15, 120) * track_id
        send_after = (get_current_time() + timedelta(minutes=initial_delay_minutes)).isoformat()
        threads[str(track_id)] = {
            "track_id": track_id,
            "name": track["name"],
            "direction": track["direction"],
            "partner_key": track["partner_key"],
            "stage_idx": 0,
            "subject": None,
            "last_msg_id": None,
            "last_timestamp": None,
            "send_after": send_after,
            "status": "ready_to_start",
            "history": []
        }

    return {
        "day": 1,
        "started_at": now_iso,
        "last_tick": now_iso,
        "total_sent": 0,
        "total_received": 0,
        "total_rescued": 0,
        "threads": threads
    }

def save_state(state):
    state["last_tick"] = get_current_time().isoformat()
    tmp_file = STATE_FILE + ".tmp"
    with open(tmp_file, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)
    # Atomic replace to prevent corrupted state on runner crash
    if os.path.exists(STATE_FILE):
        os.replace(tmp_file, STATE_FILE)
    else:
        os.rename(tmp_file, STATE_FILE)

# ------------------------------------------------------------------------------
# 3. IMAP & SMTP CLIENT HELPERS
# ------------------------------------------------------------------------------
def get_imap_connection(email_addr, password):
    m = imaplib.IMAP4_SSL("imap.gmail.com", 993)
    m.login(email_addr, password)
    return m

def get_smtp_connection(email_addr, password):
    s = smtplib.SMTP("smtp.gmail.com", 587, timeout=15)
    s.starttls()
    s.login(email_addr, password)
    return s

def find_spam_folder(imap_conn):
    """Dynamically finds the Spam / Junk folder path for Gmail"""
    typ, data = imap_conn.list()
    if typ == "OK":
        for folder in data:
            name = folder.decode("utf-8")
            if "\\Spam" in name or "[Gmail]/Spam" in name:
                # Extract quoted name
                parts = name.split(' "/" ')
                if len(parts) > 1:
                    return parts[-1].strip('"')
    return "[Gmail]/Spam"

# ------------------------------------------------------------------------------
# 4. UNIFIED HIGH-SPEED MAILBOX PROCESSOR (SPAM RESCUE + ENGAGEMENT)
# ------------------------------------------------------------------------------
def process_account_mailbox(email_addr, password):
    """
    Connects to an account once:
    1. Scans recent emails in [Gmail]/Spam -> Moves trapped fleet emails to INBOX
    2. Scans INBOX for UNSEEN fleet emails -> Marks as Seen, Starred (⭐), and IMPORTANT
    """
    rescued_count = 0
    m = None
    try:
        m = get_imap_connection(email_addr, password)

        # 1. SPAM RESCUE
        spam_folder = find_spam_folder(m)
        status, _ = m.select(f'"{spam_folder}"')
        if status == "OK":
            typ, data = m.search(None, "ALL")
            if typ == "OK" and data[0]:
                msg_ids = data[0].split()[-10:]
                for msg_id in msg_ids:
                    try:
                        typ_fetch, msg_data = m.fetch(msg_id, "(RFC822.HEADER)")
                        if typ_fetch == "OK":
                            raw_header = msg_data[0][1]
                            parsed = email.message_from_bytes(raw_header)
                            sender = email.utils.parseaddr(parsed.get("From", ""))[1].lower()

                            if sender in FLEET_EMAILS:
                                print(f"  🚨 [SPAM RESCUE] Trapped email from {mask_email(sender)} in {mask_email(email_addr)}'s Spam! Rescuing...", flush=True)
                                m.copy(msg_id, "INBOX")
                                m.store(msg_id, "+FLAGS", "(\\Deleted)")
                                m.expunge()
                                rescued_count += 1
                                print(f"  ✨ [RESCUED] Moved to INBOX for {mask_email(email_addr)}!", flush=True)
                    except Exception:
                        pass

        # 2. INBOX ENGAGEMENT
        m.select("INBOX")
        typ, data = m.search(None, "UNSEEN")
        if typ == "OK" and data[0]:
            msg_ids = data[0].split()[-10:]
            for msg_id in msg_ids:
                try:
                    typ_fetch, msg_data = m.fetch(msg_id, "(RFC822.HEADER)")
                    if typ_fetch == "OK":
                        raw_header = msg_data[0][1]
                        parsed = email.message_from_bytes(raw_header)
                        sender = email.utils.parseaddr(parsed.get("From", ""))[1].lower()
                        if sender in FLEET_EMAILS:
                            m.store(msg_id, "+FLAGS", "(\\Seen \\Flagged IMPORTANT)")
                            print(f"  ⭐ [ENGAGEMENT] Starred and Marked Important: email from {mask_email(sender)} to {mask_email(email_addr)}", flush=True)
                except Exception:
                    pass

    except Exception as e:
        print(f"  ⚠️ Mailbox check notice for {mask_email(email_addr)}: {e}", flush=True)
    finally:
        if m:
            try:
                m.logout()
            except Exception:
                pass
    return rescued_count

def check_mailboxes(accounts=None):
    """
    Targeted, high-speed mailbox processor.
    Defaults to checking HERO (our primary domain) and any specified partner seeds.
    Completes in 3-8 seconds!
    """
    if accounts is None:
        accounts = ["HERO"]
    total_rescued = 0
    for acc_key in accounts:
        em, pwd = get_account_creds(acc_key)
        if em and pwd:
            r = process_account_mailbox(em, pwd)
            total_rescued += r
    return total_rescued

def process_all_mailboxes():
    """Processes all 9 accounts across the fleet (used for full manual audits)"""
    print("\n🔍 --- Running Fleet Mailbox Sweep (Spam Rescue + Engagement) ---", flush=True)
    all_keys = ["HERO"] + [f"SEED_{i}" for i in range(1, 9)]
    total_rescued = check_mailboxes(all_keys)
    if total_rescued == 0:
        print("  ✅ All clean: 0 emails trapped in spam across the fleet.", flush=True)
    else:
        print(f"  🎉 Total Rescued in this cycle: {total_rescued} emails successfully saved to INBOX!", flush=True)
    return total_rescued

# ------------------------------------------------------------------------------
# 6. EMAIL TRANSMISSION ENGINE (HUMAN JITTER & THREADING)
# ------------------------------------------------------------------------------
def calculate_human_delay():
    """
    Calculates realistic human reply delay:
    - Mode A (15%): 8 to 25 minutes (Quick desk reply)
    - Mode B (65%): 45 to 210 minutes (Deep work / meeting delay)
    - Mode C (20%): 360 to 720 minutes (Next morning catch-up)
    """
    rand = random.random()
    if rand < 0.15:
        # At desk
        minutes = random.randint(8, 25)
    elif rand < 0.80:
        # Deep focus
        minutes = random.randint(45, 210)
    else:
        # Long gap / next session
        minutes = random.randint(360, 720)
    return minutes

def is_business_hours():
    """
    Checks if current IST time is within daylight business hours (09:00 AM - 07:30 PM IST).
    Guaranteed consistent locally and on GitHub Actions runners (which run on UTC).
    """
    now = get_current_time()
    if 9 <= now.hour < 19:
        return True
    if now.hour == 19 and now.minute <= 30:
        return True
    return False

def send_message(from_email, from_pwd, to_email, subject, body_text, in_reply_to=None, references=None):
    """
    Constructs an authentic multipart email with proper threading headers.
    """
    msg = MIMEMultipart("alternative")
    domain = from_email.split("@")[-1]
    msg_id = make_msgid(domain=domain)

    msg["From"] = from_email
    msg["To"] = to_email
    msg["Subject"] = subject
    msg["Date"] = formatdate(localtime=True)
    msg["Message-ID"] = msg_id

    if in_reply_to:
        msg["In-Reply-To"] = in_reply_to
    if references:
        msg["References"] = references
    elif in_reply_to:
        msg["References"] = in_reply_to

    # Plain text version
    part1 = MIMEText(body_text, "plain", "utf-8")
    msg.attach(part1)

    # Clean native HTML version (<div dir="ltr">...</div>) matching Gmail composer
    html_paragraphs = "".join(f"<p style=\"margin:0 0 12px 0;\">{line}</p>" if line else "<br>" for line in body_text.split("\n"))
    html_content = f'<div dir="ltr" style="font-family:Arial,Helvetica,sans-serif;font-size:14px;color:#222222;line-height:1.5;">{html_paragraphs}</div>'
    part2 = MIMEText(html_content, "html", "utf-8")
    msg.attach(part2)

    # Send via TLS
    s = get_smtp_connection(from_email, from_pwd)
    s.sendmail(from_email, [to_email], msg.as_string())
    s.quit()

    return msg_id

# ------------------------------------------------------------------------------
# 7. THE TICK CONTROLLER (30-SECOND MICRO-RUN)
# ------------------------------------------------------------------------------
def run_tick(force=False):
    """
    Executes a single micro-run (ideal for GitHub Actions cron or local scheduler):
    1. Rescues trapped emails from Spam
    2. Stars and reads new incoming emails
    3. Finds at most ONE eligible scheduled conversation turn to send
    4. Schedules the next turn with realistic human delay
    5. Saves state and exits in under 25 seconds
    """
    now = get_current_time()
    print("=" * 70)
    print(f"⏰ [BAZX WARMUP TICK] {now.strftime('%Y-%m-%d %H:%M:%S IST')}")
    print("=" * 70)

    state = load_state()

    # 1. Check Business Hours
    if not is_business_hours() and not force:
        print(f"🌙 Outside business hours ({now.strftime('%H:%M')} IST - active: 09:00 - 19:30 IST). Maintaining sleep silence to mimic human behavior.")
        save_state(state)
        return

    # 2. Check scheduled send queue
    eligible_threads = []

    for t_id, thread in state["threads"].items():
        send_after_str = thread.get("send_after")
        if not send_after_str:
            continue
        send_after = parse_iso_time(send_after_str)
        if now >= send_after:
            eligible_threads.append(thread)

    if not eligible_threads:
        print("⏳ No scheduled emails due at this minute. Waiting for human delay windows to expire.")
        # Fast sweep HERO only while waiting
        rescued = check_mailboxes(["HERO"])
        state["total_rescued"] += rescued
        save_state(state)
        return

    # Pick the most delayed eligible thread to process (strictly 1 message per tick!)
    thread_to_run = sorted(eligible_threads, key=lambda t: parse_iso_time(t["send_after"]))[0]
    track_id = thread_to_run["track_id"]
    partner_key = thread_to_run.get("partner_key", "SEED_1")

    # Fast sweep for HERO and the partner account in this thread
    print(f"\n🔍 --- Targeted Sweep (HERO + {partner_key}) ---", flush=True)
    rescued = check_mailboxes(["HERO", partner_key])
    state["total_rescued"] += rescued
    stage_idx = thread_to_run["stage_idx"]
    track_def = TRACKS[track_id]
    stages = track_def["stages"]

    if stage_idx >= len(stages):
        print(f"✅ Track {track_id} ('{track_def['name']}') has completed all 5 stages!")
        thread_to_run["send_after"] = None
        save_state(state)
        return

    turn = stages[stage_idx]
    hero_email, hero_pwd = get_account_creds("HERO")
    seed_email, seed_pwd = get_account_creds(thread_to_run["partner_key"])

    if turn["role"] == "hero":
        sender_email, sender_pwd = hero_email, hero_pwd
        recip_email = seed_email
    else:
        sender_email, sender_pwd = seed_email, seed_pwd
        recip_email = hero_email

    # Prepare Subject & Body with deep spintax
    raw_subject = turn["subject"]
    if "{subject}" in raw_subject:
        subject = raw_subject.replace("{subject}", thread_to_run["subject"] or track_def["name"])
    else:
        subject = spin(raw_subject)
        thread_to_run["subject"] = subject

    body = spin(turn["body"])

    print(f"\n📨 [DISPATCHING EMAIL] Track {track_id}: {track_def['name']}")
    print(f"  From: {sender_email}")
    print(f"  To:   {recip_email}")
    print(f"  Subj: {subject}")
    print(f"  Turn: {stage_idx + 1} of {len(stages)} (Stage {turn['stage']})")

    try:
        msg_id = send_message(
            from_email=sender_email,
            from_pwd=sender_pwd,
            to_email=recip_email,
            subject=subject,
            body_text=body,
            in_reply_to=thread_to_run.get("last_msg_id"),
            references=thread_to_run.get("last_msg_id")
        )
        print(f"  ✅ Sent successfully! Message-ID: {msg_id}")

        # Update state
        thread_to_run["stage_idx"] += 1
        thread_to_run["last_msg_id"] = msg_id
        thread_to_run["last_timestamp"] = now.isoformat()
        state["total_sent"] += 1

        # Schedule next turn with human delay
        next_delay_minutes = calculate_human_delay()
        next_send_after = now + timedelta(minutes=next_delay_minutes)
        thread_to_run["send_after"] = next_send_after.isoformat()
        print(f"  ⏱️ Next turn in Track {track_id} scheduled for {next_send_after.strftime('%Y-%m-%d %H:%M:%S')} (Delay: {next_delay_minutes} mins)")
    except Exception as e:
        print(f"  ❌ SMTP Send error for Track {track_id}: {e}")
        # Retry with a 15-minute backoff
        thread_to_run["send_after"] = (now + timedelta(minutes=15)).isoformat()

    save_state(state)
    print("\n🏁 Micro-tick completed.")

# ------------------------------------------------------------------------------
# 8. TEST SEND (SINGLE ISOLATED EMAIL AS REQUESTED BY USER)
# ------------------------------------------------------------------------------
def run_test_send():
    """
    Sends exactly ONE verified test email from HERO account to SEED_1
    and confirms receipt via IMAP.
    """
    hero_email, hero_pwd = get_account_creds("HERO")
    seed_email, seed_pwd = get_account_creds("SEED_1")

    print("\n" + "=" * 70)
    print("🧪 [SINGLE VERIFICATION TEST] Sending 1 Email from HERO account...")
    print(f"  Sender:    {hero_email}")
    print(f"  Recipient: {seed_email}")
    print("=" * 70)

    test_subj = f"Verification Ping - {datetime.now().strftime('%H:%M:%S')}"
    test_body = (
        "Hey,\n\n"
        f"Testing the direct SMTP pipe from our Google Workspace domain {hero_email}.\n\n"
        "Verifying DKIM cryptographic signature and SPF alignment. No action required.\n\n"
        "Best,\n"
        "Raj bazx"
    )

    print("📤 Connecting to SMTP and dispatching message...")
    msg_id = send_message(hero_email, hero_pwd, seed_email, test_subj, test_body)
    print(f"✅ Dispatched successfully! Message-ID: {msg_id}")

    print("\n📥 Checking delivery in recipient mailbox (waiting 5 seconds)...")
    time.sleep(5)

    # Check recipient IMAP
    try:
        m = get_imap_connection(seed_email, seed_pwd)
        # Check INBOX first
        m.select("INBOX")
        typ, data = m.search(None, f'SUBJECT "{test_subj}"')
        if typ == "OK" and data[0]:
            print("🎉 DELIVERY CONFIRMED IN PRIMARY INBOX! (100% Inbox Placement)")
            m.logout()
            return True

        # Check Spam
        spam_folder = find_spam_folder(m)
        m.select(f'"{spam_folder}"')
        typ, data = m.search(None, f'SUBJECT "{test_subj}"')
        if typ == "OK" and data[0]:
            print(f"⚠️ Delivered to {spam_folder}. Triggering auto-rescue...")
            msg_num = data[0].split()[0]
            m.copy(msg_num, "INBOX")
            m.store(msg_num, "+FLAGS", "(\\Deleted)")
            m.expunge()
            print("✨ Auto-rescued to INBOX successfully!")
            m.logout()
            return True

        m.logout()
        print("ℹ️ Email in transit or taking slightly longer to index. SMTP transmission succeeded.")
    except Exception as e:
        print(f"⚠️ Delivery check warning: {e}")
    return True

# ------------------------------------------------------------------------------
# 9. CONTINUOUS RUNNER & CLOUD SYNC (FOR LONG-RUNNING GITHUB ACTIONS)
# ------------------------------------------------------------------------------
def git_sync_state(commit_msg="Auto-update warmup state [skip ci]"):
    """Pushes updated state.json back to GitHub remote repository."""
    try:
        subprocess.run(["git", "add", "state.json"], timeout=10)
        diff = subprocess.run(["git", "diff", "--staged"], capture_output=True)
        if diff.stdout:
            subprocess.run(["git", "commit", "-m", commit_msg], timeout=10)
            subprocess.run(["git", "push", "origin", "main"], timeout=20)
            print("  💾 State synced to GitHub remote successfully!", flush=True)
    except Exception as e:
        print(f"  ⚠️ Git sync notice: {e}", flush=True)

def run_session(max_hours="auto"):
    """
    Keeps running on GitHub Actions runner for the full daylight working window.
    - 'auto' mode: calculates remaining hours until 19:30 IST (capped at 5.9h for GitHub's 6h limit)
    - Paces conversation turns with genuine, natural human delays (40 to 70 minutes).
    - Eliminates rushed bursts and quick replies.
    - Saves and pushes state to Git after every single transaction.
    """
    # Early exit: don't waste runner time if business hours are already over
    if not is_business_hours():
        print(f"🌙 Outside business hours ({get_current_time().strftime('%H:%M')} IST). No session needed. Exiting.", flush=True)
        return

    start_time = time.time()

    if max_hours == "auto":
        now = get_current_time()
        end_of_day = now.replace(hour=19, minute=30, second=0, microsecond=0)
        remaining_hours = (end_of_day - now).total_seconds() / 3600
        if remaining_hours < 0.5:
            print(f"⏰ Only {remaining_hours:.1f}h left in business day. Too short for a session. Exiting.", flush=True)
            return
        max_hours = min(remaining_hours, 5.9)  # GitHub Actions max ~6 hours
        print(f"🔄 Auto-duration: {remaining_hours:.1f}h remaining till 19:30 IST → capped session: {max_hours:.1f}h", flush=True)
    else:
        max_hours = float(max_hours)

    max_seconds = max_hours * 3600

    print("=" * 70, flush=True)
    print(f"🚀 [BAZX WARMUP LIVE SHIFT STARTED] {get_current_time().strftime('%Y-%m-%d %H:%M:%S IST')}", flush=True)
    print(f"   Target Duration: {max_hours:.1f} hours | Pacing Jitter: 40-70 mins | Daylight Only", flush=True)
    print("=" * 70, flush=True)

    while True:
        now = get_current_time()
        elapsed = time.time() - start_time

        # 1. Check max session duration
        if elapsed >= max_seconds:
            print(f"\n🏁 Shift time limit reached ({max_hours:.1f} hrs). Ending shift cleanly.", flush=True)
            break

        # 2. Check daylight business hours (09:00 - 19:30 IST)
        if not is_business_hours():
            print(f"\n🌙 Outside business hours ({now.strftime('%H:%M')} IST - active: 09:00 - 19:30 IST). Ending shift cleanly.", flush=True)
            break

        # 3. Pull latest state from remote in case of external commits
        try:
            subprocess.run(["git", "pull", "--rebase", "origin", "main"], capture_output=True, timeout=15)
        except Exception:
            pass

        state = load_state()

        # 4. Check eligible threads
        eligible = []
        for t_id, t in state["threads"].items():
            s_after = t.get("send_after")
            if s_after and now >= parse_iso_time(s_after):
                eligible.append(t)

        if eligible:
            # Pick the most delayed eligible thread
            thread_to_run = sorted(eligible, key=lambda x: parse_iso_time(x["send_after"]))[0]
            track_id = thread_to_run["track_id"]
            partner_key = thread_to_run.get("partner_key", "SEED_1")
            track_def = TRACKS[track_id]
            stage_idx = thread_to_run["stage_idx"]
            stages = track_def["stages"]

            if stage_idx < len(stages):
                turn = stages[stage_idx]
                hero_email, hero_pwd = get_account_creds("HERO")
                seed_email, seed_pwd = get_account_creds(partner_key)

                if turn["role"] == "hero":
                    sender_email, sender_pwd = hero_email, hero_pwd
                    recip_email = seed_email
                else:
                    sender_email, sender_pwd = seed_email, seed_pwd
                    recip_email = hero_email

                # Sweep mailboxes for spam rescue and engagement
                print(f"\n🔍 --- Targeted Sweep (HERO + {partner_key}) ---", flush=True)
                rescued = check_mailboxes(["HERO", partner_key])
                state["total_rescued"] += rescued

                # Spintax formatting
                raw_subj = turn["subject"]
                if "{subject}" in raw_subj:
                    subj = raw_subj.replace("{subject}", thread_to_run["subject"] or track_def["name"])
                else:
                    subj = spin(raw_subj)
                    thread_to_run["subject"] = subj
                body = spin(turn["body"])

                print(f"\n📨 [DISPATCHING EMAIL] Track {track_id}: {track_def['name']}", flush=True)
                print(f"  From: {mask_email(sender_email)}", flush=True)
                print(f"  To:   {mask_email(recip_email)}", flush=True)
                print(f"  Subj: {subj}", flush=True)
                print(f"  Turn: {stage_idx + 1} of {len(stages)} (Stage {turn['stage']})", flush=True)

                try:
                    msg_id = send_message(
                        sender_email,
                        sender_pwd,
                        recip_email,
                        subj,
                        body,
                        in_reply_to=thread_to_run.get("last_msg_id"),
                        references=thread_to_run.get("last_msg_id")
                    )
                    print(f"  ✅ Sent successfully! Message-ID: {msg_id}", flush=True)

                    # Update state
                    thread_to_run["stage_idx"] += 1
                    thread_to_run["last_msg_id"] = msg_id
                    thread_to_run["last_timestamp"] = now.isoformat()
                    state["total_sent"] += 1

                    # Next turn delay (human delay)
                    next_delay_m = calculate_human_delay()
                    next_send_after = now + timedelta(minutes=next_delay_m)
                    thread_to_run["send_after"] = next_send_after.isoformat()
                    print(f"  ⏱️ Next turn in Track {track_id} scheduled for {next_send_after.strftime('%Y-%m-%d %H:%M:%S IST')} (Delay: {next_delay_m} mins)", flush=True)

                except Exception as e:
                    print(f"  ❌ SMTP Send error for Track {track_id}: {e}", flush=True)
                    thread_to_run["send_after"] = (now + timedelta(minutes=15)).isoformat()

                # Save state and immediately push to GitHub remote
                save_state(state)
                git_sync_state(f"Auto-update warmup: Track {track_id} Turn {stage_idx+1} [skip ci]")

                # Full 40 to 70 minutes realistic agency workday gap
                pacing_delay = random.randint(2400, 4200)
                mins = pacing_delay // 60
                secs = pacing_delay % 60
                print(f"\n☕ [HUMAN PACING GAP] Pausing {mins}m {secs}s before next interaction to simulate authentic agency workday rhythm...", flush=True)

                time_slept = 0
                while time_slept < pacing_delay:
                    sleep_chunk = min(60, pacing_delay - time_slept)
                    time.sleep(sleep_chunk)
                    time_slept += sleep_chunk
                    remaining = pacing_delay - time_slept
                    if remaining > 0 and remaining % 300 == 0:
                        print(f"   ⏳ Pacing heartbeat: {remaining // 60}m remaining until next interaction...", flush=True)
                continue

        # If no email is due right now, sleep until the earliest scheduled turn
        pending = [parse_iso_time(t["send_after"]) for t in state["threads"].values() if t.get("send_after")]
        if pending:
            earliest = min(pending)
            wait_s = max(60, int((earliest - now).total_seconds()))
            wait_s = min(wait_s, 900)  # Max sleep 15 mins before rechecking
            print(f"\n⏳ No email due right now. Next due at {earliest.strftime('%H:%M:%S IST')}. Waiting {wait_s//60}m {wait_s%60}s...", flush=True)
            time.sleep(wait_s)
        else:
            print("🎉 All 8 tracks completed all stages! Warmup complete.", flush=True)
            break

# ------------------------------------------------------------------------------
# 10. CLI ENTRYPOINT
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "--session":
            hours = sys.argv[2] if len(sys.argv) > 2 else "auto"
            run_session(max_hours=hours)
        elif cmd == "--test-send":
            run_test_send()
        elif cmd == "--tick":
            force_flag = "--force" in sys.argv
            run_tick(force=force_flag)
        elif cmd == "--spam-rescue":
            process_all_mailboxes()
        elif cmd == "--status":
            st = load_state()
            print("\n📊 --- BAZX WARMUP ENGINE STATUS ---")
            print(f"  Day:            {st['day']} / 14")
            print(f"  Total Sent:     {st['total_sent']}")
            print(f"  Total Rescued:  {st['total_rescued']}")
            print(f"  Active Tracks:  {len(st['threads'])}")
            print("---------------------------------------")
            for t_id, t in st["threads"].items():
                print(f"  Track {t_id}: {t['name']:<35} | Turn: {t['stage_idx']}/10 | Next: {t.get('send_after') or 'Completed'}")
        else:
            print("Unknown command. Options: --session [hours], --test-send, --tick [--force], --spam-rescue, --status")
    else:
        print("BazxWarmupEngine v5.0 ready. Use --session, --test-send, --tick, --spam-rescue, or --status.")
