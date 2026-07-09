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
    the viewport on scroll. The navy banner is full-bleed (edge to edge),
    the nav row underneath it is inset with the same 2rem side padding as
    the page's own .block-container, so its left/right edges line up
    exactly with the content below.
    """
    st.markdown(
        """
        <style>
        div.st-key-sticky_header {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            width: 100%;
            z-index: 999;
            background-color: #FFFFFF;
            box-sizing: border-box;
            padding: 0;
        }
        div.st-key-nav_row {
            padding: 0 2rem;
            box-sizing: border-box;
        }
        button[kind="secondary"],
        div.nav-active {
            min-height: 3rem;
            padding: 0.55rem 0;
            border-radius: 8px;
            box-sizing: border-box;
            text-transform: uppercase !important;
            letter-spacing: 0.03em !important;
            font-size: 1.3rem !important;
            font-weight: 700 !important;
            line-height: 1 !important;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        button[kind="secondary"] {
            font-size: 1.3rem !important;
        }
        button[kind="secondary"] p,
        button[kind="secondary"] span {
            font-size: 1.3rem !important;
            font-weight: 700 !important;
            text-transform: uppercase !important;
            letter-spacing: 0.03em !important;
            line-height: 1 !important;
            margin: 0 !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    with st.container(key="sticky_header"):
        st.markdown(
            "<div style='background-color:#1A2332; padding:1.1rem 2rem; "
            "text-align:center; margin-bottom:0.8rem;'>"
            "<h1 style='color:white; font-size:2.2rem; margin:0; letter-spacing:0.02em;'>"
            "IRISH TRANSPORT DECARBONISATION TRACKER</h1></div>",
            unsafe_allow_html=True,
        )
        with st.container(key="nav_row"):
            cols = st.columns(len(PAGES))
            for col, (path, label) in zip(cols, PAGES):
                with col:
                    if label == current:
                        st.markdown(
                            f'<div class="nav-active" style="background:#1A2332; color:white; '
                            f'text-align:center; border:1px solid transparent;">'
                            f'{label}</div>',
                            unsafe_allow_html=True,
                        )
                    else:
                        if st.button(label, key=f"nav_{label}", use_container_width=True):
                            st.switch_page(path)
    st.divider()