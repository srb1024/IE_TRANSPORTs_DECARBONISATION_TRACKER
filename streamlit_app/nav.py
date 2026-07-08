"""Shared sticky header: page heading + navigation bar, pinned on scroll."""
import streamlit as st

PAGES = [
    ("pages/0_Home.py", "Home"),
    ("pages/1_Overview.py", "Overview"),
    ("pages/2_Fuel_Transition.py", "Fuel Transition"),
    ("pages/3_Predictive_Analytics.py", "Predictive"),
    ("pages/4_Prescriptive_Simulator.py", "Prescriptive"),
]


def sticky_header(page_title: str, current: str) -> None:
    """Render the page heading and nav bar together, pinned to the top of
    the viewport on scroll. st.container(key=...) puts its CSS class on an
    inner wrapper rather than the outer scrolling div, so this targets the
    outer div via :has() instead of the marked element directly. This is a
    community CSS workaround, not an official Streamlit API, so it can
    behave slightly differently across Streamlit versions.
    """
    st.markdown(
        """
        <style>
        div:has(> div.st-key-sticky_header),
        div:has(> div > div.st-key-sticky_header) {
            position: sticky;
            top: 0;
            z-index: 999;
            background-color: #FFFFFF;
            padding-top: 0.4rem;
            padding-bottom: 0.4rem;
            border-bottom: 1px solid #E3E6EA;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    with st.container(key="sticky_header"):
        st.markdown(
            f"<h1 style='text-align:center; font-size:1.75rem; margin-top:0; margin-bottom:0.6rem;'>"
            f"IRISH TRANSPORT DECARBONISATION TRACKER - {page_title.upper()}</h1>",
            unsafe_allow_html=True,
        )
        cols = st.columns(len(PAGES))
        for col, (path, label) in zip(cols, PAGES):
            with col:
                if label == current:
                    st.markdown(
                        f'<div style="background:#1A2332; color:white; text-align:center; '
                        f'padding:10px 0; border-radius:8px; font-weight:700; font-size:1.02rem;">'
                        f'{label}</div>',
                        unsafe_allow_html=True,
                    )
                else:
                    if st.button(label, key=f"nav_{label}", use_container_width=True):
                        st.switch_page(path)
    st.divider()