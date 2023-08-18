
### standard library import
from collections.abc import Iterable


### third-party imports

from pygame import Surface, Rect

from pygame import locals as pygame_ce_locals

from pygame.draw import rect as draw_rect_on_surf

from pygame.color import Color



def color_surf_from_size(
    size: {'widget_name': 'literal_entry', 'type': tuple} = (256, 256),
    color: {
        'widget_name': 'color_button',
        'widget_kwargs': {'color_format': 'rgb_tuple'},
        'type': (tuple, list, str, Color),
    } = (255, 0, 0),
) -> [
    {'name': 'surface', 'type': Surface},
]:
    """Return surface of given color.

    Parameters
    ==========
    size (sequence of integers)
        Size of surface to be created
    color (string or sequence of RGB(A) integers in range(256))
        If string must be the name of a color. Regardless of
        whether it is a string or sequence of integers, it must be
        accepted by pygame.Surface.fill().

        If color is a sequence of integers and has an alpha value
        (fourth value) which is less than 255, the surface is
        converted with pygame.Surface.convert_alpha(), in all other
        scenarios it is converted with pygame.Surface.convert().
    """
    surf = Surface(size)

    if not isinstance(color, str):

        try:
            alpha = color[3]

        except IndexError:
            surf = surf.convert()

        else:

            if alpha < 255:
                surf = surf.convert_alpha()
            else:
                surf = surf.convert()

    else:
        surf = surf.convert()

    surf.fill(color)

    return surf


def color_surf_from_wh(
    width: 'natural_number' = 256,
    height: 'natural_number' = 256,
    color: {
        'widget_name': 'color_button',
        'widget_kwargs': {'color_format': 'rgb_tuple'},
        'type': (tuple, list, str, Color),
    } = (255, 0, 0),
) -> [
    {'name': 'surface', 'type': Surface},
]:
    """Return surface of given color.

    Parameters
    ==========
    width, height (integers)
        Size of surface to be created
    color (string or sequence of RGB(A) integers in range(256))
        If string must be the name of a color. Regardless of
        whether it is a string or sequence of integers, it must be
        accepted by pygame.Surface.fill().

        If color is a sequence of integers and has an alpha value
        (fourth value) which is less than 255, the surface is
        converted with pygame.Surface.convert_alpha(), in all other
        scenarios it is converted with pygame.Surface.convert().
    """
    surf = Surface((width, height))

    if not isinstance(color, str):

        try:
            alpha = color[3]

        except IndexError:
            surf = surf.convert()

        else:

            if alpha < 255:
                surf = surf.convert_alpha()
            else:
                surf = surf.convert()

    else:
        surf = surf.convert()

    surf.fill(color)

    return surf


def get_pygame_constant(constant_name: str = '') -> [{'name': 'value'}]:
    """Return pygame constant by retrieving given name from pygame.locals."""
    return getattr(pygame_ce_locals, constant_name)


def blit_surf_a_onto_b(
    surf_a: Surface,
    surf_b: Surface,
    topleft_or_rect: (tuple, list, Rect),
    area=None,
    special_flags=0,
) -> [
    {'name': 'affected_rect', 'type': Rect},
    {'name': 'surf_b', 'type': Surface},
]:
    """Draw surface a onto b and return affected area and surface b."""
    affected_rect = surf_b.blit(surf_a, topleft_or_rect, area, special_flags)

    return {
        'affected_rect': affected_rect,
        'surf_b': surf_b,
    }



def get_positioned_rects(
    surfaces:Iterable,
    retrieve_pos_from : {
        'widget_name': 'option_menu',
        'widget_kwargs': {
            'options': [
                'topleft', 'topright', 'bottomleft', 'bottomright',
                'midleft', 'midright', 'midtop', 'midbottom',
                'center'
            ]
        },
        'type': str,
    } = 'center',
    assign_pos_to : {
        'widget_name': 'option_menu',
        'widget_kwargs': {
            'options': [
                'topleft', 'topright', 'bottomleft', 'bottomright',
                'midleft', 'midright', 'midtop', 'midbottom',
                'center'
            ]
        },
        'type': str,
    } = 'center',
    offset_pos_by: 'python_literal' = (0, 0),
) -> [
    {'name': 'rects', 'type': list}
]:
    """Return list of rects positioned relative to each other."""

    rects = [surf.get_rect() for surf in surfaces]

    rects_copy = rects.copy()

    rects.reverse()

    while True:

        pos = getattr(rects.pop().move(offset_pos_by), retrieve_pos_from)

        if rects:

            setattr(rects[-1], assign_pos_to, pos)
            continue

        break

    return rects_copy


