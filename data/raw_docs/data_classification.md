# Data Classification Policy

HelixForge has four data classes: Public, Internal, Confidential, and
Restricted.

Public: marketing website copy, published papers, job listings. May live
anywhere.

Internal: org charts, non-sensitive handbook pages, sprint boards without
customer names. May live in Google Drive, Notion, and Slack. Do not post
Internal data on public GitHub.

Confidential: unreleased product plans, salaries, customer names in CRM,
architecture docs. Must live in Google Drive with link-sharing set to
restricted, or in Notion with a named-person ACL. Confidential data in Slack
is allowed only in private channels. Confidential data is not allowed in
personal AI accounts.

Restricted: production customer content, authentication secrets, government
ID documents, health information collected for benefits. Restricted data may
only live in approved systems: the production datastore, Workday, Greenhouse
(candidates), and the secrets manager. Restricted data must not be pasted into
tickets, Slack, or eval datasets without tokenization.

RAG evaluation sets built from customer data require tokenization of names,
emails, and account IDs before they leave production. Synthetic HelixForge
handbook data (this corpus) is Internal, not Restricted.

When in doubt, classify one level higher and ask Security. Mis-classifying
Restricted data as Confidential is an incident.
