"""
InnerAthlete Evidence Review System
==================================
Automated monitoring of new athlete-performance research relevant to InnerAthlete's
biomarker, genetics/SNP, and guardrail logic. Combines PubMed primary literature with
expert practitioner RSS feeds.

FORMAL EVIDENCE REVIEW POLICY
-----------------------------
No biomarker interpretation rule, genetics recommendation, or product guardrail change
without supporting higher-level evidence and practitioner review. Single new studies go
to WATCHLIST, not production.

Purpose: FORWARD-LOOKING INBOX only.
  Foundational references and product guardrails already live in RESEARCH_FOUNDATION.md
  and the InnerAthlete content registries. This monitor surfaces NEW research only.
  Run weekly via GitHub Actions. Triage in Evidence Review tab (Insights).

Decision ladder:
  WATCHLIST  -> interesting, single study, monitor for replication
  CANDIDATE  -> meta-analysis/SR/consensus eligible for formal review
  APPROVED   -> reviewed by performance/medical staff, approved for update
  INTEGRATED -> change made to code, content, docs, or guardrails
  REJECTED   -> reviewed, not applicable or not safe to operationalize

Guardrails:
  - Biomarkers support context, not diagnosis.
  - Genetics is probabilistic context only, never talent ID or deterministic labeling.
  - No single SNP paper should change product logic on its own.

Usage:
  python research_monitor.py                          # last 7 days, console
  python research_monitor.py --days 30                # last 30 days
  python research_monitor.py --save                   # save/update research_log.json
  python research_monitor.py --html                   # HTML decision report
  python research_monitor.py --output custom.json     # save to different file
  python research_monitor.py --github-action          # print GitHub Actions YAML
"""

import urllib.request
import urllib.parse
import urllib.error
import json
import argparse
import time
import re
import hashlib
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from pathlib import Path


