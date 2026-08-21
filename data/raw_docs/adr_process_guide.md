# Architectural Decision Records (ADR) Process & Guide
*HelixForge fictional handbook.*

Owner: Devon Hale, CTO (devon.hale@helixforge.example). Operational Lead: Marcus Vance, Head of Core Compute (marcus.vance@helixforge.example / CC-1010). Effective date: February 1, 2026.

## 1. Purpose of ADRs
Architectural Decision Records (ADRs) capture significant architectural and technical design choices across HelixForge distributed inference clusters, model training pipelines, and data platforms. The written KB is the source of truth for all technical standards; informal Slack consensus does not constitute architectural approval.

## 2. When is an ADR Required?
An engineer must draft an ADR when a proposed change meets any of the following criteria:
- Introduces a new persistent data store, message broker, or external cloud service (see software_catalog.csv).
- Alters core public/private API contracts or authentication flows.
- Changes system RPO/RTO boundaries or multi-region failover topology (see disaster_recovery_rpo_rto.md).
- Impacts cross-border data transfer boundaries (see data_residency_matrix.csv).
- Establishes a new programming language, major framework, or distributed runtime (e.g. Ray / vLLM upgrades).

## 3. Lifecycle and Decision Workflow
1. **Proposed**: Author forks the repository template at docs/adr/template.md and submits a pull request with status PROPOSED.
2. **Review & RFC Window**: The PR enters an open RFC period of **10 business days**. All L5+ engineers (per leveling_rubric.md) in relevant pods are requested for review.
3. **Architecture Review Board (ARB)**: Meets bi-weekly on Thursdays at 15:00 UTC (during core collaboration hours 14:00–17:00 UTC). Chaired by Devon Hale and Marcus Vance.
4. **Outcome**:
   - ACCEPTED: Merged into main branch and archived in the active ADR index.
   - REJECTED: Merged with detailed rationale documenting why the approach was declined.
   - SUPERSEDED: Linked to a newer ADR when architectural patterns evolve.

## 4. Required ADR Document Structure
Every ADR must include:
- **Title**: Sequential number and descriptive slug (e.g., ADR-042-vllm-paged-attention-migration.md).
- **Context & Problem Statement**: Clear explanation of constraints, scale targets, and latency requirements.
- **Decision Drivers**: Quantitative metrics (e.g. GPU memory utilization, P99 latency < 50ms).
- **Considered Options**: At least 3 evaluated alternatives with pros/cons matrix.
- **Decision Outcome**: Selected option with justification and implementation plan.
- **Compliance & Security Impact**: Assessment against vendor_security.md and data_residency_matrix.csv.

## 5. Cross-Links
- Leveling rubric and L5+ review expectations: leveling_rubric.md.
- Software and infrastructure catalog: software_catalog.csv.
- Disaster recovery and multi-region specs: disaster_recovery_rpo_rto.md.
