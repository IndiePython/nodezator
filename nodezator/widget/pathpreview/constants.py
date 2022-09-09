"""Constants for the path previewer."""

### standard library import
from xml.etree.ElementTree import Element

### third-party import
from pygame.transform import rotate as rotate_surface


### local imports

from ...surfsman.render import combine_surfaces, render_rect

from ...surfsman.icon import render_layered_icon

from ...colorsman.colors import (
    BLACK,
    PATHPREVIEW_BG,
)


### surface representing file manager

ICON_SURF = render_layered_icon(
    chars=[chr(ordinal) for ordinal in (33, 34)],
    dimension_name="height",
    dimension_value=18,
    colors=[BLACK, (30, 130, 70)],
    background_width=20,
    background_height=20,
)


### button surfs

BUTTON_WIDTH, BUTTON_HEIGHT = ICON_SURF.get_size()

char_width, char_height = (s - 6 for s in ICON_SURF.get_size())

##
MEDIA_SURF = render_rect(
    BUTTON_WIDTH,
    BUTTON_HEIGHT,
    PATHPREVIEW_BG,
)


### create different lists to gather the surfaces and
### other relevant data

BUTTON_SURFS = (
    ICON_SURF,
    MEDIA_SURF,
)

BUTTON_RECTS = [surf.get_rect() for surf in BUTTON_SURFS]

BUTTON_CALLABLE_NAMES = (
    "select_new_paths",
    "preview_paths",
)


###
BUTTON_RECTS[0].topleft = (1, 1)
BUTTON_RECTS[1].topleft = BUTTON_RECTS[0].move(1, 0).topright

### svg representation of buttons

BUTTON_SVG_REPRS = [
    ## folder icon
    [
        (
            (
                " m2 1"
                " m0 3"
                " q0 -3 3 -3"
                " l3 0"
                " q3 0 3 3"
                " l0 12"
                " q0 3 -3 3"
                " l-3 0"
                " q-3 0 -3 -3"
                " l0 -12"
                " Z"
            ),
            "fill:rgb(30, 130, 70);stroke:black;stroke-width:2;",
        ),
        (
            (
                " m2 1"
                " m0 10"
                " l0 -3"
                " q0 -3 3 -3"
                " l11 0"
                " q3 0 3 3"
                " q0 3 -3 3"
                " l-4 0"
                " q-2 0 -2 2"
                " q0 2 -2 2"
                " l-3 0"
                " q-3 0 -3 -3"
                " Z"
            ),
            "fill:rgb(30, 130, 70);stroke:black;stroke-width:2;",
        ),
        (
            (
                "m2 1"
                "m0 10"
                " l0 5"
                " q0 3 3 3"
                " l11 0"
                " q3 0 3 -3"
                " l0 -9"
                " q0 3 -3 3"
                " l-4 0"
                " q-2 0 -2 2"
                " q0 2 -2 2"
                " l-3 0"
                " q-3 0 -3 -3"
                " Z"
            ),
            "fill:rgb(30, 130, 70);stroke:black;stroke-width:2;",
        ),
    ],
    ## dummy media icon
    [
        (
            "m1 1 l18 0 l0 18 l-18 0 l0 -18",
            "fill:grey;",
        )
    ],
]


############

ARROW_UP = render_layered_icon(
    chars=[chr(ordinal) for ordinal in (52, 53)],
    dimension_name="width",
    dimension_value=18,
    colors=[BLACK, (30, 130, 70)],
    background_width=20,
    background_height=20,
    retrieve_pos_from="midbottom",
    assign_pos_to="midbottom",
    offset_pos_by=(0, -2),
)

ARROW_DOWN = rotate_surface(ARROW_UP, 180)

RELOAD_BUTTON_SURF = combine_surfaces(
    [ARROW_UP, ARROW_DOWN], retrieve_pos_from="center", assign_pos_to="center"
)


SP_BUTTON_SURFS = [
    *BUTTON_SURFS,
    RELOAD_BUTTON_SURF,
]

SP_BUTTON_RECTS = [
    *BUTTON_RECTS,
    # TODO fix positioning of rect below
    RELOAD_BUTTON_SURF.get_rect().move(BUTTON_RECTS[1].move(90, 0).topright),
]

SP_BUTTON_CALLABLE_NAMES = [
    *BUTTON_CALLABLE_NAMES,
    "update_previews",
]

SP_BUTTON_SVG_REPRS = [
    *BUTTON_SVG_REPRS,
    [
        (
            (
                " m 2  1"
                " m 0  6"
                " l 0 -3"
                " q 0 -3 3 -3"
                " l 8  0"
                " q 3  0 3 3"
                " l 0  4"
                " l 3  0"
                " l-5  4"
                " l-5 -4"
                " l 3  0"
                " l 0 -4"
                " l-6  0"
                " l 0  3"
                " Z"
            ),
            "fill:rgb(30, 130, 70);stroke:black;stroke-width:2;stroke-linejoin:round;",
        ),
        (
            (
                " m 0   1"
                " m 0  11"
                " l 5  -4"
                " l 5   4"
                " l-3   0"
                " l 0   4"
                " l 6   0"
                " l 0  -3"
                " l 4   0"
                " l 0   3"
                " q 0   3  -3  3"
                " l-8   0"
                " q-3   0  -3 -3"
                " l 0  -4"
                " Z"
            ),
            "fill:rgb(30, 130, 70);stroke:black;stroke-width:2;stroke-linejoin:round;",
        ),
    ],
]

##


def get_missing_path_repr(rect):

    g = Element("g", {"class": "file_not_found_shapes"})

    g.append(
        Element(
            "rect",
            {
                **{
                    attr_name: str(getattr(rect, attr_name))
                    for attr_name in ("x", "y", "width", "height")
                },
            },
        ),
    )

    ellipse_rect = rect.inflate(-16, -16)

    g.append(
        Element(
            "ellipse",
            {
                "cx": str(ellipse_rect.centerx),
                "cy": str(ellipse_rect.centery),
                "rx": str(ellipse_rect.width // 2),
                "ry": str(ellipse_rect.height // 2),
            },
        ),
    )

    slash_rect = rect.inflate(-60, -60)

    p1 = slash_rect.bottomleft
    p2 = slash_rect.topright

    g.append(
        Element(
            "line",
            {
                **{
                    key: value
                    for key, value in (
                        zip(
                            ("x1", "y1"),
                            map(str, p1),
                        )
                    )
                },
                **{
                    key: value
                    for key, value in (
                        zip(
                            ("x2", "y2"),
                            map(str, p2),
                        )
                    )
                },
            },
        ),
    )

    return g
