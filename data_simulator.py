"""
Deterministic Simulation, Financial, Thermodynamic & Telemetry Engine for GreenCompute.
Prepared by WAS Group 2, TAPMI Bengaluru for GreenCore Data Services Pvt. Ltd., Bengaluru.
"""
from __future__ import annotations

from typing import Any, Dict, Optional

import numpy as np
import pandas as pd
import streamlit as st

# ---------------------------------------------------------------------------
# Constants & Reference Tables
# ---------------------------------------------------------------------------
USD_TO_INR: float = 84.0
REFERENCE_FACILITY_MW: float = 2.0
HOURS_PER_YEAR: float = 8760.0

TIER_OPTIONS = [
    "Tier 1: Visibility & Software Advisory (12-Week PoC)",
    "Tier 2: Full-Stack Optimization Blueprint",
    "Tier 3: Turnkey AI Automation & Carbon Offset (Phase-2 Scale-Up)",
]

GRID_REGIONS: Dict[str, float] = {
    "India - Southern Grid / Bengaluru (0.71 kgCO2/kWh)": 0.71,
    "India - Western Grid (0.76 kgCO2/kWh)": 0.76,
    "US - Average (0.38 kgCO2/kWh)": 0.38,
    "EU - Average (0.25 kgCO2/kWh)": 0.25,
}

# Exact ₹8,20,000 itemized 12-week pilot budget from the report (Appendix B)
TIER1_PILOT_BUDGET_INR: Dict[str, int] = {
    "Consulting & Delivery": 5_40_000,
    "Cloud/Software/AI": 45_000,
    "Test Sensors/Data Setup": 65_000,
    "Dashboard & Integration": 70_000,
    "Training/SOPs": 25_000,
    "Contingency": 75_000,
}
assert sum(TIER1_PILOT_BUDGET_INR.values()) == 8_20_000

# Phase-2 Hardware CapEx reference costs (in INR for a 2.0 MW reference facility)
PHASE2_HARDWARE_CATALOG_INR: Dict[str, Dict[str, Any]] = {
    "Deploy 48 Wireless LoRaWAN Rack Inlet Sensors": {
        "min_tier": 2,
        "ref_cost_inr": 3_60_000,
        "min_slider_inr": 1_00_000,
        "max_slider_inr": 12_00_000,
        "category": "IoT Telemetry Mesh",
        "impact": "Eliminates 6-rack thermal blind spots; enables sub-rack ASHRAE A1 monitoring.",
    },
    "Install Hot-Aisle Containment Curtains": {
        "min_tier": 2,
        "ref_cost_inr": 5_80_000,
        "min_slider_inr": 1_50_000,
        "max_slider_inr": 20_00_000,
        "category": "Airflow Containment",
        "impact": "Separates supply/return air streams; mitigates bypass airflow on R03, R08, R11.",
    },
    "Retrofit CRAC Units with Variable Frequency Drives (VFDs)": {
        "min_tier": 3,
        "ref_cost_inr": 9_40_000,
        "min_slider_inr": 2_50_000,
        "max_slider_inr": 30_00_000,
        "category": "Closed-Loop HVAC Automation",
        "impact": "Enables dynamic fan affinity-law modulation (-22% CRAC fan power draw).",
    },
    "Direct-to-Chip Liquid Cooling for High-Density AI Racks": {
        "min_tier": 3,
        "ref_cost_inr": 18_50_000,
        "min_slider_inr": 5_00_000,
        "max_slider_inr": 60_00_000,
        "category": "High-Density Thermal Scale-Up",
        "impact": "Supports >25 kW/rack AI training pods with ultra-low PUE overhead.",
    },
}

PHASE2_HARDWARE_REFERENCE_INR: Dict[str, Dict[str, Any]] = {
    "Tier 2": {
        k: v["ref_cost_inr"]
        for k, v in PHASE2_HARDWARE_CATALOG_INR.items()
        if v["min_tier"] <= 2
    },
    "Tier 3": {
        k: v["ref_cost_inr"]
        for k, v in PHASE2_HARDWARE_CATALOG_INR.items()
        if v["min_tier"] <= 3
    },
}

# Overhead reduction fractions & recommended total reduction per tier
TIER_PHYSICS_CONFIG: Dict[str, Dict[str, float]] = {
    "Tier 1": {
        "recommended_reduction_pct": 5.0,
        "overhead_reduction_fraction": 0.12,  # 12% overhead reduction
    },
    "Tier 2": {
        "recommended_reduction_pct": 12.0,
        "overhead_reduction_fraction": 0.28,  # 28% overhead reduction
    },
    "Tier 3": {
        "recommended_reduction_pct": 20.0,
        "overhead_reduction_fraction": 0.45,  # 45% overhead reduction
    },
}


