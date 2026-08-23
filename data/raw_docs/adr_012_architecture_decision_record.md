# ADR-012: Model Checkpoint Backup Cadence

**Status**: Accepted
**Date**: 2026-02-01
**Owner**: Ananya Zhao

## Context

Training jobs lost 11 days of progress after a single AZ disk failure.

## Decision drivers

- RPO ≤ 4 hours for training checkpoints
- Cross-region copy for foundation-model runs
- Encrypted at rest with Vault-managed keys

## Decision

Hourly incremental + daily full checkpoints for foundation-model jobs. See `sop_model_checkpoint_backup.txt`.

## Consequences

Cost center CC-2010 funds cross-region replication for foundation-model tracks only.
