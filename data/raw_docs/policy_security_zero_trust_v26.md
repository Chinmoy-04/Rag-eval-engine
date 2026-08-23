# Zero Trust Network & YubiKey Mandate

**Document ID**: POL-SECURITY-ZT-001
**Effective Date**: February 1, 2026
**Owner**: Carlos Nair (Security)
**Approved By**: Elena Voss (CISO)

## Scope

Applies to all production systems, developer laptops used for production access, GitHub organization access, AWS consoles, and HashiCorp Vault. Complements `information_security.md` and `vpn_and_network_security_policy.md`; those documents remain authoritative for VPN split-tunnel and device baseline rules.

## Network posture

- Default deny for east-west traffic without service identity (see ADR on Istio mTLS).
- No standing VPN access to production CIDRs without a time-boxed ticket.
- Admin endpoints require both network path controls and hardware-backed MFA.

## Hardware security keys

All production SSH, GitHub organization SSO, AWS console, and Vault UI/CLI auth require company-issued YubiKey 5 Series (WebAuthn/FIDO2). SMS and TOTP are disabled for these surfaces. Operational steps: `sop_production_ssh_yubikey.txt`.

## Device trust

Corporate or MDM-enrolled devices only for production access. BYOD may access email and Slack per `byod_and_mobile_device_policy.md` but cannot hold production SSH certs or Vault tokens.

## Break-glass

Dual-control break-glass accounts exist for SEV-1 only. Use requires Incident Commander approval and a follow-up ticket within 24 hours. Secrets used in break-glass are rotated within 48 hours via `sop_secrets_rotation_vault.txt`.

## Exceptions

Exceptions expire after 30 days and must be listed in Slack `#policy-exceptions` with CISO acknowledgment. Silent long-lived exceptions are treated as audit findings.
