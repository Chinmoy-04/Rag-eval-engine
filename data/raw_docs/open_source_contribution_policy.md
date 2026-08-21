# Open Source Software (OSS) Licensing & Contribution Policy
*HelixForge fictional handbook.*

Owner: Clara Dupont, Head of Legal, Regulatory & Compliance (clara.dupont@helixforge.example / CC-4030). Technical Lead: Marcus Vance (CC-1010). Effective date: February 1, 2026.

## 1. Purpose & Guiding Principles
HelixForge builds upon and actively contributes to the open-source AI ecosystem. This policy establishes rules for incorporating third-party open-source libraries into HelixForge products and contributing internal code upstream.

## 2. Inbound Open Source License Classification

| Category | Permitted Licenses | Restrictions & Approval Requirements |
| :--- | :--- | :--- |
| **Category A (Permissive)** | MIT, Apache 2.0, BSD-2/3-Clause, ISC | Approved for immediate use in all commercial and proprietary products without Legal pre-screening. |
| **Category B (Weak Copyleft)** | LGPL v2.1/v3, MPL 2.0, EPL 2.0 | Permitted only as dynamically linked shared libraries (.so / .dylib). Must not be statically compiled into core model engine binaries. |
| **Category C (Strong Copyleft / Prohibited)** | GPL v2/v3, AGPL v3, SSPL, Commons Clause | **STRICTLY PROHIBITED** in all proprietary inference serving runtimes, SaaS microservices, and distributed model kernels. |

## 3. Outbound Contribution Workflow
1. **Bug Fixes & Minor Patches**: Employees may contribute bug fixes and documentation updates to existing open-source projects under permissive licenses without formal review.
2. **New Open-Source Project Release**: Open-sourcing internal HelixForge tools, benchmarks, or SDKs requires approval from the Open Source Review Board (OSRB: Clara Dupont, Devon Hale, and Marcus Vance).
3. **Contributor License Agreements (CLAs)**: Corporate CLAs must be signed exclusively by Clara Dupont; individual employees are barred from binding corporate IP without authorization per pproval_matrix.csv.

## 4. Model Weights and Open Weights Release Policy
- Releasing trained foundation weights under permissive open weights licenses (e.g., Apache 2.0 or HelixForge Community License) requires clearance from the Model Safety Committee (model_eval_ethics_policy.md) and dual sign-off from Devon Hale (CTO) and Mara Chen (CEO).

## 5. Cross-Links
- Model evaluation safety gates: model_eval_ethics_policy.md.
- Software inventory and vendor risk: software_catalog.csv.
- Spend and legal contract authorization: approval_matrix.csv and cost_centers.csv (CC-4030).
