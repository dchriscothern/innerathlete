# InnerAthlete Research Foundation

Evidence and policy notes for the current monitoring and recommendation workflow.

---

## Research Philosophy

InnerAthlete should be evidence-informed and context-aware.

Working rule:
- research sets the starting point
- practitioner context adjusts interpretation
- real athlete deployment requires stronger governance than a demo

This repo is still a demo environment. It should not be treated as a clinical system.

---

## Current Evidence Areas In The Project

### Sleep and recovery

Used to support:
- readiness interpretation
- recovery recommendations
- cognition context

### Subjective wellness

Used to support:
- daily monitoring
- burden-conscious athlete check-ins
- personal baseline comparison

### Neuromuscular monitoring

Used to support:
- CMJ and RSI interpretation
- readiness and fatigue context

### Load and schedule context

Used to support:
- training-load interpretation
- forecast/risk context
- cumulative stress logic

### Biomarker context

Used to support:
- inflammation discussion
- endocrine and micronutrient discussion
- recommendation framing in the InnerAthlete tabs

### Genetics and cognition context

Used to support:
- recommendation framing
- domain-level interpretation
- individualized communication

These should be treated as contextual decision-support signals, not deterministic truth.

---

## Data Quality Policy

Missing data is meaningful in athlete monitoring.

Project principles:
- do not silently fabricate subjective data
- flag missing daily wellness instead of pretending it is normal
- keep imputation explicit and auditable
- prefer personal baselines over broad population assumptions when possible

The current data-quality implementation lives in `data_quality.py`.

---

## Validation Policy

The project should avoid over-claiming predictive accuracy.

Reasonable demo posture:
- readiness ranking and workflow support are acceptable
- injury prediction claims should remain conservative
- any production-style claim requires stronger validation on real longitudinal data

The current validation implementation lives in `model_validation.py`.

---

## Privacy And Governance

This is the most important non-model requirement.

Before any real athlete deployment:
- use role-based access
- encrypt data at rest and in transit
- keep audit logs
- document retention and deletion rules
- obtain explicit consent where required
- review legal and contractual obligations

For this repo specifically:
- keep demo data anonymized
- do not commit raw clinical or athlete-identifying documents

---

## Practical Evidence Posture For InnerAthlete

The InnerAthlete tabs should communicate:
- signals
- context
- recommendations

They should avoid presenting:
- diagnosis
- deterministic genetic claims
- definitive medical advice

A safe default is:
"this pattern may support" or "this suggests monitoring" rather than a hard clinical conclusion.

---

## Current Gap Areas

Still worth future review:
- final cleanup of older basketball-specific WAIMS narrative inside legacy modules
- clearer source mapping for biomarker and genetics interpretation rules
- tighter evidence notes for S2-style cognition recommendations
- updated references for any future production use

---

## Source Of Truth

If this file conflicts with older legacy notes, prefer the current InnerAthlete framing from:
- `README.md`
- `SETUP_GUIDE.md`
- `README_PYTHON.md`
- `innerathlete_context.md`
