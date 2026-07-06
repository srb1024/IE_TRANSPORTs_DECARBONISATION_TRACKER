"""Shared navigation bar and page heading."""
import streamlit as st

PAGES = [
    ("Home.py", "Home"),
    ("pages/1_Overview.py", "Overview"),
    ("pages/2_Fuel_Transition.py", "Fuel Transition"),
    ("pages/3_Predictive_Analytics.py", "Predictive"),
    ("pages/4_Prescriptive_Simulator.py", "Prescriptive"),
]


def hide_sidebar():
    st.markdown(
        """
        <style>
        section[data-testid="stSidebar"] {display: none !important;}
        div[data-testid="stSidebarCollapsedControl"] {display: none !important;}
        button[data-testid="stSidebarCollapsedControl"] {display: none !important;}
        [data-testid="collapsedControl"] {display: none !important;}
        </style>
        """,
        unsafe_allow_html=True,
    )


def page_heading(page_title: str):
    st.markdown(
        f"<h1 style='text-align:center; font-size:1.5rem; margin-top:0;'>"
        f"IRISH TRANSPORT DECARBONISATION TRACKER - {page_title.upper()}</h1>",
        unsafe_allow_html=True,
    )


def nav_bar(current: str):
    cols = st.columns(len(PAGES))
    for col, (path, label) in zip(cols, PAGES):
        with col:
            if st.button(label, key=f"nav_{label}", use_container_width=True, disabled=(label == current)):
                st.switch_page(path)
    st.divider()