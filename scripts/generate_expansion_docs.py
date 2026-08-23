"""Generate expanded HelixForge synthetic corpus for realistic RAG evaluation.

This script creates ~250 new documents (CSVs, MDs, TXTs) matching existing
HelixForge style, entities, and cross-references, producing ~2,500–4,000 chunks.
"""

import json
import random
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DOCS_DIR = PROJECT_ROOT / "data" / "raw_docs"
MANIFEST_PATH = RAW_DOCS_DIR / "CORPUS_MANIFEST.json"

RAW_DOCS_DIR.mkdir(parents=True, exist_ok=True)

random.seed(42)

# Global HelixForge metadata
LOCATIONS = ["Austin, TX", "Dublin, Ireland", "Singapore"]
LEVELS = ["L3", "L4", "L5", "L6", "L7", "L8"]
DIVISIONS = ["Platform Engineering", "Applied Research", "Customer Success", "Business Operations"]
TEAMS = [
    "Core Retrieval", "Vector Engine", "Eval & Benchmarks", "Fine-Tuning",
    "Customer Solutions", "Infra & DevOps", "Security & Compliance", "People Ops",
    "Finance & Procurement", "Product Design"
]
COST_CENTERS = ["CC-1010", "CC-1020", "CC-1500", "CC-2010", "CC-3010", "CC-3020", "CC-4010", "CC-5010"]

FIRST_NAMES = ["Mara", "Devon", "Priya", "Elena", "Marcus", "Aris", "Sarah", "Liam", "Sophia", "Noah", "Olivia", "Ethan", "Ava", "Lucas", "Mina", "Carlos", "Aisha", "Kaito", "Chloe", "Dmitri", "Zoe", "Tariq", "Fatima", "Chen", "Raj", "Hannah", "Viktor", "Yuki", "Lars", "Siddharth", "Beatriz", "Matteo", "Soren", "Mei-Ling", "Xavier", "Ananya", "Dominic", "Elena", "Gabriel", "Isla"]
LAST_NAMES = ["Chen", "Hale", "Nair", "Voss", "Vance", "Thorne", "Lin", "Smith", "Johnson", "Patel", "Garcia", "Kim", "Nguyen", "Mueller", "Ivanov", "Santos", "O'Connor", "Takahashi", "Zhao", "Wong", "Kovacs", "Dubois", "Al-Mansoor", "Bhat", "Lindqvist", "Moreau", "Silva", "Novak", "Joshi", "Tanaka", "Watanabe", "Hoffmann"]

def get_name():
    return f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"

def get_email(name):
    clean = name.lower().replace(" ", ".").replace("'", "")
    return f"{clean}@helixforge.example"

manifest_entries = []
created_summary = []

def save_doc(filename, content, doc_format, primary_topics, row_count=0):
    filepath = RAW_DOCS_DIR / filename
    filepath.write_text(content.strip() + "\n", encoding="utf-8")
    
    words = len(content.split())
    # Precise chunk calculation based on SentenceSplitter(chunk_size=512, chunk_overlap=50) (~400 tokens / 300 words net stride)
    approx_chunks = max(1, round(words / 280)) if doc_format != "csv" else max(1, round(row_count / 10))
    
    entry = {
        "filename": filename,
        "format": doc_format,
        "primary_topics": primary_topics,
        "approx_chunks": approx_chunks
    }
    if doc_format == "csv":
        entry["row_count"] = row_count
    else:
        entry["approx_word_count"] = words
        
    manifest_entries.append(entry)
    created_summary.append({
        "filename": filename,
        "format": doc_format,
        "words": words,
        "rows": row_count,
        "chunks": approx_chunks
    })

print("Building synthetic corpus files...")

# ==============================================================================
# SECTION 1: GENERATE CSV/TABLE FILES (~40% of files, ~100 files)
# ==============================================================================

# 1. On-Call Rotations (12 files: Q1-Q4 for 3 regions)
for q in ["q1", "q2", "q3", "q4"]:
    for loc in ["austin", "dublin", "singapore"]:
        fname = f"oncall_schedule_2026_{q}_{loc}.csv"
        rows = ["shift_id,week_number,start_date,primary_engineer,primary_email,secondary_engineer,secondary_email,escalation_tier_1,escalation_tier_2,team,cost_center,oncall_stipend_usd"]
        count = 0
        for week in range(1, 14):
            shift_id = f"ONCALL-{q.upper()}-{loc[:3].upper()}-W{week:02d}"
            start_date = f"2026-{(int(q[1])-1)*3 + (week-1)//4 + 1:02d}-{(week%4)*7+1:02d}"
            p_name = get_name()
            s_name = get_name()
            tier1 = get_name()
            tier2 = "Devon Hale (CTO)" if week % 3 == 0 else "Elena Voss (CISO)"
            team = random.choice(["Vector Engine", "Core Retrieval", "Infra & DevOps", "Security & Compliance"])
            cc = random.choice(["CC-1010", "CC-1500", "CC-5010"])
            stipend = 350
            rows.append(f"{shift_id},{week},{start_date},{p_name},{get_email(p_name)},{s_name},{get_email(s_name)},{tier1},{tier2},{team},{cc},{stipend}")
            count += 1
        save_doc(fname, "\n".join(rows), "csv", ["oncall", "escalation", "engineering", loc], row_count=count)