def normalize_tier_key(selected_tier: str) -> str:
    """Map full tier radio string or short label to 'Tier 1', 'Tier 2', or 'Tier 3'."""
    if selected_tier.startswith("Tier 1"):
        return "Tier 1"
    if selected_tier.startswith("Tier 2"):
        return "Tier 2"
    if selected_tier.startswith("Tier 3"):
        return "Tier 3"
    return "Tier 1"


# ---------------------------------------------------------------------------
# 1. Financial & Thermodynamic Engine (Appendix B Formulas)
# ---------------------------------------------------------------------------
@st.cache_data(show_spinner=False)
def compute_financials_and_thermodynamics(
    selected_tier: str = TIER_OPTIONS[0],
    baseline_kwh: float = 1_200_000.0,
    reduction_pct: float = 5.0,
    baseline_pue: float = 1.65,
    currency: str = "INR (₹)",
    tariff: float = 8.50,
    recurring_opex: float = 1_20_000.0,
    grid_region: str = "India - Southern Grid / Bengaluru (0.71 kgCO2/kWh)",
    hardware_capex_override_inr: Optional[float] = None,
    hw_capex_overrides: Optional[Dict[str, float]] = None,
) -> Dict[str, Any]:
    """
    Compute Appendix B financials, physics-safe PUE, and Scope 1 & 2 emissions.

    Note on currency handling:
    - `tariff` and `recurring_opex` are provided in the active `currency`
      (e.g., ₹8.50/kWh and ₹1,20,000 in INR, or $0.10/kWh and $1,428.57 in USD).
    - Also returns both INR and active-currency values for seamless formatting.
    """
    tier_key = normalize_tier_key(selected_tier)
    is_usd = currency == "USD ($)"
    fx_rate = USD_TO_INR if is_usd else 1.0

    # Facility load in MW and scale factor relative to 2.0 MW reference facility
    avg_facility_kw = baseline_kwh / HOURS_PER_YEAR
    avg_facility_mw = avg_facility_kw / 1000.0
    avg_it_kw = avg_facility_kw / max(baseline_pue, 1.05)
    avg_it_mw = avg_it_kw / 1000.0
    # Scale factor relative to 2.0 MW facility (bounded to [0.25, 12.0] for realistic PoC-to-hyperscale sizing)
    facility_scale_factor = float(np.clip(avg_facility_mw / REFERENCE_FACILITY_MW, 0.25, 12.0))

    # Itemized Tier 1 Pilot Budget (exact ₹8,20,000 in INR)
    pilot_budget_inr = float(sum(TIER1_PILOT_BUDGET_INR.values()))
    pilot_line_items_currency = {
        k: (v / fx_rate) for k, v in TIER1_PILOT_BUDGET_INR.items()
    }

    # Phase-2 Hardware CapEx for Tier 2 & Tier 3
    if tier_key == "Tier 1":
        default_hw_items_inr: Dict[str, float] = {}
        hardware_items_inr: Dict[str, float] = {}
        default_hardware_capex_inr = 0.0
    else:
        ref_items = PHASE2_HARDWARE_REFERENCE_INR[tier_key]
        default_hw_items_inr = {
            k: round(v * facility_scale_factor, -3) for k, v in ref_items.items()
        }
        hardware_items_inr = dict(default_hw_items_inr)
        if hw_capex_overrides:
            for item_name, override_val in hw_capex_overrides.items():
                if item_name in hardware_items_inr and override_val is not None:
                    hardware_items_inr[item_name] = float(override_val)
        default_hardware_capex_inr = float(sum(default_hw_items_inr.values()))

    if hardware_capex_override_inr is not None and tier_key != "Tier 1":
        active_hardware_capex_inr = float(hardware_capex_override_inr)
    else:
        active_hardware_capex_inr = float(sum(hardware_items_inr.values()))

    initial_cost_inr = pilot_budget_inr + active_hardware_capex_inr
    initial_cost = initial_cost_inr / fx_rate

    # Appendix B Financial Formulas (in active currency)
    annual_kwh_saved = baseline_kwh * (reduction_pct / 100.0)
    projected_annual_kwh = baseline_kwh - annual_kwh_saved

    baseline_annual_cost = baseline_kwh * tariff
    annual_gross_saving = baseline_kwh * (reduction_pct / 100.0) * tariff
    annual_net_benefit = annual_gross_saving - recurring_opex

    # Also compute exact INR equivalents
    tariff_inr = tariff * fx_rate
    recurring_opex_inr = recurring_opex * fx_rate
    annual_gross_saving_inr = annual_gross_saving * fx_rate
    annual_net_benefit_inr = annual_net_benefit * fx_rate

    if annual_net_benefit > 0:
        simple_payback_months: Optional[float] = (initial_cost / annual_net_benefit) * 12.0
        simple_payback_display = f"{simple_payback_months:.1f} months"
    else:
        simple_payback_months = None
        simple_payback_display = "N/A - Net Negative"

    annual_roi_pct = (annual_net_benefit / initial_cost) * 100.0 if initial_cost > 0 else 0.0

    # Physics-Safe Projected PUE
    # Apply efficiency gains ONLY to facility cooling/power overhead (Baseline PUE - 1.0)
    # Tier 1 reduces overhead by 12%, Tier 2 by 28%, Tier 3 by 45% at recommended reduction,
    # scaled smoothly if the user adjusts the Target Facility Energy Reduction slider.
    tier_cfg = TIER_PHYSICS_CONFIG[tier_key]
    base_oh_red = tier_cfg["overhead_reduction_fraction"]
    rec_red = tier_cfg["recommended_reduction_pct"]
    slider_ratio = reduction_pct / rec_red if rec_red > 0 else 1.0
    effective_overhead_reduction = float(np.clip(base_oh_red * slider_ratio, 0.02, 0.75))

    baseline_overhead = max(0.0, baseline_pue - 1.0)
    projected_overhead = baseline_overhead * (1.0 - effective_overhead_reduction)
    projected_pue = float(max(1.05, round(1.0 + projected_overhead, 3)))
    pue_improvement_pct = (
        ((baseline_pue - projected_pue) / baseline_pue) * 100.0 if baseline_pue > 0 else 0.0
    )

    # Emissions Engine
    grid_ef = GRID_REGIONS.get(grid_region, 0.71)
    scope2_baseline_tonnes = (baseline_kwh * grid_ef) / 1000.0
    scope1_baseline_tonnes = 0.05 * scope2_baseline_tonnes  # 5% diesel testing & fugitive refrigerants
    total_baseline_emissions_tonnes = scope2_baseline_tonnes + scope1_baseline_tonnes

    co2_avoided_efficiency_tonnes = (
        baseline_kwh * (reduction_pct / 100.0) * grid_ef
    ) / 1000.0
    scope2_projected_tonnes = max(0.0, scope2_baseline_tonnes - co2_avoided_efficiency_tonnes)
    total_projected_emissions_tonnes = scope2_projected_tonnes + scope1_baseline_tonnes

    return {
        "tier_key": tier_key,
        "selected_tier": selected_tier,
        "currency": currency,
        "fx_rate": fx_rate,
        "baseline_kwh": baseline_kwh,
        "projected_annual_kwh": projected_annual_kwh,
        "annual_kwh_saved": annual_kwh_saved,
        "reduction_pct": reduction_pct,
        "avg_facility_kw": avg_facility_kw,
        "avg_facility_mw": avg_facility_mw,
        "avg_it_kw": avg_it_kw,
        "avg_it_mw": avg_it_mw,
        "facility_scale_factor": facility_scale_factor,
        # Active currency financials
        "tariff": tariff,
        "recurring_opex": recurring_opex,
        "baseline_annual_cost": baseline_annual_cost,
        "annual_gross_saving": annual_gross_saving,
        "annual_net_benefit": annual_net_benefit,
        "initial_cost": initial_cost,
        "pilot_budget": pilot_budget_inr / fx_rate,
        "hardware_capex": active_hardware_capex_inr / fx_rate,
        "default_hardware_capex": default_hardware_capex_inr / fx_rate,
        "pilot_line_items": pilot_line_items_currency,
        "hardware_line_items": {k: v / fx_rate for k, v in hardware_items_inr.items()},
        "default_hardware_line_items": {k: v / fx_rate for k, v in default_hw_items_inr.items()},
        # INR canonical financials
        "tariff_inr": tariff_inr,
        "recurring_opex_inr": recurring_opex_inr,
        "annual_gross_saving_inr": annual_gross_saving_inr,
        "annual_net_benefit_inr": annual_net_benefit_inr,
        "initial_cost_inr": initial_cost_inr,
        "pilot_budget_inr": pilot_budget_inr,
        "hardware_capex_inr": active_hardware_capex_inr,
        "default_hardware_capex_inr": default_hardware_capex_inr,
        "pilot_line_items_inr": dict(TIER1_PILOT_BUDGET_INR),
        "hardware_line_items_inr": hardware_items_inr,
        "default_hardware_line_items_inr": default_hw_items_inr,
        # Payback & ROI
        "simple_payback_months": simple_payback_months,
        "simple_payback_display": simple_payback_display,
        "annual_roi_pct": annual_roi_pct,
        # Thermodynamics & PUE
        "baseline_pue": baseline_pue,
        "projected_pue": projected_pue,
        "pue_improvement_pct": pue_improvement_pct,
        "overhead_reduction_pct": effective_overhead_reduction * 100.0,
        # Carbon & ESG
        "grid_region": grid_region,
        "grid_emission_factor": grid_ef,
        "scope2_baseline_tonnes": scope2_baseline_tonnes,
        "scope1_baseline_tonnes": scope1_baseline_tonnes,
        "total_baseline_emissions_tonnes": total_baseline_emissions_tonnes,
        "co2_avoided_efficiency_tonnes": co2_avoided_efficiency_tonnes,
        "scope2_projected_tonnes": scope2_projected_tonnes,
        "total_projected_emissions_tonnes": total_projected_emissions_tonnes,
    }


