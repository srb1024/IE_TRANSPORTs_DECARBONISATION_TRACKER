# Methodology
## National Transport Decarbonisation Dashboard for Ireland

_This document records every analytical decision made in the project — model
selection, KPI construction, scenario assumptions and target sources — so that
all forecasts, scenarios and policy recommendations surfaced by the dashboard can
be understood, challenged and updated as official targets evolve._

---

## 1. Overview

The project transforms eight official CSO / data.gov.ie time series into a
three-tier analytics artefact spanning descriptive, predictive and prescriptive
analytics. The methodology follows the **Data Value Map (DVM)** structure
described in the project proposal: Acquisition → Integration → Analysis
(Tiers 1–3) → Delivery.

This document covers Tiers 1–3 in detail. Data acquisition and integration
decisions are recorded in `DATA_QUALITY_REPORT.md` (auto-generated on each
pipeline run) and `DATA_DICTIONARY.md`.

---

## 2. Analysis windows

### 2.1 Core analysis window: 2019–2023

The core window is determined by the **intersection** of all eight datasets. It
represents the shortest common overlapping period in which every KPI can be
computed and compared in a consistent, fully integrated fact table.

| Dataset | Available from | Available to | Notes |
|---|---|---|---|
| TOA11 | 2018 | 2025 | Extended window |
| PEA01 | 2018 | 2025 | Extended window |
| THA25 | 2019 | 2025 | **Rail data absent in 2019 — bus only** |
| THA18 | 2018 | 2023 | Binding constraint |
| THA17 | 2018 | 2023 | Binding constraint |
| TEM12 | 2015 | 2026 | Extended window |
| TEM22 | 2019 | 2021 | Historical archive |
| TEM23 | 2022 | 2026 | Extended window |

The core window 2019–2023 is analytically rich because it captures three
distinct phases:

- **2019** — pre-pandemic transport baseline (car ownership peak, high PT growth
  trajectory)
- **2020–2021** — Covid-19 structural break (PT collapse, car km reduction,
  accelerated EV uptake)
- **2022–2023** — post-pandemic normalisation and policy intervention effects
  (PT recovery, EV policy incentives)

### 2.2 Supplementary extended windows

Two datasets are used **independently** beyond the core window:

- **TEM12 (2015–2026):** Used for the fuel transition analysis. The 11-year
  monthly series provides statistical power for modelling the petrol-to-EV
  compositional shift and supports ARIMA forecasting of EV share to 2030.
- **TEM22 + TEM23 (2019–2026):** Used for the private-car licensing series. A
  documented definitional bridge joins the two tables at 2022 (see
  `DATA_QUALITY_REPORT.md`).

---

## 3. Key Performance Indicator construction

### 3.1 Car Dependency Index (CDI)

```
CDI = private_car_vehicle_population / total_population × 1,000
```

- **Numerator:** THA18 `Vehicle Population` statistic, summed across all engine
  capacities, fuel types and counties. Represents licensed private cars in use
  at year-end.
- **Denominator:** PEA01 total population (April reference), derived from a
  clean five-year age-band partition summed across both sexes and converted from
  thousands to persons.
- **Unit:** private cars per 1,000 population.
- **Interpretation:** Higher CDI indicates greater car dependency. Ireland's CDI
  was approximately 437 in 2023, one of the highest in the EU and well above the
  modal-shift aspiration.

### 3.2 Public Transport Usage Index (PTUI)

```
PTUI = (bus_journeys + rail_journeys + luas_journeys) / total_population
```

- **Bus and rail journeys:** THA25 weekly data summed to annual, covering Dublin
  Metro Bus, all other bus and rail services.
- **Luas journeys:** TOA11 monthly data for Red and Green lines, summed to annual.
- **Denominator:** PEA01 total population (same as CDI).
- **Unit:** public transport journeys per capita per year.
- **Important caveat:** THA25 provides no rail data for 2019 (the weekly tracker
  began reporting rail later). The `pt_total_complete` flag in the fact table
  marks 2019 as bus-and-Luas-only. Do not compare 2019 PTUI directly to later
  years for rail-inclusive trend analysis; use 2020 as the effective pre-recovery
  baseline for PT.

### 3.3 Transport Intensity Indicator (TII)

```
TII = total_vehicle_km_million × 1,000,000 / total_population
```

- **Numerator:** THA17 `Kilometres Travelled` statistic (reported in millions),
  summed across all vehicle types, fuel types and counties. This is a modelled
  estimate produced by TII/RSA using a national traffic model, not a direct
  roadside measurement.
