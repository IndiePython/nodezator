### standard library imports

from functools import partial
from collections import defaultdict


### third-party import
from pygame import Rect


### local imports

from ...ourstdlibs.collections.general import FactoryDict

from ...classes2d.single import Object2D
from ...classes2d.collections import List2D

from ...fontsman.constants import ENC_SANS_BOLD_FONT_PATH

from ...textman.render import render_text

from ...rectsman.main import RectsManager

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
    NORMAL_PARAMETER_TEXT_SETTINGS,
    COMMENTED_OUT_PARAMETER_TEXT_SETTINGS,
    NODE_OUTLINE_THICKNESS,
    RIGHT_PADDING,
    DY_BETWEEN_INPUT_SOCKETS,
    DX_BETWEEN_PARAMS_AND_CHARS,
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

PARAM_DYS_FROM_TOP = {}


_get_socket_rect = partial(Rect, (0, 0, SOCKET_DIAMETER, SOCKET_DIAMETER))
TEMP_RECT_MAP = defaultdict(_get_socket_rect)

TEMP_RECT_LIST = []
TEMP_RECTSMAN =  RectsManager(TEMP_RECT_LIST.__iter__)


def get_node_surface(
    string_mode_pair,
    char_fg,
    operation_char_fg,
    bg_color,
    outline_color,
    param_text_settings,
):

    ### retrieve the individual values in the pair
    string, mode_name = string_mode_pair

    ### create the big characters that are displayed in the node's body

    char_objs = List2D(

        ##

        Object2D.from_surface(

            ### if the flag is on

            render_text(
                text=char,
                font_height=AB_CHARS_HEIGHT,
                font_path=ENC_SANS_BOLD_FONT_PATH,
                foreground_color=char_fg,
            )
            if flag

            ### otherwise

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

        ## data
        for char, flag in zip(string, CHAR_FILTERING_MAP[string])

        ## condition
        if char != " "

    )

    ### position the big characters relative to each other

    char_objs.rect.snap_rects_ip(
        retrieve_pos_from="bottomright",
        assign_pos_to="bottomleft",
        offset_pos_by=(2, 0),
    )

    ### define width of area wherein the parameters are to be
    ### blitted (if they are not, the width is zero)
    param_area_width = 0 if mode_name == 'callable' else PARAM_AREA_WIDTH

    ### define height of parameter area depending on mode

    if mode_name == 'expanded_signature':

        params = [char for char, flag in zip(string, CHAR_FILTERING_MAP[string]) if flag]

        TEMP_RECT_LIST.clear()

        TEMP_RECT_LIST.extend(
            TEMP_RECT_MAP[index]
            for index, _ in enumerate(params)
        )

        TEMP_RECTSMAN.snap_rects_ip(
            retrieve_pos_from="midbottom",
            assign_pos_to="midtop",
            offset_pos_by=(0, DY_BETWEEN_INPUT_SOCKETS),
        )

        ###
        param_area_height = max(char_objs.rect.height, TEMP_RECTSMAN.height)

    else:
        param_area_height = char_objs.rect.height

    ###

    param_area_surf = render_rect(
        param_area_width,
        param_area_height,
        color=bg_color,
    )

    ###

    id_label_area_width = char_objs.rect.width + param_area_width

    id_label_area_surf = render_rect(
        id_label_area_width,
        LABEL_AREA_HEIGHT,
        color=bg_color,
    )
    ###

    right_padding_surf = render_rect(RIGHT_PADDING, 2, color=bg_color)
    right_padding_area = right_padding_surf.get_rect()

    ###

    param_area_rect = param_area_surf.get_rect()
    id_label_area_rect = id_label_area_surf.get_rect()

    param_area_rect.topleft = id_label_area_rect.bottomleft

    dx = DX_BETWEEN_PARAMS_AND_CHARS
    char_objs.rect.midleft = param_area_rect.move(dx, 0).midright

    right_padding_area.midleft = char_objs.rect.midright

    surf = unite_surfaces(
        [
            (id_label_area_surf, id_label_area_rect),
            (param_area_surf, param_area_rect),
            *((obj.image, obj.rect) for obj in char_objs),
            (right_padding_surf, right_padding_area),
        ],
        padding=NODE_OUTLINE_THICKNESS + 2,
        background_color=bg_color,
    )

    draw_border(
        surf,
        color=outline_color,
        thickness=NODE_OUTLINE_THICKNESS,
    )

    node_rect = surf.get_rect()

    CHAR_CENTERXS_MAP[string_mode_pair] = [obj.rect.centerx for obj in char_objs]

    ###

    if mode_name == 'expanded_signature':

        ###
        TEMP_RECTSMAN.centery = param_area_rect.centery

        dys = PARAM_DYS_FROM_TOP[string] = []

        ###

        for rect, char in zip(TEMP_RECT_LIST, params):

            dys.append(rect.centery)

            text_obj = Object2D.from_surface(
                render_text(
                    text=char,
                    **param_text_settings,
                )
            )

            text_obj.rect.midleft = (PARAM_X_PADDING, rect.centery)

            surf.blit(text_obj.image, text_obj.rect)

    ###
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
