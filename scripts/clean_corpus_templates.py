"""Clean HelixForge corpus: remove template spam, resolve conflicts, rebuild manifest.

Canonical originals in data/raw_docs/ win for overlapping policy facts.
"""

from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "data" / "raw_docs"

# Topics that already have a canonical source-of-truth file. Versioned masters
# and policy_doc_guide clones for these topics are deleted (not rewritten).
CANONICAL_TOPICS: dict[str, str] = {
    "pto": "pto_policy.md",
    "parental": "parental_leave.md",
    "remote": "remote_work.md",
    "travel": "travel_policy.md",
    "infosec": "information_security.md",
    "disaster_recovery": "disaster_recovery_rpo_rto.md",
    "model_gov": "model_release_governance_and_checkpoints.md",
    "pto_accrual": "pto_policy.md",
    "parental_leave": "parental_leave.md",
    "remote_work": "remote_work.md",
    "learning_stipend": "learning_stipend_and_conferences.md",
    "wellness_eap": "wellness_and_mental_health_eap.md",
    "data_classification": "data_classification.md",
    "vulnerabilities": "security_vulnerability_disclosure_and_embargo.md",
    "model_safety": "model_eval_ethics_policy.md",
}

# SOP procedure families map to original SOP filenames (without .txt).
SOP_CANONICAL: dict[str, str] = {
    "sop_customer_incident_war_room_procedure": "sop_customer_incident_war_room.txt",
    "sop_gdpr_right_to_be_forgotten_procedure": "sop_gdpr_right_to_be_forgotten.txt",
    "sop_production_ssh_yubikey_procedure": "sop_production_ssh_yubikey.txt",
    "sop_slurm_gpu_job_submission_procedure": "sop_slurm_gpu_job_submission.txt",
    "sop_vault_secret_rotation_guide_procedure": "sop_secrets_rotation_vault.txt",
    "sop_ddos_and_api_rate_limiting_procedure": "sop_ddos_and_api_rate_limiting.txt",
    "sop_laptop_imaging_deprovisioning_procedure": "sop_laptop_imaging_deprovisioning.txt",
    "sop_model_checkpoint_backup_procedure": "sop_model_checkpoint_backup.txt",
    "sop_prompt_injection_investigation_procedure": "sop_prompt_injection_reporting.txt",
    "sop_cve_vulnerability_patching_procedure": "sop_cve_vulnerability_patching.txt",
}

BOILERPLATE_SECTION_RE = re.compile(
    r"(?ms)^### (?:Procedural Controls.*|Case Study.*)\n.*?(?=^## |\Z)"
)
BOILERPLATE_BLOCK_RE = re.compile(
    r"(?ms)^#### Case Study.*?\n.*?(?=^## |\Z)"
)


def version_key(path: Path) -> tuple[str, int] | None:
    m = re.match(r"(.+)_v(\d+)\.(md|txt)$", path.name)
    if not m:
        return None
    return m.group(1), int(m.group(2))


def topic_from_family(family: str) -> str | None:
    """Map family prefix to a CANONICAL_TOPICS key if overlapping."""
    # policy_doc_guide_pto -> pto
    if family.startswith("policy_doc_guide_"):
        return family.removeprefix("policy_doc_guide_")
    if family.startswith("policy_hr_"):
        return family.removeprefix("policy_hr_")
    if family.startswith("policy_security_"):
        return family.removeprefix("policy_security_")
    return None


def strip_boilerplate(text: str) -> str:
    text = BOILERPLATE_SECTION_RE.sub("", text)
    text = BOILERPLATE_BLOCK_RE.sub("", text)
    # Drop repeated SOC2 / S3 archive paragraphs that pad every section.
    lines = []
    skip_markers = (
        "s3://helixforge-compliance-archive",
        "SOC2 Type II Trust Services Criteria",
        "Cross-Policy Alignment",
        "ticket category `",
        "ticket type `",
    )
    for line in text.splitlines():
        if any(m in line for m in skip_markers):
            continue
        lines.append(line)
    # Collapse excessive blank lines
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


def make_pointer_doc(title: str, canonical: str, family: str, version: int) -> str:
    """Short non-conflicting pointer that preserves retrieval surface without new facts."""
    return (
        f"# {title} (Archive Index v{version})\n\n"
        f"**Status**: Superseded for normative rules.\n"
        f"**Canonical policy**: `{canonical}`\n"
        f"**Archive family**: `{family}`\n\n"
        f"This file is retained only as an index pointer for historical "
        f"revision labels. Do not use it for leave banks, SLAs, accrual tables, "
        f"or approval thresholds. When answering questions, prefer the canonical "
        f"document named above.\n"
    )


