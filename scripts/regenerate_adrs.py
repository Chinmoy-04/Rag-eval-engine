"""Regenerate ADRs and zero-trust policy without boilerplate templates."""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "data" / "raw_docs"

ADRS: list[tuple[str, str, str, list[str], str, str]] = [
    # title, owner, context, drivers, options_chosen, consequences
    (
        "Istio Service Mesh Mutual TLS Enforcement",
        "Mei-Ling Johnson",
        "East-west traffic between inference pods was still plaintext inside the VPC. A SEV-2 review found 14 services without mTLS.",
        [
            "Enforce mTLS for all in-cluster service-to-service calls",
            "Keep P99 sidecar overhead under 3ms",
            "Compatible with existing gRPC model-serving paths",
        ],
        "Adopt Istio STRICT mTLS with PeerAuthentication defaults; allow PERMISSIVE only during a 30-day migration window.",
        "All new services inherit STRICT mode. Break-glass PERMISSIVE requires CISO approval logged in #security-exceptions.",
    ),
    (
        "Chroma vs Managed Vector DB for Internal RAG",
        "Marcus Vance",
        "Internal policy RAG currently uses local Chroma. Product wants multi-tenant isolation and PITR for customer pilots.",
        [
            "RPO ≤ 15 minutes for vector indexes",
            "Per-tenant collection isolation",
            "Keep embed latency under 80ms p95 for MiniLM",
        ],
        "Keep Chroma for internal HelixForge handbook RAG; use managed OpenSearch k-NN for customer-facing retrieval only.",
        "Two retrieval stacks remain. Internal eval tooling continues to target Chroma; customer RAG uses OpenSearch.",
    ),
    (
        "vLLM PagedAttention for Shared GPU Inference",
        "Devon Hale",
        "A100 nodes under-utilized at 41% due to KV-cache fragmentation across concurrent chat sessions.",
        [
            "Increase tokens/sec/GPU by ≥1.8×",
            "Support continuous batching",
            "No regression on SEV-1 on-call paging latency",
        ],
        "Standardize production LLM serving on vLLM with PagedAttention; deprecate HuggingFace text-generation-inference by Q3.",
        "Slurm queue `gpu-infer` updated. Checkpoint restore SOPs must reference vLLM engine versions.",
    ),
    (
        "HashiCorp Vault as Sole Secrets Backend",
        "Elena Voss",
        "AWS Secrets Manager, GitHub Actions secrets, and Vault coexisted; rotation audits failed SOC2 sampling.",
        [
            "Single source of truth for production secrets",
            "90-day automated rotation for API keys",
            "Break-glass human path with dual control",
        ],
        "Vault is mandatory for production; AWS Secrets Manager allowed only for AWS-native service-linked roles.",
        "See `sop_secrets_rotation_vault.txt`. GitHub Actions must fetch runtime secrets from Vault via OIDC.",
    ),
    (
        "Regional Data Residency for EU Customer Logs",
        "Priya Nair",
        "EU-West customers require logs and embeddings to remain in eu-west-1 / eu-central-1.",
        [
            "No cross-border transfer of customer content without DPA addendum",
            "Match `data_residency_matrix.csv` rows",
            "Support dual-region failover inside EU only",
        ],
        "Pin EU customer content stores to eu-west-1 primary and eu-central-1 replica; US tooling may process only aggregated metrics.",
        "On-call runbooks must not copy EU content buckets to us-east-1 for debugging.",
    ),
    (
        "Feature Flag Platform Standardization",
        "Xavier Thorne",
        "Teams used LaunchDarkly, custom Redis flags, and config maps with inconsistent kill-switch semantics.",
        [
            "Global kill switch under 60 seconds",
            "Audit trail of flag changes",
            "Environment promotion gates",
        ],
        "Adopt LaunchDarkly for product flags; forbid ad-hoc Redis boolean flags in production after 2026-06-01.",
        "See `sop_feature_flag_lifecycle.txt` for promotion and rollback.",
    ),
    (
        "ONNX MiniLM for Local Embedding Pipeline",
        "Hannah Tanaka",
        "Eval laptop ingest needed offline embeddings without OpenAI spend.",
        [
            "No API key required for default ingest",
            "Deterministic vectors across Windows/Linux",
            "Acceptable recall for handbook-scale corpora",
        ],
        "Default `EMBEDDING_PROVIDER=local` with Chroma ONNX MiniLM; OpenAI embeddings remain optional for production A/B.",
        "Eval comparisons must record embedding fingerprint in ingest_meta.json.",
    ),
    (
        "PagerDuty as Canonical Incident Router",
        "Liam Hale",
        "Slack @channel pages and email aliases bypassed escalation matrices.",
        [
            "Every SEV-1/2 must create a PagerDuty incident",
            "Match service IDs in on-call CSVs",
            "Preserve secondary escalation within 15 minutes",
        ],
        "PagerDuty is the only paging path; Slack notifications are informational mirrors.",
        "On-call schedules in `oncall_schedule_*.csv` map to PD services; see `engineering_oncall.md`.",
    ),
    (
        "Workday as HR System of Record",
        "Elena Takahashi",
        "Leave requests split across email, Notion, and Workday caused accrual mismatches.",
        [
            "Single leave ledger",
            "Manager SLA of 3 business days",
            "Sync on-call removals for parental leave",
        ],
        "All PTO and parental leave requests must originate in Workday; Notion trackers are non-authoritative.",
        "Canonical leave rules remain in `pto_policy.md` and `parental_leave.md`.",
    ),
    (
        "S3 Glacier Compliance Archive Retention",
        "Carlos Nair",
        "Ticket exports lived in Google Drive with uneven retention.",
        [
            "7-year retention for SOC2 evidence",
            "Immutable storage class",
            "Access logged via CloudTrail",
        ],
        "Compliance exports land in `s3://helixforge-compliance-archive/` with Object Lock GOVERNANCE mode.",
        "Does not change product data retention in `data_retention_schedules.csv`.",
    ),
    (
        "YubiKey-Only Production SSH",
        "Zoe Moreau",
        "Password and TOTP SSH still enabled on bastion hosts.",
        [
            "Phishing-resistant MFA",
            "Hardware key inventory in asset DB",
            "Emergency break-glass with dual approval",
        ],
        "Production SSH requires YubiKey WebAuthn; SMS/TOTP disabled. See `sop_production_ssh_yubikey.txt`.",
        "Contractors receive loaner YubiKeys; BYOD SSH keys are rejected at the bastion.",
    ),
    (
        "Model Checkpoint Backup Cadence",
        "Ananya Zhao",
        "Training jobs lost 11 days of progress after a single AZ disk failure.",
        [
            "RPO ≤ 4 hours for training checkpoints",
            "Cross-region copy for foundation-model runs",
            "Encrypted at rest with Vault-managed keys",
        ],
        "Hourly incremental + daily full checkpoints for foundation-model jobs. See `sop_model_checkpoint_backup.txt`.",
        "Cost center CC-2010 funds cross-region replication for foundation-model tracks only.",
    ),
    (
        "Prompt Injection Reporting Path",
        "Isla Bhat",
        "Red-team findings were filed as ordinary Jira bugs and missed security triage SLAs.",
        [
            "Dedicated ticket type",
            "24h ack for active exploits",
            "Link to model safety review",
        ],
        "All prompt-injection reports use the Security Intake form and `sop_prompt_injection_reporting.txt`.",
        "Product bugs that are not security-relevant stay in the engineering backlog.",
    ),
    (
        "CVE Patch Windows by Severity",
        "Raj Lin",
        "Critical CVEs waited on sprint planning instead of vulnerability SLAs.",
        [
            "Match `vulnerability_patching_sla_matrix.csv`",
            "Emergency change window for active exploits",
            "Evidence attached to SOC2 controls",
        ],
        "Critical with active exploit: 24h; High: 7d; Medium: 30d. Follow `sop_cve_vulnerability_patching.txt`.",
        "Exceptions require Elena Voss approval and appear on the weekly vuln board.",
    ),
    (
        "Customer War Room Channel Naming",
        "Mina Johnson",
        "Incident channels reused #general-help and lost history for postmortems.",
        [
            "Unique channel per SEV-1 customer incident",
            "Auto-archive after 30 days",
            "Export to compliance bucket",
        ],
        "War rooms are `#war-sev{N}-{customer}-{date}` created via `sop_customer_incident_war_room.txt`.",
        "Postmortems must link the war-room export path.",
    ),
    (
        "Slurm Fair-Share for Research GPUs",
        "Gabriel O'Connor",
        "Interactive Jupyter jobs starved batch training queues.",
        [
            "Protect batch queue latency",
            "Publish per-team allocations",
            "Preemption for idle interactive sessions",
        ],
        "Adopt fair-share weights from `slurm_queue_allocations.csv`; interactive sessions preempted after 45 idle minutes.",
        "See `gpu_cluster_scheduling_and_slurm_policy.md` and `sop_slurm_gpu_job_submission.txt`.",
    ),
    (
        "API Rate Limit Tiers",
        "Sarah Lindqvist",
        "Enterprise customers shared a single global RPM bucket with free-tier traffic.",
        [
            "Per-subscription TPM/RPM",
            "Overage billing hooks",
            "DDoS-safe defaults",
        ],
        "Publish tiers in `api_rate_limits_matrix.csv`; enforce at the edge with `sop_ddos_and_api_rate_limiting.txt`.",
        "Support escalations for limit increases go through Solutions Engineering + FinOps.",
    ),
    (
        "Laptop Imaging and Deprovisioning",
        "Chen Garcia",
        "Departing employees retained admin images for weeks after access revocation.",
        [
            "Same-day deprovision for involuntary exits",
            "Verified disk wipe",
            "Asset ID reconciliation",
        ],
        "Follow `sop_laptop_imaging_deprovisioning.txt` and `sop_employee_departure_and_revocation.txt` in order.",
        "People Ops closes the Workday case only after IT confirms wipe attestation.",
    ),
    (
        "GDPR Erasure Runbook Ownership",
        "Olivia Santos",
        "Right-to-be-forgotten tickets bounced between Support and Legal.",
        [
            "30-day statutory clock",
            "Clear system inventory",
            "Evidence of deletion",
        ],
        "Privacy Ops owns erasure; engineering executes `sop_gdpr_right_to_be_forgotten.txt` within published SLAs.",
        "Customer Data Deletion policy remains authoritative for product data; this ADR only clarifies ownership.",
    ),
    (
        "Cost Center Tagging on Cloud Resources",
        "Marcus Vance",
        "Untagged GPU instances attributed incorrectly to CC-0000.",
        [
            "100% tag coverage for compute",
            "Monthly FinOps report by CC",
            "Block deploy without tags",
        ],
        "Required tags: `cost_center`, `team`, `environment`. CI fails if missing.",
        "Canonical CC list is `cost_centers.csv`; billing extracts live in `cloud_billing_cost_center_report_*.csv`.",
    ),
    (
        "ADR Numbering and Supersession",
        "Devon Hale",
        "Teams published design docs without sequential ADR IDs.",
        [
            "Stable IDs",
            "Explicit supersession links",
            "ARB review window",
        ],
        "Follow `adr_process_guide.md`: sequential ADR-NNN, 10-business-day RFC, ARB Thursday slot.",
        "Informal Slack decisions are non-binding without an accepted ADR.",
    ),
    (
        "Red Team Scope Boundaries",
        "Elena Voss",
        "Adversarial tests accidentally targeted production customer tenants.",
        [
            "Isolated staging tenants only",
            "Written scope approval",
            "24h disclosure path",
        ],
        "Red-team engagements require signed scope; production customer data is out of scope. See `sop_red_team_adversarial_testing.txt`.",
        "Findings file through Security Intake, not public GitHub issues.",
    ),
    (
        "Status Page Truthfulness Rules",
        "Priya Hale",
        "Marketing delayed SEV-1 status updates past customer SLA.",
        [
            "Update within 15 minutes of SEV-1 declare",
            "No marketing edit without Incident Commander",
            "Historical incident accuracy",
        ],
        "Incident Commander owns status page copy per `status_page_rules.md`.",
        "Comms may draft, but IC publishes.",
    ),
    (
        "Subprocessor DPA Register",
        "Legal Ops",
        "New vendors onboarded without DPA rows in the catalog.",
        [
            "Every subprocessor listed",
            "Annual security review",
            "Customer-facing transparency",
        ],
        "No production data to a vendor until listed in `subprocessor_catalog.csv` with an executed DPA.",
        "See `subprocessor_security_and_dpas.md` and audit logs `subprocessor_dpa_audit_log_*.csv`.",
    ),
    (
        "Synthetic Data for Model Eval",
        "Ananya Nguyen",
        "Eval sets occasionally included real customer prompts.",
        [
            "No customer content in public eval packs",
            "Label synthetic vs production-derived",
            "License clarity",
        ],
        "Default eval corpora must be synthetic or licensed public data per `synthetic_data_generation_policy.md`.",
        "Production-derived eval requires Privacy Ops approval and residency controls.",
    ),
    (
        "Open Source Contribution Licensing",
        "Staff Counsel",
        "Engineers published internal retrieval code under conflicting licenses.",
        [
            "Apache-2.0 default for public repos",
            "Legal review for copyleft",
            "No customer data in samples",
        ],
        "Follow `open_source_contribution_policy.md`; CLA required before first public commit.",
        "Security still reviews for secret leakage via standard PR checks.",
    ),
    (
        "Conference Travel Funding Path",
        "People Ops",
        "Applied Research conference travel charged random cost centers.",
        [
            "Predictable budgets",
            "Manager + FinOps visibility",
            "Align with learning stipend",
        ],
        "Conference travel for research presentations uses CC listed in learning stipend policy; manager + stipend owner approve.",
        "Canonical stipend rules: `learning_stipend_and_conferences.md`.",
    ),
    (
        "Remote Work International Day Cap",
        "People Ops",
        "Employees worked >90 days abroad without tax review.",
        [
            "Fiscal-year day cap",
            "Workday tracking",
            "Immigration/tax review triggers",
        ],
        "Enforce the international day cap in `remote_work.md`; Workday flags at 80% of the annual limit.",
        "Exceptions need People Ops + Finance written approval.",
    ),
    (
        "Equity Refresh Band Publication",
        "Comp Committee",
        "Managers quoted outdated midpoints in offers.",
        [
            "Single compensation source",
            "Location differentials",
            "Annual refresh",
        ],
        "Offer math must use current `compensation_bands.csv` / location CSVs; verbal bands are invalid.",
        "Equity refresh policy remains in `equity_refresh_and_options_policy.md`.",
    ),
    (
        "Incident Postmortem Deadline",
        "Elena Voss",
        "SEV-1 writeups slipped past 10 business days.",
        [
            "Blameless format",
            "Action items with owners",
            "Published timeline",
        ],
        "SEV-1/2 postmortems due in 10 business days per `security_incident_postmortem_guidelines.md`.",
        "Summary rows also land in `incident_postmortem_summary_log_*.csv` for trends.",
    ),
    (
        "Customer PoC Data Isolation",
        "Solutions Engineering",
        "PoC tenants shared embedding indexes with production demos.",
        [
            "Hard isolation",
            "Auto-expiry of PoC data",
            "No training on PoC content",
        ],
        "PoC tenants are isolated and expire per `customer_poc_and_trial_governance.md`.",
        "Model training pipelines must deny PoC bucket ARMs.",
    ),
    (
        "Documentation Style for Public APIs",
        "DevRel",
        "Endpoint docs disagreed with OpenAPI and support macros.",
        [
            "OpenAPI as source of truth",
            "Examples runnable",
            "Versioned changelog",
        ],
        "Public API docs follow `documentation_standards_and_style_guide.md`; OpenAPI wins on conflicts.",
        "Support macros must link to versioned docs, not Notion drafts.",
    ),
    (
        "Carbon Metrics for GPU Jobs",
        "Sustainability WG",
        "FinOps reports omitted estimated kgCO2e for training runs.",
        [
            "Per-job estimate",
            "Monthly rollup",
            "No blocking of research",
        ],
        "Emit estimates into `sustainability_and_carbon_metrics.csv` using the green-compute policy factors.",
        "Estimates are advisory; they do not change Slurm scheduling priority in v1.",
    ),
    (
        "Interview Loop Scorecard Storage",
        "Recruiting Ops",
        "Scorecards lived in personal Drive folders.",
        [
            "Consistent rubric",
            "Retention limits",
            "Bias review sampling",
        ],
        "Store scorecards in the ATS only; rubric is `interview_evaluation_scorecard_rubric.csv`.",
        "See `interview_loop_and_hiring_standards.md` for panel composition.",
    ),
    (
        "Telemetry Metric Catalog Ownership",
        "Observability",
        "Duplicate metric names broke burn-rate alerts.",
        [
            "Unique metric registry",
            "Owner per metric family",
            "Cardinality budgets",
        ],
        "New metrics must be registered in `telemetry_metrics_catalog_*.csv` before production dashboards reference them.",
        "Unregistered metrics are dropped from the global recording rules pack.",
    ),
]


