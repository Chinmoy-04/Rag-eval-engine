# ADR-024: Subprocessor DPA Register

**Status**: Accepted
**Date**: 2026-02-01
**Owner**: Legal Ops

## Context

New vendors onboarded without DPA rows in the catalog.

## Decision drivers

- Every subprocessor listed
- Annual security review
- Customer-facing transparency

## Decision

No production data to a vendor until listed in `subprocessor_catalog.csv` with an executed DPA.

## Consequences

See `subprocessor_security_and_dpas.md` and audit logs `subprocessor_dpa_audit_log_*.csv`.
