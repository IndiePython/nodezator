
### standard library imports

from itertools import takewhile

from functools import reduce

from inspect import signature, getsource

from contextlib import redirect_stdout

from io import StringIO


### third-party import

## module(s) from where to retrieve callables to turn
## into nodes
import pygame


### local import
from . import signaturedefs



THIRDLIB_IDS_TO_MODULE = {

    "load_image_as_surf": pygame,
    "save_surf_to_file": pygame,
    "surf_from_bytes": pygame,
    "surf_to_bytes": pygame,

    "flip_surface": pygame,
    "scale_surface": pygame,
    "scale_surface_by": pygame,
    "rotate_surface": pygame,
    "rotozoom_surface": pygame,
    "scale2x_surface": pygame,
    "smoothscale_surface": pygame,
    "smoothscale_surf_by": pygame,

    "Font": pygame,
    "SysFont": pygame,
    "Font.render": pygame,
    "Font.size": pygame,

    "Surface": pygame,
    "Surface.convert": pygame,
    "Surface.convert_alpha": pygame,
    "Surface.copy": pygame,
    "Surface.subsurface": pygame,
    "Surface.get_size": pygame,
    "Surface.get_width": pygame,
    "Surface.get_height": pygame,
    "Surface.get_rect": pygame,
    "Surface.get_bounding_rect": pygame,
    "Surface.get_at": pygame,
    "Surface.get_parent": pygame,
    "Surface.get_abs_parent": pygame,
    "Surface.get_offset": pygame,
    "Surface.get_abs_offset": pygame,

    "Rect(obj)": pygame,
    "Rect(topleft, size)": pygame,
    "Rect(left, top, width, height)": pygame,
    "Rect.copy": pygame,
    "Rect.move(delta)": pygame,
    "Rect.move(delta_x, delta_y)": pygame,
    "Rect.inflate(inflation)": pygame,
    "Rect.inflate(x_inflation, y_inflation)": pygame,
    "Rect.clamp": pygame,
    "Rect.clip": pygame,
    "Rect.union": pygame,
    "Rect.unionall": pygame,
    "Rect.fit": pygame,
    "Rect.contains": pygame,
    "Rect.collidepoint(point)": pygame,
    "Rect.collidepoint(x, y)": pygame,
    "Rect.colliderect": pygame,

}


THIRDLIB_SORTED_CATEGORIES = (
    "pygame.image",
    "pygame.transform",
    "pygame.font",
    "Surface",
    "Rect",
)

THIRDLIB_CATEGORY_TO_SORTED_ITEMS = {

    "pygame.image": (
        "load_image_as_surf",
        "save_surf_to_file",
        "surf_from_bytes",
        "surf_to_bytes",
    ),

    "pygame.transform": (
        "flip_surface",
        "scale_surface",
        "scale_surface_by",
        "rotate_surface",
        "rotozoom_surface",
        "scale2x_surface",
        "smoothscale_surface",
        "smoothscale_surf_by",
    ),

    "pygame.font": (
        "Font",
        "SysFont",
        "Font.render",
        "Font.size",
    ),

    "Surface": (
        "Surface",
        "Surface.convert",
        "Surface.convert_alpha",
        "Surface.copy",
        "Surface.subsurface",
        "Surface.get_size",
        "Surface.get_width",
        "Surface.get_height",
        "Surface.get_rect",
        "Surface.get_bounding_rect",
        "Surface.get_at",
        "Surface.get_parent",
        "Surface.get_abs_parent",
        "Surface.get_offset",
        "Surface.get_abs_offset",
    ),

    "Rect": (
        "Rect(obj)",
        "Rect(topleft, size)",
        "Rect(left, top, width, height)",
        "Rect.copy",
        "Rect.move(delta)",
        "Rect.move(delta_x, delta_y)",
        "Rect.inflate(inflation)",
        "Rect.inflate(x_inflation, y_inflation)",
        "Rect.clamp",
        "Rect.clip",
        "Rect.union",
        "Rect.unionall",
        "Rect.fit",
        "Rect.contains",
        "Rect.collidepoint(point)",
        "Rect.collidepoint(x, y)",
        "Rect.colliderect",
    ),
}

