"""Populate data/raw_docs/ with a small fictional company-policy corpus.

The documents are written as HelixForge internal policies: overlapping facts
across files so later RAG evaluation can include simple lookups and multi-hop
questions (e.g. PTO + on-call, travel + expenses).
"""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DOCS_DIR = PROJECT_ROOT / "data" / "raw_docs"

DOCUMENTS: dict[str, str] = {
    "company_overview.md": """# HelixForge Company Overview

HelixForge is a fictional AI infrastructure company founded in 2019 and
headquartered in Austin, Texas, with satellite offices in Dublin and Singapore.
The company builds managed vector databases, retrieval APIs, and evaluation
tooling for enterprise RAG systems.

As of the 2026 handbook revision, HelixForge has 420 full-time employees and
about 60 contractors. The CEO is Mara Chen. The CTO is Devon Hale. People
Operations is led by Priya Nair. Security is led by CISO Elena Voss.

HelixForge's fiscal year starts on February 1. Official working hours for
office-based staff are 09:30–17:30 local time, Monday through Friday. Core
collaboration hours for all time zones are 14:00–17:00 UTC.

Employees are organized into four divisions: Platform Engineering, Applied
Research, Customer Success, and Business Operations. Platform Engineering owns
the retrieval runtime. Applied Research owns ranking models and evaluation
benchmarks. Customer Success owns onboarding of paying customers. Business
Operations owns finance, legal, and people.

The internal knowledge base is the source of truth for policy. Slack messages
and hallway conversations are not policy. If a policy document and a manager's
verbal instruction conflict, the written policy wins unless Legal issues a
signed exception.

HelixForge's public support email is support@helixforge.example. Internal HR
questions go to people@helixforge.example. Security incidents go to
security@helixforge.example and must follow the Incident Response policy, not
email alone.
""",
    "pto_policy.md": """# Paid Time Off Policy

HelixForge uses an accrual PTO model, not unlimited PTO. Full-time employees
accrue 18 days of PTO per fiscal year during their first two years of
employment, 23 days during years three through five, and 28 days after five
complete years. Accrual is monthly: annual days divided by 12, credited on the
first working day of each month.

PTO does not include HelixForge's ten company holidays, parental leave, or
bereavement leave. Sick leave is a separate bank of 10 days per year and does
not roll over.

PTO requests of 1–4 consecutive days require manager approval in Workday at
least 5 business days in advance. Requests of 5 or more consecutive days
require 15 business days of notice. Managers must respond within 3 business
days. If a manager is on leave, the skip-level manager approves.

Unused PTO rolls over up to a cap of 8 days. Anything above the cap is
forfeited on January 31, the last day of the fiscal year. HelixForge does not
pay out unused PTO except in California, where state law requires payout at
termination, and in Ireland for statutory annual leave.

Contractors do not accrue HelixForge PTO. They follow their contracting firm's
leave rules.

Blackout periods: Platform Engineering has a blackout during the two weeks
before a major product launch, published on the engineering calendar. PTO
during a blackout needs VP approval.

On-call engineers who take PTO remain responsible for swapping their on-call
shift before the leave starts. PTO does not automatically remove on-call
duties. See the Engineering On-Call policy.
""",
    "parental_leave.md": """# Parental Leave Policy

HelixForge provides 16 weeks of fully paid parental leave for the primary
caregiver and 8 weeks for the secondary caregiver. Primary vs secondary is
self-declared in Workday; employees may not both claim primary for the same
child.

Leave may be taken continuously or in two blocks, but must be completed within
12 months of the child's birth, adoption, or foster placement. A minimum block
is 2 weeks.

Parental leave does not reduce the PTO accrual rate. Employees continue to
accrue PTO while on parental leave. Health benefits continue; HelixForge pays
the employer portion as usual.

Employees on parental leave are removed from on-call rotations automatically
starting the first day of leave. They are not required to find a swap. On-call
stipends pause during parental leave and resume the first full week after
return.

To request leave, submit a Parental Leave case in Workday at least 30 days
before the expected start, or as soon as practicable for adoption. People
Operations will schedule a benefits walkthrough within 10 business days.

Short-term disability (US) may run concurrently with parental leave for birth
parents. HelixForge tops up disability payments so the employee receives 100%
base salary during the combined period, up to 16 weeks total paid time.

This policy applies to full-time employees who have been employed at least 6
months. Employees under 6 months may take unpaid leave and use accrued PTO.
Contractors are not eligible.
""",
    "expense_policy.md": """# Expense Reimbursement Policy

HelixForge reimburses reasonable business expenses submitted in Expensify
within 30 days of the charge. Reports submitted after 60 days require VP
Finance approval and may be denied.

Meals: employees may expense meals with customers or candidates. Per-person
caps are $40 lunch and $90 dinner excluding tax and tip. Alcohol is allowed
only at dinners with external guests, capped at $30 per person. Internal team
lunches require a director's pre-approval and are capped at $25 per person.

Home-office internet is not reimbursable; it is covered by the $150 monthly
remote stipend in the Remote Work policy. Office snacks purchased for a
personal desk are not reimbursable.

Software and cloud accounts: engineering tools under $50/month may be expensed
with manager approval. Anything $50/month or more, or any annual contract,
must go through Procurement. Do not put production cloud spend on a personal
card.

Receipts are required above $25. Missing receipts under $75 can be replaced
with a missing-receipt affidavit once per quarter. Above $75, no affidavit is
accepted.

Travel expenses follow the Travel Policy, not this document. If both could
apply, Travel Policy wins for flights, hotels, and ground transport; this
policy wins for meals during travel.

Reimbursement is paid on the next weekly AP run after manager approval.
Typical arrival is 5–8 business days after submission.
""",
    "travel_policy.md": """# Travel Policy

HelixForge books work travel through Navan. Personal-card bookings are not
reimbursed unless Navan could not complete the booking and Finance pre-approved
an exception in writing.

Flights under 6 hours: economy only. Flights of 6 hours or more: premium
economy is allowed. Business class requires VP approval and is limited to
flights over 8 hours when the employee must work the next calendar day.

Hotels: cap is $220/night in US tier-1 cities (NYC, SF, Seattle, Boston),
$180/night in other US cities, and €180/night in EU cities. Singapore cap is
SGD 280/night. Airbnb is allowed if cheaper than the hotel cap and the stay is
3 nights or longer.

Ground transport: rideshare to/from airports is reimbursable. Rental cars
need manager approval. Parking at the employee's usual office is not a travel
expense.

Travel days do not count as PTO. If an employee adds personal days to a trip,
the personal hotel nights and extra flight change fees are not reimbursable.
The business flight must still be the logical business routing; HelixForge
does not pay for a personal-destination upgrade.

Customer-facing travel should be booked at least 14 days in advance. Internal
offsite travel should be booked at least 21 days in advance. Late booking fees
are the team's budget problem, not a reason to skip Navan.

Meals while traveling follow the Expense Policy caps. The company does not
issue a daily per diem except for multi-week customer onsite work in
Singapore, where a SGD 90/day per diem replaces itemized meals.
""",
    "remote_work.md": """# Remote Work Policy

HelixForge is hybrid-remote. Employees within 50 miles of Austin, Dublin, or
Singapore are Office-Primary: they work from the office Tuesday through
Thursday. Monday and Friday are remote-optional.

Employees outside those radiuses are Remote-Primary. Remote-Primary staff
receive a $150 monthly stipend for internet and workspace costs, paid with
payroll. The stipend is taxable in the US. It is not a reimbursement and does
not require receipts.

Office-Primary employees do not receive the stipend. They may still work
remotely on Monday and Friday without extra approval. Remote work on a core
office day (Tue–Thu) needs manager approval in Slack, posted before 09:00
local.

Core collaboration hours are 14:00–17:00 UTC for all employees, including
Remote-Primary. Meetings that require more than two time zones should be
scheduled inside that window.

International remote work (working from a country that is not the employment
country) is limited to 30 calendar days per fiscal year and requires a
mobility ticket in Workday. Working from a country on the restricted list
(currently Russia, Iran, North Korea, and Belarus) is prohibited for security
reasons.

Equipment is provided per the Equipment Policy. HelixForge does not pay
coworking memberships except when an office-primary employee is traveling for
more than 10 consecutive business days and has no HelixForge office nearby.
""",
    "information_security.md": """# Information Security Policy

HelixForge classifies systems as production, staging, and corporate. Production
access requires a hardware security key (YubiKey) and a just-in-time access
grant that expires in 8 hours. Standing production SSH is forbidden.

Passwords, where still used, must be at least 16 characters and stored only in
1Password. SMS 2FA is not accepted for production or email. GitHub, Google
Workspace, and AWS SSO require hardware keys.

Laptops must run the company MDM profile, full-disk encryption, and automatic
screen lock at 5 minutes. Jailbroken or unmanaged devices may not access
email, Slack, or code.

Customer data may not be copied to personal machines, USB drives, or personal
cloud accounts. Using a personal ChatGPT, Claude, or Gemini account with
customer data is a security incident. Internal AI tools are covered by the AI
Usage Policy.

Phishing: report suspected phishing to security@helixforge.example and via the
#sec-reports Slack channel. Do not forward the raw message to teammates.

Vendors that process customer data need a signed DPA and a Security review.
Employees may not sign vendor security questionnaires; Security does.

Lost devices must be reported to Security within 1 hour of noticing the loss.
Security will remotely lock the device. Delay beyond 1 hour is a policy
violation even if the device is later found.

This policy is owned by CISO Elena Voss. Exceptions require a written ticket
and expire after 90 days unless renewed.
""",
    "data_classification.md": """# Data Classification Policy

HelixForge has four data classes: Public, Internal, Confidential, and
Restricted.

Public: marketing website copy, published papers, job listings. May live
anywhere.

Internal: org charts, non-sensitive handbook pages, sprint boards without
customer names. May live in Google Drive, Notion, and Slack. Do not post
Internal data on public GitHub.

Confidential: unreleased product plans, salaries, customer names in CRM,
architecture docs. Must live in Google Drive with link-sharing set to
restricted, or in Notion with a named-person ACL. Confidential data in Slack
is allowed only in private channels. Confidential data is not allowed in
personal AI accounts.

Restricted: production customer content, authentication secrets, government
ID documents, health information collected for benefits. Restricted data may
only live in approved systems: the production datastore, Workday, Greenhouse
(candidates), and the secrets manager. Restricted data must not be pasted into
tickets, Slack, or eval datasets without tokenization.

RAG evaluation sets built from customer data require tokenization of names,
emails, and account IDs before they leave production. Synthetic HelixForge
handbook data (this corpus) is Internal, not Restricted.

When in doubt, classify one level higher and ask Security. Mis-classifying
Restricted data as Confidential is an incident.
""",
    "incident_response.md": """# Incident Response Policy

An incident is any event that actually or potentially exposes Restricted data,
takes down production for more than 15 minutes, or involves a lost device with
corporate access.

Severity:
- SEV-1: production down for all customers, or confirmed Restricted data
  exposure. Page the on-call security engineer and the platform on-call
  immediately. CEO is notified within 30 minutes.
- SEV-2: partial production impact or suspected exposure. Page platform
  on-call. CISO notified within 1 hour.
- SEV-3: contained issue, no customer impact. Ticket only, handled next
  business day.

The incident commander for SEV-1/2 is the platform on-call unless Security
takes command for a confirmed data exposure. The commander runs a Zoom bridge
and writes to the #incidents Slack channel. Status updates every 30 minutes
until mitigation.

Customer notification: Customer Success drafts external messaging. Legal must
approve any message about data exposure before it is sent. Do not tweet, post
on LinkedIn, or email customers from a personal account.

After mitigation, a blameless postmortem is due in 5 business days for SEV-1
and 10 business days for SEV-2. Postmortems live in the incidents Drive folder
and are Confidential.

Employees who discover an incident and stay quiet are in violation even if
they later fix it themselves. Report first, then fix.
""",
    "code_of_conduct.md": """# Code of Conduct

HelixForge expects employees, contractors, and visitors to treat each other
with respect. Harassment, discrimination, and retaliation are prohibited.
This includes jokes about protected characteristics, repeated unwanted
messages, and using performance feedback as cover for personal hostility.

Report conduct issues to people@helixforge.example, to Priya Nair, or
anonymously via the EthicsPoint form linked in Workday. Managers who receive a
report must forward it to People Operations within 24 hours and must not
investigate privately.

Romantic relationships between a manager and someone in their reporting line
are prohibited. Relationships between peers must be disclosed to People
Operations if both work on the same product surface.

Alcohol at company events is optional. No one may pressure others to drink.
Company cards may not buy alcohol for events without People Operations
pre-approval, except customer dinners under the Expense Policy.

The code applies on Slack, GitHub, offsites, and customer sites. "It was a
joke" is not a defense.

Violations can result in coaching, a written warning, or termination.
HelixForge does not publish a mandatory-escalation ladder; People Operations
decides based on severity and history.
""",
    "onboarding.md": """# Onboarding Guide

New full-time employees start on Mondays. Day 1 is in the Austin, Dublin, or
Singapore office when the hire is Office-Primary, and on Zoom when
Remote-Primary. People Operations ships a laptop to arrive by the Friday
before start. If the laptop is late, Day 1 is still not delayed; the hire uses
a loaner Chromebook with limited access until MDM enrollment.

Week 1 checklist:
1. 1Password, Google Workspace, Slack, GitHub.
2. Security training (45 minutes) and phishing simulation enrollment.
3. Engineering hires: staging access only. Production access is not granted
   during week 1.
4. Buddy assignment. Buddies are paid a $250 one-time bonus after the 30-day
   check-in is completed in Workday.

Managers must hold a 30-60-90 plan meeting on Day 2. The plan is stored in
the employee's Drive folder. Without a 30-60-90 plan, People Operations will
nudge the manager on Day 5.

Production access for engineers requires: completed security training, a
YubiKey issued and registered, and a manager ticket. Typical grant is Day 10,
not Day 1.

Contractors skip the buddy bonus and 30-60-90 process. They still complete
security training before any repo access.

New hires accrue PTO from Day 1 but should not take PTO during the first 30
days except for pre-approved, already-booked trips disclosed at offer.
""",
    "benefits.md": """# Benefits Summary

US full-time employees receive medical, dental, and vision through Aetna.
HelixForge pays 90% of employee premiums and 70% of dependent premiums.
Enrollment is in Workday within 30 days of start or a qualifying life event.

401(k): HelixForge matches 100% of the first 4% of eligible compensation.
Matching is contributed each payroll. Vesting is immediate.

Ireland employees receive private health insurance through VHI, a 5% pension
contribution, and statutory leave. Singapore employees receive CPIB medical
and the legal CPF contributions plus a 4% company top-up to the employee's
CPF Ordinary Account.

All full-time employees get a $1,000 annual learning stipend. Courses need
manager approval. Unused stipend does not roll over. Conference travel uses
the Travel Policy and does not come out of the learning stipend unless the
employee prefers that for a small virtual ticket.

The employee assistance program (EAP) is available 24/7 at the number in
Workday. EAP use is confidential from managers.

Contractors are not on HelixForge medical plans. They may not be added as
dependents of a full-time employee unless they are a legal spouse or partner.
""",
    "engineering_oncall.md": """# Engineering On-Call Policy

Platform Engineering runs a weekly on-call rotation. The primary on-call is
the incident first responder for SEV-1 and SEV-2 production issues. A
secondary on-call is shadowing and takes over if the primary does not
acknowledge a page within 10 minutes.

On-call weeks run Thursday 12:00 UTC to the next Thursday 12:00 UTC. The
stipend is $400 for primary and $150 for secondary, paid monthly in arrears.
Parental leave pauses the stipend as described in the Parental Leave policy.

Primary on-call must remain within 30 minutes of a laptop with production
access and must not be on a flight without secondary coverage arranged.
Alcohol during an on-call shift is prohibited.

Shift swaps must be recorded in PagerDuty before the shift starts. PTO does
not auto-swap on-call. Taking PTO during your on-call week without a recorded
swap is a policy violation and may forfeit that week's stipend.

New engineers join secondary on-call after 90 days, not immediately after
production access. Managers may delay this if the engineer is still ramping.

After a SEV-1, the primary on-call is entitled to the following business day
as a recovery day that does not consume PTO, if the incident lasted more than
4 hours overnight. Recovery days are logged in Workday as "On-call recovery".
""",
    "ai_usage_policy.md": """# AI Usage Policy

HelixForge employees may use approved AI tools for coding, writing, and
internal research. Approved tools: GitHub Copilot on company GitHub, the
internal HelixForge RAG assistant, and the company-managed ChatGPT Enterprise
workspace.

Unapproved tools (personal ChatGPT, Claude.ai, Gemini, public Hugging Face
Spaces, consumer Copilot) may not receive Confidential or Restricted data.
Internal handbook text (Internal classification) may be pasted into unapproved
tools only after customer names and credentials are removed.

Customer data, production logs, and secrets are never allowed in any AI tool
except the internal RAG assistant running in the production VPC. The internal
assistant logs prompts for 14 days for abuse review; do not paste secrets
there either.

Model outputs are not a source of policy. If the assistant disagrees with this
handbook, the handbook wins. Employees remain responsible for code and emails
they send, including AI-drafted text.

Training: HelixForge does not use customer prompts to train third-party
foundation models. Evaluation datasets derived from customer data must be
tokenized per the Data Classification policy.

Violations of this policy are security incidents when Restricted data is
involved, and conduct issues otherwise.
""",
    "performance_reviews.txt": """HelixForge Performance Review Cycle

HelixForge runs two formal review cycles per fiscal year: a mid-year
checkpoint in August and a year-end review in January. Ratings from the
January cycle determine merit increases, which take effect on March 1.

Rating scale: 1 Does not meet, 2 Inconsistent, 3 Meets, 4 Exceeds, 5
Transformational. A 5 is rare; managers need VP calibration to assign a 5.
A 1 requires a performance improvement plan (PIP) of 30 or 60 days, designed
with People Operations.

Calibration happens at the division level. Managers submit draft ratings 2
weeks before calibration. Employees write a self-review in Workday; it is
visible to the manager but not to skip-levels unless the employee opts in.

Promotion packets are separate from ratings. An employee can be rated 4 and
still not be promoted if the next-level bar is not evidenced. Promotions are
effective March 1 or September 1 only.

Feedback outside the cycle is expected. The review cycle is not the only time
to discuss performance. Surprise 1 ratings are a manager failure; People
Operations will inspect whether prior written feedback existed.

Contractors do not receive HelixForge ratings. Their firms may run their own
reviews.
""",
    "equipment_policy.txt": """HelixForge Equipment Policy

Every full-time employee receives one company laptop (14-inch MacBook Pro or
ThinkPad T14, employee's choice during onboarding), one YubiKey 5C NFC, and
noise-cancelling headphones on request.

Monitors: Office-Primary employees use office-provided monitors and may not
expense a home monitor unless they are approved for an exception. Remote-
Primary employees may expense one monitor up to $350 or two monitors totaling
$500, once every 3 years.

Phones: HelixForge does not provide phones. A $30/month stipend is available
if the employee enables MDM on a personal phone. Without MDM, Slack and email
on a personal phone are still allowed via the official apps, but Drive file
downloads are blocked.

Broken equipment: open an IT ticket. Do not expense a replacement laptop on a
personal card. Lost equipment follows the Information Security lost-device
rule first, then IT issues a replacement.

On termination, laptops and YubiKeys must be returned within 10 business days
using the prepaid label IT sends. The remote stipend stops on the last day of
employment. Unreturned laptops after 21 days may be deducted from final pay
where legally allowed.
""",
}


def seed(target_dir: Path = RAW_DOCS_DIR, overwrite: bool = True) -> list[Path]:
    """Write the sample corpus to target_dir. Returns written file paths."""
    target_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for name, content in DOCUMENTS.items():
        path = target_dir / name
        if path.exists() and not overwrite:
            continue
        path.write_text(content.strip() + "\n", encoding="utf-8")
        written.append(path)
    return written


def main() -> None:
    written = seed()
    print(f"Wrote {len(written)} documents to {RAW_DOCS_DIR}")
    for path in written:
        print(f"  - {path.name}")


if __name__ == "__main__":
    sys.exit(main() or 0)
