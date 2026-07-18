"""Overview page."""
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from data_loader import load_table
from nav import sticky_header
from style import (
    ACTUAL_LINE, BLUE, BLUISH_GREEN, DATA_LABEL_FONT, KPI_COLORS, KPI_LABELS, KPI_MARKERS, ORANGE, PLOTLY_CONFIG,
    VERMILLION, add_covid_highlight, apply_page_style, chart_heading, chart_layout, chart_subheading,
    kpi_circle_card, stat_card,
)

apply_page_style()
sticky_header("Overview", "Overview")

fact = load_table("fact_transport")
fuel = load_table("fuel_mix_annual")
ev_forecast = load_table("ev_forecast")
county = load_table("county_recommendations")

# 2019 to 2023 is the window where every KPI has complete data
core = fact[fact["Year"].between(2019, 2023)].sort_values("Year").reset_index(drop=True)
year_options = core["Year"].tolist()

# Default the year picker to the most recent year available
if "overview_year" not in st.session_state:
    st.session_state.overview_year = year_options[-1]

st.divider()

# Year pills: the selected one is static markup, the rest are clickable buttons
pill_cols = st.columns([2, 2] + [1] * len(year_options) + [2, 2])
for i, yr in enumerate(year_options):
    with pill_cols[i + 2]:
        if yr == st.session_state.overview_year:
            st.markdown(
                f'<div style="background:#1A2332; color:white; text-align:center; '
                f'padding:8px 0; border-radius:8px; font-weight:700; font-size:1.02rem; '
                f'border:1px solid #1A2332; box-sizing:border-box;">{yr}</div>',
                unsafe_allow_html=True,
            )
        else:
            if st.button(str(yr), key=f"yr_pill_{yr}", use_container_width=True):
                st.session_state.overview_year = yr
                st.rerun()
# Selected year plus the 2019 baseline every comparison is measured against
year = st.session_state.overview_year
row = core.loc[core["Year"] == year].iloc[0]
baseline_row = core.loc[core["Year"] == 2019].iloc[0]


def pct_since_2019(kpi_key):
    """Percent change vs 2019. Returns None when either value is missing."""
    base_val = baseline_row[kpi_key]
    cur_val = row[kpi_key]
    if pd.isna(cur_val) or pd.isna(base_val) or base_val == 0:
        return None
    return (cur_val / base_val - 1) * 100


# Headline KPI cards for the selected year
with st.container(border=True, key="kpi_cards_box"):
    c1, c2, c3 = st.columns(3)
    c1.markdown(
        kpi_circle_card(
            "Car Dependency Index",
            "Cars per 1,000 population",
            f"{row['car_dependency_index']:.2f}",
            pct_since_2019("car_dependency_index"),
            circle_color=VERMILLION,
        ),
        unsafe_allow_html=True,
    )
    c2.markdown(
        kpi_circle_card(
            "Public Transport Usage Index",
            "Journeys per capita",
            f"{row['pt_usage_index']:.2f}",
            pct_since_2019("pt_usage_index"),
            circle_color=BLUE,
        ),
        unsafe_allow_html=True,
    )
    # Vehicle km data runs short in some years so this KPI can be blank
    tii_val = f"{row['transport_intensity_index']:.2f}" if pd.notna(row["transport_intensity_index"]) else "n/a"
    c3.markdown(
        kpi_circle_card(
            "Transport Intensity Indicator",
            "Vehicle km per capita",
            tii_val,
            pct_since_2019("transport_intensity_index"),
            circle_color=BLUISH_GREEN,
        ),
        unsafe_allow_html=True,
    )

# Rebase every KPI to 2019 = 100 so three different units share one axis
indexed = core.copy()
for kpi in KPI_LABELS:
    base_val = indexed.loc[indexed["Year"] == 2019, kpi].iloc[0]
    indexed[f"{kpi}_idx"] = indexed[kpi] / base_val * 100

# Wide trend chart on the left, single-year bar chart on the right
chart_col, side_col = st.columns([2, 1])
with chart_col:
    with st.container(border=True):
        chart_heading("KPIs indexed to 2019")
        chart_subheading("Shows how each KPI has moved relative to its own 2019 level, on a common scale.")

        fig = go.Figure()
        for kpi, label in KPI_LABELS.items():
            fig.add_trace(
                go.Scatter(
                    x=indexed["Year"], y=indexed[f"{kpi}_idx"], mode="lines+markers",
                    name=label,
                    line=dict(color=KPI_COLORS[kpi], **ACTUAL_LINE),
                    marker=dict(symbol=KPI_MARKERS[kpi], size=9),
                )
            )
        fig = add_covid_highlight(fig)
        fig = chart_layout(fig, height=380)
        fig.update_layout(xaxis=dict(dtick=1, title="Year"), yaxis_title="Index (2019 = 100)")
        st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)

with side_col:
    with st.container(border=True):
        chart_heading(f"% change since 2019 - {year}")
        chart_subheading("Percentage change for each KPI in the selected year, relative to 2019.")

        pct_vals = [pct_since_2019(k) or 0 for k in KPI_LABELS]
        fig2 = go.Figure()
        for (kpi, label), pct_val in zip(KPI_LABELS.items(), pct_vals):
            fig2.add_trace(
                go.Bar(
                    x=[label], y=[pct_val], name=label, marker_color=KPI_COLORS[kpi], showlegend=True,
                    text=[f"{pct_val:+.1f}%"], textposition="outside", textfont=DATA_LABEL_FONT,
                )
            )
        fig2 = chart_layout(fig2, height=380)
        fig2.update_layout(yaxis_title="% change since 2019", xaxis=dict(visible=False, showticklabels=False, title=None))
        st.plotly_chart(fig2, use_container_width=True, config=PLOTLY_CONFIG)