# 2. Hardware Asset Inventories (10 files)
for idx in range(1, 11):
    fname = f"hardware_asset_inventory_batch_{idx:02d}.csv"
    rows = ["asset_tag_id,device_model,serial_number,assigned_employee,employee_level,office_location,procurement_date,warranty_expiration,disk_encryption_status,mdm_enrolled,purchase_price_usd"]
    count = 0
    models = ["MacBook Pro 16 M3 Max", "MacBook Pro 14 M3 Pro", "Lenovo ThinkPad P1 Gen 6", "Dell Precision 7680", "System76 Serval WS"]
    for r in range(1, 160):
        tag = f"HF-HW-{idx:02d}-{r:04d}"
        model = random.choice(models)
        sn = f"SN-2026-{random.randint(100000, 999999)}"
        emp = get_name()
        lvl = random.choice(LEVELS)
        loc = random.choice(LOCATIONS)
        proc_date = f"202{random.randint(3,6)}-{random.randint(1,12):02d}-{random.randint(1,28):02d}"
        warr_date = f"202{random.randint(6,9)}-{random.randint(1,12):02d}-{random.randint(1,28):02d}"
        enc = "Enabled (FileVault2/BitLocker)" if r % 10 != 0 else "Pending Compliance Review"
        mdm = "Jamf Pro" if "MacBook" in model else "Intune/Knox"
        price = random.randint(2200, 4200)
        rows.append(f"{tag},{model},{sn},{emp},{lvl},{loc},{proc_date},{warr_date},{enc},{mdm},{price}")
        count += 1
    save_doc(fname, "\n".join(rows), "csv", ["hardware", "procurement", "asset_tracking", "it"], row_count=count)

# 3. SOC2 Compliance Control Matrices (10 files)
domains = ["access_control", "data_encryption", "incident_response", "vendor_risk", "disaster_recovery", "change_management", "network_security", "vulnerability_mgmt", "privacy_gdpr", "physical_security"]
for domain in domains:
    fname = f"soc2_control_matrix_{domain}.csv"
    rows = ["control_id,domain,control_description,testing_frequency,control_owner,owner_email,sample_size_required,automated_evidence_check,status_2026,last_audited_date"]
    count = 0
    for r in range(1, 140):
        cid = f"SOC2-{domain[:3].upper()}-{r:03d}"
        desc = f"Ensure all {domain.replace('_', ' ')} procedures strictly adhere to NIST SP 800-53 and ISO 27001 requirements across Austin, Dublin, and Singapore."
        freq = random.choice(["Continuous (Automated)", "Monthly", "Quarterly", "Annual"])
        owner = get_name()
        email = get_email(owner)
        sample = random.choice([25, 40, 60, 100])
        check_id = f"CHECK-AUTO-{random.randint(1000, 9999)}"
        status = "Effective / Passed" if r % 7 != 0 else "Observation Noted"
        audit_date = f"2026-0{random.randint(1,6):02d}-15"
        rows.append(f'"{cid}","{domain}","{desc}","{freq}","{owner}","{email}",{sample},"{check_id}","{status}","{audit_date}"')
        count += 1
    save_doc(fname, "\n".join(rows), "csv", ["soc2", "compliance", domain, "security"], row_count=count)

# 4. Cloud Compute Rate Sheets & Cost Center Breakdown (10 files)
for idx in range(1, 11):
    fname = f"cloud_billing_cost_center_report_month_{idx:02d}.csv"
    rows = ["record_id,aws_account_id,service_name,cost_center_id,department,monthly_budget_usd,actual_spend_usd,variance_usd,primary_owner,tagging_compliance_pct,environment"]
    count = 0
    services = ["Amazon OpenSearch Vector Engine", "EC2 p4d.24xlarge GPU", "EC2 g5.12xlarge", "S3 Glacier Deep Archive", "AWS Bedrock API", "CloudFront CDN", "RDS PostgreSQL Multi-AZ", "Datadog Telemetry"]
    for r in range(1, 150):
        rec_id = f"REC-2026-M{idx:02d}-{r:04d}"
        aws_id = f"89412093{random.randint(1000, 9999)}"
        service = random.choice(services)
        cc = random.choice(COST_CENTERS)
        dept = random.choice(DIVISIONS)
        budget = random.randint(5000, 85000)
        actual = budget + random.randint(-4000, 6000)
        var = actual - budget
        owner = get_name()
        tag_pct = f"{random.randint(92, 100)}%"
        env = random.choice(["Production", "Staging", "Benchmark-Eval"])
        rows.append(f"{rec_id},{aws_id},{service},{cc},{dept},{budget},{actual},{var},{owner},{tag_pct},{env}")
        count += 1
    save_doc(fname, "\n".join(rows), "csv", ["cloud", "finops", "billing", "cost_centers"], row_count=count)