def unite_surfaces(
    surfaces: Iterable,
    rects: Iterable,
    padding: 'natural_number' = 0,
    background_color: {
        'widget_name': 'color_button',
        'widget_kwargs': {'color_format': 'rgb_tuple'},
        'type': (tuple, list, str, Color),
    } = (0, 0, 0, 0),
) -> [
    {'name': 'union_surf', 'type': Surface},
]:
    """Return union of surfaces positioned with given rects."""
    ### create union rect and surface

    first, *remaining = rects

    union_rect = (
        ## unit rects
        first
        .unionall(remaining)
        ## inflate union
        .inflate(padding*2, padding*2)
    )

    union_surf = Surface(union_rect.size)

    ### fill union surface

    if not isinstance(background_color, str):

        try:
            alpha = background_color[3]

        except IndexError:
            union_surf = union_surf.convert()

        else:

            if alpha < 255:
                union_surf = union_surf.convert_alpha()
            else:
                union_surf = union_surf.convert()

    else:
        union_surf = surf.convert()

    union_surf.fill(background_color)

    ### position and blit surfaces on union

    offset = tuple(-coordinate for coordinate in union_rect.topleft)

    union_rect.move_ip(offset)

    for surf, rect in zip(surfaces, rects):
        union_surf.blit(surf, rect.move(offset))

    ### finally return it
    return union_surf


def fill_surface(
    surface: Surface,
    color: {
        'widget_name': 'color_button',
        'widget_kwargs': {'color_format': 'rgb_tuple'},
        'type': (tuple, list, str, Color),
    } = (255, 0, 0),
    rect: (Rect, type(None)) = None,
    special_flags=0,
) -> [
    {'name': 'affected_rect', 'type': Rect},
    {'name': 'surface', 'type': Surface},
]:
    """Fill surface and return affected area and surface itself."""
    affected_rect = surface.fill(color, rect, special_flags)

    return {
        'affected_rect': affected_rect,
        'surface': surface,
    }


def increase_surf_border(
    surface: Surface,
    color: {
        'widget_name': 'color_button',
        'widget_kwargs': {'color_format': 'rgb_tuple'},
        'type': (tuple, list, str, Color),
    } = (0, 0, 0),
    thickness: 'positive_integer' = 1,
) -> [
    {'name': 'larger_surface', 'type': Surface},
]:
    """Return new larger surface with added border."""
    new_size = (
        ## get rect
        surface.get_rect()
        ## inflate it
        .inflate(thickness*2, thickness*2)
        ## grab size
        .size
    )

    larger_surf = Surface(new_size)

    if not isinstance(color, str):

        try:
            alpha = color[3]

        except IndexError:
            larger_surf = larger_surf.convert()

        else:

            if alpha < 255:
                larger_surf = larger_surf.convert_alpha()
            else:
                larger_surf = larger_surf.convert()

    else:
        larger_surf = larger_surf.convert()

    larger_surf.fill(color)

    larger_surf.blit(surface, (thickness, thickness))

    return larger_surf


def draw_border_on_surf(
    surface: Surface,
    color: {
        'widget_name': 'color_button',
        'widget_kwargs': {'color_format': 'rgb_tuple'},
        'type': (tuple, list, str, Color),
    } = (0, 0, 0),
    thickness: 'positive_integer' = 1,
) -> [
    {'name': 'surface', 'type': Surface},
]:
    """Draw border on surface edges and return surface."""

    rect = surface.get_rect()

    for _ in range(thickness):

        draw_rect_on_surf(surface, color, rect, 1)
        rect.size = tuple(dimension - 2 for dimension in rect.size)
        rect.move_ip(1, 1)

    return surface
