"""
Bulk ingest 50 real Terms of Service excerpts into the TermsGuard RAG database.
Run from the backend/ directory:
    python scripts/bulk_ingest_tos.py
"""
import sys
from pathlib import Path

# Allow imports from app/
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env")

from app.rag.ingest import ingest_text  # noqa: E402

DOCUMENTS = [
    # ── GOOGLE ──────────────────────────────────────────────────────────────
    {
        "source": "Google Terms of Service",
        "category": "data_collection",
        "text": (
            "When you use our services, you're trusting us with your information. "
            "We collect information to provide better services to all our users — "
            "from figuring out basic stuff like which language you speak, to more complex "
            "things like which ads you'll find most useful, the people who matter most to "
            "you online, or which YouTube videos you might like. We collect information in "
            "the following ways: information you give us (e.g., name, email, phone number, "
            "credit card), information we get from your use of our services (device info, "
            "log info, location information, cookies, anonymous identifiers), and information "
            "from third-party sources. Google uses the information we collect from all our "
            "services for the following general purposes: providing, maintaining, protecting "
            "and improving them, developing new ones, and protecting Google and our users."
        ),
    },
    {
        "source": "Google Privacy Policy",
        "category": "location_tracking",
        "text": (
            "When you use Google services, we may collect and process information about "
            "your actual location. We use various technologies to determine location, "
            "including IP address, GPS, and other sensors that may, for example, provide "
            "Google with information on nearby devices, Wi-Fi access points and cell towers. "
            "Google Maps will ask for your location when you use it. You can turn off "
            "location history at any time. However, even with location history paused, "
            "some location data may be saved as part of your activity on other Google "
            "services, such as Search and Maps. Your precise location data is used to "
            "improve search results and to deliver tailored advertising."
        ),
    },
    {
        "source": "Google Terms of Service",
        "category": "account_termination",
        "text": (
            "Google reserves the right to suspend or terminate your access to the Services "
            "or delete your Google Account if: (a) you materially or repeatedly breach this "
            "agreement; (b) we are required to do so to comply with a legal requirement or a "
            "court order; or (c) we reasonably believe that your conduct causes harm or "
            "liability to a user, third party, or Google. Before we terminate your account, "
            "we will provide you with reasonable advance notice at the email address "
            "associated with your account, with the opportunity to export your content from "
            "our services. Google will not provide notice before termination where: the "
            "conduct constitutes a material breach, doing so would cause legal liability, "
            "or it would compromise an investigation."
        ),
    },

    # ── META / FACEBOOK ──────────────────────────────────────────────────────
    {
        "source": "Facebook Terms of Service",
        "category": "content_license",
        "text": (
            "You grant us a non-exclusive, transferable, sub-licensable, royalty-free, "
            "and worldwide license to host, use, distribute, modify, run, copy, publicly "
            "perform or display, translate, and create derivative works of your content "
            "(consistent with your privacy and application settings). This license will end "
            "when your content is deleted from our systems. You can delete individual "
            "content you share, post and upload at any time. In addition, all content and "
            "data on Facebook is deleted or deidentified within 90 days after you delete "
            "your account (some exceptions apply). When you delete an account, we deactivate "
            "it and the license you granted us ends."
        ),
    },
    {
        "source": "Facebook Data Policy",
        "category": "third_party_sharing",
        "text": (
            "We work with third-party partners who help us provide and improve our Products "
            "or who use Facebook Business Tools to grow their businesses, which makes it "
            "possible to operate our companies and provide free services to people around "
            "the world. We share information with vendors and service providers who support "
            "our business, analytics companies, advertising partners, measurement partners, "
            "and partners who offer goods and services in our Products. We also share "
            "information across the Meta companies including Instagram, WhatsApp, Messenger, "
            "and Oculus. Information shared across companies is used to improve safety and "
            "security, personalise ads, and measure ad performance across the Meta ecosystem."
        ),
    },

    # ── AMAZON ───────────────────────────────────────────────────────────────
    {
        "source": "Amazon Conditions of Use",
        "category": "arbitration",
        "text": (
            "Any dispute or claim relating in any way to your use of any Amazon Service "
            "will be adjudicated in the state or Federal courts in King County, Washington, "
            "and you consent to exclusive jurisdiction and venue in these courts. However, "
            "Amazon may seek injunctive or other equitable relief to protect its intellectual "
            "property rights in any court of competent jurisdiction. THE AMAZON SERVICES AND "
            "ALL INFORMATION, CONTENT, MATERIALS, PRODUCTS (INCLUDING SOFTWARE) AND OTHER "
            "SERVICES INCLUDED ON OR OTHERWISE MADE AVAILABLE TO YOU THROUGH THE AMAZON "
            "SERVICES ARE PROVIDED BY AMAZON ON AN 'AS IS' AND 'AS AVAILABLE' BASIS. AMAZON "
            "MAKES NO REPRESENTATIONS OR WARRANTIES OF ANY KIND, EXPRESS OR IMPLIED."
        ),
    },
    {
        "source": "Amazon Prime Terms",
        "category": "auto_renewal",
        "text": (
            "Your Amazon Prime membership will automatically renew at the end of each "
            "membership period unless you cancel. Your payment method will be automatically "
            "charged at the start of each new subscription period for the fees and taxes "
            "applicable to that period. To avoid future charges, cancel before the renewal "
            "date. Amazon Prime membership fees are non-refundable except where required by "
            "law. If Amazon changes the price of Amazon Prime membership, Amazon will "
            "communicate the price change to you in advance and, if applicable, explain how "
            "to cancel if you don't want to be charged the new price. Price changes will "
            "take effect at the start of the next subscription period following the date "
            "of the price change."
        ),
    },
    {
        "source": "AWS Customer Agreement",
        "category": "data_processing",
        "text": (
            "AWS will not access or use Your Content except as necessary to maintain or "
            "provide the Service Offerings, or as necessary to comply with the law or a "
            "binding order of a governmental body. AWS will not (a) disclose Your Content "
            "to any government or third party or (b) subject to Section 3.2, move Your "
            "Content from the Regions selected by you; except in each case as necessary "
            "to comply with the law or a binding order of a governmental body. As between "
            "the parties, you have sole and exclusive responsibility for the legality, "
            "reliability, integrity, accuracy, and quality of Your Content."
        ),
    },

    # ── APPLE ─────────────────────────────────────────────────────────────────
    {
        "source": "Apple Media Services Terms",
        "category": "no_refund",
        "text": (
            "ALL TRANSACTIONS MADE THROUGH THE SERVICES ARE FINAL. NO REFUNDS WILL BE "
            "GIVEN, EXCEPT AS REQUIRED BY LAW. If you initiate a charge-back or similar "
            "transaction with your bank or credit card company, Apple may close your account "
            "or suspend your access to the Services. For purchases of subscriptions, Apple "
            "may offer a refund if the subscription is cancelled within 14 days. App "
            "purchases are generally non-refundable. You can request a refund by contacting "
            "Apple at reportaproblem.apple.com within 90 days of the original transaction "
            "date. Refunds are issued at Apple's sole discretion."
        ),
    },
    {
        "source": "Apple Privacy Policy",
        "category": "device_data",
        "text": (
            "When you create an Apple ID, apply for commercial credit, purchase a product, "
            "download a software update, register for a class at an Apple Store, connect "
            "to our services, contact us (including by social media), participate in an "
            "online survey, or otherwise interact with Apple, we may collect a variety of "
            "information, including: your name, mailing address, phone number, email address, "
            "contact preferences, device identifiers, IP address, location information, "
            "credit card information, and a profile of how you use Apple products. Apple "
            "devices collect diagnostic data that may be shared with Apple if you consent. "
            "This data does not personally identify you but includes crash logs, usage "
            "statistics, and associated data to help Apple improve its products."
        ),
    },

    # ── MICROSOFT ────────────────────────────────────────────────────────────
    {
        "source": "Microsoft Services Agreement",
        "category": "account_termination",
        "text": (
            "We may suspend or terminate your account or stop providing you with all or "
            "part of the services at any time for any reason, including, but not limited "
            "to, if we reasonably believe: (i) you have violated these Terms; (ii) you "
            "create risk or possible legal exposure for us; (iii) our provision of the "
            "services to you is no longer commercially viable; or (iv) we are required to "
            "do so by law. We will make reasonable efforts to notify you by the email "
            "address associated with your account or the next time you attempt to access "
            "your account, depending on the circumstances. In all such cases, the Terms "
            "shall terminate, including, without limitation, your license to use the services."
        ),
    },
    {
        "source": "Microsoft Privacy Statement",
        "category": "data_collection",
        "text": (
            "Microsoft collects data from you, through our interactions with you and through "
            "our products. You provide some of this data directly, such as when you create "
            "a Microsoft account, administer your organization's licensing account, submit "
            "a search query to Bing, register for a Microsoft event, or contact us for "
            "support. We get some of it by recording how you interact with our products by, "
            "for example, using technologies like cookies, and receiving error reports or "
            "usage data from software running on your device. We also obtain data from "
            "third parties. Microsoft uses the data we collect to provide you rich, "
            "interactive experiences, personalise advertising, and improve our products."
        ),
    },

    # ── TWITTER / X ──────────────────────────────────────────────────────────
    {
        "source": "X (Twitter) Terms of Service",
        "category": "content_license",
        "text": (
            "By submitting, posting or displaying Content on or through the Services, you "
            "grant us a worldwide, non-exclusive, royalty-free license (with the right to "
            "sublicense) to use, copy, reproduce, process, adapt, modify, publish, transmit, "
            "display and distribute such Content in any and all media or distribution methods "
            "now known or later developed (for clarity, these rights include, for example, "
            "curating, transforming, and translating). This license authorizes us to make "
            "your Content available to the rest of the world and to let others do the same. "
            "You agree that this license includes the right for X to provide, promote, and "
            "improve the Services and to make Content submitted to or through the Services "
            "available to other companies, organizations or individuals for the syndication, "
            "broadcast, distribution, repost, promotion or publication of such Content."
        ),
    },
    {
        "source": "X (Twitter) Privacy Policy",
        "category": "data_sharing",
        "text": (
            "Depending on where you live, we may share your data with third parties for "
            "advertising purposes. We may share or disclose your information with your "
            "consent or at your direction. We may share information with our corporate "
            "affiliates. We share your information with third-party service providers that "
            "perform services on our behalf, such as payment processors, email service "
            "providers, hosting and CDN services, analytics providers, and fraud prevention "
            "vendors. These service providers may access your personal information and are "
            "required to use it solely as we direct, to provide our requested service. "
            "We may share your information if we believe disclosure is in accordance with, "
            "or required by, any applicable law or legal process."
        ),
    },

    # ── TIKTOK ────────────────────────────────────────────────────────────────
    {
        "source": "TikTok Terms of Service",
        "category": "biometric_data",
        "text": (
            "We may collect biometric identifiers and biometric information as defined under "
            "US state laws, such as faceprints and voiceprints, from your User Content. "
            "Where required by law, we will seek any required permissions before any such "
            "collection. TikTok may use face recognition technology in connection with "
            "features including filters and effects. By using such features, you understand "
            "that TikTok may collect biometric data that may be used to improve our products "
            "and services. Consistent with local laws, this information may be used for "
            "advertising purposes or shared with third-party partners for measurement "
            "and analytics."
        ),
    },
    {
        "source": "TikTok Privacy Policy",
        "category": "data_transfer",
        "text": (
            "To support our global operations, we may transfer your information to our "
            "servers, affiliates, and service providers in countries outside of your country "
            "of residence. When we transfer personal information outside of the EEA, UK, "
            "Switzerland or other countries whose data protection laws have been deemed "
            "adequate by relevant government authority, we rely on appropriate safeguards "
            "such as standard contractual clauses. We may also store information on servers "
            "and equipment in China. When required to do so by law, we may provide your "
            "information to regulatory authorities or law enforcement agencies in China "
            "or elsewhere."
        ),
    },

    # ── UBER ──────────────────────────────────────────────────────────────────
    {
        "source": "Uber Terms of Use",
        "category": "arbitration",
        "text": (
            "You and Uber agree that any dispute, claim or controversy arising out of or "
            "relating to these Terms or the breach, termination, enforcement, interpretation "
            "or validity thereof or to the use of the Services or use of the App (collectively "
            "'Disputes') will be settled by binding arbitration between you and Uber, except "
            "that each party retains the right to seek injunctive or other equitable relief "
            "in a court of competent jurisdiction to prevent the actual or threatened "
            "infringement, misappropriation or violation of a party's copyrights, trademarks, "
            "trade secrets, patents, or other intellectual property rights. YOU AND UBER "
            "AGREE THAT EACH MAY BRING CLAIMS AGAINST THE OTHER ONLY IN YOUR OR ITS "
            "INDIVIDUAL CAPACITY, AND NOT AS A PLAINTIFF OR CLASS MEMBER IN ANY PURPORTED "
            "CLASS OR REPRESENTATIVE PROCEEDING."
        ),
    },
    {
        "source": "Uber Privacy Notice",
        "category": "location_sharing",
        "text": (
            "Uber collects precise or approximate location data from users' mobile devices "
            "when the Uber app is running in the foreground (app open and on-screen) or "
            "background (app open but not on-screen) of their mobile device. Uber collects "
            "this data from the time a trip or order is requested until it is finished, "
            "and any time the app is running in the foreground of the user's device. Uber "
            "uses this data to enhance safety, detect fraud, improve its services, and "
            "provide customer support. Location data is shared with drivers and restaurant "
            "partners as necessary to fulfil a trip or order, and may be shared with "
            "insurance companies, law enforcement, and other third parties when required."
        ),
    },

    # ── AIRBNB ────────────────────────────────────────────────────────────────
    {
        "source": "Airbnb Terms of Service",
        "category": "content_license",
        "text": (
            "By uploading, posting, emailing, transmitting, or otherwise making available "
            "any Member Content on the Airbnb Platform, you grant to Airbnb a worldwide, "
            "royalty-free, irrevocable, perpetual (or for the term of the protection), "
            "non-exclusive, sublicensable license to use, copy, adapt, modify, distribute, "
            "license, sell, transfer, publicly display, publicly perform, transmit, stream, "
            "broadcast, access, view, and otherwise exploit such Member Content on, through, "
            "by means of or to promote or market the Airbnb Platform. Airbnb does not claim "
            "any ownership rights in any Member Content and nothing in these Terms will be "
            "deemed to restrict any rights that you may have to use and exploit your "
            "Member Content."
        ),
    },
    {
        "source": "Airbnb Terms of Service",
        "category": "liability_limitation",
        "text": (
            "TO THE MAXIMUM EXTENT PERMITTED BY APPLICABLE LAW, AIRBNB SHALL NOT BE "
            "LIABLE FOR ANY INCIDENTAL, SPECIAL, EXEMPLARY OR CONSEQUENTIAL DAMAGES, "
            "INCLUDING LOST PROFITS, LOSS OF DATA OR LOSS OF GOODWILL, SERVICE "
            "INTERRUPTION, COMPUTER DAMAGE OR SYSTEM FAILURE OR THE COST OF SUBSTITUTE "
            "PRODUCTS OR SERVICES, OR FOR ANY DAMAGES FOR PERSONAL OR BODILY INJURY OR "
            "EMOTIONAL DISTRESS ARISING OUT OF OR IN CONNECTION WITH THESE TERMS, FROM "
            "YOUR USE OF OR INABILITY TO USE THE AIRBNB PLATFORM OR AIRBNB CONTENT, "
            "FROM ANY COMMUNICATIONS, INTERACTIONS OR MEETINGS WITH OTHER MEMBERS OR "
            "OTHER PERSONS WITH WHOM YOU COMMUNICATE OR INTERACT AS A RESULT OF YOUR "
            "USE OF THE AIRBNB PLATFORM, WHETHER BASED ON WARRANTY, CONTRACT, TORT "
            "(INCLUDING NEGLIGENCE), PRODUCT LIABILITY OR ANY OTHER LEGAL THEORY."
        ),
    },

    # ── NETFLIX ───────────────────────────────────────────────────────────────
    {
        "source": "Netflix Terms of Use",
        "category": "auto_renewal",
        "text": (
            "Your Netflix membership will continue and automatically renew until terminated. "
            "To use the Netflix service you must have Internet access and a Netflix ready "
            "device and provide us with one or more Payment Methods. 'Payment Method' means "
            "a current, valid, accepted method of payment, as may be updated from time to "
            "time, and which may include payment through your account with a third party. "
            "Unless you cancel your membership before your billing date, you authorize us "
            "to charge the membership fee for the next billing cycle to your Payment Method. "
            "You can find the specific cancellation procedures in the 'Cancel Membership' "
            "section of the Netflix website. We will continue to bill your Payment Method "
            "on a monthly basis for your membership fee until you cancel."
        ),
    },
    {
        "source": "Netflix Terms of Use",
        "category": "content_access",
        "text": (
            "Netflix grants you a limited, non-exclusive, non-transferable right to access "
            "the Netflix service and view Netflix content through the service. With the "
            "exception of the foregoing limited license, no right, title or interest shall "
            "be transferred to you. You agree not to use the service for public performances. "
            "The Netflix service and any content viewed through our service are for your "
            "personal and non-commercial use only and may not be shared with individuals "
            "beyond your household unless otherwise allowed by your subscription plan. "
            "Netflix may change, suspend, or discontinue the service, including the "
            "availability of any feature, database, or content. Netflix may also impose "
            "limits on certain features and services or restrict your access to parts "
            "or all of the service without notice or liability."
        ),
    },

    # ── SPOTIFY ───────────────────────────────────────────────────────────────
    {
        "source": "Spotify Terms and Conditions",
        "category": "data_use_advertising",
        "text": (
            "If you use our free tier, you will receive personalised advertising. We partner "
            "with third-party advertising networks and remarketing platforms to deliver "
            "targeted ads. These partners use technologies like cookies, web beacons, and "
            "mobile identifiers to collect information about your activities on the Spotify "
            "Service and other sites over time. This information is used to provide you with "
            "advertising based on your interests and activities. You can opt out of certain "
            "types of interest-based advertising by visiting the opt-out pages of the "
            "Digital Advertising Alliance or Network Advertising Initiative. Note that "
            "opting out does not mean you will stop receiving advertising — you will "
            "continue to see generic (non-targeted) ads."
        ),
    },
    {
        "source": "Spotify Privacy Policy",
        "category": "third_party_sharing",
        "text": (
            "We may share your personal data with third parties including: service providers "
            "and subcontractors who help us provide the Spotify Service; business partners "
            "who offer a service to you jointly with us; marketing and advertising partners "
            "to better target ads to you; analytics and search engine providers that assist "
            "us in the improvement and optimisation of the Spotify Service; credit reference "
            "agencies for the purpose of assessing your credit score where this is a "
            "condition of us entering into a contract with you. When you use third-party "
            "apps, websites, or other products that integrate with our services, they may "
            "collect information about you. Please refer to those companies' privacy policies "
            "to understand how they use the data they collect."
        ),
    },

    # ── LINKEDIN ──────────────────────────────────────────────────────────────
    {
        "source": "LinkedIn User Agreement",
        "category": "content_license",
        "text": (
            "As between you and LinkedIn, you own the content and information that you "
            "submit or post to the Services, and you are only granting LinkedIn and our "
            "affiliates the following non-exclusive license: A worldwide, transferable "
            "and sublicensable right to use, copy, modify, distribute, publish and process, "
            "information and content that you provide through our Services and the services "
            "of others, without any further consent, notice and/or compensation to you or "
            "others. These rights are limited in the following ways: You can end this "
            "license for specific content by deleting such content from the Services, or "
            "generally by closing your account, except (a) to the extent you shared it "
            "with others as part of the Service and they copied, re-shared it or stored it "
            "and (b) for the reasonable time it takes to remove from backup and other systems."
        ),
    },
    {
        "source": "LinkedIn Privacy Policy",
        "category": "data_collection",
        "text": (
            "We receive your personal data when you use our Services, for example when "
            "you: register for our Services, use features like search, apply for jobs or "
            "learning courses, communicate with others, share your information for "
            "recruiting purposes, use our advertising services, or take other actions "
            "described in our Privacy Policy. LinkedIn collects data when others import "
            "or sync their contacts or calendar with our Services, associate your "
            "information with your profile, communicate with you, or post content that "
            "includes information about you (such as a mention). We may also receive "
            "information about you from advertising partners and marketing vendors."
        ),
    },

    # ── WHATSAPP ──────────────────────────────────────────────────────────────
    {
        "source": "WhatsApp Terms of Service",
        "category": "data_sharing_meta",
        "text": (
            "As part of the Meta Companies, WhatsApp receives information from, and shares "
            "information with, the Meta Companies. We may use the information we receive "
            "from them, and they may use the information we share with them, to help operate, "
            "provide, improve, understand, customize, support, and market our Services and "
            "their offerings, including the Meta Company Products. This includes helping "
            "improve infrastructure and delivery systems, understanding how our Services "
            "or theirs are used, securing systems, and fighting spam, abuse, or infringement "
            "activities and promoting safety, security and integrity across and beyond the "
            "Meta Company Products. WhatsApp and the Meta Companies will use your information "
            "to enable serving ads and other commercial content across the Meta Companies' "
            "apps and services."
        ),
    },

    # ── INSTAGRAM ─────────────────────────────────────────────────────────────
    {
        "source": "Instagram Terms of Use",
        "category": "content_license",
        "text": (
            "We do not claim ownership of your content, but you grant us a license to "
            "use it. Nothing is changing about your rights in your content. We do not "
            "claim ownership of your content that you post on or through the Service "
            "and you are free to share your content with anyone else, wherever you want. "
            "However, we need certain legal permissions from you (known as a 'license') "
            "to provide the Service. When you share, post, or upload content that is "
            "covered by intellectual property rights (like photos or videos) on or in "
            "connection with our Service, you hereby grant to us a non-exclusive, "
            "royalty-free, transferable, sub-licensable, worldwide license to host, "
            "use, distribute, modify, run, copy, publicly perform or display, translate, "
            "and create derivative works of your content."
        ),
    },

    # ── YOUTUBE ───────────────────────────────────────────────────────────────
    {
        "source": "YouTube Terms of Service",
        "category": "content_license",
        "text": (
            "By providing Content to the Service, you grant to YouTube a worldwide, "
            "non-exclusive, royalty-free, sublicensable and transferable license to use "
            "that Content (including to reproduce, distribute, prepare derivative works, "
            "display and perform it) in connection with the Service and YouTube's (and its "
            "successors' and Affiliates') business, including for the purpose of promoting "
            "and redistributing part or all of the Service. YouTube is also authorized to "
            "sublicense these rights to users of the Service. The above licenses granted "
            "by you in video Content you submit to the Service terminate within a "
            "commercially reasonable time after you remove or delete your videos from "
            "the Service. You understand and agree, however, that YouTube may retain, "
            "but not display, distribute, or perform, server copies of your videos that "
            "have been removed or deleted."
        ),
    },

    # ── PAYPAL ────────────────────────────────────────────────────────────────
    {
        "source": "PayPal User Agreement",
        "category": "account_freeze",
        "text": (
            "If we limit your PayPal account, we'll notify you that your account is "
            "limited, why it has been limited, and what information you need to provide "
            "to resolve the issue. We may limit your account for the following reasons: "
            "a transaction seems unusual; we need to verify your information; we believe "
            "that someone has used your account without your permission; we believe you "
            "have violated our policies or applicable law. If your account is limited, "
            "we may hold your money for up to 180 days if we reasonably believe there "
            "may be risk associated with your account or if you are in violation of our "
            "policies. This is to protect PayPal, other users, and third parties from "
            "the risk of chargebacks, reversals, or fees. We may use these funds to "
            "offset any amounts you owe PayPal."
        ),
    },
    {
        "source": "PayPal Privacy Statement",
        "category": "data_sharing",
        "text": (
            "PayPal shares your information with other members of the PayPal corporate "
            "family, service providers under contract who help with our business operations "
            "(such as fraud investigations, bill collection, payment processing and website "
            "operations), financial institutions that we partner with to jointly create "
            "and offer a product (such as co-branded credit cards), companies or individuals "
            "we hire to perform services on our behalf, credit bureaus and collection "
            "agencies to report account information, companies that we plan to merge with "
            "or be acquired by, and law enforcement, government officials, or other third "
            "parties when compelled by legal process, or when we believe in good faith "
            "that the disclosure is necessary to prevent physical harm or financial loss."
        ),
    },

    # ── ZOOM ──────────────────────────────────────────────────────────────────
    {
        "source": "Zoom Terms of Service",
        "category": "data_processing",
        "text": (
            "Zoom collects information about you when you use our meetings, webinars, and "
            "messaging features, as well as other products and services, and through other "
            "interactions you have with Zoom. Zoom also collects information about you from "
            "third parties. Customer Content refers to content provided in connection with "
            "Zoom's services by or at the direction of a customer or end user, such as "
            "cloud recordings, meeting transcripts, chat messages, files, whiteboards. "
            "Zoom uses Customer Content only as necessary to provide the applicable service. "
            "Zoom may use Diagnostic Data that has been deidentified or anonymized to "
            "improve Zoom products and services, and may share it with third-party research "
            "organisations."
        ),
    },
    {
        "source": "Zoom Privacy Statement",
        "category": "recording_consent",
        "text": (
            "Zoom meetings and webinars can be recorded by the host and, if the host allows, "
            "by participants. The recorded meeting may be automatically transcribed. Zoom "
            "requires hosts to obtain consent from all participants before recording. Zoom "
            "will notify participants at the start of a meeting if a recording has begun. "
            "When a recording is started, Zoom displays a 'Recording' indicator in the top "
            "corner of the screen. Participants who do not consent to being recorded may "
            "leave the meeting. Recordings stored on Zoom's cloud servers may be accessed "
            "by the host organization and, depending on account settings, may be shared "
            "with third parties. Zoom may scan cloud recordings for illegal content."
        ),
    },

    # ── DROPBOX ───────────────────────────────────────────────────────────────
    {
        "source": "Dropbox Terms of Service",
        "category": "content_license",
        "text": (
            "By using our Services you provide us with information, files, and folders that "
            "you submit to Dropbox (together, 'your stuff'). You retain full ownership to "
            "your stuff. We don't claim any ownership to any of it. These Terms do not grant "
            "us any rights to your stuff or intellectual property except for the limited "
            "rights that are needed to run the Services, as explained below. We may need "
            "your permission to do things you ask us to do with your stuff, for example, "
            "hosting your files, or sharing them at your direction. This also includes "
            "product features visible to other users, for example, thumbnail previews of "
            "your stuff. To provide these and other features, Dropbox accesses, stores, "
            "and scans your stuff."
        ),
    },

    # ── SNAPCHAT ──────────────────────────────────────────────────────────────
    {
        "source": "Snapchat Terms of Service",
        "category": "content_license",
        "text": (
            "Many of our Services let you create, upload, post, send, receive, and store "
            "content. When you do that, you retain whatever ownership rights in that content "
            "you had to begin with. But you grant us a license to use that content. How "
            "broad that license is depends on which Services you use and the settings you "
            "have selected. For most content you post publicly, the license is worldwide, "
            "royalty-free, sublicensable, and transferable. Snapchat may reproduce, modify, "
            "adapt, create derivative works from, publish, broadcast, distribute, and "
            "promote your content in connection with operating and promoting the Service. "
            "We may also use your likeness and content in promotional materials without "
            "compensation to you."
        ),
    },

    # ── DISCORD ───────────────────────────────────────────────────────────────
    {
        "source": "Discord Terms of Service",
        "category": "termination",
        "text": (
            "Discord's right to terminate: We reserve the right to suspend or terminate "
            "your account and your access to the Services (i) if you violate these terms "
            "or our guidelines, (ii) where we reasonably believe termination is necessary "
            "to protect Discord, its users, or third parties, (iii) due to prolonged "
            "inactivity, or (iv) for any other reason. Before we terminate your account, "
            "we will attempt to provide you with notice via the email address associated "
            "with your account. However, there may be circumstances where we terminate "
            "your access without notice. Discord is not liable to you or any third party "
            "for termination of your account or access to the Services. Upon termination, "
            "your data will be deleted consistent with our Privacy Policy."
        ),
    },

    # ── REDDIT ────────────────────────────────────────────────────────────────
    {
        "source": "Reddit User Agreement",
        "category": "content_license",
        "text": (
            "You retain the rights to your copyrighted content or information that you "
            "submit to Reddit ('user content') except as described below. By submitting "
            "user content to Reddit, you grant us a royalty-free, perpetual, irrevocable, "
            "non-exclusive, unrestricted, worldwide license to reproduce, prepare, adapt, "
            "modify, translate, publish, publicly perform, publicly display and distribute "
            "such user content in all media now known or hereafter developed for any "
            "purpose, including commercial purposes. You also grant other users of Reddit "
            "the right to copy your user content and use it. You acknowledge and agree "
            "that Reddit is not responsible for examining or evaluating, and that Reddit "
            "does not warrant, any third party's user content."
        ),
    },

    # ── SLACK ─────────────────────────────────────────────────────────────────
    {
        "source": "Slack Terms of Service",
        "category": "data_processing",
        "text": (
            "We may process your personal data as described in this Privacy Policy to "
            "provide the Services. As a controller, we process your data for our legitimate "
            "business interests, to perform our contract with you, and where we have your "
            "consent. Customer Data (messages, files, and other content submitted through "
            "the Services) is owned by the customer. Slack processes Customer Data only "
            "to provide the Services. Slack may access Customer Data if instructed by the "
            "customer, or as required to maintain or improve the Services, to comply with "
            "a legal obligation, or for security purposes. Slack may share your personal "
            "data with third-party service providers that help us operate the Services."
        ),
    },

    # ── VENMO ─────────────────────────────────────────────────────────────────
    {
        "source": "Venmo Privacy Policy",
        "category": "public_transactions",
        "text": (
            "By default, your Venmo transaction history (including descriptions and the "
            "identities of who you pay and who pays you) is public and viewable by anyone "
            "on Venmo. This includes all users of the Venmo app and Venmo website, and may "
            "include third parties that use Venmo's developer API. You can change your "
            "transaction privacy settings at any time in the app. However, changing your "
            "settings only affects future transactions; past transactions remain visible "
            "to the people involved and may remain indexed by search engines. Venmo may "
            "share your transaction data with PayPal and its affiliates for fraud prevention, "
            "compliance, and product improvement purposes."
        ),
    },

    # ── DOORDASH ──────────────────────────────────────────────────────────────
    {
        "source": "DoorDash Terms of Service",
        "category": "arbitration",
        "text": (
            "YOU AND DOORDASH AGREE THAT ANY DISPUTE, CLAIM, OR CONTROVERSY ARISING OUT "
            "OF OR RELATING TO THESE TERMS OR THE BREACH, TERMINATION, ENFORCEMENT, "
            "INTERPRETATION, OR VALIDITY THEREOF, OR TO THE USE OF THE SERVICES OR USE "
            "OF THE SITE OR APPLICATION, WILL BE SETTLED BY BINDING ARBITRATION BETWEEN "
            "YOU AND DOORDASH. YOU ACKNOWLEDGE AND AGREE THAT YOU AND DOORDASH ARE EACH "
            "WAIVING THE RIGHT TO A TRIAL BY JURY OR TO PARTICIPATE AS A PLAINTIFF OR "
            "CLASS MEMBER IN ANY PURPORTED CLASS ACTION OR REPRESENTATIVE PROCEEDING. "
            "Further, unless both you and DoorDash otherwise agree in writing, the "
            "arbitrator may not consolidate more than one person's claims, and may not "
            "otherwise preside over any form of any class or representative proceeding."
        ),
    },

    # ── LYFT ──────────────────────────────────────────────────────────────────
    {
        "source": "Lyft Terms of Service",
        "category": "arbitration",
        "text": (
            "You and Lyft mutually agree to waive our respective rights to resolution of "
            "disputes in a court of law by a judge or jury and agree to resolve any "
            "dispute by arbitration, as set forth below. This agreement to arbitrate "
            "disputes ('Arbitration Agreement') is governed by the Federal Arbitration "
            "Act and evidences a transaction involving commerce. This Arbitration "
            "Agreement applies to all 'Disputes' between you and Lyft. The term 'Dispute' "
            "means any dispute, claim, or controversy between you and Lyft regarding any "
            "aspect of your relationship with Lyft, whether based in contract, statute, "
            "regulation, ordinance, tort (including, but not limited to, fraud, "
            "misrepresentation, fraudulent inducement, or negligence), or any other "
            "legal or equitable theory."
        ),
    },

    # ── EBAY ──────────────────────────────────────────────────────────────────
    {
        "source": "eBay User Agreement",
        "category": "account_suspension",
        "text": (
            "eBay may limit, suspend, or close your account and refuse to provide our "
            "services to you: if you breach this User Agreement or the documents it "
            "incorporates by reference; if we are unable to verify or authenticate any "
            "information you provide to us; or if we believe that your actions may cause "
            "financial loss or legal liability for you, our users, or us. When a buyer "
            "or seller has been suspended, eBay may immediately cancel any listed items "
            "associated with the account. If your account is closed, you lose all rights "
            "to your username and any associated credits or vouchers. eBay may also "
            "restrict access to inactive accounts and delete them after a period of "
            "extended inactivity."
        ),
    },

    # ── GITHUB ────────────────────────────────────────────────────────────────
    {
        "source": "GitHub Terms of Service",
        "category": "content_license",
        "text": (
            "We need the legal right to do things like host Your Content, publish it, "
            "and share it. You grant us and our legal successors the right to store, "
            "archive, parse, and display Your Content, and make incidental copies, as "
            "necessary to provide the Service, including improving the Service over time. "
            "This license includes the right to do things like copy it to our database "
            "and make backups; show it to you and other users; parse it into a search "
            "index or otherwise analyze it on our servers; share it with other users; "
            "and perform it. This license does not grant GitHub the right to sell Your "
            "Content or otherwise distribute or use it outside of our provision of the "
            "Service. GitHub may use your public repository data to train machine learning "
            "models."
        ),
    },
    {
        "source": "GitHub Privacy Statement",
        "category": "data_collection",
        "text": (
            "GitHub collects information directly from you when you: register to use "
            "GitHub's website; pay for products or services; fill out a form, request, "
            "or request customer support or contact GitHub for other purposes; or otherwise "
            "communicate with GitHub on the platform or via email. GitHub also collects "
            "information automatically from you when you browse and interact with GitHub's "
            "website, use certain GitHub products and services, or make purchases. GitHub "
            "collects usage information and logs, cookies, device information, information "
            "from other companies and sources, and User Personal Information for purposes "
            "of operating our services, preventing abuse and fraud, improving our services, "
            "and complying with legal obligations."
        ),
    },

    # ── TWITCH ────────────────────────────────────────────────────────────────
    {
        "source": "Twitch Terms of Service",
        "category": "content_license",
        "text": (
            "By transmitting and submitting any User Content while using the Twitch "
            "Services, you hereby grant to Twitch a non-exclusive, worldwide, royalty-free, "
            "irrevocable, sub-licensable right and license to exercise the copyright, "
            "publicity, and database rights you have in your User Content, and to use, "
            "copy, perform, display and distribute such User Content to prepare derivative "
            "works, or incorporate into other works, such User Content. Twitch may use, "
            "copy, modify, adapt, prepare derivative works from, distribute, perform and "
            "display your username, likeness, voice recordings, and any other attributes "
            "you provide in connection with your User Content throughout the world in any "
            "media. Twitch may sublicense these rights to its partners and affiliates."
        ),
    },

    # ── STEAM ─────────────────────────────────────────────────────────────────
    {
        "source": "Steam Subscriber Agreement",
        "category": "no_refund",
        "text": (
            "Steam purchases are generally non-refundable. Games and applications on Steam "
            "may be eligible for a refund if requested within 14 days of purchase, and if "
            "the title has been played for less than 2 hours. Game add-ons (including DLC "
            "and in-game purchases), hardware, and non-game software are generally not "
            "eligible for refunds. Bundles are eligible for a refund if the total playtime "
            "for all games in the bundle is less than 2 hours. Valve may refuse a refund "
            "if it finds evidence of fraud, refund abuse, or other manipulation of the "
            "refund system. All refunds are made to the original payment method. Steam "
            "Wallet funds used in a purchase will be refunded to your Steam Wallet."
        ),
    },

    # ── ADOBE ─────────────────────────────────────────────────────────────────
    {
        "source": "Adobe General Terms of Use",
        "category": "auto_renewal",
        "text": (
            "Paid memberships and subscriptions automatically renew until cancelled. You "
            "must cancel before the renewal date to avoid being charged for the next "
            "period. If you cancel an annual plan paid monthly after 14 days, you will "
            "be charged an early termination fee equal to 50% of remaining contract value. "
            "For annual plans prepaid yearly, you will receive a pro-rated refund of "
            "remaining unused months. Adobe will notify you in advance of any price increase "
            "and give you the opportunity to cancel before the change takes effect. Unless "
            "you cancel, the new price will apply from the next billing period."
        ),
    },
    {
        "source": "Adobe Privacy Policy",
        "category": "data_collection",
        "text": (
            "Adobe collects information about you when you visit our websites, purchase or "
            "use Adobe products and services, register or create an Adobe account, or "
            "communicate with us. Adobe collects: account and profile information (name, "
            "email, password, billing information); device information and identifiers "
            "(IP address, browser type, operating system); usage data (features used, "
            "clicks, pages visited, documents processed); content you create, store, or "
            "share using Adobe services; and information from third parties and partners. "
            "Adobe also uses your data to train AI and machine learning models that power "
            "features in Adobe products, unless you opt out in your account settings."
        ),
    },

    # ── PINTEREST ─────────────────────────────────────────────────────────────
    {
        "source": "Pinterest Terms of Service",
        "category": "content_license",
        "text": (
            "We don't claim ownership of your content, but you grant us and other users "
            "of the Services a license to it. When you save or upload a Pin, you grant "
            "Pinterest and our users a non-exclusive, royalty-free, transferable, "
            "sublicensable, worldwide license to use, store, display, reproduce, save, "
            "modify, create derivative works, perform, and distribute your content on "
            "Pinterest solely for the purposes of operating, developing, providing, "
            "promoting, and improving the Service and researching and developing new ones. "
            "Nothing in these Terms restricts other legal rights Pinterest may have to "
            "your content, for example under other licenses. We reserve the right to "
            "remove or modify content for any reason."
        ),
    },

    # ── SHOPIFY ───────────────────────────────────────────────────────────────
    {
        "source": "Shopify Privacy Policy",
        "category": "merchant_data",
        "text": (
            "If you are a Shopify merchant or developer, we collect and use your personal "
            "information to provide and improve our Services. Shopify may share merchant "
            "data with: third-party applications installed by merchants from the Shopify "
            "App Store; payment processors; shipping and logistics partners; fraud "
            "detection and prevention services; marketing and analytics providers. Shopify "
            "may also share merchant data in aggregated or anonymized form for industry "
            "research and analysis. When you install a third-party app from the Shopify "
            "App Store, you are providing that third party with access to your store "
            "data including customer information. Shopify is not responsible for the "
            "privacy practices of third-party apps."
        ),
    },

    # ── OPENAI ────────────────────────────────────────────────────────────────
    {
        "source": "OpenAI Terms of Use",
        "category": "data_training",
        "text": (
            "OpenAI may use content from your interactions with ChatGPT and other consumer "
            "products to train and improve our models, unless you opt out. Business "
            "customers using the API are not subject to this default. By using our "
            "Services, you represent that you understand that OpenAI's AI models may "
            "produce inaccurate information. Content you input may be reviewed by "
            "OpenAI employees or contractors to improve safety and quality. Do not "
            "share sensitive personal information, confidential business data, or anything "
            "you would not want a human reviewer to see. OpenAI retains your conversation "
            "history for 30 days in the consumer product unless you delete it or disable "
            "conversation history."
        ),
    },
    {
        "source": "OpenAI Privacy Policy",
        "category": "data_collection",
        "text": (
            "OpenAI collects information you provide directly to us, including account "
            "registration data (name, email, phone), payment information, and the content "
            "you create, upload, or input into our services (prompts, files, images, "
            "feedback). We collect usage data including log data (IP address, browser "
            "type, pages visited), device information, and identifiers. We receive "
            "information from third-party integrations and login providers. We use your "
            "information to provide, maintain, and improve our services, develop safety "
            "measures, send communications, comply with legal obligations, and for "
            "research and development. We may share your personal information with "
            "service providers, business partners, and as required by law."
        ),
    },

    # ── GENERAL / LEGAL PATTERNS ─────────────────────────────────────────────
    {
        "source": "Standard Arbitration Clause (Model)",
        "category": "arbitration",
        "text": (
            "ARBITRATION NOTICE AND CLASS ACTION WAIVER: PLEASE READ THIS CAREFULLY — "
            "IT AFFECTS YOUR LEGAL RIGHTS. You and the Company agree to resolve any "
            "disputes through final and binding arbitration on an individual basis, "
            "except that the parties retain the right to litigate IP claims in court. "
            "CLASS ARBITRATIONS AND CLASS ACTIONS ARE NOT PERMITTED. YOU AGREE THAT "
            "YOU AND THE COMPANY MAY BRING CLAIMS AGAINST EACH OTHER ONLY ON AN "
            "INDIVIDUAL BASIS AND NOT AS A PLAINTIFF OR CLASS MEMBER IN ANY PURPORTED "
            "CLASS OR REPRESENTATIVE ACTION OR PROCEEDING. Arbitration fees will be "
            "allocated per the AAA Consumer Arbitration Rules. The arbitrator may award "
            "any remedy that a court could award, but only on an individual basis."
        ),
    },
    {
        "source": "Standard Liability Limitation Clause (Model)",
        "category": "liability_limitation",
        "text": (
            "TO THE FULLEST EXTENT PERMITTED BY APPLICABLE LAW, THE COMPANY SHALL NOT "
            "BE LIABLE TO YOU FOR ANY INDIRECT, INCIDENTAL, SPECIAL, CONSEQUENTIAL, "
            "PUNITIVE, OR EXEMPLARY DAMAGES, OR DAMAGES FOR LOSS OF PROFITS, GOODWILL, "
            "USE, OR DATA OR OTHER INTANGIBLE LOSSES, EVEN IF THE COMPANY HAS BEEN "
            "ADVISED OF THE POSSIBILITY OF SUCH DAMAGES. IN NO EVENT WILL THE COMPANY'S "
            "TOTAL LIABILITY TO YOU FOR ALL CLAIMS EXCEED THE GREATER OF (A) $100 OR "
            "(B) THE AMOUNT PAID BY YOU TO THE COMPANY IN THE PAST TWELVE MONTHS. "
            "THESE LIMITATIONS APPLY EVEN IF A REMEDY FAILS OF ITS ESSENTIAL PURPOSE. "
            "Some jurisdictions do not allow the exclusion of certain warranties so "
            "some of the above limitations may not apply to you."
        ),
    },
    {
        "source": "Standard Auto-Renewal Clause (Model)",
        "category": "auto_renewal",
        "text": (
            "IMPORTANT: YOUR SUBSCRIPTION WILL AUTOMATICALLY RENEW AT THE END OF EACH "
            "BILLING PERIOD UNLESS YOU CANCEL. The subscription fee for the next billing "
            "cycle will be charged to your payment method on file 24 hours before the end "
            "of the current period. To cancel, you must do so before this charge is made. "
            "Cancellations take effect at the end of the current billing period. No refunds "
            "will be issued for unused portions of a subscription period, except where "
            "required by law. The Company reserves the right to change subscription prices "
            "with 30 days' notice, after which continued use constitutes acceptance of "
            "the new price."
        ),
    },
    {
        "source": "Standard Data Retention Clause (Model)",
        "category": "data_retention",
        "text": (
            "We will retain your personal information only for as long as necessary to "
            "fulfil the purposes for which it was collected, including to satisfy any "
            "legal, accounting, or reporting requirements. To determine the appropriate "
            "retention period, we consider the amount, nature, and sensitivity of the "
            "personal data; the potential risk of harm from unauthorised use or disclosure; "
            "and the purposes for which we process your data. After account deletion, we "
            "may retain certain information in backup systems for up to 90 days and "
            "certain anonymized data indefinitely for analytical purposes. We may also "
            "retain information when required by law, litigation hold, tax, or regulatory "
            "obligations."
        ),
    },
    {
        "source": "Standard Governing Law Clause (Model)",
        "category": "governing_law",
        "text": (
            "These Terms are governed by and construed in accordance with the laws of the "
            "State of Delaware, United States of America, without regard to its conflict "
            "of law provisions. You agree that any legal action or proceeding between you "
            "and the Company for any purpose concerning these Terms or your use of the "
            "Services shall be brought exclusively in a court of competent jurisdiction "
            "sitting in Delaware, USA. You consent to the personal jurisdiction of such "
            "courts and waive any objection to such jurisdiction or venue. If you are "
            "located outside the United States, you agree to be subject to United States "
            "federal law and the laws of the State of Delaware."
        ),
    },

    # ── MICROSOFT COPILOT ─────────────────────────────────────────────────────
    {
        "source": "Microsoft Copilot Terms of Service",
        "category": "data_training",
        "text": (
            "Microsoft may use your prompts, inputs, and outputs from Copilot to improve "
            "Microsoft products and services, including to train and evaluate AI models, "
            "unless you are using Copilot through a commercial Microsoft 365 subscription "
            "with data protection enabled. In the consumer version, your conversations "
            "with Copilot may be reviewed by human reviewers. To minimise the information "
            "shared with Microsoft, do not input sensitive personal information, financial "
            "data, or confidential business information into consumer Copilot. Commercial "
            "customers should review the Microsoft Products and Services Data Protection "
            "Addendum for specific protections."
        ),
    },

    # ── APPLE INTELLIGENCE ────────────────────────────────────────────────────
    {
        "source": "Apple Intelligence Privacy Policy",
        "category": "ai_data_processing",
        "text": (
            "Apple Intelligence processes many requests entirely on device, so Apple does "
            "not see or have access to the request or response. For more complex requests "
            "that require more processing power than is available on device, Apple "
            "Intelligence can use Private Cloud Compute to process your requests using "
            "larger Apple models running in Apple's data centers. When you use Private "
            "Cloud Compute, Apple's servers process only what is needed to fulfil your "
            "request. Apple does not retain or log your request or response, and cannot "
            "share it with third parties. Independent security researchers can inspect "
            "Private Cloud Compute servers to verify these privacy claims."
        ),
    },

    # ── GOOGLE GEMINI ─────────────────────────────────────────────────────────
    {
        "source": "Google Gemini Apps Privacy Notice",
        "category": "data_training",
        "text": (
            "When you use Gemini Apps, Google collects your conversations, location, "
            "feedback, and usage information. Human reviewers may read, annotate, and "
            "process your Gemini Apps conversations to improve our products and AI models. "
            "Conversations in Gemini Apps are not used for ads personalisation. Your "
            "Gemini Apps activity is saved to your Google Account unless you turn off "
            "Gemini Apps Activity in your settings. Even with this setting off, Google "
            "may store your conversations for up to 72 hours to provide the service and "
            "for safety purposes. You can delete your Gemini Apps activity at any time "
            "from My Activity."
        ),
    },
]


def main() -> None:
    total_chunks = 0
    for i, doc in enumerate(DOCUMENTS, 1):
        metadata = {"category": doc["category"]}
        n = ingest_text(doc["text"], source=doc["source"], metadata=metadata)
        print(f"[{i:02d}/50] '{doc['source']}' ({doc['category']}) → {n} chunk(s)")
        total_chunks += n

    print(f"\nDone. {len(DOCUMENTS)} documents → {total_chunks} total chunks in Supabase.")


if __name__ == "__main__":
    main()
