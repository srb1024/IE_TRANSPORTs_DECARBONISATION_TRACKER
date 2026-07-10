"""Prescriptive Scenario Simulator page."""
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import streamlit as st
from plotly.subplots import make_subplots

from data_loader import load_table
from nav import sticky_header
from style import (
    DATA_LABEL_FONT, KPI_LABELS, PLOTLY_CONFIG, TARGET_LINE, apply_page_style, chart_heading, chart_layout,
    chart_subheading, stat_card, status_badge,
)

apply_page_style()
sticky_header("Prescriptive Simulator", "Prescriptive")

scenarios = load_table("prescriptive_scenarios")
monte_carlo = load_table("prescriptive_monte_carlo")
reverse_solve = load_table("prescriptive_reverse_solve")
county = load_table("county_recommendations")
reg_gap = load_table("ev_registration_gap").sort_values("Year")

KPI_DIRECTION = {"car_dependency_index": "down", "pt_usage_index": "up", "transport_intensity_index": "down"}
SCENARIO_ORDER = ["Business-As-Usual", "Moderate Intervention", "Accelerated Transition"]
RISK_COLORS = {"Critical": "#D55E00", "High": "#E69F00", "Medium": "#F0E442", "Low": "#009E73"}
GEOJSON_URL = "https://raw.githubusercontent.com/codeforgermany/click_that_hood/main/public/data/ireland-counties.geojson"


def status(gap, target, direction):
    on_track = gap >= 0 if direction == "down" else gap <= 0
    if on_track:
        return "On Track"
    return "At Risk" if abs(gap) / target * 100 < 20 else "Off Track"

st.divider()

st.subheader("Scenario comparison", anchor=False)

SCENARIO_COLORS = {
    "Business-As-Usual": "#D55E00",
    "Moderate Intervention": "#E69F00",
    "Accelerated Transition": "#009E73",
}
SCENARIO_BAND_COLORS = {
    "Business-As-Usual": "rgba(213,94,0,0.22)",
    "Moderate Intervention": "rgba(230,159,0,0.22)",
    "Accelerated Transition": "rgba(0,158,115,0.22)",
}
KPI_YAXIS_TITLES = {
    "car_dependency_index": "Cars per 1,000 population",
    "pt_usage_index": "Journeys per capita",
    "transport_intensity_index": "Vehicle km per capita",
}

kpi_items = list(KPI_LABELS.items())

