
### third-party import
from pygame import Surface


def get_rectangle(
    color : {'widget_name': 'color_button', 'type': tuple} = (255, 0, 0),
    width:int=100,
    height: int=100,
) -> [{'name': 'surface', 'type': Surface}]:
    """Return surface representing rectangle."""

    surf = Surface((width, height)).convert_alpha()
    surf.fill(color)

    return surf

main_callable = get_rectangle
