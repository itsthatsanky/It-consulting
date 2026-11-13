"""
GreenCompute | Energy & Computing Optimization
Prepared by WAS Group 2, TAPMI Bengaluru for GreenCore Data Services Pvt. Ltd., Bengaluru
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# ---------------------------------------------------------------------------
# Page Configuration
# ---------------------------------------------------------------------------
st.set_page_config(
    layout="wide",
    page_title="GreenCompute | GreenCore Data Services",
    page_icon="⚡",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Custom CSS Styling (#111827 fill, #1F2937 1px borders, Emerald/Cyan/Amber accents)
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
    /* Global dark background refinements */
    .stApp {
        background-color: #0B0F19;
        color: #F9FAFB;
    }
    section[data-testid="stSidebar"] {
        background-color: #111827;
        border-right: 1px solid #1F2937;
    }

    /* Metric Cards Styling */
    [data-testid="stMetric"] {
        background-color: #111827;
        border: 1px solid #1F2937;
        border-left: 4px solid #10B981;
        border-radius: 10px;
        padding: 16px 18px;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.35);
        transition: border-color 0.2s ease, transform 0.15s ease;
    }
    [data-testid="stMetric"]:hover {
        border-color: #06B6D4;
        transform: translateY(-1px);
    }
    [data-testid="stMetricLabel"] {
        color: #9CA3AF !important;
        font-size: 0.82rem !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }
    [data-testid="stMetricValue"] {
        color: #F9FAFB !important;
        font-size: 1.65rem !important;
        font-weight: 700 !important;
    }
    [data-testid="stMetricDelta"] {
        font-weight: 600 !important;
    }

    /* Accent utility cards & badges */
    .gc-header-banner {
        background: linear-gradient(135deg, #111827 0%, #0B0F19 100%);
        border: 1px solid #1F2937;
        border-left: 4px solid #10B981;
        border-radius: 12px;
        padding: 18px 22px;
        margin-bottom: 18px;
    }
    .gc-badge-emerald {
        display: inline-block;
        background: rgba(16, 185, 129, 0.14);
        color: #10B981;
        border: 1px solid rgba(16, 185, 129, 0.4);
        border-radius: 999px;
        padding: 3px 10px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-right: 6px;
    }
    .gc-badge-cyan {
        display: inline-block;
        background: rgba(6, 182, 212, 0.14);
        color: #06B6D4;
        border: 1px solid rgba(6, 182, 212, 0.4);
        border-radius: 999px;
        padding: 3px 10px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-right: 6px;
    }
    .gc-badge-amber {
        display: inline-block;
        background: rgba(245, 158, 11, 0.14);
        color: #F59E0B;
        border: 1px solid rgba(245, 158, 11, 0.4);
        border-radius: 999px;
        padding: 3px 10px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-right: 6px;
    }
    .gc-tier-card {
        background-color: #111827;
        border: 1px solid #1F2937;
        border-radius: 10px;
        padding: 14px;
        margin-top: 8px;
        font-size: 0.83rem;
    }
    .gc-module-unlocked {
        color: #10B981;
        margin: 4px 0;
        font-weight: 500;
    }
    .gc-module-locked {
        color: #6B7280;
        margin: 4px 0;
    }
    .gc-safety-note {
        background: rgba(245, 158, 11, 0.1);
        border: 1px solid rgba(245, 158, 11, 0.35);
        color: #FBBF24;
        border-radius: 8px;
        padding: 8px 10px;
        margin-top: 8px;
        font-size: 0.76rem;
        line-height: 1.35;
    }

    /* Tabs styling */
    button[data-baseweb="tab"] {
        font-weight: 600 !important;
        font-size: 0.92rem !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Constants & Reference Maps
# ---------------------------------------------------------------------------
USD_TO_INR = 84.0

TIER_OPTIONS = [
    "Tier 1: Visibility & Software Advisory (12-Week PoC)",
    "Tier 2: Full-Stack Optimization Blueprint",
    "Tier 3: Turnkey AI Automation & Carbon Offset (Phase-2 Scale-Up)",
]

TIER_META = {
    TIER_OPTIONS[0]: {
        "short": "Tier 1 · PoC Advisory",
        "recommended_reduction": 5.0,
        "default_scenario": "Base Case (5%)",
        "capex_inr": 8_20_000,
        "pue_delta": 0.08,
        "accent": "#10B981",
        "unlocked": [
            "15-Min Smart Meter Telemetry & Baseline Profiling",
            "ML Load Forecasting & Isolation Forest Anomaly Alerts",
            "Python / SQL Batch Workload Profiling & Refactoring",
            "Executive Financial & Payback Scenario Simulator",
        ],
        "locked": [
            "Sub-Rack Thermal Sensor Mesh & CFD Airflow Balancing (Tier 2+)",
            "Automated Cold-Aisle Containment & VFD Chiller Tuning (Tier 2+)",
            "Closed-Loop AI HVAC Control & Real-Time Carbon Shifting (Tier 3)",
        ],
    },
    TIER_OPTIONS[1]: {
        "short": "Tier 2 · Full-Stack Blueprint",
        "recommended_reduction": 12.0,
        "default_scenario": "Tier Recommended",
        "capex_inr": 24_50_000,
        "pue_delta": 0.20,
        "accent": "#06B6D4",
        "unlocked": [
            "15-Min Smart Meter Telemetry & Baseline Profiling",
            "ML Load Forecasting & Isolation Forest Anomaly Alerts",
            "Python / SQL Batch Workload Profiling & Refactoring",
            "Executive Financial & Payback Scenario Simulator",
            "Sub-Rack Thermal Sensor Mesh & CFD Airflow Balancing",
            "Automated Cold-Aisle Containment & VFD Chiller Tuning",
        ],
        "locked": [
            "Closed-Loop AI HVAC Control & Real-Time Carbon Shifting (Tier 3)",
        ],
    },
    TIER_OPTIONS[2]: {
        "short": "Tier 3 · Turnkey AI & ESG Scale-Up",
        "recommended_reduction": 20.0,
        "default_scenario": "Tier Recommended",
        "capex_inr": 58_00_000,
        "pue_delta": 0.32,
        "accent": "#F59E0B",
        "unlocked": [
            "15-Min Smart Meter Telemetry & Baseline Profiling",
            "ML Load Forecasting & Isolation Forest Anomaly Alerts",
            "Python / SQL Batch Workload Profiling & Refactoring",
            "Executive Financial & Payback Scenario Simulator",
            "Sub-Rack Thermal Sensor Mesh & CFD Airflow Balancing",
            "Automated Cold-Aisle Containment & VFD Chiller Tuning",
            "Closed-Loop AI HVAC Control & Real-Time Carbon Shifting",
        ],
        "locked": [],
    },
}

SCENARIO_OPTIONS = [
    "Conservative (2%)",
    "Base Case (5%)",
    "Optimistic (8%)",
    "Tier Recommended",
]

SCENARIO_FIXED_PCT = {
    "Conservative (2%)": 2.0,
    "Base Case (5%)": 5.0,
    "Optimistic (8%)": 8.0,
}

GRID_REGIONS = {
    "India - Southern Grid / Bengaluru (0.71 kgCO2/kWh)": 0.71,
    "India - Western Grid (0.76 kgCO2/kWh)": 0.76,
    "US - Average (0.38 kgCO2/kWh)": 0.38,
    "EU - Average (0.25 kgCO2/kWh)": 0.25,
}

TEAM_MEMBERS = [
    ("M1", "PM / Client", "Adithya Pradeep", "246213368"),
    ("M2", "Tech / AI", "Sankarshana Mulugundam", "246213080"),
    ("M3", "Delivery / QA", "Samiksha Sandeep Das", "246213076"),
    ("M4", "Finance", "Faizan Ali Siddiqui", "246213110"),
    ("M5", "Research", "Anupama Sahu", "246213502"),
    ("M6", "Prototype / Adoption", "Prathamesh Prabhu", "246213290"),
]


# ---------------------------------------------------------------------------
# Formatting Helpers
# ---------------------------------------------------------------------------
def format_inr(amount: float, decimals: int = 0) -> str:
    """Format number using Indian numbering system (e.g. ₹8,20,000)."""
    neg = "-" if amount < 0 else ""
    val = abs(amount)
    whole = int(round(val)) if decimals == 0 else int(val)
    frac = "" if decimals == 0 else f"{val - whole:.{decimals}f}"[1:]
    s = str(whole)
    if len(s) > 3:
        head, tail = s[:-3], s[-3:]
        groups = []
        while len(head) > 2:
            groups.insert(0, head[-2:])
            head = head[:-2]
        if head:
            groups.insert(0, head)
        s = ",".join(groups) + "," + tail
    return f"{neg}₹{s}{frac}"


def format_currency(amount_inr: float, currency: str, decimals: int = 0) -> str:
    """Format an INR base value in the active currency (INR or USD at ₹84/$)."""
    if currency == "USD ($)":
        usd_val = amount_inr / USD_TO_INR
        neg = "-" if usd_val < 0 else ""
        return f"{neg}${abs(usd_val):,.{decimals}f}"
    return format_inr(amount_inr, decimals=decimals)


# ---------------------------------------------------------------------------
# Session State Initialization & Reactive Callbacks
# ---------------------------------------------------------------------------
if "selected_tier" not in st.session_state:
    st.session_state.selected_tier = TIER_OPTIONS[0]

if "scenario_pill" not in st.session_state:
    st.session_state.scenario_pill = "Base Case (5%)"

if "target_reduction_pct" not in st.session_state:
    st.session_state.target_reduction_pct = 5.0

if "baseline_kwh" not in st.session_state:
    st.session_state.baseline_kwh = 1_200_000

if "baseline_pue" not in st.session_state:
    st.session_state.baseline_pue = 1.65

if "currency" not in st.session_state:
    st.session_state.currency = "INR (₹)"

if "tariff_inr" not in st.session_state:
    st.session_state.tariff_inr = 8.50

if "tariff_usd" not in st.session_state:
    st.session_state.tariff_usd = 0.10

if "opex_inr" not in st.session_state:
    st.session_state.opex_inr = 120_000

if "opex_usd" not in st.session_state:
    st.session_state.opex_usd = int(round(120_000 / USD_TO_INR))

if "grid_region" not in st.session_state:
    st.session_state.grid_region = "India - Southern Grid / Bengaluru (0.71 kgCO2/kWh)"


def on_tier_change() -> None:
    """Update scenario pill and target reduction slider when Consulting Tier changes."""
    tier = st.session_state.selected_tier
    meta = TIER_META[tier]
    st.session_state.scenario_pill = meta["default_scenario"]
    st.session_state.target_reduction_pct = float(meta["recommended_reduction"])


def on_scenario_change() -> None:
    """Sync Target Facility Energy Reduction (%) slider when a scenario pill is clicked."""
    pill = st.session_state.scenario_pill
    if pill is None:
        return
    if pill in SCENARIO_FIXED_PCT:
        st.session_state.target_reduction_pct = float(SCENARIO_FIXED_PCT[pill])
    elif pill == "Tier Recommended":
        tier = st.session_state.selected_tier
        st.session_state.target_reduction_pct = float(
            TIER_META[tier]["recommended_reduction"]
        )


def on_opex_inr_change() -> None:
    st.session_state.opex_usd = int(round(st.session_state.opex_inr / USD_TO_INR))


def on_opex_usd_change() -> None:
    st.session_state.opex_inr = int(round(st.session_state.opex_usd * USD_TO_INR))


# ---------------------------------------------------------------------------
# Persistent Left Sidebar Controls
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown(
        """
        <div style="margin-bottom: 10px;">
            <span class="gc-badge-emerald">GREENCOMPUTE</span>
            <span class="gc-badge-cyan">WAS GROUP 2</span>
            <h3 style="margin: 8px 0 2px 0; color: #F9FAFB; font-size: 1.15rem;">
                Control & Scenario Center
            </h3>
            <div style="color: #9CA3AF; font-size: 0.78rem;">
                GreenCore Data Services Pvt. Ltd. · Bengaluru
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()

    # 1. Consulting Tier Radio Selector
    st.markdown("##### 1. Consulting Tier")
    selected_tier = st.radio(
        "Select Engagement Scope",
        options=TIER_OPTIONS,
        key="selected_tier",
        on_change=on_tier_change,
        label_visibility="collapsed",
    )
    active_tier_meta = TIER_META[selected_tier]

    st.divider()

    # 2. Financial Scenario & Reduction Override
    st.markdown("##### 2. Financial Scenario & Reduction Override")
    if hasattr(st, "pills"):
        st.pills(
            "Scenario Quick-Select",
            options=SCENARIO_OPTIONS,
            key="scenario_pill",
            on_change=on_scenario_change,
        )
    else:
        st.radio(
            "Scenario Quick-Select",
            options=SCENARIO_OPTIONS,
            key="scenario_pill",
            on_change=on_scenario_change,
            horizontal=True,
        )

    target_reduction_pct = st.slider(
        "Target Facility Energy Reduction (%)",
        min_value=1.0,
        max_value=30.0,
        step=0.5,
        key="target_reduction_pct",
        help="Auto-updates from Scenario Pills or Tier selection, and can be manually overridden at any time.",
    )
    st.caption(
        f"Active Scenario: **{st.session_state.scenario_pill or 'Custom Override'}** · "
        f"Tier Recommended: **{active_tier_meta['recommended_reduction']:.0f}%**"
    )

    st.divider()

    # 3. Client Facility & Tariff Sliders
    st.markdown("##### 3. Client Facility & Tariff Parameters")

    baseline_kwh = st.slider(
        "Annual Baseline Electricity (kWh/yr)",
        min_value=500_000,
        max_value=50_000_000,
        step=100_000,
        key="baseline_kwh",
    )
    avg_mw = baseline_kwh / (8760.0 * 1000.0)
    avg_kw = baseline_kwh / 8760.0
    st.caption(
        f"⚡ Equivalent Facility Load: **{avg_mw:.2f} MW** ({avg_kw:,.1f} kW continuous average)"
    )

    baseline_pue = st.slider(
        "Current Baseline PUE",
        min_value=1.20,
        max_value=2.50,
        step=0.05,
        key="baseline_pue",
    )

    currency = st.radio(
        "Currency Toggle (Fixed Rate: 1 USD = ₹84)",
        options=["INR (₹)", "USD ($)"],
        key="currency",
        horizontal=True,
    )

    if currency == "INR (₹)":
        tariff_inr = st.slider(
            "Electricity Tariff (₹/kWh)",
            min_value=4.00,
            max_value=18.00,
            step=0.25,
            key="tariff_inr",
        )
        effective_tariff_inr = float(tariff_inr)
        effective_tariff_display = f"₹{tariff_inr:.2f}/kWh"

        opex_inr = st.slider(
            "Annual Recurring Solution OpEx (₹/yr)",
            min_value=50_000,
            max_value=1_500_000,
            step=10_000,
            key="opex_inr",
            on_change=on_opex_inr_change,
        )
        effective_opex_inr = float(opex_inr)
        st.caption(
            f"Formatted OpEx: **{format_inr(effective_opex_inr)}/yr** "
            f"(~${effective_opex_inr / USD_TO_INR:,.0f}/yr)"
        )
    else:
        tariff_usd = st.slider(
            "Electricity Tariff ($/kWh)",
            min_value=0.05,
            max_value=0.25,
            step=0.01,
            key="tariff_usd",
        )
        effective_tariff_inr = float(tariff_usd) * USD_TO_INR
        effective_tariff_display = f"${tariff_usd:.2f}/kWh"

        opex_usd = st.slider(
            "Annual Recurring Solution OpEx ($/yr)",
            min_value=int(round(50_000 / USD_TO_INR)),
            max_value=int(round(1_500_000 / USD_TO_INR)),
            step=100,
            key="opex_usd",
            on_change=on_opex_usd_change,
        )
        effective_opex_inr = float(opex_usd) * USD_TO_INR
        st.caption(
            f"Equivalent INR OpEx: **{format_inr(effective_opex_inr)}/yr** (at 1 USD = ₹84)"
        )

    grid_region = st.selectbox(
        "Grid Region & Emission Factor",
        options=list(GRID_REGIONS.keys()),
        key="grid_region",
    )
    grid_ef = GRID_REGIONS[grid_region]

    st.divider()

    # 4. Dynamic Tier Capability Badge
    st.markdown("##### 4. Dynamic Tier Capability Badge")
    unlocked_html = "".join(
        f'<div class="gc-module-unlocked">✔ {item}</div>'
        for item in active_tier_meta["unlocked"]
    )
    locked_html = "".join(
        f'<div class="gc-module-locked">🔒 {item}</div>'
        for item in active_tier_meta["locked"]
    )
    st.markdown(
        f"""
        <div class="gc-tier-card" style="border-left: 4px solid {active_tier_meta['accent']};">
            <div style="font-weight: 700; color: #F9FAFB; margin-bottom: 6px;">
                {active_tier_meta['short']}
            </div>
            <div style="font-size: 0.75rem; color: #9CA3AF; margin-bottom: 6px;">
                UNLOCKED MODULES ({len(active_tier_meta['unlocked'])})
            </div>
            {unlocked_html}
            {f'<div style="font-size: 0.75rem; color: #9CA3AF; margin: 8px 0 4px 0;">LOCKED MODULES ({len(active_tier_meta["locked"])})</div>' + locked_html if active_tier_meta["locked"] else ''}
            <div class="gc-safety-note">
                ⚠️ <strong>Governance Note:</strong> Tier 3 closed-loop AI HVAC control is a
                <strong>Phase-2 post-pilot scale-up</strong> subject to formal engineering safety sign-off
                after the 12-week human-in-the-loop PoC.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------------------------
# Core Derived Facility, Financial & Carbon Metrics (via data_simulator.py)
# ---------------------------------------------------------------------------
from data_simulator import PHASE2_HARDWARE_CATALOG_INR, run_full_simulation
from tab_esg import render_tab_esg
from tab_floorplan import render_tab_floorplan
from tab_overview import render_tab_overview
from tab_roadmap import render_tab_roadmap

st.session_state.setdefault("hw_capex_overrides", {})

# Sync any active Tab 3 hardware CapEx slider keys into hw_capex_overrides before simulation
for _hw_idx, (_hw_name, _hw_meta) in enumerate(PHASE2_HARDWARE_CATALOG_INR.items()):
    _k_inr = f"hw_slider_{_hw_idx}_inr"
    _k_usd = f"hw_slider_{_hw_idx}_usd"
    if currency == "INR (₹)" and _k_inr in st.session_state:
        st.session_state["hw_capex_overrides"][_hw_name] = float(st.session_state[_k_inr])
    elif currency == "USD ($)" and _k_usd in st.session_state:
        st.session_state["hw_capex_overrides"][_hw_name] = (
            float(st.session_state[_k_usd]) * USD_TO_INR
        )

active_tariff_val = (
    st.session_state.tariff_inr
    if currency == "INR (₹)"
    else st.session_state.tariff_usd
)
active_opex_val = (
    float(st.session_state.opex_inr)
    if currency == "INR (₹)"
    else float(st.session_state.opex_usd)
)

sim_bundle = run_full_simulation(
    selected_tier=selected_tier,
    baseline_kwh=float(baseline_kwh),
    reduction_pct=float(target_reduction_pct),
    baseline_pue=float(baseline_pue),
    currency=currency,
    tariff=float(active_tariff_val),
    recurring_opex=float(active_opex_val),
    grid_region=grid_region,
    hardware_capex_override_inr=st.session_state.get("hardware_capex_override_inr"),
    hw_capex_overrides=dict(st.session_state.get("hw_capex_overrides", {})),
    tier3_closed_loop_override=st.session_state.get("tier3_closed_loop_override"),
)

fin = sim_bundle["financials"]

params = {
    "selected_tier": selected_tier,
    "tier_key": fin["tier_key"],
    "scenario_pill": st.session_state.scenario_pill,
    "target_reduction_pct": float(target_reduction_pct),
    "baseline_kwh": float(baseline_kwh),
    "baseline_pue": float(baseline_pue),
    "currency": currency,
    "tariff": float(active_tariff_val),
    "tariff_inr": float(fin["tariff_inr"]),
    "recurring_opex": float(active_opex_val),
    "opex_inr": float(fin["recurring_opex_inr"]),
    "grid_region": grid_region,
    "grid_ef": float(grid_ef),
}

# ---------------------------------------------------------------------------
# Main Page Header Banner & Global KPI Strip Container
# ---------------------------------------------------------------------------
st.markdown(
    f"""
    <div class="gc-header-banner">
        <div style="display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center; gap: 12px;">
            <div>
                <span class="gc-badge-emerald">GREENCOMPUTE</span>
                <span class="gc-badge-cyan">WAS GROUP 2 · TAPMI BENGALURU</span>
                <span class="gc-badge-amber">{active_tier_meta['short'].upper()}</span>
                <h1 style="margin: 8px 0 4px 0; font-size: 1.75rem; color: #F9FAFB;">
                    GreenCompute | Energy & Computing Optimization
                </h1>
                <div style="color: #9CA3AF; font-size: 0.9rem;">
                    Prepared for <strong>GreenCore Data Services Pvt. Ltd., Bengaluru</strong> (Hypothetical Mid-Tier Data Centre Client)
                    · Active Tariff: <strong>{effective_tariff_display}</strong> · Grid Factor: <strong>{grid_ef:.2f} kgCO₂/kWh</strong>
                </div>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

top_kpi_container = st.container()

# ---------------------------------------------------------------------------
# 4 Main Navigation Tabs
# ---------------------------------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs(
    [
        "1. Executive Overview & Telemetry",
        "2. Rack & Thermal Floorplan",
        "3. Optimization Roadmap & BoM",
        "4. Carbon Offset & ESG Reporting",
    ]
)

