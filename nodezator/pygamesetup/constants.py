
### third-party imports

from pygame import (
    locals as pygame_locals,
    Surface,
)

from pygame.locals import KMOD_NONE

from pygame.time import Clock

from pygame.font import SysFont

from pygame.draw import rect as draw_rect



# choose appropriate window resize event type according to
# availability

try:
    from pygame import WINDOWRESIZED
except ImportError:
    from pygame import VIDEORESIZE
    WINDOW_RESIZE_EVENT_TYPE = VIDEORESIZE
else:
    WINDOW_RESIZE_EVENT_TYPE = WINDOWRESIZED


### local import
from ..config import APP_REFS



### general screen setup constant
DEPTH = 32


### framerate-related values/objects

FPS = 24

_CLOCK = Clock()

maintain_fps = _CLOCK.tick
get_fps = _CLOCK.get_fps

### label text rendering operations

render_label_text = SysFont('Arial', 16, bold=True).render

Object = type("Object", (), {})

def get_label_object(text, label_fg, label_bg, label_outline, padding):

    ### render the text itself

    text_surface = render_label_text(
        text,
        True,
        label_fg,
        label_bg,
    )

    ### create a surface with the sides incremented by
    ### double the padding

    label_surface = (

        Surface(

            tuple(
                v + (padding * 2)
                for v in text_surface.get_size()
            )

        ).convert()

    )

    ### fill the surface with the outline color
    label_surface.fill(label_outline)

    ### draw a slightly smaller rect inside the surface with the
    ### filling color

    draw_rect(
        label_surface,
        label_bg,
        label_surface.get_rect().inflate(-2, -2),
    )

    ### blit the text inside the surface where the padding
    ### ends
    label_surface.blit(text_surface, (padding, padding))

    ### create label rect
    label_rect = label_surface.get_rect()

    ### instantiate and populate label object

    label = Object()
    label.__dict__.update(image=label_surface, rect=label_rect)

    ### finally return the label
    return label


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
    'MOUSEMOTION': 'mm',
    'MOUSEBUTTONUP': 'mbu',
    'MOUSEBUTTONDOWN': 'mbd',
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
