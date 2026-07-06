"""Predictive Analytics page."""
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from data_loader import load_table
from nav import hide_sidebar, nav_bar, page_heading
from style import (
    ACTUAL_LINE, BLUE, FORECAST_LINE, KPI_COLORS, KPI_FORECAST_COLORS, KPI_LABELS, KPI_UNITS,
    PLOTLY_CONFIG, add_covid_highlight, apply_page_style, chart_layout,
)

st.set_page_config(page_title="Predictive | Irish Transport Decarbonisation Tracker", page_icon="🔮", layout="wide")
hide_sidebar()
apply_page_style()

page_heading("Predictive Analytics")
nav_bar("Predictive")

fact = load_table("fact_transport")
hw = load_table("kpi_forecast_hw")
sarima = load_table("pt_forecast_sarima")


def hw_chart(kpi_key, kpi_label, height=280):
    actual = fact[["Year", kpi_key]].dropna().sort_values("Year")
    last_year = actual["Year"].max()
    last_val = actual.loc[actual["Year"] == last_year, kpi_key].iloc[0]
    fc = hw[hw["kpi"] == kpi_key].sort_values("Year")
    fc_after = fc[fc["Year"] > last_year]
    mape = fc["MAPE_pct"].iloc[0] if not fc.empty else None

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=actual["Year"], y=actual[kpi_key], mode="lines+markers", name="Actual", line=dict(color=KPI_COLORS[kpi_key], **ACTUAL_LINE)))
    fx = [last_year] + fc_after["Year"].tolist()
    fy = [last_val] + fc_after["forecast_value"].tolist()
    if len(fx) > 1:
        fig.add_trace(go.Scatter(x=fx, y=fy, mode="lines+markers", name="Forecast", line=dict(color=KPI_FORECAST_COLORS[kpi_key], **FORECAST_LINE)))
    fig = add_covid_highlight(fig)
    fig = chart_layout(fig, title=kpi_label, height=height)
    fig.update_layout(xaxis=dict(dtick=2, title="Year"), yaxis_title=KPI_UNITS[kpi_key])
    return fig, mape


row1 = st.columns(2)
with row1[0], st.container(border=True):
    fig, mape = hw_chart("car_dependency_index", "Car Dependency Index (Holt-Winters)")
    st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG, key="cdi_chart")
    if mape is not None:
        st.caption(f"Holdout MAPE {mape:.2f}%")

with row1[1], st.container(border=True):
    fig, mape = hw_chart("transport_intensity_index", "Transport Intensity Indicator (Holt-Winters)")
    st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG, key="tii_chart")
    if mape is not None:
        st.caption(f"Holdout MAPE {mape:.2f}%")

row2 = st.columns(2)
with row2[0], st.container(border=True):
    fig, mape = hw_chart("pt_usage_index", "Public Transport Usage Index (Holt-Winters)")
    st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG, key="ptui_chart")
    if mape is not None:
        st.caption(f"Holdout MAPE {mape:.2f}%")

with row2[1], st.container(border=True):
    sarima_sorted = sarima.sort_values("Date")
    mape_sarima = sarima_sorted["MAPE_pct"].iloc[0]

    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(
        x=pd.concat([sarima_sorted["Date"], sarima_sorted["Date"][::-1]]),
        y=pd.concat([sarima_sorted["ci_upper"], sarima_sorted["ci_lower"][::-1]]),
        fill="toself", fillcolor="rgba(0,114,178,0.15)", line=dict(color="rgba(0,0,0,0)"),
        name="95% confidence interval",
    ))
    fig2.add_trace(go.Scatter(x=sarima_sorted["Date"], y=sarima_sorted["pt_journeys_forecast"], mode="lines+markers", name="Forecast", line=dict(color=BLUE, **FORECAST_LINE)))
    fig2 = chart_layout(fig2, title="Monthly PT Journeys (SARIMA)", height=280)
    fig2.update_layout(yaxis_title="Journeys", xaxis_title="Month")
    st.plotly_chart(fig2, use_container_width=True, config=PLOTLY_CONFIG, key="sarima_chart")

    negative_months = int((sarima_sorted["ci_lower"] < 0).sum())
    caption = f"Holdout MAPE {mape_sarima:.2f}%."
    if negative_months:
        caption += f" Lower bound dips below zero for {negative_months} months near the end of the horizon, reflecting wide uncertainty rather than a real possibility."
    st.caption(caption)