- **Denominator:** PEA01 total population.
- **Unit:** vehicle-kilometres per capita per year.
- **Interpretation:** Captures the overall intensity of road use. The Covid-19
  drop to ~7,200 km/capita in 2020 (from ~9,500 in 2019) and the recovery to
  ~8,950 by 2023 is the central transport intensity story of the period.

### 3.4 EV and electrified share of new private cars

```
ev_phev_share       = (BEV_registrations + PHEV_registrations) / total_new_car_registrations
electrified_share   = (BEV + HEV + PHEV) / total
```

- **Source:** TEM12, filtered to `New Private Cars`, monthly, 2015–2026.
- **Fuel group mapping:** Raw CSO fuel labels are mapped to five clean groups:
  Petrol, Diesel, Battery Electric (BEV), Hybrid (HEV), Plug-in Hybrid (PHEV).
- **Partial year 2026** (January–April only): annual shares remain valid
  (numerator and denominator affected equally) but annual totals must not be
  compared year-on-year.

---

## 4. Descriptive analytics (Tier 1, notebook 02)

Descriptive analytics answers: _"What has actually happened to Ireland's
transport system over 2019–2023, and is the fuel mix changing?"_

### 4.1 Approach

- Profile year-on-year changes in each KPI over the core window with percentage
  change and absolute change columns (pre-computed in the fact table).
- Annotate the Covid-19 structural break (2020–2021) explicitly on all trend
  charts using the `period_phase` column in the fact table.
- Summarise the fuel transition story using the TEM12 annual fuel-share table,
  with monthly granularity for intra-year detail.
- Where THA17/THA18 provide county breakdowns, include a regional analysis of
  car dependency to surface urban/rural differences — relevant for the local
  authority planner persona.

### 4.2 Charts produced (saved to `reports/figures/`)

| Figure | Source data | Key message |
|---|---|---|
| `kpi_trends_2019_2023.png` | `fact_transport_annual.csv` | All three KPIs on one axes; Covid trough visible |
| `car_dependency_yoy.png` | `fact_transport_annual.csv` | CDI barely changed — modal shift not occurring at scale |
| `pt_usage_recovery.png` | `public_transport_annual.csv` | Bus vs rail vs Luas recovery trajectories post-2020 |
| `fuel_mix_area_2015_2026.png` | `fuel_mix_new_private_cars_annual.csv` | Petrol/diesel decline, BEV/PHEV rise |
| `ev_share_monthly.png` | `fuel_mix_new_private_cars_monthly.csv` | Monthly volatility (registration spikes in January) |
| `county_car_dependency.png` | THA18 (county level) | Rural–urban gradient in car dependency |

---

## 5. Predictive analytics (Tier 2, notebook 03)

Predictive analytics answers: _"Where is Ireland's transport system heading if
current trends continue, and is it on track for its 2030 targets?"_

### 5.1 Challenge: short annual series

The core analysis window for annual KPIs is only five data points (2019–2023).
This is extremely short for standard ARIMA modelling, which typically requires
50+ observations for reliable parameter estimation. Three strategies address this:

1. **Separate monthly and annual models.** Monthly series (TEM12 fuel mix:
   132+ months, 2015–2025) have sufficient length for ARIMA with seasonal
   components. Annual KPI series use simpler exponential smoothing.
2. **Covid-aware training window.** For annual KPIs, the structural break in
   2020–2021 distorts trend estimation. Models are calibrated on 2019 (pre-break)
   and 2022–2023 (post-recovery), with 2020–2021 treated as a documented
   exceptional period rather than a trend signal. Where a structural break dummy
   is included, it is documented explicitly.
3. **Forecast horizon capped at three years (2024–2026).** Beyond three years,
   uncertainty intervals from short-series models become uninformatively wide.
   Longer-range projections (2027–2030) are handled in the scenario modelling
   layer (Tier 3) rather than as statistical forecasts.

### 5.2 Annual KPI models (CDI, PTUI, TII)

| Model | When preferred | Selection criterion |
|---|---|---|
| **Holt-Winters double exponential smoothing** (trend only) | Default for annual series; no seasonality | Lower AIC; performs better on very short n |
| **ARIMA(p,d,q)** | When residual autocorrelation is detected post-Holt-Winters | AIC/BIC minimisation via auto_arima (pmdarima) |

**Implementation steps in notebook 03:**

1. Fit both Holt-Winters and auto-ARIMA to the 2019–2023 annual series (or
   the 2019 + 2022–2023 Covid-excluded window).
2. Select the model with lower AIC. Record both AIC values in the notebook
   output.
3. Generate point forecasts for 2024, 2025, 2026 with 80% and 95% confidence
   intervals.
