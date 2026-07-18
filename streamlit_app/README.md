# Irish Transport Decarbonisation Tracker — Streamlit Dashboard

The interactive dashboard for the [National Transport Decarbonisation Dashboard for Ireland](../README.md) project. Five pages covering the descriptive, predictive, and prescriptive analytics tiers, all reading exclusively from pre-computed CSVs in `data/processed/` and `data/supplementary/` — no computation happens inside the app itself.

## Pages

| Page | What it shows |
|---|---|
| **Home** | Landing page |
| **Overview** | The three KPIs indexed to 2019, fleet composition, CO2 avoided, at-a-glance stats |
| **Fuel Transition** | New registrations by fuel type, EV/PHEV adoption vs the CAP 2030 target, monthly registration gap, projected CO2 per capita |
| **Predictive Analytics** | Holt-Winters forecasts for the three KPIs, SARIMA forecast for monthly PT journeys |
| **Prescriptive Simulator** | 2030 scenario comparison with Monte Carlo uncertainty, policy lever sensitivity, EV adoption by income tier, the equity priority matrix, and the county priority map |

## File structure

```
streamlit_app/
├── router.py              # entry point — run this file
├── data_loader.py          # cached table loader; only reads data/processed/ + data/supplementary/
├── nav.py                  # page navigation / sticky header
├── style.py                 # shared colour palette, fonts, chart layout helpers
├── requirements.txt          # streamlit + plotly (dashboard-specific deps)
└── pages/
    ├── 0_Home.py
    ├── 1_Overview.py
    ├── 2_Fuel_Transition.py
    ├── 3_Predictive_Analytics.py
    └── 4_Prescriptive_Simulator.py
```

## Data contract

`data_loader.py` exposes one function, `load_table(name)`, which maps a short logical name to a specific CSV. If you add a new chart that needs a new table, register it in `data_loader.py`'s table map rather than reading a CSV path directly inside a page — this keeps every data dependency in one place and keeps the "only pipeline-produced files" governance rule enforceable.

If `load_table()` raises a `FileNotFoundError`, it will name the exact file it expected — that means a notebook (usually 01, 01b, 03, or 04) needs to be rerun first.

## Setup

From the **repository root** (not from inside `streamlit_app/`) — this matters, since Streamlit resolves `.streamlit/config.toml` relative to your working directory, and Streamlit Community Cloud always runs from the repo root too, so local behaviour matches deployed behaviour:

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt -r streamlit_app/requirements.txt
```

## Run locally

```bash
streamlit run streamlit_app/router.py
```

## Deploy to Streamlit Community Cloud (free)

1. Push your latest commit to GitHub.
2. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub.
3. **New app** → select this repository and the branch you want to deploy.
4. **Main file path:** `streamlit_app/router.py`
5. Click **Deploy**.

Community Cloud clones the repository fresh on every deploy, so any file the app reads at runtime — every CSV in `data/processed/` and `data/supplementary/` — must actually be committed to git, not just present locally.

## Design notes

- Colour palette is the **Okabe-Ito colour-blind-safe set** throughout (`#0072B2` blue, `#E69F00` amber, `#D55E00` vermillion, `#009E73` teal), so charts stay distinguishable under the most common forms of colour blindness.
- Actual data is always a **solid line**; every forecast, anywhere on the dashboard, is always a **dotted line** — one visual convention learned once, reused everywhere.
- Government targets are always a **black dash-dot line**, visually distinct from both actual and forecast series.

## Known limitations, stated plainly

- The three annual KPI forecasts are fit on roughly five real data points each — Holt-Winters was chosen specifically because it needs fewer parameters than ARIMA, but a small sample is still a small sample.
- The Business-As-Usual/Moderate/Accelerated scenario multipliers (current rate × 1, ×1.5, ×2.5) are illustrative, not derived from any specific costed policy.
- Monte Carlo uncertainty bands reflect observed year-to-year variability in the underlying growth rates, not full statistical uncertainty in the regression model itself.
- The income-tier EV adoption curves are fit on ~6 annual points per tier, with no holdout validation — reported accuracy is in-sample.

These are documented here deliberately rather than left implicit — each is also flagged directly in the notebook cell that produces it.
