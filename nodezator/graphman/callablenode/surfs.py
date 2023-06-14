"""Common surfaces for nodes."""

### third-party imports

from pygame.draw import line as draw_line

from pygame.transform import rotate as rotate_surface


### local imports

from ...ourstdlibs.collections.general import FactoryDict

from ...surfsman.render import render_rect, combine_surfaces

from ...surfsman.icon import render_layered_icon

from ...surfsman.cache import NOT_FOUND_SURF_MAP

from ...fontsman.constants import FIRA_MONO_BOLD_FONT_PATH

from ...colorsman.colors import (
    NODE_BODY_BG,
    COMMENTED_OUT_NODE_BG,
    NODE_OUTLINE,
    NODE_KEYWORD_KEY_OUTLINE,
    NODE_KEYWORD_KEY_FILL,
    WIDGET_ADD_BUTTON_FILL,
    WIDGET_ADD_BUTTON_OUTLINE,
    WIDGET_REMOVE_BUTTON_FILL,
    WIDGET_REMOVE_BUTTON_OUTLINE,
    SUBP_MOVE_BUTTON_FG,
    SUBP_MOVE_BUTTON_BG,
    NODE_CATEGORY_COLORS,
    UNPACKING_ICON_COLOR,
    BLACK,
)

from .constants import (
    NODE_WIDTH,
    NODE_BODY_HEAD_HEIGHT,
    NODE_OUTLINE_THICKNESS,
)


###### create map of top corner surfaces


def get_top_corners(fill_color):
    """Create 2-tuple of top corners of given color."""

    return tuple(
        render_layered_icon(
            chars=[chr(ordinal) for ordinal in (161, 162)],
            dimension_name="height",
            dimension_value=10,
            colors=[NODE_OUTLINE, fill_color],
            background_width=8,
            background_height=8,
            flip_x=flip_x,
            flip_y=flip_y,
        )
        for flip_x, flip_y in (
            (False, False),
            (True, False),
        )
    )


TOP_CORNERS_MAP = FactoryDict(get_top_corners)


##

bottom_corner_surfs = tuple(
    render_layered_icon(
        chars=[chr(ordinal) for ordinal in (161, 162)],
        dimension_name="height",
        dimension_value=10,
        colors=[NODE_OUTLINE, fill_color],
        background_width=8,
        background_height=8,
        flip_x=flip_x,
        flip_y=flip_y,
    )
    for fill_color, flip_x, flip_y in (
        ## normal bottom corners
        (NODE_BODY_BG, False, True),
        (NODE_BODY_BG, True, True),
        ## commented out bottom corners
        (COMMENTED_OUT_NODE_BG, False, True),
        (COMMENTED_OUT_NODE_BG, True, True),
    )
)

NORMAL_BOTTOM_CORNERS = bottom_corner_surfs[:2]
COMMENTED_OUT_BOTTOM_CORNERS = bottom_corner_surfs[2:]

##
corner_width, corner_height = bottom_corner_surfs[0].get_size()


###### create map of roof surfaces (rectangle between top
###### corners)

roof_width = NODE_WIDTH - (corner_width * 2)
roof_height = corner_height


def get_node_roof(fill_color):

    roof = render_rect(roof_width, roof_height, fill_color)

    draw_line(
        roof,
        NODE_OUTLINE,
        (0, 0),
        (roof_width, 0),
        NODE_OUTLINE_THICKNESS,
    )

    return roof


NODE_ROOFS_MAP = FactoryDict(get_node_roof)


###### create map to store body head surfaces
######
###### a surf representing the head part of a node's body,
###### which has the same color of the node's roof and top
###### corners in order to look like they all are a single
###### object


def get_body_head(fill_color):

    return render_rect(NODE_WIDTH, NODE_BODY_HEAD_HEIGHT, fill_color)


BODY_HEAD_SURFS_MAP = FactoryDict(get_body_head)


###### create and store 02 foot surfaces (for when the
###### node is in a normal state or commented out)

foot_width = NODE_WIDTH - (corner_width * 2)
foot_height = corner_height

foot_surfs = (NORMAL_NODE_FOOT, COMMENTED_OUT_NODE_FOOT) = tuple(
    render_rect(foot_width, foot_height, color)
    for color in (NODE_BODY_BG, COMMENTED_OUT_NODE_BG)
)

# since line thickness is applied from top to bottom,
# we had to use a value equivalent to the foot height
# minus the thickness of the line

line_bottom = foot_height - NODE_OUTLINE_THICKNESS

line_start = (0, line_bottom)
line_end = (foot_width, line_bottom)


