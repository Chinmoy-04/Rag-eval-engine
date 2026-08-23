# ADR-004: HashiCorp Vault as Sole Secrets Backend

**Status**: Accepted
**Date**: 2026-02-01
**Owner**: Elena Voss

## Context

AWS Secrets Manager, GitHub Actions secrets, and Vault coexisted; rotation audits failed SOC2 sampling.

## Decision drivers

- Single source of truth for production secrets
- 90-day automated rotation for API keys
- Break-glass human path with dual control

## Decision

Vault is mandatory for production; AWS Secrets Manager allowed only for AWS-native service-linked roles.

## Consequences

See `sop_secrets_rotation_vault.txt`. GitHub Actions must fetch runtime secrets from Vault via OIDC.
