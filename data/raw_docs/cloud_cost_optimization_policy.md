# Cloud Infrastructure Cost Optimization & FinOps Policy
*HelixForge fictional handbook.*

Owner: Chloe Bennett, Head of Cloud Infrastructure & SRE (chloe.bennett@helixforge.example / CC-1030). Approved by: Devon Hale (CTO) and Julian Sterling (Finance Controller). Effective date: February 1, 2026.

## 1. Purpose & Scope
Distributed GPU compute and cloud data infrastructure represent HelixForge largest operational expenditure. This policy establishes FinOps standards, resource allocation guardrails, and waste reduction requirements across all AWS, GCP, and bare-metal GPU clusters.

## 2. GPU Cluster Utilization Baselines
- **Production Inference Clusters**: Must maintain an average GPU compute utilization of **>= 75%** over a 7-day rolling window. Clusters dropping below 60% utilization trigger automated scaling down via Kubernetes KEDA.
- **Research & Pre-Training Workloads**: Large training sweeps managed by Applied Research (cost_centers.csv CC-2010) must utilize spot/preemptible instances for at least **40%** of non-critical workers.
- **Checkpointing Hygiene**: Training jobs must implement automated gradient snapshotting every 30 minutes to minimize compute loss from spot preemption.

## 3. Staging and Development Environment Guardrails
1. **Automated Nightly Shutdown**: All development Kubernetes namespaces and staging GPU nodes are automatically scaled to zero replicas at **20:00 local time** on weekdays and remain suspended on weekends.
2. **Weekend Exemptions**: Engineers requiring continuous weekend testing must file an exemption ticket in FIN-OPS approved by their Department Head per pproval_matrix.csv.
3. **Unattached Storage Cleanup**: Unattached EBS/Persistent Volumes older than **7 days** are automatically snapshotted and purged by the Cloud Custodian daemon.

## 4. Budget Overrun Thresholds & Approvals
- Monthly cloud spending is tracked in Datadog FinOps dashboards against department allocations in cost_centers.csv.
- If a department exceeds **85%** of its monthly compute allocation before Day 20 of the billing cycle, an automated alert routes to the Division VP and Julian Sterling.
- Additional GPU capacity procurement must follow unit costs in cloud_compute_rate_sheet.csv and approval limits in pproval_matrix.csv.

## 5. Cross-Links
- Internal GPU and cloud rate cards: cloud_compute_rate_sheet.csv.
- Financial spend approvals: approval_matrix.csv and cost_centers.csv.
- Cloud vendor security reviews: vendor_security.md.
