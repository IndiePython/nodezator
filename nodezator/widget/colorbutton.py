"""Facility for color picking button widget."""

### standard library imports

from math import inf

from xml.etree.ElementTree import Element


### third-party import
from pygame import Surface


### local imports

from ..ourstdlibs.behaviour import empty_function

from ..surfsman.draw import (
    draw_checker_pattern,
    blit_aligned,
)

from ..surfsman.render import render_rect, combine_surfaces

from ..classes2d.single import Object2D

from ..imagesman.cache import IMAGE_SURFS_DB

from ..surfsman.icon import render_layered_icon

from ..alphamask.main import AlphaMask

from ..fontsman.constants import (
    ICON_FONT_PATH,
    ENC_SANS_BOLD_FONT_PATH,
)

from ..textman.render import render_text

from ..colorsman.viewer.main import view_colors

from ..colorsman.editor.main import edit_colors

from ..ourstdlibs.color.custom import (
    custom_format_color,
    validate_custom_color_format,
)

from ..colorsman.colors import (
    BLACK,
    WHITE,
    COLORBUTTON_BG,
    TRANSP_COLOR_A,
    TRANSP_COLOR_B,
)

from ..pointsman2d.create import get_circle_points


### constants

## surface representing color button

ICON_SURF = render_layered_icon(
    chars=[chr(ordinal) for ordinal in range(106, 113)],
    dimension_name="height",
    dimension_value=20,
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
    background_width=17,
    background_height=20,
)

## retrieve and store icon width
ICON_SIZE = ICON_SURF.get_size()

## create fill mask to produce filled surfaces representing
## color units

COLOR_UNIT_MASK = AlphaMask.from_surface(
    render_text(
        text=chr(114),
        font_height=20,
        font_path=ICON_FONT_PATH,
        foreground_color=BLACK,
    )
)

## create color unit outline surface

COLOR_UNIT_OUTLINE_SURF = render_text(
    text=chr(113), font_height=20, font_path=ICON_FONT_PATH, foreground_color=BLACK
)

## retrieve and store the size of the mask as the
## size to be used for surface representing a single color
SINGLE_COLOR_SIZE = COLOR_UNIT_MASK.size

## create a surface representing an ellipsis ('…')

_period_surf = render_layered_icon(
    chars=["."],
    font_path=ENC_SANS_BOLD_FONT_PATH,
    dimension_name="width",
    dimension_value=5,
    colors=[BLACK],
    background_color=WHITE,
    background_width=4,
)

ELLIPSIS_SURF = combine_surfaces(
    [_period_surf] * 3,
    retrieve_pos_from="midright",
    assign_pos_to="midleft",
)


## create and store a surf with a checker pattern, with
## the transparent area masked out

# create surf
CHECKERED_SURF = Surface(SINGLE_COLOR_SIZE).convert_alpha()

# draw checker pattern (we use squares of 6 by 6 pixels
# since it looks good)
draw_checker_pattern(CHECKERED_SURF, TRANSP_COLOR_A, TRANSP_COLOR_B, 6, 6)

# mask out transparency
COLOR_UNIT_MASK.mask_by_replacing(CHECKERED_SURF)


## define the height of the colorbutton widget as the
## either the height of the icon or of a color surface,
## whichever is higher
BUTTON_HEIGHT = max(ICON_SIZE[1], SINGLE_COLOR_SIZE[1])

### utility functions


def get_color_surfaces(colors, no_of_slots):
    """Return a list of surfaces representing colors.

    Parameters
    ==========
    colors (tuple containing tuples of integers)
        each inner tuple represents one color and its items
        are integers in the range(0, 256) interval; the
        integers represent the values of each RGB(A) channel
        of a color, respectively.
    no_of_slots (integer)
        number of available spots wherein to display colors.
    """
    ### limit number of surfaces created if number of colors
    ### surpass the number of available spots; in such case,
    ### the last slot must be a white surface with the
    ### ellipsis character ('…') draw in the center;
    ### and we indicate so with a flag set here

    if len(colors) > no_of_slots:

        colors = colors[: no_of_slots - 1] + (WHITE,)
        should_blit_ellipsis = True

    else:
        should_blit_ellipsis = False

    ### generate color surfaces

    color_surfs = [get_single_color_surface(color) for color in colors]

    ### blit ellipsis if needed

    if should_blit_ellipsis:

        blit_aligned(ELLIPSIS_SURF, color_surfs[-1], "center", "center")

    ### finally return the color surfaces
    return color_surfs


