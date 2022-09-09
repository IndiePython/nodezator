### standard library import
from itertools import chain


def cross_from_rect(rect, thickness_percent):
    """Yield points describing a cross inside a rect."""

    half_thickness = round(rect.width * thickness_percent) // 2

    yield from (
        getattr(rect.move(dx, dy), attr_name)
        for attr_name, dx, dy in (
            (
                "midtop",
                -half_thickness,
                0,
            ),
            (
                "midtop",
                half_thickness,
                0,
            ),
            (
                "center",
                half_thickness,
                -half_thickness,
            ),
            (
                "midright",
                0,
                -half_thickness,
            ),
            (
                "midright",
                0,
                half_thickness,
            ),
            (
                "center",
                half_thickness,
                half_thickness,
            ),
            (
                "midbottom",
                half_thickness,
                0,
            ),
            (
                "midbottom",
                -half_thickness,
                0,
            ),
            (
                "center",
                -half_thickness,
                half_thickness,
            ),
            (
                "midleft",
                0,
                half_thickness,
            ),
            (
                "midleft",
                0,
                -half_thickness,
            ),
            (
                "center",
                -half_thickness,
                -half_thickness,
            ),
        )
    )
