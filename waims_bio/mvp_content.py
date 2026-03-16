from collections import OrderedDict


ATHLETE_OVERVIEW = {
    "athlete_code": "ATH-001",
    "label": "Athlete X",
    "height": "6'1\"",
    "weight": "222 lbs",
    "age": "19",
    "phase": "Preseason Workouts",
    "goals": ["Athleticism", "Cognitive Skills", "Sport Skills"],
    "context": "Add daily wellness, load, and fatigue monitoring.",
}


GENOMIC_SUMMARY = OrderedDict(
    [
        (
            "Nutrition & Vitamins",
            [
                "Normal fat utilization",
                "Enhanced carb utilization",
                "Low vitamin D tendency",
                "Low vitamin A, B6, and B9 tendency",
            ],
        ),
        (
            "Exercise & Response",
            [
                "Equal power and endurance profile",
                "Above-average grip strength",
                "Below-average response to strength training",
                "Above-average exercise heart-rate response",
                "Normal fitness response to cardio exercise",
            ],
        ),
        (
            "Sleep",
            [
                "Decreased sleep quality risk",
                "Decreased sleep duration risk",
            ],
        ),
        (
            "Recovery & Resilience",
            [
                "Above-average systemic inflammation tendency",
                "Below-average injury resilience",
            ],
        ),
        (
            "Cognitive Skills",
            [
                "Mildly challenging: impulse control, motor learning",
                "Strong advantage: distraction control",
                "Elite level: timing control, instinctive learning, decision complexity, improvisation",
            ],
        ),
    ]
)


BIOMARKER_RANGES = OrderedDict(
    [
        ("hs-CRP", {"value": 2.1, "unit": "mg/L", "display": "2.1", "optimal": (0.0, 2.0), "priority": "Monitor"}),
        ("Vitamin D", {"value": 48.8, "unit": "ng/mL", "display": "48.8", "optimal": (50.0, 80.0), "priority": "Watch"}),
        ("Ferritin", {"value": 233.8, "unit": "ng/mL", "display": "233.8", "optimal": (50.0, 200.0), "priority": "Monitor"}),
        ("Cortisol", {"value": 14.7, "unit": "mcg/dL", "display": "14.7", "optimal": (3.0, 10.0), "priority": "Monitor"}),
        ("GGT", {"value": 5.0, "unit": "U/L", "display": "5", "optimal": (0.0, 40.0), "priority": "Optimal"}),
        ("Glucose", {"value": 113.0, "unit": "mg/dL", "display": "113", "optimal": (70.0, 99.0), "priority": "Watch"}),
        ("Triglycerides", {"value": 134.0, "unit": "mg/dL", "display": "134", "optimal": (0.0, 149.0), "priority": "Optimal"}),
        ("TSH", {"value": 1.5, "unit": "uIU/mL", "display": "1.5", "optimal": (0.5, 2.0), "priority": "Optimal"}),
        ("Testosterone", {"value": 344.0, "unit": "ng/dL", "display": "344", "optimal": (400.0, 700.0), "priority": "Watch"}),
    ]
)


BIOMARKER_INSIGHTS = OrderedDict(
    [
        ("Recovery & Resilience", "Higher inflammation markers suggest recovery support should be prioritized after training and competition."),
        ("Sleep", "Sleep remains the fastest lever to improve recovery, cognition, and daily readiness."),
        ("Nutrition & Vitamins", "Higher-carb fueling, vitamin-rich foods, and possible vitamin D support fit the current biomarker profile."),
        ("Exercise & Response", "Moderate-to-high intensity cardio and monitored power work fit the current response profile."),
        ("Cognitive Skills", "Better sleep and lower inflammation should improve reaction speed and decision quality."),
    ]
)


ACTION_PLAN = OrderedDict(
    [
        (
            "Exercise & Response",
            [
                "Moderate to high intensity cardio 2-3x per week, with more volume only if body-composition goals require it.",
                "Use hypertrophy blocks carefully because the profile suggests slower-than-average response to pure strength training.",
                "Monitor neuromuscular fatigue and daily wellness before progressing volume.",
            ],
        ),
        (
            "Nutrition",
            [
                "Bias toward higher-carb, lower-fat fueling with carbohydrate timing around workouts.",
                "Limit white bread, pastries, sugary drinks, chips, and crackers.",
                "Lean on anti-inflammatory foods such as berries, green tea, walnuts, cherries, salmon, rice, and potatoes.",
            ],
        ),
        (
            "Recovery & Resilience",
            [
                "Tier 1: protect sleep, hydration, and post-session fueling.",
                "Tier 2: use cryotherapy, hydrotherapy, yoga, pool work, breathwork, massage, or red-light therapy.",
                "Tier 3: compression boots, float tanks, cupping, and similar recovery add-ons only after basics are consistent.",
            ],
        ),
        (
            "Sleep",
            [
                "Aim for 8+ hours and consider naps before 4 PM when overnight sleep is limited.",
                "Turn off phones 30-45 minutes before bed and avoid caffeine after 2 PM.",
                "Keep the room quiet, dark, and around 62-68 degrees.",
            ],
        ),
        (
            "Cognitive Skills",
            [
                "Practice impulse-control drills that force quick, decisive choices under pressure.",
                "Use unpredictable read-react drills to train timing and improvisation.",
                "Keep new technical learning simple by focusing on one or two movement concepts at a time.",
            ],
        ),
    ]
)


S2_METRICS = [
    {
        "metric": "Timing Control",
        "value": 92,
        "band": "Elite",
        "description": "Times attacks and reactions well even when the speed of play changes unexpectedly.",
    },
    {
        "metric": "Distraction Control",
        "value": 71,
        "band": "Higher Average",
        "description": "Can lock attention onto key cues and stay composed around noise and pressure.",
    },
    {
        "metric": "Impulse Control",
        "value": 36,
        "band": "Lower Average",
        "description": "Needs cleaner decision patience so deceptive actions do not pull reactions too early.",
    },
    {
        "metric": "Improvisation",
        "value": 88,
        "band": "Elite",
        "description": "Handles fast-changing situations well and can produce split-second counter actions.",
    },
    {
        "metric": "Instinctive Learning",
        "value": 86,
        "band": "Elite",
        "description": "Recognizes subtle patterns quickly and adapts naturally as a contest unfolds.",
    },
    {
        "metric": "Decision Complexity",
        "value": 91,
        "band": "Elite",
        "description": "Processes multiple options at speed and selects workable actions under dynamic conditions.",
    },
    {
        "metric": "Motor Learning",
        "value": 30,
        "band": "Lower Average",
        "description": "Can learn mechanics, but higher-complexity movement stacks may need more repetition and simplification.",
    },
]


S2_ACTIONS = [
    "Prioritize impulse-control reps and read-react drills under mild fatigue.",
    "Keep technical teaching simple when introducing new mechanics or layered movement patterns.",
    "Use elite timing, pattern recognition, and improvisation as performance strengths in training design.",
]


def score_band(score):
    if score < 20:
        return "Basic", "#ef4444", "#fee2e2"
    if score < 40:
        return "Lower Average", "#f97316", "#ffedd5"
    if score < 60:
        return "Average", "#f59e0b", "#fef3c7"
    if score < 80:
        return "Higher Average", "#84cc16", "#ecfccb"
    return "Elite", "#16a34a", "#dcfce7"