for surf in foot_surfs:

    draw_line(surf, NODE_OUTLINE, line_start, line_end, NODE_OUTLINE_THICKNESS)

###### create map of surfaces for sigmode toggle button


def get_button_surfs(bg_color):
    """Create 2-tuple of surfaces with given background color."""

    return tuple(

        render_layered_icon(
            chars=[chr(82)],
            dimension_name="height",
            dimension_value=8,
            colors=[(255, 255, 255)],
            background_width=10,
            background_height=10,
            offset_pos_by=(-1, -1),
            rotation_degrees=rotation_degrees,
            background_color=bg_color,
        )

        for rotation_degrees in (-180, -90)

    )


SIGMODE_TOGGLE_BUTTON_MAP = FactoryDict(get_button_surfs)


###### load and store other commonly used surfaces

### add/remove buttons' surfaces

ADD_BUTTON_SURF, REMOVE_BUTTON_SURF = (
    render_layered_icon(
        chars=[chr(ordinal) for ordinal in ordinals],
        dimension_name="height",
        dimension_value=14,
        colors=colors,
        background_width=14,
        background_height=14,
    )
    for ordinals, colors in (
        ((79, 80), (WIDGET_ADD_BUTTON_OUTLINE, WIDGET_ADD_BUTTON_FILL)),
        ((125, 126), (WIDGET_REMOVE_BUTTON_OUTLINE, WIDGET_REMOVE_BUTTON_FILL)),
    )
)


### subparameter moving buttons

(SUBP_UP_BUTTON_SURF, SUBP_DOWN_BUTTON_SURF) = (
    render_layered_icon(
        chars=[chr(82)],
        dimension_name="height",
        dimension_value=7,
        colors=[SUBP_MOVE_BUTTON_FG],
        background_width=10,
        background_height=10,
        offset_pos_by=(-1, -1),
        background_color=SUBP_MOVE_BUTTON_BG,
        flip_x=flip_x,
        flip_y=flip_y,
        depth_finish_thickness=1,
    )
    for flip_x, flip_y in (
        (False, False),
        (False, True),
    )
)

### subparameter unpacking buttons

(NORMAL_ITERABLE_UNPACKING_SURF, COMMENTED_OUT_ITERABLE_UNPACKING_SURF,) = (
    render_layered_icon(
        chars="*",
        font_path=FIRA_MONO_BOLD_FONT_PATH,
        dimension_name="height",
        dimension_value=14,
        colors=[UNPACKING_ICON_COLOR],
        background_width=16,
        background_height=16,
        background_color=bg_color,
    )
    for bg_color in (
        NODE_BODY_BG,
        COMMENTED_OUT_NODE_BG,
    )
)


(NORMAL_DICT_UNPACKING_SURF, COMMENTED_OUT_DICT_UNPACKING_SURF,) = (
    combine_surfaces(
        [
            surf,
            surf,
        ],
        background_color=bg_color,
    )
    for surf, bg_color in (
        (
            NORMAL_ITERABLE_UNPACKING_SURF,
            NODE_BODY_BG,
        ),
        (
            COMMENTED_OUT_ITERABLE_UNPACKING_SURF,
            COMMENTED_OUT_NODE_BG,
        ),
    )
)

UNPACKING_ICON_SURFS_MAP = {
    ("var_pos", False): NORMAL_ITERABLE_UNPACKING_SURF,
    ("var_pos", True): COMMENTED_OUT_ITERABLE_UNPACKING_SURF,
    ("var_key", False): NORMAL_DICT_UNPACKING_SURF,
    ("var_key", True): COMMENTED_OUT_DICT_UNPACKING_SURF,
}


### keyword key icon surf and its rect

KEYWORD_KEY_SURF = render_layered_icon(
    chars=[chr(ordinal) for ordinal in (102, 103)],
    dimension_name="height",
    dimension_value=16,
    colors=[
        NODE_KEYWORD_KEY_OUTLINE,
        NODE_KEYWORD_KEY_FILL,
    ],
    background_width=16,
    background_height=16,
)

KEYWORD_KEY_RECT = KEYWORD_KEY_SURF.get_rect()


### reload icon for preview toolbar button 

_arrow_up = render_layered_icon(
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

_arrow_down = rotate_surface(_arrow_up, 180)

RELOAD_PREVIEW_BUTTON_SURF = combine_surfaces(
    [_arrow_up, _arrow_down],
    retrieve_pos_from="center",
    assign_pos_to="center",
)

PREVIEW_PANEL_NOT_FOUND_SURFACE = NOT_FOUND_SURF_MAP[(256, 256)]
