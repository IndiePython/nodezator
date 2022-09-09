"""Facility for a options widgets."""

### third-party imports

from pygame.mouse import (
    get_pos as get_mouse_pos,
    get_pressed as get_mouse_pressed,
)

from pygame.transform import flip as flip_surface


### local imports

from ..ourstdlibs.behaviour import empty_function

from ..classes2d.single import Object2D

from ..surfsman.icon import render_layered_icon


### constant definition

HANDLE_SURF = flip_surface(
    render_layered_icon(
        chars=[chr(ordinal) for ordinal in (81, 82)],
        colors=[(18, 18, 18), (30, 130, 70)],
        dimension_name="height",
        dimension_value=15,
        background_width=15,
        background_height=15,
    ),
    False,
    True,
)


### class definition


class Scale(Object2D):
    """A custom scale."""

    def __init__(
        self,
        value,
        scale_surf,
        max_value,
        padding_x=10,
        name="scale",
        coordinates_name="topleft",
        coordinates_value=(0, 0),
        command=empty_function,
    ):
        """Assign variables and perform setups.

        Parameters
        ==========

        value (0.0 <= float <= 1.0)
            initial value of the scale.
        scale_surf (pygame.Surface instance)
            represents the scale.
        max_value (positive integer)
            maximum value the scale can assume.
        padding_x (integer)
            represents amount in pixels to pad the width of
            the scale widget rect area used to pick value.
        name (string)
            just an optional way of further identifying
            the scale; it is stored in the 'name' attribute
            of the instantiated scale.
        coordinates_name (string)
            attribute name of a pygame.Rect instance
            wherein to store the position information from
            the coordinates value argument.
        coordinates_value (2-tuple or list; has 2 integers)
            represents a position in 2d space, the values
            of the x and y axes, respectively.
        command (callable)
            command to be executed everytime the value
            changes; defaults to an empty function.
        """
        ### store arguments

        self.value = value
        self.name = name
        self.command = command
        self.max_value = max_value
        self.padding_x = padding_x

        ### set image and rect for widget

        self.image = scale_surf
        self.rect = self.image.get_rect()
        setattr(self.rect, coordinates_name, coordinates_value)

        ### set handle object

        self.handle = Object2D(image=HANDLE_SURF, rect=HANDLE_SURF.get_rect())

        ### define a selection area excluding the padding
        self.define_selection_area()

        ### position handle according to value
        self.place_handle()

    def define_selection_area(self):
        self.selection_area = self.rect.inflate(-self.padding_x, 0)

    def place_handle(self):
        """Place handle according to current value."""
        ### calculate x based on value

        ## retrieve starting x
        x = self.selection_area.x

        ## calculate x increment based on value

        increment = round(self.value / self.max_value * self.selection_area.width)

        ## increment x
        x += increment

        ### finally position handle
        self.handle.rect.midtop = (x, self.rect.top)

    def get(self):
        """Return stored value."""
        return self.value

    def set(self, value, custom_command=True):
        """Set scale to value.

        Parameters
        ==========

        value (0.0 <= float <= 1.0)
            value of the widget.
        custom_command (boolean)
            indicates whether the command must be executed
            after setting the value.
        """
        ### clamp and store value
        self.value = value

        ### update handle position
        self.place_handle()

        ### if requested, give feedback
        if custom_command:
            self.command()

    def draw(self):
        """Draw self and handle.

        Extends Object2D.draw.
        """
        super().draw()
        self.handle.draw()

    def check_handle(self):
        """Check if handle is being changed."""
        x, y = get_mouse_pos()

        ## if mouse cursor is outside widget, return earlier
        if not self.rect.collidepoint(x, y):
            return

        ### if mouse button 1 is pressed, position handle
        ### and update value

        if get_mouse_pressed()[0]:

            self.handle_to_x(x)
            self.update_value()
            self.command()

    update = check_handle

    def handle_to_x(self, mouse_x):
        """Position handle according to mouse x coordinate.

        Parameters
        ==========
        mouse_x (integer)
            mouse x coordinate relative to screen and
            constrained to it.
        """
        ### clamp mouse_x to selection area width

        ## retrieve selection area horizontal edges

        left = self.selection_area.left
        right = self.selection_area.right

        ## clamp
        clamped_x = max(left, min(right, mouse_x))

        ### position handle
        self.handle.rect.centerx = clamped_x

    def update_value(self):
        """Update value attribute using handle position."""
        ### retrieve handle x center pos
        handle_centerx = self.handle.rect.centerx

        ### retrieve selection area starting x and width

        x = self.selection_area.x
        width = self.selection_area.width

        ### calculate value based on
        ### - proportion of the handle distance from x
        ###   to the width of selection area
        ### - maximum possible value

        distance = handle_centerx - x
        percentage = distance / width

        self.value = round(percentage * self.max_value)