ATTR_NOTATION_MAP = {
    "load_image_as_surf": 'image.load',
    "save_surf_to_file": 'image.save',
    "surf_from_bytes": 'image.frombytes',
    "surf_to_bytes": 'image.tobytes',

    "flip_surface": 'transform.flip',
    "scale_surface": 'transform.scale',
    "scale_surface_by": 'transform.scale_by',
    "rotate_surface": 'transform.rotate',
    "rotozoom_surface": 'transform.rotozoom',
    "scale2x_surface": 'transform.scale2x',
    "smoothscale_surface": 'transform.smoothscale',
    "smoothscale_surf_by": 'transform.smoothscale_by',

    "Font": 'font.Font',
    "SysFont": 'font.SysFont',
    "Font.render": 'font.Font.render',
    "Font.size": 'font.Font.size',

}


### small utility


def get_callable_from_module(thirdlib_id, module_obj):

    ### retrieve attribute notation from special map, if available,
    ### otherwise use thirdlib_id itself

    attr_notation = (
        ATTR_NOTATION_MAP[thirdlib_id]
        if thirdlib_id in ATTR_NOTATION_MAP
        else thirdlib_id
    )

    ### get attributes from where to retrieve
    ### callable

    attr_names = "".join(
        takewhile(
            lambda c: c != "(",
            attr_notation,
        )
    ).split(".")

    ### retrieve callable using getattr
    ### in as much levels as needed
    return reduce(getattr, attr_names, module_obj)


### callables map

THIRDLIB_IDS_TO_CALLABLES_MAP = {
    thirdlib_id: get_callable_from_module(thirdlib_id, module_obj)
    for thirdlib_id, module_obj in THIRDLIB_IDS_TO_MODULE.items()
}


### signature callables map

THIRDLIB_IDS_TO_SIGNATURE_CALLABLES_MAP = {

    "load_image_as_surf": signaturedefs._load_image_as_surf,
    "save_surf_to_file": signaturedefs._save_surf_to_file,
    "surf_from_bytes": signaturedefs._surf_from_bytes,
    "surf_to_bytes": signaturedefs._surf_to_bytes,

    "flip_surface": signaturedefs._flip_surface,
    "scale_surface": signaturedefs._scale_surface,
    "scale_surface_by": signaturedefs._scale_surface_by,
    "rotate_surface": signaturedefs._rotate_surface,
    "rotozoom_surface": signaturedefs._rotozoom_surface,
    "scale2x_surface": signaturedefs._scale2x_surface,
    "smoothscale_surface": signaturedefs._smoothscale_surface,
    "smoothscale_surf_by": signaturedefs._smoothscale_surf_by,

    "Font": signaturedefs._font,
    "SysFont": signaturedefs._sysfont,
    "Font.render": signaturedefs._font_render,
    "Font.size": signaturedefs._font_size,

    "Surface": signaturedefs._surface,
    "Surface.convert": signaturedefs._surface_convert,
    "Surface.convert_alpha": signaturedefs._surface_alpha_convert,
    "Surface.copy": signaturedefs._surface_copy,
    "Surface.subsurface": signaturedefs._surface_subsurface,
    "Surface.get_size": signaturedefs._surface_get_size,
    "Surface.get_width": signaturedefs._surface_get_width,
    "Surface.get_height": signaturedefs._surface_get_height,
    "Surface.get_rect": signaturedefs._surface_get_rect,
    "Surface.get_bounding_rect": signaturedefs._surface_get_bounding_rect,
    "Surface.get_at": signaturedefs._surface_get_at,
    "Surface.get_parent": signaturedefs._surface_get_parent,
    "Surface.get_abs_parent": signaturedefs._surface_get_abs_parent,
    "Surface.get_offset": signaturedefs._surface_get_offset,
    "Surface.get_abs_offset": signaturedefs._surface_get_abs_offset,

    "Rect(obj)": signaturedefs._rect1,
    "Rect(topleft, size)": signaturedefs._rect2,
    "Rect(left, top, width, height)": signaturedefs._rect3,
    "Rect.copy": signaturedefs._rect_copy,
    "Rect.move(delta)": signaturedefs._rect_move1,
    "Rect.move(delta_x, delta_y)": signaturedefs._rect_move2,
    "Rect.inflate(inflation)": signaturedefs._rect_inflate1,
    "Rect.inflate(x_inflation, y_inflation)": signaturedefs._rect_inflate2,
    "Rect.clamp": signaturedefs._rect_clamp,
    "Rect.clip": signaturedefs._rect_clip,
    "Rect.union": signaturedefs._rect_union,
    "Rect.unionall": signaturedefs._rect_unionall,
    "Rect.fit": signaturedefs._rect_fit,
    "Rect.contains": signaturedefs._rect_contains,
    "Rect.collidepoint(point)": signaturedefs._rect_collidepoint1,
    "Rect.collidepoint(x, y)": signaturedefs._rect_collidepoint2,
    "Rect.colliderect": signaturedefs._rect_colliderect,

}


