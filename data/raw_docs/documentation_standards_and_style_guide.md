# Technical Documentation Standards & Style Guide
*HelixForge fictional handbook.*

Owner: Devon Hale, CTO (devon.hale@helixforge.example). Editor-in-Chief: Rachel Adams, Head of Enterprise Technical Support (rachel.adams@helixforge.example / CC-3010). Effective date: February 1, 2026.

## 1. Documentation as Source of Truth
At HelixForge, written documentation is the primary mechanism for scaling technical decisions, onboarding team members, and maintaining operational consistency across Austin, Dublin, and Singapore. The written KB is the single source of truth; if an architecture pattern or policy is not documented in the repository, it does not exist.

## 2. Document Taxonomy & File Organization
All internal knowledge is authored in GitHub Markdown (.md), Standard SOP Text (.txt), or tabular CSVs (.csv):
- /docs/architecture/: System design docs, RFCs, and Architectural Decision Records (ADRs per dr_process_guide.md).
- /docs/sop/: Standard Operating Procedures detailing repeatable, step-by-step engineering and security workflows.
- /docs/policies/: Corporate and HR governance policies owned by Division VPs.
- /docs/reference/: Machine-readable CSV lookup tables (e.g. rate sheets, cost centers, calendars).

## 3. Authoring Style Guide & Quality Rules
Every narrative document must adhere to the following baseline rules:
1. **Metadata Header**: Top of doc must specify Document Title, Owner Name, Department/Cost Center, Review Date, and Effective Date.
2. **Concrete Retrievability**: Include exact numbers, time limits, tool names, and SLA deadlines. Avoid vague statements like " respond promptly\ or \keep backups periodically\.
3. **Multi-Hop Cross-Linking**: Every doc must include a dedicated ## Cross-Links section referencing at least two related policies, CSV tables, or SOPs.
4. **Code and Command Blocks**: Shell commands, CLI snippets, and config blocks must be complete, functional examples using @helixforge.example domain naming.
5. **Data Classification**: Classify documents according to Internal, Confidential, or Restricted standards.

## 4. Document Review & Staleness Lifecycle
- **Semi-Annual Policy Review**: All active documents must be re-reviewed by the designated owner every **6 months**.
- **Automated Staleness Bot**: A GitHub Action flags any document unmodified for > 180 days, creating a review task for the owning department head.
- **Deprecation**: Deprecated documents must be prefixed with [DEPRECATED], containing a redirect link to the superseding guide.

## 5. Cross-Links
- ADR authoring and review lifecycle: adr_process_guide.md.
- Department cost centers and ownership: cost_centers.csv.
- Customer support documentation standards: customer_support_slas.md.