# ---------------------------------------------------------------------------
# 2. Workstream B (Python Workload Benchmark Data)
# ---------------------------------------------------------------------------
@st.cache_data(show_spinner=False)
def get_python_workload_benchmark(
    grid_emission_factor: float = 0.71,
) -> Dict[str, Any]:
    """
    Return deterministic baseline vs. optimized metrics for Workstream B:
    Python 3.11 batch ETL/analytics workload (pandas/numpy vectorization).
    """
    np.random.seed(42)

    runtime_baseline_s = 14.8
    runtime_optimized_s = 5.2
    runtime_reduction_pct = -64.9  # (5.2 - 14.8) / 14.8 * 100 = -64.86% -> -64.9%

    cpu_baseline_pct = 88.0
    cpu_optimized_pct = 54.0
    cpu_reduction_pct = round(((cpu_optimized_pct - cpu_baseline_pct) / cpu_baseline_pct) * 100.0, 1)

    mem_baseline_mb = 1420.0
    mem_optimized_mb = 610.0
    mem_reduction_pct = -57.0  # (610 - 1420) / 1420 * 100 = -57.04% -> -57.0%

    # Software Carbon Intensity (SCI): gCO2e per 1,000 functional records
    # Based on server package power draw during execution scaled by grid_emission_factor
    sci_baseline_gco2_per_1k = round(0.68 * grid_emission_factor, 3)
    sci_optimized_gco2_per_1k = round(
        sci_baseline_gco2_per_1k * (runtime_optimized_s / runtime_baseline_s), 3
    )
    sci_reduction_pct = -64.9

    comparison_df = pd.DataFrame(
        [
            {
                "Metric": "Execution Runtime (s)",
                "Baseline (Row-Iter / Loops)": f"{runtime_baseline_s:.1f} s",
                "Optimized (NumPy/Pandas Vectorized)": f"{runtime_optimized_s:.1f} s",
                "Delta (%)": f"{runtime_reduction_pct:.1f}%",
            },
            {
                "Metric": "Peak CPU Utilization (%)",
                "Baseline (Row-Iter / Loops)": f"{cpu_baseline_pct:.0f}%",
                "Optimized (NumPy/Pandas Vectorized)": f"{cpu_optimized_pct:.0f}%",
                "Delta (%)": f"{cpu_reduction_pct:.1f}%",
            },
            {
                "Metric": "Peak Memory Footprint (MB)",
                "Baseline (Row-Iter / Loops)": f"{mem_baseline_mb:,.0f} MB",
                "Optimized (NumPy/Pandas Vectorized)": f"{mem_optimized_mb:,.0f} MB",
                "Delta (%)": f"{mem_reduction_pct:.1f}%",
            },
            {
                "Metric": "Software Carbon Intensity (SCI)",
                "Baseline (Row-Iter / Loops)": f"{sci_baseline_gco2_per_1k:.3f} gCO₂e / 1k rec",
                "Optimized (NumPy/Pandas Vectorized)": f"{sci_optimized_gco2_per_1k:.3f} gCO₂e / 1k rec",
                "Delta (%)": f"{sci_reduction_pct:.1f}%",
            },
            {
                "Metric": "Output Equivalence Check",
                "Baseline (Row-Iter / Loops)": "Reference SHA-256",
                "Optimized (NumPy/Pandas Vectorized)": "PASS - 100% Exact Match",
                "Delta (%)": "0.0% Drift",
            },
        ]
    )

    return {
        "environment": "Python 3.11 · pandas / NumPy Vectorized Batch ETL Pipeline",
        "records_processed": 2_500_000,
        "runtime_baseline_s": runtime_baseline_s,
        "runtime_optimized_s": runtime_optimized_s,
        "runtime_reduction_pct": runtime_reduction_pct,
        "peak_cpu_baseline_pct": cpu_baseline_pct,
        "peak_cpu_optimized_pct": cpu_optimized_pct,
        "peak_cpu_reduction_pct": cpu_reduction_pct,
        "peak_memory_baseline_mb": mem_baseline_mb,
        "peak_memory_optimized_mb": mem_optimized_mb,
        "peak_memory_reduction_pct": mem_reduction_pct,
        "output_equivalence": "PASS - 100% Exact Match",
        "sci_baseline_gco2_per_1k": sci_baseline_gco2_per_1k,
        "sci_optimized_gco2_per_1k": sci_optimized_gco2_per_1k,
        "sci_reduction_pct": sci_reduction_pct,
        "comparison_df": comparison_df,
    }


