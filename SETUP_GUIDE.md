# InnerAthlete Setup Guide

Step-by-step local setup for the current InnerAthlete MVP.

---

## Requirements

- Python 3.11+
- pip
- PowerShell or another shell
- enough disk space for the demo database, generated model files, and local assets

---

## Standard Local Setup

```bash
# 1. Open the repo
cd C:\GitHub\innerathlete

# 2. Create a virtual environment
python -m venv .venv

# 3. Activate it
.\.venv\Scripts\Activate.ps1

# 4. Install dependencies
pip install -r requirements.txt

# 5. Generate the demo database
python generate_database.py

# 6. Train the demo models
python train_models.py

# 7. Launch the main app
streamlit run dashboard.py
```

App runs at `http://localhost:8501`.

---

## InnerAthlete Prototype Only

If you are only iterating on the smaller InnerAthlete MVP interface:

```bash
cd C:\GitHub\innerathlete
.\.venv\Scripts\Activate.ps1
streamlit run waims_bio/dashboard.py
```

Use this when working specifically on:
- biomarkers
- S2 cognition
- genetics
- privacy-safe uploads

---

## Main Entry Points

- `dashboard.py` - full app with original monitoring workflow plus InnerAthlete tabs
- `waims_bio/dashboard.py` - smaller standalone InnerAthlete demo

---

## Required Files Generated During Setup

Running the standard flow creates or refreshes:
- `waims_demo.db`
- `models/injury_risk_model.pkl`
- `models/readiness_scorer.pkl`
- `data/processed_data.csv`

---

## Environment Variables

Most local UI work does not require environment variables.

Optional integrations may use a `.env` file at the repo root:

```env
ANTHROPIC_API_KEY=your_key_here
BALLDONTLIE_API_KEY=your_key_here
```

Do not commit `.env`.

---

## Privacy Setup Rules

Before importing example files:

- remove athlete names
- remove DOBs
- remove email/phone
- remove report IDs tied to people
- remove team/school identifiers when they can re-identify the athlete
- replace identifiers with codes like `ATH-001`

The InnerAthlete upload flow includes basic screening, but safe handling still depends on manual review.

---

## Safe Demo Templates

Use these included templates for testing:

- `waims_bio/data/biomarkers/innerathlete_biomarker_template.csv`
- `waims_bio/data/cognitive/innerathlete_cognition_template.csv`

---

## Common Commands

```bash
python generate_database.py
python train_models.py
python -m compileall dashboard.py auth.py waims_bio
streamlit run dashboard.py
streamlit run waims_bio/dashboard.py
```

---

## Troubleshooting

| Symptom | Fix |
|---|---|
| `no such table` errors | rerun `python generate_database.py` |
| missing `models/*.pkl` | rerun `python train_models.py` |
| main app opens but InnerAthlete tabs look empty | confirm `waims_bio/` files are present and import cleanly |
| standalone bio app errors on import | run `python -m compileall waims_bio` |
| port 8501 already in use | run `streamlit run dashboard.py --server.port 8502` |
| uploads are blocked | remove direct identifiers and retry with anonymized columns |

---

## Current Documentation Reality

This project evolved from an earlier WAIMS codebase. Some internal filenames and comments still reflect that history. Setup instructions in this file follow the current InnerAthlete framing and should take precedence over older legacy references.
