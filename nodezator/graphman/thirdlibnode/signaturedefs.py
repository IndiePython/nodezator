"""Facility with signature function definitions.

That is, functions whose signatures will be used to represent
imported callables.
"""

### standard library imports
from collections.abc import Sequence


### third-party imports

from pygame import Rect, Surface

from pygame.math import Vector2

from pygame.color import Color

from pygame.font import Font





### signatures for functions from pygame.image


def _load_image_as_surf(
    filename_or_fileobj: 'image_path' = '.',
    namehint:str='',
) -> [
    {'name': 'surface', 'type': Surface}
]:
    pass


def _save_surf_to_file(
    surface: Surface,
    filename_or_fileobj: 'image_path' = '.',
    namehint:str='',
):
    pass

def _surf_from_bytes(
    image_bytes: bytes,
    size: {'widget_name': 'literal_entry', 'type': tuple} = (256, 256),
    format: {
        'widget_name': 'option_menu',
        'widget_kwargs': {
            'options': [
                'P',
                'RGB',
                'RGBX',
                'RGBA',
                'ARGB',
                'BGRA',
                'RGBA_PREMULT',
                'ARGB_PREMULT',
            ],
        },
        'type': str,
    } = 'RGB',
    flipped: bool = False,
) -> [
    {'name': 'surface', 'type': Surface}
]:
    pass

def _surf_to_bytes(
    surface: Surface,
    format: {
        'widget_name': 'option_menu',
        'widget_kwargs': {
            'options': [
                'P',
                'RGB',
                'RGBX',
                'RGBA',
                'ARGB',
                'BGRA',
                'RGBA_PREMULT',
                'ARGB_PREMULT',
            ],
        },
        'type': str,
    } = 'RGB',
    flipped: bool = False,
) -> [
    {'name': 'image_bytes', 'type': bytes}
]:
    pass





### signatures for functions from pygame.transform


def _flip_surface(
    surface: Surface,
    flip_x: bool = False,
    flip_y: bool = False,
) -> [
    {'name': 'new_surface', 'type': Surface}
]:
    pass


def _scale_surface(
    surface: Surface,
    size: {'widget_name': 'literal_entry', 'type': (Sequence, Vector2)} = (256, 256),
) -> [
    {'name': 'new_surface', 'type': Surface}
]:
    pass


def _scale_surface_by(
    surface: Surface,
    factor: {'widget_name': 'literal_entry', 'type': (int, float, Sequence, Vector2)} = 1,
) -> [
    {'name': 'new_surface', 'type': Surface}
]:
    pass


def _rotate_surface(
    surface: Surface,
    angle: float = 0.,
) -> [
    {'name': 'new_surface', 'type': Surface}
]:
    pass


def _rotozoom_surface(
    surface: Surface,
    angle: float = 0.,
    scale: float = 1.,
) -> [
    {'name': 'new_surface', 'type': Surface}
]:
    pass


def _scale2x_surface(surface: Surface) -> [
    {'name': 'new_surface', 'type': Surface}
]:
    pass


def _smoothscale_surface(
    surface: Surface,
    size: {'widget_name': 'literal_entry', 'type': (Sequence, Vector2)} = (256, 256),
) -> [
    {'name': 'new_surface', 'type': Surface}
]:
    pass


def _smoothscale_surf_by(
    surface: Surface,
    factor: {'widget_name': 'literal_entry', 'type': (int, float, Sequence, Vector2)} = 1,
) -> [
    {'name': 'new_surface', 'type': Surface}
]:
    pass



### signatures for callables from pygame.font

def _font(
    filepath: {
        'widget_name': 'font_preview',
        'type': (str, type(None))
    } = '.',
    size: 'natural_number' = 20,
) -> [
    {'name': 'font_obj', 'type': Font}
]:
    pass

def _sysfont(
    name: str = 'Arial',
    size: 'natural_number' = 20,
    bold: bool = False,
    italic: bool = False,
) -> [
    {'name': 'font_obj', 'type': Font}
]:
    pass


def _font_render(
    font_obj: Font,
    text: str = 'text',
    antialias: bool = True,
    foreground_color: {
        'widget_name': 'color_button',
        'widget_kwargs': {'color_format': 'rgb_tuple'},
        'type': (tuple, list, str, Color),
    } = (0, 0, 0),
    background_color: {
        'widget_name': 'color_button',
        'widget_kwargs': {'color_format': 'rgb_tuple'},
        'type': (tuple, list, str, Color, type(None)),
    } = (255, 255, 255),
    wraplength: 'natural_number' = 0,
) -> [
    {'name': 'text_surface', 'type': Surface}
]:
    pass

def _font_size(
    font_obj: Font,
    text: str = 'text',
) -> [
    {'name': 'size', 'type': tuple}
]:
    pass


### signatures for pygame.Surface and its methods


def _surface(
    size: {'widget_name': 'literal_entry', 'type': tuple} = (256, 256)
) -> [
    {'name': 'surface', 'type': Surface}
]:
    pass

def _surface_convert(surface:Surface) -> [
    {'name': 'conv_surface', 'type': Surface}
]:
    pass

