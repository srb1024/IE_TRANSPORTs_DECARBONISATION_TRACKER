"""Prescriptive Scenario Simulator page."""
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import streamlit as st

from data_loader import load_table
from nav import sticky_header
from style import DATA_LABEL_FONT, KPI_LABELS, PLOTLY_CONFIG, TARGET_LINE, apply_page_style, chart_layout, stat_card, status_badge

apply_page_style()
sticky_header("Prescriptive Simulator", "Prescriptive")

scenarios = load_table("prescriptive_scenarios")
monte_carlo = load_table("prescriptive_monte_carlo")
reverse_solve = load_table("prescriptive_reverse_solve")
county = load_table("county_recommendations")

KPI_DIRECTION = {"car_dependency_index": "down", "pt_usage_index": "up", "transport_intensity_index": "down"}
SCENARIO_ORDER = ["Business-As-Usual", "Moderate Intervention", "Accelerated Transition"]
RISK_COLORS = {"Critical": "#D55E00", "High": "#E69F00", "Medium": "#F0E442", "Low": "#009E73"}
GEOJSON_URL = "https://raw.githubusercontent.com/codeforgermany/click_that_hood/main/public/data/ireland-counties.geojson"


def status(gap, target, direction):
    on_track = gap >= 0 if direction == "down" else gap <= 0
    if on_track:
        return "On Track"
    return "At Risk" if abs(gap) / target * 100 < 20 else "Off Track"


st.subheader("Scenario comparison", anchor=False)
cols = st.columns(3)
for col, (kpi_key, kpi_label) in zip(cols, KPI_LABELS.items()):
    with col:
        with st.container(border=True):
            direction = KPI_DIRECTION[kpi_key]
            scen = scenarios[scenarios["kpi"] == kpi_key].set_index("scenario").loc[SCENARIO_ORDER]
            mc = monte_carlo[monte_carlo["kpi"] == kpi_key].set_index("scenario").loc[SCENARIO_ORDER]
            target = scen["gov_target_2030"].iloc[0]

            fig = go.Figure(
                go.Bar(
                    x=SCENARIO_ORDER,
                    y=mc["mean_2030"],
                    error_y=dict(
                        type="data",
                        symmetric=False,
                        array=mc["p95_2030"] - mc["mean_2030"],
                        arrayminus=mc["mean_2030"] - mc["p5_2030"],
                    ),
                    marker_color=["#D55E00", "#E69F00", "#009E73"],
                    text=[f"{v:,.0f}" for v in mc["mean_2030"]],
                    textposition="outside",
                    textfont=DATA_LABEL_FONT,
                )
            )
            fig.add_trace(
                go.Scatter(
                    x=SCENARIO_ORDER,
                    y=[target] * 3,
                    mode="lines",
                    name="Target",
                    line=dict(color=TARGET_LINE["color"], dash=TARGET_LINE["dash"], width=TARGET_LINE["width"]),
                )
            )
            fig = chart_layout(fig, title=kpi_label, height=340)
            fig.update_layout(showlegend=False, yaxis_title=None)
            y_max = max(mc["p95_2030"].max(), target) * (1.6 if kpi_key == "car_dependency_index" else 1.35)
            fig.update_yaxes(range=[0, y_max])
            st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG, key=f"scenario_{kpi_key}")

            gap = scen.loc["Accelerated Transition", "gap_to_target"]
            st.markdown(status_badge(status(gap, target, direction)), unsafe_allow_html=True)
            st.caption("Best case scenario status shown.")

st.subheader("Policy Scenario Simulator", anchor=False)
st.caption(
    "Select a single scenario to see its projected outcome and target status. "
    "The 'required rate to close this gap' figure is calculated relative to "
    "BAU specifically (holding the other lever fixed at its BAU value), not "
    "recalculated separately per scenario, your underlying model doesn't "
    "produce a per-scenario version of that number, so it's shown as a "
    "constant reference point across all three scenarios."
)

selected_scenario = st.radio(
    "Choose a scenario", SCENARIO_ORDER, horizontal=True, key="sim_scenario_select"
)

