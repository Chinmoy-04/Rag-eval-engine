# ADR-031: Customer PoC Data Isolation

**Status**: Accepted
**Date**: 2026-02-01
**Owner**: Solutions Engineering

## Context

PoC tenants shared embedding indexes with production demos.

## Decision drivers

- Hard isolation
- Auto-expiry of PoC data
- No training on PoC content

## Decision

PoC tenants are isolated and expire per `customer_poc_and_trial_governance.md`.

## Consequences

Model training pipelines must deny PoC bucket ARMs.
