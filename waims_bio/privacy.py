import io
import re

import pandas as pd
import streamlit as st


SUSPICIOUS_COLUMN_PATTERNS = [
    r"\bname\b",
    r"player",
    r"athlete(?!_code)",
    r"email",
    r"phone",
    r"mobile",
    r"address",
    r"\bdob\b",
    r"birth",
    r"ssn",
    r"social",
    r"mrn",
    r"medical_record",
]

ALLOWED_ID_COLUMNS = {"athlete_code", "sample_id", "record_id", "session_id"}


def load_uploaded_csv(uploaded_file):
    uploaded_file.seek(0)
    return pd.read_csv(io.BytesIO(uploaded_file.read()))


def scan_dataframe_for_identifiers(df):
    suspicious_columns = []
    normalized_columns = {col: col.strip().lower() for col in df.columns}

    for original, normalized in normalized_columns.items():
        if normalized in ALLOWED_ID_COLUMNS:
            continue
        for pattern in SUSPICIOUS_COLUMN_PATTERNS:
            if re.search(pattern, normalized):
                suspicious_columns.append(original)
                break

    text_blob = " ".join(df.astype(str).fillna("").head(25).stack().tolist())
    email_match = re.search(r"[\w.+-]+@[\w-]+\.[\w.-]+", text_blob)
    phone_match = re.search(r"(?:\+?1[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?){2}\d{4}", text_blob)

    findings = []
    if suspicious_columns:
        findings.append(f"Suspicious columns detected: {', '.join(suspicious_columns)}")
    if email_match:
        findings.append("Possible email address detected in uploaded values.")
    if phone_match:
        findings.append("Possible phone number detected in uploaded values.")

    return findings


def validate_demo_upload(df, required_columns):
    missing = [column for column in required_columns if column not in df.columns]
    findings = scan_dataframe_for_identifiers(df)
    return missing, findings


def render_privacy_guardrail(title_suffix=""):
    st.caption(
        f"Privacy guardrail{title_suffix}: upload anonymized examples only. "
        "Use cohort codes like `ATH-001` and remove names, DOB, email, phone, MRN, or any direct identifiers."
    )