# ==============================================================================
# PUBMED SEARCH TOPICS
# Focus on athlete biomarkers, genetics/SNP interpretation, and safe implementation.
# ==============================================================================
PUBMED_TOPICS = [
    {
        "topic": "Athlete Biomarker Monitoring Methodology",
        "query": (
            '((biomarker[Title/Abstract] OR "blood marker"[Title/Abstract] OR '
            '"blood testing"[Title/Abstract] OR hematology[Title/Abstract]) AND '
            '(athlete[Title/Abstract] OR sport[Title/Abstract] OR exercise[Title/Abstract]) AND '
            '(monitoring[Title/Abstract] OR longitudinal[Title/Abstract] OR interpretation[Title/Abstract] '
            'OR recovery[Title/Abstract] OR readiness[Title/Abstract])) NOT '
            '(cancer OR surgery OR intensive care OR pregnancy OR rat OR mouse)'
        ),
        "waims_signal": "Biomarker collection and interpretation guardrails",
        "waims_action": "Would change how InnerAthlete frames repeat testing, timing, or longitudinal review",
        "tags": ["biomarker", "methodology", "guardrail"],
    },
    {
        "topic": "Ferritin, Iron, And Oxygen Support In Athletes",
        "query": (
            '((ferritin[Title/Abstract] OR iron[Title/Abstract] OR hemoglobin[Title/Abstract]) AND '
            '(athlete[Title/Abstract] OR sport[Title/Abstract] OR "female athlete"[Title/Abstract]) AND '
            '(performance[Title/Abstract] OR fatigue[Title/Abstract] OR recovery[Title/Abstract] OR '
            'monitoring[Title/Abstract])) NOT (anemia of chronic disease OR cancer OR dialysis)'
        ),
        "waims_signal": "Ferritin and oxygen-support interpretation",
        "waims_action": "Would change athlete-safe copy around energy, recovery support, or repeat-draw context",
        "tags": ["biomarker", "ferritin", "iron"],
    },
    {
        "topic": "Vitamin D And Micronutrient Support In Athletes",
        "query": (
            '((vitamin d[Title/Abstract] OR micronutrient[Title/Abstract]) AND '
            '(athlete[Title/Abstract] OR sport[Title/Abstract] OR exercise[Title/Abstract]) AND '
            '(performance[Title/Abstract] OR injury[Title/Abstract] OR recovery[Title/Abstract] OR '
            'monitoring[Title/Abstract])) NOT (rickets OR osteoporosis OR renal failure)'
        ),
        "waims_signal": "Vitamin D and micronutrient support framing",
        "waims_action": "Would change how InnerAthlete discusses supplementation context, seasonality, and retest cadence",
        "tags": ["biomarker", "vitamin_d", "nutrition"],
    },
    {
        "topic": "Inflammation And Stress Markers In Athletes",
        "query": (
            '((c-reactive protein[Title/Abstract] OR hs-crp[Title/Abstract] OR cortisol[Title/Abstract] OR '
            'inflammation[Title/Abstract]) AND '
            '(athlete[Title/Abstract] OR sport[Title/Abstract] OR exercise[Title/Abstract]) AND '
            '(recovery[Title/Abstract] OR readiness[Title/Abstract] OR fatigue[Title/Abstract] OR '
            'training[Title/Abstract])) NOT (sepsis OR intensive care OR surgery OR cancer)'
        ),
        "waims_signal": "Inflammation and stress-physiology context",
        "waims_action": "Would change sample-timing caution language or how blood context is blended with load and wellness",
        "tags": ["biomarker", "hs_crp", "cortisol", "recovery"],
    },
    {
        "topic": "Female Athlete Biomarker Support",
        "query": (
            '(("female athlete"[Title/Abstract] OR sportswomen[Title/Abstract] OR women[Title/Abstract]) AND '
            '(biomarker[Title/Abstract] OR ferritin[Title/Abstract] OR vitamin d[Title/Abstract] '
            'OR hematology[Title/Abstract]) AND '
            '(recovery[Title/Abstract] OR performance[Title/Abstract] OR monitoring[Title/Abstract])) NOT '
            '(pregnancy OR fertility treatment OR oncology)'
        ),
        "waims_signal": "Female-athlete biomarker interpretation",
        "waims_action": "Would change population-specific wording or repeat-testing emphasis for women athletes",
        "tags": ["biomarker", "female"],
    },
    {
        "topic": "Athlete Genomics And SNP Validity",
        "query": (
            '((genetic[Title/Abstract] OR genomic[Title/Abstract] OR SNP[Title/Abstract] OR polymorphism[Title/Abstract]) '
            'AND (athlete[Title/Abstract] OR sport[Title/Abstract] OR exercise[Title/Abstract]) AND '
            '(performance[Title/Abstract] OR recovery[Title/Abstract] OR training response[Title/Abstract] '
            'OR sleep[Title/Abstract] OR injury[Title/Abstract] OR validity[Title/Abstract])) NOT '
            '(cancer OR prenatal OR embryo OR livestock OR mouse OR rat)'
        ),
        "waims_signal": "Genetics/SNP contextual interpretation",
        "waims_action": "Would change domain-level genetics summaries, not deterministic athlete conclusions",
        "tags": ["genetics", "snp", "guardrail"],
    },
    {
        "topic": "Nutrigenomics, Sleep, And Caffeine Response",
        "query": (
            '((nutrigenomics[Title/Abstract] OR caffeine[Title/Abstract] OR circadian[Title/Abstract] '
            'OR sleep genotype[Title/Abstract] OR chronotype[Title/Abstract]) AND '
            '(athlete[Title/Abstract] OR sport[Title/Abstract] OR exercise[Title/Abstract]) AND '
            '(performance[Title/Abstract] OR recovery[Title/Abstract] OR sleep[Title/Abstract] OR nutrition[Title/Abstract])) '
            'NOT (cancer OR psychiatric disorder OR pregnancy)'
        ),
        "waims_signal": "Nutrition and sleep genetics guidance",
        "waims_action": "Would sharpen athlete-safe coaching language around caffeine, bedtime routines, and fuel support",
        "tags": ["genetics", "sleep", "nutrition"],
    },
    {
        "topic": "Sport Genomics Ethics, Validity, And Consent",
        "query": (
            '((genetic testing[Title/Abstract] OR sport genomics[Title/Abstract] OR direct-to-consumer[Title/Abstract] '
            'OR ethics[Title/Abstract] OR consent[Title/Abstract] OR privacy[Title/Abstract]) AND '
            '(athlete[Title/Abstract] OR sport[Title/Abstract] OR exercise[Title/Abstract]))'
        ),
        "waims_signal": "Genetics guardrails, consent, and privacy posture",
        "waims_action": "Would change product guardrails, consent language, or operational boundaries for DNA inputs",
        "tags": ["genetics", "ethics", "guardrail", "consent"],
    },
]


# ==============================================================================
# POST-FETCH RELEVANCE FILTER
# Applied after PubMed returns results to catch clinical noise and non-athlete genetics papers.
# ==============================================================================

TITLE_CONTEXT_TERMS = [
    "athlete", "sport", "sports", "exercise", "training", "player",
    "female athlete", "sportswomen", "women athlete",
]

