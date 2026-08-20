# Incident Response Policy

An incident is any event that actually or potentially exposes Restricted data,
takes down production for more than 15 minutes, or involves a lost device with
corporate access.

Severity:
- SEV-1: production down for all customers, or confirmed Restricted data
  exposure. Page the on-call security engineer and the platform on-call
  immediately. CEO is notified within 30 minutes.
- SEV-2: partial production impact or suspected exposure. Page platform
  on-call. CISO notified within 1 hour.
- SEV-3: contained issue, no customer impact. Ticket only, handled next
  business day.

The incident commander for SEV-1/2 is the platform on-call unless Security
takes command for a confirmed data exposure. The commander runs a Zoom bridge
and writes to the #incidents Slack channel. Status updates every 30 minutes
until mitigation.

Customer notification: Customer Success drafts external messaging. Legal must
approve any message about data exposure before it is sent. Do not tweet, post
on LinkedIn, or email customers from a personal account.

After mitigation, a blameless postmortem is due in 5 business days for SEV-1
and 10 business days for SEV-2. Postmortems live in the incidents Drive folder
and are Confidential.

Employees who discover an incident and stay quiet are in violation even if
they later fix it themselves. Report first, then fix.
