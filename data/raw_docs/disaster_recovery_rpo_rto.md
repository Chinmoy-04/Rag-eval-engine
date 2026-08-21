# Disaster Recovery, RPO, and RTO Framework
*HelixForge fictional handbook.*

Owner: Tariq Mansoor, Head of Model Serving & Inference (tariq.mansoor@helixforge.example). Reviewed by: Devon Hale (CTO) and Elena Voss (CISO). Effective: February 2026.

## 1. Objectives and Scope
This policy governs disaster recovery (DR) planning, Recovery Point Objectives (RPO), and Recovery Time Objectives (RTO) across all HelixForge production environments and distributed training clusters. HelixForge maintains active infrastructure across primary regions in Austin (US-Central) with hot-standby and warm-dr regional failovers in Dublin (EU-West) and Singapore (AP-East).

## 2. Criticality Tiers and Target Metrics

| Tier | System / Workload Description | Target RPO | Target RTO | Failover Mechanism |
| :--- | :--- | :--- | :--- | :--- |
| **Tier 0** | Core Inference Gateway, User Auth (Okta/Vault tokens), API Routing | <= 1 minute | <= 15 minutes | Multi-region active-active automatic BGP route shift |
| **Tier 1** | Model Serving Pods, Customer Metadata DB, Vector Index Store | <= 15 minutes | <= 1 hour | Hot-standby replication with automated database promotion |
| **Tier 2** | Model Fine-Tuning Workers, Training Pipeline Checkpoints, Billing Aggregators | <= 4 hours | <= 8 hours | Automated rebuild from snapshot in secondary cloud zone |
| **Tier 3** | Internal Evaluation Dashboards, Dev/Staging Sandboxes, Historical Logs | <= 24 hours | <= 48 hours | Cold restore from encrypted S3/GCS glacier archive |

## 3. Production Access and Failover Execution
1. Initiating a manual DR failover requires dual authorization: Devon Hale (CTO) or Chloe Bennett (Cloud Infra Lead), alongside Elena Voss (CISO).
2. Production access during a DR event requires YubiKey hardware authentication and an active emergency ticket in the SEV queue. Standing emergency access is capped at **8 hours** maximum before re-authentication is enforced.
3. Network cutover to secondary regions must trigger automated health checks across all Tier 0 inference clusters before DNS cutover is marked complete.

## 4. DR Testing and Simulation Cadence
- **Tier 0/1 Simulation**: Conducted **semi-annually** (Q1 and Q3 of the fiscal year, which begins February 1). Unannounced tabletop drills occur quarterly.
- **Backup Integrity Validation**: Automated daily backup verification checks; monthly test restores of customer metadata databases to isolated scratch environments.
- Results of DR tests must be archived in the compliance vault for SOC 2 Type II audit readiness.

## 5. Cross-Links
- Incident response and status updates: status_page_rules.md and customer_support_slas.md.
- Emergency access and secrets handling: secrets_handling.md and approval_matrix.csv.
- Cloud compute budget allocation: cost_centers.csv (CC-1020, CC-1030).