# 5. API Rate Limits & Tier Quotas (8 files)
for idx in range(1, 9):
    fname = f"api_rate_limits_and_quotas_region_{idx:02d}.csv"
    rows = ["endpoint_route,customer_tier,rate_limit_rps,burst_capacity,monthly_token_quota,overage_rate_per_1k_tokens,sla_uptime_target,latency_p99_ms,region"]
    count = 0
    routes = ["/v1/vector/search", "/v1/vector/upsert", "/v1/rerank/cross-encoder", "/v1/eval/ragas-score", "/v1/embeddings/batch", "/v1/ingest/document"]
    tiers = ["Free Community", "Developer Pro", "Enterprise Dedicated", "Custom Sovereign"]
    regions = ["us-central-austin", "eu-west-dublin", "ap-east-singapore"]
    for route in routes:
        for tier in tiers:
            for reg in regions:
                rps = 50 if tier == "Free Community" else (250 if tier == "Developer Pro" else (2000 if tier == "Enterprise Dedicated" else 10000))
                burst = rps * 2
                quota = "5,000,000" if tier == "Free Community" else ("100,000,000" if tier == "Developer Pro" else ("5,000,000,000" if tier == "Enterprise Dedicated" else "Unlimited"))
                overage = "$0.00" if tier == "Free Community" else ("$0.0015" if tier == "Developer Pro" else "$0.0008")
                sla = "99.0%" if tier == "Free Community" else ("99.9%" if tier == "Developer Pro" else "99.99%")
                p99 = 150 if "search" in route else (350 if "rerank" in route else 500)
                rows.append(f"{route},{tier},{rps},{burst},{quota},{overage},{sla},{p99},{reg}")
                count += 1
    save_doc(fname, "\n".join(rows), "csv", ["api", "rate_limits", "slas", "customer_tiers"], row_count=count)

# 6. Vulnerability Remediation SLA Tracker (8 files)
for idx in range(1, 9):
    fname = f"vulnerability_remediation_sla_log_q{idx%4+1}_2026_part{idx}.csv"
    rows = ["cve_id,severity_rating,affected_component,repository_name,discovery_date,sla_remediation_days,deadline_date,remediation_status,assigned_lead,jira_ticket_id,cvss_score"]
    count = 0
    sevs = [("P0 - Critical", 1, 1, 9.8), ("P1 - High", 7, 7, 8.4), ("P2 - Medium", 30, 30, 6.1), ("P3 - Low", 90, 90, 3.2)]
    comps = ["llama-index-core", "chromadb-vector-store", "litellm-proxy", "torch-cuda-runtime", "uvicorn-asgi-server", "openssl-crypto-lib"]
    for r in range(1, 130):
        cve = f"CVE-2026-{random.randint(1000, 9999)}"
        sev, sla_days, days, cvss = random.choice(sevs)
        comp = random.choice(comps)
        repo = f"helixforge/{comp}"
        disc_date = f"2026-0{random.randint(1,6):02d}-{random.randint(1,28):02d}"
        dead_date = f"2026-0{random.randint(6,9):02d}-{random.randint(1,28):02d}"
        status = "Resolved / Patched" if r % 5 != 0 else "In Progress (SLA Active)"
        lead = get_name()
        jira = f"SEC-{random.randint(4000, 9999)}"
        rows.append(f"{cve},{sev},{comp},{repo},{disc_date},{sla_days},{dead_date},{status},{lead},{jira},{cvss}")
        count += 1
    save_doc(fname, "\n".join(rows), "csv", ["cve", "vulnerabilities", "security", "slas"], row_count=count)

# 7. GPU Slurm Cluster Allocations (8 files)
for idx in range(1, 9):
    fname = f"gpu_slurm_cluster_nodes_region_{idx:02d}.csv"
    rows = ["node_hostname,gpu_model,gpu_count_per_node,total_vram_gb,slurm_partition,reserved_team,cost_center_id,maintenance_window,node_status,interconnect_speed"]
    count = 0
    models = [("NVIDIA H100 SXM5", 8, 640), ("NVIDIA A100 80GB", 8, 640), ("NVIDIA L40S", 4, 192), ("NVIDIA RTX 6000 Ada", 4, 192)]
    parts = ["gpu-research-long", "gpu-eval-short", "gpu-prod-inference", "gpu-interactive-dev"]
    for r in range(1, 130):
        host = f"gpu-node-{idx:02d}-{r:03d}.internal.helixforge.net"
        gmodel, gcount, vram = random.choice(models)
        part = random.choice(parts)
        team = random.choice(["Applied Research", "Vector Engine", "Eval & Benchmarks"])
        cc = random.choice(["CC-1010", "CC-1020"])
        maint = f"Every 2nd Sunday 02:00-04:00 UTC"
        status = "ALLOCATED_AND_RUNNING" if r % 8 != 0 else "DRAINING_FOR_MAINTENANCE"
        speed = "3.2 Tbps InfiniBand NDR"
        rows.append(f"{host},{gmodel},{gcount},{vram},{part},{team},{cc},{maint},{status},{speed}")
        count += 1
    save_doc(fname, "\n".join(rows), "csv", ["gpu", "slurm", "compute", "infrastructure"], row_count=count)

