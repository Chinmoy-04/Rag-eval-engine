# Model Release Governance & Checkpoint Promotion Policy
*HelixForge fictional handbook.*

Owner: Dr. Alina Rostova, Head of Foundation Model Pre-Training (alina.rostova@helixforge.example / CC-2010). Approved by: Devon Hale (CTO) and Elena Voss (CISO). Effective date: February 1, 2026.

## 1. Overview & Release Tiers
To ensure stability, safety, and performance across HelixForge distributed inference clusters, all new foundation model checkpoints and architecture updates progress through four formal release tiers:

- **Tier 1 (Alpha / Experimental)**: Internal research environment only. Accessible to Applied Research team (CC-2010 / CC-2020) for benchmark sweeps and alignment tuning.
- **Tier 2 (Beta / Dogfood)**: Internal company-wide deployment across ~420 FTE accounts for real-world usage and dogfood evaluation.
- **Tier 3 (Release Candidate / Private Preview)**: Selected Enterprise Tier 1 customers opted into private previews via feature flags (per sop_feature_flag_lifecycle.txt).
- **Tier 4 (General Availability / GA)**: Global production deployment serving all enterprise and developer API endpoints.

## 2. Promotion Gates & Required Approvals

| Promotion Step | Minimum Soak Time | Quality & Safety Gate Requirements | Required Sign-Offs |
| :--- | :--- | :--- | :--- |
| **Alpha -> Beta** | 7 Days | Loss convergence verified; zero NaN gradients; safety scan bypass < 0.1% | Alina Rostova & Soren Lindqvist |
| **Beta -> RC** | 14 Days | Dogfood NPS > 40; Automated Safety Suite bypass < 0.05% (model_eval_ethics_policy.md) | Zheng Wei & Marcus Vance |
| **RC -> GA** | 14 Days | Zero P1/P2 regression bugs; P99 inference latency within SLA; multi-region backup complete | Devon Hale (CTO) & Elena Voss (CISO) |

## 3. Deprecation and Sunset Lifecycle
- Base model versions in GA are supported for a minimum of **12 months** following the release of a succeeding major version.
- Deprecation notices must be posted to the public status portal with at least **90 days** advance notice to enterprise customers.

## 4. Cross-Links
- Model safety benchmarks and ethics gates: model_eval_ethics_policy.md.
- Feature flag canary ramping: sop_feature_flag_lifecycle.txt.
- Checkpoint backup and replication: sop_model_checkpoint_backup.txt.
