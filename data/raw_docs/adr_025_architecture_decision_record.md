# ADR-025: Synthetic Data for Model Eval

**Status**: Accepted
**Date**: 2026-02-01
**Owner**: Ananya Nguyen

## Context

Eval sets occasionally included real customer prompts.

## Decision drivers

- No customer content in public eval packs
- Label synthetic vs production-derived
- License clarity

## Decision

Default eval corpora must be synthetic or licensed public data per `synthetic_data_generation_policy.md`.

## Consequences

Production-derived eval requires Privacy Ops approval and residency controls.
