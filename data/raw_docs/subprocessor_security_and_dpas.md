# Subprocessor Security & Data Processing Agreements (DPA) Policy
*HelixForge fictional handbook.*

Owner: Clara Dupont, Head of Legal, Regulatory & Compliance (clara.dupont@helixforge.example / CC-4030). Reviewed by: Elena Voss (CISO). Effective: February 1, 2026.

## 1. Purpose & Regulatory Scope
Under the General Data Protection Regulation (GDPR Article 28) and Singapore Personal Data Protection Act (PDPA), HelixForge must maintain strict oversight of third-party vendors and subprocessors that store, process, or transmit customer data.

## 2. Subprocessor Engagement Requirements
Before engaging any third-party subprocessor:
1. **Security & SOC 2 Assessment**: Compliance conducts a Tier 1 or Tier 2 security review per endor_security.md. The vendor must possess a current SOC 2 Type II or ISO 27001 certification.
2. **Data Processing Agreement (DPA)**: A binding DPA must be executed incorporating standard contractual clauses (SCCs) for cross-border EU data transfers (per data_residency_matrix.csv).
3. **Spend and Contract Sign-Off**: SOWs and contracts must follow spend authorization thresholds in pproval_matrix.csv.

## 3. Customer Notification SLAs for New Subprocessors
- HelixForge maintains a public roster of all approved subprocessors at 	rust.helixforge.example/subprocessors (see subprocessor_catalog.csv).
- **30-Day Advance Notice**: When adding a new subprocessor handling customer data, HelixForge must notify customers via email and status portal at least **30 calendar days** prior to authorizing data access.
- **Customer Objection Period**: Customers have **14 calendar days** to object to a new subprocessor on reasonable data protection grounds.

## 4. Annual Subprocessor Audit Review
- Compliance conducts an **annual audit** of all active subprocessors in Q4 of the fiscal year.
- Subprocessors failing to provide updated SOC 2 reports within **60 days** of request are placed on probationary status and scheduled for vendor replacement.

## 5. Cross-Links
- Approved subprocessor inventory: subprocessor_catalog.csv.
- Vendor risk tiering: vendor_security.md.
- Data residency and GDPR transfer frameworks: data_residency_matrix.csv.
- Spend approval limits: approval_matrix.csv.
