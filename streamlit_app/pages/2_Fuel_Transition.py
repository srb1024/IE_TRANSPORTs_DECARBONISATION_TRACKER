"""Fuel Transition page."""
import plotly.graph_objects as go
import streamlit as st

from data_loader import load_table
from nav import sticky_header
from style import ACTUAL_LINE, BLUISH_GREEN, DATA_LABEL_FONT, FORECAST_LINE, FUEL_COLORS, ORANGE, PLOTLY_CONFIG, TARGET_LINE, apply_page_style, chart_layout, stat_card

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

with st.container(border=True):
    c1, c2, c3 = st.columns(3)
    c1.metric(f"New registrations ({latest_year})", f"{total_latest:,}")
    c2.metric(f"EV and PHEV share ({latest_year})", f"{latest_ev_share:.1f}%")
    c3.metric("Gap to CAP 2030 target", f"{gap_2030:.1f}pp")

col1, col2 = st.columns(2)

with col1:
    with st.container(border=True):
        fuel_order = ["Petrol", "Diesel", "Hybrid (HEV)", "Plug-in Hybrid (PHEV)", "Battery Electric (BEV)", "Other"]
        fig1 = go.Figure()
        for fuel in fuel_order:
            fig1.add_trace(
                go.Bar(x=fuel_complete["Year"], y=fuel_complete[fuel], name=fuel, marker_color=FUEL_COLORS[fuel])
            )
        fig1.update_layout(barmode="stack")
        fig1 = chart_layout(fig1, title="Registrations by fuel type", height=420)
        fig1.update_layout(
            legend=dict(orientation="h", yanchor="top", y=-0.28, xanchor="center", x=0.5),
            margin=dict(t=45, l=10, r=10, b=110),
            xaxis=dict(dtick=2, title="Year"),
            yaxis_title="Registrations",
        )
        st.plotly_chart(fig1, use_container_width=True, config=PLOTLY_CONFIG)
        st.caption(f"Complete years only, 2015 to {latest_year}.")

with col2:
    with st.container(border=True):
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
        fig2 = chart_layout(fig2, title="EV and PHEV adoption vs target", height=420)
        fig2.update_layout(xaxis=dict(dtick=2, title="Year"), yaxis_title="Share of registrations (%)")
        st.plotly_chart(fig2, use_container_width=True, config=PLOTLY_CONFIG)
        st.caption(f"Forecast plateaus at {forecast_2030:.1f}% by 2030.")
        
        st.subheader("Registrations needed to close the gap", anchor=False)
st.caption(
    "Converts the EV/PHEV share gap into an absolute registration count: how "
    "many additional cars per year, not just what percentage share, is "
    "needed to stay on the CAP 2030 glide path. Uses a 3-year average "
    "registration volume assumption and a straight-line glide path to "
    "target, both flagged as planning assumptions, not model outputs."
)

reg_gap = load_table("ev_registration_gap").sort_values("Year")
gap_2030_row = reg_gap.loc[reg_gap["Year"] == reg_gap["Year"].max()]
additional_2030 = int(gap_2030_row["additional_registrations_needed"].iloc[0])
total_additional = int(reg_gap["additional_registrations_needed"].sum())
assumed_volume = int(reg_gap["assumed_annual_total_registrations"].iloc[0])

card_col, chart_col = st.columns([1, 2])
with card_col:
    st.markdown(
        stat_card(
            f"Additional registrations needed ({int(reg_gap['Year'].max())})",
            f"{additional_2030:,}",
            f"{total_additional:,} cumulative, {int(reg_gap['Year'].min())} to {int(reg_gap['Year'].max())}",
            accent=ORANGE,
        ),
        unsafe_allow_html=True,
    )
    st.caption(f"Assumes ~{assumed_volume:,} total new registrations/year.")

with chart_col:
    with st.container(border=True):
        fig4 = go.Figure()
        fig4.add_trace(go.Bar(x=reg_gap["Year"], y=reg_gap["bau_registrations"], name="BAU trajectory", marker_color=ORANGE))
        fig4.add_trace(go.Bar(x=reg_gap["Year"], y=reg_gap["required_registrations"], name="Required for CAP target", marker_color=BLUISH_GREEN))
        fig4.update_layout(barmode="group")
        fig4 = chart_layout(fig4, title="EV and hybrid registrations: BAU vs. required", height=340)
        fig4.update_layout(xaxis=dict(dtick=1, title="Year"), yaxis_title="New registrations")
        st.plotly_chart(fig4, use_container_width=True, config=PLOTLY_CONFIG)

st.caption(
    f"By {int(reg_gap['Year'].max())}, BAU reaches roughly "
    f"{int(gap_2030_row['bau_registrations'].iloc[0]):,} EV/hybrid registrations against a required "
    f"{int(gap_2030_row['required_registrations'].iloc[0]):,}, a gap of {additional_2030:,} "
    f"registrations that year alone."
)