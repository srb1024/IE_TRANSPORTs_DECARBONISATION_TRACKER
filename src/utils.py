"""
Shared utilities for the preprocessing pipeline.

Responsibilities:
  * Locate and load raw CSO extracts robustly (BOM, quoting, timestamped names).
  * Coerce the CSO ``VALUE`` column to numeric, recording how blanks/suppressed
    cells were treated.
  * Parse the several different CSO period formats into a single tidy
    (year, month) representation.
  * Lightweight data-quality auditing so every cleaning step leaves a trace.
"""
from __future__ import annotations

import glob
import re
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd

from . import config


# --------------------------------------------------------------------------- #
# Loading
# --------------------------------------------------------------------------- #
def raw_path(key: str) -> Path:
    """Resolve a raw file by its prefix, tolerating CSO timestamp suffixes."""
    prefix = config.RAW_PREFIXES[key]
    matches = sorted(glob.glob(str(config.RAW_DIR / f"{prefix}*.csv")))
    if not matches:
        raise FileNotFoundError(
            f"No raw file matching '{prefix}*.csv' in {config.RAW_DIR}"
        )
    # If multiple drops are present, take the most recent (lexicographically
    # last, since names embed an ISO-ish timestamp).
    return Path(matches[-1])


def load_raw(key: str) -> pd.DataFrame:
    """Load a raw CSO CSV. Reads everything as string first so we can audit the
    VALUE column before coercion. Handles the UTF-8 BOM and quoted variants."""
    df = pd.read_csv(raw_path(key), dtype=str, keep_default_na=False)
    # Strip BOM / whitespace from headers (TEM12/TEM23 ship a BOM, some files
    # quote every field).
    df.columns = [c.replace("\ufeff", "").strip().strip('"') for c in df.columns]
    # Trim stray whitespace in object cells.
    for c in df.columns:
        df[c] = df[c].str.strip()
    return df


# --------------------------------------------------------------------------- #
# VALUE coercion
# --------------------------------------------------------------------------- #
# CSO PxStat uses blank cells and a handful of symbolic markers for values that
# are zero, not applicable, or statistically suppressed. We treat them per the
# semantics of each table (counts vs. measured quantities) — see clean modules.
_SUPPRESSED_MARKERS = {"", "-", "..", ":", "n/a", "na", "c", "*", "x"}


def coerce_value(series: pd.Series) -> pd.Series:
    """Convert a raw VALUE string column to float, mapping suppressed/blank
    markers to NaN and stripping thousands separators."""
    s = series.astype(str).str.strip()
    s = s.str.replace(",", "", regex=False)
    s = s.where(~s.str.lower().isin(_SUPPRESSED_MARKERS), other=np.nan)
    return pd.to_numeric(s, errors="coerce")


def blank_mask(series: pd.Series) -> pd.Series:
    """Boolean mask of cells that are blank / suppressed in the raw data."""
    s = series.astype(str).str.strip().str.lower()
    return s.isin(_SUPPRESSED_MARKERS)


# --------------------------------------------------------------------------- #
# Period parsing
# --------------------------------------------------------------------------- #
def parse_month(period: str) -> tuple[int, int]:
    """Parse the assorted CSO monthly period formats into (year, month).

    Handles:
        '2019M01'        -> (2019, 1)     # TEM22
        '2022 January'   -> (2022, 1)     # TEM23 / TEM12
        '2015 April'     -> (2015, 4)     # TEM12
    """
    p = str(period).strip()
    m = re.fullmatch(r"(\d{4})M(\d{1,2})", p, flags=re.IGNORECASE)
    if m:
        return int(m.group(1)), int(m.group(2))
    m = re.fullmatch(r"(\d{4})\s+([A-Za-z]+)", p)
    if m:
        return int(m.group(1)), config.MONTH_NAME_TO_NUM[m.group(2).lower()]
    raise ValueError(f"Unrecognised month period: {period!r}")


def parse_week(period: str) -> tuple[int, int]:
    """Parse THA25 ISO-week periods: '2019 Week 01' -> (2019, 1)."""
    m = re.fullmatch(r"(\d{4})\s+Week\s+(\d{1,2})", str(period).strip(),
                     flags=re.IGNORECASE)
    if not m:
        raise ValueError(f"Unrecognised week period: {period!r}")
    return int(m.group(1)), int(m.group(2))


def add_month_columns(df: pd.DataFrame, period_col: str) -> pd.DataFrame:
    """Append Year, MonthNum and a first-of-month Date column from a period."""
    ym = df[period_col].map(parse_month)
    df = df.copy()
    df["Year"] = [y for y, _ in ym]
    df["MonthNum"] = [m for _, m in ym]
    df["Date"] = pd.to_datetime(
        dict(year=df["Year"], month=df["MonthNum"], day=1)
    )
    return df


# --------------------------------------------------------------------------- #
# Data-quality auditing
# --------------------------------------------------------------------------- #
@dataclass
class Audit:
    """Accumulates per-dataset data-quality notes for the governance report."""
    lines: list[str] = field(default_factory=list)

    def log(self, dataset: str, message: str) -> None:
        self.lines.append(f"- **{dataset}** — {message}")

    def to_markdown(self) -> str:
        return "\n".join(self.lines)


AUDIT = Audit()


def assert_complete_year_partition(df: pd.DataFrame, year_col: str,
                                   expected: range, name: str) -> None:
    """Sanity-check that the expected years are present after aggregation."""
    have = set(df[year_col].unique())
    missing = set(expected) - have
    if missing:
        AUDIT.log(name, f"missing expected years after aggregation: "
                         f"{sorted(missing)}")