def make_sop_pointer(canonical: str, family: str, version: int) -> str:
    return (
        f"SOP PROCEDURE INDEX (v{version})\n"
        f"Canonical procedure: {canonical}\n"
        f"Family: {family}\n\n"
        f"This revision index does not redefine steps. Follow the canonical "
        f"SOP file for SSH, Vault, GDPR, war-room, Slurm, CVE, and related "
        f"operational procedures.\n"
    )


def delete_path(path: Path, deleted: list[str]) -> None:
    path.unlink()
    deleted.append(path.name)


def clean_corpus() -> dict:
    deleted: list[str] = []
    rewritten: list[str] = []
    kept_latest: list[str] = []

    # 1) Delete every policy_doc_guide_* (pure template spam).
    for path in sorted(ROOT.glob("policy_doc_guide_*.md")):
        delete_path(path, deleted)

    # 2) Group remaining versioned md/txt families.
    families: dict[str, list[Path]] = defaultdict(list)
    for path in ROOT.iterdir():
        if not path.is_file():
            continue
        key = version_key(path)
        if key is None:
            continue
        family, _ver = key
        families[family].append(path)

    for family, paths in sorted(families.items()):
        paths_sorted = sorted(
            paths, key=lambda p: version_key(p)[1]  # type: ignore[index]
        )
        latest = paths_sorted[-1]
        older = paths_sorted[:-1]
        for path in older:
            delete_path(path, deleted)

        topic = topic_from_family(family)
        ver = version_key(latest)[1]  # type: ignore[index]

        # Conflicting HR/security masters → short pointers to canonical docs.
        if topic is not None and topic in CANONICAL_TOPICS:
            canonical = CANONICAL_TOPICS[topic]
            title = latest.stem.replace("_", " ").title()
            latest.write_text(
                make_pointer_doc(title, canonical, family, ver),
                encoding="utf-8",
            )
            rewritten.append(latest.name)
            kept_latest.append(latest.name)
            continue

        # Versioned SOP procedures → pointer to original SOP.
        if family in SOP_CANONICAL:
            canonical = SOP_CANONICAL[family]
            latest.write_text(
                make_sop_pointer(canonical, family, ver),
                encoding="utf-8",
            )
            rewritten.append(latest.name)
            kept_latest.append(latest.name)
            continue

        # Other versioned docs (e.g. zero_trust, soc2_framework without exact
        # canonical): keep latest, strip boilerplate only.
        if latest.suffix.lower() in {".md", ".txt"}:
            text = latest.read_text(encoding="utf-8", errors="ignore")
            cleaned = strip_boilerplate(text)
            if cleaned != text:
                latest.write_text(cleaned, encoding="utf-8")
                rewritten.append(latest.name)
            kept_latest.append(latest.name)
        else:
            kept_latest.append(latest.name)

    return {
        "deleted": deleted,
        "rewritten": rewritten,
        "kept_latest": kept_latest,
    }


def rebuild_manifest() -> dict:
    """Rebuild CORPUS_MANIFEST.json with accurate chunk estimates."""
    from src.config import load_config
    from src.ingestion.loader import load_and_chunk

    config = load_config()
    nodes = load_and_chunk(config)

    chunks_by_file: dict[str, int] = defaultdict(int)
    for node in nodes:
        meta = node.metadata or {}
        name = str(meta.get("file_name") or meta.get("filename") or "unknown")
        chunks_by_file[name] += 1

    # Original seed corpus (~86 files) — treat as baseline; mark expansion.
    # Heuristic: files listed in CORPUS_MANIFEST before, or not in a small
    # known-original set. Simpler: include every supported file with stats.
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
        entries.append(entry)

    payload = {
        "corpus_dir": "data/raw_docs",
        "chunk_size": config.chunk_size,
        "chunk_overlap": config.chunk_overlap,
        "num_files": len(entries),
        "num_chunks": len(nodes),
        "files": entries,
    }
    out = ROOT / "CORPUS_MANIFEST.json"
    out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return {
        "num_files": len(entries),
        "num_chunks": len(nodes),
        "manifest": str(out),
    }


def main() -> None:
    summary = clean_corpus()
    print(f"deleted={len(summary['deleted'])}")
    print(f"rewritten={len(summary['rewritten'])}")
    print(f"kept_latest={len(summary['kept_latest'])}")
    man = rebuild_manifest()
    print(f"manifest_files={man['num_files']}")
    print(f"manifest_chunks={man['num_chunks']}")
    print(f"manifest_path={man['manifest']}")


if __name__ == "__main__":
    main()
