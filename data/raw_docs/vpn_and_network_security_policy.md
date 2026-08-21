# Zero-Trust VPN & Network Security Policy
*HelixForge fictional handbook.*

Owner: Elena Voss, CISO (elena.voss@helixforge.example / CC-1050). Operational Lead: Chloe Bennett, Head of Cloud Infrastructure (chloe.bennett@helixforge.example / CC-1030). Effective date: February 1, 2026.

## 1. Zero-Trust Network Architecture
HelixForge enforces a zero-trust network access (ZTNA) model across all corporate endpoints, distributed cloud VPCs, and bare-metal GPU clusters. Traditional perimeter-based VPNs are replaced by cryptographic identity-aware proxies powered by Cloudflare Access and internal WireGuard mesh routers.

## 2. Regional Gateways and Routing Topology
HelixForge maintains three primary ZTNA ingress gateways:
- **US Gateway**: pn.austin.helixforge.example (Austin HQ Data Center / AWS us-east-1).
- **EU Gateway**: pn.dublin.helixforge.example (AWS eu-west-1).
- **APAC Gateway**: pn.singapore.helixforge.example (AWS p-southeast-1).

All client traffic to internal development environments, staging clusters, and database bastions must traverse the nearest regional gateway.

## 3. Split-Tunneling and DNS Encryption
- **Split-Tunneling**: Standard corporate laptops utilize split-tunneling. Only traffic destined for *.internal.helixforge.example, internal RFC1918 subnets (10.0.0.0/8, 172.16.0.0/12), and managed cloud endpoints is routed through the ZTNA tunnel.
- **DNS over HTTPS (DoH)**: All managed endpoints enforce encrypted DNS resolving through Cloudflare 1.1.1.1 for Teams, blocking phishing domains and malicious command-and-control IPs.
- **Production Isolation**: Connecting to the production Kubernetes control plane or SSH bastion hops requires stepping through an additional hardware YubiKey challenge and active Jira ticket (see sop_production_ssh_yubikey.txt).

## 4. Connection Lifetimes and Session Expiry
- Standard ZTNA user sessions expire every **24 hours**, requiring Okta SSO re-authentication with biometric MFA.
- Production bastion elevation remains capped at **8 hours** maximum (see sop_production_ssh_yubikey.txt).
- Inactive VPN sessions are disconnected after **60 minutes** of idle traffic.

## 5. Cross-Links
- Production SSH elevation: sop_production_ssh_yubikey.txt.
- Laptop imaging and MDM network client setup: sop_laptop_imaging_deprovisioning.txt.
- Multi-region infrastructure and data residency: data_residency_matrix.csv.
