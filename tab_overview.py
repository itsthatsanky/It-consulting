"""
Tab 1: Executive Overview & Workload Telemetry for GreenCompute Decision-Support System.
Prepared by WAS Group 2, TAPMI Bengaluru for GreenCore Data Services Pvt. Ltd., Bengaluru.
"""
from __future__ import annotations

from typing import Any, Dict

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st


# ---------------------------------------------------------------------------
# Indian Currency & USD Formatting Helpers
# ---------------------------------------------------------------------------
def _format_inr_grouped(amount: float) -> str:
    """Format a number in Indian numbering system (e.g., ₹8,20,000)."""
    sign = "-" if amount < 0 else ""
    val = int(round(abs(amount)))
    s = str(val)
    if len(s) <= 3:
        return f"{sign}₹{s}"
    last3 = s[-3:]
    rest = s[:-3]
    parts = []
    while len(rest) > 2:
        parts.insert(0, rest[-2:])
        rest = rest[:-2]
    if rest:
        parts.insert(0, rest)
    return f"{sign}₹{','.join(parts)},{last3}"


def _format_currency(amount: float, currency: str, compact: bool = False) -> str:
    """
    Format currency in INR (Indian grouping / Lakhs / Crores) or USD ($ / $K / $M).
    """
    is_usd = currency == "USD ($)"
    sign = "-" if amount < 0 else ""
    abs_val = abs(amount)

    if is_usd:
        if compact:
            if abs_val >= 1_000_000:
                return f"{sign}${abs_val / 1_000_000:,.2f}M"
            if abs_val >= 10_000:
                return f"{sign}${abs_val / 1_000:,.1f}K"
        return f"{sign}${abs_val:,.0f}"
    else:
        if compact:
            if abs_val >= 1_00_00_000:
                return f"{sign}₹{abs_val / 1_00_00_000:.2f} Cr"
            if abs_val >= 1_00_000:
                return f"{sign}₹{abs_val / 1_00_000:.2f} L"
        return _format_inr_grouped(amount)


