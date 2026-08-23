# ADR-009: Workday as HR System of Record

**Status**: Accepted
**Date**: 2026-02-01
**Owner**: Elena Takahashi

## Context

Leave requests split across email, Notion, and Workday caused accrual mismatches.

## Decision drivers

- Single leave ledger
- Manager SLA of 3 business days
- Sync on-call removals for parental leave

## Decision

All PTO and parental leave requests must originate in Workday; Notion trackers are non-authoritative.

## Consequences

Canonical leave rules remain in `pto_policy.md` and `parental_leave.md`.
