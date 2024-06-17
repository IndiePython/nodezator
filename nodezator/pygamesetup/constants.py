
### standard library import
from functools import partial


### third-party imports

from pygame import (
    init as init_pygame,
    get_sdl_version,
    locals as pygame_locals,
)

from pygame.locals import (

    QUIT,
    KEYDOWN,

    K_F7,
    K_F8,

    RESIZABLE,
    KMOD_NONE,

)

from pygame.mixer import pre_init as pre_init_mixer

from pygame.key import set_repeat

from pygame.time import Clock

from pygame.display import (
    set_icon,
    set_caption,
    set_mode,
    list_modes,
    update,
)

from pygame.image import load as load_image

from pygame.event import get


# choose appropriate window resize event type according to
# availability

try:
    from pygame.locals import WINDOWRESIZED
except ImportError:
    from pygame.locals import VIDEORESIZE
    WINDOW_RESIZE_EVENT_TYPE = VIDEORESIZE
else:
    WINDOW_RESIZE_EVENT_TYPE = WINDOWRESIZED


### local imports

from ..config import APP_REFS, DATA_DIR

from ..appinfo import FULL_TITLE, ABBREVIATED_TITLE

from ..loopman.exception import QuitAppException



### pygame initialization setups

## pygame mixer pre-initialization
pre_init_mixer(44100, -16, 2, 4096)

## pygame initialization
init_pygame()

## store whether the system support full HD resolution
APP_REFS.full_hd_available = (1920, 1080) in list_modes()


### create a callable to reset the caption to a
### default state whenever needed, then use
### it to set the caption

reset_caption = partial(set_caption, FULL_TITLE, ABBREVIATED_TITLE)
reset_caption()

### set icon and caption for window

image_path = str(DATA_DIR / "app_icon.png")
set_icon(load_image(image_path))


### set key repeating (unit: milliseconds)

set_repeat(
    500, # delay (time before repetition begins)
    30, # interval (interval between repetitions)
)


### create/set screen

SIZE = (
    # this value causes window size to equal screen resolution
    (0, 0)
    if get_sdl_version() >= (1, 2, 10)

    # if sld isn't >= (1, 2, 10) though, it would raise an exception,
    # so we need to provide a proper size
    else (1280, 720)
)

SCREEN = set_mode(SIZE, RESIZABLE)
SCREEN_RECT = SCREEN.get_rect()
blit_on_screen = SCREEN.blit



### framerate-related values/objects

FPS = 24

_CLOCK = Clock()

maintain_fps = _CLOCK.tick
get_fps = _CLOCK.get_fps


### anonymous object to keep track of general values;
###
### values are introduced/update during app's usage:
### frame index is incremented, reset to -1, mode name
### is changed as we switch to other modes, etc.

GENERAL_NS = type("Object", (), {})()

GENERAL_NS.frame_index = -1
GENERAL_NS.mode_name = 'normal'


### name of key pygame services used by all different modes

GENERAL_SERVICE_NAMES = (

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

)


## event values to strip

EVENT_KEY_STRIP_MAP = {

  'MOUSEMOTION': {
    'buttons': (0, 0, 0),
    'touch': False,
    'window': None,
  },

  'MOUSEBUTTONDOWN': {
    'button': 1,
    'touch': False,
    'window': None,
  },

  'MOUSEBUTTONUP': {
    'button': 1,
    'touch': False,
    'window': None,
  },

  'KEYUP': {
    'mod': KMOD_NONE,
    'unicode': '',
    'window': None,
  },

  'KEYDOWN': {
    'mod': KMOD_NONE,
    'unicode': '',
    'window': None,
  },

  'TEXTINPUT': {
    'window': None,
  },

}

### event name to make compact

EVENT_COMPACT_NAME_MAP = {
    'KEYDOWN': 'kd',
    'KEYUP': 'ku',
    'TEXTINPUT': 'ti',
    'MOUSEMOTION': 'mm',
    'MOUSEBUTTONUP': 'mbu',
    'MOUSEBUTTONDOWN': 'mbd',
}

### key of events to make compact

EVENT_KEY_COMPACT_NAME_MAP = {

  'MOUSEMOTION': {
    'pos': 'p',
    'rel': 'r',
    'buttons': 'b',
    'touch': 't',
    'window': 'w',
  },

  'MOUSEBUTTONDOWN': {
    'pos': 'p',
    'button': 'b',
    'touch': 't',
    'window': 'w',
  },

  'MOUSEBUTTONUP': {
    'pos': 'p',
    'button': 'b',
    'touch': 't',
    'window': 'w',
  },

  'KEYUP': {
    'key': 'k',
    'scancode': 's',
    'mod': 'm',
    'unicode': 'u',
    'window': 'w',
  },

  'KEYDOWN': {
    'key': 'k',
    'scancode': 's',
    'mod': 'm',
    'unicode': 'u',
    'window': 'w',
  },

  'TEXTINPUT': {
    'text': 't',
    'window': 'w',
  },

}


### available keys

KEYS_MAP = {

    item : getattr(pygame_locals, item)

    for item in dir(pygame_locals)

    if item.startswith('K_')

}

SCANCODE_NAMES_MAP = {

    getattr(pygame_locals, name): name

    for name in dir(pygame_locals)

    if name.startswith('KSCAN')

}


MOD_KEYS_MAP = {

    item: getattr(pygame_locals, item)

    for item in dir(pygame_locals)

    if (
        item.startswith('KMOD')
        and item != 'KMOD_NONE'
    )

}


### temporary file cleaning

def clean_temp_files():
    """Clean temporary files."""

    ### remove temporary paths
    APP_REFS.temp_filepaths_man.ensure_removed()

    ### remove swap path if it there's one

    try:
        swap_path = APP_REFS.swap_path
    except AttributeError:
        pass
    else:
        swap_path.unlink()


### 

def watch_window_size():
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
        APP_REFS.wm.draw()

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


### function to pause when recording/playing session

class CancelWhenPaused(Exception):
    """Raised during pause to cancel and return to normal mode."""

def pause():

    running = True

    while running:

        ### keep constants fps
        maintain_fps(FPS)

        ### process events

        for event in get():

            if event.type == QUIT:
                raise QuitAppException

            elif event.type == KEYDOWN:

                if event.key == K_F8:
                    running = False

                elif event.key == K_F7:
                    raise CancelWhenPaused

        ### update the screen
        update()

