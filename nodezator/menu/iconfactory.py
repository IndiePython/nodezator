"""Common icon surfaces for the menu manager subpackage."""

### local imports

from ..surfsman.icon import render_layered_icon

from ..surfsman.render import combine_surfaces

from ..fontsman.constants import ENC_SANS_BOLD_FONT_PATH

from ..imagesman.cache import IMAGE_SURFS_DB

from ..colorsman.colors import (
    BLACK,
    WHITE,
    NODE_BODY_BG,
    NODE_CATEGORY_COLORS,
    TEXT_BLOCK_OUTLINE,
)

from ..graphman.textblock.surf import COMMENT_THEME_MAP

TEXT_BLOCK_BG = COMMENT_THEME_MAP["background_color"]

TEXT_BLOCK_FG = COMMENT_THEME_MAP["text_settings"]["normal"]["foreground_color"]


### below we create icon surfaces and at the bottom we
### store them within an icon map

FOLDER_ICON = render_layered_icon(
    chars=[chr(ordinal) for ordinal in (33, 34)],
    dimension_name="height",
    dimension_value=20,
    colors=[BLACK, (30, 130, 70)],
    background_width=27,
    background_height=27,
)

NATIVE_FILE_ICON = render_layered_icon(
    chars=[chr(ordinal) for ordinal in (183, 184, 185)],
    dimension_name="width",
    dimension_value=22,
    colors=[BLACK, WHITE, (77, 77, 105)],
    background_width=27,
    background_height=27,
)

PLUS_MINI_SURF = render_layered_icon(
    chars=[chr(ordinal) for ordinal in (79, 80)],
    dimension_name="height",
    dimension_value=12,
    colors=[BLACK, (80, 220, 120)],
)

NEW_NATIVE_FILE_ICON = combine_surfaces(
    [NATIVE_FILE_ICON, PLUS_MINI_SURF],
    retrieve_pos_from="bottomright",
    assign_pos_to="bottomright",
)

IMAGE_ICON = render_layered_icon(
    chars=[chr(ordinal) for ordinal in (38, 40, 41, 39)],
    dimension_name="height",
    dimension_value=20,
    colors=[BLACK, BLACK, WHITE, (30, 130, 70)],
    background_width=27,
    background_height=27,
)

EXECUTE_ICON = render_layered_icon(
    chars=[chr(ordinal) for ordinal in range(186, 190)],
    dimension_name="height",
    dimension_value=20,
    colors=[BLACK, BLACK, WHITE, (30, 130, 70)],
    background_width=27,
    background_height=27,
)

_TEXT_ICON = render_layered_icon(
    chars=[chr(ordinal) for ordinal in (37, 36)],
    dimension_name="height",
    dimension_value=20,
    colors=[BLACK, WHITE],
    background_width=27,
    background_height=27,
)

_SMALL_PENCIL_ICON = render_layered_icon(
    chars=[chr(ordinal) for ordinal in range(115, 119)],
    dimension_name="height",
    dimension_value=14,
    colors=[BLACK, (255, 225, 140), (255, 255, 0), (255, 170, 170)],
)

TEXT_EDITING_ICON = combine_surfaces(
    [_TEXT_ICON, _SMALL_PENCIL_ICON],
    retrieve_pos_from="bottomright",
    assign_pos_to="bottomright",
    offset_pos_by=(-2, -2),
)

_SMALL_EYE_ICON = render_layered_icon(
    chars=[chr(ordinal) for ordinal in (87, 88, 89)],
    dimension_name="height",
    dimension_value=14,
    colors=[BLACK, WHITE, (115, 40, 30)],
)

_SMALL_TEXT_ICON = render_layered_icon(
    chars=[chr(ordinal) for ordinal in (37, 36)],
    dimension_name="height",
    dimension_value=14,
    colors=[BLACK, WHITE],
)

EXECUTE_WITH_TEXT_ICON = combine_surfaces(
    [EXECUTE_ICON, _SMALL_TEXT_ICON],
    retrieve_pos_from="bottomright",
    assign_pos_to="bottomright",
)


PYTHON_ICON = IMAGE_SURFS_DB["python_menu_icon.png"][{"use_alpha": True}]

PYTHON_VIEWING_ICON = combine_surfaces(
    [PYTHON_ICON, _SMALL_EYE_ICON],
    retrieve_pos_from="bottomright",
    assign_pos_to="bottomright",
)

