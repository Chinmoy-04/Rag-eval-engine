# Model Evaluation, Safety, and Ethics Policy
*HelixForge fictional handbook.*

Owner: Zheng Wei, Evaluation & Safety Benchmarks Lead (zheng.wei@helixforge.example). Approved by: Devon Hale (CTO) and Elena Voss (CISO). Effective: February 1, 2026.

## 1. Purpose and Guiding Principles
As an AI infrastructure provider serving enterprise customers across Austin, Dublin, and Singapore, HelixForge enforces rigorous evaluation and safety standards across all base foundation models, fine-tuned weights, and agentic inference runtimes. 

Our core mandate:
1. Prevent catastrophic misuse, autonomous privilege escalation, and unauthorized data leakage.
2. Maintain transparency in benchmark reporting and model card disclosures.
3. Comply with emerging global standards including the EU AI Act (Tier 2 GPAI regulations) and NIST AI RMF.

## 2. Mandatory Evaluation Gates Before Deployment
Every model checkpoint intended for customer serving or external release must clear three sequential gates:

1. **Automated Safety Suite (Gate 1)**: Automated scanning against 10,000+ adversarial jailbreak and prompt injection prompts (see sop_prompt_injection_reporting.txt). Maximum allowed bypass rate is **< 0.05%**.
2. **Toxicity and Bias Evaluation (Gate 2)**: Benchmarked against standard toxicity datasets. Severe toxicity score must not exceed **0.01**.
3. **Red-Team Human Review (Gate 3)**: Multi-turn red-teaming conducted by internal research staff (CC-2030) or authorized third-party security vendors evaluated under endor_security.md.

## 3. Human Annotation & Data Ethics Standards
- **Data Filtering**: Pre-training and fine-tuning datasets must undergo automated PII scrubbing (regex + NER models) to remove credit cards, social security numbers, and private credentials.
- **Annotation Compensation**: Third-party contractors providing human feedback (RLHF / RLAIF) must be compensated at or above living wage benchmarks in their local geographic jurisdiction, audited annually by People Ops (Priya Nair).
- **Copyright & Open Source Compliance**: Data scrapers and dataset imports must adhere strictly to open_source_license_policy.md. Scraped data containing explicit 
obots.txt disallow clauses is strictly prohibited.

## 4. Safety Escalation & Zero-Day Patching
If an active model in production exhibits critical safety vulnerabilities (e.g. cross-tenant extraction or unconstrained tool loop execution):
- An immediate **SEV-0** or **SEV-1** incident is declared per severity_definitions.csv.
- The Incident Commander coordinates with Zheng Wei and Tariq Mansoor to apply runtime logit-bias suppression or fall back to an earlier safe checkpoint within **60 minutes**.

## 5. Cross-Links
- Jailbreak reporting SOP and severity tiers: sop_prompt_injection_reporting.txt.
- Severity levels and status page updates: severity_definitions.csv and status_page_rules.md.
- Research division cost center: cost_centers.csv (CC-2030) and software_catalog.csv.