# ---------------------------------------------------------------------------
# 3. 24-Hour Telemetry & ML Validation Data
# ---------------------------------------------------------------------------
@st.cache_data(show_spinner=False)
def generate_24h_telemetry_and_ml(
    baseline_kwh: float = 1_200_000.0,
    baseline_pue: float = 1.65,
    reduction_pct: float = 5.0,
    grid_emission_factor: float = 0.71,
    selected_tier: str = TIER_OPTIONS[0],
) -> Dict[str, Any]:
    """
    Generate deterministic 24-hour (00:00–23:00) telemetry DataFrame,
    Tier 3 AI carbon-aware shifted load curve, ML validation metrics,
    and 6-row Anomaly & Recommendation Audit Log.
    """
    np.random.seed(42)
    hours = np.arange(24)
    hour_labels = [f"{h:02d}:00" for h in hours]

    avg_total_kw = baseline_kwh / HOURS_PER_YEAR
    avg_it_kw = avg_total_kw / max(baseline_pue, 1.05)
    avg_cooling_kw = max(0.0, avg_total_kw - avg_it_kw)

    # Diurnal IT workload curve (higher between 09:00 and 20:00, batch peak 13:00-18:00)
    diurnal_it_profile = np.array(
        [
            0.78, 0.74, 0.72, 0.71, 0.73, 0.77,
            0.85, 0.94, 1.03, 1.10, 1.14, 1.16,
            1.18, 1.22, 1.25, 1.24, 1.21, 1.19,
            1.12, 1.04, 0.96, 0.90, 0.84, 0.80,
        ]
    )
    diurnal_it_profile = diurnal_it_profile / diurnal_it_profile.mean()
    noise_it = np.random.normal(0.0, 0.012, size=24)
    it_power_kw = np.round(avg_it_kw * (diurnal_it_profile + noise_it), 2)

    # Cooling overhead curve (peaks 13:00–18:00 due to afternoon ambient wet-bulb temp)
    cooling_profile = np.array(
        [
            0.72, 0.68, 0.66, 0.65, 0.66, 0.70,
            0.78, 0.88, 0.98, 1.06, 1.14, 1.20,
            1.26, 1.34, 1.38, 1.36, 1.30, 1.22,
            1.10, 0.98, 0.89, 0.82, 0.77, 0.74,
        ]
    )
    cooling_profile = cooling_profile / cooling_profile.mean()
    cooling_overhead_kw = np.round(avg_cooling_kw * cooling_profile, 2)

    total_baseline_kw = np.round(it_power_kw + cooling_overhead_kw, 2)
    optimized_total_kw = np.round(total_baseline_kw * (1.0 - reduction_pct / 100.0), 2)

    # Grid Carbon Intensity (gCO2/kWh): dips during early morning (01:00–05:00)
    # and midday solar window (10:00–12:00), peaks during 13:00–18:00 thermal dispatch
    base_gco2 = grid_emission_factor * 1000.0
    carbon_multiplier = np.array(
        [
            0.86, 0.81, 0.78, 0.77, 0.79, 0.85,
            0.94, 0.98, 0.95, 0.90, 0.84, 0.83,
            0.92, 1.15, 1.22, 1.25, 1.23, 1.19,
            1.12, 1.05, 0.99, 0.94, 0.90, 0.88,
        ]
    )
    carbon_multiplier = carbon_multiplier / carbon_multiplier.mean()
    grid_carbon_intensity_gco2 = np.round(base_gco2 * carbon_multiplier, 1)

    # Tier 3 "AI Carbon-Aware Shifted Load (kW)":
    # Shifts 18% of afternoon batch jobs (13:00–18:00, 6 hours) into low-carbon windows
    # (01:00–04:00 early morning and 10:00–11:00 solar dip, 6 hours total)
    ai_carbon_shifted_kw = optimized_total_kw.copy()
    afternoon_mask = (hours >= 13) & (hours <= 18)
    low_carbon_mask = ((hours >= 1) & (hours <= 4)) | ((hours >= 10) & (hours <= 11))

    shifted_kw_per_afternoon_hr = optimized_total_kw[afternoon_mask] * 0.18
    total_shifted_kwh = float(shifted_kw_per_afternoon_hr.sum())

    ai_carbon_shifted_kw[afternoon_mask] = np.round(
        optimized_total_kw[afternoon_mask] - shifted_kw_per_afternoon_hr, 2
    )
    # Distribute shifted batch energy across the 6 low-carbon target hours
    weights = np.array([0.18, 0.20, 0.20, 0.16, 0.13, 0.13])
    ai_carbon_shifted_kw[low_carbon_mask] = np.round(
        ai_carbon_shifted_kw[low_carbon_mask] + total_shifted_kwh * weights, 2
    )

    # ML Forecast vs Historical Baseline Curves (illustrating 8.4% vs 19.2% MAPE)
    ml_errors = np.random.uniform(-0.04, 0.04, size=24)
    ml_forecast_kw = np.round(total_baseline_kw * (1.0 + ml_errors), 2)
    hist_baseline_forecast_kw = np.round(
        np.full(24, avg_total_kw) * (1.0 + 0.05 * np.sin(hours * np.pi / 12.0)), 2
    )

    telemetry_df = pd.DataFrame(
        {
            "hour": hours,
            "hour_label": hour_labels,
            "it_power_kw": it_power_kw,
            "cooling_overhead_kw": cooling_overhead_kw,
            "total_baseline_kw": total_baseline_kw,
            "optimized_total_kw": optimized_total_kw,
            "ai_carbon_shifted_kw": ai_carbon_shifted_kw,
            "ml_forecast_kw": ml_forecast_kw,
            "hist_baseline_forecast_kw": hist_baseline_forecast_kw,
            "grid_carbon_intensity_gco2": grid_carbon_intensity_gco2,
        }
    )

    # Carbon savings solely from temporal load shifting (Tier 3)
    unshifted_daily_co2_kg = float(
        np.sum(optimized_total_kw * grid_carbon_intensity_gco2) / 1000.0
    )
    shifted_daily_co2_kg = float(
        np.sum(ai_carbon_shifted_kw * grid_carbon_intensity_gco2) / 1000.0
    )
    annual_temporal_shift_co2_tonnes = max(
        0.0, ((unshifted_daily_co2_kg - shifted_daily_co2_kg) * 365.0) / 1000.0
    )

    # 6-Row Anomaly & Recommendation Audit Log
    audit_log_df = pd.DataFrame(
        [
            {
                "Timestamp": "2026-11-12 14:15",
                "Source Metric": "Rack R08 Cold-Aisle Inlet (°C)",
                "Detected Event & Advisory": "Hot-air recirculation spike (29.1°C); check blanking panels & floor grommets",
                "Confidence %": 98.4,
                "Owner": "M2 · Sankarshana (Tech/AI)",
                "Review Status": "Verified · Action Dispatched",
            },
            {
                "Timestamp": "2026-11-12 15:00",
                "Source Metric": "CRAC-02 Chilled Water Valve (%)",
                "Detected Event & Advisory": "Simultaneous heating/sub-cooling hunting loop; raise supply setpoint +1.5°C",
                "Confidence %": 96.1,
                "Owner": "M3 · Samiksha (Delivery/QA)",
                "Review Status": "Approved · Human-in-the-Loop",
            },
            {
                "Timestamp": "2026-11-12 15:45",
                "Source Metric": "Batch ETL Cluster Node-04 (CPU %)",
                "Detected Event & Advisory": "Unvectorized pandas loop pegging 88% CPU during peak grid tariff window",
                "Confidence %": 94.8,
                "Owner": "M6 · Prathamesh (Prototype)",
                "Review Status": "Resolved · Vectorized Patch Deployed",
            },
            {
                "Timestamp": "2026-11-12 16:30",
                "Source Metric": "Rack R03 Differential Pressure (Pa)",
                "Detected Event & Advisory": "Under-floor plenum pressure drop (8.8 Pa); rebalance perforated tile damper",
                "Confidence %": 92.7,
                "Owner": "M3 · Samiksha (Delivery/QA)",
                "Review Status": "Verified · Scheduled in Maintenance",
            },
            {
                "Timestamp": "2026-11-12 17:15",
                "Source Metric": "Rack R11 Cold-Aisle Inlet (°C)",
                "Detected Event & Advisory": "Bypass airflow hotspot (27.9°C); recommend containment curtain seal check",
                "Confidence %": 91.5,
                "Owner": "M1 · Adithya (PM/Client)",
                "Review Status": "In Review · Facility Ops Sign-Off",
            },
            {
                "Timestamp": "2026-11-12 19:00",
                "Source Metric": "PDU-B2 Reactive Power Factor",
                "Detected Event & Advisory": "Transient harmonic distortion during backup generator load-bank test",
                "Confidence %": 64.2,
                "Owner": "M4 · Faizan (Finance/Risk)",
                "Review Status": "Dismissed · Planned Test (False Positive)",
            },
        ]
    )

    ml_validation = {
        "forecast_mape_ml": 8.4,
        "forecast_mape_baseline": 19.2,
        "smart_target_mape": 15.0,
        "mape_target_met": True,
        "anomaly_recall_pct": 93.3,
        "anomaly_precision_pct": 93.3,
        "true_positives": 14,
        "false_positives": 1,
        "missed_anomalies": 1,
        "total_injected_events": 15,
        "smart_target_recall": 90.0,
        "recall_target_met": True,
        "shifted_batch_fraction_pct": 18.0,
        "annual_temporal_shift_co2_tonnes": round(annual_temporal_shift_co2_tonnes, 2),
    }

    return {
        "telemetry_df": telemetry_df,
        "ml_validation": ml_validation,
        "audit_log_df": audit_log_df,
    }


