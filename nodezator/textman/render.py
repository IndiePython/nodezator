"""Facility for text related utilities."""

### TODO update docstring; it is far from specific enough;

### standard library import
from textwrap import wrap


### third-party import
from pygame import Surface


### local imports

from ..fontsman.cache import FONTS_DB

from ..fontsman.constants import (
    ENC_SANS_BOLD_FONT_PATH,
    ENC_SANS_BOLD_FONT_HEIGHT,
)

from ..surfsman.draw import draw_border, draw_depth_finish

from ..rectsman.main import RectsManager

from ..colorsman.colors import BLACK


def get_text_size(
    text,
    font_height=ENC_SANS_BOLD_FONT_HEIGHT,
    font_path=ENC_SANS_BOLD_FONT_PATH,
    padding=0,
):
    """Return surf size of text as if it were rendered.

    text
        Any string.
    font_height
        Integer indicating desired font height in pixels.
    font_path
        either ENC_SANS_BOLD_FONT_PATH for default font or any other key
        from the font path map found on the font.py module.
    """
    font = FONTS_DB[font_path][font_height]

    width, height = (dimension + (padding * 2) for dimension in font.size(text))

    return width, height


### XXX refactor: list and explain parameters, review
### docstring and comments


def fit_text(
    text,
    max_width,
    ommit_direction,
    font_height=ENC_SANS_BOLD_FONT_HEIGHT,
    font_path=ENC_SANS_BOLD_FONT_PATH,
    padding=0,
):
    """Return optimal text to fit max_width passed."""
    ### get font
    font = FONTS_DB[font_path][font_height]

    ### update max_width to take padding into account
    max_width += -padding * 2

    ### if text as it is fits width, then return earlier
    if not font.size(text)[0] > max_width:
        return text

    ### define the ellipsis text
    ellipsis = "\N{horizontal ellipsis}"

    ### if not even the ellipsis text fits the max width,
    ### we raise an error to indicate such.
    if font.size(ellipsis)[0] > max_width:
        raise ValueError("max_width defined is too small.")

    ### concatenate the ellipsis with the text according
    ### to the ommit_direction and also define the index
    ### from which we will repeatedly remove characters
    ### when making the text shorter

    if ommit_direction == "left":
        text = ellipsis + text
        pop_index = 1

    elif ommit_direction == "right":
        text = text + ellipsis
        pop_index = -2

    else:

        raise RuntimeError("This 'else' clause should never be reached")

    ### define a list of the characters
    char_list = list(text)

    ### iterate over the list, removing characters closer
    ### to the ellipsis; the number of iterations is equal
    ### to the number of characters minus the ellipsis

    number_of_iterations = len(text) - 1

    for _ in range(number_of_iterations):

        ## pop the char nearest to the ellipsis and
        ## join the text together

        char_list.pop(pop_index)
        text = "".join(char_list)

        ## if font width of the resulting text fits the
        ## max_width, we can leave the for loop
        if font.size(text)[0] <= max_width:
            break

    ### we finally return the text
    return text


### XXX this function could use a similar mechanism
### as the one used by the option menu widget or the
### appcommon.text.label.main.Label class, so
### that surfaces with the same settings would
### only be generated once; however, if this ends up
### being implemented, it would need an option to
### disable the behaviour, since the user may
### want to further manipulate the surface, which
### would end up making it useless for usage in
### other objects;


def render_text(
    text,
    font_height=ENC_SANS_BOLD_FONT_HEIGHT,
    font_path=ENC_SANS_BOLD_FONT_PATH,
    antialiased=True,
    padding=0,
    foreground_color=BLACK,
    background_color=(*BLACK, 0),
    depth_finish_thickness=False,
    depth_finish_outset=True,
    border_thickness=0,
    border_color=BLACK,
    max_width=0,
    ommit_direction="right",
):
    """Return surface or object representing rendered text.

    Parameters
    ==========

    text (string)
        text to be rendered.
    font_height (integer)
        integer indicating desired font height in pixels.
    font_path (string)
        represents the font to be used. Check sibling
        font.py module to see available values. In doubt,
        use ENC_SANS_BOLD_FONT_PATH for the default font.
    antialiased (boolean)
        indicates whether or not the text on the surface
        should be antialiased.
    padding (integer >= 0)
        represents extra space in pixels added on all four
        sides of the surface.
    foreground_color, background_color (sequence of integers)
        colors to be used for the font and background,
        respectively; the integers represent the values
        of the red, green and blue channels and must be in
        the range(0, 256) interval; the background color
        can optionally receive an additional integers in
        the same range, representing the alpha (transparency)
        of the background.
    depth_finish_thickness (integer, defaults to 0)
        if a positive integer is given, a finish is drawn
        around the surface in order to convey depth, and it
        is used as the thickness of such finish.
    depth_finish_outset (boolean, defaults to True)
        whether the depth you want to convey is that of an
        outset surf (True) or an inset one (False); only
        relevant if depth_finish_thickness is truthy.
    border_thickness (integer, defaults to 0)
        if a positive integer is given, a border is drawn
        around the surface and it is used as the thickness
        of such border; the color of the border is given
        by the border_color argument.
    border_color (sequence of integers)
        it represents the color of the border drawn around
        the surface if border_thickness is a positive
        integer;
    max_width (integer)
        if provided, the text surf won't assume a width
        larger than max width in pixels.
    ommit_direction (string)
        indicates edge of the text to ommit in case its
        width surpass the max_width. Values can be either
        'left' or 'right'. This is only taken into account
        if a max width different from 0 (zero) is provided.
    """
    ### retrieve the suitable font according to the desired
    ### height and style
    font = FONTS_DB[font_path][font_height]

    ### if a maximum width is required, fit the text
    ### in such width if the text surpasses it once
    ### rendered, ommiting characters in the specified
    ### direction

    if max_width:

        text = fit_text(text, max_width, ommit_direction, font_height, font_path)

    ### define whether the background has transparency

    try:
        has_transparency = background_color[3] < 255
    except IndexError:
        has_transparency = False

    ### if no padding was requested nor there's transparency
    ### in the background, just render the surf right away

    if not padding and not has_transparency:

        surf = font.render(
            text, antialiased, foreground_color, background_color
        ).convert()

    else:

        ### render the text surface without background

        text_surf = font.render(text, antialiased, foreground_color).convert_alpha()

        ### if padding was requested

        if padding:

            ## calculate new width and height

            width, height = (
                dimension + (padding * 2) for dimension in text_surf.get_size()
            )

            ## create new background surface with appropriate
            ## color according to presence of transparency

            surf = (
                Surface((width, height)).convert_alpha()
                if has_transparency
                else Surface((width, height)).convert()
            )

            surf.fill(background_color)

            ## blit text surf on new surf taking the padding
            ## into account
            surf.blit(text_surf, (padding, padding))

        ### otherwise, we assume the background has
        ### transparency and create such transparent
        ### background for our text surface

        else:

            surf = Surface(text_surf.get_size()).convert_alpha()

            surf.fill(background_color)
            surf.blit(text_surf, (0, 0))

    ### add other effects as requested

    ## if depth finish was requested...

    if depth_finish_thickness:

        draw_depth_finish(surf, depth_finish_thickness, depth_finish_outset)

    ## if a border was requested...
    if border_thickness:
        draw_border(surf, border_color, border_thickness)

    ### finally return the surf
    return surf


