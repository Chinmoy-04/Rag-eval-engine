# Public and Private Status Page Operating Rules
*HelixForge fictional handbook.*

Owner: Chloe Bennett, Head of Cloud Infrastructure & SRE (chloe.bennett@helixforge.example). Approved by: Devon Hale (CTO) and Elena Voss (CISO). Effective date: February 1, 2026.

## 1. Scope and Platform Architecture
HelixForge maintains two status communication channels:
1. **Public Status Page** (status.helixforge.example): Tracks platform-wide availability of global inference endpoints, authentication gateways, and API routing.
2. **Private Customer Status Portals**: Dedicated tenant views for Enterprise Tier 1 customers reflecting dedicated GPU cluster health and isolated VPC peering links.

The written KB is the source of truth for communications; Slack channels must not be used to issue external uptime commitments.

## 2. Publication Thresholds and Triggers

- **SEV-1 (Critical Outage)**: Mandatory public post within **15 minutes** of incident declaration. Applies if >= 2% of total API traffic is dropping or inference error rate exceeds 5.0%.
- **SEV-2 (Major Impairment)**: Mandatory post within **30 minutes** if customer-facing degradation exceeds 15 minutes continuous duration.
- **SEV-3 (Minor Degradation)**: Optional public post; mandatory private portal update if specific dedicated customer clusters are impacted.
- **Maintenance Windows**: Scheduled maintenance must be posted with at least **5 business days** prior notice, approved by the Platform Engineering division lead.

## 3. Update Cadence and Communication Roles
During active incidents:
- **SEV-1**: Status page updates must be published at least every **30 minutes**, even if only to state that investigation is ongoing.
- **SEV-2**: Status page updates must be published at least every **60 minutes**.
- **Incident Commander (IC)**: Holds sole authority to draft and post public updates. If the IC is unassigned, the Cloud Infrastructure primary on-call assumes posting responsibility.
- **Sanitization Rule**: Public posts must never include customer identifiers, internal IP addresses, unredacted tracebacks, or proprietary model architecture weights. Data classification must strictly adhere to Internal/Confidential guidelines.

## 4. Post-Mortem and Incident Closure SLAs
1. When service is restored, the status post must be moved to 'Monitoring' for a minimum of **60 minutes** before marking 'Resolved'.
2. Internal post-mortem (RCA) draft must be completed in the wiki within **72 hours** of incident resolution.
3. Customer-facing executive summary must be sanitized and delivered to Customer Success within **5 business days** for distribution to Enterprise Tier 1 customers.

## 5. Cross-Links
- Support ticket escalation and customer comms: customer_support_slas.md.
- Incident recovery and RTO/RPO limits: disaster_recovery_rpo_rto.md.
- Hardware provisioning and lab incidents: cost_centers.csv (CC-1030).
