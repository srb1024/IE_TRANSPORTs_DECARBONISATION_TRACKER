"""Overview page."""
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from data_loader import load_table
from nav import hide_sidebar, nav_bar, page_heading
from style import (
    ACTUAL_LINE, BLUE, BLUISH_GREEN, KPI_COLORS, KPI_LABELS, ORANGE, PLOTLY_CONFIG,
    VERMILLION, add_covid_highlight, apply_page_style, chart_layout, kpi_circle_card, stat_card,
)

st.set_page_config(page_title="Overview | Irish Transport Decarbonisation Tracker", page_icon="🚆", layout="wide")
hide_sidebar()
apply_page_style()

page_heading("Overview")
nav_bar("Overview")

fact = load_table("fact_transport")
fuel = load_table("fuel_mix_annual")
ev_forecast = load_table("ev_forecast")
county = load_table("county_recommendations")

core = fact[fact["Year"].between(2019, 2023)].sort_values("Year").reset_index(drop=True)
year = st.select_slider("Year", options=core["Year"].tolist(), value=2023)
row = core.loc[core["Year"] == year].iloc[0]
baseline_row = core.loc[core["Year"] == 2019].iloc[0]


def pct_since_2019(kpi_key):
    base_val = baseline_row[kpi_key]
    cur_val = row[kpi_key]
    if pd.isna(cur_val) or pd.isna(base_val) or base_val == 0:
        return None
    return (cur_val / base_val - 1) * 100


# Every value below is read from the loaded dataframes for the selected
# year, nothing here is a fixed string.
with st.container(border=True):
    c1, c2, c3 = st.columns(3)
    c1.markdown(
        kpi_circle_card(
            "Car Dependency Index", "Cars per 1,000 population",
            f"{row['car_dependency_index']:.2f}", pct_since_2019("car_dependency_index"),
            circle_color=VERMILLION,
        ),
        unsafe_allow_html=True,
    )
    c2.markdown(
        kpi_circle_card(
            "Public Transport Usage Index", "Journeys per capita",
            f"{row['pt_usage_index']:.2f}", pct_since_2019("pt_usage_index"),
            circle_color=BLUE,
        ),
        unsafe_allow_html=True,
    )
    tii_val = f"{row['transport_intensity_index']:.2f}" if pd.notna(row["transport_intensity_index"]) else "n/a"
    c3.markdown(
        kpi_circle_card(
            "Transport Intensity Indicator", "Vehicle km per capita",
            tii_val, pct_since_2019("transport_intensity_index"),
            circle_color=BLUISH_GREEN,
        ),
        unsafe_allow_html=True,
    )
    st.caption("Delta shown is the percentage change versus the 2019 baseline: (value for the selected year divided by the 2019 value) times 100, minus 100.")

indexed = core.copy()
for kpi in KPI_LABELS:
    base_val = indexed.loc[indexed["Year"] == 2019, kpi].iloc[0]
    indexed[f"{kpi}_idx"] = indexed[kpi] / base_val * 100

chart_col, side_col = st.columns([2, 1])
with chart_col, st.container(border=True):
    fig = go.Figure()
    for kpi, label in KPI_LABELS.items():
        fig.add_trace(go.Scatter(x=indexed["Year"], y=indexed[f"{kpi}_idx"], mode="lines+markers", name=label, line=dict(color=KPI_COLORS[kpi], **ACTUAL_LINE)))
    fig = add_covid_highlight(fig)
    fig = chart_layout(fig, title="KPIs indexed to 2019", height=300)
    fig.update_layout(xaxis=dict(dtick=1, title="Year"), yaxis_title="Index (2019 = 100)")
    st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)

with side_col, st.container(border=True):
    pct_vals = [pct_since_2019(k) or 0 for k in KPI_LABELS]
    fig2 = go.Figure(go.Bar(x=list(KPI_LABELS.values()), y=pct_vals, marker_color=list(KPI_COLORS.values())))
    fig2 = chart_layout(fig2, title=f"% change since 2019, {year}", height=300)
    fig2.update_layout(yaxis_title="% change since 2019", xaxis_title=None)
    st.plotly_chart(fig2, use_container_width=True, config=PLOTLY_CONFIG)

st.subheader("At a glance", anchor=False)
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
c1.markdown(stat_card(f"EV share ({latest_fuel_year})", f"{ev_share_latest:.1f}%", f"{gap_2030:.1f}pp below target", accent=BLUISH_GREEN), unsafe_allow_html=True)
c2.markdown(stat_card("Private car fleet (2023)", f"{cars_2023/1e6:.2f}M", f"+{car_growth:.1f}% since 2019", accent=VERMILLION), unsafe_allow_html=True)
c3.markdown(stat_card(f"PT journeys ({pt_latest_year})", f"{pt_latest/1e6:.0f}M", "Bus, rail and Luas", accent=BLUE), unsafe_allow_html=True)
c4.markdown(stat_card("Counties needing action", f"{n_critical} of {n_counties}", "Critical priority", accent=ORANGE), unsafe_allow_html=True)