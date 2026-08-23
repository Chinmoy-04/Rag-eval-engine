# ADR-006: Feature Flag Platform Standardization

**Status**: Accepted
**Date**: 2026-02-01
**Owner**: Xavier Thorne

## Context

Teams used LaunchDarkly, custom Redis flags, and config maps with inconsistent kill-switch semantics.

## Decision drivers

- Global kill switch under 60 seconds
- Audit trail of flag changes
- Environment promotion gates

## Decision

Adopt LaunchDarkly for product flags; forbid ad-hoc Redis boolean flags in production after 2026-06-01.

## Consequences

See `sop_feature_flag_lifecycle.txt` for promotion and rollback.
