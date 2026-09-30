import random
import re

def spin(text: str) -> str:
    """Recursively resolves spintax {option1|option2|...}"""
    pattern = r'\{([^{}]+)\}'
    while re.search(pattern, text):
        text = re.sub(pattern, lambda m: random.choice(m.group(1).split('|')), text)
    return text

# 8 Persistent Project Tracks (4 Inbound Initiators, 4 Outbound Initiators)
TRACKS = {
    1: {
        "partner_key": "SEED_1",
        "name": "Webhook Buffer & Redis Queue",
        "direction": "inbound",  # Seed initiates -> Hero replies
        "stages": [
            {
                "stage": 1,
                "role": "seed",
                "subject": "{Quick question regarding webhook drops|Webhook payload bottleneck - quick question|Python webhook buffer question}",
                "body": "{Hey|Hi} Raj,\n\n{Came across|Saw} your Python repos around event-driven data ingestion. We have a nagging issue at our agency where high-volume client webhook payloads randomly drop packets during sudden traffic spikes on Friday afternoons.\n\nCurious if you have hands-on experience building lightweight Redis or Celery buffer queues to absorb these bursts before hitting our internal database? Happy to commission a quick sprint script to test the waters if you have bandwidth.\n\n{Best|Cheers},\nRaj"
            },
            {
                "stage": 1,
                "role": "hero",
                "subject": "Re: {subject}",
                "body": "{Hey|Hi} Raj,\n\nThanks for reaching out. Yes, that is a common architectural bottleneck when webhooks hit synchronous database handlers directly. Usually solve this with an asynchronous FastAPI endpoint pushing straight into a Redis stream or memory buffer.\n\nHappy to take a look at a sample payload structure if you want to keep it async over email first. No commitments needed.\n\n{Best|Cheers},\nRaj bazx"
            },
            {
                "stage": 2,
                "role": "seed",
                "subject": "Re: {subject}",
                "body": "{Hey|Hi} Raj,\n\nAppreciate the quick reply. Attached the sample JSON payload below (around 45 fields per event). We average 120 events/sec during peak traffic.\n\nWould Thursday morning work for a quick 10-minute sync, or should we just share endpoint documentation and keep moving async?\n\n{Best|Cheers},\nRaj"
            },
            {
                "stage": 2,
                "role": "hero",
                "subject": "Re: {subject}",
                "body": "{Hey|Hi} Raj,\n\nLet us keep it async first to save your team's time. Looked through the schema—the payload is relatively clean, but nested telemetry arrays are causing serialization overhead.\n\nI can put together a standalone Python worker script with batch insert logic this afternoon and drop a snippet here for review.\n\n{Best|Cheers},\nRaj bazx"
            },
            {
                "stage": 3,
                "role": "seed",
                "subject": "Re: {subject}",
                "body": "{Hey|Hi} Raj,\n\nSounds like a solid plan. Dropped the sandbox endpoint credentials in your inbox. Keep in mind the staging server throttles with 429 errors if concurrency exceeds 20 workers.\n\nLooking forward to seeing the batching benchmark numbers.\n\n{Best|Cheers},\nRaj"
            },
            {
                "stage": 3,
                "role": "hero",
                "subject": "Re: {subject}",
                "body": "{Hey|Hi} Raj,\n\nFinished the worker script with exponential backoff and token-bucket throttling. Ran a simulation on sandbox pushing 800 events across 5 concurrent workers—zero packet drops and response latency hovered around 18ms.\n\nPushed the test script to the staging branch for your team to inspect.\n\n{Best|Cheers},\nRaj bazx"
            },
            {
                "stage": 4,
                "role": "seed",
                "subject": "Re: {subject}",
                "body": "{Hey|Hi} Raj,\n\nOur backend engineer inspected the staging branch this morning. Exception logging and connection pooling look super clean. Quick tweak: can we log event timestamps strictly in UTC for our analytics cluster?\n\n{Best|Cheers},\nRaj"
            },
            {
                "stage": 4,
                "role": "hero",
                "subject": "Re: {subject}",
                "body": "{Hey|Hi} Raj,\n\nUpdated timestamps to strict ISO-8601 UTC across all log handlers. Also added a minimal Dockerfile and healthcheck ping endpoint so your team can spin it up on ECS or Cloud Run without manual config.\n\n{Best|Cheers},\nRaj bazx"
            },
            {
                "stage": 5,
                "role": "seed",
                "subject": "Re: {subject}",
                "body": "{Hey|Hi} Raj,\n\nMerged the container to production yesterday evening. Handled overnight spike seamlessly with zero dropped payloads. The dev leads are thrilled with the turnaround.\n\nWould you have bandwidth next month for a recurring retainer to assist with our upcoming analytics data ingestion pipeline?\n\n{Best|Cheers},\nRaj"
            },
            {
                "stage": 5,
                "role": "hero",
                "subject": "Re: {subject}",
                "body": "{Hey|Hi} Raj,\n\nGlad to hear production held up smoothly through the traffic spike. Yes, I have room for one more retainer slot starting next month. Happy to jump into the analytics ingestion pipeline whenever you are ready.\n\nLet us touch base early next week.\n\n{Best|Cheers},\nRaj bazx"
            }
        ]
    },
    2: {
        "partner_key": "SEED_2",
        "name": "AI Overviews & Perplexity Citation Tracker",
        "direction": "inbound",  # Seed initiates -> Hero replies
        "stages": [
            {
                "stage": 1,
                "role": "seed",
                "subject": "{Google AI Overviews tracking question|Perplexity citation tracker - Python script|AI search visibility pipeline}",
                "body": "{Hey|Hi} Raj,\n\n{Noticed|Saw} your automation work with Python and modern web APIs. Our search team is struggling with tracking brand citation visibility inside Google AI Overviews and Perplexity search answers across our top 50 client keywords.\n\nManual verification is burning 15 hours every week. Wondering if you have built custom headless scrapers or API connectors that can monitor citation presence and alert on drops? Open to a small trial sprint.\n\n{Best|Cheers},\nBit"
            },
            {
                "stage": 1,
                "role": "hero",
                "subject": "Re: {subject}",
                "body": "{Hey|Hi} Bit,\n\nThanks for reaching out. Yes, traditional rank trackers fail completely with dynamic AI Overviews and Perplexity because the answer snippets fluctuate based on query semantics and geo IP.\n\nI built a headless worker recently that pulls structured citations via reverse search APIs and extracts domain mentions directly into a lightweight SQLite or Postgres table. Happy to share how the workflow runs.\n\n{Best|Cheers},\nRaj bazx"
            },
            {
                "stage": 2,
                "role": "seed",
                "subject": "Re: {subject}",
                "body": "{Hey|Hi} Bit,\n\nThat matches our needs closely. We specifically need to flag when a client's root domain drops off the top 3 source citations in Perplexity Pro results.\n\nShould we set up a quick 10-minute Loom or keep iterating over email?\n\n{Best|Cheers},\nBit"
            },
            {
                "stage": 2,
                "role": "hero",
                "subject": "Re: {subject}",
                "body": "{Hey|Hi} Bit,\n\nEmail is great, saves us both calendar overhead. Send over a sample list of 10 keywords and the target brand domains. I will draft a quick script that fetches the citation sources and outputs a clean JSON diff showing presence changes.\n\n{Best|Cheers},\nRaj bazx"
            },
            {
                "stage": 3,
                "role": "seed",
                "subject": "Re: {subject}",
                "body": "{Hey|Hi} Raj,\n\nSent over the 10 target queries across FinTech and SaaS niches. Watch out for bot verification headers on Perplexity when running frequent queries.\n\nLet me know once you have a test run output ready to review.\n\n{Best|Cheers},\nBit"
            },
            {
                "stage": 3,
                "role": "hero",
                "subject": "Re: {subject}",
                "body": "{Hey|Hi} Bit,\n\nFinished the prototype script. Handled session rotation and parsed the citation card links accurately across all 10 queries. Found that 4 queries showed source citations for your client in the top 2 slots.\n\nShared the generated CSV report and script via email for your team's review.\n\n{Best|Cheers},\nRaj bazx"
            },
            {
                "stage": 4,
                "role": "seed",
                "subject": "Re: {subject}",
                "body": "{Hey|Hi} Raj,\n\nThe citation extraction data is spot-on. Can we integrate a simple webhook alert so if a domain drops from an AI overview, our Slack channel receives an instant alert?\n\n{Best|Cheers},\nBit"
            },
            {
                "stage": 4,
                "role": "hero",
                "subject": "Re: {subject}",
                "body": "{Hey|Hi} Bit,\n\nAdded an incoming Slack webhook handler. It calculates the delta between consecutive runs and posts an actionable alert card with the query, previous citation position, and timestamp.\n\nTested with a sample drop event and it fired within 2 seconds.\n\n{Best|Cheers},\nRaj bazx"
            },
            {
                "stage": 5,
                "role": "seed",
                "subject": "Re: {subject}",
                "body": "{Hey|Hi} Raj,\n\nOur client was amazed by the automated citation report in our monthly review today. This tool saved our agency dozens of hours already. We want to put this into daily production across all 80 agency accounts on a retainer basis. Let us sync next week.\n\n{Best|Cheers},\nBit"
            },
            {
                "stage": 5,
                "role": "hero",
                "subject": "Re: {subject}",
                "body": "{Hey|Hi} Bit,\n\nThrilled to hear your client loved the report! That kind of visibility into generative search is a major differentiator in 2026. Happy to onboard the remaining accounts under a monthly maintenance agreement.\n\nSpeak early next week.\n\n{Best|Cheers},\nRaj bazx"
            }
        ]
    },
    3: {
        "partner_key": "SEED_3",
        "name": "Live Ad Spend Velocity & Anomaly Alerter",
        "direction": "inbound",  # Seed initiates -> Hero replies
        "stages": [
            {
                "stage": 1,
                "role": "seed",
                "subject": "{API spend velocity script inquiry|Ad budget anomaly monitor - Python script|PPC API spend velocity question}",
                "body": "{Hey|Hi} Raj,\n\n{Saw|Noticed} your Python automation scripts online. Our performance marketing team had an incident last week where a campaign budget cap malfunctioned and burned through $2,000 in two hours before anyone spotted it.\n\nWe are looking to build a lightweight script that queries Meta and Google Ads APIs every 15 minutes to calculate hourly spend velocity and alert if velocity spikes beyond 150% of forecast. Open to a quick trial project?\n\n{Best|Cheers},\nRaya"
            },
            {
                "stage": 1,
                "role": "hero",
                "subject": "Re: {subject}",
                "body": "{Hey|Hi} Raya,\n\nThanks for reaching out. Yes, that is a scary situation and happens more often than platforms admit due to delayed reporting attribution. A lightweight script polling the Insights API with rolling window averages is very straightforward to set up.\n\nHappy to write a standalone Python monitor with Telegram or Slack alerting for your team. Zero commitment upfront.\n\n{Best|Cheers},\nRaj bazx"
            },
            {
                "stage": 2,
                "role": "seed",
                "subject": "Re: {subject}",
                "body": "{Hey|Hi} Raj,\n\nTelegram alerts would be fantastic since our on-call media buyer can react immediately from their phone. We have read-only API access tokens ready in our sandbox environment.\n\nShall we do a brief sync or proceed async over email?\n\n{Best|Cheers},\nRaya"
            },
            {
                "stage": 2,
                "role": "hero",
                "subject": "Re: {subject}",
                "body": "{Hey|Hi} Raya,\n\nAsync over email is ideal. Send over the sandbox ad account ID and API scopes. I will construct the script to calculate rolling 60-minute spend rate and flag any acceleration anomalies.\n\n{Best|Cheers},\nRaj bazx"
            },
            {
                "stage": 3,
                "role": "seed",
                "subject": "Re: {subject}",
                "body": "{Hey|Hi} Raj,\n\nShared sandbox credentials. Keep in mind Google Ads API uses gRPC protocol while Meta uses Graph API, so auth tokens refresh slightly differently.\n\nLet us know once the spend calculations check out.\n\n{Best|Cheers},\nRaya"
            },
            {
                "stage": 3,
                "role": "hero",
                "subject": "Re: {subject}",
                "body": "{Hey|Hi} Raya,\n\nCompleted the unified monitor. Unified both Google Ads and Meta spend metrics into a single dataclass. The script computes standard deviation over the prior 48 hours to prevent false alarms during normal peak traffic hours.\n\nTested against simulated spikes and alerts fired cleanly.\n\n{Best|Cheers},\nRaj bazx"
            },
            {
                "stage": 4,
                "role": "seed",
                "subject": "Re: {subject}",
                "body": "{Hey|Hi} Raj,\n\nSimulated an intentional test spike this morning and the Telegram bot notified our media buyer within 4 minutes. Exactly what we needed. Can we add automated pause functionality if spend exceeds 200%?\n\n{Best|Cheers},\nRaya"
            },
            {
                "stage": 4,
                "role": "hero",
                "subject": "Re: {subject}",
                "body": "{Hey|Hi} Raya,\n\nAdded an optional auto-pause kill-switch. It requires a confirmed flag in the config file to prevent accidental shutoffs. Tested in sandbox and campaign status toggles to PAUSED in under 800ms.\n\n{Best|Cheers},\nRaj bazx"
            },
            {
                "stage": 5,
                "role": "seed",
                "subject": "Re: {subject}",
                "body": "{Hey|Hi} Raj,\n\nThe spend guard script gives our leadership total peace of mind across our $250k monthly ad accounts. We want to roll this out as a permanent service and discuss a monthly retainer for continuous monitoring.\n\n{Best|Cheers},\nRaya"
            },
            {
                "stage": 5,
                "role": "hero",
                "subject": "Re: {subject}",
                "body": "{Hey|Hi} Raya,\n\nWonderful to hear the team feels secure now. Protecting high-velocity ad spend is mission critical. Happy to manage and maintain the infrastructure on retainer. Let us coordinate next steps Monday.\n\n{Best|Cheers},\nRaj bazx"
            }
        ]
    },
    4: {
        "partner_key": "SEED_4",
        "name": "Sitemap & Real-Time Indexation Monitor",
        "direction": "inbound",  # Seed initiates -> Hero replies
        "stages": [
            {
                "stage": 1,
                "role": "seed",
                "subject": "{Sitemap delta & indexation script inquiry|Google Search Console API indexation monitor|Real-time indexation checker}",
                "body": "{Hey|Hi} Raj,\n\n{Came across|Saw} your Python backend engineering work online. Our technical SEO agency manages several high-traffic publisher portals with over 100,000 URLs. We frequently suffer from stealth de-indexation after CMS updates, which goes unnoticed for weeks and hurts organic revenue.\n\nCurious if you have built automated scripts that compare XML sitemap deltas against Google Search Console Indexing API and highlight un-indexed URLs? Open to a small trial script first to test workflow.\n\n{Best|Cheers},\nForgex"
            },
            {
                "stage": 1,
                "role": "hero",
                "subject": "Re: {subject}",
                "body": "{Hey|Hi} Forgex,\n\nThanks for reaching out. Yes, sitemap drift and silent canonicalization drops are huge pain points for large catalogs. GSC inspection API has quota limits, but combining sitemap parsing with batched URL Inspection API solves this reliably.\n\nHappy to assemble a lightweight diffing script to benchmark against your staging environment without any upfront commitment.\n\n{Best|Cheers},\nRaj bazx"
            },
            {
                "stage": 2,
                "role": "seed",
                "subject": "Re: {subject}",
                "body": "{Hey|Hi} Raj,\n\nExactly, GSC's 2,000 daily API quota has been our biggest hurdle. A smart diff engine that only inspects newly added or modified URLs from the `<lastmod>` tag would solve our problem.\n\nShall we keep communication async via email?\n\n{Best|Cheers},\nForgex"
            },
            {
                "stage": 2,
                "role": "hero",
                "subject": "Re: {subject}",
                "body": "{Hey|Hi} Forgex,\n\nYes, async email is perfect. Filtering by `<lastmod>` timestamp and caching inspected URLs in SQLite cuts API call volume by over 85%. Send over a sample sitemap index and I will prototype the parser.\n\n{Best|Cheers},\nRaj bazx"
            },
            {
                "stage": 3,
                "role": "seed",
                "subject": "Re: {subject}",
                "body": "{Hey|Hi} Raj,\n\nSent over the sitemap index URL containing 15 child sitemaps. Let me know how the delta parsing performs against our 40,000 URL test partition.\n\n{Best|Cheers},\nForgex"
            },
            {
                "stage": 3,
                "role": "hero",
                "subject": "Re: {subject}",
                "body": "{Hey|Hi} Forgex,\n\nParsed all 15 child sitemaps in 6.4 seconds using asynchronous streaming. The delta engine isolated 142 URLs modified in the last 48 hours and batched them against GSC API seamlessly.\n\nSent the HTML discrepancy report for your review.\n\n{Best|Cheers},\nRaj bazx"
            },
            {
                "stage": 4,
                "role": "seed",
                "subject": "Re: {subject}",
                "body": "{Hey|Hi} Raj,\n\nThe speed and delta accuracy are exceptional. It already caught 8 product pages with inadvertent `noindex` headers. Could we package this as a nightly GitHub Action cron job?\n\n{Best|Cheers},\nForgex"
            },
            {
                "stage": 4,
                "role": "hero",
                "subject": "Re: {subject}",
                "body": "{Hey|Hi} Forgex,\n\nCreated the GitHub Action workflow file with encrypted secrets for service account credentials. It runs at 03:00 UTC nightly and emails an executive summary if anomalies exceed 5 URLs.\n\n{Best|Cheers},\nRaj bazx"
            },
            {
                "stage": 5,
                "role": "seed",
                "subject": "Re: {subject}",
                "body": "{Hey|Hi} Raj,\n\nThe workflow has run flawlessly for 5 straight nights and our account managers rely on the morning summary. We want to retain you to maintain this script and build our Core Web Vitals monitor next. Let us connect next week.\n\n{Best|Cheers},\nForgex"
            },
            {
                "stage": 5,
                "role": "hero",
                "subject": "Re: {subject}",
                "body": "{Hey|Hi} Forgex,\n\nGlad the nightly workflow is delivering clear value to your account managers. Would be delighted to help build out the Core Web Vitals crawler as well. Let us sync on Monday.\n\n{Best|Cheers},\nRaj bazx"
            }
        ]
    },
    5: {
        "partner_key": "SEED_5",
        "name": "HubSpot & CRM Bi-directional Sync",
        "direction": "outbound",  # Hero initiates -> Seed replies
        "stages": [
            {
                "stage": 1,
                "role": "hero",
                "subject": "{HubSpot webhook sync question|CRM lead routing automation - quick thought|Bi-directional CRM sync inquiry}",
                "body": "{Hey|Hi} Dev Team,\n\nBuilt a quick Python script last week for an agency whose sales reps were losing 20 minutes every morning manually reconciling deal stages between HubSpot and their internal database.\n\nAutomated it with a lightweight webhook listener that updates deal records bi-directionally in under 800ms. Curious if you have similar custom integration backlogs at your studio? Happy to knock out a small trial script with zero commitment.\n\n{Best|Cheers},\nRaj bazx"
            },
            {
                "stage": 1,
                "role": "seed",
                "subject": "Re: {subject}",
                "body": "{Hey|Hi} Raj,\n\nTimely outreach. We actually have an open ticket for a client wanting their Close CRM lead status synced with their PostgreSQL database without relying on expensive Zapier tasks.\n\nDo you handle OAuth token refresh and rate limit retries in pure Python?\n\n{Best|Cheers},\nDev Studio"
            },
            {
                "stage": 2,
                "role": "hero",
                "subject": "Re: {subject}",
                "body": "{Hey|Hi} Dev Studio,\n\nYes, absolutely. Avoid Zapier overhead completely with a clean Python service using FastAPI and AsyncPG. OAuth refresh tokens are stored securely with automatic background rotation before expiry.\n\nSend over the specific field mapping specs whenever convenient and I will sketch out the architecture.\n\n{Best|Cheers},\nRaj bazx"
            },
            {
                "stage": 2,
                "role": "seed",
                "subject": "Re: {subject}",
                "body": "{Hey|Hi} Raj,\n\nField mappings attached: 12 standard lead attributes plus 3 custom UTM fields. The client processes around 400 lead events per day.\n\nCan you demonstrate a quick proof-of-concept on sandbox?\n\n{Best|Cheers},\nDev Studio"
            },
            {
                "stage": 3,
                "role": "hero",
                "subject": "Re: {subject}",
                "body": "{Hey|Hi} Dev Studio,\n\nBuilt the sandbox service. Set up webhook validation signatures to reject unauthorized payloads, mapped all 15 fields, and handled upsert conflicts with PostgreSQL `ON CONFLICT DO UPDATE`.\n\nRan 50 test leads through the sandbox endpoint—all synced in sub-500ms.\n\n{Best|Cheers},\nRaj bazx"
            },
            {
                "stage": 3,
                "role": "seed",
                "subject": "Re: {subject}",
                "body": "{Hey|Hi} Raj,\n\nJust verified the database records. Data types and custom UTM strings populated perfectly. Exception handling on invalid email formats was handled gracefully too.\n\nWhat is your deployment recommendation for production?\n\n{Best|Cheers},\nDev Studio"
            },
            {
                "stage": 4,
                "role": "hero",
                "subject": "Re: {subject}",
                "body": "{Hey|Hi} Dev Studio,\n\nRecommend a minimal container on AWS App Runner or DigitalOcean App Platform for $5/mo. Included Dockerfile, healthcheck route, and automated migration scripts in the repo.\n\n{Best|Cheers},\nRaj bazx"
            },
            {
                "stage": 4,
                "role": "seed",
                "subject": "Re: {subject}",
                "body": "{Hey|Hi} Raj,\n\nDeployed on DigitalOcean App Platform seamlessly. Client saw their live leads syncing within seconds and signed off on delivery.\n\nWe would like to discuss ongoing contractor support for our agency client integrations.\n\n{Best|Cheers},\nDev Studio"
            },
            {
                "stage": 5,
                "role": "hero",
                "subject": "Re: {subject}",
                "body": "{Hey|Hi} Dev Studio,\n\nAwesome to hear the client was impressed. Delivering rock-solid integrations without third-party SaaS bloat is always rewarding. Would love to partner on future agency builds.\n\nLet us catch up early next week.\n\n{Best|Cheers},\nRaj bazx"
            },
            {
                "stage": 5,
                "role": "seed",
                "subject": "Re: {subject}",
                "body": "{Hey|Hi} Raj,\n\nCalendar invite sent for next Tuesday. Looking forward to formalizing our integration partnership.\n\n{Best|Cheers},\nDev Studio"
            }
        ]
    },
    6: {
        "partner_key": "SEED_6",
        "name": "High-Concurrency Shopify Feed Sync",
        "direction": "outbound",  # Hero initiates -> Seed replies
        "stages": [
            {
                "stage": 1,
                "role": "hero",
                "subject": "{Shopify product inventory sync script|High-volume Shopify catalog updater|Catalog API concurrency script}",
                "body": "{Hey|Hi} E-commerce Team,\n\nBuilt a high-concurrency Python script last week for an agency friend whose brand catalog was failing daily inventory syncs across 50,000 SKUs due to Shopify GraphQL rate limits.\n\nAutomated the pipeline using token-bucket concurrency that cut catalog sync duration from 3 hours to 18 minutes. Curious if you have similar custom inventory automation sitting on your backlog? Happy to run a small trial script with zero commitment.\n\n{Best|Cheers},\nRaj bazx"
            },
            {
                "stage": 1,
                "role": "seed",
                "subject": "Re: {subject}",
                "body": "{Hey|Hi} Raj,\n\nVery relevant timing. We manage a multi-brand retailer with 35,000 SKUs experiencing out-of-stock discrepancies because their inventory sync script crashes halfway through.\n\nDoes your script support Shopify's Bulk Operations GraphQL API or standard REST batches?\n\n{Best|Cheers},\nRaven"
            },
            {
                "stage": 2,
                "role": "hero",
                "subject": "Re: {subject}",
                "body": "{Hey|Hi} Raven,\n\nIt leverages the GraphQL Bulk Operation API for bulk extraction, and asynchronous GraphQL mutations with leaky-bucket rate limiting for incremental stock adjustments.\n\nSend over a sample CSV or API spec of the supplier inventory feed and I will build a tailored parser for your staging store.\n\n{Best|Cheers},\nRaj bazx"
            },
            {
                "stage": 2,
                "role": "seed",
                "subject": "Re: {subject}",
                "body": "{Hey|Hi} Raj,\n\nSample inventory feed attached: CSV with barcode, SKU, warehouse location, and quantity. Supplier drops a fresh file every 2 hours via SFTP.\n\nLet me know if you can automate the SFTP pull and inventory mutation.\n\n{Best|Cheers},\nRaven"
            },
            {
                "stage": 3,
                "role": "hero",
                "subject": "Re: {subject}",
                "body": "{Hey|Hi} Raven,\n\nBuilt the end-to-end worker. It connects to SFTP via Paramiko, streams the CSV in chunks, diffs against existing inventory cache, and dispatches batched GraphQL mutations to Shopify.\n\nTested against 10,000 mock SKU updates—completed in 4 minutes with zero rate limit throttles.\n\n{Best|Cheers},\nRaj bazx"
            },
            {
                "stage": 3,
                "role": "seed",
                "subject": "Re: {subject}",
                "body": "{Hey|Hi} Raj,\n\nRan your worker on our staging store this morning. Stock levels updated across all variants without a single desync error. Benchmark speed is remarkable.\n\nCan we add email notifications if the SFTP feed is missing or unreadable?\n\n{Best|Cheers},\nRaven"
            },
            {
                "stage": 4,
                "role": "hero",
                "subject": "Re: {subject}",
                "body": "{Hey|Hi} Raven,\n\nAdded automated alert handling. If SFTP connection fails or the CSV schema fails validation, it sends an alert via SMTP and retries after a 10-minute backoff.\n\nReady for production deployment.\n\n{Best|Cheers},\nRaj bazx"
            },
            {
                "stage": 4,
                "role": "seed",
                "subject": "Re: {subject}",
                "body": "{Hey|Hi} Raj,\n\nDeployed to production yesterday. Overnight stock counts matched our physical warehouse inventory 100% for the first time this quarter. Our operations director is ecstatic.\n\nLet us talk about a monthly maintenance agreement.\n\n{Best|Cheers},\nRaven"
            },
            {
                "stage": 5,
                "role": "hero",
                "subject": "Re: {subject}",
                "body": "{Hey|Hi} Raven,\n\nDelighted to hear the warehouse counts match 100%! Eliminating phantom inventory is huge for customer retention. Happy to support your stores on a monthly retainer.\n\nLet us connect early next week.\n\n{Best|Cheers},\nRaj bazx"
            },
            {
                "stage": 5,
                "role": "seed",
                "subject": "Re: {subject}",
                "body": "{Hey|Hi} Raj,\n\nWill send over contract details on Monday. Welcome aboard.\n\n{Best|Cheers},\nRaven"
            }
        ]
    },
    7: {
        "partner_key": "SEED_7",
        "name": "Medical Imaging PACS & DICOM Pipeline",
        "direction": "outbound",  # Hero initiates -> Seed replies
        "stages": [
            {
                "stage": 1,
                "role": "hero",
                "subject": "{DICOM CT pipeline automation|Medical imaging DICOM de-identification script|High-throughput DICOM processing question}",
                "body": "{Hey|Hi} Medical Research Team,\n\nBuilt a high-throughput Python pipeline recently for an imaging lab struggling with processing bottlenecks when converting 16-bit DICOM CT series and stripping HIPAA metadata before feeding into vision models.\n\nAutomated the workflow using PyDICOM streaming that reduced memory usage by 70% and processed studies in sub-minute batches. Curious if your lab has similar medical imaging data backlogs? Happy to run a small trial script on sample scans with zero commitment.\n\n{Best|Cheers},\nRaj bazx"
            },
            {
                "stage": 1,
                "role": "seed",
                "subject": "Re: {subject}",
                "body": "{Hey|Hi} Raj,\n\nYour note is exceptionally timely. We are currently scaling an MRI volumetric segmentation project, and our researchers spend hours manually running de-identification scripts on multi-frame DICOM files coming off the scanner.\n\nDoes your pipeline handle multi-frame pixel data and non-standard private DICOM tags?\n\n{Best|Cheers},\nBazx Singh"
            },
            {
                "stage": 2,
                "role": "hero",
                "subject": "Re: {subject}",
                "body": "{Hey|Hi} Singh,\n\nYes, absolutely. The pipeline implements standard HIPAA Safe Harbor de-identification while systematically scrubbing private vendor tags (GE/Siemens) that frequently leak PHI in shadow dictionaries. Multi-frame pixel arrays are extracted using memory-mapped NumPy views without blowing up RAM.\n\nShare a sample anonymized study and I will demonstrate the extraction throughput.\n\n{Best|Cheers},\nRaj bazx"
            },
            {
                "stage": 2,
                "role": "seed",
                "subject": "Re: {subject}",
                "body": "{Hey|Hi} Raj,\n\nUploaded a test multi-slice CT abdomen series (around 800 slices) to our secure sandbox bucket. We need automated windowing/leveling applied and slices saved as compressed NIfTI and preprocessed PNGs.\n\nLooking forward to seeing your benchmarks.\n\n{Best|Cheers},\nSingh"
            },
            {
                "stage": 3,
                "role": "hero",
                "subject": "Re: {subject}",
                "body": "{Hey|Hi} Singh,\n\nCompleted the benchmark. The script processed all 800 CT slices in 14.2 seconds on standard compute, stripped all PHI tags, applied soft tissue windowing (WL: 40, WW: 400), and exported both NIfTI volumes and normalized arrays.\n\nPushed the benchmark report and output files for your review.\n\n{Best|Cheers},\nRaj bazx"
            },
            {
                "stage": 3,
                "role": "seed",
                "subject": "Re: {subject}",
                "body": "{Hey|Hi} Raj,\n\nOur radiology informatics lead reviewed the exported NIfTI volumes today. The slice ordering, voxel spacing, and tag de-identification are 100% compliant with our IRB standards. Incredible speed.\n\nCan we integrate this directly with an incoming PACS Orthanc webhook?\n\n{Best|Cheers},\nSingh"
            },
            {
                "stage": 4,
                "role": "hero",
                "subject": "Re: {subject}",
                "body": "{Hey|Hi} Singh,\n\nAdded an Orthanc PACS webhook listener in FastAPI. When a study finishes transferring over C-STORE, Orthanc notifies our webhook, which triggers the worker pipeline automatically and uploads the preprocessed volume to your research bucket.\n\n{Best|Cheers},\nRaj bazx"
            },
            {
                "stage": 4,
                "role": "seed",
                "subject": "Re: {subject}",
                "body": "{Hey|Hi} Raj,\n\nWe routed our scanner test feed to the webhook and the automated conversion completed flawlessly before the research fellow even sat down at their workstation. This transforms our clinical research workflow.\n\nWe want to formalize an ongoing technical retainer.\n\n{Best|Cheers},\nSingh"
            },
            {
                "stage": 5,
                "role": "hero",
                "subject": "Re: {subject}",
                "body": "{Hey|Hi} Singh,\n\nExtremely rewarding to see the pipeline accelerate research workflows for your fellows. Happy to support your informatics infrastructure and future volumetric models on a monthly retainer.\n\nLet us coordinate next steps next week.\n\n{Best|Cheers},\nRaj bazx"
            },
            {
                "stage": 5,
                "role": "seed",
                "subject": "Re: {subject}",
                "body": "{Hey|Hi} Raj,\n\nOur administrative coordinator will send over the consulting agreement on Monday. Excited to collaborate.\n\n{Best|Cheers},\nSingh"
            }
        ]
    },
    8: {
        "partner_key": "SEED_8",
        "name": "Semiconductor ATE STDF Wafer Test Log Parser",
        "direction": "outbound",  # Hero initiates -> Seed replies
        "stages": [
            {
                "stage": 1,
                "role": "hero",
                "subject": "{STDF wafer test log parser inquiry|High-throughput ATE test log processing|Automated wafer yield analysis script}",
                "body": "{Hey|Hi} Silicon Engineering Team,\n\nBuilt a high-throughput Python parser recently for a post-silicon validation group that was wasting hours manually converting multi-gigabyte STDF binary test logs off ATE testers to calculate wafer yield drops.\n\nEngineered a streaming generator using memory-mapped files that reduced parsing runtime from 45 minutes to 38 seconds while keeping RAM under 200MB. Curious if your team has similar semiconductor test automation backlogs? Happy to run a small trial script on sample binary logs with zero commitment.\n\n{Best|Cheers},\nRaj bazx"
            },
            {
                "stage": 1,
                "role": "seed",
                "subject": "Re: {subject}",
                "body": "{Hey|Hi} Raj,\n\nVery interesting timing. Our product engineering team is currently qualifying a 5nm test chip, and standard third-party STDF parsers are crashing with Out-Of-Memory exceptions on our 2.5GB multi-site wafer logs.\n\nDoes your parser handle custom Parametric Test Records (PTR) and Multiple-Result Parametric Records (MPR) without memory leaks?\n\n{Best|Cheers},\nAnanaya"
            },
            {
                "stage": 2,
                "role": "hero",
                "subject": "Re: {subject}",
                "body": "{Hey|Hi} Ananaya,\n\nYes, absolutely. The memory leaks in standard STDF libraries happen because they instantiate Python objects for every PTR record. My parser uses `struct.unpack_from` over a memory-mapped buffer and streams yield metrics directly into columnar arrays without allocating intermediate objects.\n\nShare a sample anonymized STDF file and I will run a benchmark extraction.\n\n{Best|Cheers},\nRaj bazx"
            },
            {
                "stage": 2,
                "role": "seed",
                "subject": "Re: {subject}",
                "body": "{Hey|Hi} Raj,\n\nShared a 1.2GB anonymized STDF V4 log via our secure transfer link. We need wafer binning summaries (Hard Bin & Soft Bin counts) and die coordinate yield matrices exported to CSV and JSON.\n\nLooking forward to seeing how your streaming approach performs.\n\n{Best|Cheers},\nAnanaya"
            },
            {
                "stage": 3,
                "role": "hero",
                "subject": "Re: {subject}",
                "body": "{Hey|Hi} Ananaya,\n\nCompleted the benchmark on the 1.2GB file. Total processing time: 24.8 seconds on standard CPU, peak RAM consumption: 114MB. Die coordinates, HBin/SBin counts, and test site efficiency matrices mapped cleanly to JSON and CSV.\n\nAttached the benchmark summary and sample wafer yield map output.\n\n{Best|Cheers},\nRaj bazx"
            },
            {
                "stage": 3,
                "role": "seed",
                "subject": "Re: {subject}",
                "body": "{Hey|Hi} Raj,\n\nOur yield analysis engineers just verified the die counts against our tester console. The binning totals match to the single die and the execution speed is 10x faster than our current tool. Really impressive engineering.\n\nCan we integrate automated wafer map visualization using Plotly?\n\n{Best|Cheers},\nAnanaya"
            },
            {
                "stage": 4,
                "role": "hero",
                "subject": "Re: {subject}",
                "body": "{Hey|Hi} Ananaya,\n\nAdded interactive wafer map generation. It renders an HTML/SVG color-coded wafer map showing pass/fail die coordinates, notch orientation, and bin clustering for defect analysis.\n\n{Best|Cheers},\nRaj bazx"
            },
            {
                "stage": 4,
                "role": "seed",
                "subject": "Re: {subject}",
                "body": "{Hey|Hi} Raj,\n\nThe wafer map visualization was demonstrated in our post-silicon review meeting this morning. The director of product engineering wants this script integrated into our automated nightly qualification pipeline across all test cells.\n\nLet us talk about an ongoing retainer agreement.\n\n{Best|Cheers},\nAnanaya"
            },
            {
                "stage": 5,
                "role": "hero",
                "subject": "Re: {subject}",
                "body": "{Hey|Hi} Ananaya,\n\nFantastic to hear the wafer maps made a strong impression in the qualification review! Optimizing silicon test telemetry and yield analytics is always exciting work. Happy to support the pipeline integration on retainer.\n\nLet us sync early next week.\n\n{Best|Cheers},\nRaj bazx"
            },
            {
                "stage": 5,
                "role": "seed",
                "subject": "Re: {subject}",
                "body": "{Hey|Hi} Raj,\n\nLooking forward to it. Will coordinate with procurement to get the paperwork moving on Monday.\n\n{Best|Cheers},\nAnanaya"
            }
        ]
    }
}