with st.container(border=True):
    chart_heading("Scenario comparison, 2030 projection")
    chart_subheading("Car Dependency Index, Public Transport Usage Index and Transport Intensity Indicator under each scenario, with Monte Carlo uncertainty.")

    # Compute status for each KPI upfront so badges can render next to headings
    kpi_status_map = {}
    for kpi_key, _ in kpi_items:
        direction = KPI_DIRECTION[kpi_key]
        scen = scenarios[scenarios["kpi"] == kpi_key].set_index("scenario").loc[SCENARIO_ORDER]
        target = scen["gov_target_2030"].iloc[0]
        gap = scen.loc["Accelerated Transition", "gap_to_target"]
        kpi_status_map[kpi_key] = status(gap, target, direction)

    if "kpi_zoom" not in st.session_state:
        st.session_state.kpi_zoom = {kpi_key: False for kpi_key, _ in kpi_items}

    for kpi_key, _ in kpi_items:
        param_name = f"zoom_{kpi_key}"
        if param_name in st.query_params:
            st.session_state.kpi_zoom[kpi_key] = st.query_params[param_name] == "1"
            del st.query_params[param_name]

    header_cols = st.columns(3)
    for col, (kpi_key, kpi_label) in zip(header_cols, kpi_items):
        with col:
            zoomed = st.session_state.kpi_zoom[kpi_key]
            next_state = "0" if zoomed else "1"
            sign = "&#8722;" if zoomed else "&#43;"

            st.markdown(
                f"""
                <div style="display:flex;justify-content:center;align-items:center;gap:10px;padding:0 8px;">
                    <a href="?zoom_{kpi_key}={next_state}" target="_self" style="
                        display:inline-flex;align-items:center;justify-content:center;
                        height:24px;padding:0 10px;
                        border:1px solid #C7C7C7;border-radius:6px;
                        background:#F5F5F5;color:#333333;
                        font-size:13px;font-weight:600;line-height:1;
                        text-decoration:none;white-space:nowrap;
                    ">&#128269;{sign}</a>
                    <span style="font-weight:700;font-size:15px;">{kpi_label}</span>
                    {status_badge(kpi_status_map[kpi_key])}
                </div>
                """,
                unsafe_allow_html=True,
            )

    fig_combined = make_subplots(
        rows=1, cols=3,
        horizontal_spacing=0.08,
    )

    for col_idx, (kpi_key, kpi_label) in enumerate(kpi_items, start=1):
        direction = KPI_DIRECTION[kpi_key]
        scen = scenarios[scenarios["kpi"] == kpi_key].set_index("scenario").loc[SCENARIO_ORDER]
        mc = monte_carlo[monte_carlo["kpi"] == kpi_key].set_index("scenario").loc[SCENARIO_ORDER]
        target = scen["gov_target_2030"].iloc[0]

        show_legend_here = (col_idx == 1)

        for scenario in SCENARIO_ORDER:
            value = mc.loc[scenario, "mean_2030"]
            p5 = mc.loc[scenario, "p5_2030"]
            p95 = mc.loc[scenario, "p95_2030"]

            fig_combined.add_trace(
                go.Bar(
                    x=[scenario],
                    y=[p95 - p5],
                    base=[p5],
                    marker_color=SCENARIO_BAND_COLORS[scenario],
                    marker_line=dict(color="black", width=1.5),
                    hoverinfo="skip",
                    showlegend=False,
                ),
                row=1, col=col_idx,
            )

            fig_combined.add_trace(
                go.Bar(
                    x=[scenario],
                    y=[value],
                    name=scenario,
                    marker_color=SCENARIO_COLORS[scenario],
                    marker_line=dict(color="black", width=1.5),
                    text=[f"<b>{value:,.0f}</b>"],
                    textposition="inside",
                    insidetextanchor="end" if st.session_state.kpi_zoom[kpi_key] else "middle",
                    textfont=dict(family=DATA_LABEL_FONT["family"], size=DATA_LABEL_FONT["size"], color="white"),
                    legendgroup=scenario,
                    showlegend=show_legend_here,
                ),
                row=1, col=col_idx,
            )

        fig_combined.add_hline(
            y=target,
            line_dash=TARGET_LINE["dash"],
            line_color=TARGET_LINE["color"],
            line_width=TARGET_LINE["width"],
            row=1, col=col_idx,
        )

        if st.session_state.kpi_zoom[kpi_key]:
            band_min = min(mc["p5_2030"].min(), target)
            band_max = max(mc["p95_2030"].max(), target)
            pad = (band_max - band_min) * 0.15
            y_range = [max(0, band_min - pad), band_max + pad]
        else:
            y_max = max(mc["p95_2030"].max(), target) * (1.3 if kpi_key == "car_dependency_index" else 1.2)
            y_range = [0, y_max]

        fig_combined.update_yaxes(title_text=KPI_YAXIS_TITLES[kpi_key], range=y_range, row=1, col=col_idx)
        fig_combined.update_xaxes(showticklabels=False, title_text=None, row=1, col=col_idx)

    fig_combined = chart_layout(fig_combined, height=380)
    fig_combined.update_layout(
        showlegend=True,
        barmode="overlay",
        legend=dict(orientation="h", yanchor="top", y=-0.15, xanchor="center", x=0.5),
        margin=dict(t=40, l=10, r=10, b=60),
    )
    fig_combined.update_xaxes(showline=False, zeroline=False)
    fig_combined.update_yaxes(showline=False, zeroline=False)

    fig_combined.update_layout(margin=dict(t=15, l=10, r=10, b=60))
    st.plotly_chart(fig_combined, use_container_width=True, config=PLOTLY_CONFIG, key="scenario_combined")
