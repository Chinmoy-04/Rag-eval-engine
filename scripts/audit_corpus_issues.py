"""Audit templating / conflicts in data/raw_docs (report only)."""

from __future__ import annotations

import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "data" / "raw_docs"
PHRASES = [
    "Procedural Controls & Technical Mandates",
    "Procedural Controls & Enforcement",
    "Case Study & Enforcement Example",
    "Cross-Policy Alignment",
    "s3://helixforge-compliance-archive",
]


def main() -> None:
    files = [
        p
        for p in ROOT.rglob("*")
        if p.is_file() and p.suffix.lower() in {".md", ".txt", ".csv"}
    ]
    cats: Counter[str] = Counter()
    for p in files:
        n = p.name
        if n.startswith("policy_doc_guide_"):
            cats["policy_doc_guide"] += 1
        elif n.startswith("policy_hr_") or n.startswith("policy_security_"):
            cats["policy_master_versions"] += 1
        elif n.startswith("sop_") and "_procedure_v" in n:
            cats["sop_procedure_versions"] += 1
        elif n.startswith("adr_"):
            cats["adr"] += 1
        else:
            cats["other"] += 1
    print("categories", dict(cats))

    for ph in PHRASES:
        c = sum(
            1
            for p in files
            if p.suffix in {".md", ".txt"}
            and ph in p.read_text(encoding="utf-8", errors="ignore")
        )
        print(f"phrase count [{ph}]: {c}")

    # Version families
    families: dict[str, list[Path]] = defaultdict(list)
    for p in files:
        m = re.match(r"(.+)_v(\d+)\.(md|txt)$", p.name)
        if m:
            families[m.group(1)].append(p)
    multi = {k: v for k, v in families.items() if len(v) > 1}
    print("versioned_families", len(multi))
    print(
        "files_in_multi_version_families",
        sum(len(v) for v in multi.values()),
    )
    for key in sorted(multi, key=lambda k: -len(multi[k]))[:15]:
        vers = sorted(
            int(re.search(r"_v(\d+)\.", p.name).group(1)) for p in multi[key]
        )
        print(f"  {key}: n={len(vers)} versions={vers[0]}..{vers[-1]}")


if __name__ == "__main__":
    main()
