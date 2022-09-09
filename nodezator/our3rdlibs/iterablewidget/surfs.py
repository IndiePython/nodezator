"""Common surfaces for the list widget."""

### local imports

from ...surfsman.icon import render_layered_icon

from ...colorsman.colors import (
    LIST_WIDGET_BUTTON_FG,
    LIST_WIDGET_BUTTON_BG,
    LIST_WIDGET_REMOVE_BUTTON_FG,
)


### surfaces for the list widget buttons

(MOVE_UP_BUTTON_SURF, MOVE_DOWN_BUTTON_SURF, ADD_BUTTON_SURF, REMOVE_BUTTON_SURF,) = (
    ### obtain a surface made by carefully rotating,
    ### positioning and blitting a icon surface
    ### for each set of data given in the "for loop"
    ### below
    render_layered_icon(
        chars=[chr(ordinal)],
        dimension_name="height",
        dimension_value=height,
        colors=[fg_color],
        background_width=17,
        background_height=17,
        background_color=LIST_WIDGET_BUTTON_BG,
        flip_y=flip_y,
        depth_finish_thickness=1,
    )
    ### sets of data for each surface
    for ordinal, height, fg_color, flip_y in (
        ## data for move up button surf
        (
            82,
            11,
            LIST_WIDGET_BUTTON_FG,
            False,
        ),
        ## data for move down button surf
        (
            82,
            11,
            LIST_WIDGET_BUTTON_FG,
            True,
        ),
        ## data for add button surf
        (
            78,
            13,
            LIST_WIDGET_BUTTON_FG,
            False,
        ),
        ## data for remove button surf
        (
            66,
            13,
            LIST_WIDGET_REMOVE_BUTTON_FG,
            False,
        ),
    )
)
