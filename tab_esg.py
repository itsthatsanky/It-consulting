"""
Tab 4: ESG, Carbon Accounting & Net-Zero Simulator (BRSR / GHG Protocol Aligned)
Prepared by WAS Group 2, TAPMI Bengaluru for GreenCore Data Services Pvt. Ltd., Bengaluru.
"""
from __future__ import annotations

from typing import Any, Dict

import plotly.graph_objects as go
import streamlit as st

USD_TO_INR: float = 84.0
HOURS_PER_YEAR: float = 8760.0


# ---------------------------------------------------------------------------
# Currency & Number Formatting Helpers
# ---------------------------------------------------------------------------
def _format_inr(amount: float, decimals: int = 0) -> str:
    """Format a number using the Indian numbering system (e.g., ₹8,20,000)."""
    neg = "-" if amount < 0 else ""
    val = abs(float(amount))
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


def _format_active_currency(amount_active: float, currency: str, decimals: int = 0) -> str:
    """Format a value already expressed in the active currency (`INR (₹)` or `USD ($)`)."""
    if currency == "USD ($)":
        neg = "-" if amount_active < 0 else ""
        return f"{neg}${abs(float(amount_active)):,.{decimals}f}"
    return _format_inr(amount_active, decimals=decimals)


def _format_dual_currency(amount_inr: float, currency: str, decimals: int = 0) -> str:
    """Return active currency string with secondary currency in parentheses."""
    usd_val = amount_inr / USD_TO_INR
    inr_str = _format_inr(amount_inr, decimals=decimals)
    usd_str = f"{'-' if usd_val < 0 else ''}${abs(usd_val):,.{decimals}f}"
    if currency == "USD ($)":
        return f"{usd_str} ({inr_str})"
    return f"{inr_str} ({usd_str})"


