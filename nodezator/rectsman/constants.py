"""Rect-related constants."""

POINTS_ATTR_NAMES = (
    "topleft",
    "topright",
    "bottomleft",
    "bottomright",
    "midleft",
    "midright",
    "midtop",
    "midbottom",
    "center",
)

ENDPOINTS_ATTR_NAMES = tuple(set(POINTS_ATTR_NAMES) - {"center"})

UPPER_ENDPOINTS = tuple(end for end in ENDPOINTS_ATTR_NAMES if "top" in end)
LOWER_ENDPOINTS = tuple(end for end in ENDPOINTS_ATTR_NAMES if "bottom" in end)
LEFT_ENDPOINTS = tuple(end for end in ENDPOINTS_ATTR_NAMES if "left" in end)
RIGHT_ENDPOINTS = tuple(end for end in ENDPOINTS_ATTR_NAMES if "right" in end)

UPPER_LINE = tuple(end for end in UPPER_ENDPOINTS if "mid" not in end)

LOWER_LINE = tuple(end for end in LOWER_ENDPOINTS if "mid" not in end)

LEFT_LINE = tuple(end for end in LEFT_ENDPOINTS if "mid" not in end)

RIGHT_LINE = tuple(end for end in RIGHT_ENDPOINTS if "mid" not in end)


VERTICAL_CROSS_SECTION_POINTS = ("midtop", "center", "midbottom")

HORIZONTAL_CROSS_SECTION_POINTS = ("midleft", "center", "midright")

VERTICAL_CROSS_SECTION_LINE = tuple(set(VERTICAL_CROSS_SECTION_POINTS) - {"center"})

HORIZONTAL_CROSS_SECTION_LINE = tuple(set(HORIZONTAL_CROSS_SECTION_POINTS) - {"center"})

TOPLEFT_BOTTOMRIGHT_DIAGONAL_POINTS = ("topleft", "center", "bottomright")

BOTTOMLEFT_TOPRIGHT_DIAGONAL_POINTS = ("bottomleft", "center", "topright")

TOPLEFT_BOTTOMRIGHT_DIAGONAL_LINE = set(TOPLEFT_BOTTOMRIGHT_DIAGONAL_POINTS) - {
    "center"
}

BOTTOMLEFT_TOPRIGHT_DIAGONAL_LINE = set(BOTTOMLEFT_TOPRIGHT_DIAGONAL_POINTS) - {
    "center"
}
