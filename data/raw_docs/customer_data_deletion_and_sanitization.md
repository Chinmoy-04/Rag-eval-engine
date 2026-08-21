# Customer Data Deletion & Cryptographic Sanitization Policy
*HelixForge fictional handbook.*

Owner: Clara Dupont, Head of Legal, Regulatory & Compliance (clara.dupont@helixforge.example / CC-4030). Technical Lead: Anand Patel, Head of Data Platform (anand.patel@helixforge.example / CC-1040). Effective date: February 1, 2026.

## 1. Scope & Deletion Commitment
HelixForge is committed to strict data minimization, privacy compliance (GDPR / Singapore PDPA), and secure lifecycle management of enterprise customer assets. This policy governs data deletion triggers, cryptographic wiping protocols, and statutory compliance certification upon contract expiration or tenant offboarding.

## 2. Deletion Triggers and Statutory Timelines
1. **Contract Termination**: Upon expiration or termination of a customer agreement, all customer-owned datasets, uploaded prompts, fine-tuning checkpoints, and embedding indices enter a 30-day grace period for customer export.
2. **Statutory 30-Day Purge SLA**: Exactly at **T+30 calendar days** post-termination, automated cryptographic purge routines execute across all production and backup data stores.
3. **Customer-Initiated Erasure (DSR / RTBF)**: Data Subject Requests submitted via privacy@helixforge.example must be executed within **30 calendar days** per sop_gdpr_right_to_be_forgotten.txt.

## 3. Technical Sanitization Standards
- **Relational & Document Stores**: Hard deletion of customer UUID records across PostgreSQL and DynamoDB metadata stores, followed by table compaction.
- **Vector Embeddings**: Deletion tombstones submitted to Pinecone / Milvus vector clusters, followed by index re-indexing within 48 hours.
- **Object Storage & Model Checkpoints**: Cryptographic erasure (crypto-shredding) of KMS encryption keys associated with customer S3/GCS buckets in HashiCorp Vault (see sop_secrets_rotation_vault.txt). Destroying the wrapping key renders all underlying tensor shards mathematically unrecoverable.
- **NIST SP 800-88 Compliance**: Physical storage decommissioned from Austin HQ lab follows NIST SP 800-88 Rev 1 Purge standards.

## 4. Certificate of Destruction
Within **5 business days** of purge completion, Legal and Data Platform issue a cryptographically signed Certificate of Destruction containing SHA-256 validation hashes, delivered to the customer's technical contact.

## 5. Cross-Links
- Right to be Forgotten SOP: sop_gdpr_right_to_be_forgotten.txt.
- Model checkpoint archiving and lifecycle: sop_model_checkpoint_backup.txt.
- Data retention schedules: data_retention_schedules.csv.
- Data residency and cloud boundaries: data_residency_matrix.csv.
