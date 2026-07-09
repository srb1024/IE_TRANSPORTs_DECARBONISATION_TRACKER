"""Predictive Analytics page."""
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from data_loader import load_table
from nav import sticky_header
from style import (
    ACTUAL_LINE, BLUE, DATA_LABEL_FONT, FORECAST_LINE, KPI_COLORS, KPI_FORECAST_COLORS, KPI_LABELS, KPI_UNITS,
    PLOTLY_CONFIG, add_covid_highlight, apply_page_style, chart_layout,
)

apply_page_style()
sticky_header("Predictive Analytics", "Predictive")

fact = load_table("fact_transport")
hw = load_table("kpi_forecast_hw")
sarima = load_table("pt_forecast_sarima")


def _fmt(v, kpi_key):
    return f"{v:,.0f}" if kpi_key == "transport_intensity_index" else f"{v:.1f}"


def hw_chart(kpi_key, kpi_label, height=340):
    actual = fact[["Year", kpi_key]].dropna().sort_values("Year")
    last_year = actual["Year"].max()
    last_val = actual.loc[actual["Year"] == last_year, kpi_key].iloc[0]
    fc = hw[hw["kpi"] == kpi_key].sort_values("Year")
    fc_after = fc[fc["Year"] > last_year]
    mape = fc["MAPE_pct"].iloc[0] if not fc.empty else None

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=actual["Year"],
            y=actual[kpi_key],
            mode="lines+markers+text",
            name="Actual",
            line=dict(color=KPI_COLORS[kpi_key], **ACTUAL_LINE),
            text=[_fmt(v, kpi_key) for v in actual[kpi_key]],
            textposition="top center",
            textfont=DATA_LABEL_FONT,
        )
    )
    fx = [last_year] + fc_after["Year"].tolist()
    fy = [last_val] + fc_after["forecast_value"].tolist()
    if len(fx) > 1:
        fig.add_trace(
            go.Scatter(
                x=fx,
                y=fy,
                mode="lines+markers+text",
                name="Forecast",
                line=dict(color=KPI_FORECAST_COLORS[kpi_key], **FORECAST_LINE),
                text=[""] + [_fmt(v, kpi_key) for v in fc_after["forecast_value"]],
                textposition="bottom center",
                textfont=DATA_LABEL_FONT,
            )
        )
    fig = add_covid_highlight(fig)
    fig = chart_layout(fig, title=kpi_label, height=height)

    # Data labels sit above each marker (textposition="top center"), but
    # Plotly's auto y-range only considers the values themselves, not the
    # label text drawn above them, so the peak point's label was getting
    # clipped by the plot's top edge. Extra headroom above the max fixes it.
    all_vals = pd.concat([actual[kpi_key], pd.Series(fy)])
    span = all_vals.max() - all_vals.min()
    y_range = [all_vals.min() - span * 0.08, all_vals.max() + span * 0.20]

    fig.update_layout(xaxis=dict(dtick=2, title="Year"), yaxis=dict(title=KPI_UNITS[kpi_key], range=y_range))
    return fig, mape


row1 = st.columns(2)
with row1[0]:
    with st.container(border=True):
        fig, mape = hw_chart("car_dependency_index", "Car Dependency Index (Holt-Winters)")
        st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG, key="cdi_chart")
        if mape is not None:
            st.caption(f"Holdout MAPE {mape:.2f}%")

with row1[1]:
    with st.container(border=True):
        fig, mape = hw_chart("transport_intensity_index", "Transport Intensity Indicator (Holt-Winters)")
        st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG, key="tii_chart")
        if mape is not None:
            st.caption(f"Holdout MAPE {mape:.2f}%")

row2 = st.columns(2)
with row2[0]:
    with st.container(border=True):
        fig, mape = hw_chart("pt_usage_index", "Public Transport Usage Index (Holt-Winters)")
        st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG, key="ptui_chart")
        if mape is not None:
            st.caption(f"Holdout MAPE {mape:.2f}%")

with row2[1]:
    with st.container(border=True):
        sarima_sorted = sarima.sort_values("Date").reset_index(drop=True)
        mape_sarima = sarima_sorted["MAPE_pct"].iloc[0]

        label_months = {(2023, 1), (2023, 4), (2023, 7), (2023, 10)}
        month_year = list(zip(sarima_sorted["Date"].dt.year, sarima_sorted["Date"].dt.month))
        sarima_labels = [
        f"{v/1e6:.1f}M" if my in label_months else ""
        for v, my in zip(sarima_sorted["pt_journeys_forecast"], month_year)
        ]

        fig2 = go.Figure()
        fig2.add_trace(
            go.Scatter(
                x=pd.concat([sarima_sorted["Date"], sarima_sorted["Date"][::-1]]),
                y=pd.concat([sarima_sorted["ci_upper"], sarima_sorted["ci_lower"][::-1]]),
                fill="toself",
                fillcolor="rgba(0,114,178,0.15)",
                line=dict(color="rgba(0,0,0,0)"),
                name="95% CI",
            )
        )
        fig2.add_trace(
            go.Scatter(
                x=sarima_sorted["Date"],
                y=sarima_sorted["pt_journeys_forecast"],
                mode="lines+markers+text",
                name="Forecast",
                line=dict(color=BLUE, **FORECAST_LINE),
                text=sarima_labels,
                textposition="top center",
                textfont=DATA_LABEL_FONT,
            )
        )
        fig2 = chart_layout(fig2, title="Monthly PT Journeys (SARIMA)", height=340)
        fig2.update_layout(yaxis_title="Journeys", xaxis_title="Month")
        st.plotly_chart(fig2, use_container_width=True, config=PLOTLY_CONFIG, key="sarima_chart")

        caption = (
            f"Holdout MAPE {mape_sarima:.2f}%. 12-month forecast horizon, deliberately "
            f"short given roughly 2 clean non-COVID training years, forecasting further "
            f"out would have overreached what that training window can support."
        )
        st.caption(caption)