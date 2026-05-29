# Data Dictionary — `fact_transport_annual.csv`

_Generated 2026-05-29 11:49 UTC. Core analysis window 2019–2023._

| Column | Type | Notes |
|---|---|---|
| `Year` | int64 | Calendar year (key). |
| `population` | int64 | Total persons (PEA01 five-year band partition x both sexes, x1000). |
| `luas_journeys` | int64 | Annual Luas journeys, Red+Green (TOA11). |
| `luas_complete` | bool | True if all 12 months present. |
| `bus_journeys` | float64 | Annual bus journeys from weekly THA25 (Dublin Metro Bus + Bus excl. Dublin Metro). |
| `rail_journeys` | float64 | Annual rail journeys (THA25). NaN/0 where not yet reported (2019). |
| `pt_weeks_present` | float64 | Distinct ISO weeks present in THA25 for the year. |
| `rail_complete` | object | False where rail data is missing for the year (e.g. 2019). |
| `private_cars` | float64 | Private-car vehicle population (THA18, summed across breakdowns). |
| `private_car_km_million` | float64 | Private-car kilometres travelled, millions (THA18). |
| `total_vehicle_km_million` | float64 | All-vehicle kilometres travelled, millions (THA17). |
| `total_vehicles` | float64 | Total licensed vehicle population (THA17). |
| `pt_total_journeys` | float64 | bus + rail + Luas journeys (NaN-aware sum). |
| `pt_total_complete` | object | True only if both rail and Luas are complete for the year. |
| `car_dependency_index` | float64 | KPI: private cars per 1,000 population. |
| `pt_usage_index` | float64 | KPI: total PT journeys per capita. |
| `transport_intensity_index` | float64 | KPI: total vehicle-km per capita. |
| `car_dependency_index_yoy_pct` | float64 | Year-on-year % change. |
| `pt_usage_index_yoy_pct` | float64 | Year-on-year % change. |
| `transport_intensity_index_yoy_pct` | float64 | Year-on-year % change. |
| `in_core_window` | bool | True for 2019-2023 (proposal core analysis window). |
| `period_phase` | str | Pre-pandemic / Covid-19 structural break / Post-pandemic recovery. |

## KPI definitions
- **car_dependency_index** = private cars ÷ population × 1,000 (THA18 ÷ PEA01)
- **pt_usage_index** = (bus + rail + Luas journeys) ÷ population (THA25 + TOA11 ÷ PEA01)
- **transport_intensity_index** = total vehicle-km × 1e6 ÷ population (THA17 ÷ PEA01)

## Companion processed files
- `dim_population_annual.csv`, `luas_journeys_annual.csv`, `public_transport_annual.csv`,
  `private_car_stock_annual.csv`, `vehicle_km_annual.csv` — per-source annual series.
- `fuel_mix_new_private_cars_{monthly,annual}.csv` — petrol→EV transition (TEM12) with BEV/PHEV & electrified shares.
- `private_car_registrations_{monthly,annual}.csv` — continuous licensing series 2019–2026 (TEM22 ⊕ TEM23).
- `naptan_stops_clean.csv` — cleaned bus/rail stop layer for the optional map.
