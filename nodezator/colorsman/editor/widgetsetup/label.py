"""Label creation for the colors editor class."""

### local imports

from ....textman.render import render_text

from ....surfsman.draw import blit_aligned
from ....surfsman.render import render_rect

from ....surfsman.icon import render_layered_icon

from ....classes2d.single import Object2D
from ....classes2d.collections import Set2D

from ...colors import BLACK, WINDOW_BG, WINDOW_FG

from .constants import FONT_HEIGHT, TEXT_PADDING


def setup_labels(self):
    """Create and set up labels.

    Function meant to be injected in the ColorsEditor
    class. Handles the creation of labels.
    """
    ### reference individual scales
    hue, light, sat, value, red, green, blue, alpha = self.scales

    ### gather text and position data for labels

    text_and_position_pairs = (
        ## color properties/representations
        ("Hue", hue.rect.move(10, 0).topright),
        ("Lightness", light.rect.move(10, 0).topright),
        ("Saturation", sat.rect.move(10, 0).topright),
        ("Value", value.rect.move(10, 0).topright),
        ("Red", red.rect.move(10, 0).topright),
        ("Green", green.rect.move(10, 0).topright),
        ("Blue", blue.rect.move(10, 0).topright),
        ("Hex", alpha.rect.move(-115, 29).bottomleft),
        ("HTML name", alpha.rect.move(50, 29).bottomleft),
        ("pygame name", alpha.rect.move(360, 29).bottomleft),
        ("Alpha", alpha.rect.move(10, 0).topright),
        ## others
        ("Current colors:", self.colors_panel.rect.move(-25, 5).bottomleft),
        ("More:", self.colors_panel.rect.move(-25, 38).bottomleft),
    )

    ### iterate over label text and position data,
    ### building a custom set while you instantiate and
    ### store the labels

    self.labels = Set2D(
        Object2D.from_surface(
            surface=render_text(
                text=text,
                font_height=FONT_HEIGHT,
                padding=TEXT_PADDING,
                foreground_color=WINDOW_FG,
                background_color=WINDOW_BG,
            ),
            coordinates_name="topleft",
            coordinates_value=topleft,
            name=text,
        )
        for text, topleft in text_and_position_pairs
    )

    ### create and store a special label to use as the
    ### title for the colors editor widget

    ## load/render surfaces
    ##
    ## note that we don't use padding for the text,
    ## cause we'll blit it over a new surface ahead
    ## and that surface has enough space;

    icon_surf = render_layered_icon(
        chars=[chr(ordinal) for ordinal in range(106, 113)],
        dimension_name="height",
        dimension_value=30,
        colors=[
            BLACK,
            *(
                (r, g, b)
                for r in (0, 255)
                for g in (0, 255)
                for b in (0, 255)
                if sum((r, g, b))
            ),
        ],
        background_width=32,
        background_height=32,
    )

    text_surf = render_text(
        text="Colors editor",
        font_height=FONT_HEIGHT,
        foreground_color=WINDOW_FG,
        background_color=WINDOW_BG,
    )

    ## combine surfs into a single one in a new object

    # define width for new object

    width = (
        # width of icon
        icon_surf.get_width()
        # plus width of text
        + text_surf.get_width()
        # plus 5 pixels for spacing between
        # the icon and text surfaces
        + 5
    )

    # height of new objects is the maximum size between
    # both surfaces

    height = max(icon_surf.get_height(), text_surf.get_height())

    # define topleft position for object and instantiate it

    topleft = self.rect.move(5, 5).topleft

    title_obj = Object2D.from_surface(
        surface=render_rect(width=width, height=height, color=WINDOW_BG),
        coordinates_name="topleft",
        coordinates_value=topleft,
    )

    # reference surface of the title object
    title_surf = title_obj.image

    # define parameters used to blit the icon and text
    # surfaces on the title's surface

    blitting_data = (
        (icon_surf, "midleft", "midleft"),
        (text_surf, "midright", "midright"),
    )

    # blit each surface on the title surface

    for (
        surf,
        pos_from,
        pos_to,
    ) in blitting_data:

        blit_aligned(
            surface_to_blit=surf,
            target_surface=title_surf,
            retrieve_pos_from=pos_from,
            assign_pos_to=pos_to,
        )

    ## finally, store the title object as a label
    self.labels.add(title_obj)
