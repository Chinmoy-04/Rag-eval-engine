# Environmental Sustainability & Green Compute Policy
*HelixForge fictional handbook.*

Owner: Brendan Walsh, Head of Facilities & Global Real Estate (brendan.walsh@helixforge.example / CC-4040). Approved by: Mara Chen (CEO) and Devon Hale (CTO). Effective date: February 1, 2026.

## 1. Environmental Commitment
High-performance distributed AI training and inference require substantial electricity and cooling resources. HelixForge is committed to minimizing our global carbon footprint across our ~420 FTE operations, Austin HQ server labs, and partner cloud data centers in Austin, Dublin, and Singapore.

## 2. Data Center Efficiency & PUE Standards
- **Power Usage Effectiveness (PUE)**: All third-party colocation facilities and dedicated cloud regions (AWS, GCP, CoreWeave per software_catalog.csv) must maintain an audited annual PUE of <= 1.25.
- **100% Renewable Energy Matching**: 100% of electricity consumed by Austin HQ labs and Dublin office facilities is matched with certified renewable energy credits (RECs) or local wind/solar grid guarantees.
- **Carbon Metrics Tracking**: Departmental compute emissions are tracked in sustainability_and_carbon_metrics.csv and reported semi-annually to the executive committee.

## 3. Workload Scheduling for Low-Carbon Intensity
- **Carbon-Aware Training Dispatch**: Non-urgent batch training jobs (scheduled on pretrain-batch per gpu_cluster_scheduling_and_slurm_policy.md) automatically leverage grid carbon intensity signals from Watttime API, biasing cluster execution to hours with high local renewable penetration.
- **Embodied Carbon Hardware Lifecycle**: Server hardware and engineer laptops are maintained on 24-to-36-month refresh lifecycles (see hardware_procurement_matrix.csv), with decommissioned units donated or recycled via certified e-Stewards vendors per sop_laptop_imaging_deprovisioning.txt.

## 4. Business Travel & Commuting Offsets
- All corporate flight travel booked through Navan is automatically offset via certified direct-air-capture and reforestation programs funded by cost_centers.csv CC-4040.
- Public transit and EV commuter subsidies are provided to employees across Austin, Dublin, and Singapore (see facilities_badge_and_visitor_policy.md).

## 5. Cross-Links
- Sustainability carbon metrics and regional PUE ratings: sustainability_and_carbon_metrics.csv.
- Cloud cost and compute allocation: cloud_cost_optimization_policy.md.
- Facilities management and transit benefits: facilities_badge_and_visitor_policy.md.
