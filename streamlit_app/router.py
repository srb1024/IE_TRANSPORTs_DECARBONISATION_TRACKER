"""Entry point and page router for the Irish Transport Decarbonisation Tracker."""
import streamlit as st

st.set_page_config(page_title="Irish Transport Decarbonisation Tracker", page_icon="🚆", layout="wide")

pages = [
    st.Page("pages/0_Home.py", title="Home", url_path="dashboard-home", default=True),
    st.Page("pages/1_Overview.py", title="Overview"),
    st.Page("pages/2_Fuel_Transition.py", title="Fuel Transition"),
    st.Page("pages/3_Predictive_Analytics.py", title="Predictive"),
    st.Page("pages/4_Prescriptive_Simulator.py", title="Prescriptive"),
]
pg = st.navigation(pages, position="hidden")
pg.run()