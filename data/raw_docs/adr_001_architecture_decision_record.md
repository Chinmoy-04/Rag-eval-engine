# ADR-001: Istio Service Mesh Mutual TLS Enforcement

**Status**: Accepted
**Date**: 2026-02-01
**Owner**: Mei-Ling Johnson

## Context

East-west traffic between inference pods was still plaintext inside the VPC. A SEV-2 review found 14 services without mTLS.

## Decision drivers

- Enforce mTLS for all in-cluster service-to-service calls
- Keep P99 sidecar overhead under 3ms
- Compatible with existing gRPC model-serving paths

## Decision

Adopt Istio STRICT mTLS with PeerAuthentication defaults; allow PERMISSIVE only during a 30-day migration window.

## Consequences

All new services inherit STRICT mode. Break-glass PERMISSIVE requires CISO approval logged in #security-exceptions.
