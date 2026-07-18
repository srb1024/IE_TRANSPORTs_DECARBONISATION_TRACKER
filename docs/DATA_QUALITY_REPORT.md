# Data Quality & Governance Report

_Generated 2026-07-08 23:38 UTC._

## Audit log

- **PEA01** — population from 19 five-year bands x 2 sexes; years 2018-2025.
- **THA25** — Rail entirely absent for [2019] -> bus-only, flagged.
- **THA25** — 61 blank weekly cells handled; annual bus/rail for 2019-2025.
- **THA18** — private-car population summed across engine x fuel x county; car-km kept separately.
- **THA18** — private-car stock additionally split into Traditional (Petrol+Diesel) vs Non-Traditional (Other fuel types = BEV+PHEV+HEV combined) - a coarse 2-way split; CSO's own THA18 table does not break electrified vehicles down further at the stock level.
- **THA17** — total vehicle-km & fleet summed across fuel x type x county; km in millions.
- **TEM12** — year 2026 partial (4/12 months) — shares valid, totals not YoY-comparable.
- **TEM12** — fuel mix of New Private Cars mapped to tidy groups; BEV/PHEV & electrified shares computed.
- **TEM22/TEM23** — concatenated to one 2019-2026 series; boundary at 2022; TEM23 aggregate rows used to avoid double-counting.
- **NaPTAN** — 17621 raw -> 17531 active stops (27 dup AtcoCodes, 0 out-of-bounds removed).
- **THA18** — estimated tailpipe/well-to-wheel CO2 by fleet category using sourced SEAI emission factors and Brady & O'Mahony (2011)'s Irish EV energy-requirement estimate - a simplified proxy model, not a COPERT-equivalent inventory.
- **FACT** — annual fact table with 5 KPIs + YoY; core window 2019-2023 tagged.

## Key limitations carried into the dashboard

- **2019 public transport is bus-only.** THA25 added rail later, so 2019 rail is
  missing; `pt_total_complete = False` flags it. Treat 2019 PT as a bus baseline.
- **'Vehicle Population' is registered stock, not live traffic.** Intensity uses
  the `Kilometres Travelled` measure (millions of km).
- **TEM22 -> TEM23 definitional break** at 2022 is bridged but made explicit via
  `source_table` / `definition`.
- **Partial 2026** (TEM12/TEM23 to March) flagged `year_complete = False`.
- **Blank cells**: zero in count tables (TEM12/22), preserved as missing in THA25.

## Predictive Analytics — Model Decisions

- **Holt-Winters PT Usage**: 2020 and 2021 excluded as COVID structural breaks. Validation MAPE 19.77% is a documented limitation — only 3 non-COVID training points available.
- **Holt-Winters Transport Intensity**: 2020 and 2021 excluded as COVID structural breaks. MAPE 0.93% on corrected series.
- **SARIMA PT**: Weekly data aggregated to monthly (S=52 weekly SARIMA unstable with 4 seasonal cycles). COVID years excluded from training. Data scaled to millions for numerical stability.
- **Logistic S-Curve**: Saturation ceiling L=31.6%. Inflection year t0=2021.09. Projected 2030 EV share 31.6% vs CAP target 50% — gap of 18.4 percentage points.

## Predictive Analytics — Model Decisions

- **Holt-Winters PT Usage**: 2020 and 2021 excluded as COVID structural breaks. Validation MAPE 19.77% is a documented limitation — only 3 non-COVID training points available.
- **Holt-Winters Transport Intensity**: 2020 and 2021 excluded as COVID structural breaks. MAPE 0.93% on corrected series.
- **SARIMA PT**: Weekly data aggregated to monthly (S=52 weekly SARIMA unstable with 4 seasonal cycles). COVID years excluded from training. Data scaled to millions for numerical stability.
- **Logistic S-Curve**: Saturation ceiling L=31.6%. Inflection year t0=2021.09. Projected 2030 EV share 31.6% vs CAP target 50% — gap of 18.4 percentage points.

## Predictive Analytics — Model Decisions

- **Holt-Winters PT Usage**: 2020 and 2021 excluded as COVID structural breaks. Validation MAPE 19.77% is a documented limitation — only 3 non-COVID training points available.
- **Holt-Winters Transport Intensity**: 2020 and 2021 excluded as COVID structural breaks. MAPE 0.93% on corrected series.
- **SARIMA PT**: Weekly data aggregated to monthly (S=52 weekly SARIMA unstable with 4 seasonal cycles). COVID years excluded from training. Data scaled to millions for numerical stability.
- **Logistic S-Curve**: Saturation ceiling L=31.6%. Inflection year t0=2021.09. Projected 2030 EV share 31.6% vs CAP target 50% — gap of 18.4 percentage points.

## Predictive Analytics — Model Decisions

- **Holt-Winters PT Usage**: 2020 and 2021 excluded as COVID structural breaks. Validation MAPE 19.77% is a documented limitation — only 3 non-COVID training points available.
- **Holt-Winters Transport Intensity**: 2020 and 2021 excluded as COVID structural breaks. MAPE 0.93% on corrected series.
- **SARIMA PT**: Weekly data aggregated to monthly (S=52 weekly SARIMA unstable with 4 seasonal cycles). COVID years excluded from training. Data scaled to millions for numerical stability.
- **Logistic S-Curve**: Saturation ceiling L=31.6%. Inflection year t0=2021.09. Projected 2030 EV share 31.6% vs CAP target 50% — gap of 18.4 percentage points.

## Predictive Analytics — Model Decisions

- **Holt-Winters PT Usage**: 2020 and 2021 excluded as COVID structural breaks. Validation MAPE 19.77% is a documented limitation — only 3 non-COVID training points available.
- **Holt-Winters Transport Intensity**: 2020 and 2021 excluded as COVID structural breaks. MAPE 0.93% on corrected series.
- **SARIMA PT**: Weekly data aggregated to monthly (S=52 weekly SARIMA unstable with 4 seasonal cycles). COVID years excluded from training. Data scaled to millions for numerical stability.
- **Logistic S-Curve**: Saturation ceiling L=31.6%. Inflection year t0=2021.09. Projected 2030 EV share 31.6% vs CAP target 50% — gap of 18.4 percentage points.

## Predictive Analytics — Model Decisions

- **Holt-Winters PT Usage**: 2020 and 2021 excluded as COVID structural breaks. Validation MAPE 19.77% is a documented limitation — only 3 non-COVID training points available.
- **Holt-Winters Transport Intensity**: 2020 and 2021 excluded as COVID structural breaks. MAPE 0.93% on corrected series.
- **SARIMA PT**: Weekly data aggregated to monthly (S=52 weekly SARIMA unstable with 4 seasonal cycles). COVID years excluded from training. Data scaled to millions for numerical stability.
- **Logistic S-Curve**: Saturation ceiling L=31.6%. Inflection year t0=2021.09. Projected 2030 EV share 31.6% vs CAP target 50% — gap of 18.4 percentage points.