st.subheader("At a glance", anchor=False)

# Pull the handful of standout numbers for the summary cards below
# Only full years count, otherwise a part-year would look like a real drop
fuel_complete = fuel[fuel["year_complete"]].sort_values("Year")
latest_fuel_year = int(fuel_complete["Year"].max())
ev_share_latest = fuel_complete.loc[fuel_complete["Year"] == latest_fuel_year, "ev_phev_share"].iloc[0] * 100
gap_2030 = ev_forecast.loc[ev_forecast["Year"] == 2030, "gap_to_target_pp"].iloc[0]
cars_2019 = fact.loc[fact["Year"] == 2019, "private_cars"].iloc[0]
cars_2023 = fact.loc[fact["Year"] == 2023, "private_cars"].iloc[0]
car_growth = (cars_2023 / cars_2019 - 1) * 100
pt_latest_year = int(fact["Year"].max())
pt_latest = fact.loc[fact["Year"] == pt_latest_year, "pt_total_journeys"].iloc[0]
n_critical = int((county["risk_tier"] == "Critical").sum())
n_counties = county["county"].nunique()

c1, c2, c3, c4 = st.columns(4)
c1.markdown(
    stat_card(f"EV share ({latest_fuel_year})", f"{ev_share_latest:.1f}%", f"{gap_2030:.1f}pp below target", accent=BLUISH_GREEN),
    unsafe_allow_html=True,
)
c2.markdown(
    stat_card("Private car fleet (2023)", f"{cars_2023/1e6:.2f}M", f"+{car_growth:.1f}% since 2019", accent=VERMILLION),
    unsafe_allow_html=True,
)
c3.markdown(
    stat_card(f"PT journeys ({pt_latest_year})", f"{pt_latest/1e6:.0f}M", "Bus, rail and Luas", accent=BLUE),
    unsafe_allow_html=True,
)
c4.markdown(
    stat_card("Counties needing action", f"{n_critical} of {n_counties}", "Critical priority", accent=ORANGE),
    unsafe_allow_html=True,
)

st.write("")

col_a, col_b = st.columns(2)

with col_a:
    # Stacked fleet split, with the non-traditional percentage labelled on top
    comp = fact[["Year", "traditional_cdi", "non_traditional_cdi"]].dropna().sort_values("Year")
    comp_share = comp["non_traditional_cdi"] / (comp["traditional_cdi"] + comp["non_traditional_cdi"]) * 100
    comp_total = comp["traditional_cdi"] + comp["non_traditional_cdi"]

    with st.container(border=True):
        chart_heading("Fleet Composition")
        chart_subheading("Fleet split between traditional and non-traditional vehicles, 2018 to 2023.")

        fig3 = go.Figure()
        fig3.add_trace(go.Bar(x=comp["Year"], y=comp["traditional_cdi"], name="Traditional (Petrol + Diesel)", marker_color=VERMILLION))
        fig3.add_trace(go.Bar(x=comp["Year"], y=comp["non_traditional_cdi"], name="Non-Traditional (EV + Hybrid + PHEV)", marker_color=BLUISH_GREEN))
        fig3.update_layout(barmode="stack")

        # Float each share label above its bar, clear of the stack
        for yr, share, total in zip(comp["Year"], comp_share, comp_total):
            fig3.add_annotation(
                x=yr, y=total + comp_total.max() * 0.12,
                text=f"{share:.1f}%", showarrow=False,
                font=DATA_LABEL_FONT,
            )

        fig3 = chart_layout(fig3, height=380)
        fig3.update_layout(
            xaxis=dict(dtick=1, title="Year"),
            yaxis=dict(title="Cars per 1,000 population", range=[0, comp_total.max() * 1.30]),
            legend=dict(orientation="h", yanchor="top", y=1.12, xanchor="center", x=0.5),
            margin=dict(t=60, l=10, r=10, b=10),
        )
        st.plotly_chart(fig3, use_container_width=True, config=PLOTLY_CONFIG)

with col_b:
    # CO2 avoided by the non-traditional fleet, one bar per year
    co2 = fact[["Year", "co2_avoided_tonnes"]].dropna().sort_values("Year")

    with st.container(border=True):
        chart_heading("Estimated CO2 Avoided")
        chart_subheading("Estimated CO2 avoided by the non-traditional fleet, 2018 to 2023.")

        fig5 = go.Figure()
        fig5.add_trace(
            go.Bar(
                x=co2["Year"], y=co2["co2_avoided_tonnes"], marker_color=BLUISH_GREEN,
                text=[f"{v:,.0f}" for v in co2["co2_avoided_tonnes"]],
                textposition="outside", textfont=DATA_LABEL_FONT,
            )
        )
        fig5 = chart_layout(fig5, height=380)
        fig5.update_layout(
            xaxis=dict(dtick=1, title="Year"),
            yaxis_title="Tonnes CO2",
            showlegend=False,
            margin=dict(t=60, l=10, r=10, b=10),
        )
        st.plotly_chart(fig5, use_container_width=True, config=PLOTLY_CONFIG)