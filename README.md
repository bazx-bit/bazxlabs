# 14-Day Elite Warmup Engine (v5.0)

A bespoke, peer-to-peer email warmup system designed for custom Google Workspace domains to achieve and sustain **100% Inbox Deliverability** before launching outbound cold outreach.

---

## 📧 Active Fleet & Project Network (8 Peer Tracks)

The warmup engine operates an authenticated peer-to-peer network across 9 distinct Google mailboxes. Each seed account pairs with the hero domain on a realistic, multi-turn technical engineering project:

| # | Fleet Identifier | Account Role | Project Topic / Engineering Track | Direction |
| :--- | :--- | :--- | :--- | :--- |
| **0** | **`HERO_ACCOUNT`** | **Google Workspace** | **Hero Domain (Account to be warmed up)** | **Bilateral (50/50)** |
| **1** | `SEED_ACCOUNT_1` | Aged Google Seed | **Track 1:** Webhook Buffer & Redis Queue | Inbound Initiator |
| **2** | `SEED_ACCOUNT_2` | Aged Google Seed | **Track 2:** AI Overviews & Perplexity Citation Tracker | Inbound Initiator |
| **3** | `SEED_ACCOUNT_3` | Aged Google Seed | **Track 3:** Live Ad Spend Velocity & Anomaly Alerter | Inbound Initiator |
| **4** | `SEED_ACCOUNT_4` | Aged Google Seed | **Track 4:** Sitemap & Real-Time Indexation Monitor | Inbound Initiator |
| **5** | `SEED_ACCOUNT_5` | Aged Google Seed | **Track 5:** HubSpot & CRM Bi-directional Sync | Outbound Initiator |
| **6** | `SEED_ACCOUNT_6` | Aged Google Seed | **Track 6:** High-Concurrency Shopify Feed Sync | Outbound Initiator |
| **7** | `SEED_ACCOUNT_7` | Aged Google Seed | 🏥 **Track 7:** Medical Imaging PACS & DICOM Pipeline | Outbound Initiator |
| **8** | `SEED_ACCOUNT_8` | Aged Google Seed | ⚡ **Track 8:** Semiconductor ATE STDF Wafer Test Log Parser | Outbound Initiator |

---

## 🛡️ Deliverability & Anti-Fingerprinting Mechanisms

1. **Zero Tracking / Zero Outbound Links**:
   - Strictly 0 links, 0 pixels, and 0 redirects across all 48 warmup drafts.
   - Clean native `<div dir="ltr">` Gmail HTML structure matching standard 1-on-1 human emails.

2. **Automated Spam Rescue ("Not Spam" Signal)**:
   - Scans `[Gmail]/Spam` across all 9 mailboxes on every run.
   - Trapped emails are automatically moved to `INBOX`, marked read, starred (⭐), and given an explicit `Not Spam` classification signal.

3. **Multi-Tiered Stochastic Human Delay**:
   - Mode A (15%): 8–25 minutes (Quick desk reply)
   - Mode B (65%): 45–210 minutes (Deep focus / meeting delay)
   - Mode C (20%): 6–14 hours (Next morning catch-up)

4. **Daylight Protection (Business Hours)**:
   - Dispatches only between 09:00 AM and 07:30 PM IST.
   - Maintains sleep silence at night to mimic human biological rhythms.

---

## ⚡ GitHub Actions Secrets Setup

Under **Settings > Secrets and variables > Actions**, add the single repository secret **`WARMUP_ENV`**.

Template:
```env
HERO_EMAIL=hero@yourdomain.com
HERO_PASSWORD=xxxx xxxx xxxx xxxx
SEED_1_EMAIL=seed1@gmail.com
SEED_1_PASSWORD=xxxx xxxx xxxx xxxx
SEED_2_EMAIL=seed2@gmail.com
SEED_2_PASSWORD=xxxx xxxx xxxx xxxx
SEED_3_EMAIL=seed3@gmail.com
SEED_3_PASSWORD=xxxx xxxx xxxx xxxx
SEED_4_EMAIL=seed4@gmail.com
SEED_4_PASSWORD=xxxx xxxx xxxx xxxx
SEED_5_EMAIL=seed5@gmail.com
SEED_5_PASSWORD=xxxx xxxx xxxx xxxx
SEED_6_EMAIL=seed6@gmail.com
SEED_6_PASSWORD=xxxx xxxx xxxx xxxx
SEED_7_EMAIL=seed7@gmail.com
SEED_7_PASSWORD=xxxx xxxx xxxx xxxx
SEED_8_EMAIL=seed8@gmail.com
SEED_8_PASSWORD=xxxx xxxx xxxx xxxx
```

> **Security Note:** All credentials, email addresses, and passwords must be stored ONLY in GitHub Encrypted Repository Secrets. Never commit real emails or credentials to Git.

---

## 💻 Local CLI Commands

```bash
# 1. Single email delivery & IMAP placement test
python engine.py --test-send

# 2. Force single micro-run tick
python engine.py --tick --force

# 3. Check live status and thread stages
python engine.py --status

# 4. Trigger standalone spam rescue scan across all accounts
python engine.py --spam-rescue
```
