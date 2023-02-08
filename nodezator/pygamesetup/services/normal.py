
### third-party imports

from pygame.event import get as get_events

from pygame.key import (
    get_pressed as get_pressed_keys,
    get_mods as get_pressed_mod_keys,
)

from pygame.mouse import (
    set_visible as set_mouse_visibility,
    get_pos as get_mouse_pos,
    set_pos as set_mouse_pos,
    get_pressed as get_mouse_pressed,
)

from pygame.display import update as update_screen


### local imports

from ...config import APP_REFS

from ..constants import SCREEN, SCREEN_RECT, FPS, maintain_fps



def _watch_window_size():
    """Perform setups needed if window was resized."""
    ### obtain current size
    current_size = SCREEN.get_size()

    ### if current screen size is different from the one
    ### we stored...

    if current_size != SCREEN_RECT.size:

        ### perform window resize setups

        SCREEN_RECT.size = current_size
        APP_REFS.window_resize_setups()

        ### redraw the window manager
        APP_REFS.window_manager.draw()

        ### update the screen copy
        APP_REFS.SCREEN_COPY = SCREEN.copy()

        ### if there's a request to draw after the setups,
        ### do so and delete the request

        if hasattr(
            APP_REFS,
            "draw_after_window_resize_setups",
        ):

            APP_REFS.draw_after_window_resize_setups()
            del APP_REFS.draw_after_window_resize_setups


def frame_checkups():
    """Perform various checkups.

    Meant to be used at the beginning of each frame in the
    app loop.
    """
    ### keep a constants framerate
    maintain_fps(FPS)

    ### keep an eye on the window size
    _watch_window_size()

def frame_checkups_with_fps(fps):
    """Same as frame_checkups(), but uses given fps."""
    ### keep a constants framerate
    maintain_fps(fps)

    ### keep an eye on the window size
    _watch_window_size()