TITLE_DOMAIN_TERMS = [
    "biomarker", "blood", "hematology", "biochemical", "ferritin", "iron",
    "hemoglobin", "vitamin d", "micronutrient", "cortisol", "inflammation",
    "c-reactive", "hs-crp", "genetic", "genomic", "snp", "polymorphism",
    "nutrigenomic", "chronotype", "caffeine", "sleep",
]

TITLE_EXCLUDE_TERMS = [
    "surgery", "surgical", "operative", "pharmacol", "drug trial",
    "placebo", "biopsy", "histolog", "patholog", "radiology",
    "cancer", "tumor", "oncol", "cardiac arrest", "sepsis",
    "inpatient", "anesthesia", "post-operative", "preoperative",
    "gastroesophageal", "reflux", "kidney", "liver", "hepat",
    "ophthalmol", "retinal", "myocardial", "arrhythmia",
    "guinea pig", "equine", "rodent", "mouse", "bovine",
    "intimate partner", "endometrial", "ovarian", "polycystic",
    "embryo", "ivf", "luteal stimulation", "follicular stimulation",
    "tinnitus", "migraine", "depression medication", "psychiatr",
    "schizophrenia", "alzheimer", "parkinson", "livestock", "racehorse",
    "stroke", "post-stroke", "prenatal", "amniotic", "fibromyalgia",
    "hip osteoarthritis", "osteoarthritis", "patient", "patients",
    "hospital", "emergency", "sexual assault",
]


def passes_relevance_filter(title: str) -> bool:
    """Returns True if paper should be included, False if it should be discarded."""
    t = title.lower()
    # Hard exclude
    for term in TITLE_EXCLUDE_TERMS:
        if term in t:
            return False

    has_context = any(term in t for term in TITLE_CONTEXT_TERMS)
    has_domain = any(term in t for term in TITLE_DOMAIN_TERMS)
    return has_context and has_domain


# ==============================================================================
# EXPERT RSS SOURCES
# ==============================================================================
RSS_SOURCES = [
    {
        "name": "Martin Buchheit",
        "url": "https://martin-buchheit.net/feed/",
        "type": "expert_practitioner",
        "trust_level": "HIGH",
        "subscription_required": False,
    },
    {
        "name": "SPSR (Sport Performance & Science Reports)",
        "url": "https://sportperfsci.com/feed/",
        "type": "practitioner_journal",
        "trust_level": "HIGH",
        "subscription_required": False,
    },
    {
        "name": "BJSM Blog",
        "url": "https://blogs.bmj.com/bjsm/feed/",
        "type": "journal_blog",
        "trust_level": "HIGH",
        "subscription_required": False,
    },
    {
        "name": "Sportsmith",
        "url": None,
        "type": "applied_practice",
        "trust_level": "HIGH",
        "subscription_required": True,
        "manual_note": "MANUAL ONLY -- $13/month. Read weekly. Log as 'Source: Sportsmith (manual YYYY-MM-DD)'.",
    },
]


# ==============================================================================
# QUALITY SCORING
# ==============================================================================
QUALITY_KEYWORDS = {
    "meta-analysis":     {"score": 10, "label": "META-ANALYSIS"},
    "systematic review": {"score": 9,  "label": "SYSTEMATIC REVIEW"},
    "consensus":         {"score": 8,  "label": "CONSENSUS"},
    "position stand":    {"score": 8,  "label": "CONSENSUS"},
    "randomised":        {"score": 7,  "label": "RCT"},
    "randomized":        {"score": 7,  "label": "RCT"},
    "prospective":       {"score": 6,  "label": "PROSPECTIVE"},
    "cohort":            {"score": 5,  "label": "COHORT"},
    "biomarker":         {"score": 3,  "label": "BIOMARKER"},
    "ferritin":          {"score": 3,  "label": "FERRITIN"},
    "vitamin d":         {"score": 3,  "label": "VITAMIN D"},
    "genetic":           {"score": 3,  "label": "GENETICS"},
    "genomic":           {"score": 3,  "label": "GENETICS"},
    "snp":               {"score": 2,  "label": "SNP"},
    "female":            {"score": 2,  "label": "FEMALE"},
    "women":             {"score": 2,  "label": "FEMALE"},
    "athlete":           {"score": 2,  "label": "ATHLETE"},
    "review":            {"score": 1,  "label": "REVIEW"},
}

PUBMED_BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
RATE_SLEEP  = 0.4


