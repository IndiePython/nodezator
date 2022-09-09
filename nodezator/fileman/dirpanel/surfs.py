"""Common surfaces for the file manager directory panel."""

### third-party import
from pygame.transform import rotate as rotate_surface


### local imports

from ...surfsman.icon import render_layered_icon

from ...surfsman.render import combine_surfaces

from ...colorsman.colors import BLACK


HOME_BUTTON_SURF = render_layered_icon(
    chars=[chr(ordinal) for ordinal in (48, 49)],
    dimension_name="height",
    dimension_value=22,
    colors=[BLACK, (30, 130, 70)],
    background_width=24,
    background_height=24,
)


ARROW_UP = render_layered_icon(
    chars=[chr(ordinal) for ordinal in (52, 53)],
    dimension_name="width",
    dimension_value=22,
    colors=[BLACK, (30, 130, 70)],
    background_width=24,
    background_height=24,
    retrieve_pos_from="midbottom",
    assign_pos_to="midbottom",
    offset_pos_by=(0, -2),
)

ARROW_DOWN = rotate_surface(ARROW_UP, 180)

RELOAD_DIR_BUTTON_SURF = combine_surfaces(
    [ARROW_UP, ARROW_DOWN], retrieve_pos_from="center", assign_pos_to="center"
)


PARENT_BUTTON_SURF = render_layered_icon(
    chars=[chr(ordinal) for ordinal in (50, 51)],
    dimension_name="height",
    dimension_value=22,
    colors=[BLACK, (30, 130, 70)],
    background_width=24,
    background_height=24,
)


FOLDER_ICON = render_layered_icon(
    chars=[chr(ordinal) for ordinal in (33, 34)],
    dimension_name="height",
    dimension_value=22,
    colors=[BLACK, (30, 130, 70)],
    background_width=24,
    background_height=24,
)

FILE_ICON = render_layered_icon(
    chars=[chr(ordinal) for ordinal in (35, 36)],
    dimension_name="height",
    dimension_value=21,
    colors=[BLACK, (30, 130, 70)],
    background_width=24,
    background_height=24,
)

PLUS_MINI_SURF = render_layered_icon(
    chars=[chr(ordinal) for ordinal in (79, 80)],
    dimension_name="height",
    dimension_value=14,
    colors=[BLACK, (80, 220, 120)],
)


NEW_FOLDER_BUTTON_SURF = combine_surfaces(
    [FOLDER_ICON, PLUS_MINI_SURF],
    retrieve_pos_from="bottomright",
    assign_pos_to="bottomright",
)

NEW_FILE_BUTTON_SURF = combine_surfaces(
    [FILE_ICON, PLUS_MINI_SURF],
    retrieve_pos_from="bottomright",
    assign_pos_to="bottomright",
)
