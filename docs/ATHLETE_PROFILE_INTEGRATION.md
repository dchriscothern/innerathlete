# InnerAthlete Profile Integration Notes

This note explains how athlete-profile style views fit into the current project.

---

## Current Reality

You do not need to manually add a new athlete profile tab from scratch anymore.

The main app already includes:
- `dashboard.py`
- `athlete_profile_tab.py`
- role-based tab visibility through `auth.py`

The more relevant integration task now is deciding how much of the athlete profile experience should remain part of the larger monitoring workflow versus how much should be mirrored into the InnerAthlete-specific experience.

---

## Current Main App Behavior

In the main app:
- athlete profiles are part of the larger monitoring workflow
- access is role-aware
- the profile view still leans on the legacy monitoring model

This means the profile view is useful for:
- readiness context
- training-load context
- force-plate context
- athlete-by-athlete review

---

## InnerAthlete Direction

The newer InnerAthlete MVP is more report-oriented and recommendation-oriented.

That means profile-style work should gradually emphasize:
- anonymized athlete summary
- biomarker flags and ranges
- genetics domains
- S2 cognition domains
- practical action plans

instead of only:
- dashboard-style monitoring mechanics

---

## Integration Guidance

If you extend profile views in this repo, prefer:

1. keeping the main `athlete_profile_tab.py` stable for the broader monitoring app
2. building new InnerAthlete-specific profile/report experiences in `waims_bio/`
3. using anonymized IDs only
4. avoiding direct upload of raw real-athlete PDFs or clinical exports

---

## Good Next Steps

Useful future profile enhancements:
- add a biomarker summary block to the main athlete profile workflow
- add a genetics summary block with domain-level takeaways
- add S2 cognition profile blocks with score-band interpretation
- add a recommendation panel that combines wellness, biomarkers, genetics, and cognition

---

## Privacy Reminder

If profile content is derived from external reports:
- strip names
- strip DOB
- strip report identifiers
- replace with codes like `ATH-001`

The repo should remain safe to share as a portfolio/demo project.