# ==============================================================================
# PUBMED
# ==============================================================================
def search_pubmed(query, days):
    params = urllib.parse.urlencode({
        "db": "pubmed", "term": query, "retmax": 25,
        "sort": "pub+date", "retmode": "json",
        "datetype": "pdat", "reldate": days,
    })
    try:
        req = urllib.request.urlopen(PUBMED_BASE + "esearch.fcgi?" + params, timeout=15)
        return json.loads(req.read())["esearchresult"].get("idlist", [])
    except Exception as e:
        print(f"    PubMed search error: {e}")
        return []


def fetch_summaries(pmids):
    if not pmids:
        return {}
    params = urllib.parse.urlencode({"db": "pubmed", "id": ",".join(pmids), "retmode": "json"})
    try:
        req = urllib.request.urlopen(PUBMED_BASE + "esummary.fcgi?" + params, timeout=15)
        return json.loads(req.read()).get("result", {})
    except Exception as e:
        print(f"    PubMed fetch error: {e}")
        return {}


def score_paper(title):
    text = title.lower()
    score, labels, seen = 0, [], set()
    for kw, meta in QUALITY_KEYWORDS.items():
        if kw in text and meta["label"] not in seen:
            score += meta["score"]
            labels.append(meta["label"])
            seen.add(meta["label"])
    return score, labels


# ==============================================================================
# RSS
# ==============================================================================
def fetch_rss(source, days):
    if not source.get("url"):
        return []
    cutoff = datetime.now() - timedelta(days=days)
    items  = []
    try:
        req  = urllib.request.Request(source["url"], headers={"User-Agent": "InnerAthlete-ResearchMonitor/1.0"})
        resp = urllib.request.urlopen(req, timeout=15)
        root = ET.fromstring(resp.read())
        ns   = {"atom": "http://www.w3.org/2005/Atom"}
        entries = root.findall(".//item") or root.findall(".//atom:entry", ns)
        for entry in entries:
            title    = (entry.findtext("title") or "").strip()
            link     = (entry.findtext("link")  or "").strip()
            date_str = entry.findtext("pubDate") or entry.findtext("atom:published", ns) or ""
            desc     = re.sub(r'<[^>]+>', ' ', entry.findtext("description") or "").strip()[:300]
            pub_date = None
            for fmt in ["%a, %d %b %Y %H:%M:%S %z", "%a, %d %b %Y %H:%M:%S %Z",
                        "%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%d"]:
                try:
                    pub_date = datetime.strptime(date_str.strip()[:30], fmt).replace(tzinfo=None)
                    break
                except Exception:
                    continue
            if pub_date and pub_date < cutoff:
                continue
            score, labels = score_paper(title)
            stable_key = link or title.lower()
            stable_id = hashlib.sha1(stable_key.encode("utf-8")).hexdigest()[:12]
            items.append({
                "id": f"rss_{re.sub(r'[^a-z0-9]','_',title.lower())[:35]}_{stable_id}",
                "source": source["name"], "source_type": source["type"],
                "trust_level": source["trust_level"],
                "title": title, "url": link,
                "pub_date": pub_date.strftime("%Y-%m-%d") if pub_date else "Unknown",
                "excerpt": desc, "quality_score": score, "quality_labels": labels,
                "waims_signal": "Practitioner article -- assess manually",
                "waims_action": "Does this change a threshold or interpretation? Cross-check with Sportsmith.",
                "decision": "PENDING",
            })
    except Exception as e:
        print(f"    RSS error ({source['name']}): {e}")
    return items


# ==============================================================================
# EVIDENCE GATE
# ==============================================================================
def build_guardrail_note(tags):
    notes = []
    if {"genetics", "snp", "ethics", "consent"} & tags:
        notes.append(
            "Guardrail: genetics is contextual only. Never use for talent ID, selection, ceiling prediction, or standalone risk labels."
        )
    if {"biomarker", "ferritin", "vitamin_d", "hs_crp", "cortisol"} & tags:
        notes.append(
            "Guardrail: biomarkers support context, not diagnosis. Interpret with collection timing, repeat draws, symptoms, and recent training/life stress."
        )
    if {"guardrail", "consent"} & tags:
        notes.append(
            "Operational guardrail: require explicit consent, privacy-safe handling, and role-appropriate communication."
        )
    return " ".join(notes)


