"""Switch related class extension for WindowManager."""

### standard library import
from functools import partial


### local imports

from ..pygameconstants import SCREEN_RECT

from ..hideswitch import HideSwitch


### utility function


def move_close_to_menubar(obj):
    """Move widgets which are closer to menubar up or down.

    The orientation (up or down) is chosen according to the
    position of the first widget. The widgets were chosen
    arbitrarily, taking into account what would look better.

    obj (obj containing widgets as attributes)
    """
    menubar_rect = obj.menubar.rect

    if SCREEN_RECT.contains(menubar_rect):
        obj.separator.rect.topleft = menubar_rect.bottomleft

    else:
        obj.separator.rect.bottomleft = menubar_rect.bottomleft

    for switch in obj.switches:
        switch.snap_switch_to_widget()


def setup_switches(self):
    """Instantiate and set hide/show switches.

    Only applies to specific widgets with a translate
    method. Those were chosen based on how useful it
    would be to be able to hide/show them at will.
    """
    self.switches = []

    extra_behaviour_for_menu = partial(move_close_to_menubar, self)

    menubar_switch = HideSwitch(
        self.menubar,
        "menubar",
        "midbottom",
        "midtop",
        "up",
        extra_behaviour_for_menu,
    )

    self.switches.extend([menubar_switch])

    ### gather behaviours for updating and drawing
    ### switches

    self.switches_update_methods = [item.update for item in self.switches]

    self.switches_drawing_methods = [item.draw for item in self.switches]
