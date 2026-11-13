"""
Tab 3: Optimization Roadmap, 12-Week Pilot Budget & Interactive Phase-2 Hardware BoM Simulator.
Prepared by WAS Group 2, TAPMI Bengaluru for GreenCore Data Services Pvt. Ltd., Bengaluru.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from data_simulator import (
    PHASE2_HARDWARE_CATALOG_INR,
    TIER1_PILOT_BUDGET_INR,
    USD_TO_INR,
    compute_financials_and_thermodynamics,
    normalize_tier_key,
)


# ---------------------------------------------------------------------------
# Currency & Number Formatting Helpers
# ---------------------------------------------------------------------------
def _format_inr(amount: float, decimals: int = 0) -> str:
    """Format an INR number using the Indian numbering system (e.g., ₹8,20,000)."""
    neg = "-" if amount < 0 else ""
    val = abs(amount)
    whole = int(round(val)) if decimals == 0 else int(val)
    frac = "" if decimals == 0 else f"{val - whole:.{decimals}f}"[1:]
    s = str(whole)
    if len(s) > 3:
        head, tail = s[:-3], s[-3:]
        groups: List[str] = []
        while len(head) > 2:
            groups.insert(0, head[-2:])
            head = head[:-2]
        if head:
            groups.insert(0, head)
        s = ",".join(groups) + "," + tail
    return f"{neg}₹{s}{frac}"


def _format_currency(amount_inr: float, currency: str, decimals: int = 0) -> str:
    """Format a canonical INR value in the active currency (INR or USD at 1 USD = ₹84)."""
    if currency == "USD ($)":
        usd_val = amount_inr / USD_TO_INR
        neg = "-" if usd_val < 0 else ""
        return f"{neg}${abs(usd_val):,.{decimals}f}"
    return _format_inr(amount_inr, decimals=decimals)


# ---------------------------------------------------------------------------
# Reference Data: Section 8.1 Pilot Budget Metadata, 12-Week Roadmap & Actions
# ---------------------------------------------------------------------------
PILOT_BUDGET_DETAILS: Dict[str, Dict[str, str]] = {
    "Consulting & Delivery": {
        "workstream": "Workstream A + B + Program Governance",
        "owner": "M1 · Adithya & M4 · Faizan (Finance)",
        "deliverable": "12-week consulting engagement, baseline energy audit, ASHRAE thermal modeling & executive business case",
        "billing_milestone": "Milestone 1–3 (40% / 30% / 30%)",
    },
    "Cloud/Software/AI": {
        "workstream": "Workstream A (ML Forecasting & Anomaly Engine)",
        "owner": "M2 · Sankarshana & M5 · Anupama",
        "deliverable": "Time-series load forecaster (8.4% MAPE), Isolation Forest anomaly pipeline & SCI carbon profiler",
        "billing_milestone": "Milestone 2 (Week 8 Prototype)",
    },
    "Test Sensors/Data Setup": {
        "workstream": "Workstream A (Telemetry & Smart Meter Ingestion)",
        "owner": "M3 · Samiksha (Delivery/QA)",
        "deliverable": "15-min smart meter Modbus/SNMP bridge, PDU/CRAC telemetry parser & 12-rack inlet test probes",
        "billing_milestone": "Milestone 1 (Week 4 Instrumentation)",
    },
    "Dashboard & Integration": {
        "workstream": "Workstream A + B (Streamlit Control Center)",
        "owner": "M6 · Prathamesh & M2 · Sankarshana",
        "deliverable": "Real-time GreenCompute command center, anomaly audit log & interactive CFO payback simulator",
        "billing_milestone": "Milestone 2 (Week 8 Prototype)",
    },
    "Training/SOPs": {
        "workstream": "Operations Handover & Governance",
        "owner": "M3 · Samiksha (Delivery/QA) & M1 · Adithya",
        "deliverable": "Human-in-the-loop runbooks, NOC alert triage SOPs & facility engineering workshop",
        "billing_milestone": "Milestone 3 (Week 12 Handover)",
    },
    "Contingency": {
        "workstream": "Risk Reserve (Appendix B Governance)",
        "owner": "M4 · Faizan (Finance)",
        "deliverable": "Ring-fenced 9.1% risk buffer for legacy BMS protocol adapters & change-window scheduling",
        "billing_milestone": "Released Only on Client Sign-Off",
    },
}

ROADMAP_PHASES: List[Dict[str, Any]] = [
    {
        "phase": "Phase 1 · Weeks 1–4",
        "title": "Discovery & Instrumentation",
        "milestone": "Milestone 1 (40% Billing · Week 4)",
        "pct_allocation": 0.40,
        "accent": "#10B981",
        "owners": [
            "M1 · Adithya",
            "M3 · Samiksha (Delivery/QA)",
            "M5 · Anupama",
        ],
        "key_activities": [
            "Ingest 15-minute utility smart-meter, PDU, and CRAC telemetry streams across all 12 racks (R01–R12).",
            "Establish immutable Baseline PUE, IT load profile, and hotspot diagnostic map (flagging R03, R08, R11 > 27.5°C).",
            "Inventory batch ETL / database workloads and establish SHA-256 output equivalence test harnesses.",
        ],
        "exit_gate": "Gate 1 Sign-Off: Baseline Telemetry Audit & Hotspot Register Verified",
    },
    {
        "phase": "Phase 2 · Weeks 5–8",
        "title": "ML & Code Prototyping",
        "milestone": "Milestone 2 (30% Billing · Week 8)",
        "pct_allocation": 0.30,
        "accent": "#06B6D4",
        "owners": [
            "M2 · Sankarshana",
            "M6 · Prathamesh",
            "M5 · Anupama",
        ],
        "key_activities": [
            "Train & validate 24-hour ML load forecaster (achieving 8.4% MAPE vs. 19.2% baseline, beating <15% target).",
            "Deploy Isolation Forest + MAD thermal anomaly detector (93.3% precision & recall across 15 injected events).",
            "Refactor Python 3.11 row-iteration ETL pipelines to vectorized NumPy/Pandas (-64.9% runtime, -57.0% RAM).",
        ],
        "exit_gate": "Gate 2 Sign-Off: ML Validation Benchmark & Vectorized Code Equivalence PASS",
    },
    {
        "phase": "Phase 3 · Weeks 9–12",
        "title": "Validation & Handover",
        "milestone": "Milestone 3 (30% Billing · Week 12)",
        "pct_allocation": 0.30,
        "accent": "#F59E0B",
        "owners": [
            "M4 · Faizan (Finance)",
            "M3 · Samiksha (Delivery/QA)",
            "M1 · Adithya",
        ],
        "key_activities": [
            "Execute shadow-mode advisory trials with NOC operators approving CRAC setpoint & workload right-sizing actions.",
            "Reconcile metered kWh & Scope 2 tCO₂e reductions against Appendix B financial payback model.",
            "Deliver NOC Standard Operating Procedures (SOPs), executive ESG pack, and Phase-2 hardware scale-up BoM.",
        ],
        "exit_gate": "Gate 3 Sign-Off: CFO Financial Verification & Phase-2 Scale-Up Readiness",
    },
]

UNLOCKED_ADVISORY_ACTIONS: List[Dict[str, Any]] = [
    {
        "id": "ACT-A1",
        "title": "Decommission 18 Idle/Zombie VMs",
        "workstream": "Workstream A · Compute Hygiene",
        "owner": "M3 · Samiksha (Delivery/QA) & M1 · Adithya",
        "share_of_tier1_savings": 0.38,
        "est_kwh_ref": 22_800,
        "confidence": "98.2% Telemetry Verified",
        "effort": "Low (Zero Hardware CapEx · Change Window)",
        "summary": (
            "14-day PDU & hypervisor telemetry identified 18 orphaned dev/test VMs drawing continuous "
            "baseload power with <1.5% CPU I/O. Automated snapshot archival and graceful termination "
            "immediately eliminates phantom IT draw and cascading CRAC cooling load."
        ),
        "verification": "Hypervisor CPU/Network I/O < 1.5% over 336 consecutive hours; snapshot backup verified.",
    },
    {
        "id": "ACT-A2",
        "title": "Right-Size Over-Provisioned DB Clusters",
        "workstream": "Workstream A · Infrastructure Right-Sizing",
        "owner": "M2 · Sankarshana & M4 · Faizan (Finance)",
        "share_of_tier1_savings": 0.34,
        "est_kwh_ref": 20_400,
        "confidence": "95.6% ML Load Forecast",
        "effort": "Low–Medium (vCPU/RAM Re-allocation)",
        "summary": (
            "ML diurnal load profiling (8.4% MAPE) proves 4 primary PostgreSQL/analytics clusters run at "
            "22% peak vCPU allocation outside the 13:00–18:00 batch window. Consolidating standby nodes "
            "and right-sizing vCPU/memory envelopes trims continuous socket power draw."
        ),
        "verification": "99.95% query SLA preserved under p99 load replay; zero latency degradation.",
    },
    {
        "id": "ACT-B1",
        "title": "Vectorize Python Batch Analytics Pipeline",
        "workstream": "Workstream B · Green Software Engineering",
        "owner": "M6 · Prathamesh & M5 · Anupama",
        "share_of_tier1_savings": 0.28,
        "est_kwh_ref": 16_800,
        "confidence": "100% SHA-256 Output Match",
        "effort": "Low (Drop-in Code Patch · Zero CapEx)",
        "summary": (
            "Replaces legacy Python `.iterrows()` and nested loops across 2.5M daily records with "
            "vectorized NumPy/Pandas array operations. Cuts execution runtime from 14.8s to 5.2s "
            "(-64.9%), peak CPU from 88% to 54%, peak RAM from 1,420 MB to 610 MB (-57.0%), and SCI by -64.9%."
        ),
        "verification": "PASS - 100% Exact SHA-256 Output Match across 2,500,000 production records.",
    },
]


# ---------------------------------------------------------------------------
# Custom Scoped CSS for Tab 3 Cards, Frosted Locked Overlays & Badges
# ---------------------------------------------------------------------------
def _inject_roadmap_css() -> None:
    st.markdown(
        """
        <style>
        .rm-section-card {
            background-color: #111827;
            border: 1px solid #1F2937;
            border-radius: 12px;
            padding: 18px 20px;
            margin-bottom: 16px;
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.35);
        }
        .rm-phase-card {
            background: linear-gradient(145deg, #111827 0%, #0B0F19 100%);
            border: 1px solid #1F2937;
            border-radius: 12px;
            padding: 16px 18px;
            height: 100%;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        }
        .rm-action-card {
            background: linear-gradient(145deg, #111827 0%, #0D1526 100%);
            border: 1px solid #1F2937;
            border-top: 3px solid #10B981;
            border-radius: 12px;
            padding: 16px 18px;
            height: 100%;
            box-shadow: 0 6px 16px rgba(0, 0, 0, 0.35);
        }
        .rm-hw-unlocked-card {
            background: linear-gradient(145deg, #111827 0%, #0F172A 100%);
            border: 1px solid #1F2937;
            border-left: 4px solid #06B6D4;
            border-radius: 12px;
            padding: 16px 18px;
            margin-bottom: 10px;
            box-shadow: 0 4px 14px rgba(0, 0, 0, 0.32);
        }
        .rm-hw-locked-wrapper {
            position: relative;
            background: linear-gradient(145deg, #111827 0%, #0B0F19 100%);
            border: 1px dashed #374151;
            border-radius: 12px;
            padding: 18px 20px;
            margin-bottom: 14px;
            overflow: hidden;
            min-height: 215px;
        }
        .rm-hw-locked-blur {
            filter: blur(3.6px);
            -webkit-filter: blur(3.6px);
            opacity: 0.38;
            user-select: none;
            pointer-events: none;
        }
        .rm-hw-locked-overlay {
            position: absolute;
            inset: 0;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            background: rgba(11, 15, 25, 0.62);
            backdrop-filter: blur(2px);
            -webkit-backdrop-filter: blur(2px);
            padding: 16px;
            text-align: center;
            z-index: 2;
        }
        .rm-lock-badge {
            display: inline-block;
            background: rgba(245, 158, 11, 0.18);
            color: #FBBF24;
            border: 1px solid rgba(245, 158, 11, 0.55);
            border-radius: 999px;
            padding: 6px 16px;
            font-size: 0.84rem;
            font-weight: 700;
            letter-spacing: 0.02em;
            margin-bottom: 8px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.45);
        }
        .rm-owner-pill {
            display: inline-block;
            background: rgba(6, 182, 212, 0.12);
            color: #22D3EE;
            border: 1px solid rgba(6, 182, 212, 0.35);
            border-radius: 999px;
            padding: 2px 9px;
            font-size: 0.72rem;
            font-weight: 600;
            margin: 2px 4px 2px 0;
        }
        .rm-status-unlocked {
            display: inline-block;
            background: rgba(16, 185, 129, 0.15);
            color: #10B981;
            border: 1px solid rgba(16, 185, 129, 0.4);
            border-radius: 999px;
            padding: 2px 10px;
            font-size: 0.73rem;
            font-weight: 700;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Proposal & Bill of Materials CSV Builder
# ---------------------------------------------------------------------------
def _build_proposal_bom_csv(
    fin: Dict[str, Any],
    currency: str,
    hw_catalog: Dict[str, Dict[str, Any]],
) -> str:
    """
    Build a comprehensive CSV containing:
    1. Tier 1 Itemized 12-Week Pilot Budget (all 6 categories)
    2. Phase-2 Hardware Upgrades (unlocked vs locked status + CapEx)
    3. Appendix B Financial Summary & 3-Year Cash-Flow Schedule
    """
    fx = USD_TO_INR if currency == "USD ($)" else 1.0
    curr_code = "USD" if currency == "USD ($)" else "INR"
    tier_key = fin["tier_key"]
    tier_num = int(tier_key.split()[-1])

    rows: List[Dict[str, Any]] = []

    # 1. Pilot Budget Line Items
    for item_name, cost_inr in TIER1_PILOT_BUDGET_INR.items():
        meta = PILOT_BUDGET_DETAILS.get(item_name, {})
        rows.append(
            {
                "Section": "Section A: Tier 1 12-Week Pilot Budget",
                "Line Item / Metric": item_name,
                "Category / Workstream": meta.get("workstream", "12-Week PoC"),
                "Lead Owner": meta.get("owner", "WAS Group 2"),
                "Status": "INCLUDED (Tier 1 Base PoC)",
                "Canonical Amount (INR)": round(float(cost_inr), 2),
                f"Active Amount ({curr_code})": round(float(cost_inr) / fx, 2),
                "Notes / Billing Schedule": meta.get("billing_milestone", ""),
            }
        )

    rows.append(
        {
            "Section": "Section A: Subtotal",
            "Line Item / Metric": "Total Tier 1 Pilot Investment (12-Week PoC)",
            "Category / Workstream": "Fixed-Fee PoC Total",
            "Lead Owner": "M1 · Adithya & M4 · Faizan (Finance)",
            "Status": "INCLUDED",
            "Canonical Amount (INR)": round(float(fin["pilot_budget_inr"]), 2),
            f"Active Amount ({curr_code})": round(float(fin["pilot_budget"]), 2),
            "Notes / Billing Schedule": "40% Week 4 / 30% Week 8 / 30% Week 12",
        }
    )

    # 2. Unlocked Software Advisory Actions
    for act in UNLOCKED_ADVISORY_ACTIONS:
        est_saving_inr = fin["annual_gross_saving_inr"] * act["share_of_tier1_savings"]
        rows.append(
            {
                "Section": "Section A: Unlocked Software Advisory Action",
                "Line Item / Metric": act["title"],
                "Category / Workstream": act["workstream"],
                "Lead Owner": act["owner"],
                "Status": "UNLOCKED (Zero Hardware CapEx)",
                "Canonical Amount (INR)": round(est_saving_inr, 2),
                f"Active Amount ({curr_code})": round(est_saving_inr / fx, 2),
                "Notes / Billing Schedule": f"Est. Annual Gross Saving Share ({act['share_of_tier1_savings']*100:.0f}%) | {act['verification']}",
            }
        )

    # 3. Phase-2 Hardware BoM Items
    hw_items_inr = fin.get("hardware_line_items_inr", {})
    scale_factor = fin.get("facility_scale_factor", 1.0)
    for hw_name, hw_meta in hw_catalog.items():
        req_tier = int(hw_meta["min_tier"])
        is_unlocked = tier_num >= req_tier
        if is_unlocked:
            item_inr = float(
                hw_items_inr.get(
                    hw_name, round(hw_meta["ref_cost_inr"] * scale_factor, -3)
                )
            )
            status_str = f"UNLOCKED (Tier {req_tier}+ Included)"
        else:
            item_inr = 0.0
            status_str = f"LOCKED (Requires Tier {req_tier})"

        rows.append(
            {
                "Section": "Section B: Phase-2 Hardware BoM",
                "Line Item / Metric": hw_name,
                "Category / Workstream": hw_meta["category"],
                "Lead Owner": "M2 · Sankarshana & M3 · Samiksha (Delivery/QA)",
                "Status": status_str,
                "Canonical Amount (INR)": round(item_inr, 2),
                f"Active Amount ({curr_code})": round(item_inr / fx, 2),
                "Notes / Billing Schedule": hw_meta["impact"],
            }
        )

    rows.append(
        {
            "Section": "Section B: Subtotal",
            "Line Item / Metric": "Total Unlocked Phase-2 Hardware CapEx",
            "Category / Workstream": "Phase-2 Physical Infrastructure",
            "Lead Owner": "M4 · Faizan (Finance)",
            "Status": "INCLUDED" if tier_num >= 2 else "LOCKED IN TIER 1",
            "Canonical Amount (INR)": round(float(fin["hardware_capex_inr"]), 2),
            f"Active Amount ({curr_code})": round(float(fin["hardware_capex"]), 2),
            "Notes / Billing Schedule": f"Scaled for {fin['avg_facility_mw']:.2f} MW facility (scale factor {scale_factor:.2f}x)",
        }
    )

    # 4. Financial & Thermodynamic Summary Schedule
    summary_metrics = [
        (
            "Total Initial Program Cost (Pilot + Active Hardware CapEx)",
            fin["initial_cost_inr"],
            fin["initial_cost"],
            f"Active Tier: {fin['selected_tier']}",
        ),
        (
            "Baseline Annual Electricity Cost",
            fin["baseline_annual_cost"] * fin["fx_rate"],
            fin["baseline_annual_cost"],
            f"{fin['baseline_kwh']:,.0f} kWh/yr @ Tariff {fin['tariff_inr']:.2f} INR/kWh",
        ),
        (
            "Annual Gross Energy Saving",
            fin["annual_gross_saving_inr"],
            fin["annual_gross_saving"],
            f"{fin['annual_kwh_saved']:,.0f} kWh/yr saved (-{fin['reduction_pct']:.1f}%)",
        ),
        (
            "Annual Recurring Solution OpEx",
            fin["recurring_opex_inr"],
            fin["recurring_opex"],
            "Ongoing cloud telemetry, model retraining & calibration",
        ),
        (
            "Annual Net Financial Benefit (Gross Saving - OpEx)",
            fin["annual_net_benefit_inr"],
            fin["annual_net_benefit"],
            f"Simple Payback: {fin['simple_payback_display']} | Annual ROI: {fin['annual_roi_pct']:.1f}%",
        ),
        (
            "3-Year Cumulative Net Cash Flow (3x Net Benefit - Initial Cost)",
            (3.0 * fin["annual_net_benefit_inr"]) - fin["initial_cost_inr"],
            (3.0 * fin["annual_net_benefit"]) - fin["initial_cost"],
            f"Projected PUE: {fin['baseline_pue']:.2f} -> {fin['projected_pue']:.2f} | Scope 2 Avoided: {fin['co2_avoided_efficiency_tonnes']:.1f} tCO2e/yr",
        ),
    ]

    for label, val_inr, val_curr, note in summary_metrics:
        rows.append(
            {
                "Section": "Section C: Executive Financial & ROI Schedule",
                "Line Item / Metric": label,
                "Category / Workstream": "Appendix B Financial Model",
                "Lead Owner": "M4 · Faizan (Finance)",
                "Status": "ACTIVE SCENARIO",
                "Canonical Amount (INR)": round(float(val_inr), 2),
                f"Active Amount ({curr_code})": round(float(val_curr), 2),
                "Notes / Billing Schedule": note,
            }
        )

    export_df = pd.DataFrame(rows)
    return export_df.to_csv(index=False)


# ---------------------------------------------------------------------------
# Main Tab 3 Renderer
# ---------------------------------------------------------------------------
def render_tab_roadmap(
    sim: Dict[str, Any], params: Optional[Dict[str, Any]] = None
) -> None:
    """
    Render Tab 3: Optimization Roadmap, Tier 1 Itemized 12-Week Pilot Budget,
    Unlocked Software Advisory Actions, and Interactive Phase-2 Hardware CapEx Simulator.
    """
    _inject_roadmap_css()
    params = params or {}
    fin_in = sim["financials"]

    # Extract active simulation parameters (preferring `params` if provided, falling back to `fin_in`)
    selected_tier: str = str(
        params.get("selected_tier", fin_in.get("selected_tier", "Tier 1"))
    )
    tier_key: str = normalize_tier_key(selected_tier)
    tier_num: int = int(tier_key.split()[-1])

    baseline_kwh: float = float(
        params.get("baseline_kwh", fin_in.get("baseline_kwh", 1_200_000.0))
    )
    reduction_pct: float = float(
        params.get(
            "reduction_pct",
            params.get("target_reduction_pct", fin_in.get("reduction_pct", 5.0)),
        )
    )
    baseline_pue: float = float(
        params.get("baseline_pue", fin_in.get("baseline_pue", 1.65))
    )
    currency: str = str(params.get("currency", fin_in.get("currency", "INR (₹)")))
    tariff: float = float(params.get("tariff", fin_in.get("tariff", 8.50)))
    recurring_opex: float = float(
        params.get("recurring_opex", fin_in.get("recurring_opex", 120_000.0))
    )
    grid_region: str = str(
        params.get(
            "grid_region",
            fin_in.get(
                "grid_region",
                "India - Southern Grid / Bengaluru (0.71 kgCO2/kWh)",
            ),
        )
    )

    is_usd = currency == "USD ($)"
    fx_rate = USD_TO_INR if is_usd else 1.0

    # Initialize canonical session state dictionary for per-item hardware CapEx overrides (in INR)
    st.session_state.setdefault("hw_capex_overrides", {})
    hw_overrides: Dict[str, float] = st.session_state["hw_capex_overrides"]

    # Compute baseline default hardware items for the current facility scale factor
    scale_factor = float(fin_in.get("facility_scale_factor", 1.0))

    # Recompute financials dynamically with any current session_state["hw_capex_overrides"]
    fin = compute_financials_and_thermodynamics(
        selected_tier=selected_tier,
        baseline_kwh=baseline_kwh,
        reduction_pct=reduction_pct,
        baseline_pue=baseline_pue,
        currency=currency,
        tariff=tariff,
        recurring_opex=recurring_opex,
        grid_region=grid_region,
        hw_capex_overrides=hw_overrides,
    )
    sim["financials"] = fin

    # Keep total hardware_capex_override_inr synchronized for app.py compatibility
    if tier_key == "Tier 1":
        st.session_state["hardware_capex_override_inr"] = None
    else:
        st.session_state["hardware_capex_override_inr"] = float(
            fin["hardware_capex_inr"]
        )

    # -----------------------------------------------------------------------
    # Top Executive Banner & Action Bar (with CSV Export)
    # -----------------------------------------------------------------------
    hdr_col, dl_col = st.columns([3.2, 1.2])
    with hdr_col:
        st.markdown(
            f"""
            <div style="margin-bottom: 6px;">
                <span class="gc-badge-emerald">SECTION 8.1 & APPENDIX B</span>
                <span class="gc-badge-cyan">{tier_key.upper()} ACTIVE</span>
                <h3 style="margin: 6px 0 4px 0; color: #F9FAFB; font-size: 1.35rem;">
                    Phased Consulting Roadmap, 12-Week Pilot Budget & Interactive CapEx BoM
                </h3>
                <div style="color: #9CA3AF; font-size: 0.86rem;">
                    Fixed-Fee 12-Week PoC (<strong>{_format_currency(fin['pilot_budget_inr'], currency)}</strong>)
                    + Tier-Unlocked Phase-2 Hardware CapEx (<strong>{_format_currency(fin['hardware_capex_inr'], currency)}</strong>)
                    · Total Initial Investment: <strong>{_format_currency(fin['initial_cost_inr'], currency)}</strong>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Note: We render the CSV download button at the top AND keep it synced after slider updates
    csv_header_placeholder = dl_col.empty()

    # =======================================================================
    # SECTION A: Tier 1 Itemized 12-Week Pilot Budget, Phased Roadmap & Actions
    # =======================================================================
    st.markdown(
        """
        <div class="rm-section-card" style="border-left: 4px solid #10B981; margin-top: 8px;">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
                <div>
                    <span class="rm-status-unlocked">✔ UNLOCKED IN ALL TIERS · SECTION 8.1 BASELINE POC</span>
                    <h4 style="margin: 6px 0 2px 0; color: #F9FAFB; font-size: 1.12rem;">
                        Section A · Tier 1 Itemized 12-Week Pilot Budget & Unlocked Software Advisory Actions
                    </h4>
                    <div style="color: #9CA3AF; font-size: 0.83rem;">
                        Non-invasive telemetry instrumentation, ML forecasting/anomaly models, and Python workload refactoring delivered over 12 weeks.
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # --- A1: Itemized ₹8,20,000 Pilot Budget Table + Visual Allocation Chart ---
    budget_rows: List[Dict[str, Any]] = []
    total_pilot_inr = float(sum(TIER1_PILOT_BUDGET_INR.values()))

    for category, inr_val in TIER1_PILOT_BUDGET_INR.items():
        details = PILOT_BUDGET_DETAILS.get(category, {})
        share_pct = (inr_val / total_pilot_inr) * 100.0
        row_dict: Dict[str, Any] = {
            "Budget Line Item": category,
            "Workstream & Scope": details.get("workstream", ""),
            "Lead Owner": details.get("owner", ""),
            "Key Deliverable": details.get("deliverable", ""),
            "Billing Milestone": details.get("billing_milestone", ""),
            "Share (%)": f"{share_pct:.1f}%",
            "Budget (INR ₹)": _format_inr(inr_val),
        }
        if is_usd:
            row_dict["Budget (USD $ @ ₹84)"] = _format_currency(
                inr_val, "USD ($)", decimals=0
            )
        budget_rows.append(row_dict)

    # Append Total Row
    total_row: Dict[str, Any] = {
        "Budget Line Item": "TOTAL 12-WEEK PILOT BUDGET",
        "Workstream & Scope": "Complete Tier 1 PoC Engagement",
        "Lead Owner": "M1 · Adithya & M4 · Faizan (Finance)",
        "Key Deliverable": "Validated Telemetry, ML Pipeline, Refactored Code & CFO Handover Pack",
        "Billing Milestone": "100% Fixed-Fee PoC",
        "Share (%)": "100.0%",
        "Budget (INR ₹)": _format_inr(total_pilot_inr),
    }
    if is_usd:
        total_row["Budget (USD $ @ ₹84)"] = _format_currency(
            total_pilot_inr, "USD ($)", decimals=0
        )
    budget_rows.append(total_row)

    budget_df = pd.DataFrame(budget_rows)

    tbl_col, chart_col = st.columns([1.65, 1.0])
    with tbl_col:
        st.markdown(
            f"**1. Tier 1 Itemized 12-Week Pilot Budget Breakdown ({_format_currency(total_pilot_inr, currency)})**"
        )
        st.dataframe(budget_df, use_container_width=True, hide_index=True)
        st.caption(
            "📌 **Currency Scaling Note:** Canonical Pilot Budget is **₹8,20,000** (Section 8.1 / Appendix B), "
            f"converted at fixed **1 USD = ₹{USD_TO_INR:.0f}** (**{_format_currency(total_pilot_inr, 'USD ($)', decimals=0)}** in USD mode)."
        )

    with chart_col:
        st.markdown("**Pilot Budget Allocation by Category**")
        cat_names = list(TIER1_PILOT_BUDGET_INR.keys())
        cat_vals_active = [v / fx_rate for v in TIER1_PILOT_BUDGET_INR.values()]
        cat_labels = [
            f"{_format_currency(v, currency)} ({(v / total_pilot_inr) * 100:.1f}%)"
            for v in TIER1_PILOT_BUDGET_INR.values()
        ]
        colors = ["#10B981", "#06B6D4", "#3B82F6", "#8B5CF6", "#F59E0B", "#64748B"]

        fig_pilot = go.Figure(
            go.Bar(
                y=cat_names[::-1],
                x=cat_vals_active[::-1],
                orientation="h",
                text=cat_labels[::-1],
                textposition="auto",
                marker=dict(color=colors[::-1], line=dict(color="#1F2937", width=1)),
                hovertemplate="<b>%{y}</b><br>Allocation: %{text}<extra></extra>",
            )
        )
        fig_pilot.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(17, 24, 39, 0.85)",
            plot_bgcolor="rgba(17, 24, 39, 0.4)",
            margin=dict(l=10, r=15, t=12, b=12),
            height=295,
            xaxis=dict(
                title=f"Allocation ({'USD $' if is_usd else 'INR ₹'})",
                showgrid=True,
                gridcolor="#1F2937",
            ),
            yaxis=dict(title="", showgrid=False),
            font=dict(color="#F9FAFB", size=11),
        )
        st.plotly_chart(fig_pilot, use_container_width=True)

    # --- A2: 12-Week Phased Consulting Roadmap & Milestone Billing Schedule ---
    st.markdown("#### 2. 12-Week Phased Consulting Roadmap & Milestone Billing Schedule")
    phase_cols = st.columns(3)
    for idx, phase in enumerate(ROADMAP_PHASES):
        milestone_inr = total_pilot_inr * phase["pct_allocation"]
        milestone_str = _format_currency(milestone_inr, currency)
        owner_badges_html = "".join(
            f'<span class="rm-owner-pill">{o}</span>' for o in phase["owners"]
        )
        activities_html = "".join(
            f'<li style="margin-bottom: 5px; color: #D1D5DB; font-size: 0.81rem;">{act}</li>'
            for act in phase["key_activities"]
        )
        with phase_cols[idx]:
            st.markdown(
                f"""
                <div class="rm-phase-card" style="border-top: 4px solid {phase['accent']};">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                        <span style="color: {phase['accent']}; font-size: 0.78rem; font-weight: 700; text-transform: uppercase;">
                            {phase['phase']}
                        </span>
                        <span style="background: rgba(255,255,255,0.06); color: #F9FAFB; padding: 2px 8px; border-radius: 6px; font-size: 0.76rem; font-weight: 700;">
                            {milestone_str} ({int(phase['pct_allocation']*100)}%)
                        </span>
                    </div>
                    <div style="font-size: 1.05rem; font-weight: 700; color: #F9FAFB; margin-bottom: 4px;">
                        {phase['title']}
                    </div>
                    <div style="font-size: 0.76rem; color: #9CA3AF; margin-bottom: 8px;">
                        💳 <strong>{phase['milestone']}</strong>
                    </div>
                    <div style="margin-bottom: 10px;">
                        {owner_badges_html}
                    </div>
                    <ul style="padding-left: 16px; margin: 0 0 10px 0;">
                        {activities_html}
                    </ul>
                    <div style="background: rgba(16, 185, 129, 0.08); border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 8px; padding: 6px 10px; font-size: 0.75rem; color: #A7F3D0;">
                        🏁 <strong>{phase['exit_gate']}</strong>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    # --- A3: 3 Unlocked Workstream A/B Advisory Action Cards ---
    st.markdown(
        "#### 3. Unlocked Workstream A & B Software Advisory Actions (Zero Hardware CapEx)"
    )
    act_cols = st.columns(3)
    for idx, act in enumerate(UNLOCKED_ADVISORY_ACTIONS):
        est_kwh = fin["annual_kwh_saved"] * act["share_of_tier1_savings"]
        est_saving_inr = fin["annual_gross_saving_inr"] * act["share_of_tier1_savings"]
        est_co2_t = fin["co2_avoided_efficiency_tonnes"] * act["share_of_tier1_savings"]

        with act_cols[idx]:
            st.markdown(
                f"""
                <div class="rm-action-card">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                        <span class="rm-status-unlocked">✔ UNLOCKED · {act['id']}</span>
                        <span style="color: #06B6D4; font-size: 0.75rem; font-weight: 600;">{act['confidence']}</span>
                    </div>
                    <div style="font-size: 1.04rem; font-weight: 700; color: #F9FAFB; margin-bottom: 4px;">
                        {act['title']}
                    </div>
                    <div style="font-size: 0.76rem; color: #9CA3AF; margin-bottom: 8px;">
                        {act['workstream']} · <strong>{act['owner']}</strong>
                    </div>
                    <p style="color: #D1D5DB; font-size: 0.81rem; line-height: 1.42; margin-bottom: 10px;">
                        {act['summary']}
                    </p>
                    <div style="background: rgba(15, 23, 42, 0.85); border: 1px solid #1F2937; border-radius: 8px; padding: 8px 10px; margin-bottom: 8px; font-size: 0.78rem;">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 3px;">
                            <span style="color: #9CA3AF;">Attributed Energy Saving:</span>
                            <strong style="color: #10B981;">{est_kwh:,.0f} kWh/yr ({int(act['share_of_tier1_savings']*100)}%)</strong>
                        </div>
                        <div style="display: flex; justify-content: space-between; margin-bottom: 3px;">
                            <span style="color: #9CA3AF;">Attributed Cost Saving:</span>
                            <strong style="color: #F9FAFB;">{_format_currency(est_saving_inr, currency)}/yr</strong>
                        </div>
                        <div style="display: flex; justify-content: space-between;">
                            <span style="color: #9CA3AF;">Scope 2 CO₂ Abatement:</span>
                            <strong style="color: #22D3EE;">{est_co2_t:,.1f} tCO₂e/yr</strong>
                        </div>
                    </div>
                    <div style="font-size: 0.74rem; color: #A7F3D0;">
                        ✅ <strong>QA Gate:</strong> {act['verification']}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.divider()

    # =======================================================================
    # SECTION B: 4 Phase-2 Hardware Upgrades (Interactive CapEx BoM Simulator)
    # =======================================================================
    st.markdown(
        f"""
        <div class="rm-section-card" style="border-left: 4px solid #06B6D4;">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
                <div>
                    <span class="gc-badge-cyan">SECTION B · INTERACTIVE CAPEX BOM SIMULATOR</span>
                    <span class="gc-badge-amber">FACILITY SCALE: {fin['avg_facility_mw']:.2f} MW ({scale_factor:.2f}x REF)</span>
                    <h4 style="margin: 6px 0 2px 0; color: #F9FAFB; font-size: 1.12rem;">
                        Section B · Phase-2 Hardware Upgrades (Interactive CapEx & Payback Simulator)
                    </h4>
                    <div style="color: #9CA3AF; font-size: 0.83rem;">
                        Adjust unlocked Phase-2 hardware CapEx sliders below to stress-test supplier quotes.
                        Initial Cost, Simple Payback (Months), and Annual ROI (%) synchronize immediately across the dashboard.
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Reset button for unlocked hardware overrides when in Tier 2 or Tier 3
    if tier_num >= 2:
        rst_col1, rst_col2 = st.columns([3.4, 1.0])
        with rst_col1:
            st.caption(
                f"💡 **Interactive CapEx Mode Active ({tier_key}):** Move any unlocked hardware slider below to override its CapEx in **{currency}**. "
                "Canonical INR values are persisted in `st.session_state['hw_capex_overrides']`."
            )
        with rst_col2:
            if st.button(
                "↺ Reset Hardware CapEx to Defaults",
                use_container_width=True,
                key="btn_reset_hw_capex",
            ):
                st.session_state["hw_capex_overrides"] = {}
                for hw_idx in range(len(PHASE2_HARDWARE_CATALOG_INR)):
                    for suffix in ("inr", "usd"):
                        w_key = f"hw_slider_{hw_idx}_{suffix}"
                        if w_key in st.session_state:
                            del st.session_state[w_key]
                st.session_state["hardware_capex_override_inr"] = None
                st.rerun()
    else:
        st.info(
            "🔒 **Tier 1 (Visibility & Software Advisory PoC) Active:** All 4 Phase-2 physical hardware upgrades are shown below as locked preview cards (`₹0` Hardware CapEx). "
            "Switch to **Tier 2** or **Tier 3** in the left sidebar to unlock interactive CapEx sliders."
        )

    # Render the 4 Phase-2 Hardware Upgrade Cards in a 2x2 Grid
    hw_items = list(PHASE2_HARDWARE_CATALOG_INR.items())
    grid_row1 = st.columns(2)
    grid_row2 = st.columns(2)
    grid_slots = [grid_row1[0], grid_row1[1], grid_row2[0], grid_row2[1]]

    updated_overrides: Dict[str, float] = dict(
        st.session_state.get("hw_capex_overrides", {})
    )

    for idx, (item_name, item_meta) in enumerate(hw_items):
        min_tier_req = int(item_meta["min_tier"])
        is_unlocked = tier_num >= min_tier_req

        # Facility-scaled reference cost in INR, clamped to catalog slider bounds
        scaled_default_inr = float(
            round(item_meta["ref_cost_inr"] * scale_factor, -3)
        )
        min_inr = float(item_meta["min_slider_inr"])
        max_inr = float(
            max(item_meta["max_slider_inr"], scaled_default_inr * 1.5)
        )
        scaled_default_inr = max(min_inr, min(scaled_default_inr, max_inr))

        current_inr = float(
            updated_overrides.get(item_name, scaled_default_inr)
        )
        current_inr = max(min_inr, min(current_inr, max_inr))

        with grid_slots[idx]:
            if is_unlocked:
                # UNLOCKED HARDWARE CARD WITH INTERACTIVE CAPEX SLIDER
                delta_vs_ref_inr = current_inr - scaled_default_inr
                delta_tag = (
                    "Default Scaled Reference"
                    if abs(delta_vs_ref_inr) < 500
                    else f"{'+' if delta_vs_ref_inr > 0 else ''}{_format_currency(delta_vs_ref_inr, currency)} vs. Ref"
                )
                st.markdown(
                    f"""
                    <div class="rm-hw-unlocked-card">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                            <span class="rm-status-unlocked">🔓 UNLOCKED · TIER {min_tier_req}+ MODULE</span>
                            <span class="gc-badge-cyan">{item_meta['category']}</span>
                        </div>
                        <div style="font-size: 1.03rem; font-weight: 700; color: #F9FAFB; margin-bottom: 4px;">
                            {idx + 1}. {item_name}
                        </div>
                        <div style="color: #D1D5DB; font-size: 0.81rem; margin-bottom: 8px;">
                            {item_meta['impact']}
                        </div>
                        <div style="display: flex; justify-content: space-between; align-items: baseline; background: rgba(11, 15, 25, 0.75); border: 1px solid #1F2937; border-radius: 8px; padding: 8px 12px;">
                            <div>
                                <div style="color: #9CA3AF; font-size: 0.72rem; text-transform: uppercase;">Active Item CapEx</div>
                                <div style="color: #10B981; font-size: 1.15rem; font-weight: 700;">
                                    {_format_currency(current_inr, currency)}
                                </div>
                            </div>
                            <div style="text-align: right;">
                                <div style="color: #9CA3AF; font-size: 0.72rem;">Ref Cost (2.0 MW): {_format_currency(item_meta['ref_cost_inr'], currency)}</div>
                                <div style="color: #22D3EE; font-size: 0.76rem; font-weight: 600;">{delta_tag}</div>
                            </div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                if not is_usd:
                    slider_val_inr = st.slider(
                        f"Adjust CapEx (₹) — {item_name}",
                        min_value=int(min_inr),
                        max_value=int(max_inr),
                        value=int(round(current_inr, -3)),
                        step=10_000,
                        key=f"hw_slider_{idx}_inr",
                        help=f"Override Phase-2 CapEx for '{item_name}'. Reference 2.0 MW cost: {_format_inr(item_meta['ref_cost_inr'])}.",
                    )
                    new_item_inr = float(slider_val_inr)
                else:
                    min_usd = int(round(min_inr / USD_TO_INR))
                    max_usd = int(round(max_inr / USD_TO_INR))
                    default_usd = int(round(current_inr / USD_TO_INR))
                    default_usd = max(min_usd, min(default_usd, max_usd))
                    slider_val_usd = st.slider(
                        f"Adjust CapEx ($) — {item_name}",
                        min_value=min_usd,
                        max_value=max_usd,
                        value=default_usd,
                        step=100,
                        key=f"hw_slider_{idx}_usd",
                        help=f"Override Phase-2 CapEx for '{item_name}' in USD (1 USD = ₹84).",
                    )
                    new_item_inr = float(slider_val_usd) * USD_TO_INR

                updated_overrides[item_name] = new_item_inr
            else:
                # LOCKED HARDWARE CARD: FROSTED / BLURRED CSS PREVIEW WITH UPGRADE BADGE
                if tier_key == "Tier 1":
                    badge_text = (
                        "🔒 Upgrade to Tier 2/3 to Unlock"
                        if min_tier_req == 2
                        else "🔒 Upgrade to Tier 3 to Unlock"
                    )
                else:
                    badge_text = "🔒 Upgrade to Tier 3 to Unlock"

                st.markdown(
                    f"""
                    <div class="rm-hw-locked-wrapper">
                        <div class="rm-hw-locked-blur">
                            <div style="display: flex; justify-content: space-between; margin-bottom: 6px;">
                                <span class="gc-badge-cyan">{item_meta['category']}</span>
                                <span style="color: #9CA3AF; font-size: 0.78rem;">Tier {min_tier_req} Hardware Module</span>
                            </div>
                            <div style="font-size: 1.05rem; font-weight: 700; color: #F9FAFB; margin-bottom: 6px;">
                                {idx + 1}. {item_name}
                            </div>
                            <p style="color: #D1D5DB; font-size: 0.82rem; margin-bottom: 12px;">
                                {item_meta['impact']}
                            </p>
                            <div style="background: #0B0F19; border: 1px solid #1F2937; border-radius: 8px; padding: 10px;">
                                <div style="color: #9CA3AF; font-size: 0.75rem;">Reference CapEx Estimate: {_format_currency(scaled_default_inr, currency)}</div>
                                <div style="height: 8px; background: #1F2937; border-radius: 4px; margin-top: 8px; width: 65%;"></div>
                            </div>
                        </div>
                        <div class="rm-hw-locked-overlay">
                            <span class="rm-lock-badge">{badge_text}</span>
                            <div style="color: #F9FAFB; font-weight: 700; font-size: 0.96rem; margin-bottom: 4px;">
                                {idx + 1}. {item_name}
                            </div>
                            <div style="color: #D1D5DB; font-size: 0.79rem; max-width: 90%; margin-bottom: 6px;">
                                {item_meta['impact']}
                            </div>
                            <div style="color: #9CA3AF; font-size: 0.75rem;">
                                Est. Scaled CapEx when unlocked: <strong>{_format_currency(scaled_default_inr, currency)}</strong>
                                (Excluded from {tier_key} CapEx)
                            </div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    # Persist updated overrides into st.session_state["hw_capex_overrides"] and recompute immediately
    st.session_state["hw_capex_overrides"] = updated_overrides

    fin = compute_financials_and_thermodynamics(
        selected_tier=selected_tier,
        baseline_kwh=baseline_kwh,
        reduction_pct=reduction_pct,
        baseline_pue=baseline_pue,
        currency=currency,
        tariff=tariff,
        recurring_opex=recurring_opex,
        grid_region=grid_region,
        hw_capex_overrides=st.session_state["hw_capex_overrides"],
    )
    sim["financials"] = fin

    if tier_key == "Tier 1":
        st.session_state["hardware_capex_override_inr"] = None
    else:
        st.session_state["hardware_capex_override_inr"] = float(
            fin["hardware_capex_inr"]
        )

    # Populate the top CSV Download Button with the live synchronized `fin` dictionary
    csv_payload = _build_proposal_bom_csv(
        fin=fin,
        currency=currency,
        hw_catalog=PHASE2_HARDWARE_CATALOG_INR,
    )
    tier_slug = tier_key.lower().replace(" ", "_")
    curr_slug = "usd" if is_usd else "inr"
    with csv_header_placeholder:
        st.download_button(
            label="Download Client Proposal & BoM (CSV)",
            data=csv_payload,
            file_name=f"greencompute_{tier_slug}_proposal_bom_{curr_slug}.csv",
            mime="text/csv",
            use_container_width=True,
            key="dl_client_proposal_bom_csv",
        )

    # -----------------------------------------------------------------------
    # Live Synchronized CapEx, Payback & ROI Strip + 36-Month Cash-Flow Chart
    # -----------------------------------------------------------------------
    st.markdown(
        "#### Live Synchronized Investment, Payback & ROI Summary (Appendix B Formulas)"
    )

    hw_delta_inr = fin["hardware_capex_inr"] - fin["default_hardware_capex_inr"]
    hw_delta_label = (
        "Default Scaled BoM"
        if abs(hw_delta_inr) < 500
        else f"{'+' if hw_delta_inr > 0 else ''}{_format_currency(hw_delta_inr, currency)} vs. Default"
    )

    m_cols = st.columns(5)
    with m_cols[0]:
        st.metric(
            "Tier 1 Pilot Budget",
            _format_currency(fin["pilot_budget_inr"], currency),
            "12-Week Fixed-Fee PoC",
        )
    with m_cols[1]:
        st.metric(
            "Unlocked Phase-2 CapEx",
            _format_currency(fin["hardware_capex_inr"], currency),
            hw_delta_label,
        )
    with m_cols[2]:
        st.metric(
            "Total Initial Cost",
            _format_currency(fin["initial_cost_inr"], currency),
            f"Pilot + {tier_key} Hardware",
        )
    with m_cols[3]:
        st.metric(
            "Simple Payback",
            fin["simple_payback_display"],
            f"Net Benefit: {_format_currency(fin['annual_net_benefit_inr'], currency)}/yr",
            delta_color="normal"
            if fin["annual_net_benefit_inr"] > 0
            else "inverse",
        )
    with m_cols[4]:
        st.metric(
            "Annual ROI (%)",
            f"{fin['annual_roi_pct']:.1f}%",
            f"Gross: {_format_currency(fin['annual_gross_saving_inr'], currency)}/yr",
            delta_color="normal" if fin["annual_roi_pct"] > 0 else "inverse",
        )

    # 36-Month Cumulative Net Cash Flow & Breakeven Trajectory
    months = list(range(0, 37))
    monthly_net_active = fin["annual_net_benefit"] / 12.0
    init_cost_active = fin["initial_cost"]
    cum_cashflow = [-init_cost_active + (m * monthly_net_active) for m in months]

    cf_col, bom_sum_col = st.columns([1.45, 1.0])
    with cf_col:
        fig_cf = go.Figure()
        fig_cf.add_hline(
            y=0,
            line_dash="dash",
            line_color="#9CA3AF",
            annotation_text="Breakeven Threshold (0)",
            annotation_position="top left",
        )
        fig_cf.add_trace(
            go.Scatter(
                x=months,
                y=cum_cashflow,
                mode="lines+markers",
                name="Cumulative Net Cash Flow",
                line=dict(color="#10B981", width=3),
                marker=dict(size=5, color="#06B6D4"),
                fill="tozeroy",
                fillcolor="rgba(16, 185, 129, 0.12)",
                hovertemplate="Month %{x}<br>Cumulative Cash Flow: %{y:,.0f}<extra></extra>",
            )
        )
        if (
            fin["simple_payback_months"] is not None
            and 0 < fin["simple_payback_months"] <= 36
        ):
            fig_cf.add_vline(
                x=fin["simple_payback_months"],
                line_dash="dot",
                line_color="#F59E0B",
                annotation_text=f"Payback: {fin['simple_payback_months']:.1f} mo",
                annotation_position="bottom right",
            )

        fig_cf.update_layout(
            title=dict(
                text=f"36-Month Cumulative Cash Flow & Breakeven Trajectory ({'USD $' if is_usd else 'INR ₹'})",
                font=dict(size=13, color="#F9FAFB"),
            ),
            template="plotly_dark",
            paper_bgcolor="rgba(17, 24, 39, 0.85)",
            plot_bgcolor="rgba(17, 24, 39, 0.4)",
            margin=dict(l=15, r=15, t=38, b=15),
            height=280,
            xaxis=dict(
                title="Months Post-Deployment",
                gridcolor="#1F2937",
                dtick=6,
            ),
            yaxis=dict(
                title=f"Cumulative Cash Flow ({'USD $' if is_usd else 'INR ₹'})",
                gridcolor="#1F2937",
            ),
            font=dict(color="#F9FAFB", size=11),
            showlegend=False,
        )
        st.plotly_chart(fig_cf, use_container_width=True)

    with bom_sum_col:
        st.markdown("**Active Program Bill of Materials (BoM) Summary**")
        bom_summary_rows: List[Dict[str, str]] = [
            {
                "Component": "Tier 1 Pilot Budget (12-Week PoC)",
                "Tier Scope": "Tier 1 Base",
                "Status": "✔ Included",
                "Cost": _format_currency(fin["pilot_budget_inr"], currency),
            }
        ]
        for hw_name, hw_meta in PHASE2_HARDWARE_CATALOG_INR.items():
            req_t = int(hw_meta["min_tier"])
            if tier_num >= req_t:
                c_inr = fin["hardware_line_items_inr"].get(hw_name, 0.0)
                bom_summary_rows.append(
                    {
                        "Component": hw_name,
                        "Tier Scope": f"Tier {req_t}+",
                        "Status": "🔓 Unlocked",
                        "Cost": _format_currency(c_inr, currency),
                    }
                )
            else:
                bom_summary_rows.append(
                    {
                        "Component": hw_name,
                        "Tier Scope": f"Tier {req_t}+",
                        "Status": f"🔒 Locked (Tier {req_t})",
                        "Cost": _format_currency(0.0, currency),
                    }
                )
        bom_summary_rows.append(
            {
                "Component": "TOTAL INITIAL INVESTMENT",
                "Tier Scope": tier_key,
                "Status": "ACTIVE TOTAL",
                "Cost": _format_currency(fin["initial_cost_inr"], currency),
            }
        )
        st.dataframe(
            pd.DataFrame(bom_summary_rows),
            use_container_width=True,
            hide_index=True,
        )
