# ADR-008: PagerDuty as Canonical Incident Router

**Status**: Accepted
**Date**: 2026-02-01
**Owner**: Liam Hale

## Context

Slack @channel pages and email aliases bypassed escalation matrices.

## Decision drivers

- Every SEV-1/2 must create a PagerDuty incident
- Match service IDs in on-call CSVs
- Preserve secondary escalation within 15 minutes

## Decision

PagerDuty is the only paging path; Slack notifications are informational mirrors.

## Consequences

On-call schedules in `oncall_schedule_*.csv` map to PD services; see `engineering_oncall.md`.
