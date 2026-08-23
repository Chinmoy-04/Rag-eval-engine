"""Pass 2: convert remaining conflicting masters to pointers; strip ADR boilerplate."""

from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "data" / "raw_docs"

# Substring match: if family contains key → canonical file
TOPIC_MATCHES: list[tuple[str, str]] = [
    ("pto", "pto_policy.md"),
    ("parental", "parental_leave.md"),
    ("remote", "remote_work.md"),
    ("travel", "travel_policy.md"),
    ("infosec", "information_security.md"),
    ("disaster_recovery", "disaster_recovery_rpo_rto.md"),
    ("model_gov", "model_release_governance_and_checkpoints.md"),
    ("learning_stipend", "learning_stipend_and_conferences.md"),
    ("wellness", "wellness_and_mental_health_eap.md"),
    ("data_classification", "data_classification.md"),
    ("vulnerabilit", "security_vulnerability_disclosure_and_embargo.md"),
    ("model_safety", "model_eval_ethics_policy.md"),
    ("soc2", "soc2_compliance_controls.csv"),
]

SOP_MATCHES: list[tuple[str, str]] = [
    ("customer_incident_war_room", "sop_customer_incident_war_room.txt"),
    ("gdpr_right_to_be_forgotten", "sop_gdpr_right_to_be_forgotten.txt"),
    ("production_ssh_yubikey", "sop_production_ssh_yubikey.txt"),
    ("slurm_gpu_job_submission", "sop_slurm_gpu_job_submission.txt"),
    ("vault_secret_rotation", "sop_secrets_rotation_vault.txt"),
    ("ddos_and_api_rate_limiting", "sop_ddos_and_api_rate_limiting.txt"),
    ("laptop_imaging_deprovisioning", "sop_laptop_imaging_deprovisioning.txt"),
    ("model_checkpoint_backup", "sop_model_checkpoint_backup.txt"),
    ("prompt_injection", "sop_prompt_injection_reporting.txt"),
    ("cve_vulnerability_patching", "sop_cve_vulnerability_patching.txt"),
]

BOILERPLATE_SECTION_RE = re.compile(
    r"(?ms)^### (?:Procedural Controls.*|Case Study.*)\n.*?(?=^## |\Z)"
)


def resolve_canonical(name: str, matches: list[tuple[str, str]]) -> str | None:
    lower = name.lower()
    for needle, canonical in matches:
        if needle in lower:
            return canonical
    return None


def pointer_md(title: str, canonical: str, name: str) -> str:
    return (
        f"# {title}\n\n"
        f"**Status**: Non-normative index pointer.\n"
        f"**Canonical source**: `{canonical}`\n"
        f"**This file**: `{name}`\n\n"
        f"Do not use this document for accrual tables, leave banks, SLAs, "
        f"approval thresholds, or security controls. Prefer the canonical "
        f"source named above when answering questions.\n"
    )


def pointer_sop(canonical: str, name: str) -> str:
    return (
        f"SOP PROCEDURE INDEX\n"
        f"Canonical procedure: {canonical}\n"
        f"This file: {name}\n\n"
        f"This revision index does not redefine operational steps. Follow the "
        f"canonical SOP for the authoritative procedure.\n"
    )


def strip_adr(text: str) -> str:
    text = BOILERPLATE_SECTION_RE.sub("", text)
    # Drop generic executive summary fluff that is identical across ADRs.
    text = re.sub(
        r"(?ms)^## Executive Summary\n\nThis document establishes standard "
        r"operating policies.*?(?=^## )",
        "",
        text,
    )
    lines = []
    for line in text.splitlines():
        if "ticket type `" in line or "policy-exceptions" in line:
            continue
        lines.append(line)
    out: list[str] = []
    blank = 0
    for line in lines:
        if not line.strip():
            blank += 1
            if blank <= 1:
                out.append(line)
        else:
            blank = 0
            out.append(line)
    return "\n".join(out).strip() + "\n"


def main() -> None:
    rewritten: list[str] = []

    for path in sorted(ROOT.glob("policy_hr_*.md")) + sorted(
        ROOT.glob("policy_security_*.md")
    ):
        canonical = resolve_canonical(path.name, TOPIC_MATCHES)
        if canonical is None:
            # Keep unique topics (e.g. zero_trust) but strip boilerplate.
            text = path.read_text(encoding="utf-8", errors="ignore")
            cleaned = BOILERPLATE_SECTION_RE.sub("", text)
            cleaned = re.sub(
                r"(?ms)^## Executive Summary\n\nThis document establishes "
                r"standard operating policies.*?(?=^## )",
                "",
                cleaned,
            )
            if cleaned != text:
                path.write_text(cleaned.strip() + "\n", encoding="utf-8")
                rewritten.append(path.name)
            continue
        title = path.stem.replace("_", " ").title()
        path.write_text(
            pointer_md(title, canonical, path.name), encoding="utf-8"
        )
        rewritten.append(path.name)

    for path in sorted(ROOT.glob("sop_*_procedure_v*.txt")):
        canonical = resolve_canonical(path.name, SOP_MATCHES)
        if canonical is None:
            continue
        path.write_text(pointer_sop(canonical, path.name), encoding="utf-8")
        rewritten.append(path.name)

    for path in sorted(ROOT.glob("adr_*.md")):
        if path.name == "adr_process_guide.md":
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        cleaned = strip_adr(text)
        if cleaned != text:
            path.write_text(cleaned, encoding="utf-8")
            rewritten.append(path.name)

    # Rebuild accurate manifest
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
        if fmt == "csv":
            raw = path.read_text(encoding="utf-8-sig", errors="ignore")
            rows = max(0, len([ln for ln in raw.splitlines() if ln.strip()]) - 1)
            entry["row_count"] = rows
        else:
            text = path.read_text(encoding="utf-8", errors="ignore")
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
        "files": entries,
    }
    (ROOT / "CORPUS_MANIFEST.json").write_text(
        json.dumps(payload, indent=2) + "\n", encoding="utf-8"
    )
    print(f"rewritten={len(rewritten)}")
    print(f"num_files={payload['num_files']}")
    print(f"num_chunks={payload['num_chunks']}")
    print(f"num_pointers={payload['num_pointer_files']}")


if __name__ == "__main__":
    main()