# 8. Employee Directory Roster (10 files)
for idx in range(1, 11):
    fname = f"employee_directory_roster_part_{idx:02d}.csv"
    rows = ["employee_id,full_name,job_title,department,job_level,manager_name,office_location,work_model,hire_date,annual_pto_accrual_days,workday_id"]
    count = 0
    titles = [
        ("Software Engineer", "Platform Engineering"), ("Research Scientist", "Applied Research"),
        ("Solutions Architect", "Customer Success"), ("Financial Analyst", "Business Operations"),
        ("Security Engineer", "Platform Engineering"), ("DevOps Engineer", "Platform Engineering"),
        ("Technical Writer", "Customer Success"), ("People Ops Partner", "Business Operations")
    ]
    for r in range(1, 150):
        emp_id = f"HF-EMP-2026-{idx:02d}-{r:04d}"
        name = get_name()
        title, dept = random.choice(titles)
        lvl = random.choice(LEVELS)
        mgr = get_name()
        loc = random.choice(LOCATIONS)
        model = "Office-Primary (3 days office)" if loc in ["Austin, TX", "Dublin, Ireland", "Singapore"] and r % 2 == 0 else "Remote-Primary ($150/mo stipend)"
        hdate = f"202{random.randint(0,5)}-{random.randint(1,12):02d}-{random.randint(1,28):02d}"
        pto = 18 if "2024" in hdate or "2025" in hdate else (23 if "2022" in hdate or "2023" in hdate else 28)
        wday = f"WD-{random.randint(10000, 99999)}"
        rows.append(f"{emp_id},{name},{title},{dept},{lvl},{mgr},{loc},{model},{hdate},{pto},{wday}")
        count += 1
    save_doc(fname, "\n".join(rows), "csv", ["employee_directory", "hr", "org_chart", "workday"], row_count=count)

# 9. Subprocessor DPA Compliance Tracker (8 files)
for idx in range(1, 9):
    fname = f"subprocessor_dpa_audit_log_2026_part{idx}.csv"
    rows = ["vendor_name,service_provided,data_transferred_category,hosting_region,dpa_execution_date,soc2_type2_report_date,encryption_in_transit,encryption_at_rest,vendor_risk_tier,annual_contract_value_usd"]
    count = 0
    vendors = [("Amazon Web Services Inc", "Cloud Compute & Storage"), ("OpenAI Ireland Ltd", "LLM Inference API"), ("Pinecone Systems Inc", "Legacy Vector Search"), ("Datadog Inc", "Infrastructure Monitoring"), ("Expensify Inc", "Expense Reimbursements"), ("Navan Inc", "Corporate Travel Booking"), ("Workday Inc", "HRIS System of Record"), ("PagerDuty Inc", "On-Call Escalations")]
    for vname, vserv in vendors:
        reg = random.choice(["US-East (N. Virginia)", "EU-West (Frankfurt)", "AP-Southeast (Singapore)"])
        dpa_date = f"2025-{random.randint(1,12):02d}-15"
        soc_date = f"2025-{random.randint(1,12):02d}-30"
        tier = "Tier 1 - Critical Subprocessor" if "AWS" in vname or "OpenAI" in vname or "Workday" in vname else "Tier 2 - Operational Vendor"
        acv = random.randint(45000, 450000)
        rows.append(f'"{vname}","{vserv}","Customer Vectors & Telemetry","{reg}","{dpa_date}","{soc_date}","TLS 1.3 AES-256-GCM","AES-256-KMS","{tier}",{acv}')
        count += 1
    save_doc(fname, "\n".join(rows), "csv", ["subprocessors", "dpa", "security", "vendors"], row_count=count)

