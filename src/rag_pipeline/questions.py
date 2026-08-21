"""Suggested HelixForge questions for the Ask UI and for learning retrieval."""

from __future__ import annotations

SUGGESTED_QUESTIONS: dict[str, list[str]] = {
    "Simple lookup": [
        "How much PTO do new full-time employees accrue in their first two years?",
        "Who is the CEO of HelixForge?",
        "Who is the CTO of HelixForge?",
        "Who is the CISO of HelixForge?",
        "Where is HelixForge headquartered?",
        "When does the HelixForge fiscal year start?",
        "What are core collaboration hours?",
        "What is the SEV-1 acknowledgment SLA in minutes?",
        "How long does standing production SSH access last?",
    ],
    "PTO and leave": [
        "How much PTO do employees accrue after five complete years?",
        "What is the PTO rollover cap?",
        "How much notice is required for 5 or more consecutive PTO days?",
        "Do contractors accrue HelixForge PTO?",
        "How many weeks of paid parental leave does a primary caregiver get?",
        "Do employees keep accruing PTO while on parental leave?",
        "Can a new hire take PTO during the first 30 days?",
    ],
    "On-call (multi-hop)": [
        "What happens to the on-call stipend during parental leave?",
        "Does taking PTO automatically remove on-call duties?",
        "What is the primary on-call stipend?",
        "When do new engineers join secondary on-call?",
        "When does an on-call week start and end?",
    ],
    "Travel and expenses": [
        "What is the dinner meal cap for customer meals?",
        "Can I book work travel on a personal credit card?",
        "When is business class allowed?",
        "What is the hotel cap in New York City?",
        "How many days in advance should customer-facing travel be booked?",
        "Is home-office internet reimbursable as an expense?",
    ],
    "Remote, security, AI": [
        "Which weekdays must Office-Primary employees work from the office?",
        "How much is the Remote-Primary monthly stipend?",
        "How long does a production access grant last?",
        "How quickly must a lost laptop be reported?",
        "May I paste customer data into a personal ChatGPT account?",
        "If the internal AI assistant disagrees with the handbook, which one wins?",
        "What YubiKey model is required for production SSH?",
    ],
    "Tables and matrices": [
        "What is the Austin USD mid salary for Software Engineering L5?",
        "What is the SEV-0 ack SLA in minutes?",
        "Who is the incident commander for a SEV-1?",
        "What is the Critical vulnerability remediation SLA in days?",
        "What are HelixForge's company holidays in 2026?",
    ],
    "Should abstain": [
        "What is the salary of the CEO?",
        "What is HelixForge's stock price?",
        "How many vacation days does Google give employees?",
        "What is HelixForge's current valuation?",
    ],
}
