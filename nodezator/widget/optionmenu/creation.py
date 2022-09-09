"""Option menu support facility for creating surfaces.

Such surfaces are the ones used/stored in the option
widgets and include the "chosen surfaces", which are also
used by the option menu itself in its 'image' attribute.
"""

### local imports

from ...surfsman.draw import blit_aligned, draw_border

from ...surfsman.render import render_rect

from ...surfsman.icon import render_layered_icon

from ...textman.render import render_text


### constants

## map to store arrow surfaces; the keys are
## custom-formatted tuples containing style
## information for the respective arrow surface
STYLE_TO_ARROW_SURFS = {}

## map to store surfaces for scrolling arrows;
## the keys are custom-formatted tuples containing style
## information for the respective arrow surface
STYLE_TO_SCROLL_ARROW_SURFS = {}


### functions to create surfaces


def get_arrow_surf(foreground_color, height):
    """Return arrow surface w/ given color and height.

    If an arrow for the given arguments doesn't exist
    already, it is created and stored on the spot,
    before being returned.

    Parameters
    ==========
    foreground_color (sequence of integers)
        represents the color of the arrow; the integers
        are in range(256) and represent values of red,
        green and blue channels of the color, respectively.
    height (integer)
        height of the arrow surface; the arrow itself
        won't have this height; such height will be
        achieved by the arrow itself plus some extra
        padding added so the arrow appears in the very
        center of the surface with some pleasing padding
        around it.
    """
    ### create a custom-formatted tuple from the received
    ### foreground color and height, to use as a key

    key = tuple(map(str, (foreground_color, height)))

    ### try retrieving a reference to the arrow surf from
    ### a special dict dedicated to store them
    try:
        arrow_surf = STYLE_TO_ARROW_SURFS[key]

    ### if such arrow doesn't exist, we create and store it,
    ### in the dictionary, and also reference it locally

    except KeyError:

        arrow_surf = STYLE_TO_ARROW_SURFS[key] = render_layered_icon(
            chars=[chr(82)],
            colors=[foreground_color],
            dimension_name="height",
            dimension_value=height - 8,
            padding=4,
            background_height=height,
            flip_y=True,
        )

    ### we then return the arrow
    return arrow_surf


def create_chosen_surfs(options, chosen_text_settings):
    """Create surfaces to display the chosen values.

    Each surface represents one of the available values
    for the option menu; the chosen surface representing
    the current value set in the option menu is the one
    used as the 'image' attribute of the option menu itself.
    """
    ### get an arrow surface with the same color as the
    ### foreground color and with the same height as the
    ### font height

    ## prepare arguments used to retrieve the arrow

    arrow_foreground_color = chosen_text_settings["foreground_color"]

    arrow_surf_height = chosen_text_settings["font_height"]

    ## retrieve it

    arrow_surf = get_arrow_surf(arrow_foreground_color, arrow_surf_height)

    ### using the options and the text settings, create
    ### a list of surfaces representing the options
    ### rendered as text surfaces

    chosen_surfs = [
        render_text(str(option), **chosen_text_settings) for option in options
    ]

    ### now calculate a new width for the surfaces, which
    ### is equal to the largest width among the existing
    ### surfaces plus the width of the arrow surface

    new_width = (
        ## largest width among existing surfaces
        max(surf.get_width() for surf in chosen_surfs)
        ## arrow width
        + arrow_surf.get_width()
    )

    ### now iterate over each surface, blitting it over
    ### a new surface created with the new width we
    ### just calculated, and replacing the existing
    ### surface with the new one

    ## define common values for all surfaces;
    ##
    ## note that we arbitrarily increment the height by
    ## 2 pixels, just to create a nice vertical padding
    ## in the new surface when we blit the original
    ## surface over it

    height = chosen_surfs[0].get_height() + 2
    bg_color = chosen_text_settings["background_color"]

    ## iterate over the index of each surface, creating
    ## the a new one and replacing the existing one with
    ## it

    for index in range(len(chosen_surfs)):

        ## retrieve the surface
        text_surf = chosen_surfs[index]

        ## create a new surface with the new width
        new_surf = render_rect(new_width, height, bg_color)

        ## blit the original surface over the new one,
        ## with the midleft coordinates aligned;
        ##
        ## note that we also offset the original surface
        ## 2 pixels to the right before blitting it;
        ##
        ## we do so to produce a nice padding to the
        ## left of the text, since the arrow already
        ## has padding around it that ends up creating
        ## a pleasing space between the text and the
        ## arrow and also between the arrow and the
        ## right edge of the new surface (we'll blit
        ## the arrow just after blitting the original
        ## surface below

        blit_aligned(
            text_surf,
            new_surf,
            retrieve_pos_from="midleft",
            assign_pos_to="midleft",
            offset_pos_by=(2, 0),
        )

        ## now blit the arrow over the new surface,
        ## with its midright aligned with the surface's
        ## midright

        blit_aligned(
            arrow_surf,
            new_surf,
            retrieve_pos_from="midright",
            assign_pos_to="midright",
        )

        ## draw a border around the surface
        draw_border(new_surf)

        ## then replace the original surface with the
        ## new one using the index
        chosen_surfs[index] = new_surf

    ### finally build and return a dictionary containing
    ### the text surfaces we created as values, with the
    ### text for each option (the options converted to
    ### strings) as the keys

    return {str(option): surf for option, surf in zip(options, chosen_surfs)}