# ---------------------------------------------------------------------------
# 4. 12-Rack Thermal Telemetry (2 Rows x 6 Racks: R01–R12)
# ---------------------------------------------------------------------------
@st.cache_data(show_spinner=False)
def generate_12rack_thermal_telemetry(
    selected_tier: str = TIER_OPTIONS[0],
    baseline_kwh: float = 1_200_000.0,
    baseline_pue: float = 1.65,
    tier3_closed_loop_active: Optional[bool] = None,
) -> Dict[str, Any]:
    """
    Generate 12-rack thermal & pressure telemetry (2 Rows x 6 Racks: R01–R12).
    R03, R08, and R11 exhibit hot-air recirculation (>27.5°C) until Tier 3
    AI Closed-Loop Control cools them to 21.5°C–22.8°C (-22% CRAC fan power).
    """
    np.random.seed(42)
    tier_key = normalize_tier_key(selected_tier)
    if tier3_closed_loop_active is None:
        is_closed_loop = tier_key == "Tier 3"
    else:
        is_closed_loop = bool(tier3_closed_loop_active)

    avg_facility_kw = baseline_kwh / HOURS_PER_YEAR
    avg_it_kw = avg_facility_kw / max(baseline_pue, 1.05)
    avg_rack_kw = avg_it_kw / 12.0

    rack_ids = [f"R{i:02d}" for i in range(1, 13)]
    rows = ["Row A (North Cold Aisle)"] * 6 + ["Row B (South Cold Aisle)"] * 6
    cols = [1, 2, 3, 4, 5, 6] * 2

    # Relative rack load weights (R03, R08, R11 run denser compute nodes)
    load_multipliers = np.array(
        [0.88, 0.95, 1.24, 0.92, 0.86, 0.98, 0.91, 1.28, 0.94, 0.89, 1.21, 0.94]
    )
    load_multipliers = load_multipliers / load_multipliers.mean()
    rack_kw = np.round(avg_rack_kw * load_multipliers, 2)

    # Baseline temperatures (°C): R03, R08, R11 > 27.5°C due to hot-air recirculation
    baseline_temps_c = np.array(
        [22.4, 23.1, 28.4, 23.5, 22.1, 23.8, 22.9, 29.1, 23.4, 22.6, 27.9, 23.2]
    )
    # Tier 2 (containment + manual balancing) moderates non-closed-loop slightly but R03/R08/R11 remain >27.5°C
    tier2_temps_c = np.array(
        [21.8, 22.3, 27.8, 22.6, 21.6, 22.9, 22.1, 28.2, 22.5, 21.9, 27.6, 22.4]
    )
    # Tier 3 AI Closed-Loop Control cools R03, R08, R11 into 21.5°C–22.8°C band
    tier3_temps_c = np.array(
        [21.4, 21.7, 22.2, 21.8, 21.3, 21.9, 21.6, 22.6, 21.7, 21.5, 21.9, 21.6]
    )

    # Differential pressure (Pa): low pressure at R03, R08, R11 causes bypass recirculation
    baseline_pressure_pa = np.array(
        [18.2, 17.5, 8.8, 16.9, 19.0, 16.4, 17.8, 8.2, 17.1, 18.4, 9.4, 17.3]
    )
    tier2_pressure_pa = np.array(
        [19.0, 18.4, 11.2, 18.0, 19.5, 17.6, 18.5, 10.6, 18.1, 19.1, 11.8, 18.2]
    )
    tier3_pressure_pa = np.array(
        [20.2, 19.8, 19.4, 19.9, 20.5, 19.6, 20.0, 19.2, 19.8, 20.3, 19.5, 19.9]
    )

    if is_closed_loop:
        active_temps_c = tier3_temps_c
        active_pressure_pa = tier3_pressure_pa
        crac_fan_power_delta_pct = -22.0
        control_mode_label = "Tier 3 AI Closed-Loop Control Active (-22% CRAC Fan Power)"
    elif tier_key == "Tier 2":
        active_temps_c = tier2_temps_c
        active_pressure_pa = tier2_pressure_pa
        crac_fan_power_delta_pct = -9.5
        control_mode_label = "Tier 2 Static Containment & Advisory Mode (Hotspots R03, R08, R11 > 27.5°C)"
    else:
        active_temps_c = baseline_temps_c
        active_pressure_pa = baseline_pressure_pa
        crac_fan_power_delta_pct = 0.0
        control_mode_label = "Tier 1 Open-Loop Telemetry Advisory (Hotspots R03, R08, R11 > 27.5°C)"

    records = []
    for idx in range(12):
        temp = float(active_temps_c[idx])
        is_hot = temp > 27.5
        if is_hot:
            status = "CRITICAL: Hot-Air Recirculation (>27.5°C)"
        elif temp > 24.5:
            status = "WARNING: Elevated Inlet Temp"
        else:
            status = "OPTIMAL: ASHRAE A1 Envelope"

        records.append(
            {
                "rack_id": rack_ids[idx],
                "row_name": rows[idx],
                "row_idx": 0 if idx < 6 else 1,
                "col_idx": cols[idx],
                "kw_load": float(rack_kw[idx]),
                "inlet_temp_c": temp,
                "baseline_inlet_temp_c": float(baseline_temps_c[idx]),
                "tier3_inlet_temp_c": float(tier3_temps_c[idx]),
                "diff_pressure_pa": float(active_pressure_pa[idx]),
                "baseline_pressure_pa": float(baseline_pressure_pa[idx]),
                "tier3_pressure_pa": float(tier3_pressure_pa[idx]),
                "is_hotspot": is_hot,
                "airflow_status": status,
            }
        )

    racks_df = pd.DataFrame(records)

    # 2x6 matrix for Plotly heatmap rendering
    temp_matrix_2x6 = active_temps_c.reshape(2, 6)
    pressure_matrix_2x6 = active_pressure_pa.reshape(2, 6)
    kw_matrix_2x6 = rack_kw.reshape(2, 6)
    label_matrix_2x6 = np.array(rack_ids).reshape(2, 6)

    return {
        "racks_df": racks_df,
        "temp_matrix_2x6": temp_matrix_2x6,
        "pressure_matrix_2x6": pressure_matrix_2x6,
        "kw_matrix_2x6": kw_matrix_2x6,
        "label_matrix_2x6": label_matrix_2x6,
        "hotspot_racks": list(racks_df.loc[racks_df["is_hotspot"], "rack_id"]),
        "max_inlet_temp_c": float(active_temps_c.max()),
        "mean_inlet_temp_c": round(float(active_temps_c.mean()), 2),
        "crac_fan_power_delta_pct": crac_fan_power_delta_pct,
        "is_closed_loop": is_closed_loop,
        "control_mode_label": control_mode_label,
    }


