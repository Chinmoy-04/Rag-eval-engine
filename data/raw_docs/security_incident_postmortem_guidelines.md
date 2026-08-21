# Blameless Post-Mortem & Root Cause Analysis (RCA) Guidelines
*HelixForge fictional handbook.*

Owner: Chloe Bennett, Head of Cloud Infrastructure & SRE (chloe.bennett@helixforge.example / CC-1030). Approved by: Devon Hale (CTO) and Elena Voss (CISO). Effective date: February 1, 2026.

## 1. Blameless Culture & Purpose
At HelixForge, outages and security incidents are viewed as systemic learning opportunities rather than individual failures. Post-mortems focus on identifying brittle architectural points, inadequate guardrails, and operational gaps to improve platform resilience across Austin, Dublin, and Singapore.

## 2. Incident Criteria Requiring Formal Post-Mortem
A formal written Post-Mortem is mandatory for any of the following triggers:
- Any declared **SEV-0** or **SEV-1** incident (see severity_definitions.csv).
- Any **SEV-2** incident resulting in customer-facing degradation exceeding **30 minutes**.
- Any data loss event affecting customer metadata or model checkpoints (Tier 0/Tier 1 RPO breach per disaster_recovery_rpo_rto.md).
- Any security vulnerability involving unauthorized access to Restricted data.

## 3. Timelines & Publishing SLAs
1. **Internal Wiki RCA Draft**: The Incident Commander (IC) must complete the initial draft in the engineering wiki within **72 hours** of incident resolution.
2. **Post-Mortem Review Meeting**: Held within **5 business days** of incident closure during core collaboration hours (14:00-17:00 UTC). Attended by the IC, component leads, and division VP.
3. **Customer-Facing Summary**: For SEV-1 incidents impacting Enterprise Tier 1 customers, a sanitized executive RCA must be delivered to Customer Success within **5 business days** per status_page_rules.md.

## 4. Required Post-Mortem Document Structure
Every post-mortem document must contain:
- **Incident Summary**: Exact start, detection, mitigation, and resolution timestamps in UTC. Total customer downtime duration.
- **Root Cause (5-Whys)**: Detailed systemic breakdown of underlying failure triggers.
- **Impact Analysis**: Quantitative metrics (e.g. number of dropped API requests, percentage error rate spike, SLA credit liabilities per pproval_matrix.csv).
- **Action Items (Preventative Corrective Actions)**: Prioritized Jira tickets assigned to specific owners with strict 30-day resolution SLAs. Action item completion is audited during quarterly SOC 2 reviews (soc2_compliance_controls.csv).

## 5. Cross-Links
- Severity definitions and IC roles: severity_definitions.csv.
- Public status page updates and customer comms: status_page_rules.md and customer_support_slas.md.
- SOC 2 incident control compliance: soc2_compliance_controls.csv.
