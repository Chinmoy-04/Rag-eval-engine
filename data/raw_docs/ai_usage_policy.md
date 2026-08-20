# AI Usage Policy

HelixForge employees may use approved AI tools for coding, writing, and
internal research. Approved tools: GitHub Copilot on company GitHub, the
internal HelixForge RAG assistant, and the company-managed ChatGPT Enterprise
workspace.

Unapproved tools (personal ChatGPT, Claude.ai, Gemini, public Hugging Face
Spaces, consumer Copilot) may not receive Confidential or Restricted data.
Internal handbook text (Internal classification) may be pasted into unapproved
tools only after customer names and credentials are removed.

Customer data, production logs, and secrets are never allowed in any AI tool
except the internal RAG assistant running in the production VPC. The internal
assistant logs prompts for 14 days for abuse review; do not paste secrets
there either.

Model outputs are not a source of policy. If the assistant disagrees with this
handbook, the handbook wins. Employees remain responsible for code and emails
they send, including AI-drafted text.

Training: HelixForge does not use customer prompts to train third-party
foundation models. Evaluation datasets derived from customer data must be
tokenized per the Data Classification policy.

Violations of this policy are security incidents when Restricted data is
involved, and conduct issues otherwise.