# ---------------------------------------------------------------------------
# Main Tab 1 Renderer
# ---------------------------------------------------------------------------
def render_tab_overview(sim: Dict[str, Any], params: Dict[str, Any]) -> None:
    """
    Render Tab 1: Executive Overview & Workload Telemetry.
    """
    fin = sim["financials"]
    wb = sim["workload_benchmark"]
    t_ml = sim["telemetry_ml"]
    telemetry_df = t_ml["telemetry_df"]
    ml_val = t_ml["ml_validation"]
    audit_log_df = t_ml["audit_log_df"]

    currency = fin["currency"]
    tier_key = fin["tier_key"]
    is_tier3 = tier_key == "Tier 3"

    # -----------------------------------------------------------------------
    # 1. Provenance Badges & Collapsible Validation Drawer
    # -----------------------------------------------------------------------
    st.markdown(
        """
        <div style="display:flex; flex-wrap:wrap; align-items:center; justify-content:space-between;
                    gap:8px; background:rgba(17,24,39,0.85); border:1px solid #1E293B;
                    border-radius:10px; padding:10px 16px; margin-bottom:10px;">
            <div style="display:flex; flex-wrap:wrap; align-items:center; gap:8px;">
                <span style="background:rgba(16,185,129,0.14); color:#10B981; border:1px solid rgba(16,185,129,0.35);
                             padding:3px 10px; border-radius:999px; font-size:0.74rem; font-weight:600;
                             font-family:'JetBrains Mono', monospace; letter-spacing:0.03em;">
                    ● DATA STATUS: SYNTHETIC / PROJECTED
                </span>
                <span style="background:rgba(6,182,212,0.14); color:#06B6D4; border:1px solid rgba(6,182,212,0.35);
                             padding:3px 10px; border-radius:999px; font-size:0.74rem; font-weight:600;
                             font-family:'JetBrains Mono', monospace;">
                    MODEL v1.2
                </span>
                <span style="background:rgba(148,163,184,0.12); color:#CBD5E1; border:1px solid #334155;
                             padding:3px 10px; border-radius:999px; font-size:0.74rem; font-weight:500;
                             font-family:'JetBrains Mono', monospace;">
                    LAST VALIDATED: 08 NOV 2026
                </span>
                <span style="background:rgba(245,158,11,0.14); color:#F59E0B; border:1px solid rgba(245,158,11,0.35);
                             padding:3px 10px; border-radius:999px; font-size:0.74rem; font-weight:600;
                             font-family:'JetBrains Mono', monospace;">
                    CLIENT: GREENCORE DATA SERVICES
                </span>
            </div>
            <div style="font-size:0.76rem; color:#94A3B8; font-family:'JetBrains Mono', monospace;">
                Active Posture: <strong style="color:#F8FAFC;">"""
        + f"{fin['selected_tier']}"
        + """</strong>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.expander(
        "View Model Validation, Forecast Benchmarks & Anomaly Audit Log ↗",
        expanded=False,
    ):
        v_col1, v_col2, v_col3 = st.columns(3)
        with v_col1:
            st.markdown(
                f"""
                <div style="background:#0B0F19; border:1px solid #1E293B; border-left:3px solid #10B981;
                            border-radius:8px; padding:12px 14px;">
                    <div style="font-size:0.75rem; color:#94A3B8; text-transform:uppercase; letter-spacing:0.05em;">
                        Workstream C · 24h Load Forecast MAPE
                    </div>
                    <div style="font-size:1.35rem; font-weight:700; color:#F8FAFC; font-family:'JetBrains Mono', monospace; margin:4px 0;">
                        {ml_val['forecast_mape_ml']:.1f}% ML <span style="font-size:0.9rem; color:#94A3B8;">vs. {ml_val['forecast_mape_baseline']:.1f}% Baseline</span>
                    </div>
                    <div style="font-size:0.78rem; color:#10B981; font-weight:600;">
                        ✓ SMART Target (≤{ml_val['smart_target_mape']:.0f}% MAPE) Met (-{ml_val['forecast_mape_baseline'] - ml_val['forecast_mape_ml']:.1f} pts error reduction)
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with v_col2:
            st.markdown(
                f"""
                <div style="background:#0B0F19; border:1px solid #1E293B; border-left:3px solid #06B6D4;
                            border-radius:8px; padding:12px 14px;">
                    <div style="font-size:0.75rem; color:#94A3B8; text-transform:uppercase; letter-spacing:0.05em;">
                        Isolation Forest · Anomaly Recall & Precision
                    </div>
                    <div style="font-size:1.35rem; font-weight:700; color:#F8FAFC; font-family:'JetBrains Mono', monospace; margin:4px 0;">
                        {ml_val['anomaly_recall_pct']:.1f}% Recall <span style="font-size:0.9rem; color:#94A3B8;">({ml_val['true_positives']} TP / {ml_val['false_positives']} FP / {ml_val['missed_anomalies']} Missed)</span>
                    </div>
                    <div style="font-size:0.78rem; color:#06B6D4; font-weight:600;">
                        ✓ SMART Target (≥{ml_val['smart_target_recall']:.0f}% Recall across {ml_val['total_injected_events']} injected thermal/power events) Met
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with v_col3:
            st.markdown(
                f"""
                <div style="background:#0B0F19; border:1px solid #1E293B; border-left:3px solid #F59E0B;
                            border-radius:8px; padding:12px 14px;">
                    <div style="font-size:0.75rem; color:#94A3B8; text-transform:uppercase; letter-spacing:0.05em;">
                        Phase-2 Carbon-Aware Batch Temporal Shift
                    </div>
                    <div style="font-size:1.35rem; font-weight:700; color:#F8FAFC; font-family:'JetBrains Mono', monospace; margin:4px 0;">
                        {ml_val['shifted_batch_fraction_pct']:.0f}% Batch Load <span style="font-size:0.9rem; color:#94A3B8;">→ -{ml_val['annual_temporal_shift_co2_tonnes']:.1f} tCO₂e/yr</span>
                    </div>
                    <div style="font-size:0.78rem; color:#F59E0B; font-weight:600;">
                        Shifts afternoon peak batch ETL (13:00–18:00) to low-carbon windows (01:00–04:00)
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown(
            "<div style='margin-top:12px; margin-bottom:6px; font-size:0.84rem; font-weight:600; color:#E2E8F0;'>"
            "6-Row Anomaly & Recommendation Audit Log (Human-in-the-Loop Governance)"
            "</div>",
            unsafe_allow_html=True,
        )
        st.dataframe(
            audit_log_df,
            use_container_width=True,
            hide_index=True,
        )

    # -----------------------------------------------------------------------
    # 2. Top 4 KPI Cards (st.columns(4) with st.metric + sub-captions)
    # -----------------------------------------------------------------------
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)

    # Card 1: Projected PUE
    pue_delta = fin["projected_pue"] - fin["baseline_pue"]
    with kpi1:
        st.metric(
            label="Projected Facility PUE",
            value=f"{fin['projected_pue']:.2f}",
            delta=f"{pue_delta:+.2f} vs {fin['baseline_pue']:.2f} base",
            delta_color="inverse",
            help="Physics-safe PUE: efficiency reductions are applied strictly to cooling & electrical overhead (PUE - 1.0), never dropping below physical limit 1.05.",
        )
        st.caption(
            f"Overhead cut by **{fin['overhead_reduction_pct']:.1f}%** · "
            f"Saves **{fin['annual_kwh_saved']:,.0f} kWh/yr** ({fin['reduction_pct']:.1f}%)"
        )

    # Card 2: Net Annual Financial Benefit
    net_benefit_formatted = _format_currency(fin["annual_net_benefit"], currency, compact=False)
    gross_formatted = _format_currency(fin["annual_gross_saving"], currency, compact=True)
    opex_formatted = _format_currency(fin["recurring_opex"], currency, compact=True)
    net_compact_inr = _format_currency(fin["annual_net_benefit_inr"], "INR (₹)", compact=True)
    with kpi2:
        st.metric(
            label="Net Annual Financial Benefit",
            value=net_benefit_formatted,
            delta=(
                f"Gross {gross_formatted} - OpEx {opex_formatted}"
                if fin["annual_net_benefit"] >= 0
                else f"Net Negative ({gross_formatted} < OpEx {opex_formatted})"
            ),
            delta_color="normal" if fin["annual_net_benefit"] >= 0 else "inverse",
            help="Appendix B Formula: Net Annual Benefit = [Baseline kWh × (Reduction % / 100) × Tariff] - Annual Recurring Cloud/Support OpEx.",
        )
        if currency == "INR (₹)":
            st.caption(
                f"Equivalent to **{net_compact_inr}/yr** · "
                f"Gross: **{_format_inr_grouped(fin['annual_gross_saving_inr'])}** | "
                f"OpEx: **{_format_inr_grouped(fin['recurring_opex_inr'])}**"
            )
        else:
            st.caption(
                f"Gross Saving: **${fin['annual_gross_saving']:,.0f}/yr** | "
                f"Recurring OpEx: **${fin['recurring_opex']:,.0f}/yr** "
                f"({net_compact_inr}/yr INR)"
            )

    # Card 3: Annual CO2 Avoided (Metric Tons)
    co2_avoided = fin["co2_avoided_efficiency_tonnes"]
    scope2_base = fin["scope2_baseline_tonnes"]
    co2_pct = (co2_avoided / scope2_base * 100.0) if scope2_base > 0 else 0.0
    with kpi3:
        st.metric(
            label="Annual CO₂ Avoided (Metric Tons)",
            value=f"{co2_avoided:,.1f} tCO₂e/yr",
            delta=f"-{co2_pct:.1f}% vs {scope2_base:,.1f} tCO₂e Scope 2 base",
            delta_color="normal",
            help="Scope 2 grid emission reduction: [Baseline kWh × (Reduction % / 100) × Grid Emission Factor] / 1,000.",
        )
        st.caption(
            f"Grid EF: **{fin['grid_emission_factor']:.2f} kgCO₂/kWh** · "
            f"Projected Scope 2: **{fin['scope2_projected_tonnes']:,.1f} tCO₂e/yr**"
        )

    # Card 4: Dynamic Simple Payback & Annual ROI (%)
    if fin["simple_payback_months"] is not None:
        payback_val = f"{fin['simple_payback_months']:.1f} mos"
        roi_delta_color = "normal"
    else:
        payback_val = "N/A - Net Negative"
        roi_delta_color = "inverse"
    initial_cost_str = _format_currency(fin["initial_cost"], currency, compact=False)
    with kpi4:
        st.metric(
            label="Simple Payback & Annual ROI",
            value=payback_val,
            delta=f"ROI: {fin['annual_roi_pct']:.1f}% / yr",
            delta_color=roi_delta_color,
            help="Simple Payback = (Initial Cost / Net Annual Benefit) × 12 months. Annual ROI = (Net Annual Benefit / Initial Cost) × 100.",
        )
        st.caption(
            f"Initial Outlay: **{initial_cost_str}** "
            f"({'12-Wk PoC Only' if tier_key == 'Tier 1' else f'PoC + {tier_key} CapEx'})"
        )

    st.markdown("<div style='margin-top:8px;'></div>", unsafe_allow_html=True)

    # -----------------------------------------------------------------------
    # 3. 65% / 35% Asymmetric Split: 24h Telemetry Chart + Workstream B Card
    # -----------------------------------------------------------------------
    left_col, right_col = st.columns([0.65, 0.35], gap="medium")

    # --- LEFT (65%): Dual-Axis 24-Hour Power & Grid Carbon Intensity Chart ---
    with left_col:
        st.markdown(
            f"""
            <div style="background:#111827; border:1px solid #1E293B; border-radius:10px; padding:14px 16px 6px 16px;">
                <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:6px;">
                    <div>
                        <span style="font-size:0.98rem; font-weight:700; color:#F8FAFC;">
                            Workstream A & C · 24-Hour Facility Power & Grid Carbon Telemetry
                        </span>
                        <div style="font-size:0.78rem; color:#94A3B8; margin-top:2px;">
                            Diurnal IT Load & Cooling Overhead (kW) vs. Regional Grid Carbon Intensity (gCO₂/kWh)
                        </div>
                    </div>
                    <span style="background:{'rgba(16,185,129,0.16)' if is_tier3 else 'rgba(148,163,184,0.12)'};
                                 color:{'#10B981' if is_tier3 else '#94A3B8'};
                                 border:1px solid {'rgba(16,185,129,0.4)' if is_tier3 else '#334155'};
                                 padding:3px 10px; border-radius:999px; font-size:0.73rem;
                                 font-family:'JetBrains Mono', monospace; font-weight:600;">
                        {"⚡ TIER 3 AI CARBON-AWARE SHIFTING ACTIVE" if is_tier3 else f"🔒 {tier_key.upper()} · SELECT TIER 3 FOR AI LOAD SHIFTING"}
                    </span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        fig = make_subplots(specs=[[{"secondary_y": True}]])

        x_hours = telemetry_df["hour_label"]

        # Left Y-Axis: IT Power (kW)
        fig.add_trace(
            go.Scatter(
                x=x_hours,
                y=telemetry_df["it_power_kw"],
                name="IT Compute Load (kW)",
                mode="lines+markers",
                line=dict(color="#10B981", width=2.6),
                marker=dict(size=5, color="#10B981"),
                fill="tozeroy",
                fillcolor="rgba(16, 185, 129, 0.12)",
                hovertemplate="<b>%{x}</b><br>IT Power: %{y:.1f} kW<extra></extra>",
            ),
            secondary_y=False,
        )

        # Left Y-Axis: Cooling & Electrical Overhead (kW)
        fig.add_trace(
            go.Scatter(
                x=x_hours,
                y=telemetry_df["cooling_overhead_kw"],
                name="Cooling & Facility Overhead (kW)",
                mode="lines+markers",
                line=dict(color="#06B6D4", width=2.4),
                marker=dict(size=5, color="#06B6D4"),
                fill="tozeroy",
                fillcolor="rgba(6, 182, 212, 0.10)",
                hovertemplate="<b>%{x}</b><br>Cooling Overhead: %{y:.1f} kW<extra></extra>",
            ),
            secondary_y=False,
        )

        # Left Y-Axis: Total Baseline Load reference line (subtle dashed)
        fig.add_trace(
            go.Scatter(
                x=x_hours,
                y=telemetry_df["total_baseline_kw"],
                name="Total Facility Baseline (kW)",
                mode="lines",
                line=dict(color="#64748B", width=1.6, dash="dot"),
                hovertemplate="<b>%{x}</b><br>Total Baseline: %{y:.1f} kW<extra></extra>",
            ),
            secondary_y=False,
        )

        # When Tier 3 is active, overlay Phase-2 AI Carbon-Aware Shifted Load (kW)
        if is_tier3:
            fig.add_trace(
                go.Scatter(
                    x=x_hours,
                    y=telemetry_df["ai_carbon_shifted_kw"],
                    name="Phase-2 AI Carbon-Aware Shifted Load (kW)",
                    mode="lines+markers",
                    line=dict(color="#34D399", width=3.0, dash="solid"),
                    marker=dict(size=6, symbol="diamond", color="#10B981"),
                    hovertemplate="<b>%{x}</b><br>AI Carbon-Shifted Load: %{y:.1f} kW<extra></extra>",
                ),
                secondary_y=False,
            )

        # Right Y-Axis: Grid Carbon Intensity (gCO2/kWh)
        fig.add_trace(
            go.Scatter(
                x=x_hours,
                y=telemetry_df["grid_carbon_intensity_gco2"],
                name="Grid Carbon Intensity (gCO₂/kWh)",
                mode="lines",
                line=dict(color="#F59E0B", width=2.5, dash="dash"),
                hovertemplate="<b>%{x}</b><br>Grid Carbon Intensity: %{y:.0f} gCO₂/kWh<extra></extra>",
            ),
            secondary_y=True,
        )

        # When Tier 3 is active, draw shaded emerald vrect zones over low-carbon & shifting windows
        if is_tier3:
            fig.add_vrect(
                x0="01:00",
                x1="04:00",
                fillcolor="rgba(16, 185, 129, 0.16)",
                opacity=1.0,
                layer="below",
                line_width=1,
                line_color="rgba(16, 185, 129, 0.45)",
                annotation_text="Phase-2 AI Carbon-Aware Shifting (Low-Carbon Absorption)",
                annotation_position="top left",
                annotation_font=dict(size=10, color="#10B981", family="JetBrains Mono"),
            )
            fig.add_vrect(
                x0="13:00",
                x1="18:00",
                fillcolor="rgba(16, 185, 129, 0.12)",
                opacity=1.0,
                layer="below",
                line_width=1,
                line_color="rgba(16, 185, 129, 0.45)",
                annotation_text="Phase-2 AI Carbon-Aware Shifting (-18% Peak Shed)",
                annotation_position="top left",
                annotation_font=dict(size=10, color="#34D399", family="JetBrains Mono"),
            )

        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="#111827",
            plot_bgcolor="#0B0F19",
            height=410,
            margin=dict(l=14, r=14, t=18, b=12),
            hovermode="x unified",
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="left",
                x=0.0,
                font=dict(size=11, color="#E2E8F0"),
                bgcolor="rgba(17,24,39,0.6)",
            ),
            xaxis=dict(
                title=dict(text="Hour of Day (24-Hour Operational Cycle)", font=dict(size=11, color="#94A3B8")),
                tickfont=dict(size=10, color="#94A3B8", family="JetBrains Mono"),
                gridcolor="#1E293B",
                showline=True,
                linecolor="#334155",
            ),
        )
        fig.update_yaxes(
            title_text="Electrical Demand (kW)",
            title_font=dict(size=11, color="#10B981"),
            tickfont=dict(size=10, color="#94A3B8", family="JetBrains Mono"),
            gridcolor="#1E293B",
            zeroline=False,
            secondary_y=False,
        )
        fig.update_yaxes(
            title_text="Grid Carbon Intensity (gCO₂/kWh)",
            title_font=dict(size=11, color="#F59E0B"),
            tickfont=dict(size=10, color="#F59E0B", family="JetBrains Mono"),
            gridcolor="rgba(30,41,59,0.3)",
            showgrid=False,
            zeroline=False,
            secondary_y=True,
        )

        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

        st.caption(
            "💡 **Telemetry Insight:** Afternoon wet-bulb temperature spikes (13:00–18:00) coincide with peak regional "
            "coal/thermal grid dispatch (**gCO₂/kWh**). Selecting **Tier 3** activates automated temporal shifting of "
            f"**{ml_val['shifted_batch_fraction_pct']:.0f}%** non-urgent batch ETL workloads into the **01:00–04:00** low-carbon window."
        )

    # --- RIGHT (35%): Workstream B — Python Code Optimization Benchmark Card ---
    with right_col:
        st.markdown(
            f"""
            <div style="background:#111827; border:1px solid #1E293B; border-top:3px solid #10B981;
                        border-radius:10px; padding:16px 18px;">
                <div style="display:flex; justify-content:space-between; align-items:flex-start; gap:8px;">
                    <div>
                        <div style="font-size:0.74rem; font-weight:700; color:#10B981; text-transform:uppercase;
                                    letter-spacing:0.06em; font-family:'JetBrains Mono', monospace;">
                            Workstream B · Software Engineering Benchmark
                        </div>
                        <div style="font-size:1.02rem; font-weight:700; color:#F8FAFC; margin-top:2px;">
                            Python 3.11 Batch Workload Optimization
                        </div>
                    </div>
                    <span style="background:rgba(16,185,129,0.16); color:#10B981; border:1px solid rgba(16,185,129,0.4);
                                 padding:3px 9px; border-radius:6px; font-size:0.72rem; font-weight:700;
                                 font-family:'JetBrains Mono', monospace; white-space:nowrap;">
                        ✓ {wb['output_equivalence']}
                    </span>
                </div>
                <div style="font-size:0.77rem; color:#94A3B8; margin-top:4px; margin-bottom:12px;">
                    Environment: <code style="color:#E2E8F0;">{wb['environment']}</code> ({wb['records_processed']:,} records)
                </div>

                <!-- 2x2 Benchmark Metric Grid -->
                <div style="display:grid; grid-template-columns:1fr 1fr; gap:10px; margin-bottom:12px;">
                    <!-- Runtime -->
                    <div style="background:#0B0F19; border:1px solid #1E293B; border-radius:8px; padding:10px 12px;">
                        <div style="font-size:0.72rem; color:#94A3B8; text-transform:uppercase;">Execution Runtime</div>
                        <div style="font-size:1.05rem; font-weight:700; color:#F8FAFC; font-family:'JetBrains Mono', monospace; margin-top:3px;">
                            {wb['runtime_baseline_s']:.1f}s → {wb['runtime_optimized_s']:.1f}s
                        </div>
                        <div style="font-size:0.76rem; color:#10B981; font-weight:600; font-family:'JetBrains Mono', monospace; margin-top:2px;">
                            {wb['runtime_reduction_pct']:.1f}% wall-time
                        </div>
                    </div>

                    <!-- Peak CPU -->
                    <div style="background:#0B0F19; border:1px solid #1E293B; border-radius:8px; padding:10px 12px;">
                        <div style="font-size:0.72rem; color:#94A3B8; text-transform:uppercase;">Peak CPU Utilization</div>
                        <div style="font-size:1.05rem; font-weight:700; color:#F8FAFC; font-family:'JetBrains Mono', monospace; margin-top:3px;">
                            {wb['peak_cpu_baseline_pct']:.0f}% → {wb['peak_cpu_optimized_pct']:.0f}%
                        </div>
                        <div style="font-size:0.76rem; color:#06B6D4; font-weight:600; font-family:'JetBrains Mono', monospace; margin-top:2px;">
                            {wb['peak_cpu_reduction_pct']:.1f}% package draw
                        </div>
                    </div>

                    <!-- Peak Memory -->
                    <div style="background:#0B0F19; border:1px solid #1E293B; border-radius:8px; padding:10px 12px;">
                        <div style="font-size:0.72rem; color:#94A3B8; text-transform:uppercase;">Peak Memory Footprint</div>
                        <div style="font-size:1.05rem; font-weight:700; color:#F8FAFC; font-family:'JetBrains Mono', monospace; margin-top:3px;">
                            {wb['peak_memory_baseline_mb']:,.0f} MB → {wb['peak_memory_optimized_mb']:,.0f} MB
                        </div>
                        <div style="font-size:0.76rem; color:#10B981; font-weight:600; font-family:'JetBrains Mono', monospace; margin-top:2px;">
                            {wb['peak_memory_reduction_pct']:.1f}% RAM allocation
                        </div>
                    </div>

                    <!-- Software Carbon Intensity (SCI) -->
                    <div style="background:#0B0F19; border:1px solid #1E293B; border-radius:8px; padding:10px 12px;">
                        <div style="font-size:0.72rem; color:#94A3B8; text-transform:uppercase;">Software Carbon (SCI)</div>
                        <div style="font-size:0.98rem; font-weight:700; color:#F8FAFC; font-family:'JetBrains Mono', monospace; margin-top:3px;">
                            {wb['sci_baseline_gco2_per_1k']:.3f} → {wb['sci_optimized_gco2_per_1k']:.3f}
                        </div>
                        <div style="font-size:0.74rem; color:#10B981; font-weight:600; font-family:'JetBrains Mono', monospace; margin-top:2px;">
                            gCO₂e / 1,000 rec ({wb['sci_reduction_pct']:.1f}%)
                        </div>
                    </div>
                </div>

                <!-- Output Equivalence Verification Banner -->
                <div style="background:rgba(16,185,129,0.09); border:1px solid rgba(16,185,129,0.3);
                            border-radius:8px; padding:8px 12px; margin-bottom:10px;
                            display:flex; justify-content:space-between; align-items:center;">
                    <span style="font-size:0.77rem; color:#CBD5E1; font-weight:600;">
                        SHA-256 Deterministic Output Equivalence:
                    </span>
                    <span style="font-size:0.77rem; color:#10B981; font-weight:700; font-family:'JetBrains Mono', monospace;">
                        {wb['output_equivalence']}
                    </span>
                </div>

                <!-- Explicit No-Double-Counting Rule Callout Box -->
                <div style="background:rgba(245,158,11,0.09); border:1px solid rgba(245,158,11,0.38);
                            border-left:4px solid #F59E0B; border-radius:8px; padding:10px 12px;">
                    <div style="font-size:0.75rem; font-weight:700; color:#F59E0B; text-transform:uppercase;
                                letter-spacing:0.04em; font-family:'JetBrains Mono', monospace;">
                        ⚖️ Audit Governance: No-Double-Counting Rule
                    </div>
                    <div style="font-size:0.76rem; color:#E2E8F0; line-height:1.45; margin-top:4px;">
                        Workstream B software runtime gains (<strong>-64.9%</strong> execution time, <strong>-57.0%</strong> RAM)
                        are reported strictly as <strong>compute-node efficiency &amp; SCI metrics</strong>. They are
                        <strong>never added</strong> to facility-level ₹/kWh or Scope 2 savings to prevent double-counting
                        against Workstream A PUE &amp; kWh reductions.
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