ZERO_TRUST = """# Zero Trust Network & YubiKey Mandate

**Document ID**: POL-SECURITY-ZT-001
**Effective Date**: February 1, 2026
**Owner**: Carlos Nair (Security)
**Approved By**: Elena Voss (CISO)

## Scope

Applies to all production systems, developer laptops used for production access, GitHub organization access, AWS consoles, and HashiCorp Vault. Complements `information_security.md` and `vpn_and_network_security_policy.md`; those documents remain authoritative for VPN split-tunnel and device baseline rules.

## Network posture

- Default deny for east-west traffic without service identity (see ADR on Istio mTLS).
- No standing VPN access to production CIDRs without a time-boxed ticket.
- Admin endpoints require both network path controls and hardware-backed MFA.

## Hardware security keys

All production SSH, GitHub organization SSO, AWS console, and Vault UI/CLI auth require company-issued YubiKey 5 Series (WebAuthn/FIDO2). SMS and TOTP are disabled for these surfaces. Operational steps: `sop_production_ssh_yubikey.txt`.

## Device trust

Corporate or MDM-enrolled devices only for production access. BYOD may access email and Slack per `byod_and_mobile_device_policy.md` but cannot hold production SSH certs or Vault tokens.

## Break-glass

Dual-control break-glass accounts exist for SEV-1 only. Use requires Incident Commander approval and a follow-up ticket within 24 hours. Secrets used in break-glass are rotated within 48 hours via `sop_secrets_rotation_vault.txt`.

## Exceptions

Exceptions expire after 30 days and must be listed in Slack `#policy-exceptions` with CISO acknowledgment. Silent long-lived exceptions are treated as audit findings.
"""