# ---------------------------------------------------------------------------
# Plotly Horizontal Stacked Bar Chart Builder
# ---------------------------------------------------------------------------
def _build_emissions_stacked_bar(
    scope1_baseline: float,
    scope2_baseline: float,
    co2_avoided_efficiency: float,
    temporal_shift_co2: float,
    rec_neutralized_co2: float,
    credit_offset_co2: float,
    unabated_residual_co2: float,
    tier_key: str,
) -> go.Figure:
    """
    Build a dark-themed horizontal stacked bar chart comparing:
      1. Total Baseline Emissions (Scope 1 + Scope 2)
      2. Post-Optimization & Temporal Shift Abatement Breakdown
      3. Net-Zero Simulator Pathway (Abated + RECs + Verified Carbon Credits vs. Final Net Footprint)
    """
    categories = [
        "3. Net-Zero Simulator<br>(RECs + Carbon Credits)",
        "2. Operational Abatement<br>(Efficiency + AI Shifting)",
        "1. Facility Baseline<br>(Scope 1 + Scope 2)",
    ]

    total_operational_abated = co2_avoided_efficiency + temporal_shift_co2
    post_efficiency_residual = max(
        0.0, (scope1_baseline + scope2_baseline) - total_operational_abated
    )

    fig = go.Figure()

    # Trace 1: Baseline Scope 2 Grid Electricity (Amber)
    fig.add_trace(
        go.Bar(
            name="Baseline Scope 2 (Grid Electricity)",
            y=[categories[2]],
            x=[scope2_baseline],
            orientation="h",
            marker=dict(color="#F59E0B", line=dict(color="#0B0F19", width=1.5)),
            text=[f"Scope 2: {scope2_baseline:,.1f} tCO₂e"],
            textposition="inside",
            insidetextanchor="middle",
            hovertemplate=(
                "<b>%{y}</b><br>"
                "Baseline Scope 2 (Grid Electricity): <b>%{x:,.2f} tCO₂e/yr</b><extra></extra>"
            ),
        )
    )

    # Trace 2: Baseline Scope 1 Diesel & Refrigerants (Slate/Amber-Red)
    fig.add_trace(
        go.Bar(
            name="Baseline Scope 1 (Diesel & Fugitive)",
            y=[categories[2]],
            x=[scope1_baseline],
            orientation="h",
            marker=dict(color="#D97706", line=dict(color="#0B0F19", width=1.5)),
            text=[f"S1: {scope1_baseline:,.1f} t"],
            textposition="inside",
            insidetextanchor="middle",
            hovertemplate=(
                "<b>%{y}</b><br>"
                "Baseline Scope 1 (Diesel Backup & Refrigerants): <b>%{x:,.2f} tCO₂e/yr</b><extra></extra>"
            ),
        )
    )

    # Trace 3: Emissions Eliminated via Efficiency (Emerald #10B981)
    fig.add_trace(
        go.Bar(
            name="Eliminated via Efficiency (IT + Cooling PUE)",
            y=[categories[0], categories[1]],
            x=[co2_avoided_efficiency, co2_avoided_efficiency],
            orientation="h",
            marker=dict(color="#10B981", line=dict(color="#0B0F19", width=1.5)),
            text=[
                f"Efficiency: -{co2_avoided_efficiency:,.1f} t" if co2_avoided_efficiency > 25 else "",
                f"Efficiency Abatement: -{co2_avoided_efficiency:,.1f} tCO₂e",
            ],
            textposition="inside",
            insidetextanchor="middle",
            hovertemplate=(
                "<b>%{y}</b><br>"
                "Eliminated via Efficiency: <b>%{x:,.2f} tCO₂e/yr</b><extra></extra>"
            ),
        )
    )

    # Trace 4: Tier 3 AI Temporal Load Shifting (Cyan #06B6D4)
    if temporal_shift_co2 > 0.01:
        fig.add_trace(
            go.Bar(
                name="Tier 3 AI Temporal Carbon Shifting",
                y=[categories[0], categories[1]],
                x=[temporal_shift_co2, temporal_shift_co2],
                orientation="h",
                marker=dict(color="#06B6D4", line=dict(color="#0B0F19", width=1.5)),
                text=[
                    f"AI Shift: -{temporal_shift_co2:,.1f} t",
                    f"AI Shift: -{temporal_shift_co2:,.1f} t",
                ],
                textposition="inside",
                insidetextanchor="middle",
                hovertemplate=(
                    "<b>%{y}</b><br>"
                    "Tier 3 AI Temporal Load Shifting: <b>%{x:,.2f} tCO₂e/yr</b><extra></extra>"
                ),
            )
        )

    # Trace 5: Un-neutralized / Pre-Offset Residual on Bar 2 (Muted Amber)
    fig.add_trace(
        go.Bar(
            name="Pre-Offset Residual Emissions (Scope 1 + 2)",
            y=[categories[1]],
            x=[post_efficiency_residual],
            orientation="h",
            marker=dict(color="#F59E0B", opacity=0.72, line=dict(color="#0B0F19", width=1.5)),
            text=[f"Residual Before Offsets: {post_efficiency_residual:,.1f} tCO₂e"],
            textposition="inside",
            insidetextanchor="middle",
            hovertemplate=(
                "<b>%{y}</b><br>"
                "Remaining Operational Residual: <b>%{x:,.2f} tCO₂e/yr</b><extra></extra>"
            ),
        )
    )

    # Trace 6: Neutralized via RECs / Green Tariff on Bar 3 (Cyan #06B6D4)
    fig.add_trace(
        go.Bar(
            name="Neutralized via RECs / Green Tariff (Scope 2)",
            y=[categories[0]],
            x=[rec_neutralized_co2],
            orientation="h",
            marker=dict(color="#06B6D4", line=dict(color="#0B0F19", width=1.5)),
            text=[f"RECs: -{rec_neutralized_co2:,.1f} t" if rec_neutralized_co2 > 30 else ""],
            textposition="inside",
            insidetextanchor="middle",
            hovertemplate=(
                "<b>%{y}</b><br>"
                "Neutralized by RECs / Green Tariff: <b>%{x:,.2f} tCO₂e/yr</b><extra></extra>"
            ),
        )
    )

    # Trace 7: Neutralized via Verified Carbon Credits on Bar 3 (Teal/Emerald #34D399)
    fig.add_trace(
        go.Bar(
            name="Verified Carbon Credits (Biochar / Afforestation)",
            y=[categories[0]],
            x=[credit_offset_co2],
            orientation="h",
            marker=dict(color="#34D399", line=dict(color="#0B0F19", width=1.5)),
            text=[f"Credits: -{credit_offset_co2:,.1f} t" if credit_offset_co2 > 30 else ""],
            textposition="inside",
            insidetextanchor="middle",
            hovertemplate=(
                "<b>%{y}</b><br>"
                "Offset via Verified Carbon Credits: <b>%{x:,.2f} tCO₂e/yr</b><extra></extra>"
            ),
        )
    )

    # Trace 8: Final Unabated Net Carbon Footprint on Bar 3 (Dark Slate / Crimson-Amber)
    fig.add_trace(
        go.Bar(
            name="Final Unabated Net Emissions",
            y=[categories[0]],
            x=[unabated_residual_co2],
            orientation="h",
            marker=dict(color="#EF4444" if unabated_residual_co2 > 0.5 else "#10B981", line=dict(color="#0B0F19", width=1.5)),
            text=[
                f"Net: {unabated_residual_co2:,.1f} t"
                if unabated_residual_co2 > 25
                else ("NET-ZERO (0.0 t)" if unabated_residual_co2 <= 0.05 else "")
            ],
            textposition="inside",
            insidetextanchor="middle",
            hovertemplate=(
                "<b>%{y}</b><br>"
                "Final Net Carbon Footprint: <b>%{x:,.2f} tCO₂e/yr</b><extra></extra>"
            ),
        )
    )

    fig.update_layout(
        barmode="stack",
        title=dict(
            text=(
                f"<b>GHG Protocol Scope 1 & 2 Abatement & Net-Zero Waterfall ({tier_key})</b>"
                "<br><span style='font-size:12px;color:#9CA3AF;'>"
                "Comparison of Total Baseline Emissions, Operational Efficiency Abatement, and REC / Carbon Credit Neutralization (tCO₂e/yr)"
                "</span>"
            ),
            font=dict(size=15, color="#F9FAFB"),
            x=0.0,
            y=0.96,
        ),
        paper_bgcolor="#111827",
        plot_bgcolor="#0B0F19",
        font=dict(color="#F9FAFB", family="Inter, sans-serif", size=12),
        height=370,
        margin=dict(l=20, r=24, t=72, b=50),
        xaxis=dict(
            title="Annual GHG Emissions (Metric Tonnes CO₂e / year)",
            gridcolor="#1F2937",
            zerolinecolor="#374151",
            tickfont=dict(color="#D1D5DB"),
            title_font=dict(color="#9CA3AF", size=12),
        ),
        yaxis=dict(
            gridcolor="#1F2937",
            tickfont=dict(color="#F9FAFB", size=12),
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.34,
            xanchor="left",
            x=0.0,
            font=dict(size=11, color="#D1D5DB"),
            bgcolor="rgba(17,24,39,0.7)",
        ),
    )
    return fig