with st.container(border=True):
    for kpi_key, kpi_label in KPI_LABELS.items():
        direction = KPI_DIRECTION[kpi_key]
        row = scenarios[
            (scenarios["kpi"] == kpi_key) & (scenarios["scenario"] == selected_scenario)
        ].iloc[0]
        target = row["gov_target_2030"]
        projected = row["projected_2030"]
        gap = row["gap_to_target"]
        kpi_status = status(gap, target, direction)

        metric_col, text_col = st.columns([1, 3])
        with metric_col:
            st.metric(kpi_label, f"{projected:,.1f}", help=f"CAP 2030 target: {target:,.0f}")
            st.markdown(status_badge(kpi_status), unsafe_allow_html=True)

        with text_col:
            if kpi_status == "On Track":
                message = (
                    f"Under **{selected_scenario}**, {kpi_label} is projected to meet its "
                    f"2030 target of {target:,.0f}."
                )
            else:
                pct_short = abs(gap) / target * 100
                direction_word = "above" if direction == "down" else "below"
                message = (
                    f"Under **{selected_scenario}**, {kpi_label} is projected to reach "
                    f"{projected:,.1f} by 2030, {pct_short:.1f}% {direction_word} its target "
                    f"of {target:,.0f} ({kpi_status})."
                )

                rs_row = reverse_solve[reverse_solve["kpi_label"] == kpi_label]
                if not rs_row.empty:
                    r = rs_row.iloc[0]
                    bau_pt, bau_ev = r["bau_pt_growth_rate"], r["bau_ev_adoption_rate"]
                    req_pt, req_ev = r["required_pt_growth_rate_if_ev_fixed"], r["required_ev_adoption_rate_if_pt_fixed"]

                    levers = []
                    if pd.notna(req_ev) and req_ev >= 0:
                        levers.append(f"EV adoption at **{req_ev*100:.1f}%/yr** (BAU: {bau_ev*100:.1f}%/yr)")
                    if pd.notna(req_pt) and req_pt >= 0:
                        levers.append(f"PT growth at **{req_pt*100:.1f}%/yr** (BAU: {bau_pt*100:.1f}%/yr)")

                    if levers:
                        message += " Fully closing this gap from BAU would require " + " or ".join(levers) + "."
                    else:
                        message += (
                            " Neither lever alone, holding the other fixed at BAU, can close "
                            "this gap per the reverse-solve model, see Policy Lever Sensitivity below."
                        )
            st.write(message)
        st.write("")

st.subheader("Policy lever sensitivity", anchor=False)
with st.container(border=True):
    bau_pt = reverse_solve["bau_pt_growth_rate"].iloc[0]
    bau_ev = reverse_solve["bau_ev_adoption_rate"].iloc[0]
    c1, c2 = st.columns(2)
    c1.metric("BAU PT growth rate", f"{bau_pt*100:.1f}%/yr")
    c2.metric("BAU EV adoption rate", f"{bau_ev*100:.1f}%/yr")

    display_cols = {
        "kpi_label": "KPI",
        "required_pt_growth_rate_if_ev_fixed": "Required PT growth (EV fixed)",
        "pt_multiplier_vs_bau": "PT multiplier",
        "required_ev_adoption_rate_if_pt_fixed": "Required EV adoption (PT fixed)",
        "ev_multiplier_vs_bau": "EV multiplier",
    }
    st.dataframe(reverse_solve[list(display_cols)].rename(columns=display_cols), use_container_width=True, hide_index=True)
    st.caption("CDI shows a negative required EV rate since EV adoption changes fuel type rather than car ownership so it cannot move CDI alone. A few other values look counterintuitive and are worth checking against notebook 04 before quoting.")

st.subheader("EV adoption by income tier", anchor=False)
st.caption(
    "Solid line: fitted S-curve over the actual 2018-2023 training data. "
    "Dashed line: forecast to 2030. Fleet-stock basis (Other fuel types = "
    "BEV+PHEV+HEV combined), a different basis to the national "
    "registrations-flow EV share on the Fuel Transition page, the two are "
    "not directly comparable."
)

tier_forecast = load_table("ev_income_tier_forecast")
TIER_COLORS = {"High": "#0072B2", "Medium": "#E69F00", "Low": "#D55E00"}
TIER_ORDER = ["High", "Medium", "Low"]

