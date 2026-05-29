"""
Central configuration for the Transport Decarbonisation Dashboard preprocessing
pipeline.

All file paths, canonical category mappings and the analysis windows defined in
the project proposal are declared here so that the cleaning modules stay free of
magic strings and the whole pipeline can be re-pointed at a new data drop by
editing a single file.
"""
from __future__ import annotations

from pathlib import Path

# --------------------------------------------------------------------------- #
# Paths
# --------------------------------------------------------------------------- #
# RAW_DIR points at the directory holding the unmodified CSO / data.gov.ie
# extracts. By default it resolves to <repo>/data/raw. Override with the
# TDD_RAW_DIR environment variable (used here to read the read-only project
# mount) without touching code.
import os

REPO_ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = Path(os.environ.get("TDD_RAW_DIR", REPO_ROOT / "data" / "raw"))
INTERIM_DIR = REPO_ROOT / "data" / "interim"
PROCESSED_DIR = REPO_ROOT / "data" / "processed"

for _d in (INTERIM_DIR, PROCESSED_DIR):
    _d.mkdir(parents=True, exist_ok=True)

# Raw file names (the CSO timestamped extracts). Resolved by glob prefix so a
# fresh download with a new timestamp still matches.
RAW_PREFIXES = {
    "TOA11": "TOA11",   # Luas passenger numbers (monthly, by line)
    "PEA01": "PEA01",   # Annual population estimates (age x sex)
    "THA25": "THA25",   # Public transport passenger journeys (weekly, bus/rail)
    "THA18": "THA18",   # Private car vehicle population & km travelled
    "THA17": "THA17",   # All-vehicle population & km travelled (by type)
    "TEM12": "TEM12",   # New vehicles licensed by fuel type (monthly)
    "TEM22": "TEM22",   # Private cars licensed 2019-2021 (new + second-hand)
    "TEM23": "TEM23",   # All private cars licensed 2022-2026
    "NAPTAN": "NaPTAN_Stop_Points",
}

# --------------------------------------------------------------------------- #
# Analysis windows (from the project proposal, section 4.1)
# --------------------------------------------------------------------------- #
CORE_WINDOW = (2019, 2023)          # common overlap across all core datasets
FUEL_WINDOW = (2015, 2026)          # TEM12 long-term fuel series
REGISTRATION_WINDOW = (2019, 2026)  # TEM22 + TEM23 combined registrations

# --------------------------------------------------------------------------- #
# Canonical category maps
# --------------------------------------------------------------------------- #
# Population total is built from a clean, NON-OVERLAPPING partition of PEA01 age
# groups. PEA01 ships both fine (5-year) and broad bands plus overlapping
# convenience bands (e.g. "0 - 14 years", "15 years and over"); summing the raw
# table would multiply-count. We use the five-year partition as canonical.
PEA01_FIVE_YEAR_BANDS = [
    "Under 1 year", "1 - 4 years", "5 - 9 years", "10 - 14 years",
    "15 - 19 years", "20 - 24 years", "25 - 29 years", "30 - 34 years",
    "35 - 39 years", "40 - 44 years", "45 - 49 years", "50 - 54 years",
    "55 - 59 years", "60 - 64 years", "65 - 69 years", "70 - 74 years",
    "75 - 79 years", "80 - 84 years", "85 years and over",
]

# TEM12 raw fuel labels -> tidy fuel groups for the petrol->EV transition story.
FUEL_GROUP_MAP = {
    "Petrol": "Petrol",
    "Diesel": "Diesel",
    "Electric": "Battery Electric (BEV)",
    "Petrol and electric hybrid": "Hybrid (HEV)",
    "Diesel and electric hybrid": "Hybrid (HEV)",
    "Petrol or Diesel plug-in hybrid electric": "Plug-in Hybrid (PHEV)",
    "Other fuel types": "Other",
}
# Fuel groups considered "electrified" for the EV/hybrid share KPI.
ELECTRIFIED_GROUPS = {
    "Battery Electric (BEV)", "Hybrid (HEV)", "Plug-in Hybrid (PHEV)",
}
# Zero-/low-emission groups for the strict "EV share" KPI (BEV + PHEV).
PLUGIN_GROUPS = {"Battery Electric (BEV)", "Plug-in Hybrid (PHEV)"}

# Month-name lookup for parsing "YYYY MonthName" style periods.
MONTH_NAME_TO_NUM = {
    "january": 1, "february": 2, "march": 3, "april": 4, "may": 5, "june": 6,
    "july": 7, "august": 8, "september": 9, "october": 10, "november": 11,
    "december": 12,
}
