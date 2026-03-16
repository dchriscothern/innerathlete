# InnerAthlete

Privacy-first athlete performance intelligence MVP built with Python, Streamlit, SQLite, and Plotly.

This repo now centers on the `InnerAthlete` concept:
- biomarkers
- genetic testing summaries
- S2-style cognition testing
- wellness and readiness workflows
- anonymized demo data only

Some module and database names still use older `WAIMS` naming. That is legacy code structure, not the current product framing.

---

## Current App Structure

There are two useful entry points:

1. `dashboard.py`
   The main app. It keeps the larger multi-tab monitoring workflow and now includes InnerAthlete tabs for Biomarkers, S2 Cognition, and Genetics.

2. `waims_bio/dashboard.py`
   The smaller InnerAthlete-focused MVP prototype. It is useful when iterating on the standalone biomarker/genomics/cognition experience.

---

## Quick Start

```bash
pip install -r requirements.txt
python generate_database.py
python train_models.py
streamlit run dashboard.py
```

Main app runs at `http://localhost:8501`.

To run the smaller InnerAthlete-only prototype:

```bash
streamlit run waims_bio/dashboard.py
```

---

## What The MVP Includes

### Main Monitoring Tabs

The main app still includes the original monitoring workflow:
- Command Center
- Today's Readiness
- Athlete Profiles
- Trends & Load
- Jump Testing
- Availability & Injuries
- Forecast
- Insights

### InnerAthlete Tabs

The main app also now includes:
- Biomarkers
- S2 Cognition
- Genetics

These tabs were reshaped from your MVP PDFs and examples into anonymized demo experiences.

---

## InnerAthlete Content Model

### Biomarkers

Current example biomarker workflow includes:
- big-number dashboard cards and gauges
- optimal ranges and watch/monitor states
- detail table for key markers
- action-plan guidance

Current demo marker set includes:
- hs-CRP
- Vitamin D
- Ferritin
- Cortisol
- GGT
- Glucose
- Triglycerides
- TSH
- Testosterone

### Genetics

Current genetics summary is organized into:
- Nutrition & Vitamins
- Exercise & Response
- Sleep
- Recovery & Resilience
- Cognitive Skills

### S2 Cognition

Current cognition summary includes:
- Timing Control
- Distraction Control
- Impulse Control
- Improvisation
- Instinctive Learning
- Decision Complexity
- Motor Learning

Banding follows the MVP range system:
- `0%-20%` Basic
- `20%-40%` Lower Average
- `40%-60%` Average
- `60%-80%` Higher Average
- `80%-100%` Elite

---

## Privacy Rules

This repo should remain portfolio-safe and anonymized.

Do not commit:
- athlete names
- DOB or age tied to a real identity
- phone numbers
- email addresses
- MRNs or report IDs
- team-specific identifiers
- raw vendor exports with direct identifiers
- publish secrets or API tokens

Use anonymized IDs like:
- `ATH-001`
- `ATH-002`
- `2024_lr_001`

The upload flow in the InnerAthlete modules blocks obvious direct identifiers, but that is a guardrail, not a substitute for manual review.

---

## Safe Reference Files

The `waims_bio/data/` area contains safe templates for demo use:
- [waims_bio/data/biomarkers/innerathlete_biomarker_template.csv](/C:/GitHub/innerathlete/waims_bio/data/biomarkers/innerathlete_biomarker_template.csv)
- [waims_bio/data/cognitive/innerathlete_cognition_template.csv](/C:/GitHub/innerathlete/waims_bio/data/cognitive/innerathlete_cognition_template.csv)

Use these as the starting point when bringing in examples.

---

## Key Files

### Product-facing

- `dashboard.py` - main multi-tab Streamlit app
- `auth.py` - role-based access and visible-tab control
- `waims_bio/dashboard.py` - standalone InnerAthlete MVP app
- `waims_bio/biomarker_tab.py` - biomarker dashboard
- `waims_bio/cognition_tab.py` - S2 cognition dashboard
- `waims_bio/genomics_tab.py` - genomics summary and action plan
- `waims_bio/mvp_content.py` - shared anonymized MVP content
- `waims_bio/privacy.py` - upload screening and privacy guardrails

### Data / modeling

- `generate_database.py` - creates synthetic demo database
- `train_models.py` - trains readiness and injury-risk outputs
- `coach_command_center.py` - main command-center rendering
- `athlete_profile_tab.py` - athlete deep-dive view

---

## Recommended Run Order

```bash
python generate_database.py
python train_models.py
streamlit run dashboard.py
```

If you only want to iterate on the smaller InnerAthlete prototype, the database is not the main dependency. You can launch `waims_bio/dashboard.py` directly for UI work.

---

## Known Project State

- The product framing is now `InnerAthlete`.
- Some internal code comments, filenames, and data structures still reflect the older WAIMS project history.
- The main shell and new InnerAthlete tabs have been updated.
- Additional documentation and in-app copy still need gradual cleanup for full naming consistency.

---

## Next Documentation Targets

After this README, the most important supporting docs are:
- `SETUP_GUIDE.md`
- `README_PYTHON.md`
- `innerathlete_context.md`

Those should be treated as the current source of truth before touching older legacy notes.
