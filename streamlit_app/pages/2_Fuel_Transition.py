"""Fuel Transition page."""
import plotly.graph_objects as go
import streamlit as st
import pandas as pd

from data_loader import load_table
from nav import sticky_header
from style import (
    ACTUAL_LINE, BLUISH_GREEN, DATA_LABEL_FONT, FORECAST_LINE, FUEL_COLORS, ORANGE, PLOTLY_CONFIG, TARGET_LINE,
    apply_page_style, chart_heading, chart_layout, chart_subheading, stat_card,
)

apply_page_style()
sticky_header("Fuel Transition", "Fuel Transition")

fuel_annual = load_table("fuel_mix_annual")
ev_forecast = load_table("ev_forecast")
fuel_complete = fuel_annual[fuel_annual["year_complete"]].sort_values("Year")

latest_year = int(fuel_complete["Year"].max())
latest_ev_share = fuel_complete.loc[fuel_complete["Year"] == latest_year, "ev_phev_share"].iloc[0] * 100
forecast_2030 = ev_forecast.loc[ev_forecast["Year"] == 2030, "ev_phev_pct_forecast"].iloc[0]
target_2030 = ev_forecast.loc[ev_forecast["Year"] == 2030, "cap_2030_target_pct"].iloc[0]
gap_2030 = ev_forecast.loc[ev_forecast["Year"] == 2030, "gap_to_target_pp"].iloc[0]
total_latest = int(fuel_complete.loc[fuel_complete["Year"] == latest_year, "total"].iloc[0])

st.divider()

with st.container(border=True):
    c1, c2, c3 = st.columns(3)
    c1.metric(f"New registrations ({latest_year})", f"{total_latest:,}")
    c2.metric(f"EV and PHEV share ({latest_year})", f"{latest_ev_share:.1f}%")
    c3.metric("Gap to CAP 2030 target", f"{gap_2030:.1f}pp")

col1, col2 = st.columns(2)

with col1:
    with st.container(border=True):
        chart_heading("Registrations by Fuel Type")
        chart_subheading(f"Fuel mix of new registrations, 2015 to {latest_year}.")

        fuel_order = ["Petrol", "Diesel", "Hybrid (HEV)", "Plug-in Hybrid (PHEV)", "Battery Electric (BEV)", "Other"]
        fig1 = go.Figure()
        for fuel in fuel_order:
            fig1.add_trace(
                go.Bar(x=fuel_complete["Year"], y=fuel_complete[fuel], name=fuel, marker_color=FUEL_COLORS[fuel])
            )
        fig1.update_layout(barmode="stack")
        fig1 = chart_layout(fig1, height=420)
        fig1.update_layout(
            legend=dict(orientation="h", yanchor="top", y=-0.28, xanchor="center", x=0.5),
            margin=dict(t=20, l=10, r=10, b=110),
            xaxis=dict(dtick=2, title="Year"),
            yaxis_title="Registrations",
        )
        st.plotly_chart(fig1, use_container_width=True, config=PLOTLY_CONFIG)

with col2:
    with st.container(border=True):
        chart_heading("EV and PHEV Adoption")
        chart_subheading("EV and PHEV share of new registrations, actual vs forecast vs target.")

        fig2 = go.Figure()
        fig2.add_trace(
            go.Scatter(
                x=fuel_complete["Year"],
                y=fuel_complete["ev_phev_share"] * 100,
                mode="lines+markers",
                name="Actual",
                line=dict(color=BLUISH_GREEN, **ACTUAL_LINE),
            )
        )
        fig2.add_trace(
            go.Scatter(
                x=ev_forecast["Year"],
                y=ev_forecast["ev_phev_pct_forecast"],
                mode="lines+markers",
                name="BAU forecast",
                line=dict(color=ORANGE, **FORECAST_LINE),
            )
        )
        fig2.add_trace(
            go.Scatter(
                x=[fuel_complete["Year"].min(), 2030],
                y=[target_2030, target_2030],
                mode="lines",
                name="CAP 2030 target",
                line=dict(color=TARGET_LINE["color"], dash=TARGET_LINE["dash"], width=TARGET_LINE["width"]),
            )
        )
        fig2 = chart_layout(fig2, height=420)
        fig2.update_layout(xaxis=dict(dtick=2, title="Year"), yaxis_title="Share of registrations (%)")
        st.plotly_chart(fig2, use_container_width=True, config=PLOTLY_CONFIG)

