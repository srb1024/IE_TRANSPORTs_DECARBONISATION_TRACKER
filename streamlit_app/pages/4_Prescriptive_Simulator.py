"""Prescriptive Scenario Simulator page."""
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

st.subheader("County priority map", anchor=False)
with st.container(border=True):
    tiers = sorted(county["risk_tier"].unique(), key=lambda t: county.loc[county["risk_tier"] == t, "priority"].iloc[0])
    tier_filter = st.multiselect("Filter by risk tier", options=tiers, default=tiers)
    filtered = county[county["risk_tier"].isin(tier_filter)].copy()

    map_rendered = False
    try:
        geojson_data = requests.get(GEOJSON_URL, timeout=10).json()
        name_key = next(k for k in geojson_data["features"][0]["properties"] if "name" in k.lower())
        gj_lookup = {
            f["properties"][name_key].strip().lower().replace("county ", ""): f["properties"][name_key]
            for f in geojson_data["features"]
        }
        filtered["geo_name"] = filtered["county"].str.strip().str.lower().map(gj_lookup)
        matched = filtered.dropna(subset=["geo_name"])
        if len(matched) >= max(5, len(filtered) // 2):
            fig_map = px.choropleth_mapbox(
                matched,
                geojson=geojson_data,
                locations="geo_name",
                featureidkey=f"properties.{name_key}",
                color="risk_tier",
                color_discrete_map=RISK_COLORS,
                mapbox_style="carto-positron",
                zoom=5.6,
                center={"lat": 53.4, "lon": -8.0},
                opacity=0.75,
                hover_name="county",
                height=440,
            )
            fig_map.update_layout(margin=dict(l=0, r=0, t=10, b=0))
            st.plotly_chart(fig_map, use_container_width=True, config=PLOTLY_CONFIG)
            st.caption("Counties shaded by risk tier. Boundary source: click_that_hood (community GeoJSON), matched by county name.")
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
            point_data,
            lat="lat",
            lon="lon",
            color="risk_tier",
            color_discrete_map=RISK_COLORS,
            size="cars_per_1000",
            size_max=26,
            hover_name="county",
            zoom=5.6,
            height=440,
            mapbox_style="open-street-map",
        )
        fig_map.update_layout(margin=dict(l=0, r=0, t=10, b=0))
        st.plotly_chart(fig_map, use_container_width=True, config=PLOTLY_CONFIG)
        st.caption("Boundary map could not be matched, showing county centre points instead. Marker size reflects cars per 1,000 population.")

    n_critical = int((county["risk_tier"] == "Critical").sum())
    n_zero_stops = int((county["stops_per_100k"] == 0).sum())
    n_counties = county["county"].nunique()
    top_county = county.loc[county["cars_per_1000"].idxmax()]

    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(stat_card("Critical priority", f"{n_critical} counties", accent="#D55E00"), unsafe_allow_html=True)
    c2.markdown(stat_card("High priority", f"{int((county['risk_tier']=='High').sum())} county", accent="#E69F00"), unsafe_allow_html=True)
    c3.markdown(stat_card("Zero recorded stops", f"{n_zero_stops} of {n_counties}", "NaPTAN coverage gap", accent="#6E6E6E"), unsafe_allow_html=True)
    c4.markdown(stat_card("Highest car dependency", top_county["county"], f"{top_county['cars_per_1000']:.0f} per 1,000", accent="#D55E00"), unsafe_allow_html=True)