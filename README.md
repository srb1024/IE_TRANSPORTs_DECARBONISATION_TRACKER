# Data Preprocessing & Cleaning — National Transport Decarbonisation Dashboard (Ireland)

This stage turns the raw CSO / data.gov.ie extracts into a **governed,
analysis-ready** dataset for the dashboard. All the work lives in one
self-contained, executed notebook:

```
notebooks/01_data_preprocessing_and_cleaning.ipynb
```

It follows **profile → clean → validate** for each source, then integrates them
into an annual fact table with the three composite KPIs and writes everything to
`data/processed/`.

## How to run

1. Put the raw CSO CSVs in `data/raw/` (or set the `TDD_RAW_DIR` env var to point
   elsewhere). Files are matched by prefix, so timestamped names work as-is.
2. Open the notebook and **Kernel → Restart & Run All**.

Requirements: `pandas>=2.0`, `numpy>=1.24` (see `requirements.txt`).

## Outputs (`data/processed/`)

| File | Grain | Purpose |
|---|---|---|
| `fact_transport_annual.csv` | year | **Headline fact table** — population, car stock, PT journeys, vehicle-km, the 3 KPIs + YoY. Bind the dashboard to this. |
| `dim_population_annual.csv` | year | National population (PEA01). |
| `luas_journeys_annual.csv` | year | Luas journeys (TOA11). |
| `public_transport_annual.csv` | year | Bus & rail from weekly THA25 + coverage flags. |
| `private_car_stock_annual.csv` | year | Private-car population + car-km (THA18). |
| `vehicle_km_annual.csv` | year | Total vehicle-km + fleet (THA17). |
| `fuel_mix_new_private_cars_{monthly,annual}.csv` | month/year | Petrol→EV transition (TEM12) + BEV/PHEV & electrified shares. |
| `private_car_registrations_{monthly,annual}.csv` | month/year | Continuous licensing series 2019–2026 (TEM22 ⊕ TEM23). |
| `naptan_stops_clean.csv` | stop | Cleaned bus/rail stop layer for the optional map. |

`docs/` holds the auto-generated `DATA_QUALITY_REPORT.md` (rewritten on every run)
and `DATA_DICTIONARY.md`.

## KPIs (proposal §4.3)

| KPI | Definition | Sources |
|---|---|---|
| Car Dependency Index | private cars per 1,000 population | THA18 ÷ PEA01 |
| Public Transport Usage Index | (bus+rail+Luas) journeys per capita | THA25 + TOA11 ÷ PEA01 |
| Transport Intensity Indicator | total vehicle-km per capita | THA17 ÷ PEA01 |

## Cleaning decisions worth knowing

- **No double-counting.** PEA01 ships overlapping age bands and TEM23 ships both
  detail rows *and* `All …` subtotals — the notebook selects clean
  partitions/aggregates explicitly rather than blind-summing.
- **TEM22 → TEM23 bridge** is made continuous but transparent via
  `source_table` / `definition` columns (boundary at 2022).
- **Honest gaps.** 2019 rail is missing from THA25 → 2019 PT flagged bus-only;
  partial 2026 flagged so totals aren't compared year-on-year.
- THA17/THA18 are CSO *vehicle population & kilometres* tables (not roadside
  counts); intensity uses the `Kilometres Travelled` measure (millions of km).
