"""Shared design system: colours, chart styling and layout helpers."""
from __future__ import annotations

import streamlit as st

BLACK = "#000000"
ORANGE = "#E69F00"
SKY_BLUE = "#56B4E9"
BLUISH_GREEN = "#009E73"
YELLOW = "#F0E442"
BLUE = "#0072B2"
VERMILLION = "#D55E00"
REDDISH_PURPLE = "#CC79A7"
GREY = "#3D4249"
GRID_GREY = "#E3E6EA"

DATA_LABEL_FONT = dict(size=20, family="Arial, sans-serif", color="#1A2332")
KPI_COLORS = {
    "car_dependency_index": VERMILLION,
    "pt_usage_index": BLUE,
    "transport_intensity_index": BLUISH_GREEN,
}
KPI_FORECAST_COLORS = {
    "car_dependency_index": ORANGE,
    "pt_usage_index": SKY_BLUE,
    "transport_intensity_index": REDDISH_PURPLE,
}
KPI_LABELS = {
    "car_dependency_index": "Car Dependency Index",
    "pt_usage_index": "Public Transport Usage Index",
    "transport_intensity_index": "Transport Intensity Indicator",
}
KPI_UNITS = {
    "car_dependency_index": "Cars per 1,000 population",
    "pt_usage_index": "Journeys per capita",
    "transport_intensity_index": "Vehicle km per capita",
}

FUEL_COLORS = {
    "Petrol": VERMILLION,
    "Diesel": ORANGE,
    "Hybrid (HEV)": YELLOW,
    "Plug-in Hybrid (PHEV)": SKY_BLUE,
    "Battery Electric (BEV)": BLUISH_GREEN,
    "Other": GREY,
}

ACTUAL_LINE = dict(width=3, dash="solid")
FORECAST_LINE = dict(width=3, dash="dot")
TARGET_LINE = dict(color=BLACK, width=2, dash="dashdot")

STATUS_COLORS = {"On Track": BLUE, "At Risk": ORANGE, "Off Track": VERMILLION}

PLOTLY_CONFIG = {"displayModeBar": False}


def status_badge(status: str) -> str:
    color = STATUS_COLORS.get(status, GREY)
    return (
        f'<span style="background-color:{color}20; color:{color}; '
        f'border:1px solid {color}; border-radius:6px; padding:4px 12px; '
        f'font-weight:600; font-size:0.95rem; white-space:nowrap;">{status}</span>'
    )


def stat_card(label: str, value: str, sub: str = "", accent: str = BLUE) -> str:
    sub_html = f'<div style="color:{GREY}; font-size:0.85rem; margin-top:3px;">{sub}</div>' if sub else ""
    return (
        f'<div style="background:#F7F8FA; border:1px solid #E3E6EA; '
        f'border-left:4px solid {accent}; border-radius:10px; padding:16px 18px; '
        f'min-height:126px; display:flex; flex-direction:column; justify-content:center;">'
        f'<div style="color:{GREY}; font-size:0.92rem; font-weight:600;">{label}</div>'
        f'<div style="font-size:1.8rem; font-weight:700; color:#1A2332; line-height:1.2;">{value}</div>'
        f'{sub_html}</div>'
    )


def kpi_circle_card(title: str, subtitle: str, value: str, delta_pct, circle_color: str = BLUE) -> str:
    if delta_pct is None:
        delta_html = ""
    else:
        d_color = BLUE if delta_pct >= 0 else VERMILLION
        sign = "+" if delta_pct >= 0 else ""
        delta_html = (
            f'<span style="font-size:0.8rem; font-weight:700; color:{d_color}; '
            f'background:{d_color}18; padding:3px 8px; border-radius:6px; white-space:nowrap;">'
            f'{sign}{delta_pct:.1f}%</span>'
        )
    return (
        f'<div style="background:white; border:1px solid #E3E6EA; border-radius:12px; '
        f'padding:16px 18px; min-height:136px; display:flex; flex-direction:column; '
        f'justify-content:space-between;">'
        f'<div>'
        f'<div style="font-weight:700; font-size:1.05rem; color:#1A2332;">{title}</div>'
        f'<div style="color:{GREY}; font-size:0.85rem;">{subtitle}</div>'
        f'</div>'
        f'<div style="display:flex; align-items:center; gap:12px; margin-top:8px;">'
        f'<div style="width:36px; height:36px; min-width:36px; border-radius:50%; background:{circle_color}55;"></div>'
        f'<div style="font-size:1.85rem; font-weight:700; color:#1A2332; flex-grow:1;">{value}</div>'
        f'{delta_html}'
        f'</div>'
        f'</div>'
    )


def apply_page_style() -> None:
    st.markdown(
        """
        <style>
        .stApp { background-color: #FFFFFF; }
        .block-container {
            padding-top: 0.6rem;
            padding-bottom: 2rem;
            padding-left: 2rem;
            padding-right: 2rem;
            background-color: #FFFFFF;
        }
        .stMarkdown p, .stMarkdown li, label, .stSelectbox label {
            font-size: 1.05rem !important;
            color: #1A2332;
        }
        .stCaption, [data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] p {
            font-size: 0.92rem !important;
            color: #3D4249 !important;
        }
        h2 { font-size: 1.55rem !important; }
        h3 { font-size: 1.3rem !important; }
        div[data-testid="stMetric"] {
            background-color: #F7F8FA;
            border: 1px solid #E3E6EA;
            border-radius: 12px;
            padding: 18px 18px 14px 18px;
            min-height: 126px;
        }
        div[data-testid="stMetricLabel"] { font-weight: 600; font-size: 1.0rem; }
        div[data-testid="stMetricValue"] { font-size: 2.2rem; font-weight: 700; }
        h1, h2, h3 { letter-spacing: -0.01em; }
        div[data-testid="stVerticalBlockBorderWrapper"] {
            border-radius: 12px;
            padding: 6px;
        }
        [data-testid="stHeaderActionElements"] { display: none !important; }
        h1 svg, h2 svg, h3 svg { display: none !important; }
        h1 a, h2 a, h3 a { pointer-events: none; text-decoration: none; }
        section[data-testid="stSidebar"] { display: none !important; }
        div[data-testid="stSidebarCollapsedControl"] { display: none !important; }
        [data-testid="collapsedControl"] { display: none !important; }
        .stButton button {
            font-size: 1.02rem !important;
            font-weight: 600;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def add_covid_highlight(fig):
    fig.add_vrect(x0=2019.5, x1=2021.5, fillcolor="rgba(110,110,110,0.15)", line_width=0)
    fig.add_annotation(x=2020.5, y=1.08, yref="paper", showarrow=False, text="Covid-19 period", font=dict(size=11, color=GREY))
    return fig


def chart_layout(fig, title: str, height: int = 340):
    fig.update_layout(
        title=dict(text=title, font=dict(size=15)),
        height=height,
        font=dict(family="Arial, sans-serif", size=13, color="#1A2332"),
        legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="center", x=0.5),
        margin=dict(t=40, l=10, r=10, b=55),
        plot_bgcolor="white",
        paper_bgcolor="white",
        hovermode="x unified",
    )
    fig.update_xaxes(showgrid=True, gridcolor=GRID_GREY)
    fig.update_yaxes(showgrid=True, gridcolor=GRID_GREY)
    return fig

