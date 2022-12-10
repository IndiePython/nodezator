"""App constants."""

### standard library import
from pathlib import Path


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

from pygame.key import set_repeat
from pygame.time import Clock
from pygame.image import load as load_image
from pygame.display import set_mode, set_icon, set_caption

from pygame.mixer import pre_init as pre_init_mixer


### local imports
from .appinfo import FULL_TITLE, ABBREVIATED_TITLE


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

image_path = str(Path(__file__).parent / "data" / "app_icon.png")

set_icon(load_image(image_path))

### set key repeating (unit: milliseconds)
set_repeat(500, 30)  # set_repeat(delay, interval)


### screen setup/constants

DEFAULT_SIZE = (
    # this value causes window size to equal screen resolution
    (0, 0)
    if get_sdl_version() >= (1, 2, 10)

    # if sld isn't >= (1, 2, 10) though, it would raise an exception,
    # so we need to provide a proper size
    else (1280, 720)
)

FLAG, DEPTH = RESIZABLE, 32

SCREEN = set_mode(DEFAULT_SIZE, FLAG, DEPTH)

blit_on_screen = SCREEN.blit

SCREEN_RECT = SCREEN.get_rect()