st.subheader("Policy lever sensitivity", anchor=False)
with st.container(border=True):
    chart_heading("Which lever moves each KPI?")
    chart_subheading("Required change vs BAU pace, as a multiplier. Teal = same direction as BAU, just faster or slower. Vermillion = the lever would need to reverse direction entirely.")

    bau_pt = reverse_solve["bau_pt_growth_rate"].iloc[0]
    bau_ev = reverse_solve["bau_ev_adoption_rate"].iloc[0]
    c1, c2 = st.columns(2)
    c1.metric("BAU PT growth rate", f"{bau_pt*100:.1f}%/yr")
    c2.metric("BAU EV adoption rate", f"{bau_ev*100:.1f}%/yr")

    tornado_cols = st.columns(3)
    for col, (kpi_key, kpi_label) in zip(tornado_cols, kpi_items):
        with col:
            with st.container(border=True):
                chart_heading(kpi_label)

                rs_row = reverse_solve[reverse_solve["kpi"] == kpi_key].iloc[0]
                levers = ["EV adoption lever", "PT growth lever"]
                multipliers = [rs_row["ev_multiplier_vs_bau"], rs_row["pt_multiplier_vs_bau"]]
                colors = ["#009E73" if m >= 0 else "#D55E00" for m in multipliers]

                fig_t = go.Figure(
                    go.Bar(
                        x=multipliers, y=levers, orientation="h",
                        marker_color=colors, marker_line=dict(color="black", width=1),
                        text=[f"{m:,.1f}x" for m in multipliers],
                        textposition="outside", textfont=DATA_LABEL_FONT,
                    )
                )
                fig_t.add_vline(x=1, line_dash="dot", line_color="black", line_width=1.5)

                span = max(multipliers) - min(multipliers)
                pad = span * 0.25 if span > 0 else 1
                fig_t = chart_layout(fig_t, height=260)
                fig_t.update_layout(showlegend=False, margin=dict(t=10, l=10, r=40, b=45))
                fig_t.update_xaxes(
                    range=[min(multipliers) - pad, max(multipliers) + pad],
                    title_text="Required \u00f7 BAU pace",
                    title_font=dict(color="black", size=12),
                    tickfont=dict(color="black", size=12),
                    showline=True, linecolor="black", linewidth=2,
                )
                fig_t.update_yaxes(
                    tickfont=dict(color="black", size=12),
                    showline=True, linecolor="black", linewidth=2,
                )
                st.plotly_chart(fig_t, use_container_width=True, config=PLOTLY_CONFIG, key=f"lever_tornado_{kpi_key}")

st.subheader("EV adoption by income tier", anchor=False)
tier_forecast = load_table("ev_income_tier_forecast")
TIER_COLORS = {"High": "#0072B2", "Medium": "#E69F00", "Low": "#D55E00"}
TIER_ORDER = ["High", "Medium", "Low"]

with st.container(border=True):
    chart_heading("Non-Traditional Fleet Share by Income Tier")
    chart_subheading("Non-traditional fleet share by income tier, fitted and forecast.")

    card_col, chart_col = st.columns([1, 2])

    with card_col:
        for tier in TIER_ORDER:
            val_2030 = tier_forecast.loc[
                (tier_forecast["income_tier"] == tier) & (tier_forecast["Year"] == 2030),
                "other_fuel_share_forecast_pct"
            ].iloc[0]
            st.markdown(stat_card(f"{tier} income, 2030", f"{val_2030:.1f}%", accent=TIER_COLORS[tier]), unsafe_allow_html=True)

        high_2030 = tier_forecast.loc[(tier_forecast["income_tier"] == "High") & (tier_forecast["Year"] == 2030), "other_fuel_share_forecast_pct"].iloc[0]
        low_2030 = tier_forecast.loc[(tier_forecast["income_tier"] == "Low") & (tier_forecast["Year"] == 2030), "other_fuel_share_forecast_pct"].iloc[0]
        st.markdown(stat_card("Equity gap (High minus Low), 2030", f"{high_2030 - low_2030:.1f}pp", accent="#CC79A7"), unsafe_allow_html=True)

    with chart_col:
        fig6 = go.Figure()
        for tier in TIER_ORDER:
            tier_symbol = {"High": "circle", "Medium": "square", "Low": "diamond"}[tier]
            tier_data = tier_forecast[tier_forecast["income_tier"] == tier].sort_values("Year")
            solid = tier_data[tier_data["Year"] <= 2023]
            dashed = tier_data[tier_data["Year"] >= 2023]

            fig6.add_trace(
                go.Scatter(
                    x=solid["Year"], y=solid["other_fuel_share_forecast_pct"],
                    mode="lines+markers", name=f"{tier} income",
                    line=dict(color=TIER_COLORS[tier], width=3, dash="solid"),
                    marker=dict(symbol=tier_symbol, size=8),
                    legendgroup=tier,
                )
            )
            fig6.add_trace(
                go.Scatter(
                    x=dashed["Year"], y=dashed["other_fuel_share_forecast_pct"],
                    mode="lines+markers", name=f"{tier} income (forecast)",
                    line=dict(color=TIER_COLORS[tier], width=3, dash="dot"),
                    marker=dict(symbol=tier_symbol, size=8),
                    legendgroup=tier, showlegend=False,
                )
            )
        fig6 = chart_layout(fig6, height=520)
        fig6.update_layout(xaxis=dict(dtick=1, title="Year"), yaxis_title="Share (%)")
        st.plotly_chart(fig6, use_container_width=True, config=PLOTLY_CONFIG)

