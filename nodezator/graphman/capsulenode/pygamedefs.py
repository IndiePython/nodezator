
### standard library import
from collections.abc import Iterable


### third-party imports

from pygame import Surface, Rect

from pygame import locals as pygame_ce_locals

from pygame.color import Color

from pygame.font import Font



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


def blit_surf_a_on_b(
    surf_a: Surface,
    surf_b: Surface,
    topleft_or_rect: { 
        'widget_name': 'literal_entry',
        'type': (tuple, list, Rect),
    } = (0, 0),
    area=None,
    special_flags=0,
) -> [
    {'name': 'surf_b', 'type': Surface},
    {'name': 'affected_rect', 'type': Rect},
]:
    """Draw surface a onto b and return affected area and surface b."""
    affected_rect = surf_b.blit(surf_a, topleft_or_rect, area, special_flags)

    return {
        'surf_b': surf_b,
        'affected_rect': affected_rect,
    }

def blit_a_on_b_aligned(
    surf_a: Surface,
    surf_b: Surface,
    pos_from_b : {
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
    pos_to_a : {
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
    area=None,
    special_flags=0,
) -> [
    {'name': 'surf_b', 'type': Surface},
    {'name': 'affected_rect', 'type': Rect},
]:
    """Draw surface a onto b and return affected area and surface b."""
    rect_a, rect_b = surf_a.get_rect(), surf_b.get_rect()

    pos = getattr(rect_b.move(offset_pos_by), pos_from_b)
    setattr(rect_a, pos_to_a, pos)

    affected_rect = surf_b.blit(surf_a, rect_a, area, special_flags)

    return {
        'surf_b': surf_b,
        'affected_rect': affected_rect,
    }



def get_aligned_rects(
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
) -> [
    {'name': 'union_surf', 'type': Surface},
]:
    """Return union of surfaces positioned with given rects.

    The generated image has per pixel alphas (it is generated with
    Surface.convert_alpha and made fully transparent before drawing
    the given surfaces on it) so you might want to convert it back
    afterwards with Surface.convert().
    """
    ### create union rect and surface

    first, *remaining = rects

    union_rect = first.unionall(remaining)

    union_surf = Surface(union_rect.size).convert_alpha()
    union_surf.fill((0, 0, 0, 0)) # make fully transparent

    ### position and blit surfaces on union

    offset = tuple(-coordinate for coordinate in union_rect.topleft)

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
    {'name': 'surface', 'type': Surface},
    {'name': 'affected_rect', 'type': Rect},
]:
    """Fill surface and return affected area and surface itself."""
    affected_rect = surface.fill(color, rect, special_flags)

    return {
        'surface': surface,
        'affected_rect': affected_rect,
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
    """Return new larger surface with added border.

    The generated image has per pixel alphas (it is generated with
    Surface.convert_alpha and made fully transparent before drawing
    the border) so you might want to convert it back afterwards
    with Surface.convert().
    """
    ### create larger surface with added thickness and fully
    ### transparent

    new_size = (
        ## get rect
        surface.get_rect()
        ## inflate it
        .inflate(thickness*2, thickness*2)
        ## grab size
        .size
    )

    larger_surf = Surface(new_size).convert_alpha()
    larger_surf.fill((0, 0, 0, 0)) # make fully transparent

    ### fill only border areas

    rect = larger_surf.get_rect()

    for border_rect in (

        # top border
        (*rect.topleft, rect.width, thickness),

        # bottom border
        (*rect.move(0, -thickness).bottomleft,
        rect.width, thickness),

        # left border
        (*rect.move(0, thickness).topleft,
        thickness, rect.height - (thickness*2)),

        # right border
        (*rect.move(-thickness, thickness).topright,
        thickness, rect.height - (thickness*2)),

    ):
        larger_surf.fill(color, border_rect)

    ### blit original surface on larger one
    larger_surf.blit(surface, (thickness, thickness))

    ### return larger surf
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

    ### fill only border areas

    rect = surface.get_rect()

    for border_rect in (

        # top border
        (*rect.topleft, rect.width, thickness),

        # bottom border
        (*rect.move(0, -thickness).bottomleft,
        rect.width, thickness),

        # left border
        (*rect.move(0, thickness).topleft,
        thickness, rect.height - (thickness*2)),

        # right border
        (*rect.move(-thickness, thickness).topright,
        thickness, rect.height - (thickness*2)),

    ):
        surface.fill(color, border_rect)


    ### return surface
    return surface

def decrease_surf_border(
    surface: Surface,
    thickness: 'positive_integer' = 1,
) -> [
    {'name': 'smaller_surface', 'type': Surface},
]:
    """Return smaller surface by cropping inner rectangle."""
    return surface.subsurface(
        surface.get_rect().inflate((thickness*-2,)*2)
    ).copy()

def crop_surface(
    surface: Surface,
    cropping_rect: Rect,
) -> [
    {'name': 'cropped_surface', 'type': Surface},
]:
    """Return new surface from rect cropped from given surface."""
    return surface.subsurface(cropping_rect).copy()


def render_text_surface(
    font_obj: Font,
    text: str = "text",
    antialiased: bool = True,
    padding: 'natural_number'=0,
    foreground_color: {
        'widget_name': 'color_button',
        'widget_kwargs': {'color_format': 'rgb_tuple'},
        'type': (tuple, list, str, Color),
    } = (0, 0, 0),
    background_color: {
        'widget_name': 'color_button',
        'widget_kwargs': {'color_format': 'rgb_tuple'},
        'type': (tuple, list, str, Color, None),
    } = (255, 255, 255, 0),
    wraplength: 'natural_number' = 0,
) -> [
    {'name': 'text_surface', 'type': Surface},
]:
    """Return surface representing rendered text.

    Can render text surfaces with semitransparent backgrounds
    (rather than only zero or full transparency).
    """
    ### use a fully transparent color if background color is None
    if background_color is None:
        background_color = (0, 0, 0, 0)

    ### define whether the background has transparency

    try:
        has_transparency = background_color[3] < 255
    except IndexError:
        has_transparency = False

    ### if no padding was requested nor there's transparency
    ### in the background, just render the surf right away

    if not padding and not has_transparency:

        surf = font_obj.render(
            text, antialiased, foreground_color, background_color, wraplength
        ).convert()

    else:

        ### render the text surface without background
        text_surf = font_obj.render(
            text, antialiased, foreground_color, None, wraplength
        ).convert_alpha()

        ### if padding was requested

        if padding:

            ## calculate new width and height

            width, height = (
                dimension + (padding * 2) for dimension in text_surf.get_size()
            )

            ## create new background surface with appropriate
            ## color according to presence of transparency

            surf = (
                Surface((width, height)).convert_alpha()
                if has_transparency
                else Surface((width, height)).convert()
            )

            surf.fill(background_color)

            ## blit text surf on new surf taking the padding
            ## into account
            surf.blit(text_surf, (padding, padding))

        ### otherwise, we assume the background has transparency and create
        ### such transparent background for our text surface

        else:

            surf = Surface(text_surf.get_size()).convert_alpha()

            surf.fill(background_color)
            surf.blit(text_surf, (0, 0))

    ### finally return the surf
    return surf