def _surface_alpha_convert(surface: Surface) -> [
    {'name': 'alphaconv_surface', 'type': Surface}
]:
    pass

def _surface_copy(surface: Surface) -> [
    {'name': 'surface_copy', 'type': Surface}
]:
    pass

def _surface_subsurface(surface: Surface, rect: (Sequence, Rect)) -> [
    {'name': 'subsurface', 'type': Surface}
]:
    pass

def _surface_get_size(surface: Surface) -> [
    {'name': 'size', 'type': tuple}
]:
    pass

def _surface_get_width(surface: Surface) -> [
    {'name': 'width', 'type': int}
]:
    pass

def _surface_get_height(surface: Surface) -> [
    {'name': 'height', 'type': int}
]:
    pass

def _surface_get_rect(surface: Surface) -> [
    {'name': 'rect', 'type': Rect}
]:
    pass

def _surface_get_bounding_rect(surface: Surface, min_alpha:int=1) -> [
    {'name': 'bounding_rect', 'type': Rect}
]:
    pass

def _surface_get_at(
    surface: Surface,
    pixel_coordinates: 'python_literal' = (0, 0),
) -> [
    {'name': 'color', 'type': Color}
]:
    pass

def _surface_get_parent(surface: Surface) -> [
    {'name': 'parent_surf_or_none', 'type': (Surface, type(None))}
]:
    pass

def _surface_get_abs_parent(surface: Surface) -> [
    {'name': 'top_parent_or_self', 'type': Surface}
]:
    pass

def _surface_get_offset(surface: Surface) -> [
    {'name': 'pos_from_parent', 'type': tuple}
]:
    pass

def _surface_get_abs_offset(surface: Surface) -> [
    {'name': 'pos_from_top_parent', 'type': tuple}
]:
    pass





### signatures for pygame.Rect and its methods


def _rect1(obj) -> [{'name': 'rect', 'type': Rect}]:
    pass

def _rect2(
    topleft: {'widget_name': 'literal_entry', 'type': (Sequence, Vector2)} = (0, 0),
    size: {'widget_name': 'literal_entry', 'type': (Sequence, Vector2)} = (256, 256),
) -> [
    {'name': 'rect', 'type': Rect}
]:
    pass

def _rect3(
    left: int = 0,
    top: int = 0,
    width: int = 256,
    height: int = 256,
) -> [
    {'name': 'rect', 'type': Rect}
]:
    pass


def _rect_copy(rect:Rect) -> [{'name': 'rect', 'type': Rect}]:
    pass

def _rect_move1(
    rect: Rect,
    delta: {'widget_name': 'literal_entry', 'type': (Sequence, Vector2)} = (0, 0),
) -> [
    {'name': 'moved_rect', 'type': Rect},
]:
    pass

def _rect_move2(
    rect: Rect,
    delta_x: int = 0,
    delta_y: int = 0,
) -> [
    {'name': 'moved_rect', 'type': Rect},
]:
    pass

def _rect_inflate1(
    rect: Rect,
    inflation: {'widget_name': 'literal_entry', 'type': (Sequence, Vector2)} = (0, 0),
) -> [
    {'name': 'inflated_rect', 'type': Rect},
]:
    pass


def _rect_inflate2(
    rect: Rect,
    x_inflation: int = 0,
    y_inflation: int = 0,
) -> [
    {'name': 'inflated_rect', 'type': Rect},
]:
    pass

def _rect_clamp(
    rect_to_clamp: Rect,
    clamping_area: (Sequence, Rect),
) -> [
    {'name': 'clamped_rect', 'type': Rect},
]:
    pass

def _rect_clip(
    rect_to_clip: Rect,
    clipping_area: (Sequence, Rect),
) -> [
    {'name': 'clipped_rect', 'type': Rect},
]:
    pass

def _rect_union(
    rect_a: Rect,
    rect_b: (Sequence, Rect),
) -> [
    {'name': 'union_rect', 'type': Rect},
]:
    pass

def _rect_unionall(
    rect: Rect,
    rect_sequence: Sequence,
) -> [
    {'name': 'union_rect', 'type': Rect},
]:
    pass


def _rect_fit(
    rect_to_fit: Rect,
    fitting_area: (Sequence, Rect),
) -> [
    {'name': 'fitted_rect', 'type': Rect},
]:
    pass

def _rect_contains(
    testing_area: Rect,
    tested_rect: (Sequence, Rect),
) -> [
    {'name': 'totally_inside', 'type': bool},
]:
    pass

def _rect_collidepoint1(
    rect: Rect,
    point: {'widget_name': 'literal_entry', 'type': (Sequence, Vector2)} = (0, 0),
) -> [
    {'name': 'inside_rect', 'type': bool},
]:
    pass

def _rect_collidepoint2(
    rect: Rect,
    x: int = 0,
    y: int = 0,
) -> [
    {'name': 'inside_rect', 'type': bool},
]:
    pass

def _rect_colliderect(
    rect_a: Rect,
    rect_b: (Sequence, Rect),
) -> [
    {'name': 'collide', 'type': bool},
]:
    pass
