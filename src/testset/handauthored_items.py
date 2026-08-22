"""Hand-authored (agent-curated) test set for the 86-doc HelixForge corpus.

Unlike ``generate.py`` (Ragas synthetic generation via an LLM judge), these 40
items were written by reading the actual corpus documents directly, so there
is zero LLM-generation cost/quota risk and every ground-truth answer is
grounded in a verified quote. Mix: 22 simple, 8 multi_hop, 5 reasoning,
5 abstain (incl. 3 that probe dangling cross-links to files that don't exist
in the corpus, e.g. ``vendor_security.md``).
"""

from __future__ import annotations

from typing import Any

ITEMS: list[dict[str, Any]] = [
    # ---------------------------------------------------------------- simple
    {
        "question": "What is the acknowledgement SLA in minutes for a SEV-1 (Critical Outage), and who can serve as incident commander?",
        "ground_truth_answer": "15 minutes ack SLA. Incident commander is the Cloud Infra Lead (Chloe Bennett) or a Staff SRE.",
        "reference_contexts": ["severity_definitions.csv: SEV-1,Critical Outage,...,15,30,Yes,Cloud Infra Lead (Chloe Bennett) or Staff SRE,..."],
        "question_type": "simple",
        "synthesizer_name": "handauthored",
    },
    {
        "question": "What is the PagerDuty service ID for the Platform-Inference on-call rotation during the 00:00-12:00 UTC shift?",
        "ground_truth_answer": "PD-SVC-INF-01 (primary contact group inference-oncall-apac-emea@helixforge.example).",
        "reference_contexts": ["oncall_escalation_matrix.csv: Platform-Inference,L1 On-Call,00:00-12:00,inference-oncall-apac-emea@helixforge.example,...,PD-SVC-INF-01"],
        "question_type": "simple",
        "synthesizer_name": "handauthored",
    },
    {
        "question": "What is the annual base salary midpoint for a Staff Software Engineer (L6) in Austin?",
        "ground_truth_answer": "$275,000 (Austin USD mid for Software Engineering L6, Staff Software Engineer).",
        "reference_contexts": ["compensation_bands.csv: Software Engineering,L6,Staff Software Engineer,240000,275000,315000,..."],
        "question_type": "simple",
        "synthesizer_name": "handauthored",
    },
    {
        "question": "For a Critical severity vulnerability (CVSS 9.0-10.0) with an active exploit, what is the SLA for remediation and who is the exception approver?",
        "ground_truth_answer": "7 days remediation SLA overall, 24 hours if there is an active exploit. The exception approver is Devon Hale (CTO).",
        "reference_contexts": ["vulnerability_patching_sla_matrix.csv: Critical,9.0,10.0,7,24,...,Elena Voss (CISO),Devon Hale (CTO)"],
        "question_type": "simple",
        "synthesizer_name": "handauthored",
    },
    {
        "question": "What is the cross-border data transfer rule for the European Union (EU-West) region?",
        "ground_truth_answer": "Strict GDPR adequacy or Standard Contractual Clauses (SCCs) are required for cross-border transfer.",
        "reference_contexts": ["data_residency_matrix.csv: European Union (EU-West),eu-west-1,...,Strict GDPR adequacy or SCCs required,GDPR / EU AI Act Tier 2"],
        "question_type": "simple",
        "synthesizer_name": "handauthored",
    },
    {
        "question": "What is the annual discretionary spending limit for the Foundation Model Pre-Training cost center, and who heads it?",
        "ground_truth_answer": "$350,000 annual discretionary limit for CC-2010 (Foundation Model Pre-Training), headed by Dr. Alina Rostova.",
        "reference_contexts": ["cost_centers.csv: CC-2010,Foundation Model Pre-Training,Applied Research,dr.alina.rostova@helixforge.example,...,350000,Austin"],
        "question_type": "simple",
        "synthesizer_name": "handauthored",
    },
    {
        "question": "How many tokens per minute (TPM) does the Enterprise Tier 1 API subscription allow, and what is the overage cost per 1k tokens?",
        "ground_truth_answer": "2,000,000 tokens per minute, with overage cost of $0.0015 per 1k tokens.",
        "reference_contexts": ["api_rate_limits_matrix.csv: Enterprise Tier 1,15000,10000,2000000,250,1.5x (5 min),.0015,..."],
        "question_type": "simple",
        "synthesizer_name": "handauthored",
    },
    {
        "question": "How many PTO days per year do full-time employees accrue during years three through five of employment?",
        "ground_truth_answer": "23 days of PTO per fiscal year during years three through five.",
        "reference_contexts": ["pto_policy.md: ...23 days during years three through five, and 28 days after five complete years."],
        "question_type": "simple",
        "synthesizer_name": "handauthored",
    },
    {
        "question": "How many weeks of paid parental leave does HelixForge provide to the secondary caregiver?",
        "ground_truth_answer": "8 weeks of fully paid parental leave for the secondary caregiver.",
        "reference_contexts": ["parental_leave.md: HelixForge provides 16 weeks of fully paid parental leave for the primary caregiver and 8 weeks for the secondary caregiver."],
        "question_type": "simple",
        "synthesizer_name": "handauthored",
    },
    {
        "question": "How many calendar days per fiscal year can an employee work internationally (outside their employment country) under the Remote Work policy?",
        "ground_truth_answer": "30 calendar days per fiscal year, and it requires a mobility ticket in Workday.",
        "reference_contexts": ["remote_work.md: International remote work ... is limited to 30 calendar days per fiscal year and requires a mobility ticket in Workday."],
        "question_type": "simple",
        "synthesizer_name": "handauthored",
    },
    {
        "question": "How long is the Post-Termination Exercise Period (PTEP) for vested stock options for an employee with at least 2 years of tenure?",
        "ground_truth_answer": "A 5-year exercise window (extended from the standard 90 days).",
        "reference_contexts": ["equity_refresh_and_options_policy.md: Employees with >= 2 years tenure receive an extended 5-year exercise window for vested options upon voluntary departure."],
        "question_type": "simple",
        "synthesizer_name": "handauthored",
    },
    {
        "question": "What one-time bonus does an onboarding buddy receive, and when is it paid?",
        "ground_truth_answer": "A $250 one-time bonus, paid after the new hire's 30-day check-in is completed in Workday.",
        "reference_contexts": ["onboarding.md: Buddies are paid a $250 one-time bonus after the 30-day check-in is completed in Workday."],
        "question_type": "simple",
        "synthesizer_name": "handauthored",
    },
    {
        "question": "Within how many hours must interviewers submit written scorecards in Ashby after an interview?",
        "ground_truth_answer": "24 hours.",
        "reference_contexts": ["interview_loop_and_hiring_standards.md: Interviewers must submit independent, written scorecards in Ashby within 24 hours of completing the interview session."],
        "question_type": "simple",
        "synthesizer_name": "handauthored",
    },
    {
        "question": "Within what time window must the CEO be notified of a SEV-1 incident involving confirmed Restricted data exposure?",
        "ground_truth_answer": "Within 30 minutes.",
        "reference_contexts": ["incident_response.md: SEV-1: ... CEO is notified within 30 minutes."],
        "question_type": "simple",
        "synthesizer_name": "handauthored",
    },
    {
        "question": "What are the four data classification levels defined in HelixForge's Data Classification Policy?",
        "ground_truth_answer": "Public, Internal, Confidential, and Restricted.",
        "reference_contexts": ["data_classification.md: HelixForge has four data classes: Public, Internal, Confidential, and Restricted."],
        "question_type": "simple",
        "synthesizer_name": "handauthored",
    },
    {
        "question": "What are the target RPO and RTO for Tier 0 systems (Core Inference Gateway, User Auth, API Routing)?",
        "ground_truth_answer": "RPO <= 1 minute and RTO <= 15 minutes.",
        "reference_contexts": ["disaster_recovery_rpo_rto.md: Tier 0 | Core Inference Gateway, User Auth (Okta/Vault tokens), API Routing | <= 1 minute | <= 15 minutes"],
        "question_type": "simple",
        "synthesizer_name": "handauthored",
    },
    {
        "question": "What is the maximum standing (uninterrupted) duration for a production SSH session before re-authentication is required?",
        "ground_truth_answer": "8 hours; the certificate has an exact 8-hour Time-To-Live and all active connections are severed automatically when it expires.",
        "reference_contexts": ["sop_production_ssh_yubikey.txt: Standing access duration is strictly capped at 8 hours. No permanent SSH keys or long-lived authorized_keys entries are permitted."],
        "question_type": "simple",
        "synthesizer_name": "handauthored",
    },
    {
        "question": "After how many minutes of inactivity is a VPN session disconnected, and how often must users re-authenticate a standard ZTNA session?",
        "ground_truth_answer": "Inactive VPN sessions disconnect after 60 minutes; standard ZTNA sessions expire every 24 hours requiring Okta SSO re-authentication.",
        "reference_contexts": ["vpn_and_network_security_policy.md: Standard ZTNA user sessions expire every 24 hours... Inactive VPN sessions are disconnected after 60 minutes of idle traffic."],
        "question_type": "simple",
        "synthesizer_name": "handauthored",
    },
    {
        "question": "Under the GDPR/PDPA Right to be Forgotten SOP, within how many hours must vector embeddings tied to a deleted customer be purged from the vector store?",
        "ground_truth_answer": "Within 48 hours.",
        "reference_contexts": ["sop_gdpr_right_to_be_forgotten.txt: Vector Embedding Purge: Embeddings associated with customer fine-tuning sets are scrubbed from Pinecone / Milvus vector stores within 48 hours."],
        "question_type": "simple",
        "synthesizer_name": "handauthored",
    },
    {
        "question": "How many free individual therapy sessions per calendar year does the Employee Assistance Program (EAP) cover?",
        "ground_truth_answer": "Up to 8 free sessions per calendar year with a licensed clinical therapist or psychologist.",
        "reference_contexts": ["wellness_and_mental_health_eap.md: Individual Therapy: Up to 8 free sessions with a licensed clinical therapist or psychologist per calendar year."],
        "question_type": "simple",
        "synthesizer_name": "handauthored",
    },
    {
        "question": "Within how many calendar days after departure must a departing employee return company-owned laptops and monitors?",
        "ground_truth_answer": "Within 14 calendar days.",
        "reference_contexts": ["sop_employee_departure_and_revocation.txt: Departing employee must return company-owned laptops and monitors within 14 calendar days."],
        "question_type": "simple",
        "synthesizer_name": "handauthored",
    },
    {
        "question": "Per the SOC 2 Type II compliance overview, within how many minutes must SEV-1 notifications be published, and within how many hours must post-mortems be delivered?",
        "ground_truth_answer": "SEV-1 notifications within 15 minutes; post-mortems within 72 hours.",
        "reference_contexts": ["soc2_compliance_executive_summary.pdf: Incident Management: SEV-1 notifications published within 15 minutes; post-mortems delivered within 72 hours."],
        "question_type": "simple",
        "synthesizer_name": "handauthored",
    },
    # ------------------------------------------------------------- multi_hop
    {
        "question": "If a Platform-Inference primary on-call engineer is paged for a SEV-1 between 22:00 and 06:00 local time, which PagerDuty service handles that page and what recovery benefit do they get the next morning?",
        "ground_truth_answer": "The page routes through the Platform-Inference rotation (PD-SVC-INF-01 or PD-SVC-INF-02 depending on shift). Per the wellness policy, being paged overnight for a SEV-1/SEV-2 grants 4 hours of mandatory rest decompression the following morning, with no impact on performance review.",
        "reference_contexts": [
            "oncall_escalation_matrix.csv: Platform-Inference,L1 On-Call,...,PD-SVC-INF-01/02",
            "wellness_and_mental_health_eap.md: If an on-call engineer is paged for a SEV-1/SEV-2 incident between 22:00 and 06:00 local time, they are granted 4 hours of mandatory rest decompression the following morning.",
        ],
        "question_type": "multi_hop",
        "synthesizer_name": "handauthored",
    },
    {
        "question": "Would an L5 Senior Software Engineer based in Singapore qualify to serve as a Bar Raiser in an interview loop, and what is that engineer's Singapore salary midpoint?",
        "ground_truth_answer": "No — the Bar Raiser must be an L6+ Staff Engineer or Lead, so an L5 does not qualify. The Singapore SGD mid for a Senior Software Engineer (L5) is 230,000.",
        "reference_contexts": [
            "interview_loop_and_hiring_standards.md: Every full-time loop includes an independent Bar Raiser—an L6+ Staff Engineer or Lead from an unrelated department.",
            "compensation_bands.csv: Software Engineering,L5,Senior Software Engineer,185000,210000,240000,155000,230000,85000",
        ],
        "question_type": "multi_hop",
        "synthesizer_name": "handauthored",
    },
    {
        "question": "Which cost center funds conference travel for Applied Research staff presenting papers, and what is that cost center's annual discretionary limit?",
        "ground_truth_answer": "CC-2010 (Foundation Model Pre-Training, Applied Research division) funds it, with an annual discretionary limit of $350,000.",
        "reference_contexts": [
            "learning_stipend_and_conferences.md: Accepted Speakers / Paper Authors: Fully covered travel and lodging expenses ... funded directly by department cost centers (cost_centers.csv CC-2010 for Applied Research...).",
            "cost_centers.csv: CC-2010,Foundation Model Pre-Training,Applied Research,...,350000,Austin",
        ],
        "question_type": "multi_hop",
        "synthesizer_name": "handauthored",
    },
    {
        "question": "What is the PagerDuty service ID for the Cloud-Infra-SRE rotation during the 12:00-24:00 UTC shift, and what is the annual discretionary spending limit for the cost center that owns that team?",
        "ground_truth_answer": "PD-SVC-SRE-02 (primary contact sre-oncall-austin@helixforge.example). The Cloud Infrastructure & SRE cost center (CC-1030) has a $250,000 annual discretionary limit.",
        "reference_contexts": [
            "oncall_escalation_matrix.csv: Cloud-Infra-SRE,L1 On-Call,12:00-24:00,sre-oncall-austin@helixforge.example,Chloe Bennett...,PD-SVC-SRE-02",
            "cost_centers.csv: CC-1030,Cloud Infrastructure & SRE,Platform Engineering,chloe.bennett@helixforge.example,...,250000,Austin",
        ],
        "question_type": "multi_hop",
        "synthesizer_name": "handauthored",
    },
    {
        "question": "For an Enterprise Tier 1 customer, what is the P1 initial response SLA, and whose approval is needed to issue a $12,000 SLA breach credit?",
        "ground_truth_answer": "The P1 response SLA for Enterprise Tier 1 is 15 minutes (24/7). A $12,000 credit falls in the 10,001-50,000 band, requiring VP Customer Success sign-off plus Finance Controller approval.",
        "reference_contexts": [
            "customer_support_slas.md: P1 - Critical | ... | 15 minutes (24/7) | ... [Enterprise Tier 1]",
            "approval_matrix.csv: Customer SLA Breach Credits,10001,50000,VP Customer Success,Finance Controller,3,...",
        ],
        "question_type": "multi_hop",
        "synthesizer_name": "handauthored",
    },
    {
        "question": "A Remote-Primary employee wants to separately expense their home internet bill in addition to receiving the monthly remote stipend. Is that allowed?",
        "ground_truth_answer": "No. Home-office internet is not reimbursable as a separate expense; it is already covered by the $150/month remote stipend under the Remote Work policy.",
        "reference_contexts": [
            "remote_work.md: Remote-Primary staff receive a $150 monthly stipend for internet and workspace costs...",
            "expense_policy.md: Home-office internet is not reimbursable; it is covered by the $150 monthly remote stipend in the Remote Work policy.",
        ],
        "question_type": "multi_hop",
        "synthesizer_name": "handauthored",
    },
    {
        "question": "If a Distinguished Engineer (L8) with 3 years of tenure voluntarily departs, how long is their stock option exercise window, and who does an L8 report to according to the leveling rubric?",
        "ground_truth_answer": "5-year exercise window (they have >= 2 years tenure). An L8 Distinguished Engineer has enterprise-level technical strategy reporting directly to CTO Devon Hale or CEO Mara Chen.",
        "reference_contexts": [
            "equity_refresh_and_options_policy.md: Employees with >= 2 years tenure receive an extended 5-year exercise window for vested options upon voluntary departure.",
            "leveling_rubric.md: Level 8 (L8) - Distinguished Engineer: Enterprise-level technical strategy reporting directly to CTO Devon Hale or CEO Mara Chen.",
        ],
        "question_type": "multi_hop",
        "synthesizer_name": "handauthored",
    },
    {
        "question": "Who is authorized to trigger emergency secret rotation after a breach, and within how many minutes must the CEO be notified if that breach is a confirmed SEV-1 Restricted data exposure?",
        "ground_truth_answer": "The CISO or Incident Commander triggers emergency secret rotation. For a confirmed SEV-1 Restricted data exposure, the CEO must be notified within 30 minutes.",
        "reference_contexts": [
            "sop_secrets_rotation_vault.txt: CISO or Incident Commander triggers emergency rotation CLI...",
            "incident_response.md: SEV-1: ... CEO is notified within 30 minutes.",
        ],
        "question_type": "multi_hop",
        "synthesizer_name": "handauthored",
    },
    # ---------------------------------------------------------------- reasoning
    {
        "question": "An engineer wants to expense a $60/month SaaS subscription with only their manager's approval, no Procurement ticket. Is this compliant?",
        "ground_truth_answer": "No. Tools costing $50/month or more (or any annual contract) must go through Procurement; manager approval alone is only sufficient for tools under $50/month.",
        "reference_contexts": ["expense_policy.md: engineering tools under $50/month may be expensed with manager approval. Anything $50/month or more ... must go through Procurement."],
        "question_type": "reasoning",
        "synthesizer_name": "handauthored",
    },
    {
        "question": "An employee lives 60 miles from the Austin office and comes in occasionally. Are they Office-Primary or Remote-Primary, and do they get the monthly stipend?",
        "ground_truth_answer": "They are Remote-Primary, since Office-Primary only applies within 50 miles of Austin, Dublin, or Singapore. As Remote-Primary they receive the $150 monthly stipend.",
        "reference_contexts": ["remote_work.md: Employees within 50 miles of Austin, Dublin, or Singapore are Office-Primary... Employees outside those radiuses are Remote-Primary. Remote-Primary staff receive a $150 monthly stipend."],
        "question_type": "reasoning",
        "synthesizer_name": "handauthored",
    },
    {
        "question": "A manager receives a harassment complaint about a direct report and decides to look into it quietly himself before telling People Ops. Does this follow the Code of Conduct?",
        "ground_truth_answer": "No. Managers who receive a report must forward it to People Operations within 24 hours and must not investigate privately.",
        "reference_contexts": ["code_of_conduct.md: Managers who receive a report must forward it to People Operations within 24 hours and must not investigate privately."],
        "question_type": "reasoning",
        "synthesizer_name": "handauthored",
    },
    {
        "question": "An employee wants to paste a page of the internal (Internal-classified) handbook into their personal ChatGPT account to help rewrite it, after deleting any names. Is this allowed?",
        "ground_truth_answer": "Yes. Internal handbook text may be pasted into unapproved personal AI tools, but only after customer names and credentials are removed.",
        "reference_contexts": ["ai_usage_policy.md: Internal handbook text (Internal classification) may be pasted into unapproved tools only after customer names and credentials are removed."],
        "question_type": "reasoning",
        "synthesizer_name": "handauthored",
    },
    {
        "question": "An interviewer submits their written scorecard in Ashby 30 hours after finishing the interview. Did they meet the scorecard SLA?",
        "ground_truth_answer": "No. The scorecard SLA is 24 hours after completing the interview, and 30 hours exceeds that.",
        "reference_contexts": ["interview_loop_and_hiring_standards.md: Interviewers must submit independent, written scorecards in Ashby within 24 hours of completing the interview session."],
        "question_type": "reasoning",
        "synthesizer_name": "handauthored",
    },
    # ---------------------------------------------------------------- abstain
    {
        "question": "What is HelixForge's current stock price?",
        "ground_truth_answer": "The provided HelixForge handbook does not include stock price information.",
        "reference_contexts": [],
        "question_type": "abstain",
        "synthesizer_name": "handauthored",
    },
    {
        "question": "What is the CEO's annual salary at HelixForge?",
        "ground_truth_answer": "The handbook does not publish executive salary figures.",
        "reference_contexts": [],
        "question_type": "abstain",
        "synthesizer_name": "handauthored",
    },
    {
        "question": "What does vendor_security.md say about approved third-party security vendors?",
        "ground_truth_answer": "vendor_security.md is referenced by cross-links in other policies but is not present in this corpus, so its contents cannot be answered from the provided documents.",
        "reference_contexts": [],
        "question_type": "abstain",
        "synthesizer_name": "handauthored",
    },
    {
        "question": "According to secrets_handling.md, how are cryptographic keys generated for new services?",
        "ground_truth_answer": "secrets_handling.md is referenced by cross-links (e.g. in the disaster recovery and secrets rotation SOPs) but is not itself present in this corpus, so its contents cannot be answered from the provided documents.",
        "reference_contexts": [],
        "question_type": "abstain",
        "synthesizer_name": "handauthored",
    },
    {
        "question": "How many total lines of code does HelixForge's inference engine codebase have?",
        "ground_truth_answer": "The handbook does not contain codebase size or line-count information.",
        "reference_contexts": [],
        "question_type": "abstain",
        "synthesizer_name": "handauthored",
    },
]