### TODO refactor


def render_multiline_text(
    text,
    ## same parameters as render_text()
    font_height=ENC_SANS_BOLD_FONT_HEIGHT,
    font_path=ENC_SANS_BOLD_FONT_PATH,
    antialiased=True,
    padding=0,
    foreground_color=BLACK,
    background_color=(*BLACK, 0),
    depth_finish_thickness=False,
    depth_finish_outset=True,
    border_thickness=0,
    border_color=BLACK,
    ## multiline-related parameters
    max_character_no=0,  # number of characters,
    retrieve_pos_from="bottomleft",
    assign_pos_to="topleft",
    offset_pos_by=(0, 0),
    ## extra styles
    text_padding=0,
):
    ### retrieve the suitable font according to the desired
    ### height and style
    font = FONTS_DB[font_path][font_height]

    ### split the text into multiple lines

    lines = wrap(text, max_character_no) if max_character_no else text.splitlines()

    ### define whether the background has transparency

    try:
        has_transparency = background_color[3] < 255
    except IndexError:
        has_transparency = False

    ### if no padding was requested nor there's transparency
    ### in the background, just render the surfaces right
    ### away

    if not padding and not has_transparency:

        text_surfaces = [
            font.render(
                line_text, antialiased, foreground_color, background_color
            ).convert()
            for line_text in lines
        ]

    else:

        ### render the text surface without background

        text_surfaces = [
            font.render(line_text, antialiased, foreground_color).convert_alpha()
            for line_text in lines
        ]

        ### if padding was requested

        if padding:

            ### pick surface converting method according to
            ### presence of transparence

            converting_method = (
                Surface.convert_alpha if has_transparency else Surface.convert
            )

            ### iterate over items within a copy of the
            ### text_surfaces list

            for index, text_surface in enumerate(text_surfaces[:]):

                ## calculate new width and height

                width, height = (
                    dimension + (padding * 2) for dimension in text_surface.get_size()
                )

                ## create new background surface with
                ## appropriate method and color
                ## of transparency

                surf = converting_method(Surface((width, height)))

                surf.fill(background_color)

                ## blit text surf on new surf taking the
                ## text padding into account
                surf.blit(text_surface, (padding, padding))

                ## update original list with new surface
                text_surfaces[index] = surf

        ### otherwise, we assume the background has
        ### transparency and create such transparent
        ### background for each text surface

        else:

            text_surfaces = [
                font.render(line_text, antialiased, foreground_color).convert_alpha()
                for line_text in lines
            ]

            for index, text_surf in enumerate(text_surfaces[:]):

                surf = Surface(text_surf.get_size()).convert_alpha()

                surf.fill(background_color)
                surf.blit(text_surf, (0, 0))

                text_surfaces[index] = surf

    ### now that all text surfaces are ready, we position
    ### them relative to each other, apply text padding as
    ### requested and unite them into a single surface

    rects = [text_surf.get_rect() for text_surf in text_surfaces]

    rectsman = RectsManager.from_iterable(rects)

    rectsman.snap_rects_ip(
        retrieve_pos_from=retrieve_pos_from,
        assign_pos_to=assign_pos_to,
        offset_pos_by=offset_pos_by,
    )

    rectsman.move_ip(text_padding, text_padding)

    inflation_amount = text_padding * 2

    inflated_rect = rectsman.inflate(
        inflation_amount,
        inflation_amount,
    )

    surf = (
        Surface(inflated_rect.size).convert_alpha()
        if has_transparency
        else Surface(inflated_rect.size).convert()
    )

    surf.fill(background_color)

    for text_surf, rect in zip(text_surfaces, rects):

        surf.blit(text_surf, rect)

    ### add other effects as requested

    ## if depth finish was requested...

    if depth_finish_thickness:

        draw_depth_finish(surf, depth_finish_thickness, depth_finish_outset)

    ## if a border was requested...
    if border_thickness:
        draw_border(surf, border_color, border_thickness)

    ### finally return the surf
    return surf
