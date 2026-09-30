import sys
import os
import re

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from stories import TRACKS

spam_keywords = [
    'free', 'urgent', 'guaranteed', 'risk-free', 'buy now', 'click here', 
    'act now', 'cash', 'crypto', 'prize', 'winner', 'miracle', 'cheap', 
    'credit', 'loan', 'mortgage', 'opt-in', 'unsubscribe', 'viagra', 'income'
]

print("=== AUDIT 1: SPAM KEYWORD SCAN ===")
flagged = []
for t_id, t_data in TRACKS.items():
    for idx, s in enumerate(t_data['stages']):
        text = (s['subject'] + ' ' + s['body']).lower()
        for kw in spam_keywords:
            # Word boundary search so 'freely' or 'freeze' is not confused
            if re.search(r'\b' + re.escape(kw) + r'\b', text):
                flagged.append((t_id, idx+1, kw))

if not flagged:
    print("  ✅ ZERO spam keywords found across all 8 tracks!")
else:
    for f in flagged:
        print(f"  ⚠️ Track {f[0]} Turn {f[1]} flagged keyword: '{f[2]}'")

print("\n=== AUDIT 2: LINK & TRACKER SCAN ===")
links_found = []
for t_id, t_data in TRACKS.items():
    for idx, s in enumerate(t_data['stages']):
        text = (s['subject'] + ' ' + s['body']).lower()
        if "http://" in text or "https://" in text or "www." in text or ".com/" in text:
            links_found.append((t_id, idx+1))

if not links_found:
    print("  ✅ ZERO links or URLs found in any email! 100% compliant with Phase 1 link rule.")
else:
    for l in links_found:
        print(f"  🚨 URL found in Track {l[0]} Turn {l[1]}!")

print("\n=== AUDIT 3: WORD COUNT DISTRIBUTION ===")
for t_id, t_data in TRACKS.items():
    t1_words = len(t_data['stages'][0]['body'].split())
    print(f"  Track {t_id} Turn 1 (Initial Hook): {t1_words} words (Target: 70-95 words)")