INFO_ICON = render_layered_icon(
    chars=[chr(ordinal) for ordinal in (167, 63, 64, 168)],
    dimension_name="height",
    dimension_value=19,
    colors=[BLACK, BLACK, WHITE, (30, 130, 70)],
    background_width=27,
    background_height=27,
)

QUESTION_MARK = render_layered_icon(
    chars=[chr(ordinal) for ordinal in (167, 92, 93, 168)],
    dimension_name="height",
    dimension_value=19,
    colors=[BLACK, BLACK, WHITE, (30, 130, 70)],
    background_width=27,
    background_height=27,
)

ARROW_DOWN_ICON = render_layered_icon(
    chars=[chr(ordinal) for ordinal in (50, 51)],
    dimension_name="height",
    dimension_value=15,
    rotation_degrees=180,
    colors=[
        BLACK,
        (30, 130, 70),
    ],
)

SSD_ICON = render_layered_icon(
    chars=[chr(ordinal) for ordinal in range(83, 87)],
    dimension_name="width",
    dimension_value=20,
    colors=[
        BLACK,
        (255, 0, 0),
        (0, 0, 255),
        (140, 140, 140),
    ],
    background_width=27,
    background_height=27,
    retrieve_pos_from="midbottom",
    assign_pos_to="midbottom",
    offset_pos_by=(0, -2),
)

SAVE_ICON = combine_surfaces(
    [SSD_ICON, ARROW_DOWN_ICON],
    retrieve_pos_from="midbottom",
    assign_pos_to="midbottom",
    offset_pos_by=(0, -10),
)

SAVE_AS_ICON = combine_surfaces(
    [SAVE_ICON, PLUS_MINI_SURF],
    retrieve_pos_from="midright",
    assign_pos_to="midright",
    offset_pos_by=(0, -6),
)

QUIT_ICON = render_layered_icon(
    chars=[chr(ordinal) for ordinal in (190, 191)],
    dimension_name="width",
    dimension_value=17,
    colors=[
        BLACK,
        (200, 30, 30),
    ],
    background_width=27,
    background_height=27,
)

TOOLS_ICON = render_layered_icon(
    chars=[chr(ordinal) for ordinal in (192, 193, 194)],
    dimension_name="width",
    dimension_value=17,
    colors=[
        BLACK,
        (215, 215, 215),
        (30, 130, 70),
    ],
    background_width=27,
    background_height=27,
)

BADGE_ICON = render_layered_icon(
    chars=[chr(ordinal) for ordinal in (56, 57, 58)],
    dimension_name="width",
    dimension_value=17,
    colors=[
        BLACK,
        (215, 215, 25),
        (200, 30, 30),
    ],
    background_width=27,
    background_height=27,
)

TEXT_BLOCK_ICON = render_layered_icon(
    chars=[chr(ordinal) for ordinal in (180, 181, 182)],
    dimension_name="width",
    dimension_value=20,
    colors=[
        TEXT_BLOCK_OUTLINE,
        TEXT_BLOCK_FG,
        TEXT_BLOCK_BG,
    ],
    background_width=27,
    background_height=27,
)

NEW_TEXT_BLOCK_ICON = combine_surfaces(
    [TEXT_BLOCK_ICON, PLUS_MINI_SURF],
    retrieve_pos_from="bottomright",
    assign_pos_to="bottomright",
)

DATA_NODE_ICON = render_layered_icon(
    chars=[chr(ordinal) for ordinal in range(195, 199)],
    dimension_name="width",
    dimension_value=20,
    colors=[
        BLACK,
        WHITE,
        (60, 60, 80),
        WHITE,
    ],
    background_width=27,
    background_height=27,
)

NEW_DATA_NODE_ICON = combine_surfaces(
    [DATA_NODE_ICON, PLUS_MINI_SURF],
    retrieve_pos_from="bottomright",
    assign_pos_to="bottomright",
)


REDIRECT_NODE_ICON = render_layered_icon(
    chars=[chr(ordinal) for ordinal in (199, 196, 197)],
    dimension_name="width",
    dimension_value=20,
    colors=[
        BLACK,
        WHITE,
        (60, 60, 80),
    ],
    background_width=27,
    background_height=27,
)

NEW_REDIRECT_NODE_ICON = combine_surfaces(
    [
        REDIRECT_NODE_ICON,
        PLUS_MINI_SURF,
    ],
    retrieve_pos_from=("bottomright"),
    assign_pos_to=("bottomright"),
)

OPERATIONS_ICON = render_layered_icon(
    chars=[chr(ordinal) for ordinal in (38, 200, 39)],
    dimension_name="width",
    dimension_value=22,
    colors=[BLACK, BLACK, WHITE],
    background_width=27,
    background_height=27,
)