def apply_gate(papers):
    for p in papers:
        labels = p.get("quality_labels", [])
        source_type = p.get("source_type", "pubmed")
        score = p.get("quality_score", 0)
        tags = set(p.get("tags", []))
        extra = build_guardrail_note(tags)

        if source_type in ("expert_practitioner", "practitioner_journal", "journal_blog"):
            p["gate_status"] = "ASSESS"
            p["gate_note"] = (
                "Practitioner article -- assess against real-world context and product safety. "
                "Does it refine explanation, sampling workflow, or guardrail copy? "
                f"{extra}"
            ).strip()
        elif ("GENETICS" in labels or "SNP" in labels or "genetics" in tags) and not (
            "META-ANALYSIS" in labels or "SYSTEMATIC REVIEW" in labels or "CONSENSUS" in labels
        ):
            p["gate_status"] = "WATCHLIST" if score >= 6 else "BACKGROUND"
            p["gate_note"] = (
                "Single genetics/SNP papers are hypothesis-generating only. Do not convert them directly into product logic. "
                f"{extra}"
            ).strip()
        elif "META-ANALYSIS" in labels or "SYSTEMATIC REVIEW" in labels or "CONSENSUS" in labels:
            p["gate_status"] = "CANDIDATE"
            p["gate_note"] = (
                "ELIGIBLE FOR FORMAL REVIEW. Check athlete relevance, practical actionability, consistency with current guardrails, "
                f"and whether the evidence supports a wording or workflow change. {extra}"
            ).strip()
        elif "BIOMARKER" in labels or "FERRITIN" in labels or "VITAMIN D" in labels or "ATHLETE" in labels:
            p["gate_status"] = "REVIEW"
            p["gate_note"] = (
                "Athlete-relevant biomarker/genetics paper -- read abstract carefully. "
                f"Single studies can sharpen language, but they should not override guardrails or become deterministic rules. {extra}"
            ).strip()
        elif score >= 6:
            p["gate_status"] = "WATCHLIST"
            p["gate_note"] = (
                "Prospective or cohort study. Monitor for replication and athlete specificity before any product change. "
                f"{extra}"
            ).strip()
        else:
            p["gate_status"] = "BACKGROUND"
            p["gate_note"] = f"Background awareness only. Not sufficient basis for product or guardrail change. {extra}".strip()
    return papers


# ==============================================================================
# DEDUPLICATION
# ==============================================================================
DECISION_PRIORITY = {
    "INTEGRATED": 5,
    "APPROVED": 4,
    "WATCHLIST": 3,
    "REJECTED": 2,
    "PENDING": 1,
    "": 0,
}


def paper_identity(paper):
    """Stable identity for a paper across reruns and source-specific IDs."""
    if paper.get("pmid"):
        return f"pmid:{paper['pmid']}"
    if paper.get("url"):
        return f"url:{paper['url'].strip().lower()}"
    title = re.sub(r"\s+", " ", (paper.get("title") or "").strip().lower())
    source = (paper.get("source") or paper.get("source_type") or "unknown").strip().lower()
    return f"title:{source}:{title}"


def _paper_rank(paper):
    decision_score = DECISION_PRIORITY.get((paper.get("decision") or "").upper(), 0)
    filled_fields = sum(1 for v in paper.values() if v not in ("", None, [], {}))
    notes_score = 1 if paper.get("decision_notes") else 0
    return (decision_score, notes_score, filled_fields)


def merge_paper_records(primary, secondary):
    """Merge two records, preserving the richer review state and filling blanks."""
    winner, loser = (primary, secondary) if _paper_rank(primary) >= _paper_rank(secondary) else (secondary, primary)
    merged = dict(winner)

    for key, value in loser.items():
        if merged.get(key) in ("", None, [], {}):
            merged[key] = value

    # Preserve earliest discovery date and latest decision date when available.
    for date_key in ("date_found", "decision_date"):
        dates = [paper.get(date_key, "") for paper in (primary, secondary) if paper.get(date_key)]
        if dates:
            merged[date_key] = min(dates) if date_key == "date_found" else max(dates)

    return merged


def dedupe_items(items):
    deduped = {}
    order = []

    for paper in items:
        key = paper_identity(paper)
        if key not in deduped:
            deduped[key] = paper
            order.append(key)
        else:
            deduped[key] = merge_paper_records(deduped[key], paper)

    return [deduped[key] for key in order]


