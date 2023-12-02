
### third-party imports

from pygame import Surface

from pygame.draw import circle as draw_circle


def get_circle(
    color : {'widget_name': 'color_button', 'type': tuple} = (255, 0, 0),
    radius:int=2,
) -> [{'name': 'surface', 'type': Surface}]:
    """Return surface with circle drawn on it."""

    diameter = round(radius * 2)

    size = (diameter,) * 2

    surf = Surface(size).convert_alpha()
    surf.fill((0,)*4)

    draw_circle(surf, color, surf.get_rect().center, radius)

    return surf


main_callable = get_circle
