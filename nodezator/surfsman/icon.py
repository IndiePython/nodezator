"""Facility for rendering icons from fonts.

That is, here we deal with font and related data to render
text surfaces of single characters, treating such characters
as icons. No actual surfaces are returned from the
functions in this module, only the font and the bounding
rect (the cropped area occupied by the character in the text
surface).

Check this problem to understand why rendering single
characters as icons is important:

    if we wanted to render the plus sign ('+') as text, the
    resulting surface would be too tall and similar to a
    rectangle in portrait position, because it would be
    rendered as a letter; the font height we provide would
    be used for the entire surface, rather than for the
    plus sign itself.

This is why this module exists. Now we can render surfaces
containing only the icon, having control over the dimension
we desire (either 'width' or 'height') of the surface.
"""

### standard library import

from pathlib import Path
from itertools import repeat


### third-party imports

from pygame import Surface

from pygame.font import Font

from pygame.transform import (
    rotate as rotate_surface,
    flip as flip_surface,
)


### local imports

from ..fontsman.constants import ICON_FONT_PATH

from .draw import (
    draw_border,
    draw_depth_finish,
)

from ..colorsman.colors import BLACK


def render_layered_icon(
    chars,
    dimension_name="height",
    dimension_value=26,
    font_path=ICON_FONT_PATH,
    # why padding if we can control background size?
    # because sometimes we just want to increment
    # the icon dimension which we can't predict;
    # for instance, by passing...
    # dimension_name = 'height'; dimension_value = 26;
    # .. which will be the resulting width? since
    # we don't know, the padding is needed here;
    padding=0,
    antialiased=True,
    colors=[BLACK, (*BLACK, 0)],
    background_width=0,
    background_height=0,
    background_color=(*BLACK, 0),
    retrieve_pos_from="center",
    assign_pos_to="center",
    offset_pos_by=(0, 0),
    rotation_degrees=0,
    flip_x=False,
    flip_y=False,
    depth_finish_thickness=0,
    depth_finish_outset=True,
    border_thickness=0,
    border_color=BLACK,
):

    ###
    stroke_char = chars[0]

    ### retrieve the suitable font and bounding rect
    ### according to the desired style, chosen dimension
    ### and its value;
    ###
    ### the bounding rect represents the area from which
    ### to crop the character surface

    font, bounding_rect = get_objs_for_icon_rendering(
        font_path, stroke_char, dimension_name, dimension_value
    )

    ###

    char_surfs = []

    for char, color in zip(chars, repeat_last(colors)):

        full_char_surf = font.render(char, antialiased, color).convert_alpha()

        clipped_b_rect = bounding_rect.clip(full_char_surf.get_rect())

        try:

            # XXX in theory, we should use the bounding
            # rect in the Surface.subsurface() call,
            # not even needing to create this clipped
            # version; investigate why this is needed;
            #
            # sometimes when we don't use the
            # clipped bounding rect there is an exception
            # raised saying the bounding rect is out of
            # the surface boundaries;
            char_surf = full_char_surf.subsurface(clipped_b_rect)
        except ValueError:

            print(f"char ordinal is {ord(char)}")
            raise

        char_surfs.append(char_surf)

    ### background

    size = tuple(
        dimension + (padding * 2)
        for dimension in (
            background_width or bounding_rect.width,
            background_height or bounding_rect.height,
        )
    )

    ### define whether the background has transparency

    try:
        has_transparency = background_color[3] < 255
    except IndexError:
        has_transparency = False

    surf = (
        Surface(size).convert_alpha() if has_transparency else Surface(size).convert()
    )

    surf.fill(background_color)
    offset_rect = surf.get_rect().move(offset_pos_by)

    while char_surfs:

        ## get char surface and rect

        char_surf = char_surfs.pop()
        char_rect = char_surf.get_rect()

        ## position char rect

        pos = getattr(offset_rect, retrieve_pos_from)

        setattr(char_rect, assign_pos_to, pos)

        ### blit char on surf
        surf.blit(char_surf, char_rect)

    ### add other effects as requested

    ## rotation

    if rotation_degrees:
        surf = rotate_surface(surf, rotation_degrees)

    ## dimension flipping

    if flip_x or flip_y:
        surf = flip_surface(surf, flip_x, flip_y)

    ## depth finish

    if depth_finish_thickness:

        draw_depth_finish(surf, depth_finish_thickness, depth_finish_outset)

    ## border

    if border_thickness:
        draw_border(surf, border_color, border_thickness)

    ### finally, return the surf
    return surf