# Populate Tab 3 first in execution order so any hardware CapEx slider updates
# propagate into `sim_bundle["financials"]` before Tab 1, Tab 2, Tab 4, and top KPIs render.
with tab3:
    render_tab_roadmap(sim_bundle, params)

# Refresh `fin` in case Tab 3 updated `sim_bundle["financials"]` via CapEx overrides
fin = sim_bundle["financials"]
annual_kwh_saved = fin["annual_kwh_saved"]
gross_savings_inr = fin["annual_gross_saving_inr"]
net_annual_savings_inr = fin["annual_net_benefit_inr"]
capex_inr = fin["initial_cost_inr"]
payback_months = fin["simple_payback_months"]
annual_roi_pct = fin["annual_roi_pct"]
target_pue = fin["projected_pue"]
annual_co2_saved_tonnes = fin["co2_avoided_efficiency_tonnes"]

with top_kpi_container:
    kpi_cols = st.columns(5)
    with kpi_cols[0]:
        st.metric(
            "Annual Gross Saving",
            format_currency(gross_savings_inr, currency),
            f"{annual_kwh_saved:,.0f} kWh (-{target_reduction_pct:.1f}%)",
            delta_color="normal",
        )
    with kpi_cols[1]:
        st.metric(
            "Annual Net Benefit",
            format_currency(net_annual_savings_inr, currency),
            f"ROI: {annual_roi_pct:.1f}% / yr",
            delta_color="normal" if net_annual_savings_inr > 0 else "inverse",
        )
    with kpi_cols[2]:
        payback_str = (
            f"{payback_months:.1f} months"
            if payback_months is not None
            else "N/A - Net Negative"
        )
        st.metric(
            "Simple Payback",
            payback_str,
            f"Init Cost: {format_currency(capex_inr, currency)}",
        )
    with kpi_cols[3]:
        st.metric(
            "Projected Facility PUE",
            f"{target_pue:.2f}",
            f"From {baseline_pue:.2f} (-{fin['overhead_reduction_pct']:.0f}% overhead)",
        )
    with kpi_cols[4]:
        st.metric(
            "CO₂ Avoided (Scope 2)",
            f"{annual_co2_saved_tonnes:,.1f} tCO₂e/yr",
            f"Scope 1+2 Base: {fin['total_baseline_emissions_tonnes']:,.1f} t",
        )

with tab1:
    render_tab_overview(sim_bundle, params)

with tab2:
    render_tab_floorplan(sim_bundle, params)

with tab4:
    render_tab_esg(sim_bundle, params)

