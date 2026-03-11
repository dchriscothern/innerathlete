class WAIMSEngine:
    """
    WAIMS Core Engine: Orchestrates data from Subjective, 
    External, and Biological pillars.
    """
    def __init__(self, athlete_id="Joe Bailey"):
        self.athlete_id = athlete_id
        self.version = "1.0.0"

    def get_unified_readiness(self, genomic_bias=1.25, sub_wellness=7, ext_load=50):
        """
        Calculates a 0-100 Readiness score based on:
        - Subjective Wellness (40%)
        - External Load (40%)
        - Genomic Baseline (20%)
        """
        # Normalizing inputs to a 100-point scale
        readiness_score = (sub_wellness * 4) + (ext_load / 10 * 4) + (genomic_bias * 20)
        return round(min(readiness_score, 100), 1)

    def get_athlete_meta(self):
        """Returns metadata for the dashboard header."""
        return {
            "name": self.athlete_id,
            "status": "Active / Post-Op Week 12",
            "genomic_type": "Power/Speed (ACTN3-RR)"
        }