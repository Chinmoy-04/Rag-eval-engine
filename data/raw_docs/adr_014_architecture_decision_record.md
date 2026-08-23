# ADR-014: CVE Patch Windows by Severity

**Status**: Accepted
**Date**: 2026-02-01
**Owner**: Raj Lin

## Context

Critical CVEs waited on sprint planning instead of vulnerability SLAs.

## Decision drivers

- Match `vulnerability_patching_sla_matrix.csv`
- Emergency change window for active exploits
- Evidence attached to SOC2 controls

## Decision

Critical with active exploit: 24h; High: 7d; Medium: 30d. Follow `sop_cve_vulnerability_patching.txt`.

## Consequences

Exceptions require Elena Voss approval and appear on the weekly vuln board.
