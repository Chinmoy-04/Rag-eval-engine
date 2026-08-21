# Customer Proof of Concept (POC) & Evaluation Governance
*HelixForge fictional handbook.*

Owner: Diego Morales, Head of Customer Solutions Engineering (diego.morales@helixforge.example / CC-3020). Approved by: Priya Nair (VP Business Operations) and Julian Sterling (Finance Controller). Effective date: February 1, 2026.

## 1. Purpose & POC Objectives
Proof of Concept (POC) engagements allow prospective enterprise customers to benchmark HelixForge distributed inference latency, throughput, and custom model fine-tuning accuracy against their proprietary workloads. This policy sets guardrails on compute credit allocations, timeline duration, and technical success criteria.

## 2. Standard POC Parameters & Guardrails
- **Standard Duration**: Exactly **30 calendar days**. Extensions up to an additional 14 days require approval from Diego Morales.
- **Compute Credit Cap**: Standard POC allowance is capped at **,000 USD** in compute credits evaluated at internal rate sheet rates (see cloud_compute_rate_sheet.csv). Credits exceeding ,000 require Division VP sign-off per pproval_matrix.csv.
- **Infrastructure Isolation**: POC workloads are provisioned on multi-tenant shared inference clusters or dedicated VPC sandboxes with ephemeral storage. Under no circumstances may prospective customers receive production root bastion access (see sop_production_ssh_yubikey.txt).

## 3. Success Criteria & Technical Qualification
Every POC must establish an agreed Technical Evaluation Plan (TEP) signed by the customer technical sponsor prior to kickoff, defining:
1. **Target Latency / TTFT**: Time-To-First-Token (e.g. < 35ms on H100 SXM5).
2. **Throughput Target**: Sustained tokens per second (TPS) under peak concurrent concurrency.
3. **Data Classification**: Customer data ingested during POC is classified as **Confidential** and subject to automated 30-day post-POC purge per customer_data_deletion_and_sanitization.md.

## 4. Conversion or Decommissioning Workflow
- Upon commercial contract execution, the POC environment seamlessly transitions into Enterprise Tier 1 or Tier 2 production serving.
- If the customer does not convert within 14 days of POC conclusion, all fine-tuned checkpoints and uploaded validation sets are cryptographically erased per customer_data_deletion_and_sanitization.md.

## 5. Cross-Links
- Compute SKU rate cards: cloud_compute_rate_sheet.csv.
- Spend approval tiers: approval_matrix.csv and cost_centers.csv (CC-3020).
- Customer data deletion and purging: customer_data_deletion_and_sanitization.md.
- Support tiers and SLAs: customer_support_slas.md.