st.write("")
with st.container(border=True):
    chart_heading("Registrations Needed to Close the Gap")
    chart_subheading("Monthly EV and hybrid registrations needed to close the gap to the CAP 2030 target, anchored to the latest actual month.")

    reg_gap = load_table("ev_registration_gap").copy()
    reg_gap["Date"] = pd.to_datetime(reg_gap["Date"])
    reg_gap = reg_gap.sort_values("Date")
    latest_gap_row = reg_gap.iloc[-1]

    card_col, chart_col = st.columns([1, 2])
    with card_col:
        st.markdown(
            stat_card(
                f"Additional registrations needed ({latest_gap_row['Date'].strftime('%b %Y')})",
                f"{int(latest_gap_row['additional_registrations_needed_monthly']):,}/mo",
                f"~{latest_gap_row['additional_registrations_needed_daily']:,.1f} more per day, "
                f"{reg_gap['Date'].min().strftime('%b %Y')} to {reg_gap['Date'].max().strftime('%b %Y')}",
                accent=ORANGE,
            ),
            unsafe_allow_html=True,
        )

    with chart_col:
        fig4 = go.Figure()
        label_mask = reg_gap["Date"].dt.month == 1  # label only January of each year

        fig4.add_trace(
            go.Scatter(
                x=reg_gap["Date"], y=reg_gap["bau_registrations_monthly"],
                mode="lines+text", name="BAU trajectory", line=dict(color=ORANGE, width=3),
                text=[f"{v:,.0f}" if lab else "" for v, lab in zip(reg_gap["bau_registrations_monthly"], label_mask)],
                textposition="top right", textfont=DATA_LABEL_FONT,
                yaxis="y2",
            )
        )
        fig4.add_trace(
            go.Scatter(
                x=reg_gap["Date"], y=reg_gap["required_registrations_monthly"],
                mode="lines+text", name="Required for CAP target", line=dict(color=BLUISH_GREEN, width=3),
                text=[f"{v:,.0f}" if lab else "" for v, lab in zip(reg_gap["required_registrations_monthly"], label_mask)],
                textposition="top left", textfont=DATA_LABEL_FONT,
            )
        )
        fig4 = chart_layout(fig4, height=340)
        bau_min, bau_max = reg_gap["bau_registrations_monthly"].min(), reg_gap["bau_registrations_monthly"].max()
        bau_pad = (bau_max - bau_min) * 0.4 if bau_max > bau_min else 50
        fig4.update_layout(
            xaxis=dict(title="Month", range=[reg_gap["Date"].min(), reg_gap["Date"].max()]),
            yaxis=dict(title="Required for CAP target", title_font=dict(color=BLUISH_GREEN), tickfont=dict(color=BLUISH_GREEN)),
            yaxis2=dict(
                title="BAU trajectory", overlaying="y", side="right",
                range=[bau_min - bau_pad, bau_max + bau_pad],
                showgrid=False,
                title_font=dict(color=ORANGE), tickfont=dict(color=ORANGE),
            ),
        )
        fig4.add_annotation(
            x=0.02, y=1.14, xref="paper", yref="paper", showarrow=False,
            xanchor="left", yanchor="top", align="left",
            text="Note: BAU reflects the fitted long-run S-curve (2015–2025 real data).<br>"
                 "Recent monthly actuals sit above it, following a 2024 registration dip<br>"
                 "and 2025 rebound the curve's monotonic shape can't capture.",
            font=dict(size=11, color="#6E6E6E"),
        )
        st.plotly_chart(fig4, use_container_width=True, config=PLOTLY_CONFIG)
        
st.write("")
with st.container(border=True):
    chart_heading("CO2 Per Capita - Projected Impact of the EV Transition")
    chart_subheading("Projected private-car CO2 emissions per person, 2024–2030, versus the latest actual (2023).")

    co2_fc = load_table("co2_per_capita").sort_values("Year")
    baseline_kg = co2_fc["baseline_2023_co2_per_capita_kg"].iloc[0]
    latest_row_co2 = co2_fc.iloc[-1]

    card_col, chart_col = st.columns([1, 2])
    with card_col:
        st.markdown(
            stat_card(
                f"CO2/capita by {int(latest_row_co2['Year'])}",
                f"{latest_row_co2['co2_per_capita_kg']:,.0f} kg",
                f"{latest_row_co2['pct_decrease_vs_latest_actual']:.1f}% below the 2023 actual ({baseline_kg:,.0f} kg)",
                accent=BLUISH_GREEN,
            ),
            unsafe_allow_html=True,
        )

    with chart_col:
        fig5 = go.Figure()
        fig5.add_trace(
            go.Scatter(
                x=co2_fc["Year"], y=co2_fc["co2_per_capita_kg"],
                mode="lines+markers+text", name="Projected CO2/capita",
                line=dict(color=BLUISH_GREEN, width=3),
                text=[f"{v:,.0f}" for v in co2_fc["co2_per_capita_kg"]],
                textposition="top center", textfont=DATA_LABEL_FONT,
            )
        )
        fig5.add_trace(
            go.Scatter(
                x=[co2_fc["Year"].min(), co2_fc["Year"].max()], y=[baseline_kg, baseline_kg],
                mode="lines", name="2023 actual (baseline)",
                line=dict(color=TARGET_LINE["color"], dash=TARGET_LINE["dash"], width=TARGET_LINE["width"]),
            )
        )
        fig5 = chart_layout(fig5, height=340)
        fig5.update_layout(xaxis=dict(dtick=1, title="Year"), yaxis=dict(title="CO2 per capita (kg)"))
        st.plotly_chart(fig5, use_container_width=True, config=PLOTLY_CONFIG)