# ---------------------------------------------------------------------------
# Unified Master Simulation Bundle
# ---------------------------------------------------------------------------
@st.cache_data(show_spinner=False)
def run_full_simulation(
    selected_tier: str = TIER_OPTIONS[0],
    baseline_kwh: float = 1_200_000.0,
    reduction_pct: float = 5.0,
    baseline_pue: float = 1.65,
    currency: str = "INR (₹)",
    tariff: float = 8.50,
    recurring_opex: float = 1_20_000.0,
    grid_region: str = "India - Southern Grid / Bengaluru (0.71 kgCO2/kWh)",
    hardware_capex_override_inr: Optional[float] = None,
    hw_capex_overrides: Optional[Dict[str, float]] = None,
    tier3_closed_loop_override: Optional[bool] = None,
) -> Dict[str, Any]:
    """
    Single convenience entrypoint returning all 4 simulation engines keyed cleanly.
    """
    fin_thermo = compute_financials_and_thermodynamics(
        selected_tier=selected_tier,
        baseline_kwh=baseline_kwh,
        reduction_pct=reduction_pct,
        baseline_pue=baseline_pue,
        currency=currency,
        tariff=tariff,
        recurring_opex=recurring_opex,
        grid_region=grid_region,
        hardware_capex_override_inr=hardware_capex_override_inr,
        hw_capex_overrides=hw_capex_overrides,
    )
    grid_ef = fin_thermo["grid_emission_factor"]

    workload_bench = get_python_workload_benchmark(grid_emission_factor=grid_ef)

    telemetry_ml = generate_24h_telemetry_and_ml(
        baseline_kwh=baseline_kwh,
        baseline_pue=baseline_pue,
        reduction_pct=reduction_pct,
        grid_emission_factor=grid_ef,
        selected_tier=selected_tier,
    )

    rack_thermal = generate_12rack_thermal_telemetry(
        selected_tier=selected_tier,
        baseline_kwh=baseline_kwh,
        baseline_pue=baseline_pue,
        tier3_closed_loop_active=tier3_closed_loop_override,
    )

    return {
        "financials": fin_thermo,
        "workload_benchmark": workload_bench,
        "telemetry_ml": telemetry_ml,
        "rack_thermal": rack_thermal,
    }

