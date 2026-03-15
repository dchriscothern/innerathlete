"""
Shared InnerAthlete content loaders for product-demo and platform views.
"""

from __future__ import annotations

import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
CONTENT_DIR = BASE_DIR / "content" / "innerathlete"
BRAND_DIR = BASE_DIR / "assets" / "branding" / "innerathlete"


def _load_json(name: str):
    return json.loads((CONTENT_DIR / f"{name}.json").read_text(encoding="utf-8"))


def biomarkers_registry():
    return _load_json("biomarkers")


def genetics_registry():
    return _load_json("genetics")


def cognition_registry():
    return _load_json("cognition")


def recommendations_registry():
    return _load_json("recommendations")


def workflow_registry():
    return _load_json("workflow_onboarding")


def report_contracts_registry():
    return _load_json("report_contracts")


def future_input_contracts_registry():
    return _load_json("future_input_contracts")


def brand_asset(name: str) -> Path:
    return BRAND_DIR / name
