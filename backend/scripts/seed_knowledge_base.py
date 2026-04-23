#!/usr/bin/env python3
"""
Seed the TermsGuard AI knowledge base with ~50 ToS/Privacy Policy documents.

Usage (run from backend/ with .env present):
    python scripts/seed_knowledge_base.py
    python scripts/seed_knowledge_base.py --dry-run
    python scripts/seed_knowledge_base.py --limit 5
    python scripts/seed_knowledge_base.py --force   # re-ingest already-ingested sources
"""

import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import trafilatura

from app.rag.ingest import ingest_text
from app.services.supabase_client import get_supabase

MIN_TEXT_LENGTH = 500
RATE_LIMIT_SECONDS = 1.5

# (display_name, url, category)
SOURCES: list[tuple[str, str, str]] = [
    # --- Developer / Cloud Infrastructure ---
    ("GitHub Terms of Service",         "https://docs.github.com/en/site-policy/github-terms/github-terms-of-service",              "developer"),
    ("GitHub Privacy Statement",        "https://docs.github.com/en/site-policy/privacy-policies/github-general-privacy-statement",  "developer"),
    ("Cloudflare Terms of Service",     "https://www.cloudflare.com/terms/",                                                          "developer"),
    ("Stripe Services Agreement",       "https://stripe.com/legal/ssa",                                                               "developer"),
    ("Heroku Terms of Service",         "https://www.heroku.com/policy/tos",                                                          "developer"),
    ("Netlify Terms of Use",            "https://www.netlify.com/legal/terms-of-use/",                                                "developer"),
    ("DigitalOcean Terms of Service",   "https://www.digitalocean.com/legal/terms-of-service-agreement",                              "developer"),
    ("Vercel Terms",                    "https://vercel.com/legal/terms",                                                             "developer"),
    ("Railway Terms of Service",        "https://railway.app/legal/terms",                                                            "developer"),
    ("HuggingFace Terms of Service",    "https://huggingface.co/terms-of-service",                                                    "developer"),

    # --- Communication / Social ---
    ("Telegram Terms of Service",       "https://telegram.org/tos",                                                                   "social"),
    ("Reddit User Agreement",           "https://www.reddit.com/policies/user-agreement",                                             "social"),
    ("Reddit Privacy Policy",           "https://www.reddit.com/policies/privacy-policy",                                             "social"),
    ("Discord Terms of Service",        "https://discord.com/terms",                                                                  "social"),
    ("Discord Privacy Policy",          "https://discord.com/privacy",                                                                "social"),
    ("Pinterest Terms of Service",      "https://policy.pinterest.com/en/terms-of-service",                                           "social"),
    ("Snapchat Terms of Service",       "https://snap.com/en-US/terms",                                                               "social"),

    # --- Productivity / SaaS ---
    ("Notion Terms of Service",         "https://www.notion.so/Terms-and-Privacy-28ffdd083dc3473e9c2da6ec011b58ac",                   "productivity"),
    ("Slack Terms of Service",          "https://slack.com/terms-of-service",                                                         "productivity"),
    ("Zoom Terms of Service",           "https://explore.zoom.us/en/terms/",                                                          "productivity"),
    ("Dropbox Terms of Service",        "https://www.dropbox.com/terms",                                                              "productivity"),
    ("Evernote Terms of Service",       "https://evernote.com/legal/terms-of-service",                                                "productivity"),
    ("Atlassian Cloud Terms",           "https://www.atlassian.com/legal/cloud-terms-of-service",                                     "productivity"),
    ("Box Terms of Service",            "https://www.box.com/legal/termsofservice",                                                   "productivity"),
    ("Canva Terms of Use",              "https://www.canva.com/policies/terms-of-use/",                                               "productivity"),

    # --- Media / Entertainment ---
    ("Spotify End User Agreement",      "https://www.spotify.com/us/legal/end-user-agreement/",                                       "media"),
    ("Twitch Terms of Service",         "https://www.twitch.tv/p/en/legal/terms-of-service/",                                         "media"),
    ("SoundCloud Terms of Use",         "https://soundcloud.com/pages/privacy",                                                       "media"),
    ("Medium Terms of Service",         "https://policy.medium.com/medium-terms-of-service-9db0094a1e0f",                             "media"),
    ("Substack Terms of Service",       "https://substack.com/tos",                                                                   "media"),

    # --- E-commerce / Finance ---
    ("Etsy Terms of Use",               "https://www.etsy.com/legal/terms-of-use",                                                    "ecommerce"),
    ("Shopify Terms of Service",        "https://www.shopify.com/legal/terms",                                                        "ecommerce"),
    ("Fiverr Terms of Service",         "https://www.fiverr.com/terms_of_service",                                                    "ecommerce"),
    ("Upwork Terms of Service",         "https://www.upwork.com/legal",                                                               "ecommerce"),
    ("PayPal User Agreement",           "https://www.paypal.com/us/legalhub/useragreement-full",                                      "finance"),

    # --- CMS / Publishing ---
    ("WordPress.com Terms of Service",  "https://wordpress.com/tos/",                                                                 "cms"),
    ("Wix Terms of Use",                "https://www.wix.com/about/terms-of-use",                                                     "cms"),
    ("Squarespace Terms of Service",    "https://www.squarespace.com/terms-of-service",                                               "cms"),
    ("Ghost Terms of Service",          "https://ghost.org/terms/",                                                                   "cms"),

    # --- AI / ML Platforms ---
    ("OpenAI Terms of Use",             "https://openai.com/policies/terms-of-use",                                                   "ai"),
    ("OpenAI Privacy Policy",           "https://openai.com/policies/privacy-policy",                                                 "ai"),
    ("Anthropic Consumer Terms",        "https://www.anthropic.com/legal/consumer-terms",                                             "ai"),
    ("Anthropic Privacy Policy",        "https://www.anthropic.com/legal/privacy",                                                    "ai"),

    # --- Email / Marketing ---
    ("Mailchimp Terms of Use",          "https://mailchimp.com/legal/terms/",                                                         "email"),
    ("Mailchimp Privacy Policy",        "https://mailchimp.com/legal/privacy/",                                                       "email"),

    # --- Open Source Foundations / Reference Docs ---
    ("Mozilla Firefox Terms",           "https://www.mozilla.org/en-US/about/legal/terms/firefox/",                                   "reference"),
    ("Mozilla Services Terms",          "https://www.mozilla.org/en-US/about/legal/terms/services/",                                  "reference"),
    ("Creative Commons Terms",          "https://creativecommons.org/terms/",                                                         "reference"),
    ("Wikimedia Terms of Use",          "https://foundation.wikimedia.org/wiki/Policy:Terms_of_Use",                                  "reference"),

    # --- Privacy Regulations (as RAG reference) ---
    ("GDPR Full Text (EUR-Lex)",        "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32016R0679",                       "regulation"),
    ("CCPA Text (CA Legislature)",      "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?sectionNum=1798.100.&lawCode=CIV", "regulation"),

    # --- Gaming ---
    ("Steam Subscriber Agreement",      "https://store.steampowered.com/subscriber_agreement/",                                        "gaming"),
    ("Epic Games Terms of Service",     "https://www.epicgames.com/site/en-US/tos",                                                    "gaming"),
    ("Roblox Terms of Use",             "https://en.help.roblox.com/hc/en-us/articles/115004647846-Roblox-Terms-of-Use",              "gaming"),
    ("PlayStation Network ToS",         "https://www.playstation.com/en-us/legal/psn-terms-of-service/",                              "gaming"),
    ("Xbox Services Agreement",         "https://www.xbox.com/en-US/legal/servicessagreement",                                        "gaming"),
    ("Nintendo Account Agreement",      "https://accounts.nintendo.com/term_agreement",                                               "gaming"),
    ("Twitch Developer Agreement",      "https://www.twitch.tv/p/en/legal/developer-agreement/",                                      "gaming"),
    ("Riot Games Terms of Service",     "https://www.riotgames.com/en/terms-of-service",                                              "gaming"),
    ("Activision Terms of Use",         "https://www.activision.com/legal/terms-of-use",                                              "gaming"),
    ("EA User Agreement",               "https://tos.ea.com/legalapp/WEBTERMS/US/en/PC/",                                             "gaming"),

    # --- Banking & Finance ---
    ("Wise Terms of Use",               "https://wise.com/gb/legal/terms-and-conditions",                                             "finance"),
    ("Revolut Terms of Service",        "https://www.revolut.com/legal/terms/",                                                       "finance"),
    ("Coinbase User Agreement",         "https://www.coinbase.com/legal/user_agreement/",                                             "finance"),
    ("Venmo User Agreement",            "https://venmo.com/legal/us-user-agreement/",                                                 "finance"),
    ("Cash App Terms of Service",       "https://cash.app/legal/us/en-us/tos",                                                        "finance"),
    ("Robinhood Customer Agreement",    "https://robinhood.com/us/en/support/articles/customer-agreement/",                           "finance"),
    ("Klarna Terms of Service",         "https://www.klarna.com/us/legal/",                                                           "finance"),
    ("Binance Terms of Use",            "https://www.binance.com/en/terms",                                                           "finance"),
    ("Affirm Terms of Service",         "https://www.affirm.com/licenses/terms-of-use",                                               "finance"),

    # --- Health & Wellness ---
    ("MyFitnessPal Terms of Service",   "https://www.myfitnesspal.com/legal/terms_of_service",                                        "health"),
    ("Headspace Terms of Service",      "https://www.headspace.com/terms-and-conditions",                                             "health"),
    ("Calm Terms of Service",           "https://www.calm.com/terms",                                                                 "health"),
    ("Fitbit Terms of Service",         "https://www.fitbit.com/global/us/legal/terms-of-service",                                   "health"),
    ("23andMe Terms of Service",        "https://www.23andme.com/en-us/legal/terms-of-service/",                                      "health"),
    ("BetterHelp Terms and Conditions", "https://www.betterhelp.com/terms-and-conditions",                                            "health"),
    ("Teladoc Terms of Use",            "https://www.teladoc.com/terms-of-use/",                                                      "health"),
    ("Apple Health Terms",              "https://www.apple.com/legal/privacy/en-ww/",                                                 "health"),

    # --- Education ---
    ("Coursera Terms of Use",           "https://www.coursera.org/about/terms",                                                       "education"),
    ("Udemy Terms of Use",              "https://www.udemy.com/terms/",                                                               "education"),
    ("Khan Academy Terms of Service",   "https://www.khanacademy.org/about/tos",                                                      "education"),
    ("Duolingo Terms of Service",       "https://www.duolingo.com/terms",                                                             "education"),
    ("edX Terms of Service",            "https://www.edx.org/edx-terms-service",                                                      "education"),
    ("Chegg Terms of Use",              "https://www.chegg.com/legal/terms-of-use",                                                   "education"),
    ("Skillshare Terms of Service",     "https://www.skillshare.com/en/terms",                                                        "education"),
    ("LinkedIn Learning Terms",         "https://www.linkedin.com/legal/user-agreement",                                              "education"),

    # --- Travel ---
    ("Airbnb Terms of Service",         "https://www.airbnb.com/help/article/2908",                                                   "travel"),
    ("Booking.com Terms",               "https://www.booking.com/content/terms.en-gb.html",                                           "travel"),
    ("Expedia Terms of Use",            "https://www.expedia.com/p/info-other/terms-conditions.htm",                                  "travel"),
    ("Uber Terms of Service",           "https://www.uber.com/legal/en/document/?name=general-terms-of-use&country=united-states&lang=en", "travel"),
    ("Lyft Terms of Service",           "https://www.lyft.com/terms",                                                                 "travel"),
    ("TripAdvisor Terms",               "https://tripadvisor.mediaroom.com/US-terms-of-use",                                          "travel"),
    ("Vrbo Terms and Conditions",       "https://www.vrbo.com/info/terms-and-conditions",                                             "travel"),
    ("DoorDash Terms of Service",       "https://help.doordash.com/consumers/s/terms-of-service-us",                                  "travel"),
    ("Instacart Terms of Service",      "https://www.instacart.com/terms",                                                            "travel"),

    # --- Telecom & Hardware ---
    ("Apple iOS Terms",                 "https://www.apple.com/legal/internet-services/itunes/us/terms.html",                         "telecom"),
    ("Google Terms of Service",         "https://policies.google.com/terms",                                                          "telecom"),
    ("Google Privacy Policy",           "https://policies.google.com/privacy",                                                        "telecom"),
    ("Microsoft Services Agreement",    "https://www.microsoft.com/en-us/servicesagreement/",                                         "telecom"),
    ("Amazon Conditions of Use",        "https://www.amazon.com/gp/help/customer/display.html?nodeId=508088",                         "telecom"),
    ("AWS Customer Agreement",          "https://aws.amazon.com/agreement/",                                                          "telecom"),
    ("Verizon Terms of Service",        "https://www.verizon.com/about/terms-conditions/",                                            "telecom"),
    ("T-Mobile Terms and Conditions",   "https://www.t-mobile.com/responsibility/legal/terms-and-conditions",                         "telecom"),
    ("AT&T Terms of Service",           "https://www.att.com/legal/terms.attrequiredlegal.html",                                      "telecom"),

    # --- Social / Dating ---
    ("Twitter/X Terms of Service",      "https://twitter.com/en/tos",                                                                 "social"),
    ("TikTok Terms of Service",         "https://www.tiktok.com/legal/page/us/terms-of-service/en",                                   "social"),
    ("LinkedIn User Agreement",         "https://www.linkedin.com/legal/user-agreement",                                              "social"),
    ("Facebook Terms of Service",       "https://www.facebook.com/terms.php",                                                         "social"),
    ("Instagram Terms of Use",          "https://help.instagram.com/581066165581870",                                                  "social"),
    ("YouTube Terms of Service",        "https://www.youtube.com/t/terms",                                                            "social"),
    ("Tinder Terms of Service",         "https://policies.tinder.com/terms/intl/en/",                                                 "social"),
    ("Bumble Terms and Conditions",     "https://bumble.com/en/terms",                                                                "social"),
    ("BeReal Terms of Service",         "https://bere.al/en/terms",                                                                   "social"),
    ("Mastodon Server Covenant",        "https://joinmastodon.org/covenant",                                                          "social"),

    # --- Productivity / Business (additional) ---
    ("Airtable Terms of Service",       "https://www.airtable.com/tos",                                                               "productivity"),
    ("Trello Terms of Service",         "https://www.atlassian.com/legal/cloud-terms-of-service",                                     "productivity"),
    ("Figma Terms of Service",          "https://www.figma.com/tos/",                                                                 "productivity"),
    ("Miro Terms of Service",           "https://miro.com/legal/terms-of-service/",                                                   "productivity"),
    ("Monday.com Terms of Use",         "https://monday.com/l/legal/terms-of-use/",                                                   "productivity"),
    ("Asana Terms of Service",          "https://asana.com/terms",                                                                    "productivity"),
    ("HubSpot Terms of Service",        "https://legal.hubspot.com/terms-of-service",                                                 "productivity"),
    ("Salesforce Terms of Service",     "https://www.salesforce.com/company/legal/sfdc-website-terms-of-service/",                    "productivity"),
    ("DocuSign Terms of Use",           "https://www.docusign.com/company/terms-and-conditions",                                      "productivity"),
    ("Typeform Terms of Service",       "https://admin.typeform.com/to/dwk6gt/",                                                      "productivity"),
    ("Calendly Terms of Service",       "https://calendly.com/legal/terms-of-use",                                                    "productivity"),
    ("Loom Terms of Service",           "https://www.loom.com/terms-of-service",                                                      "productivity"),

    # --- AI / ML Platforms (additional) ---
    ("Google AI Terms",                 "https://ai.google.dev/gemini-api/terms",                                                     "ai"),
    ("Midjourney Terms of Service",     "https://docs.midjourney.com/docs/terms-of-service",                                          "ai"),
    ("Stability AI Terms",              "https://stability.ai/terms-of-service",                                                      "ai"),
    ("Replicate Terms of Service",      "https://replicate.com/terms",                                                                "ai"),
    ("Perplexity AI Terms",             "https://www.perplexity.ai/hub/faq/what-are-perplexity-s-terms-of-service",                  "ai"),
    ("Character.AI Terms of Service",   "https://character.ai/tos",                                                                   "ai"),
    ("Runway Terms of Service",         "https://runwayml.com/terms-of-service/",                                                     "ai"),

    # --- E-commerce (additional) ---
    ("eBay User Agreement",             "https://www.ebay.com/help/policies/member-behaviour-policies/user-agreement?id=4259",        "ecommerce"),
    ("Walmart Terms of Use",            "https://www.walmart.com/help/article/walmart-com-terms-of-use/3b75080af40340d6bbd596f116fae5cf", "ecommerce"),
    ("Target Terms and Conditions",     "https://www.target.com/spot/terms-conditions",                                               "ecommerce"),
    ("AliExpress Terms of Use",         "https://rule.alibaba.com/rule/detail/2041.htm",                                              "ecommerce"),

    # --- News & Media ---
    ("The New York Times ToS",          "https://help.nytimes.com/hc/en-us/articles/115014893428-Terms-of-service",                  "media"),
    ("Reddit Content Policy",           "https://www.reddit.com/policies/content-policy",                                             "media"),
    ("Wikipedia Terms of Use",          "https://foundation.wikimedia.org/wiki/Policy:Terms_of_Use",                                  "media"),
    ("Patreon Terms of Use",            "https://www.patreon.com/policy/legal",                                                       "media"),
    ("Vimeo Terms of Service",          "https://vimeo.com/terms",                                                                    "media"),
    ("Getty Images Terms of Use",       "https://www.gettyimages.com/company/terms",                                                  "media"),
    ("Shutterstock Terms of Service",   "https://www.shutterstock.com/terms",                                                         "media"),

    # --- Developer / Cloud (additional) ---
    ("GCP Terms of Service",            "https://cloud.google.com/terms/",                                                            "developer"),
    ("Azure Terms of Service",          "https://azure.microsoft.com/en-us/support/legal/",                                           "developer"),
    ("Firebase Terms of Service",       "https://firebase.google.com/terms/",                                                         "developer"),
    ("Twilio Terms of Service",         "https://www.twilio.com/en-us/legal/tos",                                                     "developer"),
    ("SendGrid Terms of Service",       "https://www.twilio.com/en-us/legal/tos",                                                     "developer"),
    ("Postman Terms of Service",        "https://www.postman.com/legal/terms/",                                                       "developer"),
    ("npm Terms of Use",                "https://docs.npmjs.com/policies/terms",                                                      "developer"),
    ("PyPI Terms of Use",               "https://pypi.org/policy/terms-of-use/",                                                      "developer"),
    ("Docker Terms of Service",         "https://www.docker.com/legal/docker-terms-service/",                                         "developer"),
    ("Cloudinary Terms of Service",     "https://cloudinary.com/tos",                                                                 "developer"),
    ("PlanetScale Terms",               "https://planetscale.com/legal/siteterms",                                                    "developer"),
    ("Supabase Terms of Service",       "https://supabase.com/terms",                                                                 "developer"),
]


