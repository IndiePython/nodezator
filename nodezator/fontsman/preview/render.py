"""Font render utilities."""

### third-party imports

from pygame import error as PygameError

from pygame.font import Font


### local imports

from ...classes2d.single import Object2D

from ...classes2d.collections import List2D

from ...surfsman.render import render_rect

from ...surfsman.draw import (
    draw_not_found_icon,
)

from ...colorsman.colors import (
    BLACK,
    WHITE,
    IMAGE_NOT_FOUND_FG,
    IMAGE_NOT_FOUND_BG,
)


### TODO finish/refactor this


def render_font_preview(
    font_path,
    font_size,
    chars,
    width,
    height,
    not_found_width=0,
    not_found_height=0,
):
    """Return surface with given chars."""

    ###
    try:

        font = Font(font_path, font_size)

        render = font.render

        char_objs = List2D(
            Object2D.from_surface(
                render(
                    char,
                    True,
                    BLACK,
                    WHITE,
                )
            )
            for char in chars
        )

    except (
        FileNotFoundError,
        IsADirectoryError,
        PygameError,
        PermissionError,
    ):

        ### if width and height in case the image file
        ### wasn't found were provided, create a surface
        ### with an drawing indicating the image wasn't
        ### found

        if not_found_width and not_found_height:

            surf = render_rect(
                not_found_width,
                not_found_height,
                IMAGE_NOT_FOUND_BG,
            )

            draw_not_found_icon(surf, IMAGE_NOT_FOUND_FG)

            return surf

        ### otherwise reraise the exception
        else:
            raise

    ###

    char_objs.rect.snap_rects_intermittently_ip(
        dimension_name="width",
        dimension_unit="pixels",
        max_dimension_value=width,
        retrieve_pos_from="topright",
        assign_pos_to="topleft",
        intermittent_pos_from="bottomleft",
        intermittent_pos_to="topleft",
    )

    surf = render_rect(width, height, WHITE)

    for char_obj in char_objs:
        surf.blit(char_obj.image, char_obj.rect)

    return surf
