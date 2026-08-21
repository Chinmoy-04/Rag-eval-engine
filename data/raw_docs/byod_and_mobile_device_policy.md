# Bring Your Own Device (BYOD) & Mobile Security Policy
*HelixForge fictional handbook.*

Owner: Elena Voss, CISO (elena.voss@helixforge.example / CC-1050). Operational Lead: Nathan Brooks, Workplace IT Lead (nathan.brooks@helixforge.example / CC-4050). Effective date: February 1, 2026.

## 1. Scope and Core Principle
This policy defines security rules for accessing corporate resources (email, calendar, Slack, 1Password) from personal mobile devices (smartphones and tablets) for all ~420 FTEs and eligible contractors. Personal laptops/desktops are **strictly barred** from connecting to HelixForge internal networks or source code repositories.

## 2. Permitted Services & Data Classification on Mobile
- **Permitted Mobile Access**: Google Workspace (Email/Calendar), Slack Enterprise Grid, Zoom, and Okta Verify / 1Password.
- **Strictly Prohibited on Personal Devices**:
  - Direct production SSH bastions or terminal sessions (see sop_production_ssh_yubikey.txt).
  - Downloading or caching raw customer datasets, model checkpoint weights, or Restricted classified assets.
  - Exporting customer support ticket attachments to personal device storage.

## 3. Mobile Device Management (MDM) Enrollment
Any mobile device accessing HelixForge corporate services must be enrolled in **Microsoft Intune Company Portal / Jamf Mobile**:
1. **Passcode Requirement**: Minimum 6-digit numeric PIN or complex alphanumeric password. Biometric unlock (FaceID / TouchID) is permitted.
2. **OS Patching**: Devices must run supported OS versions (iOS within latest 2 major releases; Android within latest 2 major releases with security patch level < 60 days old).
3. **Jailbreak / Root Detection**: Jailbroken iOS or rooted Android devices are blocked immediately from authenticating via Okta.
4. **Inactivity Lock**: Screen auto-lock enforced after **5 minutes** of inactivity.

## 4. Remote Selective Wipe & Lost Device SLAs
- If a mobile device is lost, stolen, or compromised, the employee must notify security-incident@helixforge.example within **2 hours**.
- Workplace IT executes an **Enterprise Selective Wipe** via Intune within 15 minutes of report receipt. This command purges all corporate email, Slack cache, and SSO tokens while leaving personal photos and data intact.
- Upon employee departure (FTE offboarding), the selective wipe is triggered automatically at **17:30 local time** on the final working day.

## 5. Cross-Links
- Laptop provisioning and offboarding wipes: sop_laptop_imaging_deprovisioning.txt.
- Data classification boundaries: vendor_security.md and data_residency_matrix.csv.
- Software catalog and mobile clients: software_catalog.csv.
