# Streamlit dashboard — setup & deployment

A Streamlit build of the National Transport Decarbonisation Dashboard,
alongside the existing Power BI version. Reads only from `data/processed/`
— the same pipeline-produced CSVs, same data-governance rule.

## File layout

```
Transport_Decarbonisation_Dashboard_IE/      ← repo root
├── .streamlit/
│   └── config.toml          ← theme. MUST live here, not inside streamlit_app/
│                                (Streamlit resolves config.toml relative to
│                                the working directory you run from, not the
│                                script's own folder — see streamlit/streamlit#8195)
├── data/processed/           ← unchanged, existing pipeline output
├── requirements.txt          ← existing pipeline deps (pandas, statsmodels, ...)
└── streamlit_app/
    ├── app.py                ← entry point / Home page
    ├── data_loader.py         ← cached loaders, data/processed/ only
    ├── style.py               ← shared colour palette + chart styling
    ├── requirements.txt       ← streamlit + plotly only
    └── pages/
        ├── 1_Overview.py
        ├── 2_Fuel_Transition.py
        ├── 3_Predictive_Analytics.py
        └── 4_Prescriptive_Simulator.py
```

## Run locally

From the **repo root** (not from inside `streamlit_app/`):

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pip install -r streamlit_app/requirements.txt
streamlit run streamlit_app/app.py
```

Running from the repo root matters for two reasons: it's how `.streamlit/config.toml`
gets picked up, and it matches how Streamlit Community Cloud always runs your
app (working directory = repo root), so local behaviour matches deployed
behaviour exactly.

## Deploy to Streamlit Community Cloud (free)

1. Push `streamlit_app/`, `.streamlit/config.toml`, and `data/processed/` to
   GitHub (already the case if you're following the branch workflow).
2. Go to [share.streamlit.io](https://share.streamlit.io) → **New app** →
   **Use existing repo**.
3. Repository: `srb1024/Transport_Decarbonisation_Dashboard_IE`. Branch: `main`
   (or wherever you merge to for the graded submission).
4. **Main file path**: `streamlit_app/app.py`
5. Deploy. Community Cloud auto-discovers `streamlit_app/requirements.txt`
   (it checks the entrypoint's own folder first, then the repo root) — no
   extra config needed there.

**Since this repo is private**: Streamlit Community Cloud's free tier allows
one privately-hosted app at a time. That's enough for this project, but
worth knowing if your team deploys other private apps under the same
account later.

## Data-governance rule (unchanged from the Power BI build)

`data_loader.py` only reads from `data/processed/`. If a table is missing,
it raises a clear error telling you which pipeline notebook (01/03/04) to
rerun — it will never silently fall back to raw or external data.