st.subheader("Equity priority matrix", anchor=False)

income_tier = load_table("income_tier_by_county")
stock = load_table("private_car_stock_by_county")

latest_stock_year = int(stock["Year"].max())
stock_latest = stock[stock["Year"] == latest_stock_year]
fuel_pivot = stock_latest.pivot_table(index="county", columns="fuel_type", values="car_stock", aggfunc="sum")
fuel_pivot["total"] = fuel_pivot.sum(axis=1)
fuel_pivot["ev_share_pct"] = fuel_pivot["Other fuel types"] / fuel_pivot["total"] * 100
ev_share = fuel_pivot[["ev_share_pct"]].reset_index()

equity = (
    county[["county", "risk_tier", "cars_per_1000"]]
    .merge(income_tier[["county", "income_tier", "median_income"]], on="county")
    .merge(ev_share, on="county")
)

RISK_ORDER = ["Critical", "High", "Medium", "Low"]
INCOME_ORDER = ["Low", "Medium", "High"]
PRIORITY_RISK = {"Critical", "High"}
PRIORITY_INCOME = {"Low", "Medium"}

AMBER_STOPS = ["#FAEEDA", "#FAC775", "#EF9F27", "#BA7517", "#854F0B"]
AMBER_TEXT = ["#633806", "#633806", "#633806", "#FAEEDA", "#FAEEDA"]

cell_rows = []
for risk in RISK_ORDER:
    for income in INCOME_ORDER:
        cell = equity[(equity["risk_tier"] == risk) & (equity["income_tier"] == income)]
        cell_rows.append({
            "risk_tier": risk,
            "income_tier": income,
            "count": len(cell),
            "avg_ev": cell["ev_share_pct"].mean() if len(cell) else None,
            "counties": cell["county"].tolist(),
        })
cell_df = pd.DataFrame(cell_rows)

non_empty_ev = cell_df.loc[cell_df["count"] > 0, "avg_ev"]
ev_min, ev_max = (non_empty_ev.min(), non_empty_ev.max()) if len(non_empty_ev) else (0, 1)

def swatch_for(avg_ev):
    if avg_ev is None or ev_max == ev_min:
        idx = 0
    else:
        pct = (avg_ev - ev_min) / (ev_max - ev_min)
        idx = min(int(pct * len(AMBER_STOPS)), len(AMBER_STOPS) - 1)
    return AMBER_STOPS[idx], AMBER_TEXT[idx]

n_bins = len(AMBER_STOPS)
bin_edges = [ev_min + (ev_max - ev_min) * i / n_bins for i in range(n_bins + 1)]
bin_labels = [f"{bin_edges[i]:.1f}\u2013{bin_edges[i + 1]:.1f}%" for i in range(n_bins)]

double_disadv = equity[(equity["risk_tier"].isin(["Critical", "High"])) & (equity["income_tier"] == "Low")]
double_advantaged = equity[(equity["risk_tier"].isin(["Critical", "High"])) & (equity["income_tier"] == "High")]