# ---------------------------------------------------------------------------
# Main Tab 4 Renderer
# ---------------------------------------------------------------------------
def render_tab_esg(sim: Dict[str, Any], params: Dict[str, Any]) -> None:
    """
    Render Tab 4: ESG, Carbon & Net-Zero Simulator.

    Parameters
    ----------
    sim : dict
        Unified output from `data_simulator.run_full_simulation(...)`.
    params : dict
        Active sidebar parameters dictionary from `app.py`.
    """
    fin = sim["financials"]
    t_ml = sim["telemetry_ml"]
    ml_val = t_ml["ml_validation"]

    # Extract exact dictionary keys from `sim["financials"]`
    scope2_baseline_tonnes = float(fin["scope2_baseline_tonnes"])
    scope1_baseline_tonnes = float(fin["scope1_baseline_tonnes"])
    total_baseline_emissions_tonnes = float(fin["total_baseline_emissions_tonnes"])
    co2_avoided_efficiency_tonnes = float(fin["co2_avoided_efficiency_tonnes"])
    scope2_projected_tonnes = float(fin["scope2_projected_tonnes"])
    total_projected_emissions_tonnes = float(fin["total_projected_emissions_tonnes"])

    annual_net_benefit = float(fin["annual_net_benefit"])
    annual_net_benefit_inr = float(fin["annual_net_benefit_inr"])
    annual_gross_saving = float(fin["annual_gross_saving"])
    recurring_opex = float(fin["recurring_opex"])
    initial_cost = float(fin["initial_cost"])
    simple_payback_display = str(fin["simple_payback_display"])
    annual_roi_pct = float(fin["annual_roi_pct"])

    baseline_pue = float(fin["baseline_pue"])
    projected_pue = float(fin["projected_pue"])
    baseline_kwh = float(fin["baseline_kwh"])
    projected_annual_kwh = float(fin["projected_annual_kwh"])
    annual_kwh_saved = float(fin["annual_kwh_saved"])
    avg_it_kw = float(fin["avg_it_kw"])
    grid_region = str(fin["grid_region"])
    grid_emission_factor = float(fin["grid_emission_factor"])
    currency = str(fin["currency"])
    fx_rate = float(fin["fx_rate"])
    selected_tier = str(fin["selected_tier"])
    tier_key = str(fin["tier_key"])

    is_usd = currency == "USD ($)"

    # Tier 3 temporal carbon shifting from `sim["telemetry_ml"]["ml_validation"]`
    raw_temporal_shift_tonnes = float(ml_val["annual_temporal_shift_co2_tonnes"])
    active_temporal_shift_tonnes = raw_temporal_shift_tonnes if tier_key == "Tier 3" else 0.0

    # Operational Scope 2 residual after efficiency AND Tier 3 temporal load shifting
    residual_scope2_before_rec = max(0.0, scope2_projected_tonnes - active_temporal_shift_tonnes)
    residual_scope1_tonnes = scope1_baseline_tonnes
    total_operational_eliminated_tonnes = co2_avoided_efficiency_tonnes + active_temporal_shift_tonnes
    total_residual_before_offsets_tonnes = residual_scope2_before_rec + residual_scope1_tonnes

    # IT Equipment Annual Energy (kWh) & Carbon Usage Effectiveness (CUE = kgCO2 / kWh of IT Energy)
    annual_it_kwh = max(1.0, avg_it_kw * HOURS_PER_YEAR)
    cue_baseline = (total_baseline_emissions_tonnes * 1000.0) / annual_it_kwh
    cue_projected_operational = (
        (total_residual_before_offsets_tonnes * 1000.0) / annual_it_kwh
    )

    # -----------------------------------------------------------------------
    # Header Banner
    # -----------------------------------------------------------------------
    st.markdown(
        f"""
        <div style="background: linear-gradient(135deg, #111827 0%, #0B0F19 100%);
                    border: 1px solid #1F2937; border-left: 4px solid #10B981;
                    border-radius: 12px; padding: 16px 20px; margin-bottom: 16px;">
            <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px;">
                <div>
                    <span class="gc-badge-emerald">GHG Protocol Corporate Standard</span>
                    <span class="gc-badge-cyan">SEBI BRSR Principle 6</span>
                    <span class="gc-badge-amber">{tier_key} Active</span>
                    <h3 style="margin:6px 0 2px 0; color:#F9FAFB; font-size:1.25rem;">
                        ESG Carbon Accounting, CUE Telemetry & Interactive Net-Zero Simulator
                    </h3>
                    <p style="margin:0; color:#9CA3AF; font-size:0.86rem;">
                        Grid Region: <strong style="color:#E5E7EB;">{grid_region}</strong>
                        &nbsp;|&nbsp; Emission Factor: <strong style="color:#10B981;">{grid_emission_factor:.2f} kgCO₂/kWh</strong>
                        &nbsp;|&nbsp; IT Compute Baseline: <strong style="color:#06B6D4;">{annual_it_kwh:,.0f} kWh/yr ({avg_it_kw:.1f} kW avg)</strong>
                    </p>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Reserve top container for the Emissions Breakdown & Horizontal Stacked Bar Chart
    # so it dynamically reflects the Interactive Net-Zero Simulator slider states in a single pass.
    top_chart_container = st.container()

    st.markdown("---")

    # -----------------------------------------------------------------------
    # Section 2: Interactive Net-Zero Simulator Controls
    # -----------------------------------------------------------------------
    st.markdown(
        """
        <div style="margin-bottom: 8px;">
            <h4 style="margin:0; color:#F9FAFB; font-size:1.08rem;">
                🎛️ Interactive Net-Zero Pathway & Self-Funding Offset Simulator
            </h4>
            <p style="margin:2px 0 10px 0; color:#9CA3AF; font-size:0.84rem;">
                Model Scope 2 neutralization via Indian I-RECs / Green Tariffs and Scope 1+2 neutralization via Verified Carbon Credits (Biochar / Afforestation).
                Evaluate whether operational energy savings fully self-fund the ESG Net-Zero program.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    sim_col1, sim_col2 = st.columns(2, gap="large")

    with sim_col1:
        st.markdown(
            """
            <div style="background-color:#111827; border:1px solid #1F2937; border-top:3px solid #06B6D4;
                        border-radius:10px; padding:12px 14px; margin-bottom:10px;">
                <div style="color:#06B6D4; font-weight:700; font-size:0.85rem; text-transform:uppercase; letter-spacing:0.04em;">
                    Instrument 1 · Scope 2 Market-Based Greening
                </div>
                <div style="color:#9CA3AF; font-size:0.78rem; margin-top:2px;">
                    Applied to residual Scope 2 grid electricity emissions ({:,.2f} tCO₂e/yr eligible).
                </div>
            </div>
            """.format(residual_scope2_before_rec),
            unsafe_allow_html=True,
        )

        rec_pct = st.slider(
            "Renewable Energy Certificates / Green Tariff (%)",
            min_value=0,
            max_value=100,
            value=50,
            step=5,
            key="esg_rec_pct",
            help="Percentage of remaining Scope 2 electricity emissions covered by I-RECs or BESCOM Green Tariff.",
        )

        if is_usd:
            rec_price_usd = st.slider(
                "I-REC / Green Tariff Price per Metric Ton CO₂e ($/tCO₂e)",
                min_value=1.0,
                max_value=25.0,
                value=4.50,
                step=0.50,
                key="esg_rec_price_usd",
                help="Market price per tCO₂e equivalent of Renewable Energy Certificates (1 USD = ₹84).",
            )
            rec_price_active = rec_price_usd
            rec_price_inr = rec_price_usd * USD_TO_INR
        else:
            rec_price_inr = float(
                st.slider(
                    "I-REC / Green Tariff Price per Metric Ton CO₂e (₹/tCO₂e)",
                    min_value=100,
                    max_value=2100,
                    value=380,
                    step=20,
                    key="esg_rec_price_inr",
                    help="Market price per tCO₂e equivalent of Indian I-RECs / Green Tariff premium.",
                )
            )
            rec_price_active = rec_price_inr

    with sim_col2:
        st.markdown(
            """
            <div style="background-color:#111827; border:1px solid #1F2937; border-top:3px solid #10B981;
                        border-radius:10px; padding:12px 14px; margin-bottom:10px;">
                <div style="color:#10B981; font-weight:700; font-size:0.85rem; text-transform:uppercase; letter-spacing:0.04em;">
                    Instrument 2 · Scope 1 + Un-Greened Scope 2 Removal Credits
                </div>
                <div style="color:#9CA3AF; font-size:0.78rem; margin-top:2px;">
                    Applied to diesel/refrigerant Scope 1 ({:,.2f} tCO₂e) + un-greened Scope 2 residual.
                </div>
            </div>
            """.format(residual_scope1_tonnes),
            unsafe_allow_html=True,
        )

        credit_pct = st.slider(
            "Verified Carbon Credits - Biochar/Afforestation (%)",
            min_value=0,
            max_value=100,
            value=50,
            step=5,
            key="esg_credit_pct",
            help="Percentage of remaining Scope 1 + un-greened Scope 2 emissions neutralized via Verra/Gold Standard carbon removal credits.",
        )

        if is_usd:
            credit_price_usd = st.slider(
                "Verified Carbon Credit Price per Metric Ton CO₂e ($/tCO₂e)",
                min_value=3.0,
                max_value=60.0,
                value=12.00,
                step=1.00,
                key="esg_credit_price_usd",
                help="Price per tCO₂e for high-integrity Biochar / Afforestation removal credits (1 USD = ₹84).",
            )
            credit_price_active = credit_price_usd
            credit_price_inr = credit_price_usd * USD_TO_INR
        else:
            credit_price_inr = float(
                st.slider(
                    "Verified Carbon Credit Price per Metric Ton CO₂e (₹/tCO₂e)",
                    min_value=250,
                    max_value=5000,
                    value=1000,
                    step=50,
                    key="esg_credit_price_inr",
                    help="Price per tCO₂e for Verra / Gold Standard Biochar & Afforestation credits.",
                )
            )
            credit_price_active = credit_price_inr

    # -----------------------------------------------------------------------
    # Compute Net-Zero Simulator Outputs
    # -----------------------------------------------------------------------
    rec_neutralized_tonnes = residual_scope2_before_rec * (rec_pct / 100.0)
    ungreened_scope2_tonnes = max(0.0, residual_scope2_before_rec - rec_neutralized_tonnes)

    remaining_for_credits_tonnes = residual_scope1_tonnes + ungreened_scope2_tonnes
    credit_offset_tonnes = remaining_for_credits_tonnes * (credit_pct / 100.0)

    total_offset_neutralized_tonnes = rec_neutralized_tonnes + credit_offset_tonnes
    final_net_footprint_tonnes = max(
        0.0, total_residual_before_offsets_tonnes - total_offset_neutralized_tonnes
    )

    total_abated_and_offset_tonnes = (
        total_operational_eliminated_tonnes + total_offset_neutralized_tonnes
    )
    pct_towards_net_zero = (
        (total_abated_and_offset_tonnes / total_baseline_emissions_tonnes) * 100.0
        if total_baseline_emissions_tonnes > 0
        else 100.0
    )
    pct_towards_net_zero = min(100.0, max(0.0, pct_towards_net_zero))

    # Costs in Active Currency and INR
    rec_cost_active = rec_neutralized_tonnes * rec_price_active
    credit_cost_active = credit_offset_tonnes * credit_price_active
    annual_carbon_offset_cost = rec_cost_active + credit_cost_active
    annual_carbon_offset_cost_inr = (
        rec_neutralized_tonnes * rec_price_inr + credit_offset_tonnes * credit_price_inr
    )

    # Exact formula: Net Financial Position = Net Annual Energy Benefit - Carbon Offset Cost
    net_financial_position = annual_net_benefit - annual_carbon_offset_cost
    net_financial_position_inr = annual_net_benefit_inr - annual_carbon_offset_cost_inr
    is_self_funded = net_financial_position >= 0.0

    # Market-based effective CUE after RECs & Offsets
    cue_market_net = (final_net_footprint_tonnes * 1000.0) / annual_it_kwh
    cue_operational_delta_pct = (
        ((cue_projected_operational - cue_baseline) / cue_baseline) * 100.0
        if cue_baseline > 0
        else 0.0
    )

    # -----------------------------------------------------------------------
    # Populate Section 1: Emissions Breakdown & Horizontal Stacked Bar Chart
    # -----------------------------------------------------------------------
    with top_chart_container:
        b_col1, b_col2, b_col3, b_col4 = st.columns(4)
        with b_col1:
            st.metric(
                label="Total Baseline Emissions",
                value=f"{total_baseline_emissions_tonnes:,.1f} tCO₂e/yr",
                delta=f"S2: {scope2_baseline_tonnes:,.1f}t | S1: {scope1_baseline_tonnes:,.1f}t",
                delta_color="off",
                help="Total annual baseline facility GHG emissions: Scope 2 grid power + Scope 1 backup diesel & refrigerants (5% of Scope 2).",
            )
        with b_col2:
            shift_note = (
                f" (incl. {active_temporal_shift_tonnes:,.1f}t AI Shift)"
                if active_temporal_shift_tonnes > 0
                else " (Efficiency Only)"
            )
            st.metric(
                label="Eliminated via Efficiency",
                value=f"{total_operational_eliminated_tonnes:,.1f} tCO₂e/yr",
                delta=f"-{(total_operational_eliminated_tonnes / total_baseline_emissions_tonnes) * 100.0:.1f}% vs Baseline{shift_note}",
                delta_color="normal",
                help="Direct Scope 2 operational abatement from facility kWh reduction plus Tier 3 AI carbon-aware temporal load shifting.",
            )
        with b_col3:
            st.metric(
                label="Pre-Offset Residual (S1 + S2)",
                value=f"{total_residual_before_offsets_tonnes:,.1f} tCO₂e/yr",
                delta=f"S2: {residual_scope2_before_rec:,.1f}t | S1: {residual_scope1_tonnes:,.1f}t",
                delta_color="off",
                help="Remaining operational emissions before applying I-RECs or Verified Carbon Credits.",
            )
        with b_col4:
            st.metric(
                label="Carbon Usage Effectiveness (CUE)",
                value=f"{cue_projected_operational:.3f} kgCO₂/kWh-IT",
                delta=f"{cue_operational_delta_pct:+.1f}% vs Baseline ({cue_baseline:.3f})",
                delta_color="inverse",
                help="CUE = Total Annual CO₂ Emissions (kgCO₂e) / Annual IT Equipment Energy (kWh). Lower is cleaner.",
            )

        stacked_fig = _build_emissions_stacked_bar(
            scope1_baseline=scope1_baseline_tonnes,
            scope2_baseline=scope2_baseline_tonnes,
            co2_avoided_efficiency=co2_avoided_efficiency_tonnes,
            temporal_shift_co2=active_temporal_shift_tonnes,
            rec_neutralized_co2=rec_neutralized_tonnes,
            credit_offset_co2=credit_offset_tonnes,
            unabated_residual_co2=final_net_footprint_tonnes,
            tier_key=tier_key,
        )
        st.plotly_chart(stacked_fig, use_container_width=True)

        if tier_key != "Tier 3":
            st.markdown(
                f"""
                <div style="background:rgba(6, 182, 212, 0.08); border:1px solid rgba(6, 182, 212, 0.35);
                            border-radius:8px; padding:8px 14px; font-size:0.81rem; color:#D1D5DB;">
                    💡 <strong style="color:#06B6D4;">Tier 3 AI Temporal Carbon Shifting Unlock Available:</strong>
                    Upgrading to <strong>Tier 3</strong> shifts 18% of afternoon batch compute out of peak thermal grid dispatch windows (13:00–18:00),
                    eliminating an additional <strong style="color:#10B981;">{raw_temporal_shift_tonnes:,.2f} tCO₂e/yr</strong> with zero hardware offset cost.
                </div>
                """,
                unsafe_allow_html=True,
            )

    # -----------------------------------------------------------------------
    # Section 2B: Interactive Net-Zero Simulator KPI Cards & Self-Funding Banner
    # -----------------------------------------------------------------------
    st.markdown("#### 📊 Net-Zero Financial & Carbon Position KPIs")

    kpi1, kpi2, kpi3, kpi4 = st.columns(4)

    with kpi1:
        st.metric(
            label="Total Offset / Neutralized CO₂",
            value=f"{total_offset_neutralized_tonnes:,.1f} tCO₂e/yr",
            delta=f"RECs: {rec_neutralized_tonnes:,.1f}t | Credits: {credit_offset_tonnes:,.1f}t",
            delta_color="normal",
            help="Sum of Scope 2 emissions neutralized via I-RECs/Green Tariff and Scope 1+2 emissions neutralized via Verified Carbon Credits.",
        )

    with kpi2:
        st.metric(
            label="Final Net Carbon Footprint",
            value=f"{final_net_footprint_tonnes:,.1f} tCO₂e/yr",
            delta=f"{pct_towards_net_zero:.1f}% Towards Net-Zero",
            delta_color="normal",
            help="Unabated net emissions remaining after operational efficiency, AI temporal load shifting, RECs, and verified carbon credits.",
        )

    with kpi3:
        st.metric(
            label="Annual Carbon Offset Cost",
            value=_format_active_currency(annual_carbon_offset_cost, currency),
            delta=f"RECs: {_format_active_currency(rec_cost_active, currency)} | Credits: {_format_active_currency(credit_cost_active, currency)}",
            delta_color="off",
            help="Total annual expenditure on Renewable Energy Certificates and Verified Carbon Removal Credits.",
        )

    with kpi4:
        pos_delta_label = (
            "Self-Funded by Efficiency Savings"
            if is_self_funded
            else "Requires Net ESG Budget Top-Up"
        )
        st.metric(
            label="Net Financial Position",
            value=_format_active_currency(net_financial_position, currency),
            delta=pos_delta_label,
            delta_color="normal" if is_self_funded else "inverse",
            help="Net Financial Position = Net Annual Energy Benefit - Annual Carbon Offset Cost.",
        )

    # Self-Funding Status Banner + Effective CUE Comparison Card
    status_col1, status_col2 = st.columns([1.45, 1.0], gap="medium")

    with status_col1:
        if is_self_funded:
            surplus_str = _format_dual_currency(net_financial_position_inr, currency)
            benefit_str = _format_dual_currency(annual_net_benefit_inr, currency)
            offset_str = _format_dual_currency(annual_carbon_offset_cost_inr, currency)
            st.markdown(
                f"""
                <div style="background: rgba(16, 185, 129, 0.12); border: 1px solid rgba(16, 185, 129, 0.45);
                            border-left: 4px solid #10B981; border-radius: 10px; padding: 14px 16px; height: 100%;">
                    <div style="color:#10B981; font-weight:700; font-size:0.92rem;">
                        ✅ SELF-FUNDING ESG PROGRAM VERIFIED ({pct_towards_net_zero:.1f}% Net-Zero Pathway)
                    </div>
                    <p style="margin:6px 0 0 0; color:#E5E7EB; font-size:0.84rem; line-height:1.45;">
                        Annual Net Energy Savings of <strong>{benefit_str}</strong> completely fund the
                        <strong>{offset_str}</strong> carbon neutralization portfolio, leaving a net cash-flow surplus of
                        <strong style="color:#10B981;">{surplus_str}/yr</strong> for GreenCore Data Services Pvt. Ltd.
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            deficit_str = _format_dual_currency(abs(net_financial_position_inr), currency)
            benefit_str = _format_dual_currency(annual_net_benefit_inr, currency)
            offset_str = _format_dual_currency(annual_carbon_offset_cost_inr, currency)
            st.markdown(
                f"""
                <div style="background: rgba(245, 158, 11, 0.12); border: 1px solid rgba(245, 158, 11, 0.45);
                            border-left: 4px solid #F59E0B; border-radius: 10px; padding: 14px 16px; height: 100%;">
                    <div style="color:#F59E0B; font-weight:700; font-size:0.92rem;">
                        ⚠️ NET ESG INVESTMENT REQUIRED ({pct_towards_net_zero:.1f}% Net-Zero Pathway)
                    </div>
                    <p style="margin:6px 0 0 0; color:#E5E7EB; font-size:0.84rem; line-height:1.45;">
                        Annual Carbon Offset Cost (<strong>{offset_str}</strong>) exceeds current Net Annual Energy Benefit
                        (<strong>{benefit_str}</strong>) by <strong style="color:#F59E0B;">{deficit_str}/yr</strong>.
                        Increase facility energy reduction % or optimize REC vs. Carbon Credit mix to restore self-funding.
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )

    with status_col2:
        st.markdown(
            f"""
            <div style="background-color:#111827; border:1px solid #1F2937; border-left:4px solid #06B6D4;
                        border-radius:10px; padding:14px 16px; height: 100%;">
                <div style="color:#06B6D4; font-weight:700; font-size:0.86rem; text-transform:uppercase; letter-spacing:0.04em;">
                    Carbon Usage Effectiveness (CUE) Benchmark
                </div>
                <div style="display:flex; justify-content:space-between; margin-top:8px; font-size:0.84rem;">
                    <span style="color:#9CA3AF;">Baseline CUE (Location-Based):</span>
                    <strong style="color:#F59E0B;">{cue_baseline:.3f} kgCO₂ / kWh-IT</strong>
                </div>
                <div style="display:flex; justify-content:space-between; margin-top:4px; font-size:0.84rem;">
                    <span style="color:#9CA3AF;">Projected CUE (Operational Efficiency):</span>
                    <strong style="color:#06B6D4;">{cue_projected_operational:.3f} kgCO₂ / kWh-IT</strong>
                </div>
                <div style="display:flex; justify-content:space-between; margin-top:4px; font-size:0.84rem;">
                    <span style="color:#9CA3AF;">Effective CUE (Post-REC & Offsets):</span>
                    <strong style="color:#10B981;">{cue_market_net:.3f} kgCO₂ / kWh-IT</strong>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # -----------------------------------------------------------------------
    # Section 3: Audit-Ready ESG Disclosure Generator (BRSR / GHG Protocol)
    # -----------------------------------------------------------------------
    st.markdown(
        """
        <div style="margin-bottom: 10px;">
            <h4 style="margin:0; color:#F9FAFB; font-size:1.08rem;">
                📑 Audit-Ready ESG Executive Disclosure Generator (SEBI BRSR & GHG Protocol)
            </h4>
            <p style="margin:2px 0 8px 0; color:#9CA3AF; font-size:0.84rem;">
                Generate a board- and auditor-ready Markdown disclosure statement for
                <strong style="color:#E5E7EB;">GreenCore Data Services Pvt. Ltd., Bengaluru</strong>, complete with Scope 1 & 2 accounting,
                PUE/CUE telemetry, financial self-funding verification, and explicit synthetic/projected data governance notes.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if "show_esg_disclosure" not in st.session_state:
        st.session_state.show_esg_disclosure = False

    btn_col1, btn_col2 = st.columns([1.2, 2.8])
    with btn_col1:
        if st.button(
            "Generate Audit-Ready ESG Disclosure (BRSR / GHG Protocol)",
            type="primary",
            use_container_width=True,
            key="btn_generate_esg_disclosure",
        ):
            st.session_state.show_esg_disclosure = True

    with btn_col2:
        if st.session_state.show_esg_disclosure:
            if st.button(
                "Hide Disclosure Preview",
                use_container_width=False,
                key="btn_hide_esg_disclosure",
            ):
                st.session_state.show_esg_disclosure = False

    # Construct the Markdown disclosure document
    funding_status_text = (
        "FULLY SELF-FUNDED BY OPERATIONAL ENERGY SAVINGS (Net Cash-Flow Positive)"
        if is_self_funded
        else "PARTIALLY SELF-FUNDED (Requires Supplemental ESG Allocation)"
    )

    disclosure_markdown = f"""# EXECUTIVE ESG & GHG PROTOCOL DISCLOSURE STATEMENT
**Reporting Entity:** GreenCore Data Services Pvt. Ltd., Bengaluru, Karnataka, India  
**Prepared By:** WAS Group 2, TAPMI Bengaluru (Consulting Engagement — GreenCompute)  
**Quality & Assurance Lead:** Samiksha Sandeep Das (M3 · Delivery / QA · ID: 246213076)  
**Financial & Carbon Risk Lead:** Faizan Ali Siddiqui (M4 · Finance · ID: 246213110)  
**Reporting Frameworks:** GHG Protocol Corporate Accounting & Reporting Standard (Scope 1 & Scope 2) | SEBI Business Responsibility and Sustainability Reporting (BRSR — Principle 6) | ISO/IEC 30134-2 (PUE) & ISO/IEC 30134-8 (CUE)  
**Active Architecture Tier:** {selected_tier}  
**Grid Region & Emission Factor:** {grid_region} ({grid_emission_factor:.2f} kgCO₂e/kWh)

---

## 1. Facility Energy, PUE & Carbon Usage Effectiveness (CUE) Summary
| Metric | Baseline (Unoptimized) | Projected ({tier_key}) | Post-REC / Offset (Market-Based) | Net Change / Status |
| :--- | :---: | :---: | :---: | :---: |
| **Total Facility Electricity (kWh/yr)** | {baseline_kwh:,.0f} kWh | {projected_annual_kwh:,.0f} kWh | {projected_annual_kwh:,.0f} kWh | -{annual_kwh_saved:,.0f} kWh/yr ({fin['reduction_pct']:.1f}%) |
| **IT Compute Load (kWh/yr)** | {annual_it_kwh:,.0f} kWh | {annual_it_kwh:,.0f} kWh | {annual_it_kwh:,.0f} kWh | {avg_it_kw:.1f} kW Avg IT Load |
| **Power Usage Effectiveness (PUE)** | {baseline_pue:.2f} | {projected_pue:.3f} | {projected_pue:.3f} | -{((baseline_pue - projected_pue) / baseline_pue) * 100.0:.1f}% PUE Overhead Improvement |
| **Carbon Usage Effectiveness (CUE)** | {cue_baseline:.3f} kgCO₂/kWh-IT | {cue_projected_operational:.3f} kgCO₂/kWh-IT | {cue_market_net:.3f} kgCO₂/kWh-IT | {pct_towards_net_zero:.1f}% Total Carbon Intensity Reduction |

---

## 2. GHG Protocol Scope 1 & Scope 2 Emissions Inventory (Metric Tonnes CO₂e / Year)
* **Baseline Scope 2 (Indirect Grid Electricity Emissions):** `{scope2_baseline_tonnes:,.2f} tCO₂e/yr`
* **Baseline Scope 1 (Direct Diesel Generator Testing & Fugitive Refrigerants @ 5% of Scope 2):** `{scope1_baseline_tonnes:,.2f} tCO₂e/yr`
* **Total Baseline Facility Emissions (Scope 1 + Scope 2):** `{total_baseline_emissions_tonnes:,.2f} tCO₂e/yr`
* **Operational Efficiency Abatement (Workstream A + B):** `-{co2_avoided_efficiency_tonnes:,.2f} tCO₂e/yr`
* **Tier 3 AI Carbon-Aware Temporal Load Shifting Abatement:** `-{active_temporal_shift_tonnes:,.2f} tCO₂e/yr`
* **Remaining Pre-Offset Operational Emissions:** `{total_residual_before_offsets_tonnes:,.2f} tCO₂e/yr` (Scope 2: `{residual_scope2_before_rec:,.2f} tCO₂e/yr` | Scope 1: `{residual_scope1_tonnes:,.2f} tCO₂e/yr`)

---

## 3. Market-Based Net-Zero Neutralization Portfolio (RECs & Carbon Removal Credits)
* **Renewable Energy Certificates (I-RECs / Green Tariff @ {rec_pct}% of Residual Scope 2):** `-{rec_neutralized_tonnes:,.2f} tCO₂e/yr` @ `{_format_dual_currency(rec_price_inr, currency, decimals=2)}/tCO₂e` = `{_format_dual_currency(rec_neutralized_tonnes * rec_price_inr, currency)}`
* **Verified Carbon Credits (Biochar / Afforestation @ {credit_pct}% of Remaining Scope 1 + Scope 2):** `-{credit_offset_tonnes:,.2f} tCO₂e/yr` @ `{_format_dual_currency(credit_price_inr, currency, decimals=2)}/tCO₂e` = `{_format_dual_currency(credit_offset_tonnes * credit_price_inr, currency)}`
* **Total Neutralized / Offset Volume:** `{total_offset_neutralized_tonnes:,.2f} tCO₂e/yr`
* **Final Net Carbon Footprint (Post-Efficiency & Post-Offsets):** `{final_net_footprint_tonnes:,.2f} tCO₂e/yr` (**{pct_towards_net_zero:.1f}% progress towards Net-Zero**)

---

## 4. Financial Self-Funding & Capital Governance (M4 · Finance Sign-Off)
* **Initial Program Investment (CapEx + 12-Week PoC):** `{_format_dual_currency(float(fin['initial_cost_inr']), currency)}` (Simple Payback: `{simple_payback_display}` | Annual ROI: `{annual_roi_pct:.1f}%`)
* **Annual Gross Energy Savings:** `{_format_dual_currency(float(fin['annual_gross_saving_inr']), currency)}/yr`
* **Less Ongoing Cloud, Sensor & SaaS OpEx:** `-{_format_dual_currency(float(fin['recurring_opex_inr']), currency)}/yr`
* **Net Annual Energy Benefit (Pre-ESG Offsets):** `{_format_dual_currency(annual_net_benefit_inr, currency)}/yr`
* **Less Annual Carbon Offset & I-REC Expenditure:** `-{_format_dual_currency(annual_carbon_offset_cost_inr, currency)}/yr`
* **Net Financial Position (Net Annual Energy Benefit - Carbon Offset Cost):** `{_format_dual_currency(net_financial_position_inr, currency)}/yr`
* **Program Funding Determination:** **{funding_status_text}**

---

## 5. Data Governance, Methodology & Assurance Disclaimer (M3 · Delivery / QA Sign-Off)
> **DATA GOVERNANCE CLASSIFICATION: `Synthetic / Projected` (Decision-Support Simulation)**
> 1. All telemetry, thermodynamic PUE curves, workload vectorization benchmarks, and GHG abatement figures in this disclosure are **Synthetic / Projected** values generated deterministically (`np.random.seed(42)`) for the 12-week Proof-of-Concept (PoC) and Phase-2 advisory evaluation at **GreenCore Data Services Pvt. Ltd., Bengaluru**.
> 2. Scope 2 location-based emissions are computed using Central Electricity Authority (CEA) / regional grid emission factors (`{grid_emission_factor:.2f} kgCO₂/kWh`). Scope 1 backup diesel and refrigerant leakage are modeled conservatively at `5.0%` of baseline Scope 2 emissions.
> 3. Before external statutory filing under **SEBI BRSR Principle 6** or registry retirement of I-RECs / Verra carbon credits, 12 weeks of live smart-meter and rack-inlet telemetry must be audited and signed off by **Samiksha Sandeep Das (M3 · Delivery / QA)** and **Faizan Ali Siddiqui (M4 · Finance)**.
"""

    if st.session_state.show_esg_disclosure:
        dl_col1, dl_col2 = st.columns([1.2, 2.8])
        with dl_col1:
            st.download_button(
                label="⬇️ Download ESG Disclosure (.md)",
                data=disclosure_markdown,
                file_name=f"GreenCore_ESG_Disclosure_{tier_key.replace(' ', '_')}.md",
                mime="text/markdown",
                use_container_width=True,
                key="btn_download_esg_md",
            )

        preview_tab, code_tab = st.tabs(
            [
                "📄 Copyable Markdown Source (Audit-Ready)",
                "👁️ Formatted Executive Preview",
            ]
        )
        with preview_tab:
            st.caption(
                "Click the copy icon in the top-right corner of the code block below to copy the full BRSR / GHG Protocol disclosure."
            )
            st.code(disclosure_markdown, language="markdown")
        with code_tab:
            st.markdown(
                f"""
                <div style="background-color:#111827; border:1px solid #1F2937; border-left:4px solid #10B981;
                            border-radius:10px; padding:18px 22px;">
                """,
                unsafe_allow_html=True,
            )
            st.markdown(disclosure_markdown)
            st.markdown("</div>", unsafe_allow_html=True)
