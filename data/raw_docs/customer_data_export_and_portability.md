# Customer Data Export & Portability Policy
*HelixForge fictional handbook.*

Owner: Anand Patel, Head of Data Platform (anand.patel@helixforge.example / CC-1040). Approved by: Clara Dupont (Head of Legal) and Rachel Adams (Head of Support). Effective date: February 1, 2026.

## 1. Purpose & Standards
HelixForge supports open data portability and avoids vendor lock-in. Enterprise customers retain full ownership of all proprietary training datasets, uploaded document corpora, fine-tuned adapter weights, and audit logs stored in their tenant partitions.

## 2. Exportable Formats & Data Artifacts
Customers may export their assets at any time via the web console or automated API:
- **Fine-Tuning Weights**: Delivered in standard HuggingFace / PyTorch .safetensors format with complete configuration JSONs.
- **Dataset Corpora**: Exported in compressed Apache Parquet (.parquet) or JSON Lines (.jsonl) with metadata tags.
- **Audit & Inference Logs**: Exported as HMAC-signed JSON logs for SOC 2 compliance.

## 3. Generation Windows & Delivery SLAs
- **Standard Self-Service Export**: Initiated via API; archive generated within 4 business hours for datasets < 100 GB.
- **Bulk Enterprise Export (> 100 GB / Multi-Node Weights)**: Coordinated by Customer Solutions Engineering (cost_centers.csv CC-3020) and delivered via presigned S3/GCS bucket replication within 48 hours.
- **Post-Termination Export Window**: Customers have 30 calendar days following contract termination to complete data exports before automated cryptographic destruction occurs (per customer_data_deletion_and_sanitization.md).

## 4. Security & Encryption in Transit
All export archives are encrypted using customer-provided PGP public keys or AES-256 TLS 1.3 presigned download URLs with a strict 24-hour expiration TTL.

## 5. Cross-Links
- Customer data deletion and sanitization: customer_data_deletion_and_sanitization.md.
- Right to be forgotten SOP: sop_gdpr_right_to_be_forgotten.txt.
- Customer support SLAs: customer_support_slas.md.