WEB_ICON = render_layered_icon(
    chars=[chr(ordinal) for ordinal in (90, 91)],
    dimension_name="height",
    dimension_value=17,
    colors=[BLACK, (0, 100, 255)],
    background_width=27,
    background_height=27,
)

AWW_ICON = render_layered_icon(
    chars=[chr(ordinal) for ordinal in (90, 91)],
    dimension_name="height",
    dimension_value=17,
    colors=[BLACK, (30, 150, 80)],
    background_width=27,
    background_height=27,
)

DELETE_ICON = render_layered_icon(
    chars=[chr(ordinal) for ordinal in (65, 66)],
    dimension_name="height",
    dimension_value=19,
    colors=[BLACK, (215, 0, 0)],
    rotation_degrees=-90,
    background_width=27,
    background_height=27,
)

PENCIL_ICON = render_layered_icon(
    chars=[chr(ordinal) for ordinal in range(115, 119)],
    dimension_name="height",
    dimension_value=21,
    colors=[BLACK, (255, 225, 140), (255, 255, 0), (255, 170, 170)],
    background_width=27,
    background_height=27,
)

MOVING_ICON = render_layered_icon(
    chars=[chr(ordinal) for ordinal in (50, 51)],
    dimension_name="height",
    dimension_value=19,
    colors=[BLACK, (30, 130, 70)],
    rotation_degrees=-90,
    background_width=27,
    background_height=27,
)

(_green_square, _blue_square,) = (
    render_layered_icon(
        chars=[chr(ordinal) for ordinal in (38, 39)],
        dimension_name="height",
        dimension_value=20,
        colors=[BLACK, fill_color],
        background_width=23,
        background_height=23,
    )
    for fill_color in (
        (30, 130, 70),
        (30, 70, 130),
    )
)

DUPLICATION_ICON = combine_surfaces(
    [_green_square, _blue_square],
    retrieve_pos_from="center",
    assign_pos_to="center",
    offset_pos_by=(4, 4),
)

HASH_ICON = render_layered_icon(
    chars=["#"],
    font_path=ENC_SANS_BOLD_FONT_PATH,
    dimension_name="height",
    dimension_value=19,
    colors=[WHITE],
    background_width=27,
    background_height=27,
)

### icon map

ICON_MAP = {
    "folder": FOLDER_ICON,
    "new_native_file": NEW_NATIVE_FILE_ICON,
    "save": SAVE_ICON,
    "save_as": SAVE_AS_ICON,
    "image": IMAGE_ICON,
    "python": PYTHON_ICON,
    "execute": EXECUTE_ICON,
    "execute_with_text": EXECUTE_WITH_TEXT_ICON,
    "quit": QUIT_ICON,
    "tools": TOOLS_ICON,
    "badge": BADGE_ICON,
    "text_block": TEXT_BLOCK_ICON,
    "new_text_block": NEW_TEXT_BLOCK_ICON,
    "data_node": DATA_NODE_ICON,
    "new_data_node": NEW_DATA_NODE_ICON,
    "operations": OPERATIONS_ICON,
    "redirect_node": REDIRECT_NODE_ICON,
    "new_redirect_node": NEW_REDIRECT_NODE_ICON,
    "info": INFO_ICON,
    "question": QUESTION_MARK,
    "web_icon": WEB_ICON,
    "aww_icon": AWW_ICON,
    "text_editing": TEXT_EDITING_ICON,
    "python_viewing": PYTHON_VIEWING_ICON,
    "moving": MOVING_ICON,
    "duplication": DUPLICATION_ICON,
    "delete": DELETE_ICON,
    "pencil": PENCIL_ICON,
    "hash": HASH_ICON,
}


## more icons defined below and inserted
## into the map

for (index, node_category_color) in enumerate(NODE_CATEGORY_COLORS):

    surf = render_layered_icon(
        chars=[chr(ordinal) for ordinal in (177, 178, 179)],
        dimension_name="height",
        dimension_value=20,
        colors=[
            BLACK,
            node_category_color,
            NODE_BODY_BG,
        ],
        background_width=27,
        background_height=27,
    )

    key = "color_index_" + str(index) + "_node"
    ICON_MAP[key] = surf

    ##

    new_key = "new_" + key
    new_surf = combine_surfaces(
        [surf, PLUS_MINI_SURF],
        retrieve_pos_from="bottomright",
        assign_pos_to="bottomright",
    )

    ICON_MAP[new_key] = new_surf