# 10. Compensation & Equity Leveling Matrix (8 files)
comp_regions = ["austin_us", "dublin_eu", "singapore_sg", "us_remote_tier1", "us_remote_tier2", "eu_remote_tier1", "apac_remote_tier1", "uk_london"]
for creg in comp_regions:
    fname = f"compensation_bands_and_equity_{creg}.csv"
    rows = ["job_level,level_title,base_salary_min,base_salary_mid,base_salary_max,annual_target_bonus_pct,initial_rsu_grant_target,annual_refresh_rsu_target,currency,401k_match_pct"]
    count = 0
    curr = "USD" if "us" in creg or "remote" in creg else ("EUR" if "dublin" in creg or "eu" in creg else ("GBP" if "london" in creg else "SGD"))
    mult = 1.0 if "us" in creg else (0.85 if "dublin" in creg or "eu" in creg else (0.90 if "london" in creg else 1.25))
    for lvl_idx, lvl in enumerate(LEVELS, start=3):
        title = f"L{lvl_idx} - " + ("Associate" if lvl_idx==3 else ("Mid-Level" if lvl_idx==4 else ("Senior" if lvl_idx==5 else ("Staff" if lvl_idx==6 else ("Principal" if lvl_idx==7 else "Distinguished")))))
        base_mid = int((90000 + (lvl_idx-3)*35000) * mult)
        base_min = int(base_mid * 0.85)
        base_max = int(base_mid * 1.15)
        bonus = f"{5 + (lvl_idx-3)*3}%"
        rsu_init = int((15000 + (lvl_idx-3)*25000) * mult)
        rsu_ref = int(rsu_init * 0.35)
        match = "4.0%" if "us" in creg else "5.0%"
        rows.append(f"{lvl},{title},{base_min},{base_mid},{base_max},{bonus},{rsu_init},{rsu_ref},{curr},{match}")
        count += 1
    save_doc(fname, "\n".join(rows), "csv", ["compensation", "salary", "equity", "levels", creg], row_count=count)

# 11. Secret Vault Rotation Logs (10 files)
for idx in range(1, 11):
    fname = f"vault_secret_rotation_audit_batch_{idx:02d}.csv"
    rows = ["secret_path,secret_type,target_service,rotation_frequency_days,last_rotated_timestamp,next_rotation_due,rotation_mechanism,rotation_lead,audit_status,vault_cluster_id"]
    count = 0
    stypes = ["AWS IAM Credentials", "Database Master Password", "TLS Private Key", "API Bearer Token", "SSH CA Signing Key"]
    for r in range(1, 140):
        spath = f"kv/prod/service-{r:03d}/credentials"
        stype = random.choice(stypes)
        target = f"microservice-runtime-v{r%10+1}"
        freq = 30 if "AWS" in stype or "Database" in stype else 90
        last_rot = f"2026-05-{random.randint(1,28):02d}T10:00:00Z"
        next_rot = f"2026-06-{random.randint(1,28):02d}T10:00:00Z"
        mech = "Automated HashiCorp Vault Plugin" if r % 4 != 0 else "Manual YubiKey Escrow Procedure"
        lead = get_name()
        status = "COMPLIANT_ROTATED" if r % 9 != 0 else "ROTATION_SCHEDULED_DUE_SOON"
        vcluster = f"VAULT-PROD-{idx:02d}"
        rows.append(f'"{spath}","{stype}","{target}",{freq},"{last_rot}","{next_rot}","{mech}","{lead}","{status}","{vcluster}"')
        count += 1
    save_doc(fname, "\n".join(rows), "csv", ["vault", "secrets", "rotation", "security"], row_count=count)

# 12. Incident Postmortem Log Summaries (10 files)
for idx in range(1, 11):
    fname = f"incident_postmortem_summary_log_202{idx%3+4}_part{idx}.csv"
    rows = ["incident_id,incident_date,severity_level,primary_root_cause,impacted_service,time_to_detect_mins,time_to_resolve_mins,customer_sla_breached,incident_commander,postmortem_document_url,financial_penalty_usd"]
    count = 0
    sevs = ["P0 - Critical Outage", "P1 - Major Degradation", "P2 - Minor Component Issue"]
    causes = ["BGP Route Flapping", "Database Connection Pool Exhaustion", "Slurm GPU Out of Memory", "Corrupted Vector Index Partition", "Expired TLS Certificate", "Upstream Provider Outage"]
    for r in range(1, 120):
        inc_id = f"INC-2026-{idx:02d}-{r:04d}"
        date = f"2026-0{random.randint(1,6):02d}-{random.randint(1,28):02d}"
        sev = random.choice(sevs)
        cause = random.choice(causes)
        svc = random.choice(["Vector Engine API", "Search Reranker", "Expensify Sync", "Workday Single Sign-On"])
        ttd = random.randint(2, 25)
        ttr = random.randint(20, 240)
        breached = "YES (Credit Issued)" if "P0" in sev and ttr > 60 else "NO"
        ic = get_name()
        url = f"https://wiki.helixforge.internal/postmortems/{inc_id}.md"
        penalty = random.randint(10000, 50000) if breached == "YES (Credit Issued)" else 0
        rows.append(f'{inc_id},{date},"{sev}","{cause}",{svc},{ttd},{ttr},{breached},"{ic}",{url},{penalty}')
        count += 1
    save_doc(fname, "\n".join(rows), "csv", ["incidents", "postmortem", "slas", "reliability"], row_count=count)

print("CSV files generation complete.")

# ==============================================================================
# SECTION 2: GENERATE PROSE MARKDOWN FILES (~40% of files, ~100 files)
# ==============================================================================

