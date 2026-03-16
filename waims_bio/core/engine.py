class WAIMSEngine:
    """
    Lightweight engine for the InnerAthlete demo experience.
    Keeps the dashboard focused on privacy-safe, anonymized cohort insights.
    """

    def __init__(self, cohort_name="InnerAthlete Demo Cohort"):
        self.cohort_name = cohort_name
        self.version = "2.0.0"

    def get_unified_readiness(self, recovery_score=7, load_score=5, biomarker_score=82):
        """
        Calculates a 0-100 readiness score from:
        - Recovery / subjective readiness (35%)
        - Training load balance (30%)
        - Biomarker stability (35%)
        """
        recovery_component = max(0, min(recovery_score, 10)) * 3.5
        load_component = max(0, min(load_score, 10)) * 3.0
        biomarker_component = max(0, min(biomarker_score, 100)) * 0.35
        return round(min(recovery_component + load_component + biomarker_component, 100), 1)

    def get_org_meta(self):
        return {
            "company": "InnerAthlete",
            "tagline": "Integrated biomarkers, genetics, and S2 cognition intelligence",
            "status": "Demo mode - anonymized sample data only",
            "program_focus": "Performance optimization and return-to-play support",
        }

    def get_program_cards(self):
        return [
            {
                "title": "Biomarkers",
                "value": "4 panels",
                "detail": "Recovery, inflammation, endocrine, micronutrient trend review",
            },
            {
                "title": "Genetic Testing",
                "value": "3 domains",
                "detail": "Power profile, soft-tissue sensitivity, recovery response",
            },
            {
                "title": "S2 Cognition",
                "value": "5 signals",
                "detail": "Tracking, reaction timing, decision load, inhibition, visual span",
            },
        ]
