"""Commonly used objects/tools."""

### third-party import
from pygame import Surface


### local imports

from ..config import APP_REFS

from ..pygameconstants import (
    SCREEN,
    SCREEN_RECT,
    blit_on_screen,
)

from ..ourstdlibs.collections.general import FactoryDict

from .render import render_rect

from .draw import draw_not_found_icon

from ..colorsman.colors import (
    CONTRAST_LAYER_COLOR,
    IMAGE_NOT_FOUND_FG,
    IMAGE_NOT_FOUND_BG,
)


### empty surface
EMPTY_SURF = Surface((0, 0)).convert()

### copy of screen to use as its cache
APP_REFS.SCREEN_COPY = SCREEN.copy()

### special operations related to the screen copy


def cache_screen_state():
    APP_REFS.SCREEN_COPY.blit(SCREEN, (0, 0))


def draw_cached_screen_state():
    blit_on_screen(APP_REFS.SCREEN_COPY, (0, 0))


### general map to store single colored surfaces for
### reuse

## factory function for map
def rect_surface_from_tuple_args(tuple_args):
    return render_rect(*tuple_args)


## map
RECT_SURF_MAP = FactoryDict(rect_surface_from_tuple_args)


### map to store surfaces used to unhighlight other
### surfaces

## factory function for map
def get_semitransp_surface_from_size(size):
    return render_rect(*size, (*CONTRAST_LAYER_COLOR, 130))


## map
UNHIGHLIGHT_SURF_MAP = FactoryDict(get_semitransp_surface_from_size)

## also make it so map already stores a surface the size of
## the screen
UNHIGHLIGHT_SURF_MAP[SCREEN_RECT.size]

### general map to store "draw not found surfaces" for
### reuse

## factory function for map


def get_draw_not_found_surface(size_tuple):

    surf = render_rect(*size_tuple, IMAGE_NOT_FOUND_BG)
    draw_not_found_icon(surf, IMAGE_NOT_FOUND_FG)

    return surf


## map
NOT_FOUND_SURF_MAP = FactoryDict(get_draw_not_found_surface)
