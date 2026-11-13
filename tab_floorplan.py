"""
Tab 2: Rack & Thermal Floorplan (NOC Server Room Visualization)
Prepared by WAS Group 2, TAPMI Bengaluru for GreenCore Data Services Pvt. Ltd., Bengaluru.
"""
from __future__ import annotations

from typing import Any, Dict, Set

import pandas as pd
import streamlit as st

from data_simulator import generate_12rack_thermal_telemetry

# 6 racks masked in Tier 1 (3 in Row A, 3 in Row B) representing sub-rack sensor blind spots
TIER1_MASKED_RACKS: Set[str] = {"R02", "R03", "R06", "R08", "R10", "R11"}
HOTSPOT_RACK_IDS: Set[str] = {"R03", "R08", "R11"}


def _inject_floorplan_css() -> None:
    """Inject scoped CSS for the 2-Row x 6-Rack NOC server floorplan."""
    st.markdown(
        """
        <style>
        .noc-container {
            background: linear-gradient(180deg, #0F172A 0%, #0B0F19 100%);
            border: 1px solid #1F2937;
            border-radius: 14px;
            padding: 20px 22px;
            margin: 14px 0 18px 0;
            box-shadow: 0 10px 28px rgba(0, 0, 0, 0.45);
        }
        .noc-header-bar {
            display: flex;
            flex-wrap: wrap;
            justify-content: space-between;
            align-items: center;
            gap: 12px;
            padding-bottom: 14px;
            margin-bottom: 16px;
            border-bottom: 1px solid #1F2937;
        }
        .noc-aisle-label {
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: rgba(6, 182, 212, 0.08);
            border: 1px dashed rgba(6, 182, 212, 0.35);
            color: #67E8F9;
            border-radius: 8px;
            padding: 7px 14px;
            font-size: 0.78rem;
            font-weight: 700;
            letter-spacing: 0.06em;
            text-transform: uppercase;
            margin: 8px 0;
        }
        .noc-hot-aisle-label {
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: rgba(245, 158, 11, 0.08);
            border: 1px dashed rgba(245, 158, 11, 0.35);
            color: #FCD34D;
            border-radius: 8px;
            padding: 8px 14px;
            font-size: 0.78rem;
            font-weight: 700;
            letter-spacing: 0.06em;
            text-transform: uppercase;
            margin: 14px 0;
        }
        .noc-rack-grid {
            display: grid;
            grid-template-columns: repeat(6, minmax(135px, 1fr));
            gap: 12px;
            margin: 10px 0;
        }
        @media (max-width: 1100px) {
            .noc-rack-grid {
                grid-template-columns: repeat(3, minmax(140px, 1fr));
            }
        }
        @media (max-width: 640px) {
            .noc-rack-grid {
                grid-template-columns: repeat(2, minmax(130px, 1fr));
            }
        }
        .noc-rack-card {
            background-color: #111827;
            border: 1px solid #1F2937;
            border-top: 3px solid #10B981;
            border-radius: 10px;
            padding: 12px 12px 10px 12px;
            min-height: 158px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            transition: transform 0.15s ease, box-shadow 0.2s ease;
            position: relative;
        }
        .noc-rack-card:hover {
            transform: translateY(-2px);
        }
        .noc-rack-masked {
            background-color: #1F2937 !important;
            border: 1px dashed #374151 !important;
            border-top: 3px solid #4B5563 !important;
            color: #9CA3AF !important;
        }
        .noc-rack-hotspot {
            background: linear-gradient(180deg, rgba(239, 68, 68, 0.16) 0%, #111827 85%) !important;
            border: 1.5px solid #EF4444 !important;
            border-top: 4px solid #F59E0B !important;
            box-shadow: 0 0 18px rgba(239, 68, 68, 0.42), inset 0 0 12px rgba(245, 158, 11, 0.15) !important;
        }
        .noc-rack-cooled {
            background: linear-gradient(180deg, rgba(16, 185, 129, 0.16) 0%, #111827 85%) !important;
            border: 1.5px solid #10B981 !important;
            border-top: 4px solid #06B6D4 !important;
            box-shadow: 0 0 14px rgba(16, 185, 129, 0.28) !important;
        }
        .noc-rack-top {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 6px;
        }
        .noc-rack-id {
            font-size: 1.02rem;
            font-weight: 800;
            color: #F9FAFB;
            letter-spacing: 0.03em;
        }
        .noc-rack-kw {
            font-size: 0.75rem;
            font-weight: 600;
            color: #38BDF8;
            background: rgba(56, 189, 248, 0.12);
            border: 1px solid rgba(56, 189, 248, 0.3);
            padding: 2px 7px;
            border-radius: 6px;
        }
        .noc-temp-readout {
            font-size: 1.38rem;
            font-weight: 800;
            margin: 4px 0 2px 0;
            letter-spacing: -0.01em;
        }
        .noc-pressure-readout {
            font-size: 0.78rem;
            color: #D1D5DB;
            margin-bottom: 6px;
        }
        .noc-badge-hotspot {
            display: inline-block;
            background: rgba(239, 68, 68, 0.2);
            color: #FCA5A5;
            border: 1px solid #EF4444;
            border-radius: 6px;
            padding: 3px 7px;
            font-size: 0.69rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.03em;
        }
        .noc-badge-optimal {
            display: inline-block;
            background: rgba(16, 185, 129, 0.15);
            color: #6EE7B7;
            border: 1px solid rgba(16, 185, 129, 0.4);
            border-radius: 6px;
            padding: 3px 7px;
            font-size: 0.69rem;
            font-weight: 700;
            letter-spacing: 0.02em;
        }
        .noc-badge-blindspot {
            display: inline-block;
            background: rgba(31, 41, 55, 0.95);
            color: #9CA3AF;
            border: 1px solid #4B5563;
            border-radius: 6px;
            padding: 6px 8px;
            font-size: 0.73rem;
            font-weight: 600;
            line-height: 1.3;
            text-align: center;
            margin: 8px 0;
        }
        .noc-crac-banner {
            display: flex;
            flex-wrap: wrap;
            justify-content: space-between;
            align-items: center;
            gap: 10px;
            background: linear-gradient(90deg, rgba(16, 185, 129, 0.18) 0%, rgba(6, 182, 212, 0.12) 100%);
            border: 1px solid #10B981;
            border-left: 5px solid #10B981;
            border-radius: 10px;
            padding: 12px 16px;
            margin: 10px 0 14px 0;
        }
        .noc-crac-pill {
            background: #10B981;
            color: #0B0F19;
            font-weight: 800;
            font-size: 0.85rem;
            padding: 5px 12px;
            border-radius: 999px;
            letter-spacing: 0.03em;
            box-shadow: 0 0 14px rgba(16, 185, 129, 0.45);
        }
        .noc-tier1-banner {
            background: linear-gradient(90deg, rgba(31, 41, 55, 0.9) 0%, rgba(17, 24, 39, 0.95) 100%);
            border: 1px solid #374151;
            border-left: 4px solid #F59E0B;
            border-radius: 10px;
            padding: 12px 16px;
            margin: 8px 0 14px 0;
            color: #E5E7EB;
            font-size: 0.86rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _build_rack_card_html(rack: Dict[str, Any], tier_key: str, is_closed_loop: bool) -> str:
    """Render an individual rack HTML card according to active tier and closed-loop state."""
    rack_id = str(rack["rack_id"])
    kw_load = float(rack["kw_load"])
    inlet_temp_c = float(rack["inlet_temp_c"])
    diff_pressure_pa = float(rack["diff_pressure_pa"])
    baseline_temp_c = float(rack["baseline_inlet_temp_c"])
    is_hotspot = bool(rack["is_hotspot"])

    # Tier 1: Mask 6 sub-rack blind-spot racks in muted slate (#1F2937 / #9CA3AF)
    if tier_key == "Tier 1":
        if rack_id in TIER1_MASKED_RACKS:
            return (
                f'<div class="noc-rack-card noc-rack-masked">'
                f'  <div class="noc-rack-top">'
                f'    <span class="noc-rack-id" style="color: #9CA3AF;">{rack_id}</span>'
                f'    <span style="font-size: 0.72rem; color: #9CA3AF; border: 1px solid #4B5563; border-radius: 5px; padding: 1px 6px;">PDU Est. {kw_load:.1f} kW</span>'
                f'  </div>'
                f'  <div class="noc-badge-blindspot">'
                f'    🔒 Sensor Blind Spot<br/><span style="font-size: 0.68rem; color: #9CA3AF;">(Unlock in Tier 2)</span>'
                f'  </div>'
                f'  <div style="font-size: 0.70rem; color: #9CA3AF; text-align: center;">'
                f'    No Sub-Rack Temp / ΔP Probe'
                f'  </div>'
                f'</div>'
            )
        return (
            f'<div class="noc-rack-card">'
            f'  <div class="noc-rack-top">'
            f'    <span class="noc-rack-id">{rack_id}</span>'
            f'    <span class="noc-rack-kw">⚡ {kw_load:.1f} kW</span>'
            f'  </div>'
            f'  <div style="margin: 8px 0;">'
            f'    <div style="font-size: 0.72rem; color: #9CA3AF; text-transform: uppercase;">PDU Feed Load</div>'
            f'    <div style="font-size: 1.28rem; font-weight: 800; color: #F9FAFB;">{kw_load:.2f} kW</div>'
            f'  </div>'
            f'  <div style="font-size: 0.71rem; color: #9CA3AF; border-top: 1px solid #1F2937; padding-top: 6px;">'
            f'    📡 Smart PDU Metered · Sub-Rack Thermal in Tier 2'
            f'  </div>'
            f'</div>'
        )

    # Tier 2 or Tier 3 (Toggle OFF -> Hotspot State)
    if is_hotspot:
        return (
            f'<div class="noc-rack-card noc-rack-hotspot">'
            f'  <div class="noc-rack-top">'
            f'    <span class="noc-rack-id">{rack_id}</span>'
            f'    <span class="noc-rack-kw">⚡ {kw_load:.1f} kW</span>'
            f'  </div>'
            f'  <div>'
            f'    <div class="noc-temp-readout" style="color: #F87171;">🌡️ {inlet_temp_c:.1f}°C</div>'
            f'    <div class="noc-pressure-readout" style="color: #FBBF24;">💨 ΔP: <strong>{diff_pressure_pa:.1f} Pa</strong> (Low)</div>'
            f'  </div>'
            f'  <div class="noc-badge-hotspot">'
            f'    ⚠️ Hotspot Alert (&gt;27°C)'
            f'  </div>'
            f'</div>'
        )

    # Tier 3 (Toggle ON) for remediated hotspot racks R03, R08, R11
    if is_closed_loop and rack_id in HOTSPOT_RACK_IDS:
        temp_drop = baseline_temp_c - inlet_temp_c
        return (
            f'<div class="noc-rack-card noc-rack-cooled">'
            f'  <div class="noc-rack-top">'
            f'    <span class="noc-rack-id">{rack_id}</span>'
            f'    <span class="noc-rack-kw">⚡ {kw_load:.1f} kW</span>'
            f'  </div>'
            f'  <div>'
            f'    <div class="noc-temp-readout" style="color: #34D399;">❄️ {inlet_temp_c:.1f}°C</div>'
            f'    <div class="noc-pressure-readout">💨 ΔP: <strong>{diff_pressure_pa:.1f} Pa</strong> (+{temp_drop:.1f}°C cooled)</div>'
            f'  </div>'
            f'  <div class="noc-badge-optimal">'
            f'    ✔ AI Remediated · ASHRAE A1'
            f'  </div>'
            f'</div>'
        )

    # Standard healthy rack in Tier 2 or Tier 3
    return (
        f'<div class="noc-rack-card">'
        f'  <div class="noc-rack-top">'
        f'    <span class="noc-rack-id">{rack_id}</span>'
        f'    <span class="noc-rack-kw">⚡ {kw_load:.1f} kW</span>'
        f'  </div>'
        f'  <div>'
        f'    <div class="noc-temp-readout" style="color: #10B981;">🌡️ {inlet_temp_c:.1f}°C</div>'
        f'    <div class="noc-pressure-readout">💨 ΔP: <strong>{diff_pressure_pa:.1f} Pa</strong></div>'
        f'  </div>'
        f'  <div class="noc-badge-optimal">'
        f'    ✔ Optimal (&lt;24°C · ASHRAE A1)'
        f'  </div>'
        f'</div>'
    )


def render_tab_floorplan(sim: dict, params: dict) -> None:
    """
    Render Tab 2: 2-Row x 6-Rack (R01–R12) NOC Thermal Floorplan for GreenCore Bengaluru.
    """
    _inject_floorplan_css()

    fin = sim["financials"]
    tier_key: str = fin["tier_key"]
    baseline_kwh: float = float(params.get("baseline_kwh", fin["baseline_kwh"]))
    baseline_pue: float = float(params.get("baseline_pue", fin["baseline_pue"]))

    st.subheader("2. Rack & Thermal Floorplan — Bengaluru Data Hall A (R01–R12)")
    st.caption(
        "Interactive 2-Row × 6-Rack Network Operations Center (NOC) thermal and differential-pressure "
        "twin for **GreenCore Data Services Pvt. Ltd., Bengaluru** (ASHRAE A1 upper cold-aisle threshold: **27.0°C**)."
    )

    # -----------------------------------------------------------------------
    # Tier-Specific Banner & Interactive Phase-2 Closed-Loop Control Toggle
    # -----------------------------------------------------------------------
    if tier_key == "Tier 1":
        st.markdown(
            """
            <div class="noc-tier1-banner">
                <strong>🔒 Tier 1 Telemetry Scope (PDU & Facility Level Only):</strong>
                In the 12-week PoC (`₹8,20,000`), GreenCompute ingests 15-minute main incomer, UPS, chiller, and rack PDU power draw (`kW`).
                <strong>6 of 12 racks (`R02, R03, R06, R08, R10, R11`) lack sub-rack inlet temperature and differential pressure probes</strong>,
                creating thermal blind spots where hot-air recirculation goes undetected.
                <em>Select <strong>Tier 2</strong> or <strong>Tier 3</strong> in the sidebar to deploy the 48-sensor LoRaWAN thermal mesh and unlock full cold-aisle visibility.</em>
            </div>
            """,
            unsafe_allow_html=True,
        )
        active_rack_thermal = sim["rack_thermal"]

    elif tier_key == "Tier 2":
        st.info(
            "📡 **Tier 2 Sub-Rack LoRaWAN Sensor Mesh Unlocked (48 Wireless Probes):** "
            "Cold-aisle inlet temperature (°C) and under-floor differential pressure (Pa) are now visible across all 12 racks. "
            "**Alert:** High-density compute racks **`R03` (27.8°C)**, **`R08` (28.2°C)**, and **`R11` (27.6°C)** suffer from "
            "low under-floor static pressure (`10.6–11.8 Pa`) and hot-air recirculation exceeding the **27.0°C ASHRAE A1** envelope."
        )
        active_rack_thermal = sim["rack_thermal"]

    else:
        # Tier 3: Interactive Toggle for Phase-2 AI Closed-Loop Cooling Control
        toggle_col, caption_col = st.columns([1.25, 2.25])
        with toggle_col:
            closed_loop_on = st.toggle(
                "Simulate Phase-2 AI Closed-Loop Cooling Control",
                value=True,
                key="tier3_closed_loop_toggle",
                help="Toggle between Open-Loop Containment (Tier 2 Hotspot State) and Phase-2 AI Closed-Loop VFD HVAC Control.",
            )
            st.session_state["tier3_closed_loop_override"] = closed_loop_on

        with caption_col:
            st.caption(
                "🛡️ **Phase-2 Engineering Safety Sign-Off:** Closed-loop AI modulation of CRAC Variable Frequency Drives (VFDs) "
                "and motorized floor dampers is gated behind formal facility engineering sign-off following the 12-week human-in-the-loop pilot. "
                "Hardware fail-safes enforce ASHRAE A1 bounds (`18°C–27°C`) with instant local BMS fallback."
            )

        if closed_loop_on:
            active_rack_thermal = generate_12rack_thermal_telemetry(
                selected_tier="Tier 3",
                baseline_kwh=baseline_kwh,
                baseline_pue=baseline_pue,
                tier3_closed_loop_active=True,
            )
            st.markdown(
                """
                <div class="noc-crac-banner">
                    <div>
                        <div style="color: #F9FAFB; font-weight: 700; font-size: 0.96rem;">
                            ✅ Phase-2 AI Closed-Loop VFD Control Engaged · All 12 Racks Balanced (21.3°C–22.6°C)
                        </div>
                        <div style="color: #D1D5DB; font-size: 0.81rem; margin-top: 2px;">
                            Hotspots <strong>R03 (22.2°C)</strong>, <strong>R08 (22.6°C)</strong>, and <strong>R11 (21.9°C)</strong> remediated via dynamic under-floor plenum pressure balancing (<strong>19.2–20.5 Pa</strong>) and fan affinity-law modulation.
                        </div>
                    </div>
                    <span class="noc-crac-pill">⚡ -22% CRAC Fan Power Reduction</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            # When toggle is OFF in Tier 3, display Tier 2 hotspot state (>27.5°C on R03, R08, R11)
            active_rack_thermal = generate_12rack_thermal_telemetry(
                selected_tier="Tier 2",
                baseline_kwh=baseline_kwh,
                baseline_pue=baseline_pue,
                tier3_closed_loop_active=False,
            )
            st.warning(
                "⚠️ **AI Closed-Loop Control Disengaged (Static Containment State):** "
                "Without dynamic VFD & plenum damper modulation, high-density racks **`R03` (27.8°C)**, "
                "**`R08` (28.2°C)**, and **`R11` (27.6°C)** revert to hot-air recirculation (`>27.5°C`) due to "
                "localized pressure drops (`10.6–11.8 Pa`). Switch the toggle **ON** to simulate Phase-2 closed-loop remediation."
            )

    racks_df: pd.DataFrame = active_rack_thermal["racks_df"]
    is_closed_loop: bool = bool(active_rack_thermal["is_closed_loop"])
    hotspot_racks = active_rack_thermal["hotspot_racks"]
    max_inlet_temp_c: float = float(active_rack_thermal["max_inlet_temp_c"])
    mean_inlet_temp_c: float = float(active_rack_thermal["mean_inlet_temp_c"])
    crac_delta_pct: float = float(active_rack_thermal["crac_fan_power_delta_pct"])

    # -----------------------------------------------------------------------
    # Summary Thermal & Airflow KPI Strip
    # -----------------------------------------------------------------------
    k1, k2, k3, k4, k5 = st.columns(5)
    with k1:
        if tier_key == "Tier 1":
            st.metric(
                "Sensor Mesh Coverage",
                "6 / 12 Racks",
                "6 Racks Masked (Tier 1)",
                delta_color="off",
            )
        elif is_closed_loop:
            st.metric(
                "Active HVAC Mode",
                "AI Closed-Loop",
                "12 / 12 Racks Balanced",
                delta_color="normal",
            )
        else:
            st.metric(
                "Active HVAC Mode",
                "Open-Loop Advisory",
                "Static Containment",
                delta_color="off",
            )

    with k2:
        if tier_key == "Tier 1":
            st.metric(
                "Max Rack Inlet Temp",
                "🔒 Blind Spot",
                "Unlock LoRaWAN in Tier 2",
                delta_color="off",
            )
        else:
            ashrae_margin = max_inlet_temp_c - 27.0
            st.metric(
                "Max Rack Inlet Temp",
                f"{max_inlet_temp_c:.1f} °C",
                f"{ashrae_margin:+.1f}°C vs 27°C ASHRAE A1",
                delta_color="inverse",
            )

    with k3:
        if tier_key == "Tier 1":
            st.metric(
                "Mean Cold-Aisle Temp",
                "🔒 Unmetered",
                "PDU Power Only in Tier 1",
                delta_color="off",
            )
        else:
            st.metric(
                "Mean Cold-Aisle Temp",
                f"{mean_inlet_temp_c:.1f} °C",
                "Target Band: 21.5–22.8°C",
                delta_color="normal" if is_closed_loop else "off",
            )

    with k4:
        if tier_key == "Tier 1":
            st.metric(
                "Detected Hotspots",
                "❓ Unknown",
                "R03, R08, R11 Unmonitored",
                delta_color="off",
            )
        else:
            hotspot_count = len(hotspot_racks)
            hotspot_str = ", ".join(hotspot_racks) if hotspot_racks else "None (All ASHRAE A1)"
            st.metric(
                "Active Hotspots (>27°C)",
                f"{hotspot_count} Racks",
                hotspot_str,
                delta_color="inverse" if hotspot_count > 0 else "normal",
            )

    with k5:
        st.metric(
            "CRAC Fan Power Delta",
            f"{crac_delta_pct:+.1f}%",
            "-22% VFD Affinity Law" if is_closed_loop else ("Static VFD Trim" if tier_key == "Tier 2" else "Baseline Fixed-Speed"),
            delta_color="normal" if crac_delta_pct < 0 else "off",
        )

    # -----------------------------------------------------------------------
    # Custom HTML/CSS 2-Row × 6-Rack NOC Floorplan
    # -----------------------------------------------------------------------
    row_a_records = racks_df[racks_df["row_idx"] == 0].to_dict(orient="records")
    row_b_records = racks_df[racks_df["row_idx"] == 1].to_dict(orient="records")

    row_a_cards_html = "".join(
        _build_rack_card_html(r, tier_key=tier_key, is_closed_loop=is_closed_loop)
        for r in row_a_records
    )
    row_b_cards_html = "".join(
        _build_rack_card_html(r, tier_key=tier_key, is_closed_loop=is_closed_loop)
        for r in row_b_records
    )

    total_it_kw = float(racks_df["kw_load"].sum())
    mode_badge_html = (
        '<span class="noc-crac-pill">⚡ -22% CRAC Fan Power Reduction</span>'
        if is_closed_loop
        else (
            '<span class="noc-badge-hotspot">⚠️ 3 Active Hotspots: R03, R08, R11 (&gt;27.5°C)</span>'
            if tier_key != "Tier 1"
            else '<span style="color: #9CA3AF; font-size: 0.8rem; font-weight: 600;">🔒 6 Sub-Rack Thermal Blind Spots (Tier 1)</span>'
        )
    )

    floorplan_html = (
        f'<div class="noc-container">'
        f'  <div class="noc-header-bar">'
        f'    <div>'
        f'      <div style="font-size: 1.05rem; font-weight: 800; color: #F9FAFB;">'
        f'        🏢 GreenCore Bengaluru — Data Hall A Floorplan (2 Rows × 6 Racks · Total IT Load: {total_it_kw:.1f} kW)'
        f'      </div>'
        f'      <div style="font-size: 0.80rem; color: #9CA3AF; margin-top: 2px;">'
        f'        Active Control State: <strong>{active_rack_thermal["control_mode_label"]}</strong>'
        f'      </div>'
        f'    </div>'
        f'    <div>{mode_badge_html}</div>'
        f'  </div>'
        f'  <div class="noc-aisle-label">'
        f'    <span>❄️ Row A — North Cold Aisle (Perforated Floor Supply · R01–R06)</span>'
        f'    <span>CRAC-01 &amp; CRAC-02 Supply Plenum</span>'
        f'  </div>'
        f'  <div class="noc-rack-grid">{row_a_cards_html}</div>'
        f'  <div class="noc-hot-aisle-label">'
        f'    <span>🔥 Central Contained Hot-Aisle Exhaust Corridor (Rear Server Exhaust Return to CRAC)</span>'
        f'    <span>{"✔ Containment + AI VFD Damper Balance Active" if is_closed_loop else ("⚠️ Recirculation Bypass at R03, R08, R11" if tier_key != "Tier 1" else "Uncontainment / Manual Baffles")}</span>'
        f'  </div>'
        f'  <div class="noc-rack-grid">{row_b_cards_html}</div>'
        f'  <div class="noc-aisle-label">'
        f'    <span>❄️ Row B — South Cold Aisle (Perforated Floor Supply · R07–R12)</span>'
        f'    <span>CRAC-03 &amp; CRAC-04 Supply Plenum</span>'
        f'  </div>'
        f'</div>'
    )

    st.markdown(floorplan_html, unsafe_allow_html=True)

    # -----------------------------------------------------------------------
    # Expandable Full 12-Rack Telemetry Schedule & Engineering Notes
    # -----------------------------------------------------------------------
    with st.expander("📋 View Full 12-Rack Telemetry Schedule (R01–R12) & Root-Cause Diagnostics", expanded=False):
        display_df = racks_df[
            [
                "rack_id",
                "row_name",
                "kw_load",
                "inlet_temp_c",
                "baseline_inlet_temp_c",
                "tier3_inlet_temp_c",
                "diff_pressure_pa",
                "airflow_status",
            ]
        ].copy()

        if tier_key == "Tier 1":
            mask = display_df["rack_id"].isin(TIER1_MASKED_RACKS)
            display_df["Inlet Temp (°C)"] = display_df["inlet_temp_c"].map(lambda x: f"{x:.1f} °C")
            display_df.loc[mask, "Inlet Temp (°C)"] = "🔒 Blind Spot (Tier 2)"
            display_df["Diff Pressure (Pa)"] = display_df["diff_pressure_pa"].map(lambda x: f"{x:.1f} Pa")
            display_df.loc[mask, "Diff Pressure (Pa)"] = "🔒 Blind Spot (Tier 2)"
            display_df["Telemetry Status"] = display_df["rack_id"].map(
                lambda r: "🔒 Sensor Blind Spot (Unlock in Tier 2)"
                if r in TIER1_MASKED_RACKS
                else "📡 PDU Power Metered Only"
            )
            table_out = pd.DataFrame(
                {
                    "Rack ID": display_df["rack_id"],
                    "Aisle Row": display_df["row_name"],
                    "IT Load (kW)": display_df["kw_load"].map(lambda x: f"{x:.2f} kW"),
                    "Cold-Aisle Inlet Temp": display_df["Inlet Temp (°C)"],
                    "Under-Floor ΔP": display_df["Diff Pressure (Pa)"],
                    "Diagnostic Status": display_df["Telemetry Status"],
                }
            )
        else:
            table_out = pd.DataFrame(
                {
                    "Rack ID": display_df["rack_id"],
                    "Aisle Row": display_df["row_name"],
                    "IT Load (kW)": display_df["kw_load"].map(lambda x: f"{x:.2f} kW"),
                    "Active Inlet Temp (°C)": display_df["inlet_temp_c"].map(lambda x: f"{x:.1f} °C"),
                    "Tier 1 Baseline (°C)": display_df["baseline_inlet_temp_c"].map(lambda x: f"{x:.1f} °C"),
                    "Tier 3 Closed-Loop (°C)": display_df["tier3_inlet_temp_c"].map(lambda x: f"{x:.1f} °C"),
                    "Active ΔP (Pa)": display_df["diff_pressure_pa"].map(lambda x: f"{x:.1f} Pa"),
                    "Airflow & ASHRAE Status": display_df["airflow_status"],
                }
            )

        st.dataframe(table_out, use_container_width=True, hide_index=True)
        st.caption(
            "**Root-Cause Physics Note:** High-density racks **`R03`**, **`R08`**, and **`R11`** draw ~21%–28% higher IT power than adjacent racks. "
            "Without under-floor damper balancing and VFD supply modulation, localized Venturi pressure drops (`<12 Pa`) draw hot exhaust air "
            "over the top and around unsealed cable grommets into the cold aisle (`>27.5°C`). Tier 3 AI Closed-Loop control restores `19.2–20.5 Pa` "
            "static pressure while trimming aggregate CRAC fan speed by **22%** via the cubic fan affinity law ($P \\propto N^3$)."
        )
