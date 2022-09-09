"""Facility for CheckButton widget class definition."""

### standard library import
from xml.etree.ElementTree import Element


### local imports

from ..ourstdlibs.behaviour import empty_function

from ..classes2d.single import Object2D

from ..surfsman.icon import render_layered_icon

from ..surfsman.draw import draw_border

from ..colorsman.colors import (
    CHECKBUTTON_FG,
    CHECKBUTTON_BG,
    CHECKBUTTON_OUTLINE,
)


### XXX docstring/comments regarding creation of surface
### map might need reviewing;


class CheckButton(Object2D):
    """A checkbutton for general usage."""

    ### define a map to hold surface maps for different
    ### styles of checkbuttons
    styles_to_surface_map = {}

    def __init__(
        self,
        value=False,
        name="check_button",
        size=16,
        foreground_color=CHECKBUTTON_FG,
        background_color=CHECKBUTTON_BG,
        outline_color=CHECKBUTTON_OUTLINE,
        command=empty_function,
        coordinates_name="topleft",
        coordinates_value=(0, 0),
    ):
        """Store arguments and perform setups.

        Parameters
        ==========

        value (boolean)
            represents current value of the widget.
        name (string)
            an arbitrary name to help identify the widget.
        size (positive integer)
            represents value of both width and height of
            the checkbutton surface, in pixels.
        command (callable)
            optional command to be execute when the
            value is changed. Default is an empty function
            which does nothing.
        coordinates_name (string)
            represents attribute name of rect wherein
            to store the position information from the
            coordinates value parameter.
        coordinates_value (list/tuple/vector w/ 2 integers)
            represents the x and y coordinates of a
            position in 2d space.
        """
        ### ensure value is a boolean

        if not isinstance(value, bool):

            raise TypeError("'value' argument must be of type 'bool'")

        ### store value, command and name arguments

        self.value = value
        self.command = command
        self.name = name

        ### try retrieving a surface for specific styles
        ### used

        ## define a string to use as a key from the styles
        ## used

        key = str((size, foreground_color, background_color, outline_color))

        ## try retrieving a surface map for the specific
        ## styles used
        try:
            self.surface_map = self.styles_to_surface_map[key]

        ### if there isn't one, create it yourself

        except KeyError:

            ### create the surface map with the given styles

            surface_map = self.get_surface_map(
                size, foreground_color, background_color, outline_color
            )

            ### store the surface map in its own attribute
            ### and also in the "size to surface map" dict
            ### in the class attribute, using the original
            ### size (not the corrected one) as the key

            self.surface_map = self.__class__.styles_to_surface_map[key] = surface_map

        ### create image attribute
        self.update_image()

        ### create a rect from the image attribute
        ### and position it

        self.rect = self.image.get_rect()
        setattr(self.rect, coordinates_name, coordinates_value)

    def get_surface_map(self, size, foreground_color, background_color, outline_color):
        """Return dict w/ surfaces of given styles.

        Parameters
        ==========
        See __init__ method docstring for information on
        the parameters.
        """
        ### define padding
        padding = 2

        ### calculate a padded size by removing padding
        ### two times from the size (to account for padding
        ### on both sides); we do so because the padding is
        ### added back to the surface when rendering the
        ### icon with the 'padding' argument
        padded_size = size - (padding * 2)

        ### create a surface to be displayed when the
        ### checkbutton is set to True; we do so by
        ### rendering a surface which represents the heavy
        ### check mark icon, with padding and a border;

        true_surf = render_layered_icon(
            chars=[chr(124)],
            dimension_name="height",
            dimension_value=padded_size,
            padding=padding,
            colors=[foreground_color],
            background_width=size,
            background_height=size,
            background_color=background_color,
            border_thickness=2,
            border_color=outline_color,
        )

        ### now create a surface for when the checkbutton
        ### is set to False

        ## copy the "true surf" and fill it with the
        ## background color

        false_surf = true_surf.copy()
        false_surf.fill(background_color)

        ## then draw a border around it

        draw_border(false_surf, color=outline_color, thickness=2)

        ### create and return dict mapping each boolean value
        ### to its corresponding surface

        return {False: false_surf, True: true_surf}

    def update_image(self):
        """Set image attribute according to value."""
        self.image = self.surface_map[self.value]

    def get(self):
        """Return current value."""
        return self.value

    def set(self, value, execute_command=True):
        """Set current value.

        Parameters
        ==========
        value (bool)
            we set it as the value for this widget;
            that is, if the value is different from the
            current one.
        execute_command (boolean)
            indicates whether to execute the command in
            case the value changes.
        """
        ### ensure value is a boolean

        if not isinstance(value, bool):

            raise TypeError("'value' argument must be of type 'bool'")

        ### store value and update the image, if the value
        ### is different than the current one;
        ###
        ### if it is the case, also execute the command,
        ### if requested

        if value != self.value:

            self.value = value
            self.update_image()

            if execute_command:
                self.command()

    def toggle_value(self, event):
        """Set the opposite of the current value.

        Parameters
        ==========
        event
            (pygame.event.Event of pygame.MOUSEBUTTONDOWN
            type)

            although we don't use it here, it is required in
            order to comply with the mouse action protocol;

            check pygame.event module documentation on
            pygame website for more info about this event
            object.
        """
        new_value = not self.value
        self.set(new_value)

    ### alias the toggle value method so it complies with
    ### the mouse action protocol
    on_mouse_click = toggle_value

    def get_expected_type(self):
        return bool

    def svg_repr(self):

        g = Element("g", {"class": "check_button"})

        rect = self.rect.inflate(-4, -4)

        g.append(
            Element(
                "rect",
                {
                    attr_name: str(getattr(rect, attr_name))
                    for attr_name in (
                        "x",
                        "y",
                        "width",
                        "height",
                    )
                },
            )
        )

        if self.value:

            r = self.rect.inflate(-12, -12)

            points = (
                f"{r.left},{r.centery}" f" {r.centerx},{r.bottom}" f" {r.right},{r.top}"
            )

            g.append(Element("polyline", {"points": points}))

        return g
