"""Facility for commonly used constants and tools.

### Note about font height

For font_height values exceedingly big, the menu manager
might not behave appropriately or even when it does it might
be difficult to pick menu items on the screen. This is due to
clamping issues.

Clamping is the operation of keeping a rectangle within
another rectangle, in this case the menu inside the
screen or whichever boundaries you set for the menu.

With extremely big values, clamping becomes difficult to
handle. This doesn't make the application crash nor makes
it slow. It just makes the menu items hard to place on the
screen.

There's no need to worry about it though, since, as I said,
this just applies to really big and unreasonable font height
values, like font heights above 113, which I've never seen
used for any menu in any application.

I even managed to use the menu with font heights bigger than
113, when stress testing, but it also depends on the length
of individual labels and structure of the menu. And, of
course, I'll say it again, I can't imagine the need to use
a font height that big.

I'd say the ideal would be to keep the menu between font
height 17 and 26. My favorite setting is font height 17.
However, the ideal value also depends on the font used
and the user's preference/need.
"""

### local imports

from ..ourstdlibs.mathutils import get_straight_distance

from ..fontsman.constants import (
    ENC_SANS_BOLD_FONT_HEIGHT,
    ENC_SANS_BOLD_FONT_PATH,
)

from ..surfsman.icon import render_layered_icon

from ..colorsman.colors import (
    MENU_FG,
    MENU_BG,
    MENU_HOVERED_FG,
    MENU_HOVERED_BG,
)


### common constants to render menu items' labels

# XXX ponder about dependency between font height
# and padding and how the switch will make the label
# below the separator on the window manager behave;
#
# see to it when convenient, so users can change the
# menu font/font height/padding without having to
# worry about changing other values elsewhere

FONT_SIZE_KWARGS = {
    # see module docstring about font height
    "font_height": ENC_SANS_BOLD_FONT_HEIGHT,
    "font_path": ENC_SANS_BOLD_FONT_PATH,
    "padding": 5,
}

NORMAL_LABEL_KWARGS = {
    **FONT_SIZE_KWARGS,
    "foreground_color": MENU_FG,
    "background_color": MENU_BG,
}

HOVERED_LABEL_KWARGS = {
    **FONT_SIZE_KWARGS,
    "foreground_color": MENU_HOVERED_FG,
    "background_color": MENU_HOVERED_BG,
}


### surfaces representing arrows pointing in horizontal
### directions;
###
### their height must be the height of the label of a
### menu item, that is, the font height plus two times
### the text padding (to account for the padding added
### above and below, since the padding is applied in all
### sides of the surfaces);
###
### the width can be any value, so we arbitrarily chose
### a proportion of the height which we think looks good;
###
### the right and left arrows serve as a buttons to scroll
### horizontal menus;
###
### the right arrow is also draw at the right side of
### submenus to indicate they are submenus (so they
### aren't confused with commands);
###
### we only need a hovered version of the right arrow,
### since it is used with the labels, which have hovered
### versions for their 'highlighted' state


## create the arrows

(LEFT_ARROW_SURF, RIGHT_ARROW_SURF, HOVERED_RIGHT_ARROW_SURF,) = (
    render_layered_icon(
        chars=[chr(82)],
        dimension_name="height",
        dimension_value=8,
        padding=NORMAL_LABEL_KWARGS["padding"],
        colors=[fg_color],
        background_width=NORMAL_LABEL_KWARGS["font_height"],
        background_height=NORMAL_LABEL_KWARGS["font_height"],
        background_color=bg_color,
        rotation_degrees=90,
        flip_x=flip_x,
    )
    for (fg_color, bg_color, flip_x,) in (
        (
            MENU_FG,
            MENU_BG,
            False,
        ),
        (
            MENU_FG,
            MENU_BG,
            True,
        ),
        (
            MENU_HOVERED_FG,
            MENU_HOVERED_BG,
            True,
        ),
    )
)


### create surfaces representing arrows pointing in vertical
### directions;
###
### for the height we pick the icon width previously used,
### so the arrows are more or less proportional to the
### horizonal arrows and in general this value just looks
### good;
###
### the width is not so important here because the actual
### up and arrow surfaces used are in reality enlarged
### copies which account for the different width of the
### menu/submenu body where they are positioned, due to the
### body adjusting to the width of its items

## create the arrows

(UP_ARROW_SURF, DOWN_ARROW_SURF) = (
    render_layered_icon(
        chars=[chr(82)],
        dimension_name="height",
        dimension_value=8,
        padding=5,
        colors=[MENU_FG],
        background_color=MENU_BG,
        flip_y=flip_y,
    )
    for flip_y in (False, True)
)


### calculate a scroll speed proportional to the left arrow
### height

### XXX this speed must account for the value of the FPS
### used;
###
### also, there should probably be two scroll speeds
### defined, depending on the orientation of the scrolling;
### ponder;

factor = 0.35  # arbitrary value
SCROLL_SPEED = round(LEFT_ARROW_SURF.get_height() * factor)


### utility function

## rect attribute names representing points (2d positions)

RECT_ATTR_NAMES = (
    "center",
    "midtop",
    "topright",
    "midright",
    "bottomright",
    "midbottom",
    "bottomleft",
    "midleft",
    "topleft",
)

## function definition


def get_nearest_attr_name(pos, rect):
    """Return the rect's attribute name nearest to position.

    This function is used to reposition pop up menus aligned
    in relation to the nearest points (corners or midpoints)
    of the area whose boundaries they respect (this area is
    usually the screen itself, but the user may have
    specified a different area upon instantiation of the
    menu).

    Parameters
    ==========

    pos (2-tuple of integers)
        represents a position in 2d space, the values of
        the x and y axes, respectively.

    rect (pygame.Rect instance)
        represent the area wherein the position is located.
    """

    ### iterate over each attribute name, calculating the
    ### distance of each respective point from the position
    ### in the 'pos' variable; such distance and attribute
    ### name must be gathered together as a tuple and
    ### appended to a list

    ## create list to hold tuples
    distance_attr_pairs = []

    for attr_name in RECT_ATTR_NAMES:

        ## get distance

        distance = get_straight_distance(getattr(rect, attr_name), pos)

        ## create and append tuple with distance and
        ## attribute name
        distance_attr_pairs.append((distance, attr_name))

    ### get pair with smaller distance from pos, that is,
    ### the nearest point
    pair = min(distance_attr_pairs)

    ### return the attr name (index 1)
    return pair[1]