assert len(ITEMS) == 40, f"expected 40 hand-authored items, got {len(ITEMS)}"

_TYPE_ORDER = ("simple", "multi_hop", "reasoning", "abstain")


def select_balanced_items(items: list[dict[str, Any]], limit: int) -> list[dict[str, Any]]:
    """Pick ``limit`` items while preserving question-type mix (largest remainder)."""
    if limit <= 0:
        raise ValueError("limit must be positive")
    if limit >= len(items):
        return list(items)

    by_type: dict[str, list[dict[str, Any]]] = {key: [] for key in _TYPE_ORDER}
    for item in items:
        qtype = str(item.get("question_type") or "simple")
        by_type.setdefault(qtype, []).append(item)

    total = len(items)
    quotas: dict[str, int] = {}
    remainders: list[tuple[float, str]] = []
    assigned = 0
    for qtype, group in by_type.items():
        exact = limit * len(group) / total
        base = int(exact)
        quotas[qtype] = base
        assigned += base
        remainders.append((exact - base, qtype))

    remainders.sort(key=lambda pair: pair[0], reverse=True)
    idx = 0
    while assigned < limit:
        quotas[remainders[idx % len(remainders)][1]] += 1
        assigned += 1
        idx += 1

    selected: list[dict[str, Any]] = []
    seen_types = set(_TYPE_ORDER)
    for qtype in _TYPE_ORDER:
        selected.extend(by_type.get(qtype, [])[: quotas.get(qtype, 0)])
    for qtype, group in by_type.items():
        if qtype not in seen_types:
            selected.extend(group[: quotas.get(qtype, 0)])
    return selected
