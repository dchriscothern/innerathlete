# InnerAthlete Python Reference

Technical reference for the current Python project structure.

---

## Project Orientation

The repo now supports two overlapping layers:

1. Legacy monitoring infrastructure
   The larger synthetic-data athlete monitoring app with readiness, forecast, and monitoring workflows.

2. InnerAthlete MVP modules
   The newer biomarker, genetics, and S2 cognition experience built for anonymized demonstration and iteration.

---

## Core Runtime Files

### Main app shell

- `dashboard.py`
  Main Streamlit app with role-aware navigation and the full tab system.

- `auth.py`
  Role-based login, permissions, and visible-tab control.

### Main monitoring modules

- `coach_command_center.py`
  Morning brief, roster alerts, and readiness summary workflow.

- `athlete_profile_tab.py`
  Athlete-level monitoring drilldown.

- `correlation_explorer.py`
  Signal relationship and correlation analysis.

- `train_models.py`
  Readiness and injury-risk model generation.

- `generate_database.py`
  Synthetic demo database creation.

### InnerAthlete MVP modules

- `waims_bio/dashboard.py`
  Standalone InnerAthlete demo entrypoint.

- `waims_bio/biomarker_tab.py`
  Big-number biomarker dashboard, ranges, statuses, and action-plan rendering.

- `waims_bio/cognition_tab.py`
  S2-style cognition dashboard and interpretation.

- `waims_bio/genomics_tab.py`
  Genetics summary and personalized recommendations layout.

- `waims_bio/mvp_content.py`
  Shared anonymized MVP content derived from the current report structure.

- `waims_bio/privacy.py`
  Upload parsing and direct-identifier checks.

---

## Data Assets

### Main synthetic database flow

- `waims_demo.db`
- `data/processed_data.csv`
- `models/injury_risk_model.pkl`
- `models/readiness_scorer.pkl`

### InnerAthlete template data

- `waims_bio/data/biomarkers/innerathlete_biomarker_template.csv`
- `waims_bio/data/cognitive/innerathlete_cognition_template.csv`

---

## What Still Uses Legacy Naming

These still use earlier naming in code or filenames:
- `waims_demo.db`
- `waims_bio/`
- older comments and narrative text in some modules
- some research and validation copy in the main app

That naming is historical. The current product framing should be treated as `InnerAthlete`.

---

## Privacy Expectations For Developers

Never commit:
- real athlete names
- DOB or other personal identifiers
- external report IDs tied to individuals
- raw PDFs or exports that are not anonymized
- secrets such as vendor tokens or publish credentials

Preferred anonymized identifiers:
- `ATH-001`
- `ATH-002`
- `2024_lr_001`

---

## Recommended Development Flow

### For main app work

```bash
python generate_database.py
python train_models.py
streamlit run dashboard.py
```

### For InnerAthlete module work

```bash
streamlit run waims_bio/dashboard.py
```

### For quick validation

```bash
python -m compileall dashboard.py auth.py waims_bio
```

---

## Current Documentation Priority

When docs disagree, use this priority:

1. `README.md`
2. `SETUP_GUIDE.md`
3. `README_PYTHON.md`
4. older legacy notes or code comments
