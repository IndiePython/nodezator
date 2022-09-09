"""Switch widget to hide/show other widgets."""

### standard library import
from itertools import cycle


### local imports

from .config import APP_REFS

from .pygameconstants import SCREEN_RECT

from .ourstdlibs.behaviour import empty_function

from .classes2d.single import Object2D

from .surfsman.icon import render_layered_icon

from .colorsman.colors import HIDE_SWITCH_FG, HIDE_SWITCH_BG


# XXX maybe the switches should change the update/drawing
# routines of the widgets so they are not drawn (and maybe
# aren't "called" by mouse events), instead of just getting
# the widgets out of screen as it is done now which needs
# management (is a bother); ponder;

ALLOWED_DIRECTION_NAMES = "up", "down", "left", "right"

### text surfaces for 'hide' and 'show' surfs

SURFACE_MAP = {
    key_name: render_layered_icon(
        chars=[chr(ordinal)],
        dimension_name="width",
        dimension_value=14,
        colors=[HIDE_SWITCH_FG],
        background_width=24,
        background_height=24,
        background_color=(*HIDE_SWITCH_BG, 130),
    )
    for key_name, ordinal in (("shown", 120), ("hidden", 78))
}


## map to help with translations

VALUE_MAP = {
    "left": ("width", -1),
    "right": ("width", 1),
    "up": ("height", -1),
    "down": ("height", 1),
}

### class definition


class HideSwitch(Object2D):
    """Switch to hide/show objects."""

    def __init__(
        self,
        widget,
        name,
        widget_coord_name,
        switch_coord_name,
        direction_name,
        extra_callable=None,
    ):
        """Store variables and perform setups.

        widget
            Any object with a translate method and a
            rect.
        name
            An unique string representing the name of the
            widget being stored for hiding/showing.
        widget_coord_name
            Point name of the point in the widget rect
            wherein to anchor the switch.
        switch_coord_name
            Point name of the point in the switch rect
            used to anchor the switch.
        direction_name
            String whose value is either 'up', 'down',
            'left' or 'right'. Indicates the direction
            wherein to hide the widget.
        """
        self.widget = widget
        self.name = name
        self.switch_coord_name = switch_coord_name
        self.widget_coord_name = widget_coord_name
        self.extra_callable = extra_callable

        ### check direction_name value

        if direction_name not in ALLOWED_DIRECTION_NAMES:

            raise ValueError(
                "'direction_name' must one of the"
                + " following string values: "
                + str(ALLOWED_DIRECTION_NAMES)
            )

        else:
            self.direction_name = direction_name

        ### reference surface for 'shown' state in the
        ### 'image' attribute and obtain a rect from it

        self.image = SURFACE_MAP["shown"]
        self.rect = self.image.get_rect()

        ### position object relative to widget rect and
        ### also store such positioning method as
        ### a window resize setup

        self.snap_switch_to_widget()

        APP_REFS.window_resize_setups.append(self.snap_switch_to_widget)

        ### create control to help with translations
        self.is_hiding = cycle([True, False])

        ### assign update behaviour
        self.update = empty_function

    def on_mouse_release(self, event):
        """Hide/show widget and perform admin tasks.

        Parameters

            - event (pygame.event.Event of
              pygame.MOUSEBUTTONUP type)

              it is not used in this method, but required
              in order to comply with protocol used;
              contains relevant information about the
              event in the form of attributes. Check
              pygame.event module documentation on pygame
              website for more info about this event
              object.
        """
        self.translate_widget()

        try:
            self.extra_callable()
        except TypeError:
            pass

    def snap_switch_to_widget(self):
        """Positions switch relative to the widget"""
        value = getattr(self.widget.rect, self.widget_coord_name)

        setattr(self.rect, self.switch_coord_name, value)

        self.rect.clamp_ip(SCREEN_RECT)

    def translate_widget(self):
        """Translate widget out or inside screen."""
        attr_name, sign = VALUE_MAP[self.direction_name]
        is_hiding = next(self.is_hiding)

        ### keep or invert signal depending of 'is_hiding'
        sign *= 1 if is_hiding else -1

        ### calculate translation deltas (offset)
        ### and perform translation

        amount = getattr(self.widget.rect, attr_name) * sign

        if attr_name == "width":
            offset = [amount, 0]

        else:
            offset = [0, amount]

        self.widget.translate(*offset)

        ### change surf to appropriate one

        surf_name = "hidden" if is_hiding else "shown"
        self.image = SURFACE_MAP[surf_name]

        ### snap switch to its designated place
        self.snap_switch_to_widget()