4. Perform a leave-one-out cross-validation on the training window (drop 2023,
   retrain on 2019–2022, forecast 2023, compare to actual) as a minimal
   out-of-sample check. Report RMSE.
5. Plot forecast bands on top of the historical series; annotate the training
   cutoff.

```python
# Example: Holt-Winters for annual CDI (statsmodels)
from statsmodels.tsa.holtwinters import ExponentialSmoothing
import pandas as pd

train = fact.loc[fact["Year"].isin([2019, 2022, 2023]), "car_dependency_index"].values
model = ExponentialSmoothing(train, trend="add", seasonal=None).fit()
forecast = model.forecast(3)   # 2024, 2025, 2026
```

### 5.3 Monthly fuel mix model (EV/PHEV share, TEM12)

The monthly TEM12 series (132+ months) supports a richer model:

- **SARIMA(p,d,q)(P,D,Q,12):** captures the strong January registration spike
  (year-plate change effect) and the underlying upward EV adoption trend.
- Alternatively, a **logistic growth model** (S-curve fit) may better capture
  the EV diffusion trajectory, which typically follows a technology-adoption
  S-curve. Both models are fitted and compared; the logistic model is preferred
  for communicating the diffusion narrative to policy stakeholders.
- Forecast horizon: monthly through 2030 for alignment with CAP target year.

### 5.4 Required Python libraries

```
statsmodels>=0.14      # ExponentialSmoothing, ARIMA
pmdarima>=2.0          # auto_arima (AIC-based ARIMA selection)
scipy>=1.11            # curve_fit (logistic growth)
matplotlib>=3.7        # charts
seaborn>=0.13          # chart styling
```

Add these to `requirements.txt` before running notebook 03.

---

## 6. Prescriptive analytics (Tier 3, notebook 04)

Prescriptive analytics answers: _"What does Ireland need to do differently to
get on track, and which interventions deliver the most decarbonisation impact?"_

### 6.1 Policy context and target sources

The following official targets define the "on track" benchmarks used in the gap
analysis. **Always verify against the current Climate Action Plan before
finalising the dashboard**, as targets are revised annually.

| Indicator | Target | Target year | Source | Status (as of 2025) |
|---|---|---|---|---|
| National GHG emissions | −51% vs 2018 baseline | 2030 | Climate Action Plan 2024 | Off track — projected ~23% reduction (EPA, May 2025) |
| Transport sector emissions | −50% vs 2018 | 2030 | CAP 2024 sectoral ceiling | Off track — projected ~21% reduction (EPA, May 2025) |
| EVs on the road | 945,000 vehicles | 2030 | CAP 2024 | Off track — 196,000 EVs in Oct 2025; requires ~750,000 additional in ~5 years |
| Electric share of national fleet | 30% of total fleet | 2030 | CAP 2024 / SEAI | Off track at current adoption rates |
| Public transport modal shift | Doubling of PT journeys vs 2019 | 2030 | NTA Sustainable Mobility Policy (2022) | Partially on track — 2023 PTUI already above 2019 on bus+rail but below 2019+rail implied baseline |

> **Note on the EV target:** CAP 2024 specifies 945,000 EVs on Irish roads by
> 2030. Ireland had ~196,000 EVs in October 2025. Closing the gap requires
> licensing approximately 125,000–150,000 EVs per year from 2026 to 2030. The
> annual new private car market is approximately 160,000–200,000 vehicles,
> meaning effectively every new car sold would need to be electric. This is the
> central finding of the prescriptive tier: the EV target is extremely
> challenging on current trajectory.

### 6.2 Three scenarios

| Scenario | Label in dashboard | Description |
|---|---|---|
| **Business-As-Usual (BAU)** | "Current trajectory" | Extrapolates the statistical forecasts from Tier 2 without policy change. Represents where Ireland lands if no additional interventions are made beyond those already embedded in current trends. |
| **Moderate Intervention** | "NTA-aligned" | Assumes a sustained **5% per annum** growth in total public transport journeys (consistent with the lower bound of NTA ridership targets) and an acceleration in EV/PHEV share of new cars growing by **+4 percentage points** per year above the BAU trend. Models the effect of announced BusConnects investment and existing EV incentive schemes if fully delivered. |
| **Accelerated Transition** | "Climate Action Plan" | Assumes **8–10% per annum** PT journey growth and EV/PHEV share reaching **≥50%** of new car registrations by 2027, aligned with the CAP 2024 full-ambition scenario needed to approach the 945,000-EV target. Requires significant modal shift in urban areas and a step-change in EV incentive schemes. |

> **Assumption transparency:** The annual growth rates above are _working
> assumptions_ derived from linear interpolation between the 2023 observed
> values and the 2030 official targets. They are documented in
> `data/external/scenario_params.csv` so they can be adjusted without changing
> the notebook code.