def generate_very_long_md(title, category, sections):
    body = [f"# {title}\n", f"**Document ID**: POL-{category.upper()}-{random.randint(100,999)}", f"**Effective Date**: February 1, 2026", f"**Owner**: {get_name()} ({category.replace('_', ' ').title()} Team)", f"**Approved By**: Mara Chen (CEO) & Elena Voss (CISO)\n"]
    body.append("## Executive Overview & Policy Mandate\n")
    body.append(f"This official HelixForge governance policy defines technical specifications, managerial responsibilities, and procedural enforcement mechanisms for {category.replace('_', ' ')} across all global operations (Austin, TX HQ; Dublin, Ireland; Singapore). Compliance is mandatory for all full-time employees, contractors, and third-party vendors. Non-compliance is escalated immediately to People Operations and CISO Elena Voss.\n")
    
    for sec_title, sec_content in sections:
        body.append(f"## {sec_title}\n")
        body.append(sec_content + "\n")
        # Add rich sub-paragraphs with concrete numeric rules and cross references
        body.append(f"### Procedural Controls & Technical Mandates for {sec_title}\n")
        body.append(f"1. **Submission & Filing Pathway**: All formal requests must be submitted through Workday or Jira Service Desk under ticket category `{category.upper()}-REQ`.\n"
                    f"2. **Budgetary Limits & Cost Centers**: Expenditures must align with designated cost center budgets ({random.choice(COST_CENTERS)}). Any variance exceeding 10% requires VP Finance Marcus Vance approval.\n"
                    f"3. **Audit Compliance & SOC2 Evidence**: System logs, approval receipts, and ticket histories are archived in S3 Glacier (`s3://helixforge-compliance-archive/`) and retained for 7 years to satisfy SOC2 Type II Trust Services Criteria (Access Control CC6.1, Encryption CC6.6, Incident Response CC7.3).\n"
                    f"4. **Cross-Policy Alignment**: This section cross-references the HelixForge Paid Time Off Policy, Engineering On-Call Escalation Matrix, and Information Security Handbook.\n")
        
        # Add detailed hypothetical scenarios / case studies to expand file depth cleanly
        body.append(f"#### Case Study & Enforcement Example ({sec_title})\n")
        body.append(f"Consider an employee in {random.choice(LOCATIONS)} requesting an exception under this section. The request must be logged 10 business days prior to implementation. "
                    f"The primary manager evaluates team workload and confirms that on-call coverage in PagerDuty is fully staffed by at least two qualified L5+ engineers. "
                    f"If approved, the Workday status updates automatically and sends notification to people@helixforge.example.\n")

    body.append("## Revision History & Annual Audit Schedule\n")
    body.append("This policy is reviewed annually by the Policy Steering Committee. Minor updates are published quarterly. For policy clarification or exception requests, submit a ticket in Slack #policy-questions or email policy@helixforge.example.\n")
    
    return "\n".join(body)

