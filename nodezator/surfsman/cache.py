"""Commonly used objects/tools."""

### third-party import
from pygame import Surface


### local imports

from ..config import APP_REFS

from ..pygamesetup import SCREEN, SCREEN_RECT, blit_on_screen

from ..ourstdlibs.collections.general import FactoryDict

from .render import render_rect, render_not_found_icon

from .draw import draw_checker_pattern

from ..colorsman.colors import CONTRAST_LAYER_COLOR



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
NOT_FOUND_SURF_MAP = FactoryDict(render_not_found_icon)

### general map to store checkered surfaces for reuse

## factory function for map

def checkered_surface_from_tuple_args(tuple_args):
    size, color_a, color_b, rect_width, rect_height = tuple_args

    surf = Surface(size).convert()
    draw_checker_pattern(surf, color_a, color_b, rect_width, rect_height)

    return surf

## map
CHECKERED_SURF_MAP = FactoryDict(checkered_surface_from_tuple_args)