def get_objs_for_icon_rendering(font_path, char, dimension_name, dimension_value):
    """Return font and bounding rect for the given arguments.

    The dimension of the cropped char will be equal to the
    given one or at least as close as possible without
    surpassing it.

    The font object is a pygame.font.Font instance.

    This is achieved by trial and error, that is, by
    instantiating fonts and checking whether a cropped surf
    produced from them has the desired dimension. Such trial
    and error is quick enough as to being imperceptible.

    Parameters
    ==========
    check the docstring of the
    get_objs_for_icon_rendering function to know
    about the parameters in this function.
    """
    ### define an index to retrieve the appropriate dimension
    ### based on the dimension name

    if dimension_name == "height":
        index = 1
    elif dimension_name == "width":
        index = 0

    else:
        raise ValueError("'dimension_name' must be either 'width'" " or 'height'")

    ### define a foreground color (it can be any color)
    foreground_color = (0,) * 3

    ### utility function

    def get_size_results(font_size):

        ### create font and produce a surface with the
        ### given char, using its "render" method; the
        ### render method must not receive a background
        ### color, otherwise the bounding rect (the cropped
        ### area) would be the whole area of the surface

        font = Font(font_path, font_size)
        full_surf = font.render(char, True, foreground_color)

        ### obtain the bounding rect and the cropped char

        bounding_rect = full_surf.get_bounding_rect()

        cropped_surf = full_surf.subsurface(bounding_rect).copy()

        return (
            full_surf.get_size()[index],
            cropped_surf.get_size()[index],
            bounding_rect,
            font,
        )

    ### calculate a first size to be attempted; such size
    ### must be based on the ratio between the heights of
    ### a full surface and its cropped area

    full_dimension, cropped_dimension = get_size_results(dimension_value)[:2]

    ratio = full_dimension / cropped_dimension

    font_size = round(dimension_value * ratio)

    ### create a set to keep track of the attempted sizes
    attempted_sizes = set()

    ### create variable to store the chosen font
    chosen_font = None

    ### create variable to store highest dimension achieved
    ### which doesn't surpass the desired dimension (but
    ### can be equal)
    highest_dimension = 0

    while font_size not in attempted_sizes:

        ### grab dimension of crooped surface for given
        ### font size and also the bounding rect
        ### (the bounding rect will only be used outside
        ### the "while loop", but must be referenced here);
        ### also pick the font
        current_dimension, bounding_rect, font = get_size_results(font_size)[1:]

        ### store current font size as an attempted one since
        ### we just tried it
        attempted_sizes.add(font_size)

        ### if the dimension of the surf isn't the amount
        ### we desired, increment/decrement the font size
        ### so we can try it (if it wasn't before, since
        ### the condition to keep executing the while loop
        ### is using a size which wasn't attempted yet)

        if current_dimension != dimension_value:

            font_size += 1 if current_dimension < dimension_value else -1

        ### otherwise, since we reached a font which
        ### satisfies our dimension requirement, we can
        ### break out of the loop after storing the surf
        ### dimension as the highest achieved one and the
        ### font and bounding rect as the chosen ones

        else:

            highest_dimension = current_dimension
            chosen_font = font
            chosen_bounding_rect = bounding_rect

            break

        ### if the dimension of the text surface is higher
        ### than the ones achieved until now but still
        ### equal or below the desired amount, consider it
        ### the highest dimension achieved until now, and its
        ### font and bounding rect as the chosen ones

        if highest_dimension < current_dimension <= dimension_value:

            highest_dimension = current_dimension

            chosen_font = font
            chosen_bounding_rect = bounding_rect

    ### if the highest dimension achieved isn't the same as
    ### the desired one, raise an error to notify the user

    if dimension_value != highest_dimension:

        message = (
            f"couldn't get icon of {dimension_name}"
            f" {dimension_value} from {Path(font_path).name}"
            " font file"
        )

        raise ValueError(message)

    ### finally, return the chosen font and bounding rect
    return chosen_font, chosen_bounding_rect


### small utility


def repeat_last(iterable):
    """Yield each item, then keep yielding the last one."""
    for item in iterable:
        yield item
    yield from repeat(item)
