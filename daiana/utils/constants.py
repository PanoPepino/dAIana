from pathlib import Path

# Mapping colors to commands
COMMAND_COLORS = {
    "save":    (0, 200, 120),      # Vivid moss green (#64E678) ↑ saturation
    "update":  (245, 200, 220),      # Vivid peach orange (#F58C64) ↑ brightness
    "show":    (200, 140, 100),       # Rich warm brown (#D6965F) ↑ lightness
    "hunt":    (240, 60, 90),        # Electric crimson (#F03C5A) ↑ intensity
    "oracle":  (230, 190, 60),       # Radiant oracle gold (#E6BE3C) ↑ glow
    "compile": (30, 170, 240),       # Electric moonlit blue (#1AAEA0) ↑ pop
}

# Colors and wording for status (history of your application)
STATUS_COLORS = {
    "applied":    (240, 240, 240),    # Pure off-white
    "contacted":  (250, 240, 180),    # Very pale cream yellow
    "int_1":      (150, 200, 150),    # Warm golden yellow (bridge)
    "int_2":      (70, 210, 190),    # Vibrant turquoise lake
    "offered":    (0, 200, 120),    # Vivid success green
    "rejected":   (240, 60, 90),      # Electric crimson
}

ALLOW_STATUS = [
    "applied",
    "contacted",
    "int_1",
    "int_2",
    "offered",
    "rejected"
]


# Fields to be filled in dictionary when saving/compiling/updating
FIELDNAMES = [
    'job_position',
    'company_name',
    'location',
    'history',
    'job_link'
]


MODE_CONFIG = {
    "cv": {
        "template": Path("cv_and_letter/template_cv.tex"),
        "addon_name": "cv",
        "required_fields": [
            "career",
            "job_position",
            "company_name",
            "location",
            "job_link",
        ],
    },
    "cl": {
        "template": Path("cv_and_letter/template_cl.tex"),
        "addon_name": "cl",
        "required_fields": [
            "career",
            "job_position",
            "company_name",
            "location",
            "job_link",
            "your_background",
            "company_challenge",
        ],
    },
}
