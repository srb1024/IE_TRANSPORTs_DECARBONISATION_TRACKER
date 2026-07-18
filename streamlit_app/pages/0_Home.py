"""Home page content."""
import pandas as pd
import streamlit as st

from data_loader import PROCESSED_DIR, SUPPLEMENTARY_DIR, load_all
from nav import sticky_header
from style import apply_page_style

apply_page_style()
sticky_header("Home", "Home")

st.markdown(
    "<style>[data-testid='stElementToolbar'] { display: none; }</style>",
    unsafe_allow_html=True,
)

# Landing cards: one per dashboard page so users know where to go
st.divider()
with st.container(border=True):
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.subheader("Overview", anchor=False)
        st.caption("KPIs indexed to 2019.")
    with col2:
        st.subheader("Fuel Transition", anchor=False)
        st.caption("Fleet fuel mix and EV adoption.")
    with col3:
        st.subheader("Predictive", anchor=False)
        st.caption("Holt-Winters and SARIMA forecasts.")
    with col4:
        st.subheader("Prescriptive", anchor=False)
        st.caption("Scenarios, sensitivity and county priority.")

# Health check so a broken data path shows up here rather than mid-chart
with st.expander("Data connection diagnostics", expanded=True):

    # Bail out early with the actual error if any CSV is missing
    try:
        tables = load_all()
    except FileNotFoundError as e:
        st.write(str(e))
        st.stop()

    # One row per table showing its size plus the years it covers
    rows = []
    for name, df in tables.items():
        year_col = "Year" if "Year" in df.columns else ("Date" if "Date" in df.columns else None)
        span = f"{df[year_col].min()} to {df[year_col].max()}" if year_col is not None else "n/a"
        rows.append({"table": name, "rows": len(df), "columns": len(df.columns), "span": span})
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    st.caption(f"{len(tables)} tables loaded successfully.")