def create_other_surfs(options, text_settings):
    """Create surfaces for other purposes.

    Like the "chosen surfaces", each surface represents one
    of the available values for the option menu. These are
    surfaces used for other purposes instead of to indicate
    that an specific value is chosen.

    By the time this text was written, this function was
    being used to produce surfaces representing the available
    values (options) for the option menu when they were
    either hovered or unhovered by the mouse.
    """
    ### using the options and the text settings, create
    ### a list of surfaces representing the options
    ### rendered as text surfaces

    surfs = [render_text(str(option), **text_settings) for option in options]

    ### now calculate a new width for the surfaces, which
    ### is equal to the largest width among the existing
    ### surfaces plus 4 pixels for extra horizontal padding;
    ###
    ### the value of the padding was arbitrarily chosen
    ### based on what looked good

    new_width = (
        ## largest width among existing surfaces
        max(surf.get_width() for surf in surfs)
        ## plus 4 pixels for extra horizontal padding
        + 4
    )

    ### now iterate over each surface, blitting it over
    ### a new surface created with the new width we
    ### just calculated, and replacing the existing
    ### surface with the new one

    ## define common values for all surfaces;
    ##
    ## note that we arbitrarily increment the height by
    ## 4 pixels, just to create a nice vertical padding
    ## in the new surface when we blit the original
    ## surface over it

    height = surfs[0].get_height() + 4
    bg_color = text_settings["background_color"]

    ## iterate over the index of each surface, creating
    ## the a new one and replacing the existing one with
    ## it

    for index in range(len(surfs)):

        ## retrieve the surface
        text_surf = surfs[index]

        ## create a new surface with the new width
        new_surf = render_rect(new_width, height, bg_color)

        ## blit the original surface over the new one,
        ## with the topleft coordinates aligned, but with
        ## 2 pixels of offset in both axis;
        ##
        ## we do so to produce a nice padding all around
        ## the text blitted in the new surface, since we
        ## added 4 extra pixels in each dimension, in
        ## previous steps

        blit_aligned(
            text_surf,
            new_surf,
            retrieve_pos_from="topleft",
            assign_pos_to="topleft",
            offset_pos_by=(2, 2),
        )

        ## then replace the original surface with the
        ## new one using the index
        surfs[index] = new_surf

    ### finally build and return a dictionary containing
    ### the text surfaces we created as values, with the
    ### text for each option (the options converted to
    ### strings) as the keys

    return {str(option): surf for option, surf in zip(options, surfs)}


def get_scroll_arrow_surfs(width, foreground_color, background_color):
    """Return scroll arrow surfaces w/ given settings.

    If an arrow for the given arguments doesn't exist
    already, it is created and stored on the spot,
    before being returned.

    Parameters
    ==========
    width (integer)
    foreground_color (sequence of integers)
    background_color (sequence of integers)
    """
    ### create a custom-formatted tuple from the received
    ### width, foreground color and background color, to use
    ### as a key

    key = tuple(map(str, (width, foreground_color, background_color)))

    try:
        upper_arrow, lower_arrow = STYLE_TO_SCROLL_ARROW_SURFS[key]

    except KeyError:

        upper_arrow, lower_arrow = (
            render_layered_icon(
                chars=[chr(82)],
                dimension_name="height",
                dimension_value=10,
                colors=[foreground_color],
                background_width=width,
                background_height=16,
                background_color=background_color,
                flip_y=flip_y,
            )
            for flip_y in (False, True)
        )

        STYLE_TO_SCROLL_ARROW_SURFS[key] = (upper_arrow, lower_arrow)

    ### we then return the surfs
    return upper_arrow, lower_arrow
