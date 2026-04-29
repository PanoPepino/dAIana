"""
Colors of the package
"""


COMMAND_COLORS: dict[str, tuple[int, int, int]] = {
    "save": (0, 200, 120),
    "update": (245, 200, 220),
    "show": (200, 120, 100),
    "hunt": (240, 60, 90),
    "oracle": (230, 190, 60),
    "compile": (30, 170, 240),
    "init": (220, 220, 0),
    "check": (100, 150, 150)
}

STATUS_COLORS: dict[str, tuple[int, int, int]] = {
    "applied": (240, 240, 240),
    "contacted": (250, 240, 180),
    "int_1": (150, 200, 150),
    "int_2": (70, 210, 190),
    "offered": (0, 200, 120),
    "rejected": (240, 60, 90),
}

NEUTRAL = (240, 240, 240)

FOREST_TEAL = (220, 220, 0)
LIGHT_WOOD = (200, 120, 100)
