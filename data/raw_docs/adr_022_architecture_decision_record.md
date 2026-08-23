# ADR-022: Red Team Scope Boundaries

**Status**: Accepted
**Date**: 2026-02-01
**Owner**: Elena Voss

## Context

Adversarial tests accidentally targeted production customer tenants.

## Decision drivers

- Isolated staging tenants only
- Written scope approval
- 24h disclosure path

## Decision

Red-team engagements require signed scope; production customer data is out of scope. See `sop_red_team_adversarial_testing.txt`.

## Consequences

Findings file through Security Intake, not public GitHub issues.
