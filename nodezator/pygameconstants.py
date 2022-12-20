"""App constants."""

### third-party imports

from pygame import (
    RESIZABLE,
    init as init_pygame,
    get_sdl_version,
)

# choose appropriate window resize event type according to
# availability

try:
    from pygame import WINDOWRESIZED
except ImportError:
    from pygame import VIDEORESIZE
    WINDOW_RESIZE_EVENT_TYPE = VIDEORESIZE
else:
    WINDOW_RESIZE_EVENT_TYPE = WINDOWRESIZED

#

from pygame.event import get

from pygame.key import (
    set_repeat,
    get_pressed,
    get_mods,
)

from pygame.mouse import (
    set_visible,
    get_pos,
    set_pos,
    get_pressed as mouse_get_pressed,
)

from pygame.display import (
    set_mode,
    set_icon,
    set_caption,
    update,
)

from pygame.time import Clock
from pygame.image import load as load_image

from pygame.mixer import pre_init as pre_init_mixer


### local imports

from .appinfo import FULL_TITLE, ABBREVIATED_TITLE

from .config import DATA_DIR

from .ourstdlibs.behaviour import empty_function


### pygame mixer pre-initialization
pre_init_mixer(44100, -16, 2, 4096)

### pygame initialization
init_pygame()

### framerate-related constants/behaviour

_CLOCK = Clock()
maintain_fps = _CLOCK.tick

FPS = 24

### set caption and icon for window

set_caption(FULL_TITLE, ABBREVIATED_TITLE)

image_path = str(DATA_DIR / "app_icon.png")

set_icon(load_image(image_path))

### set key repeating (unit: milliseconds)
set_repeat(500, 30)  # set_repeat(delay, interval)


### general screen setup constant
DEPTH = 32

### overridable constants/behavior;
###
### the names below can be overriden to change the app's behavior;
###
### that is, one can set other values and/or replace the behaviors
### by other ones that extend them;

DEFAULT_SIZE = (
    # this value causes window size to equal screen resolution
    (0, 0)
    if get_sdl_version() >= (1, 2, 10)

    # if sld isn't >= (1, 2, 10) though, it would raise an exception,
    # so we need to provide a proper size
    else (1280, 720)
)

FLAG = RESIZABLE

SCREEN = set_mode(DEFAULT_SIZE, FLAG, DEPTH)

get_events = get

get_mouse_pos = get_pos
set_mouse_pos = set_pos
get_mouse_pressed = mouse_get_pressed
set_mouse_visibility = set_visible

get_pressed_keys = get_pressed
get_pressed_mod_keys = get_mods

update_screen = update


### the constants below should not be overriden, since they are
### useful regardless of the desired behavior

blit_on_screen = SCREEN.blit

SCREEN_RECT = SCREEN.get_rect()
