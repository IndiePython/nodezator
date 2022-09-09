### standard library import
from functools import partial


### local imports

from ...ourstdlibs.collections.general import FactoryDict

from ...classes2d.single import Object2D
from ...classes2d.collections import List2D

from ...fontsman.constants import ENC_SANS_BOLD_FONT_PATH

from ...textman.render import render_text

from ...surfsman.draw import draw_border
from ...surfsman.render import render_rect, unite_surfaces

from ...surfsman.icon import render_layered_icon

from ..socket.surfs import SOCKET_DIAMETER

from .constants import (
    FONT_HEIGHT,
    MAX_WIDTH,
    OPERATIONS_MAP,
    CHAR_FILTERING_MAP,
    AB_CHARS_HEIGHT,
    OP_CHARS_HEIGHT,
    LABEL_AREA_HEIGHT,
    NODE_PADDING,
    NORMAL_PARAMETER_TEXT_SETTINGS,
    COMMENTED_OUT_PARAMETER_TEXT_SETTINGS,
    NODE_OUTLINE_THICKNESS,
)

from ...colorsman.colors import (
    OPERATION_NODE_NORMAL_BG,
    OPERATION_NODE_NORMAL_FG,
    OPERATION_NODE_NORMAL_OUTLINE,
    OPERATION_NODE_NORMAL_AB_CHARS,
    OPERATION_NODE_NORMAL_OP_CHARS,
    OPERATION_NODE_COMMENTED_OUT_BG,
    OPERATION_NODE_COMMENTED_OUT_FG,
    OPERATION_NODE_COMMENTED_OUT_OUTLINE,
    OPERATION_NODE_COMMENTED_OUT_AB_CHARS,
    OPERATION_NODE_COMMENTED_OUT_OP_CHARS,
)

###

PARAM_CHAR_WIDTH = round(
    render_text(
        text="ab",
        **NORMAL_PARAMETER_TEXT_SETTINGS,
    ).get_width()
    / 2
)

PARAM_AREA_WIDTH = (SOCKET_DIAMETER // 2) + PARAM_CHAR_WIDTH

PARAM_X_PADDING = (SOCKET_DIAMETER // 2) + 2


CHAR_CENTERXS_MAP = {}


def get_node_surface(
    string,
    char_fg,
    operation_char_fg,
    bg_color,
    outline_color,
    param_text_settings,
):

    char_objs = List2D(
        Object2D.from_surface(
            render_text(
                text=char,
                font_height=AB_CHARS_HEIGHT,
                font_path=ENC_SANS_BOLD_FONT_PATH,
                foreground_color=char_fg,
            )
            if flag
            ###
            else (
                get_drawn_subsurf(
                    render_text(
                        text=char,
                        font_height=OP_CHARS_HEIGHT,
                        font_path=ENC_SANS_BOLD_FONT_PATH,
                        foreground_color=operation_char_fg,
                    )
                )
            )
        )
        for char, flag in zip(string, CHAR_FILTERING_MAP[string])
        if char != " "
    )

    char_objs.rect.snap_rects_ip(
        retrieve_pos_from="bottomright",
        assign_pos_to="bottomleft",
        offset_pos_by=(2, 0),
    )

    param_area_surf = render_rect(
        PARAM_AREA_WIDTH,
        char_objs.rect.height,
        color=bg_color,
    )

    param_area_rect = param_area_surf.get_rect()

    label_area_width = char_objs.rect.width + param_area_surf.get_width()

    label_area_surf = render_rect(
        label_area_width,
        LABEL_AREA_HEIGHT,
        color=bg_color,
    )

    label_area_rect = label_area_surf.get_rect()

    param_area_rect.topleft = label_area_rect.bottomleft
    char_objs.rect.topleft = param_area_rect.topright

    surf = unite_surfaces(
        [
            (label_area_surf, label_area_rect),
            (param_area_surf, param_area_rect),
            *((obj.image, obj.rect) for obj in char_objs),
        ],
        padding=NODE_PADDING,
        background_color=bg_color,
    )

    draw_border(
        surf,
        color=outline_color,
        thickness=NODE_OUTLINE_THICKNESS,
    )

    node_rect = surf.get_rect()

    CHAR_CENTERXS_MAP[string] = [obj.rect.centerx for obj in char_objs]

    ###

    params = [char for char, flag in zip(string, CHAR_FILTERING_MAP[string]) if flag]

    divisions = len(params) + 1
    jump_height = (node_rect.height - (LABEL_AREA_HEIGHT // 2)) // divisions

    centery = LABEL_AREA_HEIGHT + jump_height

    for char in params:

        text_obj = Object2D.from_surface(
            render_text(
                text=char,
                **param_text_settings,
            )
        )

        text_obj.rect.midleft = (PARAM_X_PADDING, centery)

        surf.blit(text_obj.image, text_obj.rect)

        centery += jump_height

    return surf


def get_drawn_subsurf(surf):
    """Remove empty upper part of operator char surf."""

    rect = surf.get_rect()
    bounding_rect = surf.get_bounding_rect()

    bounding_rect.height += rect.bottom - bounding_rect.bottom

    return surf.subsurface(bounding_rect)


get_normal_node_surface = partial(
    get_node_surface,
    char_fg=OPERATION_NODE_NORMAL_AB_CHARS,
    operation_char_fg=OPERATION_NODE_NORMAL_OP_CHARS,
    bg_color=OPERATION_NODE_NORMAL_BG,
    outline_color=OPERATION_NODE_NORMAL_OUTLINE,
    param_text_settings=NORMAL_PARAMETER_TEXT_SETTINGS,
)

get_commented_out_node_surface = partial(
    get_node_surface,
    char_fg=OPERATION_NODE_COMMENTED_OUT_AB_CHARS,
    operation_char_fg=(OPERATION_NODE_COMMENTED_OUT_OP_CHARS),
    bg_color=OPERATION_NODE_COMMENTED_OUT_BG,
    outline_color=OPERATION_NODE_COMMENTED_OUT_OUTLINE,
    param_text_settings=(COMMENTED_OUT_PARAMETER_TEXT_SETTINGS),
)

NORMAL_SURFS = FactoryDict(get_normal_node_surface)

COMMENTED_OUT_SURFS = FactoryDict(get_commented_out_node_surface)

###


def get_label_surface(tuple_args):

    text, commented_out = tuple_args

    (foreground_color, background_color) = (
        (
            OPERATION_NODE_COMMENTED_OUT_FG,
            OPERATION_NODE_COMMENTED_OUT_BG,
        )
        if commented_out
        else (
            OPERATION_NODE_NORMAL_FG,
            OPERATION_NODE_NORMAL_BG,
        )
    )

    return render_text(
        text,
        font_height=FONT_HEIGHT,
        foreground_color=foreground_color,
        background_color=background_color,
        max_width=MAX_WIDTH,
    )


LABEL_SURF_MAP = FactoryDict(get_label_surface)