def fetch_text(url: str) -> str | None:
    downloaded = trafilatura.fetch_url(url)
    if not downloaded:
        return None
    return trafilatura.extract(
        downloaded,
        include_comments=False,
        include_tables=True,
        no_fallback=False,
    )


def already_ingested(url: str) -> bool:
    result = get_supabase().table("documents").select("id").eq("source", url).limit(1).execute()
    return len(result.data) > 0


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed TermsGuard AI knowledge base")
    parser.add_argument("--dry-run", action="store_true", help="Fetch and parse but do not write to DB")
    parser.add_argument("--limit", type=int, default=None, help="Process only the first N sources")
    parser.add_argument("--force", action="store_true", help="Re-ingest sources already in the DB")
    args = parser.parse_args()

    sources = SOURCES[: args.limit] if args.limit else SOURCES
    total = len(sources)

    ingested = skipped = failed = 0

    print(f"Seeding knowledge base — {total} sources\n")

    for i, (name, url, category) in enumerate(sources, 1):
        prefix = f"[{i:02d}/{total}]"

        if not args.force and already_ingested(url):
            print(f"{prefix} SKIP     {name}")
            skipped += 1
            continue

        print(f"{prefix} FETCH    {name} ...", end="", flush=True)
        text = fetch_text(url)

        if not text or len(text) < MIN_TEXT_LENGTH:
            print(f"  FAILED (got {len(text) if text else 0} chars)")
            failed += 1
            time.sleep(RATE_LIMIT_SECONDS)
            continue

        print(f"  {len(text):,} chars", end="", flush=True)

        if args.dry_run:
            print("  [dry-run]")
        else:
            chunks = ingest_text(text, source=url, metadata={"name": name, "category": category})
            print(f"  → {chunks} chunks")
            ingested += 1

        time.sleep(RATE_LIMIT_SECONDS)

    print(f"\n{'='*50}")
    print(f"Done:  {ingested} ingested  |  {skipped} skipped  |  {failed} failed")
    print(f"Total chunks in DB after run: check Supabase dashboard")


if __name__ == "__main__":
    main()
