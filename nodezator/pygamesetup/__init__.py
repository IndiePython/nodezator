"""Setup of different modes."""

### local imports

## constants
from .constants import (
    SCREEN, SCREEN_RECT, blit_on_screen, clean_temp_files
)

## custom services
from .services import normal, record, play


### create a namespace to store the services in use
SERVICES_NS = type("Object", (), {})()


### create and use function to activate normal behaviour

def set_normal_behaviour():
    """Set normal services as current ones.

    This is done by storing them in the SERVICES_NS
    namespace.
    """
    for attr_name in (

        "get_events",

        "get_pressed_keys",
        "get_pressed_mod_keys",

        "get_mouse_pos",
        "get_mouse_pressed",

        "set_mouse_pos",
        "set_mouse_visibility",

        "update_screen",

        "frame_checkups",
        "frame_checkups_with_fps",

    ):

        value = getattr(normal, attr_name)
        setattr(SERVICES_NS, attr_name, value)

set_normal_behaviour()
