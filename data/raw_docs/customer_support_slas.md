# Customer Support Service Level Agreements (SLAs)
*HelixForge fictional handbook.*

Owner: Rachel Adams, Head of Enterprise Technical Support (rachel.adams@helixforge.example). Approved by: Priya Nair (VP Business Operations) and Devon Hale (CTO). Effective date: February 1, 2026.

## 1. Overview and Support Tiers
HelixForge provides tiered technical support for customers deploying our distributed AI inference clusters and fine-tuning pipelines. Support entitlements are determined by the customer's contractual subscription tier:

- **Enterprise Tier 1 (Mission-Critical)**: 24/7/365 coverage for all severities. Includes dedicated Technical Account Manager (TAM) and direct Slack bridge.
- **Enterprise Tier 2 (Production)**: 24/7/365 for Critical (P1) and High (P2); 09:30–17:30 local time (Austin, Dublin, Singapore) for P3/P4.
- **Standard (Developer)**: Business hours support only (09:30–17:30 local office hours). Core collaboration window is 14:00–17:00 UTC.
- **Community / Evaluation**: Best-effort async support via documentation forum; no contractual SLA.

## 2. Severity Definitions and Target Response Times

| Severity Level | Definition | Enterprise Tier 1 SLA | Enterprise Tier 2 SLA | Standard SLA |
| :--- | :--- | :--- | :--- | :--- |
| **P1 - Critical** | Production cluster complete outage, data corruption, or total API failure with no workaround. | 15 minutes (24/7) | 30 minutes (24/7) | 2 business hours |
| **P2 - High** | Severe performance degradation, model inference latency > 400% above baseline, or non-critical worker node failures. | 1 hour (24/7) | 2 hours (24/7) | 4 business hours |
| **P3 - Medium** | Minor feature defect, non-blocking bug in admin dashboard, or query optimization request. | 4 business hours | 8 business hours | 1 business day |
| **P4 - Low** | General questions, documentation clarification, feature enhancement requests. | 12 business hours | 24 business hours | 2 business days |

## 3. Escalation and On-Call Engagement
When a P1 ticket is received for Enterprise Tier 1:
1. Support Engineer acknowledges within 15 minutes and verifies production status.
2. If confirmed as an active infrastructure failure, Support Engineer triggers a SEV-1 incident in PagerDuty, paging the Platform Engineering on-call primary.
3. The Incident Commander opens a customer bridge within 25 minutes of ticket creation.
4. Support updates the customer every 30 minutes until resolution or downgrade, aligned with status_page_rules.md.

Note: Engineers taking PTO do not have their on-call shifts automatically reassigned; engineers must manually swap shifts on the PagerDuty roster prior to taking PTO.

## 4. SLA Breach Credits and Authorization
If HelixForge breaches the initial response SLA for P1 or P2 incidents:
- Enterprise Tier 1 customers receive a 5% monthly service credit per breach, capped at 30% of monthly recurring revenue (MRR).
- Credit approvals must follow approval_matrix.csv: credits up to ,000 require Head of Enterprise Support sign-off; credits above ,000 require VP sign-off and Finance Controller approval.
- Cost center for SLA penalty adjustments is CC-3010 (Enterprise Technical Support).

## 5. Cross-Links
- Internal incident severity levels and war room protocols: status_page_rules.md and disaster_recovery_rpo_rto.md.
- Financial sign-offs and credit authorizations: approval_matrix.csv and cost_centers.csv.
- Holiday staffing and on-call holiday multipliers: holiday_calendar_2026.csv.
