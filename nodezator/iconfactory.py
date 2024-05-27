"""Common icon surfaces for the whole package."""

### local imports

from .surfsman.icon import render_layered_icon

from .surfsman.render import combine_surfaces

from .fontsman.constants import ENC_SANS_BOLD_FONT_PATH

from .colorsman.colors import (
    BLACK,
    WHITE,
    NODE_BODY_BG,
    COMMENTED_OUT_NODE_BG,
    NODE_CATEGORY_COLORS,
    TEXT_BLOCK_OUTLINE,
)

from .graphman.textblock.surf import COMMENT_THEME_MAP



TEXT_BLOCK_BG = COMMENT_THEME_MAP["background_color"]
TEXT_BLOCK_FG = (
    COMMENT_THEME_MAP["text_settings"]["normal"]["foreground_color"]
)


### below we create icon surfaces and at the bottom we
### store them within an icon map


IMAGE_ICON = (
    render_layered_icon(
        chars=[chr(ordinal) for ordinal in (38, 40, 41, 39)],
        dimension_name='height',
        dimension_value=20,
        colors=[BLACK, BLACK, WHITE, (30, 130, 70)],
        background_width=27,
        background_height=27,
    )
)


TEXT_BLOCK_ICON = (
    render_layered_icon(
        chars=[chr(ordinal) for ordinal in (180, 181, 182)],
        dimension_name='width',
        dimension_value=20,
        colors=[
            TEXT_BLOCK_OUTLINE,
            TEXT_BLOCK_FG,
            TEXT_BLOCK_BG,
        ],
        background_width=27,
        background_height=27,
    )
)

DATA_NODE_ICON = (
    render_layered_icon(
        chars=[chr(ordinal) for ordinal in range(195, 199)],
        dimension_name='width',
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
)

COMMENTED_OUT_DATA_NODE_ICON = (
    render_layered_icon(
        chars=[chr(ordinal) for ordinal in range(195, 199)],
        dimension_name='width',
        dimension_value=20,
        colors=[
            BLACK,
            WHITE,
            COMMENTED_OUT_NODE_BG,
            WHITE,
        ],
        background_width=27,
        background_height=27,
    )
)


PROXY_NODE_ICON = (
    render_layered_icon(
        chars=[chr(ordinal) for ordinal in (199, 196, 197)],
        dimension_name='width',
        dimension_value=20,
        colors=[
            BLACK,
            WHITE,
            (60, 60, 80),
        ],
        background_width=27,
        background_height=27,
    )
)

COMMENTED_OUT_PROXY_NODE_ICON = (
    render_layered_icon(
        chars=[chr(ordinal) for ordinal in (199, 196, 197)],
        dimension_name='width',
        dimension_value=20,
        colors=[
            BLACK,
            WHITE,
            COMMENTED_OUT_NODE_BG,
        ],
        background_width=27,
        background_height=27,
    )
)


OPERATION_NODE_ICON = (
    render_layered_icon(
        chars=[chr(ordinal) for ordinal in (38, 200, 39)],
        dimension_name='width',
        dimension_value=22,
        colors=[BLACK, BLACK, WHITE],
        background_width=27,
        background_height=27,
    )
)

COMMENTED_OUT_OPERATION_NODE_ICON = (
    render_layered_icon(
        chars=[chr(ordinal) for ordinal in (38, 200, 39)],
        dimension_name='width',
        dimension_value=22,
        colors=[BLACK, BLACK, COMMENTED_OUT_NODE_BG],
        background_width=27,
        background_height=27,
    )
)


DEFAULT_NODE_ICON = (
    render_layered_icon(
        chars=[chr(ordinal) for ordinal in (177, 178, 179)],
        dimension_name='height',
        dimension_value=20,
        colors=[
            BLACK,
            BLACK,
            NODE_BODY_BG,
        ],
        background_width=27,
        background_height=27,
    )
)

COMMENTED_OUT_DEFAULT_NODE_ICON = (
    render_layered_icon(
        chars=[chr(ordinal) for ordinal in (177, 178, 179)],
        dimension_name='height',
        dimension_value=20,
        colors=[
            BLACK,
            BLACK,
            COMMENTED_OUT_NODE_BG,
        ],
        background_width=27,
        background_height=27,
    )
)


### icon maps

ICON_MAP = {
    'image': IMAGE_ICON,
    'text_block': TEXT_BLOCK_ICON,
    'default_node': DEFAULT_NODE_ICON,
    'commented_out_default_node': COMMENTED_OUT_DEFAULT_NODE_ICON,
    'operation_node': OPERATION_NODE_ICON,
    'commented_out_operation_node': COMMENTED_OUT_OPERATION_NODE_ICON,
    'data_node': DATA_NODE_ICON,
    'commented_out_data_node': COMMENTED_OUT_DATA_NODE_ICON,
    'proxy_node': PROXY_NODE_ICON,
    'commented_out_proxy_node': COMMENTED_OUT_PROXY_NODE_ICON,
}


## more icons defined below and inserted into the map

for (index, node_category_color) in enumerate(NODE_CATEGORY_COLORS):

    surf = (
        render_layered_icon(
            chars=[chr(ordinal) for ordinal in (177, 178, 179)],
            dimension_name='height',
            dimension_value=20,
            colors=[
                BLACK,
                node_category_color,
                NODE_BODY_BG,
            ],
            background_width=27,
            background_height=27,
        )
    )

    key = f'color_index_{index}_node'
    ICON_MAP[key] = surf

    ###

    commeted_out_surf = (
        render_layered_icon(
            chars=[chr(ordinal) for ordinal in (177, 178, 179)],
            dimension_name='height',
            dimension_value=20,
            colors=[
                BLACK,
                node_category_color,
                COMMENTED_OUT_NODE_BG,
            ],
            background_width=27,
            background_height=27,
        )
    )

    ##
    ICON_MAP[f'commented_out_{key}'] = commeted_out_surf
