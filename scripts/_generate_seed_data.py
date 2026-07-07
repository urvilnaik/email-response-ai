"""One-off helper to generate seed, negative, and sanity JSONL files."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

SEED_PAIRS = [
    {
        "id": "seed_001",
        "category": "billing",
        "urgency": "high",
        "tone": "apologetic",
        "incoming_email": {
            "subject": "Double charge on order #12345",
            "body": "I was charged twice for order #12345 on my Visa ending in 4421. Please refund the duplicate charge immediately.",
            "from": "sarah.chen@email.com",
        },
        "reply": {
            "body": "Hi Sarah,\n\nThank you for reaching out. I confirmed a duplicate charge of $49.99 on order #12345 and have initiated a refund. You should see the credit within 5-7 business days on your Visa ending in 4421.\n\nPlease let me know if you have any other questions.\n\nBest regards,\nSupport Team",
            "tone": "professional",
        },
        "metadata": {
            "quality": "clean",
            "intent": ["refund_request", "duplicate_charge"],
            "actions": ["confirm_order_id", "process_refund_5_7_days"],
        },
    },
    {
        "id": "seed_002",
        "category": "billing",
        "urgency": "high",
        "tone": "apologetic",
        "incoming_email": {
            "subject": "charged twice fix this asap!!!",
            "body": "charged twice fix this asap!!! order 12345 my card got hit 2x",
            "from": "mike.r@email.com",
        },
        "reply": {
            "body": "Hi Mike,\n\nI'm sorry about the duplicate charge on order #12345. I've verified the issue and started a refund for the extra charge. The credit should appear within 5-7 business days.\n\nBest regards,\nSupport Team",
            "tone": "professional",
        },
        "metadata": {
            "quality": "messy",
            "intent": ["refund_request", "duplicate_charge"],
            "actions": ["confirm_order_id", "process_refund_5_7_days"],
        },
    },
    {
        "id": "seed_003",
        "category": "billing",
        "urgency": "medium",
        "tone": "informative",
        "incoming_email": {
            "subject": "Invoice question for March subscription",
            "body": "Can you explain the $29 line item on my March invoice? I thought my plan was $19/month.",
            "from": "alex.j@corp.com",
        },
        "reply": {
            "body": "Hi Alex,\n\nThe $29 charge reflects your Pro plan ($19) plus a one-time add-on for extra storage ($10) activated on March 3. I've attached a detailed breakdown. Let me know if you'd like to remove the add-on.\n\nBest,\nBilling Team",
            "tone": "professional",
        },
        "metadata": {
            "quality": "clean",
            "intent": ["invoice_inquiry"],
            "actions": ["explain_line_item", "offer_addon_removal"],
        },
    },
    {
        "id": "seed_004",
        "category": "support",
        "urgency": "high",
        "tone": "helpful",
        "incoming_email": {
            "subject": "Export feature crashes on CSV files",
            "body": "Every time I try to export my project data as CSV, the app crashes. I'm on macOS 14 and using version 3.2.1.",
            "from": "dev.user@startup.io",
        },
        "reply": {
            "body": "Hi there,\n\nThank you for the detailed report. This is a known issue in v3.2.1 affecting CSV exports on macOS 14. Our engineering team released a fix in v3.2.2 — please update via Settings > About > Check for Updates. If the crash persists after updating, reply with your project ID and we'll investigate further.\n\nBest,\nTechnical Support",
            "tone": "professional",
        },
        "metadata": {
            "quality": "clean",
            "intent": ["bug_report", "export_issue"],
            "actions": ["acknowledge_known_issue", "recommend_update_3_2_2", "offer_followup"],
        },
    },
    {
        "id": "seed_005",
        "category": "support",
        "urgency": "high",
        "tone": "helpful",
        "incoming_email": {
            "subject": "it dont work when i export fix it",
            "body": "it dont work when i export fix it csv keeps crashing",
            "from": "frustrated@gmail.com",
        },
        "reply": {
            "body": "Hi,\n\nSorry you're running into crashes when exporting CSV files. Please update to version 3.2.2, which includes a fix for this issue. Go to Settings > About > Check for Updates. If it still crashes, send us your project ID and we'll help right away.\n\nBest,\nTechnical Support",
            "tone": "professional",
        },
        "metadata": {
            "quality": "messy",
            "intent": ["bug_report", "export_issue"],
            "actions": ["recommend_update_3_2_2", "offer_followup"],
        },
    },
    {
        "id": "seed_006",
        "category": "support",
        "urgency": "medium",
        "tone": "helpful",
        "incoming_email": {
            "subject": "How do I reset my API key?",
            "body": "I accidentally shared my API key in a public repo. How can I rotate it?",
            "from": "security@devshop.com",
        },
        "reply": {
            "body": "Hi,\n\nFor security, please rotate your API key immediately: go to Dashboard > Settings > API Keys > Regenerate. The old key will be revoked within 5 minutes. Also review your repo history and remove any exposed credentials.\n\nBest,\nSecurity Team",
            "tone": "professional",
        },
        "metadata": {
            "quality": "clean",
            "intent": ["api_key_rotation"],
            "actions": ["provide_rotation_steps", "advise_revoke_old_key"],
        },
    },
    {
        "id": "seed_007",
        "category": "complaints",
        "urgency": "high",
        "tone": "empathetic",
        "incoming_email": {
            "subject": "My delivery is 2 weeks late",
            "body": "I ordered on March 1 and still haven't received my package. Tracking hasn't updated in 10 days. This is unacceptable.",
            "from": "angry.customer@mail.com",
        },
        "reply": {
            "body": "Hi,\n\nI'm truly sorry your order is significantly delayed. I've escalated this with our shipping partner and initiated a replacement shipment at no cost, expected to arrive within 3-5 business days. You'll also receive a 20% credit on your next order. I'll personally monitor tracking and update you within 24 hours.\n\nSincerely,\nCustomer Care",
            "tone": "empathetic",
        },
        "metadata": {
            "quality": "clean",
            "intent": ["shipping_delay", "complaint"],
            "actions": ["escalate_shipping", "send_replacement", "offer_credit_20_percent", "followup_24h"],
        },
    },
    {
        "id": "seed_008",
        "category": "complaints",
        "urgency": "high",
        "tone": "empathetic",
        "incoming_email": {
            "subject": "where is my stuff??? still waiting",
            "body": "where is my stuff??? still waiting 2 weeks now this is ridiculous",
            "from": "impatient@yahoo.com",
        },
        "reply": {
            "body": "Hi,\n\nI completely understand your frustration — waiting two weeks is not acceptable. I've escalated with our carrier and arranged a free replacement shipment arriving in 3-5 business days. You'll also get 20% off your next order. I'll update you within 24 hours.\n\nSincerely,\nCustomer Care",
            "tone": "empathetic",
        },
        "metadata": {
            "quality": "messy",
            "intent": ["shipping_delay", "complaint"],
            "actions": ["escalate_shipping", "send_replacement", "offer_credit_20_percent", "followup_24h"],
        },
    },
    {
        "id": "seed_009",
        "category": "complaints",
        "urgency": "medium",
        "tone": "empathetic",
        "incoming_email": {
            "subject": "Product arrived damaged",
            "body": "The laptop stand I received has a cracked base. I'd like a replacement, not a refund.",
            "from": "buyer@shop.com",
        },
        "reply": {
            "body": "Hi,\n\nI'm sorry your laptop stand arrived damaged. I've arranged a replacement shipment — no need to return the damaged item. The new unit should arrive within 5-7 business days. Please reply with a photo if you'd like us to file a carrier claim.\n\nBest,\nCustomer Care",
            "tone": "empathetic",
        },
        "metadata": {
            "quality": "clean",
            "intent": ["damaged_product", "replacement_request"],
            "actions": ["arrange_replacement", "no_return_needed", "timeline_5_7_days"],
        },
    },
    {
        "id": "seed_010",
        "category": "account_access",
        "urgency": "high",
        "tone": "helpful",
        "incoming_email": {
            "subject": "Locked out of my account",
            "body": "I tried logging in too many times and now my account is locked. I need access for a client presentation tomorrow.",
            "from": "consultant@work.com",
        },
        "reply": {
            "body": "Hi,\n\nI've unlocked your account. Please reset your password using the link I sent to your registered email. For future lockouts, use 'Forgot Password' on the login page or contact us before the 5-attempt limit.\n\nGood luck with your presentation!\n\nBest,\nAccount Support",
            "tone": "professional",
        },
        "metadata": {
            "quality": "clean",
            "intent": ["account_lockout"],
            "actions": ["unlock_account", "send_password_reset"],
        },
    },
    {
        "id": "seed_011",
        "category": "account_access",
        "urgency": "medium",
        "tone": "helpful",
        "incoming_email": {
            "subject": "cant login help",
            "body": "cant login help forgot password and email not coming thru",
            "from": "lost.user@gmail.com",
        },
        "reply": {
            "body": "Hi,\n\nI've sent a new password reset link to your registered email (check spam/junk). The link expires in 24 hours. If you still don't receive it, reply with your account email and we'll verify manually.\n\nBest,\nAccount Support",
            "tone": "professional",
        },
        "metadata": {
            "quality": "messy",
            "intent": ["password_reset"],
            "actions": ["send_password_reset", "check_spam", "offer_manual_verification"],
        },
    },
    {
        "id": "seed_012",
        "category": "scheduling",
        "urgency": "medium",
        "tone": "professional",
        "incoming_email": {
            "subject": "Need to reschedule our demo",
            "body": "Hi, I need to move our product demo from Thursday 2pm to Friday 10am EST. Same attendees. Is that possible?",
            "from": "prospect@bigco.com",
        },
        "reply": {
            "body": "Hi,\n\nAbsolutely — I've moved your demo to Friday at 10:00 AM EST. Updated calendar invite sent to all attendees. Looking forward to showing you the platform!\n\nBest,\nSales Team",
            "tone": "professional",
        },
        "metadata": {
            "quality": "clean",
            "intent": ["meeting_reschedule"],
            "actions": ["confirm_new_time", "send_updated_invite"],
        },
    },
    {
        "id": "seed_013",
        "category": "scheduling",
        "urgency": "low",
        "tone": "professional",
        "incoming_email": {
            "subject": "Cancel onboarding call",
            "body": "Please cancel our onboarding call scheduled for next Tuesday. We'll reach out when ready to proceed.",
            "from": "new.client@firm.com",
        },
        "reply": {
            "body": "Hi,\n\nYour onboarding call for next Tuesday has been cancelled. When you're ready to proceed, reply to this email or book a new slot at cal.example.com/onboarding. No charges apply.\n\nBest,\nCustomer Success",
            "tone": "professional",
        },
        "metadata": {
            "quality": "clean",
            "intent": ["cancel_meeting"],
            "actions": ["confirm_cancellation", "provide_rebooking_link"],
        },
    },
    {
        "id": "seed_014",
        "category": "sales",
        "urgency": "medium",
        "tone": "informative",
        "incoming_email": {
            "subject": "Enterprise pricing for 50 seats",
            "body": "We're evaluating your platform for our 50-person team. Can you share enterprise pricing and whether SSO is included?",
            "from": "it.director@enterprise.com",
        },
        "reply": {
            "body": "Hi,\n\nThank you for your interest. Enterprise pricing for 50 seats starts at $45/user/month (annual billing) and includes SSO, dedicated support, and 99.9% SLA. I've attached our enterprise datasheet. Would you like to schedule a call with our sales engineer this week?\n\nBest,\nEnterprise Sales",
            "tone": "professional",
        },
        "metadata": {
            "quality": "clean",
            "intent": ["pricing_inquiry", "enterprise_evaluation"],
            "actions": ["provide_pricing", "confirm_sso_included", "offer_sales_call"],
        },
    },
    {
        "id": "seed_015",
        "category": "sales",
        "urgency": "low",
        "tone": "informative",
        "incoming_email": {
            "subject": "how much for team plan???",
            "body": "how much for team plan??? need 10 users",
            "from": "startup.founder@gmail.com",
        },
        "reply": {
            "body": "Hi,\n\nOur Team plan for 10 users is $25/user/month (or $250/month total) on annual billing. It includes shared workspaces, admin controls, and priority email support. Happy to set up a 14-day trial — just reply to confirm.\n\nBest,\nSales Team",
            "tone": "professional",
        },
        "metadata": {
            "quality": "messy",
            "intent": ["pricing_inquiry"],
            "actions": ["provide_pricing", "offer_trial"],
        },
    },
    {
        "id": "seed_016",
        "category": "feature_request",
        "urgency": "low",
        "tone": "appreciative",
        "incoming_email": {
            "subject": "Dark mode for mobile app",
            "body": "Love the product! Any plans to add dark mode to the iOS app? It's hard on the eyes at night.",
            "from": "fan@mobile.dev",
        },
        "reply": {
            "body": "Hi,\n\nThank you for the feedback! Dark mode for iOS is on our Q3 roadmap and targeted for release in August. I've added your vote to the feature request. We'll notify you when it's available.\n\nBest,\nProduct Team",
            "tone": "friendly",
        },
        "metadata": {
            "quality": "clean",
            "intent": ["feature_request"],
            "actions": ["acknowledge_request", "share_roadmap_timeline", "add_to_feature_votes"],
        },
    },
    {
        "id": "seed_017",
        "category": "feature_request",
        "urgency": "low",
        "tone": "appreciative",
        "incoming_email": {
            "subject": "want dark mode pls",
            "body": "want dark mode pls eyes hurt at night on iphone app",
            "from": "user99@gmail.com",
        },
        "reply": {
            "body": "Hi,\n\nGreat suggestion! Dark mode for the iOS app is planned for Q3 (August). I've logged your request. We'll email you when it launches.\n\nBest,\nProduct Team",
            "tone": "friendly",
        },
        "metadata": {
            "quality": "messy",
            "intent": ["feature_request"],
            "actions": ["acknowledge_request", "share_roadmap_timeline"],
        },
    },
    {
        "id": "seed_018",
        "category": "onboarding",
        "urgency": "medium",
        "tone": "welcoming",
        "incoming_email": {
            "subject": "Getting started — where's my welcome email?",
            "body": "I signed up yesterday but never received the welcome email with setup instructions. Can you resend it?",
            "from": "newuser@company.org",
        },
        "reply": {
            "body": "Hi,\n\nWelcome aboard! I've resent the welcome email to newuser@company.org — please check your spam folder. It includes your setup guide and a link to schedule a free onboarding call. Let us know if you need anything else!\n\nBest,\nOnboarding Team",
            "tone": "friendly",
        },
        "metadata": {
            "quality": "clean",
            "intent": ["welcome_email_missing"],
            "actions": ["resend_welcome_email", "check_spam", "offer_onboarding_call"],
        },
    },
    {
        "id": "seed_019",
        "category": "onboarding",
        "urgency": "medium",
        "tone": "welcoming",
        "incoming_email": {
            "subject": "no welcome email got",
            "body": "no welcome email got signed up yesterday where is it",
            "from": "confused@gmail.com",
        },
        "reply": {
            "body": "Hi,\n\nSorry you didn't receive your welcome email! I've just resent it — check spam/junk too. It has setup steps and a link to book a free onboarding call. Reply if you still don't see it.\n\nBest,\nOnboarding Team",
            "tone": "friendly",
        },
        "metadata": {
            "quality": "messy",
            "intent": ["welcome_email_missing"],
            "actions": ["resend_welcome_email", "check_spam"],
        },
    },
    {
        "id": "seed_020",
        "category": "billing",
        "urgency": "medium",
        "tone": "informative",
        "incoming_email": {
            "subject": "Cancel subscription effective end of month",
            "body": "Please cancel my Pro subscription. I'd like it to remain active until March 31, then not renew.",
            "from": "subscriber@email.com",
        },
        "reply": {
            "body": "Hi,\n\nYour Pro subscription is set to cancel on March 31. You'll retain full access until then. No further charges will occur. If you change your mind, you can reactivate anytime from Account > Subscription before that date.\n\nBest,\nBilling Team",
            "tone": "professional",
        },
        "metadata": {
            "quality": "clean",
            "intent": ["cancel_subscription"],
            "actions": ["confirm_cancel_date", "retain_access_until_date", "explain_reactivation"],
        },
    },
    {
        "id": "seed_021",
        "category": "support",
        "urgency": "low",
        "tone": "helpful",
        "incoming_email": {
            "subject": "Integration with Slack not syncing",
            "body": "Our Slack integration stopped posting notifications 3 days ago. We reconnected but messages still don't appear.",
            "from": "admin@team.io",
        },
        "reply": {
            "body": "Hi,\n\nI checked your Slack integration and found the webhook token expired. I've re-authorized it on our end — please disconnect and reconnect in Settings > Integrations > Slack. Notifications should resume within 15 minutes. Let me know if issues persist.\n\nBest,\nTechnical Support",
            "tone": "professional",
        },
        "metadata": {
            "quality": "clean",
            "intent": ["integration_issue"],
            "actions": ["diagnose_token_expiry", "reauthorize_integration", "recommend_reconnect"],
        },
    },
    {
        "id": "seed_022",
        "category": "complaints",
        "urgency": "high",
        "tone": "empathetic",
        "incoming_email": {
            "subject": "Terrible customer service experience",
            "body": "I've been bounced between three agents over four days with no resolution on my billing dispute. I want to speak with a manager.",
            "from": "fedup@customer.com",
        },
        "reply": {
            "body": "Hi,\n\nI'm sorry you've had such a frustrating experience — that's not the standard we aim for. I've assigned a senior account manager (CC'd) to resolve your billing dispute within 24 hours. They'll call you directly at the number on file. Thank you for your patience.\n\nSincerely,\nCustomer Relations",
            "tone": "empathetic",
        },
        "metadata": {
            "quality": "clean",
            "intent": ["escalation_request", "complaint"],
            "actions": ["assign_senior_manager", "resolve_within_24h", "schedule_direct_call"],
        },
    },
    {
        "id": "seed_023",
        "category": "account_access",
        "urgency": "high",
        "tone": "helpful",
        "incoming_email": {
            "subject": "Need to change account email address",
            "body": "I'm leaving my company and need to transfer my account from work@oldco.com to personal@gmail.com. How do I do this?",
            "from": "work@oldco.com",
        },
        "reply": {
            "body": "Hi,\n\nTo change your account email: go to Settings > Account > Email, enter your new address, and verify via the confirmation link sent to personal@gmail.com. Your data and subscription transfer automatically. If you lose access to the old email, reply with ID verification and we'll assist manually.\n\nBest,\nAccount Support",
            "tone": "professional",
        },
        "metadata": {
            "quality": "clean",
            "intent": ["email_change"],
            "actions": ["provide_email_change_steps", "explain_verification", "offer_manual_assistance"],
        },
    },
    {
        "id": "seed_024",
        "category": "scheduling",
        "urgency": "high",
        "tone": "professional",
        "incoming_email": {
            "subject": "urgent need to move meeting today",
            "body": "emergency came up cant do 3pm call today need tomorrow same time pls",
            "from": "busy.exec@corp.com",
        },
        "reply": {
            "body": "Hi,\n\nNo problem — I've moved today's 3 PM call to tomorrow at 3 PM. Updated invite sent. Let us know if you need a different time.\n\nBest,\nSales Team",
            "tone": "professional",
        },
        "metadata": {
            "quality": "messy",
            "intent": ["meeting_reschedule"],
            "actions": ["confirm_new_time", "send_updated_invite"],
        },
    },
    {
        "id": "seed_025",
        "category": "sales",
        "urgency": "medium",
        "tone": "informative",
        "incoming_email": {
            "subject": "Nonprofit discount available?",
            "body": "We're a registered 501(c)(3) nonprofit with 15 staff. Do you offer discounted pricing?",
            "from": "director@nonprofit.org",
        },
        "reply": {
            "body": "Hi,\n\nYes! We offer 40% off for verified nonprofits — your Team plan would be $15/user/month for 15 seats. Please reply with your 501(c)(3) determination letter and we'll activate the discount within one business day.\n\nBest,\nSales Team",
            "tone": "professional",
        },
        "metadata": {
            "quality": "clean",
            "intent": ["nonprofit_pricing"],
            "actions": ["confirm_nonprofit_discount", "request_verification", "activate_within_1_day"],
        },
    },
]

SANITY_PAIRS = [
    {
        "id": "sanity_001",
        "incoming_email": {
            "subject": "Double charge on invoice",
            "body": "I was billed twice for order #98765. Please refund the duplicate charge.",
            "from": "billing.issue@email.com",
        },
        "mismatched_reply": {
            "body": "To reset your password, click the link below and follow the instructions. The link expires in 24 hours.",
            "tone": "professional",
        },
        "source_categories": {"email": "billing", "reply": "account_access"},
        "why_mismatched": "Reply addresses password reset, not billing dispute.",
    },
    {
        "id": "sanity_002",
        "incoming_email": {
            "subject": "Need to reschedule demo to Friday",
            "body": "Can we move our product demo from Thursday to Friday at 10am?",
            "from": "prospect@company.com",
        },
        "mismatched_reply": {
            "body": "I've confirmed your refund for order #12345. The credit will appear within 5-7 business days.",
            "tone": "professional",
        },
        "source_categories": {"email": "scheduling", "reply": "billing"},
        "why_mismatched": "Reply confirms a refund instead of rescheduling a meeting.",
    },
    {
        "id": "sanity_003",
        "incoming_email": {
            "subject": "Enterprise pricing for 50 seats",
            "body": "What is your enterprise pricing and does it include SSO?",
            "from": "buyer@enterprise.com",
        },
        "mismatched_reply": {
            "body": "I'm sorry your package is delayed. I've sent a replacement shipment expected in 3-5 business days.",
            "tone": "empathetic",
        },
        "source_categories": {"email": "sales", "reply": "complaints"},
        "why_mismatched": "Reply apologizes for shipping delay instead of answering pricing.",
    },
    {
        "id": "sanity_004",
        "incoming_email": {
            "subject": "Export crashes on CSV",
            "body": "The app crashes every time I export to CSV on macOS.",
            "from": "dev@startup.io",
        },
        "mismatched_reply": {
            "body": "Your Pro subscription is set to cancel on March 31. You'll retain access until then.",
            "tone": "professional",
        },
        "source_categories": {"email": "support", "reply": "billing"},
        "why_mismatched": "Reply discusses subscription cancellation, not a technical bug.",
    },
    {
        "id": "sanity_005",
        "incoming_email": {
            "subject": "Package 2 weeks late",
            "body": "My order still hasn't arrived after two weeks. This is unacceptable.",
            "from": "angry@mail.com",
        },
        "mismatched_reply": {
            "body": "Our Team plan for 10 users is $25/user/month on annual billing. Would you like a trial?",
            "tone": "professional",
        },
        "source_categories": {"email": "complaints", "reply": "sales"},
        "why_mismatched": "Reply provides sales pricing instead of addressing shipping.",
    },
    {
        "id": "sanity_006",
        "incoming_email": {
            "subject": "Locked out of account",
            "body": "Too many login attempts locked me out. I need access today.",
            "from": "user@work.com",
        },
        "mismatched_reply": {
            "body": "Dark mode for iOS is on our Q3 roadmap targeted for August release.",
            "tone": "friendly",
        },
        "source_categories": {"email": "account_access", "reply": "feature_request"},
        "why_mismatched": "Reply discusses feature roadmap instead of account unlock.",
    },
    {
        "id": "sanity_007",
        "incoming_email": {
            "subject": "Dark mode for mobile",
            "body": "Any plans to add dark mode to the iOS app?",
            "from": "fan@app.dev",
        },
        "mismatched_reply": {
            "body": "I've unlocked your account. Please reset your password using the link sent to your email.",
            "tone": "professional",
        },
        "source_categories": {"email": "feature_request", "reply": "account_access"},
        "why_mismatched": "Reply unlocks account instead of addressing feature request.",
    },
    {
        "id": "sanity_008",
        "incoming_email": {
            "subject": "Cancel onboarding call",
            "body": "Please cancel our onboarding call next Tuesday.",
            "from": "client@firm.com",
        },
        "mismatched_reply": {
            "body": "Please update to version 3.2.2 which fixes the CSV export crash on macOS 14.",
            "tone": "professional",
        },
        "source_categories": {"email": "scheduling", "reply": "support"},
        "why_mismatched": "Reply recommends software update instead of cancelling meeting.",
    },
    {
        "id": "sanity_009",
        "incoming_email": {
            "subject": "Slack integration not syncing",
            "body": "Slack notifications stopped working three days ago.",
            "from": "admin@team.io",
        },
        "mismatched_reply": {
            "body": "We offer 40% off for verified nonprofits. Please send your 501(c)(3) letter.",
            "tone": "professional",
        },
        "source_categories": {"email": "support", "reply": "sales"},
        "why_mismatched": "Reply discusses nonprofit discount instead of integration fix.",
    },
    {
        "id": "sanity_010",
        "incoming_email": {
            "subject": "Welcome email missing",
            "body": "I signed up but never got the welcome email with setup instructions.",
            "from": "new@org.com",
        },
        "mismatched_reply": {
            "body": "I've assigned a senior manager to resolve your billing dispute within 24 hours.",
            "tone": "empathetic",
        },
        "source_categories": {"email": "onboarding", "reply": "complaints"},
        "why_mismatched": "Reply escalates billing dispute instead of resending welcome email.",
    },
]

NEGATIVE_TEMPLATES = [
    {
        "suffix": "a",
        "failure_mode": "ignores_intent",
        "why_bad": "Generic acknowledgment with no answer to the customer's question.",
        "body": "Thanks for reaching out! We appreciate your message and will get back to you soon.",
    },
    {
        "suffix": "b",
        "failure_mode": "missing_actions",
        "why_bad": "Acknowledges the issue but omits required next steps and timelines.",
        "body": "Hi,\n\nSorry to hear about this. We'll look into it and take care of it for you.\n\nBest,\nSupport",
    },
    {
        "suffix": "c",
        "failure_mode": "wrong_tone",
        "why_bad": "Dismissive or overly casual tone inappropriate for the situation.",
        "body": "Hey,\n\nNot a big deal — these things happen. Just wait a bit and it should sort itself out.\n\nCheers",
    },
    {
        "suffix": "d",
        "failure_mode": "hallucinated_policy",
        "why_bad": "Invents refund terms, features, or policies not supported by the gold reply.",
        "body": "Hi,\n\nPer our lifetime refund guarantee, we'll process a full refund within 24 hours and add a free year of premium service.\n\nBest,\nSupport",
    },
    {
        "suffix": "e",
        "failure_mode": "off_topic",
        "why_bad": "Answers a completely different question than the one asked.",
        "body": "Hi,\n\nTo update your billing address, go to Settings > Billing > Address. Let me know if you need help with that.\n\nBest,\nSupport",
    },
]


def write_jsonl(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def main() -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    write_jsonl(DATA / "seed_emails.jsonl", SEED_PAIRS)
    write_jsonl(DATA / "sanity_check_pairs.jsonl", SANITY_PAIRS)

    # Negative examples keyed to holdout IDs (assigned during build_dataset split)
    # Pre-create templates that build_dataset will copy/adapt; also seed a static set
    negatives: list[dict] = []
    holdout_candidates = [p for i, p in enumerate(SEED_PAIRS) if i % 5 == 0][:5]
    for pair in holdout_candidates:
        for tmpl in NEGATIVE_TEMPLATES[:2]:
            negatives.append(
                {
                    "id": f"neg_{pair['id'].replace('seed_', '')}{tmpl['suffix']}",
                    "paired_email_id": pair["id"],
                    "bad_reply": {"body": tmpl["body"], "tone": "unprofessional"},
                    "failure_mode": tmpl["failure_mode"],
                    "why_bad": tmpl["why_bad"],
                }
            )
    write_jsonl(DATA / "negative_examples.jsonl", negatives)

    messy = sum(1 for p in SEED_PAIRS if p["metadata"]["quality"] == "messy")
    print(f"Wrote {len(SEED_PAIRS)} seed pairs ({messy} messy, {messy/len(SEED_PAIRS)*100:.0f}%)")
    print(f"Wrote {len(SANITY_PAIRS)} sanity pairs")
    print(f"Wrote {len(negatives)} negative examples (seed templates)")


if __name__ == "__main__":
    main()
