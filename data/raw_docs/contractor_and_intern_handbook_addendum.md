# Contractor & Intern Handbook Addendum
*HelixForge fictional handbook.*

Owner: Priya Nair, VP Business Operations / People Ops (priya.nair@helixforge.example / CC-4010). Approved by: Mara Chen (CEO) and Elena Voss (CISO). Effective date: February 1, 2026.

## 1. Scope and Workforce Classification
HelixForge maintains an extended workforce comprising ~60 independent contractors and specialist consultants alongside an annual summer intern cohort (~15 interns). This addendum outlines policy modifications and security boundaries applicable specifically to non-FTE personnel.

## 2. Contractor Terms and Engagement Limits
- **Maximum SOW Tenure**: Contractor Statements of Work (SOWs) are limited to **12 continuous months**. Any extension beyond 12 months requires written justification by the Division VP and sign-off from Priya Nair.
- **Equipment & Hardware**: Contractors are provisioned managed hardware under Tier-CON-1 (managed Dell XPS 13 or MacBook Air per hardware_procurement_matrix.csv). Use of personal unmanaged devices (BYOD) for production environments is strictly prohibited.
- **Benefits Exclusions**: Contractors are not eligible for company equity programs, healthcare benefits, Modern Health EAP counseling, or the ,500 continuous learning stipend.
- **Invoicing & SOW Authorizations**: Contractor invoices must be billed against approved department cost centers (cost_centers.csv) and follow the spend approval thresholds defined in pproval_matrix.csv.

## 3. Intern Cohort Program Rules
- **Mentorship & Supervision**: Every intern is paired with an L5+ Senior Engineer or Researcher (per leveling_rubric.md) who serves as primary technical mentor.
- **Production Guardrails**: Interns are restricted from holding direct production SSH bastion credentials (see sop_production_ssh_yubikey.txt). All code written by interns must be peer-reviewed and merged by an L4+ full-time engineer.
- **Equipment & Stipend**: Interns receive standard L3 engineering hardware (Tier-ENG-1) and a one-time  remote setup stipend.

## 4. System Access and Offboarding
1. Contractor and intern accounts in Okta and Google Workspace are configured with a strict expiration date matching the contract end date.
2. Upon contract termination or project conclusion, Workplace IT executes immediate deprovisioning per sop_laptop_imaging_deprovisioning.txt.
3. Departing non-FTE personnel must return all company property within **14 calendar days** to Austin HQ or regional offices.

## 5. Cross-Links
- Laptop provisioning and retrieval: sop_laptop_imaging_deprovisioning.txt.
- Hardware tiers and allocation: hardware_procurement_matrix.csv.
- Spend approval tiers: approval_matrix.csv and cost_centers.csv.
