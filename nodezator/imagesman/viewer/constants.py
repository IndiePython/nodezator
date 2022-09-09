"""Constants for the image viewer."""

### local imports

from ...pygameconstants import SCREEN_RECT

from ...classes2d.single import Object2D
from ...classes2d.collections import List2D

from ...fontsman.constants import ENC_SANS_BOLD_FONT_HEIGHT, ENC_SANS_BOLD_FONT_PATH

from ...textman.label.main import Label

from ...textman.render import render_text

from ..cache import CachedImageObject

from ...surfsman.render import combine_surfaces

from ...surfsman.icon import render_layered_icon

from ...colorsman.colors import (
    BLACK,
    WHITE,
    IMAGES_VIEWER_FG,
    IMAGES_VIEWER_BG,
    THUMB_BG,
)


VIEWER_BORDER_THICKNESS = 2
VIEWER_PADDING = 5

LARGE_THUMB_WIDTH = 800
LARGE_THUMB_HEIGHT = 424

SMALL_THUMB_WIDTH = 153
SMALL_THUMB_HEIGHT = 153


###

VIEWER_OBJS = List2D()

image_icon = render_layered_icon(
    chars=[chr(ordinal) for ordinal in (38, 40, 41, 39)],
    dimension_name="height",
    dimension_value=26,
    colors=[BLACK, BLACK, WHITE, (30, 130, 70)],
)

eye_icon = render_layered_icon(
    chars=[chr(ordinal) for ordinal in (87, 88, 89)],
    dimension_name="height",
    dimension_value=21,
    colors=[BLACK, WHITE, (115, 40, 30)],
)

VIEWER_ICON = Object2D.from_surface(
    combine_surfaces(
        surfaces=[image_icon, eye_icon],
        retrieve_pos_from="bottomright",
        assign_pos_to="bottomright",
        offset_pos_by=(10, 5),
        padding=2,
    )
)

VIEWER_OBJS.append(VIEWER_ICON)

VIEWER_CAPTION = Object2D.from_surface(
    render_text(
        text="Images Viewer",
        font_height=ENC_SANS_BOLD_FONT_HEIGHT,
        font_path=ENC_SANS_BOLD_FONT_PATH,
        padding=5,
        foreground_color=IMAGES_VIEWER_FG,
        background_color=IMAGES_VIEWER_BG,
    )
)


VIEWER_OBJS.append(VIEWER_CAPTION)

VIEWER_OBJS.rect.snap_rects_ip(
    retrieve_pos_from="midright", assign_pos_to="midleft", offset_pos_by=(2, 0)
)

###

LARGE_THUMB_SETTINGS = {
    "use_alpha": True,
    "max_width": LARGE_THUMB_WIDTH,
    "max_height": LARGE_THUMB_HEIGHT,
    "keep_size_ratio": True,
    "checkered_alpha": True,
    "background_width": LARGE_THUMB_WIDTH,
    "background_height": LARGE_THUMB_HEIGHT,
    "background_color": THUMB_BG,
    "retrieve_pos_from": "center",
    "assign_pos_to": "center",
    "offset_pos_by": (0, 0),
    "not_found_width": LARGE_THUMB_WIDTH,
    "not_found_height": LARGE_THUMB_HEIGHT,
}

LARGE_THUMB = CachedImageObject(image_path=".", image_settings=LARGE_THUMB_SETTINGS)

LARGE_THUMB.rect.topleft = VIEWER_OBJS.rect.move(0, 5).bottomleft
VIEWER_OBJS.append(LARGE_THUMB)


SMALL_THUMB_SETTINGS = {
    "use_alpha": True,
    "max_width": SMALL_THUMB_WIDTH,
    "max_height": SMALL_THUMB_HEIGHT,
    "keep_size_ratio": True,
    "checkered_alpha": True,
    "background_width": SMALL_THUMB_WIDTH,
    "background_height": SMALL_THUMB_HEIGHT,
    "background_color": THUMB_BG,
    "retrieve_pos_from": "center",
    "assign_pos_to": "center",
    "offset_pos_by": (0, 0),
    "not_found_width": SMALL_THUMB_WIDTH,
    "not_found_height": SMALL_THUMB_HEIGHT,
}

SMALL_THUMB = CachedImageObject(image_path=".", image_settings=SMALL_THUMB_SETTINGS)


SMALL_THUMB.rect.topleft = VIEWER_OBJS.rect.move(0, 5).bottomleft

VIEWER_OBJS.append(SMALL_THUMB)


PATH_LABEL = Label(
    text="dummy text",
    font_height=ENC_SANS_BOLD_FONT_HEIGHT,
    font_path=ENC_SANS_BOLD_FONT_PATH,
    padding=2,
    max_width=LARGE_THUMB_WIDTH,
    foreground_color=IMAGES_VIEWER_FG,
    background_color=IMAGES_VIEWER_BG,
    ellipsis_at_end=False,
)

PATH_LABEL.rect.topleft = VIEWER_OBJS.rect.bottomleft
VIEWER_OBJS.append(PATH_LABEL)

##

VIEWER_OBJS.rect.center = SCREEN_RECT.center

AMOUNT_TO_INFLATE = (VIEWER_BORDER_THICKNESS + VIEWER_PADDING) * 2

VIEWER_RECT = VIEWER_OBJS.rect.inflate(AMOUNT_TO_INFLATE, AMOUNT_TO_INFLATE)
