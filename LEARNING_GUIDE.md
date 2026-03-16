# InnerAthlete Learning Guide

High-level explanation of what the project is doing and why it is organized this way.

---

## What This Project Is

InnerAthlete is currently a hybrid project:

1. a larger athlete-monitoring app with readiness, trends, and forecast workflows
2. a newer InnerAthlete MVP layer focused on biomarkers, genetics, S2 cognition, and personalized action plans

That is why the repo still contains both:
- legacy monitoring infrastructure
- newer report-style InnerAthlete modules

---

## Why The Project Uses Multiple Views

Different users need different levels of detail.

Examples:
- coaches want quick interpretation
- practitioners want more underlying context
- executives want summary-level views

The app structure reflects that reality through:
- role-based access
- summary tabs
- detail tabs
- InnerAthlete recommendation-oriented tabs

---

## What The Main App Does

The main app still handles:
- readiness
- load and trend monitoring
- athlete profiles
- availability
- forecast and insights

This is the operational workflow side of the repo.

---

## What The InnerAthlete MVP Adds

The InnerAthlete modules shift the experience toward individualized reporting:
- biomarker dashboards
- genomics summaries
- S2 cognition summaries
- action-plan style recommendations

This comes from the newer MVP materials and report examples.

---

## Why Privacy Matters So Much Here

A project like this becomes useless if athlete trust is broken.

That is why this repo should stay:
- anonymized
- portfolio-safe
- free of direct identifiers

The technical upload guardrails help, but the more important rule is cultural and procedural: do not bring real identifiable athlete data into the repo.

---

## What To Learn From The Codebase

Useful concepts in this repo:
- role-based UI design
- readiness and monitoring workflows
- synthetic demo-data generation
- privacy-safe prototyping
- turning report examples into interactive app flows

---

## How To Talk About The Project

A good concise description is:

"InnerAthlete is a privacy-first athlete performance intelligence MVP that combines readiness workflows with biomarker, genetics, and S2 cognition reporting inside an anonymized Streamlit application."

---

## What To Be Careful About

Avoid overselling:
- genetics as destiny
- injury prediction as clinical certainty
- demo thresholds as medical truth

Safer framing:
- decision support
- context-aware recommendations
- anonymized MVP prototype

---

## Best Files To Read First

- `README.md`
- `SETUP_GUIDE.md`
- `README_PYTHON.md`
- `innerathlete_context.md`
- `waims_bio/mvp_content.py`
- `waims_bio/privacy.py`
