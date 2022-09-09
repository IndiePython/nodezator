### standard library import
from functools import partial


### local imports

from ...textman.render import render_text

from ...surfsman.draw import draw_border
from ...surfsman.render import render_rect

from ...surfsman.icon import render_layered_icon

from .constants import (
    FONT_HEIGHT,
    HEADER_HEIGHT,
    MAX_WIDTH,
    NODE_OUTLINE_THICKNESS,
)

from ...ourstdlibs.collections.general import FactoryDict

from ...colorsman.colors import (
    PROXY_NODE_NORMAL_BG,
    PROXY_NODE_NORMAL_FG,
    PROXY_NODE_NORMAL_OUTLINE,
    PROXY_NODE_COMMENTED_OUT_BG,
    PROXY_NODE_COMMENTED_OUT_FG,
    PROXY_NODE_COMMENTED_OUT_OUTLINE,
    PROXY_NODE_WIDGET_ADD_BUTTON_FILL,
    PROXY_NODE_WIDGET_ADD_BUTTON_OUTLINE,
    PROXY_NODE_WIDGET_REMOVE_BUTTON_FILL,
    PROXY_NODE_WIDGET_REMOVE_BUTTON_OUTLINE,
)


### general map to store colored surfaces with outlines,
### used for header reuse

## factory function for map


def get_header_surface(tuple_args):

    ##

    width, commented_out = tuple_args

    (background_color, outline_color) = (
        (
            PROXY_NODE_COMMENTED_OUT_BG,
            PROXY_NODE_COMMENTED_OUT_OUTLINE,
        )
        if commented_out
        else (
            PROXY_NODE_NORMAL_BG,
            PROXY_NODE_NORMAL_OUTLINE,
        )
    )

    ##

    surf = render_rect(
        width,
        HEADER_HEIGHT,
        background_color,
    )

    draw_border(
        surf,
        outline_color,
        thickness=NODE_OUTLINE_THICKNESS,
    )

    return surf


HEADER_SURF_MAP = FactoryDict(get_header_surface)

###


def get_label_surface(tuple_args):

    text, commented_out = tuple_args

    (foreground_color, background_color) = (
        (
            PROXY_NODE_COMMENTED_OUT_FG,
            PROXY_NODE_COMMENTED_OUT_BG,
        )
        if commented_out
        else (
            PROXY_NODE_NORMAL_FG,
            PROXY_NODE_NORMAL_BG,
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


### add/remove buttons' surfaces

ADD_BUTTON_SURF, REMOVE_BUTTON_SURF = (
    render_layered_icon(
        chars=[chr(ordinal) for ordinal in ordinals],
        dimension_name="width",
        dimension_value=18,
        colors=colors,
        background_width=18,
        background_height=18,
    )
    for ordinals, colors in (
        (
            (79, 80),
            (
                PROXY_NODE_WIDGET_ADD_BUTTON_OUTLINE,
                PROXY_NODE_WIDGET_ADD_BUTTON_FILL,
            ),
        ),
        (
            (125, 126),
            (
                PROXY_NODE_WIDGET_REMOVE_BUTTON_OUTLINE,
                PROXY_NODE_WIDGET_REMOVE_BUTTON_FILL,
            ),
        ),
    )
)