with st.container(border=True):
    chart_heading("Equity priority matrix")
    chart_subheading(f"Car-dependency risk tier vs income tier, {latest_stock_year} EV/non-traditional fleet share by cell.")

    stat_col, chart_col = st.columns([1, 2])
    with stat_col:
        st.markdown(
            stat_card(
                "Critical/High risk & low income",
                f"{len(double_disadv)} counties",
                ", ".join(double_disadv["county"].tolist()) if len(double_disadv) else "None",
                accent="#D55E00",
            ),
            unsafe_allow_html=True,
        )
        st.write("")
        st.markdown(
            stat_card(
                "Critical/High risk & high income",
                f"{len(double_advantaged)} counties",
                ", ".join(double_advantaged["county"].tolist()) if len(double_advantaged) else "None found",
                accent="#009E73",
            ),
            unsafe_allow_html=True,
        )

        st.write("")

        priority_mask = equity["risk_tier"].isin(PRIORITY_RISK) & equity["income_tier"].isin(PRIORITY_INCOME)
        priority_ev = equity.loc[priority_mask, "ev_share_pct"].mean()
        rest_ev = equity.loc[~priority_mask, "ev_share_pct"].mean()
        ev_gap = rest_ev - priority_ev
        st.markdown(
            stat_card(
                "EV/non-trad share, priority counties",
                f"{priority_ev:.1f}%",
                f"{ev_gap:.1f}pp behind non-priority counties ({rest_ev:.1f}%)",
                accent="#BA7517",
            ),
            unsafe_allow_html=True,
        )
        st.write("")

        priority_income = equity.loc[priority_mask, "median_income"].mean()
        national_income = equity["median_income"].mean()
        income_gap = national_income - priority_income
        st.markdown(
            stat_card(
                "Median income, priority counties",
                f"\u20ac{priority_income:,.0f}",
                f"\u20ac{income_gap:,.0f} below the national county average (\u20ac{national_income:,.0f})",
                accent="#993C1D",
            ),
            unsafe_allow_html=True,
        )


    with chart_col:
        n_bins = len(AMBER_STOPS)
        bin_edges = [ev_min + (ev_max - ev_min) * i / n_bins for i in range(n_bins + 1)]
        bin_labels = [f"{bin_edges[i]:.1f}\u2013{bin_edges[i + 1]:.1f}%" for i in range(n_bins)]
        legend_swatches = "".join(
            f'<span style="display:flex;align-items:center;gap:4px;">'
            f'<span style="width:16px;height:16px;border-radius:3px;background:{AMBER_STOPS[i]};'
            f'display:inline-block;"></span>{bin_labels[i]}</span>'
            for i in range(n_bins)
        )
        legend_html = (
            '<div style="display:flex;flex-wrap:wrap;align-items:center;gap:16px;'
            'margin-bottom:12px;font-size:14px;font-weight:700;color:#2C2C2A;">'
            '<span>Avg Non-trad share:</span>'
            f'{legend_swatches}'
            '<span style="display:flex;align-items:center;gap:4px;margin-left:8px;">'
            '<span style="width:16px;height:16px;border-radius:3px;border:2px solid #993C1D;'
            'display:inline-block;"></span>&#9650; Priority county</span>'
            '</div>'
        )
        st.markdown(legend_html, unsafe_allow_html=True)

        header_cells = "".join(
            f'<div style="text-align:center;font-size:13px;font-weight:700;color:#000000;">{inc} income</div>'
            for inc in INCOME_ORDER
        )
        grid_html = (
            '<div style="display:grid;grid-template-columns:90px repeat(3,1fr);gap:6px;margin-bottom:20px;">'
            f'<div></div>{header_cells}'
        )

        for risk in RISK_ORDER:
            grid_html += f'<div style="font-size:13px;font-weight:700;color:#000000;display:flex;align-items:center;">{risk}</div>'
            for income in INCOME_ORDER:
                row = cell_df[(cell_df["risk_tier"] == risk) & (cell_df["income_tier"] == income)].iloc[0]
                is_priority = risk in PRIORITY_RISK and income in PRIORITY_INCOME
                if row["count"] == 0:
                    grid_html += (
                        '<div style="background:#F1EFE8;border-radius:8px;padding:10px 6px;'
                        'text-align:center;color:#B4B2A9;font-size:11px;">0 counties</div>'
                    )
                    continue
                bg, text_color = swatch_for(row["avg_ev"])
                border = "border:2px solid #993C1D;" if is_priority else ""
                names_display = ", ".join(row["counties"])
                priority_flag = (
                    f'<div style="position:absolute;top:4px;right:6px;font-size:16px;font-weight:700;'
                    f'color:{text_color};">&#9650;</div>'
                    if is_priority else ""
                )
                grid_html += (
                    f'<div style="position:relative;background:{bg};{border}border-radius:8px;padding:12px 8px;text-align:center;">'
                    f'{priority_flag}'
                    f'<div style="font-weight:500;font-size:24px;color:{text_color};">{row["count"]}</div>'
                    f'<div style="font-size:14px;font-weight:500;color:{text_color};">avg EV {row["avg_ev"]:.1f}%</div>'
                    f'<div style="font-size:13px;color:{text_color};line-height:1.4;">{names_display}</div>'
                    f'</div>'
                )

        grid_html += "</div>"
        st.markdown(grid_html, unsafe_allow_html=True)
        # st.caption(
        #     "▲ Priority county = high car dependency (Critical or High risk tier) combined with "
        #     "lower household income (Low or Medium income tier) — these counties are least able to "
        #     "self-fund an EV transition and are the natural candidates for targeted grants or "
        #     "subsidised financing."
        # )