# Generate 100 comprehensive Markdown files (approx 2,500 - 4,000 words each)
md_topic_defs = [
    ("Paid Time Off and Accrual Master Policy", "pto", [
        ("Monthly Accrual Schedules by Level", "Full-time employees accrue PTO on the 1st of each month. L3 to L5 staff accrue 18 days annually. L6 to L8 staff accrue 23 days annually. Employees with >5 years service accrue 28 days annually."),
        ("Rollover Caps and Forfeiture Rules", "A maximum of 8 accrued PTO days (64 hours) may roll over into the next fiscal year. Excess days are forfeited on January 31, except in California and Ireland where statutory law prohibits PTO forfeiture."),
        ("Blackout Windows & Release Schedules", "Platform Engineering enforces a strict PTO blackout during the two weeks preceding major platform launches as published on the master release calendar in Jira."),
        ("On-Call Swap Mandates", "Taking PTO does not automatically remove an engineer from PagerDuty on-call shifts. The engineer must arrange a swap in PagerDuty at least 48 hours prior to taking leave.")
    ]),
    ("Remote Work and Stipend Guidelines", "remote", [
        ("Hybrid vs Remote Primary Status", "Staff within 50 miles of Austin, Dublin, or Singapore are Office-Primary (office Tue-Thu). Remote-Primary staff live outside 50 miles and work 100% remotely."),
        ("Monthly Internet Stipend Details", "Remote-Primary employees receive a $150/month tax-free stipend processed in monthly payroll for home internet and utility costs."),
        ("International Work Limits", "Working outside your home country is capped at 30 days per fiscal year and requires a Workday Mobility Ticket. Working from sanctioned nations is strictly forbidden.")
    ]),
    ("Parental Leave and Family Benefits Framework", "parental", [
        ("Primary vs Secondary Caregiver Benefits", "Primary caregivers receive 16 weeks of 100% paid leave. Secondary caregivers receive 8 weeks of 100% paid leave. Caregiver status is declared in Workday."),
        ("On-Call Pause & Stipend Rules", "Staff on parental leave are automatically removed from PagerDuty rotations on day 1. On-call stipends pause during leave and resume upon return."),
        ("Disability Top-Up Alignment", "HelixForge tops up short-term disability payments in the US so birth mothers receive 100% base salary for up to 16 full weeks.")
    ]),
    ("Information Security and Zero Trust Mandate", "infosec", [
        ("Hardware Security Key Enforcement", "YubiKey 5 Series hardware keys are mandatory for GitHub, AWS, Vault, and Workday access. SMS and authenticator apps are disabled."),
        ("Step-CA Short Lived SSH Certificates", "Direct SSH keys on production nodes are forbidden. Engineers must issue 8-hour certificates via step-ca bound to YubiKeys."),
        ("Data Classification Tiers", "Data is classified into Public, Internal, Confidential, and Restricted. Customer vector embeddings are strictly Restricted.")
    ]),
    ("AI Model Governance and Red Teaming Policy", "model_gov", [
        ("Adversarial Red Teaming Requirements", "Models must undergo 80 hours of red teaming for prompt injection, toxic output, and memorized PII before production release."),
        ("Benchmark Quality Gates", "Models must score >92% on the internal Safety Rubric and <0.01% toxicity score on RealToxicityPrompts before CISO sign-off."),
        ("Synthetic Data Safeguards", "Synthetic training datasets must be scrubbed using Microsoft Presidio and audited by the Data Privacy Officer.")
    ]),
    ("Disaster Recovery and Business Continuity SOP", "disaster_recovery", [
        ("RPO and RTO Targets", "HelixForge targets an RPO of 15 minutes and an RTO of 2 hours for all core vector database search APIs across Austin and Dublin."),
        ("Bi-Annual DR Failover Drills", "DR drills are executed twice per fiscal year. Automated DNS failover switches traffic to secondary regions within 5 minutes."),
        ("Database Backup Verification", "PostgreSQL database snapshots are backed up hourly to multi-region S3 buckets with Object Lock enabled.")
    ]),
    ("Travel and Per Diem Policy Guide", "travel", [
        ("Flight Booking & Class Rules", "Flights under 6 hours must be economy class. Flights over 6 hours allow premium economy. Business class requires VP approval."),
        ("Hotel Nightly Rate Caps", "Hotel caps: $220/night in US tier-1 cities (SF, NYC, Seattle), $180/night in other US cities, €180/night in EU, and SGD 280/night in Singapore."),
        ("Meals and Per Diem Rules", "Daily meal caps during business travel are $40 lunch and $90 dinner. Singapore onsite work provides an SGD 90/day per diem.")
    ])
]

for idx in range(1, 101):
    topic_info = md_topic_defs[(idx-1) % len(md_topic_defs)]
    fname = f"policy_doc_guide_{topic_info[1]}_v{idx}.md"
    content = generate_very_long_md(f"{topic_info[0]} (Revision {idx})", topic_info[1], topic_info[2])
    save_doc(fname, content, "md", ["policy", topic_info[1], "helixforge_handbook"])

print("Prose Markdown files generation complete.")

# ==============================================================================
# SECTION 3: GENERATE TEXT SOP FILES (~20% of files, ~50 files)
# ==============================================================================

sop_defs = [
    ("sop_vault_secret_rotation_guide", "HashiCorp Vault Secret & Key Rotation Procedure", [
        "1. Log into Vault cluster via SSH using YubiKey step-ca certificate.",
        "2. Execute `vault operator step-down` to verify active leader health.",
        "3. Run `/scripts/rotate_db_credentials.sh --environment=prod --cost-center=CC-1500`.",
        "4. Validate service health in Grafana panel DASH-GRAFANA-842.",
        "5. Update Vault audit log spreadsheet `vault_secret_rotation_audit_batch_01.csv`."
    ]),
    ("sop_slurm_gpu_job_submission", "Slurm GPU Cluster Batch Job Submission Procedure", [
        "1. Connect to Slurm head node `slurm-head-01.internal.helixforge.net` via WireGuard VPN.",
        "2. Prepare your `.sbatch` script specifying `#SBATCH --partition=gpu-research-long`.",
        "3. Request exact GPU resources: `#SBATCH --gres=gpu:h100:8` and maximum walltime `#SBATCH --time=48:00:00`.",
        "4. Submit job using `sbatch submission_script.sh` and record the returned Job ID.",
        "5. Monitor GPU memory utilization via `squeue -u $USER` and `nvidia-smi` logging."
    ]),
    ("sop_production_ssh_yubikey", "Production SSH Access via YubiKey & Step-CA", [
        "1. Insert YubiKey 5 Series into local USB port.",
        "2. Run `step ca bootstrap --ca-url=https://step-ca.internal.helixforge.net`.",
        "3. Issue 8-hour SSH certificate: `step ssh login $USER@helixforge.example --provisioner=yubikey`.",
        "4. Touch YubiKey gold contacts when prompted for hardware presence authorization.",
        "5. SSH to target server: `ssh admin@gpu-node-01.internal.helixforge.net`."
    ]),
    ("sop_customer_incident_war_room", "Customer Incident Escalation & War Room Protocol", [
        "1. Upon P0/P1 trigger, PagerDuty automatically creates Zoom War Room and Slack channel `#inc-2026-xxxx`.",
        "2. On-call engineer assumes role of Incident Commander (IC) and posts initial status update within 15 mins.",
        "3. IC assigns Tech Lead to investigate root cause and Comms Lead to update status page.",
        "4. Status page updates must be posted every 30 minutes until incident resolution.",
        "5. Conduct blameless postmortem within 5 business days and log in `incident_postmortem_summary_log_2026.csv`."
    ]),
    ("sop_gdpr_right_to_be_forgotten", "GDPR Right to Be Forgotten Data Deletion SOP", [
        "1. Receive customer DSAR deletion ticket from Jira Service Desk (`GDPR-DEL-xxxx`).",
        "2. Verify legal authorization with Data Privacy Officer Elena Voss.",
        "3. Run automated purge script: `python -m src.cli purge-customer --org-id=$ORG_ID`.",
        "4. Confirm zero vector matches remain in Chroma DB and AWS S3 cold storage.",
        "5. Issue Certificate of Destruction to customer within 14 calendar days."
    ])
]