def get_single_color_surface(fill_color):
    """Return custom surface representing a single color.

    Parameters
    ==========
    fill_color (tuple of integers)
        the color the surface created represents; the
        integers are in the range(0, 256) interval and
        represent the values of the RGB(A) channels
        of a color.
    """
    ### create a completely transparent button surface

    color_unit_surf = Surface(SINGLE_COLOR_SIZE).convert_alpha()
    color_unit_surf.fill((0, 0, 0, 0))

    ###
    color_surf = COLOR_UNIT_MASK.get_colored_surface(fill_color)

    ### now blit all other surfaces over the button surface

    for surf in (
        CHECKERED_SURF,  ## checkered pattern
        color_surf,  ## color filling
        COLOR_UNIT_OUTLINE_SURF,
    ):
        color_unit_surf.blit(surf, (0, 0))

    ### finally return the surface
    return color_unit_surf


### class definition


class ColorButton(Object2D):
    """Button-like widget for picking/storing colors.

    May store one or more colors.
    """

    def __init__(
        self,
        value=(0, 0, 255),
        color_format="rgb_tuple",
        alone_when_single=True,
        width=155,
        name="color_button",
        command=empty_function,
        coordinates_name="topleft",
        coordinates_value=(0, 0),
    ):
        """Store arguments and perform setups.

        Parameters
        ==========

        value (string or tuple)
            the value stored by the widget; may represent
            one or more colors;

            here are the possible meanings of the value:
                - (1) tuple of integers: a single color
                  where each integer is in the
                  range(0, 256) interval and represent
                  the value of each of the red, green, blue
                  and, possibly, the alpha channel;
                - (2) string: a single color in the
                  '#ffffff' or '#ffffffff' format, where
                  the characters after the '#' represent
                  hexadecimal numbers, two digits for
                  each of the red, green, blue and,
                  possibly, the alpha channel;
                - (3) tuple of tuples: each item of the
                  tuple represents a color in the format
                  shown in the item (1);
                - (4) tuple of strings: each item of the
                  tuple represents a color in the format
                  shown in the item (2);
        color_format (string)
            either 'rgb_tuple', if individual colors
            must use the representation described in
            the item (1) of the 'value' parameter
            explanation above or 'hex_string', if the
            format in item (2) must be used instead;
        alone_when_single (boolean)
            when True, instead of a tuple of colors, the
            color itself is used as the value when the
            color value represents a single color (that is,
            when True, if only one color is stored, it will
            be either a string or a tuple of integers
            representing a single color, instead of a tuple
            containing such color);

            for instance, for
            color_format='hex_string' and
            alone_when_single=True, say the value of the
            button is ['#ffffff', '#00ff00aa'], if you
            go and delete any color (for instance, the
            second one), instead of ['#ffffff'] as the
            value of the button, you'll end up with
            '#ffffff' (that is, the string itself).
        width (integer)
            width available for the button.
        name (string)
            an arbitrary name to help identify the widget;
            it is assigned to the 'name' attribute.
        command (callable)
            callable to be executed whenever the value
            of the button is changed.
        coordinates_name (string)
            represents the name of a pygame.Rect attribute
            wherein to store the position information from
            the "coordinates_value" parameter.
        coordinates_value (sequence with 2 integers)
            integers represent the x and y coordinates of a
            position in 2d space, respectively.
        """
        ### store arguments

        self.value = value
        self.color_format = color_format
        self.alone_when_single = alone_when_single
        self.command = command
        self.name = name
        self.width = width

        ### make sure value and its type are valid; errors
        ### raised in this step are purposefully not caught
        ### (no try/except clauses are set up)

        validate_custom_color_format(value, color_format, alone_when_single)

        ### define the number of available slots to display
        ### colors, storing it in a dedicated attribute

        ## if a width wasn't specified (it is None), then
        ## any number of slots can be used, in which case
        ## we assign math.inf to the relevant attribute
        if width is None:
            self.no_of_slots = inf

        ## otherwise we calculate how many slots we can
        ## fit in the remaining space in the button after
        ## we blit the colorbutton icon and use such
        ## number as the number of slots available

        else:

            available_width_for_colors = width - ICON_SIZE[0]

            self.no_of_slots = available_width_for_colors // (SINGLE_COLOR_SIZE[0] - 2)

            # we subtract 2 because the color unit shape
            # is a bit inclined, so they can be lined
            # closer to each other, which means their
            # width doesn't  occupy so much spacke

        ### create/update the surface representing the
        ### value of the widget, to be stored in the
        ### 'image' attribute
        self.update_image()

        ### create rect from the image attribute and
        ### position it according to the given
        ### coordinates

        self.rect = self.image.get_rect()

        setattr(self.rect, coordinates_name, coordinates_value)

    def get(self):
        """Return the widget value."""
        return self.value

    def set(self, value, custom_command=True):
        """Set the value of the widget.

        Parameters
        ==========
        value (string or tuple)
            check __init__ docstring for more info on this
            parameters; the format must be compatible with
            the settings stored in the 'color_format' and
            'alone_when_single' attributes; again, look into
            the __init__ docstring for the parameters with
            the same name as those attributes for more
            info.
        custom_command (boolean)
            indicates whether the custom command stored
            upon instantiation should be executed after
            updating the value.
        """
        ### check whether value and its type are valid

        try:
            validate_custom_color_format(
                value, self.color_format, self.alone_when_single
            )

        ### if not, report error and exit the method by
        ### returning earlier

        except (ValueError, TypeError) as err:

            print(err)
            return

        ### changes are only performed if the new value is
        ### indeed different from the current one

        if self.value != value:

            ### store new value
            self.value = value

            ### update the widget image
            self.update_image()

            ### if requested, execute the custom command
            if custom_command:
                self.command()

    def set_format(self, color_format, alone_when_single):
        """Change format in which value is represented.

        Parameters
        ==========
        color_format (string), alone_when_single (boolean)
            describe the format used by the value of the
            button; look into the __init__ docstring for the
            parameters with the same name for more info.
        """
        ### convert value using format described by given
        ### arguments

        self.value = custom_format_color(self.value, color_format, alone_when_single)

        ### store the arguments

        self.color_format = color_format
        self.alone_when_single = alone_when_single

    def update_image(self):
        """Create and store surface representing value.

        The surface is stored in the 'image' attribute
        of this widget, hence the name of the method.
        """
        ### get value as a tuple of rgba colors

        colors = custom_format_color(self.value, "rgb_tuple", False)

        ### generate surfaces representing color value

        color_surfs = get_color_surfaces(
            colors,
            self.no_of_slots,
        )

        ### define the width of the image surface

        width = (
            ## the width of the icon
            ICON_SIZE[0]
            ## plus the sum of the width of all color
            ## surfaces (we subtract to cause the color
            ## surfaces are blit 2 pixels closer to
            ## each other, thus occupying less space)
            + ((SINGLE_COLOR_SIZE[0] - 2) * len(color_surfs))
            ## plus 8 additional pixels which will use as
            ## additional space before the icon, between the
            ## icon and the color surfaces and after the
            ## color surfaces, so things look better
            + 8
        )

        ### create an image using the calculated width

        image = self.image = render_rect(width, BUTTON_HEIGHT, COLORBUTTON_BG)

        ### if a rect exists, update its width

        try:
            rect = self.rect
        except AttributeError:
            pass
        else:
            rect.width = image.get_width()

        ### blit icon aligned to the midleft of the surface,
        ### 2 pixels to the right, so there's some padding
        ### to its left

        blit_aligned(ICON_SURF, image, "midleft", "midleft", offset_pos_by=(2, 0))

        ### store the distance from the beginning of the
        ### image until the right of the icon (the width
        ### of the icon plus the 2 pixels we used to offset
        ### it; we won't use it here anymore, but in the
        ### 'on_mouse_release' method, to check whether the
        ### mouse hovered the icon;
        self.distance_till_icon_end = ICON_SIZE[0] + 2

        ### blit each color surface in the "image" surface

        ## use the width of the icon as the "start", a fixed
        ## amount to offset the beginning position x where
        ## the color surfaces will be blitted, plus 4
        ## additional pixels (2 pixels of compensation for
        ## the offset we used in the previous step and 2
        ## additional pixels to put space between the
        ## icon and the color surfaces)
        start = ICON_SIZE[0] + 4

        ## use the width of a color surface as the "step"
        ## amount, an amount used to increment at each
        ## iteration, that is, while bliting each color
        ## surface in the image (the step has 2 pixels
        ## subtracted because the color surfaces are
        ## blit closer to each other to take advantage
        ## of their "inclined" shape)
        step = SINGLE_COLOR_SIZE[0] - 2

        ## iterate over each color surface, calculating
        ## an horizontal offset (x offset) relative to the
        ## midleft corner of the "image" surface and using
        ## such offset to blit the color surface in the
        ## suitable position

        for index, surf in enumerate(color_surfs):

            x_offset = start + (index * step)

            blit_aligned(surf, image, "midleft", "midleft", offset_pos_by=(x_offset, 0))

    def on_mouse_release(self, event):
        """Act according to mouse release position.

        Parameters
        ==========
        event
            (pygame.event.Event of pygame.MOUSEBUTTONUP type)

            It is required in order to comply with
            protocol used. We retrieve the mouse position
            from its "pos" attribute.

            Check pygame.event module documentation on
            pygame website for more info about this event
            object.
        """
        x, _ = event.pos

        ### if click was more to the left, that is, over the
        ### icon, we call the method responsible for
        ### changing the value of the widget by editing/
        ### selecting colors
        if x < (self.rect.x + self.distance_till_icon_end):
            self.change_color_value()

        ### otherwise the user clicked on the portion of
        ### the button which hints the contents of the
        ### widget (that is, the color surfaces), so we
        ### display the widget value instead
        else:
            view_colors(self.value)

    def change_color_value(self):
        """Start a color editor session to change value."""
        ### retrieve new value from the color editor

        value = edit_colors(
            color_value=self.value,
            color_format=self.color_format,
            alone_when_single=self.alone_when_single,
        )

        ### if the value doesn't evaluate to False, try
        ### setting it (it will only be set if it is
        ### different from the current value, though)
        if value:
            self.set(value)

    def get_expected_type(self):

        classes = set((tuple,))

        if self.alone_when_single and self.color_format == "hex_string":
            classes.add(str)

        return classes.pop() if len(classes) == 1 else tuple(classes)

    def svg_repr(self):

        g = Element("g", {"class": "color_button"})

        rect = self.rect

        ### append polygons forming icon
        centerx = rect.x + (ICON_SURF.get_width() // 2) + 1
        centery = rect.centery

        points = list(get_circle_points(12, 9, (centerx, centery)))[1::2]

        polygons = [
            (
                points[i],
                points[(i + 1) % 6],
                (centerx, centery),
            )
            for i in range(6)
        ]

        for polygon, color in zip(
            polygons,
            [
                (r, g, b)
                for r in (0, 255)
                for g in (0, 255)
                for b in (0, 255)
                if sum((r, g, b)) not in (0, 255 * 3)
            ],
        ):

            g.append(
                Element(
                    "polygon",
                    {
                        "points": " ".join(f"{x},{y}" for x, y in polygon),
                        "style": (
                            f"fill:rgb{color};"
                            "stroke:black;"
                            "stroke-width:2px;"
                            "stroke-linejoin:round;"
                        ),
                    },
                )
            )

        ### append color units

        x = rect.x + ICON_SURF.get_width() + 6 + 10
        y = rect.y + 1

        round_radius = 3

        increment = SINGLE_COLOR_SIZE[0] - 2

        width = SINGLE_COLOR_SIZE[0] - (round_radius * 2) - 6
        height = rect.height - (round_radius * 2) - 2

        def path_directives(x, y, width, height):

            return (
                f"M{x} {y} "
                f"l{width} 0 "
                "q1 0 0 3 "
                f"l-4 {height} "
                "q-1 3 -3 3"
                f"l{-width} 0 "
                "q -4 0 -3 -3"
                f"l4 {-height} "
                "q 1 -3 3 -3"
                "Z"
            )

        colors = custom_format_color(self.value, "rgb_tuple", False)

        no_of_colors = len(colors)

        for i, color in enumerate(colors, 1):

            ###
            if i == self.no_of_slots and no_of_colors > self.no_of_slots:

                g.append(
                    Element(
                        "path",
                        {
                            "d": path_directives(x, y, width, height),
                            "style": "fill:white",
                            "class": "color_unit",
                        },
                    )
                )

                text_element = Element(
                    "text",
                    {
                        "x": str(x + round(width / 2) - 5),
                        "y": str(y + round(height / 2) + 5),
                        "text-anchor": "middle",
                        "style": "fill:black",
                    },
                )

                text_element.text = "..."

                g.append(text_element)

                break

            ###
            g.extend(
                [
                    Element(
                        "path",
                        {
                            "d": path_directives(x, y, width, height),
                            "class": "color_unit_checker_bg",
                        },
                    ),
                    Element(
                        "path",
                        {
                            "d": path_directives(x, y, width, height),
                            "style": _get_color_unit_svg_style(color),
                            "class": "color_unit",
                        },
                    ),
                ]
            )

            ###
            x += increment

        return g


def _get_color_unit_svg_style(color):
    """"""
    try:
        color[3]

    except IndexError:
        return f"fill: rgb{color};"

    else:
        return f"fill: rgb{color[:3]};" f"fill-opacity: {round(color[3]/255, 3)};"
