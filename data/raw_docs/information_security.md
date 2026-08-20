# Information Security Policy

HelixForge classifies systems as production, staging, and corporate. Production
access requires a hardware security key (YubiKey) and a just-in-time access
grant that expires in 8 hours. Standing production SSH is forbidden.

Passwords, where still used, must be at least 16 characters and stored only in
1Password. SMS 2FA is not accepted for production or email. GitHub, Google
Workspace, and AWS SSO require hardware keys.

Laptops must run the company MDM profile, full-disk encryption, and automatic
screen lock at 5 minutes. Jailbroken or unmanaged devices may not access
email, Slack, or code.

Customer data may not be copied to personal machines, USB drives, or personal
cloud accounts. Using a personal ChatGPT, Claude, or Gemini account with
customer data is a security incident. Internal AI tools are covered by the AI
Usage Policy.

Phishing: report suspected phishing to security@helixforge.example and via the
#sec-reports Slack channel. Do not forward the raw message to teammates.

Vendors that process customer data need a signed DPA and a Security review.
Employees may not sign vendor security questionnaires; Security does.

Lost devices must be reported to Security within 1 hour of noticing the loss.
Security will remotely lock the device. Delay beyond 1 hour is a policy
violation even if the device is later found.

This policy is owned by CISO Elena Voss. Exceptions require a written ticket
and expire after 90 days unless renewed.