st.subheader("County priority map", anchor=False)
with st.container(border=True):
    tiers = sorted(county["risk_tier"].unique(), key=lambda t: county.loc[county["risk_tier"] == t, "priority"].iloc[0])
    tier_filter = st.multiselect("Filter by risk tier", options=tiers, default=tiers)
    filtered = county[county["risk_tier"].isin(tier_filter)].copy()
    filtered = filtered.merge(income_tier[["county", "income_tier"]], on="county", how="left")
    filtered["income_tier"] = filtered["income_tier"].fillna("Unknown")
    filtered["combo"] = filtered["risk_tier"] + " / " + filtered["income_tier"]

    RISK_OPACITY = {"Critical": 0.95, "High": 0.75, "Medium": 0.55, "Low": 0.3}

    def _hex_to_rgb(hex_color):
        hex_color = hex_color.lstrip("#")
        return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))

    BIVAR_COLOR_MAP = {"Unknown / Unknown": "rgba(150,150,150,0.4)"}
    for risk_lvl, opacity in RISK_OPACITY.items():
        BIVAR_COLOR_MAP[f"{risk_lvl} / Unknown"] = "rgba(150,150,150,0.4)"
        for income_lvl, hex_color in TIER_COLORS.items():
            rr, gg, bb = _hex_to_rgb(hex_color)
            BIVAR_COLOR_MAP[f"{risk_lvl} / {income_lvl}"] = f"rgba({rr},{gg},{bb},{opacity})"

    def _add_map_legend(fig, color_map, risk_order, income_order):
        pad = 0.012
        risk_title_w, row_label_w = 0.042, 0.068
        grid_w = 0.22
        box_x0 = 0.005
        content_x0 = box_x0 + pad
        grid_x0 = content_x0 + risk_title_w + row_label_w
        grid_x1 = grid_x0 + grid_w
        box_x1 = grid_x1 + pad
        col_w = grid_w / len(income_order)

        box_y1 = 0.975
        content_y1 = box_y1 - pad
        income_title_h, title_gap = 0.036, 0.010
        col_header_h, header_gap = 0.034, 0.012
        row_h = 0.052

        grid_y1 = content_y1 - income_title_h - title_gap - col_header_h - header_gap
        grid_y0 = grid_y1 - row_h * len(risk_order)
        box_y0 = grid_y0 - pad

        rx, ry = 0.010, 0.014
        legend_path = (
            f"M{box_x0 + rx},{box_y1} "
            f"L{box_x1 - rx},{box_y1} "
            f"Q{box_x1},{box_y1} {box_x1},{box_y1 - ry} "
            f"L{box_x1},{box_y0 + ry} "
            f"Q{box_x1},{box_y0} {box_x1 - rx},{box_y0} "
            f"L{box_x0 + rx},{box_y0} "
            f"Q{box_x0},{box_y0} {box_x0},{box_y0 + ry} "
            f"L{box_x0},{box_y1 - ry} "
            f"Q{box_x0},{box_y1} {box_x0 + rx},{box_y1} Z"
        )
        fig.add_shape(
            type="path", path=legend_path, xref="paper", yref="paper",
            fillcolor="rgba(255,255,255,0.95)", line=dict(color="#B4B2A9", width=1.2),
            layer="above",
        )

        fig.add_annotation(
            x=(grid_x0 + grid_x1) / 2, y=content_y1 - income_title_h / 2,
            xref="paper", yref="paper", showarrow=False,
            text="<b>Income tier</b>", font=dict(size=13, color="#2C2C2A"),
        )
        col_header_y = content_y1 - income_title_h - title_gap - col_header_h / 2
        for j, income_lvl in enumerate(income_order):
            fig.add_annotation(
                x=grid_x0 + col_w * (j + 0.5), y=col_header_y,
                xref="paper", yref="paper", showarrow=False,
                text=f"<b>{income_lvl}</b>", font=dict(size=12, color="#2C2C2A"),
            )
        fig.add_annotation(
            x=content_x0 + risk_title_w / 2, y=(grid_y0 + grid_y1) / 2,
            xref="paper", yref="paper", showarrow=False, textangle=-90,
            text="<b>Risk tier</b>", font=dict(size=13, color="#2C2C2A"),
        )
        for i, risk_lvl in enumerate(risk_order):
            fig.add_annotation(
                x=content_x0 + risk_title_w + row_label_w / 2, y=grid_y1 - row_h * (i + 0.5),
                xref="paper", yref="paper", showarrow=False, xanchor="center",
                text=f"<b>{risk_lvl}</b>", font=dict(size=11, color="#2C2C2A"),
            )
            for j, income_lvl in enumerate(income_order):
                swatch = color_map.get(f"{risk_lvl} / {income_lvl}", "rgba(150,150,150,0.4)")
                fig.add_shape(
                    type="rect", xref="paper", yref="paper",
                    x0=grid_x0 + col_w * j + 0.005, y0=grid_y1 - row_h * (i + 1) + 0.005,
                    x1=grid_x0 + col_w * (j + 1) - 0.005, y1=grid_y1 - row_h * i - 0.005,
                    fillcolor=swatch, line=dict(color="#2C2C2A", width=0.6),
                    layer="above",
                )
        return fig
    
    card_col, chart_col = st.columns([1, 2])

    with card_col:
        n_critical = int((county["risk_tier"] == "Critical").sum())
        n_zero_stops = int((county["stops_per_100k"] == 0).sum())
        n_counties = county["county"].nunique()
        top_county = county.loc[county["cars_per_1000"].idxmax()]

        st.markdown(stat_card("Critical priority", f"{n_critical} counties", accent="#D55E00"), unsafe_allow_html=True)
        st.write("")
        st.markdown(stat_card("High priority", f"{int((county['risk_tier']=='High').sum())} county", accent="#E69F00"), unsafe_allow_html=True)
        st.write("")
        st.markdown(stat_card("Zero recorded stops", f"{n_zero_stops} of {n_counties}", "NaPTAN coverage gap", accent="#6E6E6E"), unsafe_allow_html=True)
        st.write("")
        st.markdown(stat_card("Highest car dependency", top_county["county"], f"{top_county['cars_per_1000']:.0f} per 1,000", accent="#D55E00"), unsafe_allow_html=True)

    with chart_col:
        map_rendered = False
        MAP_CONFIG = {
            **PLOTLY_CONFIG,
            "scrollZoom": True,
            "displayModeBar": True,
            "displaylogo": False,
            "modeBarButtonsToRemove": ["select2d", "lasso2d", "toImage"],
        }

        CITY_COUNTY_ALIASES = {
            "cork": ["cork city", "cork county"],
            "dublin": ["dublin city", "south dublin", "fingal", "dun laoghaire-rathdown", "dún laoghaire-rathdown"],
            "limerick": ["limerick city", "limerick county"],
            "galway": ["galway city", "galway county"],
            "waterford": ["waterford city", "waterford county"],
            "tipperary": ["north tipperary", "south tipperary"],
        }

        CITY_COUNTY_ALIASES = {
            "cork": ["cork city", "cork county"],
            "dublin": ["dublin city", "south dublin", "fingal", "dun laoghaire-rathdown", "dún laoghaire-rathdown"],
            "limerick": ["limerick city", "limerick county"],
            "galway": ["galway city", "galway county"],
            "waterford": ["waterford city", "waterford county"],
            "tipperary": ["north tipperary", "south tipperary"],
        }

        try:
            geojson_data = requests.get(GEOJSON_URL, timeout=10).json()
            name_key = next(k for k in geojson_data["features"][0]["properties"] if "name" in k.lower())
            gj_names = {f["properties"][name_key].strip().lower(): f["properties"][name_key] for f in geojson_data["features"]}

            expanded_rows = []
            for _, row in filtered.iterrows():
                county_key = row["county"].strip().lower()
                candidates = CITY_COUNTY_ALIASES.get(county_key, [county_key, f"{county_key} county"])
                for cand in candidates:
                    if cand in gj_names:
                        new_row = row.copy()
                        new_row["geo_name"] = gj_names[cand]
                        expanded_rows.append(new_row)

            matched = pd.DataFrame(expanded_rows) if expanded_rows else pd.DataFrame()

            if len(matched) >= max(5, len(filtered) // 2):
                fig_map = px.choropleth_mapbox(
                    matched, geojson=geojson_data, locations="geo_name",
                    featureidkey=f"properties.{name_key}", color="combo",
                    color_discrete_map=BIVAR_COLOR_MAP, mapbox_style="carto-positron",
                    zoom=5.6, center={"lat": 53.4, "lon": -8.0}, opacity=0.9,
                    hover_name="county", hover_data={"risk_tier": True, "income_tier": True, "combo": False},
                    height=560,
                )

                LABEL_COUNTIES = {
                    "Dublin": (53.349, -6.260), "Cork": (51.897, -8.470), "Galway": (53.270, -9.048),
                    "Mayo": (53.850, -9.400), "Donegal": (54.653, -8.110), "Kerry": (52.157, -9.567),
                    "Tipperary": (52.473, -8.160),
                }
                fig_map.add_trace(
                    go.Scattermapbox(
                        lat=[c[0] for c in LABEL_COUNTIES.values()], lon=[c[1] for c in LABEL_COUNTIES.values()],
                        mode="text", text=list(LABEL_COUNTIES.keys()),
                        textfont=dict(size=20, color="#FFFFFF"), hoverinfo="skip", showlegend=False,
                    )
                )
                fig_map.add_trace(
                    go.Scattermapbox(
                        lat=[c[0] for c in LABEL_COUNTIES.values()], lon=[c[1] for c in LABEL_COUNTIES.values()],
                        mode="text", text=list(LABEL_COUNTIES.keys()),
                        textfont=dict(size=17, color="#000000"), hoverinfo="skip", showlegend=False,
                    )
                )

                fig_map.update_layout(margin=dict(l=0, r=0, t=10, b=10), showlegend=False)
                fig_map = _add_map_legend(fig_map, BIVAR_COLOR_MAP, RISK_ORDER, INCOME_ORDER)
                st.plotly_chart(fig_map, use_container_width=True, config=MAP_CONFIG)
                map_rendered = True
        except Exception:
            pass

        if not map_rendered:
            COUNTY_COORDS = {
                "Carlow": (52.836, -6.926), "Cavan": (53.990, -7.360), "Clare": (52.845, -8.986),
                "Cork": (51.897, -8.470), "Donegal": (54.653, -8.110), "Dublin": (53.349, -6.260),
                "Galway": (53.270, -9.048), "Kerry": (52.157, -9.567), "Kildare": (53.158, -6.910),
                "Kilkenny": (52.653, -7.244), "Laois": (52.993, -7.332), "Leitrim": (54.125, -8.000),
                "Limerick": (52.664, -8.623), "Longford": (53.727, -7.793), "Louth": (53.898, -6.443),
                "Mayo": (53.850, -9.400), "Meath": (53.605, -6.657), "Monaghan": (54.249, -6.968),
                "Offaly": (53.243, -7.712), "Roscommon": (53.760, -8.190), "Sligo": (54.276, -8.469),
                "Tipperary": (52.473, -8.160), "Waterford": (52.259, -7.110), "Westmeath": (53.533, -7.350),
                "Wexford": (52.336, -6.460), "Wicklow": (52.980, -6.045),
            }
            filtered["lat"] = filtered["county"].map(lambda c: COUNTY_COORDS.get(c, (None, None))[0])
            filtered["lon"] = filtered["county"].map(lambda c: COUNTY_COORDS.get(c, (None, None))[1])
            point_data = filtered.dropna(subset=["lat", "lon"])
            fig_map = px.scatter_mapbox(
                point_data, lat="lat", lon="lon", color="combo", color_discrete_map=BIVAR_COLOR_MAP,
                size="cars_per_1000", size_max=32, hover_name="county",
                hover_data={"risk_tier": True, "income_tier": True, "combo": False},
                zoom=5.7, height=560, mapbox_style="carto-positron", center={"lat": 53.4, "lon": -8.0},
            )
            fig_map.update_traces(marker=dict(sizemin=10))
            fig_map.update_layout(margin=dict(l=0, r=0, t=10, b=10), showlegend=False)
            fig_map = _add_map_legend(fig_map, BIVAR_COLOR_MAP, RISK_ORDER, INCOME_ORDER)
            st.plotly_chart(fig_map, use_container_width=True, config=MAP_CONFIG)

    