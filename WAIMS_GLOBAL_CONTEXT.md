# InnerAthlete Global Context

Project context note for future development sessions.

---

## Current Product Framing

The repo should now be understood as `InnerAthlete`.

Legacy `WAIMS` naming still exists in:
- some filenames
- the generated database name
- older comments and historical notes

That legacy naming reflects project history, not the current product direction.

---

## What The Project Contains

### Main app

`dashboard.py` is the full app and includes:
- command-center style monitoring
- readiness and load workflows
- athlete profiles
- forecast and insight workflows
- InnerAthlete tabs for biomarkers, S2 cognition, and genetics

### Standalone InnerAthlete MVP

`waims_bio/dashboard.py` is the smaller prototype focused on:
- biomarkers
- genetics
- S2-style cognition
- privacy-safe uploads

---

## Current Priorities

1. Keep the repo anonymized.
2. Continue replacing legacy WAIMS framing in user-facing materials.
3. Improve InnerAthlete tab content without breaking the main app workflow.
4. Avoid importing real athlete-identifying source material into the repo.

---

## Key Technical Areas

- `auth.py` - role-based access and visible tabs
- `dashboard.py` - main Streamlit shell
- `coach_command_center.py` - command-center workflow
- `athlete_profile_tab.py` - athlete monitoring detail
- `train_models.py` - generated readiness/risk outputs
- `generate_database.py` - synthetic data generation
- `waims_bio/biomarker_tab.py` - biomarker MVP tab
- `waims_bio/cognition_tab.py` - cognition MVP tab
- `waims_bio/genomics_tab.py` - genetics MVP tab
- `waims_bio/privacy.py` - anonymization/upload screening

---

## Privacy Requirements

Do not commit:
- names
- DOB
- emails or phone numbers
- raw report identifiers
- private vendor exports
- publishing credentials or secrets

Use anonymized IDs such as `ATH-001`.

---

## Safe Working Assumption

If there is any doubt whether a file contains real athlete identifiers, do not add it to the repo unchanged.
