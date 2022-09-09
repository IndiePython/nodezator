"""Common surfaces for the file manager bookmark panel."""

### third-party import
from pygame.draw import line as draw_line

### local imports

from ...surfsman.icon import render_layered_icon

from ...colorsman.colors import BLACK


BOOKMARK_BUTTON_SURF = render_layered_icon(
    chars=[chr(ordinal) for ordinal in (54, 55)],
    dimension_name="height",
    dimension_value=22,
    colors=[BLACK, (30, 130, 70)],
    background_width=24,
    background_height=24,
)

UNBOOKMARK_BUTTON_SURF = BOOKMARK_BUTTON_SURF.copy()

rect = UNBOOKMARK_BUTTON_SURF.get_rect()

draw_line(
    UNBOOKMARK_BUTTON_SURF,
    (255, 0, 0),
    rect.move(-4, 4).topright,
    rect.move(4, -4).bottomleft,
    2,
)