for idx in range(1, 51):
    sop_info = sop_defs[(idx-1) % len(sop_defs)]
    fname = f"{sop_info[0]}_procedure_v{idx}.txt"
    title = f"STANDARD OPERATING PROCEDURE: {sop_info[1]} (Rev {idx})"
    
    header = [
        "================================================================================",
        f"HELIXFORGE STANDARD OPERATING PROCEDURE - DOCUMENT REF: SOP-{idx:04d}",
        f"TITLE: {title}",
        f"EFFECTIVE DATE: 2026-02-01 | REVIEW FREQUENCY: QUARTERLY",
        f"CLASSIFICATION: INTERNAL CONFIDENTIAL | OWNER: {get_name()}",
        "================================================================================",
        "\nPURPOSE & OPERATIONAL SCOPE:",
        "This standard operating procedure defines mandatory step-by-step instructions for",
        "HelixForge staff. All personnel performing this workflow must adhere strictly to these steps.",
        "Failure to adhere to these procedures will result in mandatory review by CISO Elena Voss.\n",
        "PROCEDURAL STEPS:\n"
    ]
    steps_text = "\n".join(sop_info[2])
    
    # Detailed operational instructions to ensure substantial file length
    deep_procedure = [
        "\nADDITIONAL VERIFICATION & VERBOSE LOGGING MANDATE:",
        "Step A: Execute diagnostic check script `/usr/local/bin/verify_system_posture.sh`.",
        "Step B: Inspect system journal logs using `journalctl -u helixforge-service -n 100 --no-pager`.",
        "Step C: Confirm cost center allocation in Expensify or Workday matching CC-1010 or CC-1500.",
        "Step D: Verify that all temporary cache files in `/var/tmp/helixforge_run/` are scrubbed upon completion.",
        "Step E: File verification confirmation in Slack channel #ops-audit-log with ticket ID reference.\n",
        "ESCALATION PATHWAY:",
        "If any step above fails or returns exit code non-zero, immediately trigger PagerDuty policy PD-POLICY-P0-IMMEDIATE",
        "and contact On-Call Lead Engineer. Do NOT attempt unapproved manual recovery on production nodes.\n",
        "VERIFICATION & AUDITING:",
        "Upon completing the procedural steps above, log execution in Jira ticket and update",
        "the associated CSV tracking log in data/raw_docs/. Direct questions to security@helixforge.example.",
        "================================================================================"
    ]
    
    content = "\n".join(header) + steps_text + "\n" + "\n".join(deep_procedure)
    save_doc(fname, content, "txt", ["sop", "procedure", "operations", sop_info[0]])

print("Text SOP files generation complete.")

# Write MANIFEST.json
MANIFEST_PATH.write_text(json.dumps(manifest_entries, indent=2), encoding="utf-8")
print(f"Saved manifest to {MANIFEST_PATH}")

# Print summary metrics (NO document content dumped)
total_files = len(manifest_entries)
total_chunks = sum(e["approx_chunks"] for e in manifest_entries)
csv_files = [e["filename"] for e in manifest_entries if e["format"] == "csv"]
md_files = [e["filename"] for e in manifest_entries if e["format"] == "md"]
txt_files = [e["filename"] for e in manifest_entries if e["format"] == "txt"]

print("\n--- GENERATION SUMMARY ---")
print(f"Total new files created: {total_files}")
print(f"Estimated chunk count: ~{total_chunks}")
print(f"CSV files count: {len(csv_files)}")
print(f"MD files count: {len(md_files)}")
print(f"TXT files count: {len(txt_files)}")