# ==============================================================================
# SAVE LOG
# ==============================================================================
def save_log(new_items, output_path="research_log.json"):
    log_path = Path(output_path)
    existing = []
    if log_path.exists():
        try:
            existing = json.loads(log_path.read_text(encoding="utf-8"))
        except Exception:
            pass
    existing = dedupe_items(existing)
    existing_ids = {paper_identity(p) for p in existing}
    to_add = []
    for p in new_items:
        pid = paper_identity(p)
        if pid not in existing_ids:
            p["date_found"]     = datetime.now().strftime("%Y-%m-%d")
            p["decision"]       = "PENDING"
            p["decision_by"]    = ""
            p["decision_date"]  = ""
            p["decision_notes"] = ""
            to_add.append(p)
            existing_ids.add(pid)
    combined = dedupe_items(to_add + existing)
    log_path.write_text(json.dumps(combined, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"  Saved {len(to_add)} new items to {output_path} (total: {len(combined)})\n")


def dedupe_log_file(output_path="research_log.json"):
    log_path = Path(output_path)
    if not log_path.exists():
        print(f"  No log found at {output_path}")
        return 0

    try:
        items = json.loads(log_path.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"  Could not read {output_path}: {e}")
        return 0

    before = len(items)
    after_items = dedupe_items(items)
    after = len(after_items)
    log_path.write_text(json.dumps(after_items, indent=2, ensure_ascii=False), encoding="utf-8")
    removed = before - after
    print(f"  Dedupe complete for {output_path}: removed {removed} duplicates (total now {after})")
    return removed


# ==============================================================================
# HTML REPORT
# ==============================================================================
def generate_html(pubmed_papers, rss_items, days):
    date_str = datetime.now().strftime("%B %d, %Y")
    fname    = f"research_report_{datetime.now().strftime('%Y%m%d')}.html"

    GATE_CFG = {
        "CANDIDATE":  ("#dc2626", "CANDIDATE -- eligible for threshold review"),
        "REVIEW":     ("#d97706", "REVIEW -- read carefully"),
        "WATCHLIST":  ("#64748b", "WATCHLIST -- single study, monitor"),
        "BACKGROUND": ("#94a3b8", "BACKGROUND -- awareness only"),
        "ASSESS":     ("#0284c7", "ASSESS -- practitioner article"),
    }
    LABEL_COLORS = {
        "META-ANALYSIS":"#7c3aed","SYSTEMATIC REVIEW":"#1d4ed8",
        "RCT":"#0369a1","PROSPECTIVE":"#0891b2","COHORT":"#0e7490",
        "BIOMARKER":"#0f766e","FERRITIN":"#b45309","VITAMIN D":"#ca8a04",
        "GENETICS":"#1d4ed8","SNP":"#4338ca","ATHLETE":"#0369a1",
        "FEMALE":"#be185d","CONSENSUS":"#7c3aed","REVIEW":"#64748b",
    }

    def badge(status):
        c, t = GATE_CFG.get(status, ("#94a3b8", status))
        return f'<span style="background:{c};color:white;padding:2px 8px;border-radius:4px;font-size:11px;font-weight:700;">{t}</span>'

    def qlabels(labels):
        return "".join(
            f'<span style="background:{LABEL_COLORS.get(l,"#64748b")};color:white;'
            f'padding:1px 6px;border-radius:3px;font-size:10px;font-weight:600;margin-right:3px;">{l}</span>'
            for l in labels)

    def card(p):
        bc   = GATE_CFG.get(p["gate_status"], ("#94a3b8", ""))[0]
        doi  = (f'<a href="https://doi.org/{p["doi"]}" style="color:#0284c7;font-size:12px;">DOI</a> | '
                if p.get("doi") else "")
        excpt = (f'<div style="font-size:11px;color:#475569;margin-bottom:6px;font-style:italic;">{p.get("excerpt","")[:200]}</div>'
                 if p.get("excerpt") else "")
        src  = p.get("authors", "") or p.get("source", "")
        jrn  = p.get("journal", "") or ""
        return f"""
<div style="border:1px solid #e2e8f0;border-left:4px solid {bc};border-radius:0 8px 8px 0;
     padding:16px;margin-bottom:12px;background:white;">
  <div style="margin-bottom:8px;display:flex;justify-content:space-between;flex-wrap:wrap;gap:4px;">
    <div>{badge(p['gate_status'])} &nbsp; {qlabels(p.get('quality_labels',[]))}</div>
    <div style="font-size:11px;color:#94a3b8;">{p.get('pub_date','?')}</div>
  </div>
  <div style="font-size:14px;font-weight:600;color:#0f172a;margin-bottom:4px;line-height:1.4;word-wrap:break-word;">{p['title']}</div>
  <div style="font-size:12px;color:#475569;margin-bottom:4px;">{src}{' | ' if src and jrn else ''}<em>{jrn}</em></div>
  {excpt}
  <div style="background:#f0f9ff;border-radius:4px;padding:5px 10px;font-size:11px;color:#0369a1;margin-bottom:6px;">
    <b>InnerAthlete:</b> {p.get('waims_signal','')}
  </div>
  <div style="background:#fefce8;border-radius:4px;padding:5px 10px;font-size:11px;color:#713f12;margin-bottom:8px;">
    <b>Gate:</b> {p.get('gate_note','')}
  </div>
  <div style="font-size:12px;">
    {doi}<a href="{p.get('url','#')}" target="_blank" style="color:#0284c7;">View</a>
  </div>
</div>"""

    groups = [
        ("CANDIDATES -- Eligible for threshold review",     [p for p in pubmed_papers if p["gate_status"] == "CANDIDATE"]),
        ("REVIEW -- Athlete-specific / high-relevance",     [p for p in pubmed_papers if p["gate_status"] == "REVIEW"]),
        ("PRACTITIONER ARTICLES -- Expert RSS feeds",       rss_items),
        ("WATCHLIST -- Single studies, monitor",            [p for p in pubmed_papers if p["gate_status"] == "WATCHLIST"]),
        ("BACKGROUND -- Awareness only",                    [p for p in pubmed_papers if p["gate_status"] == "BACKGROUND"]),
    ]
    body = ""
    for heading, items in groups:
        if not items:
            continue
        body += f'<h2 style="color:#1e3a5f;border-bottom:2px solid #e2e8f0;padding-bottom:8px;">{heading} ({len(items)})</h2>\n'
        body += "\n".join(card(p) for p in items)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>InnerAthlete Evidence Review — {date_str}</title>
  <style>body{{font-family:Arial,sans-serif;max-width:960px;margin:40px auto;padding:0 24px;background:#f8fafc;}}</style>
</head>
<body>
  <div style="background:#1e3a5f;color:white;border-radius:8px;padding:20px 28px;margin-bottom:20px;">
    <div style="font-size:22px;font-weight:700;">InnerAthlete Evidence Review System</div>
    <div style="margin-top:6px;opacity:.85;">{date_str} | Last {days} days |
    {len(pubmed_papers)} PubMed | {len(rss_items)} practitioner articles</div>
  </div>
  <div style="background:#fef3c7;border-left:4px solid #d97706;border-radius:0 8px 8px 0;padding:12px 16px;margin-bottom:16px;font-size:13px;">
    <b>Purpose:</b> Forward-looking inbox only. Foundational papers are in RESEARCH_FOUNDATION.md.
    This tab surfaces NEW research for weekly triage. No threshold change without meta-analysis support.
  </div>
  {body}
  <p style="text-align:center;color:#94a3b8;font-size:12px;margin-top:40px;">
    InnerAthlete Evidence Review -- PubMed E-utilities + public RSS feeds
  </p>
</body>
</html>"""

    Path(fname).write_text(html, encoding='utf-8')
    print(f"  HTML report: {fname}\n")


# ==============================================================================
# GITHUB ACTIONS YAML
# ==============================================================================
GITHUB_YAML = """\
# .github/workflows/research_monitor.yml
name: InnerAthlete Evidence Review
on:
  schedule:
    - cron: '0 8 * * 1'
  workflow_dispatch:

jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: {python-version: '3.12'}
      - run: python research_monitor.py --days 7 --save --html
      - name: Commit results
        run: |
          git config user.name "InnerAthlete Evidence Monitor"
          git config user.email "monitor@innerathlete"
          git add research_log.json research_report_*.html 2>/dev/null || true
          git diff --staged --quiet || git commit -m "Evidence review $(date +%Y-%m-%d)"
          git push
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
"""


# ==============================================================================
# MAIN
# ==============================================================================
def run_monitor(days=7, save=False, html=False, output_path="research_log.json"):
    print(f"\n{'='*60}")
    print(f"  InnerAthlete Evidence Review -- last {days} days (new research only)")
    print(f"  {datetime.now().strftime('%B %d, %Y  %H:%M')}")
    print(f"{'='*60}\n")

    all_papers = {}

    print("── PubMed ───────────────────────────────────────────────────\n")
    for cfg in PUBMED_TOPICS:
        print(f"  {cfg['topic']}...")
        pmids = search_pubmed(cfg["query"], days)
        time.sleep(RATE_SLEEP)
        if not pmids:
            print("    No new papers.\n"); continue
        summaries = fetch_summaries(pmids)
        time.sleep(RATE_SLEEP)
        new = 0
        for pmid in pmids:
            if pmid in all_papers:
                all_papers[pmid]["topics"].append(cfg["topic"]); continue
            art = summaries.get(pmid, {})
            if not art or not art.get("title"): continue

            # Apply relevance filter -- skip clinical noise
            if not passes_relevance_filter(art.get("title", "")):
                continue

            authors = art.get("authors", [])
            doi     = next((u["value"] for u in art.get("articleids", []) if u["idtype"] == "doi"), None)
            score, labels = score_paper(art.get("title", ""))
            all_papers[pmid] = {
                "id": f"pmid_{pmid}", "pmid": pmid,
                "source": "PubMed", "source_type": "pubmed", "trust_level": "PRIMARY",
                "title": art.get("title", "Unknown"),
                "authors": (authors[0].get("name", "?") + " et al.") if authors else "Unknown",
                "journal": art.get("source", "Unknown"),
                "pub_date": art.get("pubdate", "?"),
                "doi": doi, "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                "topics": [cfg["topic"]],
                "waims_signal": cfg["waims_signal"],
                "waims_action": cfg["waims_action"],
                "tags": cfg["tags"],
                "quality_score": score, "quality_labels": labels,
                "decision": "PENDING",
            }
            new += 1
        print(f"    {new} new (total unique after filter: {len(all_papers)})\n")

    print("── Expert RSS feeds ─────────────────────────────────────────\n")
    rss_items = []
    for src in RSS_SOURCES:
        if src.get("subscription_required"):
            print(f"  {src['name']}: MANUAL -- {src.get('manual_note','')}\n"); continue
        print(f"  {src['name']}...")
        items = fetch_rss(src, days)
        rss_items.extend(items)
        print(f"    {len(items)} articles\n")
        time.sleep(0.5)

    pubmed_list = apply_gate(list(all_papers.values()))
    rss_items   = apply_gate(rss_items)
    pubmed_list.sort(key=lambda x: x["quality_score"], reverse=True)

    candidates = [p for p in pubmed_list if p["gate_status"] == "CANDIDATE"]
    reviews    = [p for p in pubmed_list if p["gate_status"] == "REVIEW"]
    watchlist  = [p for p in pubmed_list if p["gate_status"] == "WATCHLIST"]

    def pr(p):
        print(f"  [{p['gate_status']}] Score {p['quality_score']} | {' . '.join(p.get('quality_labels',[]))}")
        print(f"  {p['title'][:90]}{'...' if len(p['title'])>90 else ''}")
        print(f"  {p.get('authors','')} | {p.get('journal','')} | {p.get('pub_date','')}")
        print(f"  Signal: {p['waims_signal']}")
        print(f"  Gate:   {p['gate_note']}")
        print(f"  URL:    {p['url']}\n")

    print(f"\n{'='*60}  RESULTS\n")
    if candidates:
        print(f"CANDIDATES ({len(candidates)}) -- eligible for threshold review\n")
        for p in candidates: pr(p)
    if reviews:
        print(f"REVIEW ({len(reviews)}) -- athlete-specific biomarker/genetics relevance\n")
        for p in reviews[:6]: pr(p)
    if watchlist:
        print(f"WATCHLIST ({len(watchlist)}) -- single studies\n")
        for p in watchlist[:4]: pr(p)
        if len(watchlist) > 4: print(f"  ... +{len(watchlist)-4} more\n")
    if rss_items:
        print(f"PRACTITIONER ({len(rss_items)}) -- expert RSS\n")
        for p in rss_items[:5]:
            print(f"  [{p['source']}] {p['pub_date']} -- {p['title'][:80]}")
            print(f"  {p['url']}\n")

    print(f"{'─'*60}")
    print("  SPORTSMITH: https://www.sportsmith.co/learn/ -- manual weekly review")
    print(f"{'─'*60}\n")
    print("  POLICY: No threshold change without meta-analysis support.")
    print("  CANDIDATE -> staff review -> APPROVED -> code + docs update\n")

    all_items = pubmed_list + rss_items
    if save: save_log(all_items, output_path)
    if html: generate_html(pubmed_list, rss_items, days)
    return all_items


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="InnerAthlete Evidence Review System")
    parser.add_argument("--days",          type=int, default=7)
    parser.add_argument("--save",          action="store_true")
    parser.add_argument("--html",          action="store_true")
    parser.add_argument("--output",        type=str, default="research_log.json",
                        help="Output path for research log (default: research_log.json)")
    parser.add_argument("--github-action", action="store_true")
    parser.add_argument("--dedupe-log",    action="store_true",
                        help="Deduplicate the existing research log and exit")
    args = parser.parse_args()
    if args.github_action:
        print(GITHUB_YAML)
    elif args.dedupe_log:
        dedupe_log_file(args.output)
    else:
        run_monitor(days=args.days, save=args.save, html=args.html, output_path=args.output)
