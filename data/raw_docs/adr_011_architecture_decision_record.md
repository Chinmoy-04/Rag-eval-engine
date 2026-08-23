# ADR-011: YubiKey-Only Production SSH

**Status**: Accepted
**Date**: 2026-02-01
**Owner**: Zoe Moreau

## Context

Password and TOTP SSH still enabled on bastion hosts.

## Decision drivers

- Phishing-resistant MFA
- Hardware key inventory in asset DB
- Emergency break-glass with dual approval

## Decision

Production SSH requires YubiKey WebAuthn; SMS/TOTP disabled. See `sop_production_ssh_yubikey.txt`.

## Consequences

Contractors receive loaner YubiKeys; BYOD SSH keys are rejected at the bastion.
