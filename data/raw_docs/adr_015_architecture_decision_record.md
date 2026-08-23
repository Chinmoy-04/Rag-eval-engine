# ADR-015: Customer War Room Channel Naming

**Status**: Accepted
**Date**: 2026-02-01
**Owner**: Mina Johnson

## Context

Incident channels reused #general-help and lost history for postmortems.

## Decision drivers

- Unique channel per SEV-1 customer incident
- Auto-archive after 30 days
- Export to compliance bucket

## Decision

War rooms are `#war-sev{N}-{customer}-{date}` created via `sop_customer_incident_war_room.txt`.

## Consequences

Postmortems must link the war-room export path.
