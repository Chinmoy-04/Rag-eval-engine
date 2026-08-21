# Distributed GPU Cluster Scheduling & Slurm Allocation Policy
*HelixForge fictional handbook.*

Owner: Marcus Vance, Head of Core Compute (marcus.vance@helixforge.example / CC-1010). Approved by: Devon Hale (CTO). Effective date: February 1, 2026.

## 1. Scope & Compute Infrastructure
HelixForge operates high-performance multi-node GPU clusters across Austin HQ on-premises labs and dedicated cloud VPCs (AWS us-east-1 and CoreWeave). To maximize compute efficiency and prevent resource starvation, all cluster jobs are scheduled via Slurm Workload Manager.

## 2. Queue Partitions and Priority Tiers

| Partition Name | Target Workload | Priority Weight | Max Walltime | Preemptible | Target Utilization |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **prod-serving** | Customer Live Inference Endpoints | 10,000 (Highest) | Infinite | No | >= 75% rolling |
| **eval-safety** | Release Gate Scans & Safety Sweeps | 5,000 | 4 Hours | No | 100% burst |
| **pretrain-batch** | Foundation Model Training (CC-2010) | 2,500 | 72 Hours | Yes (Grace: 10m) | >= 85% |
| **inetune-lora** | Alignment & Customer Fine-Tuning | 1,000 | 24 Hours | Yes (Grace: 5m) | >= 80% |
| **dev-interactive**| Researcher Jupyter / Debugging | 200 | 8 Hours | Yes (Immediate) | Auto-shutdown 20:00 |

## 3. Scheduling Guardrails & Fair-Share Rules
1. **Interactive Session Limits**: Engineers and researchers are limited to a maximum of **2 active GPUs** in dev-interactive. Sessions idle for > 45 minutes are automatically terminated.
2. **Multi-Node Job Checkpointing**: All batch jobs submitted to pretrain-batch or inetune-lora must implement PyTorch checkpointing at intervals of **<= 30 minutes** to support graceful preemption (per cloud_cost_optimization_policy.md).
3. **Queue Allocations Matrix**: Detailed Slurm partition limits and GPU core limits are codified in slurm_queue_allocations.csv.

## 4. Out-of-Band Priority Escalations
Jobs requiring dedicated non-preemptible access across > 64 GPUs for major conference deadlines (e.g. NeurIPS / ICML per learning_stipend_and_conferences.md) must be approved by Marcus Vance and Devon Hale at least **5 business days** in advance.

## 5. Cross-Links
- Slurm queue parameters and partition matrix: slurm_queue_allocations.csv.
- FinOps cost optimization and GPU utilization: cloud_cost_optimization_policy.md.
- Internal GPU rate sheet: cloud_compute_rate_sheet.csv.
- Slurm job submission SOP: sop_slurm_gpu_job_submission.txt.
