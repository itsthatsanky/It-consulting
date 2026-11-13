# GreenCompute: AI-Driven Energy and Computing Optimization for Sustainable Data Centres

**Prepared by:** WAS Group 2 · TAPMI Bengaluru (NAT Consulting and Project Management · BBA Semester 5)  
**Client:** GreenCore Data Services Pvt. Ltd., Bengaluru *(Hypothetical Mid-Tier Data Centre Client)*

---

## Project Overview

**GreenCompute** is an interactive decision-support and telemetry consulting dashboard designed for **GreenCore Data Services Pvt. Ltd., Bengaluru**. It models facility-wide power usage effectiveness (PUE), 24-hour load forecasting and anomaly detection, Python batch workload optimization, rack-level thermal diagnostics, phased CapEx/OpEx financial payback scenarios, and BRSR / GHG Protocol carbon abatement pathways across three progressive consulting tiers:

- **Tier 1:** Visibility & Software Advisory (12-Week PoC · `₹8,20,000` Pilot Budget)
- **Tier 2:** Full-Stack Optimization Blueprint (Sub-Rack LoRaWAN Sensor Mesh & Aisle Containment)
- **Tier 3:** Turnkey AI Automation & Carbon Offset (Phase-2 Closed-Loop HVAC Scale-Up & Temporal Load Shifting)

---

## Dashboard Architecture (4 Interactive Tabs)

1. **`1. Executive Overview & Telemetry` (`tab_overview.py`)**
   - Live KPI cards for Projected Facility PUE, Net Annual Financial Benefit (`INR ₹` / `USD $`), Annual Scope 2 $\text{CO}_2$ Avoided, and Simple Payback & Annual ROI (%).
   - Dual-axis 24-hour telemetry chart (IT Power kW, Cooling Overhead kW, Grid Carbon Intensity $\text{gCO}_2/\text{kWh}$, and Tier 3 AI Carbon-Aware Shifted Load).
   - Collapsible ML Model Validation & Anomaly Audit Drawer (`8.4%` ML Forecast MAPE vs. `19.2%` baseline; `93.3%` Isolation Forest Recall across 15 injected anomaly events).
   - Workstream B Python 3.11 vectorized ETL benchmark card (`14.8s → 5.2s` runtime, `-64.9%`; `1,420 MB → 610 MB` peak RAM, `-57.0%`; `PASS - 100% Exact Match`).
2. **`2. Rack & Thermal Floorplan` (`tab_floorplan.py`)**
   - 2-Row $\times$ 6-Rack (`R01`–`R12`) NOC thermal and differential pressure floorplan for Bengaluru Data Hall A.
   - Simulates Tier 1 sensor blind spots, Tier 2 hot-air recirculation alerts on `R03`, `R08`, and `R11` ($>27.5^\circ\text{C}$), and Tier 3 Phase-2 AI Closed-Loop Cooling Control ($21.5^\circ\text{C}\text{–}22.8^\circ\text{C}$ with `-22%` CRAC fan power reduction).
3. **`3. Optimization Roadmap & BoM` (`tab_roadmap.py`)**
   - Section A: Itemized `₹8,20,000` 12-week pilot budget breakdown, 3-milestone billing schedule (`40% / 30% / 30%`), and 3 unlocked Workstream A/B software advisory actions.
   - Section B: Interactive Phase-2 Hardware Bill of Materials (BoM) CapEx simulator with real-time payback/ROI recalculation and one-click CSV proposal export.
4. **`4. Carbon Offset & ESG Reporting` (`tab_esg.py`)**
   - Scope 1 & Scope 2 emissions stacked comparison, Carbon Usage Effectiveness (CUE) tracking, and an interactive Net-Zero Simulator (I-RECs / Green Tariff % and Verified Carbon Credits %).
   - Generates a copyable and downloadable **BRSR / GHG Protocol Executive ESG Disclosure**.

---

## Data Governance & Provenance Rules

- **Synthetic / Projected Status:** GreenCore Data Services Pvt. Ltd. is a hypothetical client. All facility telemetry, rack thermal profiles, and financial trajectories are deterministically seeded (`np.random.seed(42)`) from the report's Appendix B assumptions.
- **No-Double-Counting Rule:** Workstream B software runtime and memory reductions (`-64.9%` runtime) are tracked separately as compute-capacity efficiency KPIs and are never added on top of facility-level `₹/kWh` utility savings.
- **Phase-2 Safety Governance:** Tier 1 is strictly a human-in-the-loop advisory pilot. Tier 3 closed-loop BMS/CRAC automation is modeled as a Phase-2 post-pilot scale-up subject to formal facility engineering safety sign-off.

---

## Consulting Team (WAS Group 2 · TAPMI Bengaluru)

| Role ID | Workstream | Consultant | Roll No. |
| :--- | :--- | :--- | :--- |
| **M1** | PM / Client | Adithya Pradeep | 246213368 |
| **M2** | Tech / AI | Sankarshana Mulugundam | 246213080 |
| **M3** | Delivery / QA | Samiksha Sandeep Das | 246213076 |
| **M4** | Finance | Faizan Ali Siddiqui | 246213110 |
| **M5** | Research | Anupama Sahu | 246213502 |
| **M6** | Prototype / Adoption | Prathamesh Prabhu | 246213290 |

---

## Local Setup & Execution

```bash
pip install -r requirements.txt
streamlit run app.py
```