def write_adr(index: int, spec: tuple) -> None:
    title, owner, context, drivers, decision, consequences = spec
    num = f"{index:03d}"
    drivers_txt = "\n".join(f"- {d}" for d in drivers)
    body = f"""# ADR-{num}: {title}

**Status**: Accepted
**Date**: 2026-02-01
**Owner**: {owner}

## Context

{context}

## Decision drivers

{drivers_txt}

## Decision

{decision}

## Consequences

{consequences}
"""
    (ROOT / f"adr_{num}_architecture_decision_record.md").write_text(
        body, encoding="utf-8"
    )


def rebuild_manifest() -> None:
    from src.config import load_config
    from src.ingestion.loader import load_and_chunk

    config = load_config()
    nodes = load_and_chunk(config)
    chunks_by_file: dict[str, int] = defaultdict(int)
    for node in nodes:
        meta = node.metadata or {}
        name = str(meta.get("file_name") or meta.get("filename") or "unknown")
        chunks_by_file[name] += 1

    entries = []
    for path in sorted(
        p
        for p in ROOT.rglob("*")
        if p.is_file() and p.suffix.lower() in {".md", ".txt", ".csv", ".pdf", ".docx"}
    ):
        name = path.name
        fmt = path.suffix.lower().lstrip(".")
        entry: dict = {
            "filename": name,
            "format": fmt,
            "chunk_count": chunks_by_file.get(name, 0),
            "bytes": path.stat().st_size,
        }
        text = path.read_text(encoding="utf-8", errors="ignore")
        if fmt == "csv":
            rows = max(0, len([ln for ln in text.splitlines() if ln.strip()]) - 1)
            entry["row_count"] = rows
        else:
            entry["approx_word_count"] = len(text.split())
            if "Canonical source" in text or "Canonical procedure" in text:
                entry["role"] = "pointer"
        entries.append(entry)

    payload = {
        "corpus_dir": "data/raw_docs",
        "chunk_size": config.chunk_size,
        "chunk_overlap": config.chunk_overlap,
        "num_files": len(entries),
        "num_chunks": len(nodes),
        "num_pointer_files": sum(1 for e in entries if e.get("role") == "pointer"),
        "notes": (
            "chunk_count is measured via load_and_chunk with current CHUNK_SIZE/"
            "CHUNK_OVERLAP. Pointer files defer to canonical policies/SOPs."
        ),
        "files": entries,
    }
    (ROOT / "CORPUS_MANIFEST.json").write_text(
        json.dumps(payload, indent=2) + "\n", encoding="utf-8"
    )
    print(f"adrs={len(ADRS)}")
    print(f"num_files={payload['num_files']}")
    print(f"num_chunks={payload['num_chunks']}")
    print(f"num_pointers={payload['num_pointer_files']}")


def main() -> None:
    assert len(ADRS) == 35, len(ADRS)
    for i, spec in enumerate(ADRS, start=1):
        write_adr(i, spec)
    # Remove adr_036+ if any leftover from earlier expansion
    for path in ROOT.glob("adr_*_architecture_decision_record.md"):
        num = int(path.name.split("_")[1])
        if num > 35:
            path.unlink()
            print(f"removed {path.name}")
    (ROOT / "policy_security_zero_trust_v26.md").write_text(
        ZERO_TRUST, encoding="utf-8"
    )
    rebuild_manifest()


if __name__ == "__main__":
    main()