### signatures map

THIRDLIB_IDS_TO_SIGNATURES_MAP = {
    thirdlib_id: signature(callable_obj)
    for thirdlib_id, callable_obj in THIRDLIB_IDS_TO_SIGNATURE_CALLABLES_MAP.items()
}


### third-party libs import map

THIRDLIB_IDS_TO_THIRDLIB_IMPORT_TEXTS = {

    "load_image_as_surf": "from pygame.image import load as load_image_as_surf",
    "save_surf_to_file": "from pygame.image import save as save_surf_to_file",
    "surf_from_bytes": "from pygame.image import frombytes as surf_from_bytes",
    "surf_to_bytes": "from pygame.image import tobytes as surf_to_bytes",

    "flip_surface": "from pygame.transform import flip as flip_surface",
    "scale_surface": "from pygame.transform import scale as scale_surface",
    "scale_surface_by": "from pygame.transform import scale_by as scale_surface_by",
    "rotate_surface": "from pygame.transform import rotate as rotate_surface",
    "rotozoom_surface": "from pygame.transform import rotozoom as rotozoom_surface",
    "scale2x_surface": "from pygame.transform import scale2x as scale2x_surface",
    "smoothscale_surface": "from pygame.transform import smoothscale as smoothscale_surface",
    "smoothscale_surf_by": "from pygame.transform import smoothscale_by as smoothscale_surf_by",

    "Font": "from pygame.font import Font",
    "SysFont": "from pygame.font import SysFont",
    "Font.render": "from pygame.font import Font",
    "Font.size": "from pygame.font import Font",

    "Surface": "from pygame import Surface",
    "Surface.convert": "from pygame import Surface",
    "Surface.convert_alpha": "from pygame import Surface",
    "Surface.copy": "from pygame import Surface",
    "Surface.subsurface": "from pygame import Surface",
    "Surface.get_size": "from pygame import Surface",
    "Surface.get_width": "from pygame import Surface",
    "Surface.get_height": "from pygame import Surface",
    "Surface.get_rect": "from pygame import Surface",
    "Surface.get_bounding_rect": "from pygame import Surface",
    "Surface.get_at": "from pygame import Surface",
    "Surface.get_parent": "from pygame import Surface",
    "Surface.get_abs_parent": "from pygame import Surface",
    "Surface.get_offset": "from pygame import Surface",
    "Surface.get_abs_offset": "from pygame import Surface",

    "Rect(obj)": "from pygame import Rect",
    "Rect(topleft, size)": "from pygame import Rect",
    "Rect(left, top, width, height)": "from pygame import Rect",
    "Rect.copy": "from pygame import Rect",
    "Rect.move(delta)": "from pygame import Rect",
    "Rect.move(delta_x, delta_y)": "from pygame import Rect",
    "Rect.inflate(inflation)": "from pygame import Rect",
    "Rect.inflate(x_inflation, y_inflation)": "from pygame import Rect",
    "Rect.clamp": "from pygame import Rect",
    "Rect.clip": "from pygame import Rect",
    "Rect.union": "from pygame import Rect",
    "Rect.unionall": "from pygame import Rect",
    "Rect.fit": "from pygame import Rect",
    "Rect.contains": "from pygame import Rect",
    "Rect.collidepoint(point)": "from pygame import Rect",
    "Rect.collidepoint(x, y)": "from pygame import Rect",
    "Rect.colliderect": "from pygame import Rect",
}


### another small utility

string_stream = StringIO()


def get_help_text(callable_obj):
    content_length = len(string_stream.getvalue())

    with redirect_stdout(string_stream):
        help(callable_obj)

    return string_stream.getvalue()[content_length:].strip()



### map used for source view (viewing node source/info)

THIRDLIB_IDS_TO_SOURCE_VIEW_TEXT = {
    thirdlib_id: f'''
### signature used:

{getsource(THIRDLIB_IDS_TO_SIGNATURE_CALLABLES_MAP[thirdlib_id])}

### help text:

"""
{get_help_text(THIRDLIB_IDS_TO_CALLABLES_MAP[thirdlib_id])}
"""
'''.strip()
    for thirdlib_id in THIRDLIB_IDS_TO_MODULE.keys()
}

string_stream.close()
