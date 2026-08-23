# ADR-017: API Rate Limit Tiers

**Status**: Accepted
**Date**: 2026-02-01
**Owner**: Sarah Lindqvist

## Context

Enterprise customers shared a single global RPM bucket with free-tier traffic.

## Decision drivers

- Per-subscription TPM/RPM
- Overage billing hooks
- DDoS-safe defaults

## Decision

Publish tiers in `api_rate_limits_matrix.csv`; enforce at the edge with `sop_ddos_and_api_rate_limiting.txt`.

## Consequences

Support escalations for limit increases go through Solutions Engineering + FinOps.