### 6.3 Scenario modelling approach

For each scenario, the KPI trajectory from 2024 to 2030 is computed as:

```
KPI_t = KPI_2023 × ∏(1 + g_i) for i in [2024, t]
```

where `g_i` is the scenario-specific annual growth/change rate for year `i`.
For the Car Dependency Index, the growth rate is negative (modal shift reduces
car dependency). For the PTUI, the rate is the annual PT journey growth.

Scenario paths are stored as long-format DataFrames (year × scenario × KPI)
and joined to the historical fact table for plotting.

### 6.4 Target gap analysis

For each KPI and each scenario, the gap to the 2030 target is computed at
every forecast year:

```
gap_pct_t = (KPI_t − target_2030) / target_2030 × 100
status_t  = "on track"  if KPI_t within 5% of linear path to target
          = "at risk"   if 5%–15% off the linear path
          = "off track" if >15% off the linear path
```

Traffic-light status indicators (`on_track`, `at_risk`, `off_track`) are
exposed as columns in the scenario output table, which Power BI reads directly
for the KPI cards and status icons on the overview page.

### 6.5 Sensitivity analysis

A one-at-a-time (OAT) sensitivity analysis answers which input lever — PT
journey growth rate or EV adoption rate — has the greater impact on the target
gap for the transport sector:

1. Hold one parameter at its BAU value; vary the other across a range of ±50%
   of the Moderate scenario value.
2. Record the resulting 2030 target gap for transport emissions proxy (EV share
   as a proportion of total fleet).
3. The parameter with steeper gap-vs-rate slope has greater leverage.

This output feeds the plain-language policy recommendation displayed on the
dashboard's scenario simulator page (e.g., _"Accelerating EV adoption has twice
the decarbonisation impact of PT growth in closing Ireland's 2030 transport
target gap under current conditions"_).

---

## 7. Known limitations and caveats

1. **Car dependency ≠ emissions.** The Car Dependency Index measures registered
   vehicles per capita, not vehicle use or emissions. Two households with the
   same CDI may have very different transport emissions depending on journey
   length, vehicle age and fuel type. The index is a structural indicator, not
   an emissions proxy.

2. **PT journeys ≠ modal share.** The PTUI measures absolute journeys per
   capita. It does not capture modal share (what % of all journeys are by PT).
   Without total journey estimates (which are not in the acquired datasets), true
   modal shift cannot be quantified directly.

3. **Vehicle-km is modelled, not measured.** The THA17 `Kilometres Travelled`
   statistic is produced by TII using a traffic model, not roadside counters.
   It provides a consistent series but should be treated as an estimate.

4. **Short time series for annual models.** Five annual data points (2019–2023)
   are insufficient for robust ARIMA estimation. All annual-KPI model outputs
   should be presented with wide confidence intervals and treated as directional
   indicators rather than precise forecasts.

5. **2019 PT is incomplete.** Rail journeys are absent from THA25 for 2019.
   The `pt_total_complete = False` flag marks this; the 2019 PTUI understates
   total ridership. Use 2020 as the effective PT baseline for trend analysis.

6. **Scenario growth rates are working assumptions.** The rates in
   `data/external/scenario_params.csv` are derived from linear interpolation to
   official targets, not econometric models. They should be reviewed against the
   latest NTA and SEAI projections before each dashboard update.

7. **Target numbers change annually.** The Irish Climate Action Plan is updated
   every year. The targets tabulated in section 6.1 were sourced from CAP 2024
   and EPA projections published in May 2025. Verify against the current plan
   before publishing dashboard outputs.

---

## 8. References

- Climate Action Plan 2024. Government of Ireland, Department of the Environment,
  Climate and Communications. Available at: gov.ie/climateaction
- Environmental Protection Agency (2025). _Greenhouse Gas Emission Projections
  2024 to 2055_. EPA, Wexford.
- National Transport Authority (2022). _Sustainable Mobility Policy: A Strategic
  Framework to 2030_. NTA, Dublin.
- Central Statistics Office. _Transport Statistics Hub_. data.cso.ie/transpost
- Hyndman, R.J. & Athanasopoulos, G. (2021). _Forecasting: Principles and
  Practice_, 3rd ed. OTexts, Melbourne. Available at: otexts.com/fpp3
- OECD (2022). _Redesigning Ireland's Transport for Net Zero_.
  doi:10.1787/b798a4c1-en

---

_Last updated: see git log. This document is maintained alongside the analytical
notebooks and should be updated whenever scenario parameters, target values or
model choices change._