with st.container(border=True):
    card_col, chart_col = st.columns([1, 2])

    with card_col:
        for tier in TIER_ORDER:
            val_2030 = tier_forecast.loc[
                (tier_forecast["income_tier"] == tier) & (tier_forecast["Year"] == 2030),
                "other_fuel_share_forecast_pct"
            ].iloc[0]
            st.markdown(
                stat_card(f"{tier} income, 2030", f"{val_2030:.1f}%", accent=TIER_COLORS[tier]),
                unsafe_allow_html=True,
            )

        high_2030 = tier_forecast.loc[
            (tier_forecast["income_tier"] == "High") & (tier_forecast["Year"] == 2030),
            "other_fuel_share_forecast_pct"
        ].iloc[0]
        low_2030 = tier_forecast.loc[
            (tier_forecast["income_tier"] == "Low") & (tier_forecast["Year"] == 2030),
            "other_fuel_share_forecast_pct"
        ].iloc[0]
        st.markdown(
            stat_card("Equity gap (High minus Low), 2030", f"{high_2030 - low_2030:.1f}pp", accent="#CC79A7"),
            unsafe_allow_html=True,
        )

    with chart_col:
        fig6 = go.Figure()
        for tier in TIER_ORDER:
            tier_data = tier_forecast[tier_forecast["income_tier"] == tier].sort_values("Year")
            solid = tier_data[tier_data["Year"] <= 2023]
            dashed = tier_data[tier_data["Year"] >= 2023]

            fig6.add_trace(
                go.Scatter(
                    x=solid["Year"], y=solid["other_fuel_share_forecast_pct"],
                    mode="lines+markers", name=f"{tier} income",
                    line=dict(color=TIER_COLORS[tier], width=3, dash="solid"),
                    legendgroup=tier,
                )
            )
            fig6.add_trace(
                go.Scatter(
                    x=dashed["Year"], y=dashed["other_fuel_share_forecast_pct"],
                    mode="lines+markers", name=f"{tier} income (forecast)",
                    line=dict(color=TIER_COLORS[tier], width=3, dash="dot"),
                    legendgroup=tier, showlegend=False,
                )
            )
        fig6 = chart_layout(fig6, title="Non-traditional fleet share by income tier: fitted + forecast", height=340)
        fig6.update_layout(xaxis=dict(dtick=1, title="Year"), yaxis_title="Share (%)")
        st.plotly_chart(fig6, use_container_width=True, config=PLOTLY_CONFIG)

    st.caption(
        f"The gap persists even at each tier's long-run ceiling, not just in "
        f"early timing: High-income counties are projected to reach a higher "
        f"saturation point than Low-income counties, {high_2030 - low_2030:.1f} "
        f"percentage points apart by 2030."
    )

st.subheader("County priority map", anchor=False)
with st.container(border=True):
    tiers = sorted(county["risk_tier"].unique(), key=lambda t: county.loc[county["risk_tier"] == t, "priority"].iloc[0])
    tier_filter = st.multiselect("Filter by risk tier", options=tiers, default=tiers)
    filtered = county[county["risk_tier"].isin(tier_filter)].copy()

    card_col, chart_col = st.columns([1, 2])

    with card_col, st.container(height=560):
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
                    featureidkey=f"properties.{name_key}", color="risk_tier",
                    color_discrete_map=RISK_COLORS, mapbox_style="carto-positron",
                    zoom=5.6, center={"lat": 53.4, "lon": -8.0}, opacity=0.75,
                    hover_name="county", height=440,
                )

                fig_map.update_layout(
                    height=560,
                    margin=dict(l=0, r=0, t=10, b=20),
                    legend=dict(
                        orientation="h", yanchor="top", y=-0.06, xanchor="center", x=0.5,
                        title_text="Risk Tier", title_font=dict(size=15), font=dict(size=15),
                    ),
                )
                st.plotly_chart(fig_map, use_container_width=True, config=PLOTLY_CONFIG)
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
                point_data, lat="lat", lon="lon", color="risk_tier", color_discrete_map=RISK_COLORS,
                size="cars_per_1000", size_max=32, hover_name="county", zoom=5.7, height=440,
                mapbox_style="carto-positron", center={"lat": 53.4, "lon": -8.0},
            )
            fig_map.update_traces(marker=dict(opacity=0.85, sizemin=10))
            fig_map.update_layout(
                height=480,
                margin=dict(l=0, r=0, t=10, b=20),
                legend=dict(
                    orientation="h", yanchor="top", y=-0.06, xanchor="center", x=0.5,
                    title_text="Risk Tier", title_font=dict(size=15), font=dict(size=15),
                ),
            )
            st.plotly_chart(fig_map, use_container_width=True, config=PLOTLY_CONFIG)