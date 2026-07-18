"""
data_loader.py — cached data-access layer for the Streamlit build.

Governance rule (unchanged from the Power BI build): only CSVs produced by
this project's own notebooks/01-04 pipeline may be loaded — nothing external,
nothing hand-edited. All paths resolve relative to the repo root so this file
works regardless of where Streamlit is launched from.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st


def _find_repo_root() -> Path:
    """Walk up from this file until we find the real repo root.

    Uses a directory-shape marker (data/processed/ + notebooks/ both present)
    rather than a single filename, since streamlit_app/ has its own
    requirements.txt now too and a filename marker would stop one level too
    early.
    """
    here = Path(__file__).resolve()
    for parent in [here] + list(here.parents):
        if (parent / "data" / "processed").is_dir() and (parent / "notebooks").is_dir():
            return parent
    raise FileNotFoundError(
        "Could not locate repo root (looked for a folder containing both "
        "data/processed/ and notebooks/)"
    )


REPO_ROOT = _find_repo_root()
PROCESSED_DIR = REPO_ROOT / "data" / "processed"
SUPPLEMENTARY_DIR = REPO_ROOT / "data" / "supplementary"

_SUPPLEMENTARY_TABLES: dict[str, str] = {
    "income_tier_by_county": "income_tier_by_county.csv",
    "private_car_stock_by_county": "private_car_stock_by_county.csv",
}

# name -> filename in data/processed/. Add new pipeline outputs here as they
# land — this is the single place the rest of the app should ever reference
# a processed CSV by name.
_TABLES: dict[str, str] = {
    "fact_transport": "fact_transport_annual.csv",
    "fuel_mix_annual": "fuel_mix_new_private_cars_annual.csv",
    "fuel_mix_monthly": "fuel_mix_new_private_cars_monthly.csv",
    "ev_forecast": "forecast_ev_adoption_logistic.csv",
    "ev_income_tier_forecast": "forecast_ev_income_tier_logistic.csv",
    "kpi_forecast_hw": "forecast_kpi_holtwinters.csv",
    "pt_forecast_sarima": "forecast_pt_journeys_sarima.csv",
    "county_risk_tiers": "county_risk_tiers.csv",
    "county_recommendations": "county_tier_recommendations.csv",
    "prescriptive_scenarios": "prescriptive_scenarios_2030.csv",
    "prescriptive_monte_carlo": "prescriptive_monte_carlo.csv",
    "prescriptive_reverse_solve": "prescriptive_reverse_solve.csv",
    "population": "dim_population_annual.csv",
    "naptan_stops": "naptan_stops_clean.csv",
    "ev_registration_gap": "forecast_ev_registration_gap.csv",
    "co2_per_capita": "forecast_co2_per_capita.csv",
}


@st.cache_data(show_spinner=False)
def load_table(name: str) -> pd.DataFrame:
    """Load one processed table by its logical name, cached across reruns."""
    if name in _TABLES:
        base_dir, filename = PROCESSED_DIR, _TABLES[name]
    elif name in _SUPPLEMENTARY_TABLES:
        base_dir, filename = SUPPLEMENTARY_DIR, _SUPPLEMENTARY_TABLES[name]
    else:
        raise KeyError(
            f"Unknown table '{name}'. Available: {sorted(list(_TABLES) + list(_SUPPLEMENTARY_TABLES))}"
        )

    path = base_dir / filename
    if not path.exists():
        raise FileNotFoundError(
            f"{path} not found. Run notebooks/01_data_preprocessing_and_cleaning.ipynb "
            "(and 03/04 for forecasts) first — this loader only reads pipeline output, "
            "per the project's data-governance rule."
        )

    df = pd.read_csv(path)
    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"])
    return df


def load_all() -> dict[str, pd.DataFrame]:
    """Eagerly load every registered table — used by the Home page health check."""
    return {name: load_table(name) for name in list(_TABLES) + list(_SUPPLEMENTARY_TABLES)}
