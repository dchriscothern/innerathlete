# Content Ingest Guide

This repo uses source materials to inform product structure and content models, but it does **not** store raw athlete-identifying material.

## Core Rule

Only sanitized abstractions may enter tracked repo content.

Allowed:
- anonymized athlete codes such as `ATH-001`
- rewritten summary copy
- domain definitions for blood, DNA, brain, and recommendations
- workflow notes abstracted from protocols
- future input contracts that describe safe schemas

Not allowed:
- athlete names
- initials that can re-identify a person
- dates of birth
- phone numbers
- emails
- direct report IDs
- decrypted files
- files labeled `fixed names`
- encryption keys
- encrypted payloads
- raw bundled report archives
- raw S2 individual reports
- raw consent forms containing user data

## Source Classification

Use one of these labels when reviewing new material:

- `public-safe`
  - General literature, non-sensitive background references, public-facing workflow ideas.
- `internal-reference-only`
  - Internal protocols, templates, workflow notes, and interpretation guidance that can inform structure after rewriting.
- `do-not-port`
  - Anything with direct identifiers, client-specific reports, decrypted content, keys, or re-identification risk.

## What Can Be Abstracted

Safe abstractions include:
- biomarker categories and sample-timing notes
- genetics domain groupings and caution language
- cognition score-band structure and coaching translation patterns
- report anatomy for athlete, coach, and practitioner audiences
- recommendation tags and action-plan logic
- privacy, consent, and onboarding boundaries at the product-architecture level

## What Must Stay Outside The Repo

Keep these outside tracked content even if they are useful references:
- named athlete reports
- PDFs or DOCX files with example athlete names
- decrypted genetics spreadsheets
- files marked with names, initials, or fixed-name mappings
- encryption keys and decryption utilities tied to real data
- zip bundles of corrected athlete reports
- raw questionnaire exports if they contain identifiable information

## Anonymization Expectations

Before any example data is used in the app:
- replace identity fields with neutral codes like `ATH-001`
- remove names, initials, team-specific identifiers, and contact fields
- remove dates that can identify a person unless they are converted to safe relative fields
- strip hidden metadata when possible
- rewrite narrative text so it is no longer traceable to a real athlete

## Product Boundaries

- Investor demo content must stay product-focused and privacy-safe.
- Consent and onboarding details belong in practitioner/admin flows, not in the investor walkthrough.
- Genetics must always be contextual and non-deterministic.
- Biomarker and cognition interpretation should favor longitudinal context over one-off snapshot claims.
