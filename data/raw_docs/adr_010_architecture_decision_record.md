# ADR-010: S3 Glacier Compliance Archive Retention

**Status**: Accepted
**Date**: 2026-02-01
**Owner**: Carlos Nair

## Context

Ticket exports lived in Google Drive with uneven retention.

## Decision drivers

- 7-year retention for SOC2 evidence
- Immutable storage class
- Access logged via CloudTrail

## Decision

Compliance exports land in `s3://helixforge-compliance-archive/` with Object Lock GOVERNANCE mode.

## Consequences

Does not change product data retention in `data_retention_schedules.csv`.
