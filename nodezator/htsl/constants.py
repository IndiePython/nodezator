### local imports

from ..fontsman.constants import (
    NOTO_SANS_REGULAR_FONT_PATH,
    NOTO_SANS_BOLD_FONT_PATH,
    NOTO_SANS_ITALIC_FONT_PATH,
    NOTO_SANS_FONT_HEIGHT,
    NOTO_SANS_MONO_MEDIUM_FONT_PATH,
    NOTO_SANS_MONO_MEDIUM_FONT_HEIGHT,
)

from ..colorsman.colors import (
    HTSL_GENERAL_TEXT_FG,
    HTSL_HEADING_TEXT_FG,
    HTSL_CANVAS_BG,
    HTSL_MARKED_TEXT_BG,
)

### tags used in htsl

HEADING_TAGS = tuple(f"h{i}" for i in range(1, 7))

KNOWN_TAGS = (
    "p",
    *HEADING_TAGS,
    "python",
    "pre",
    "ol",
    "ul",
    "a",
    "img",
    "surfdef",
    "blockquote",
    "table",
    "dl",
)

### text settings

## anchor minus fg

ANCHOR_TEXT_SETTINGS_MINUS_FG = {
    "font_path": NOTO_SANS_REGULAR_FONT_PATH,
    "font_height": NOTO_SANS_FONT_HEIGHT,
    "background_color": HTSL_CANVAS_BG,
}

### normal text settings

NORMAL_TEXT_SETTINGS = {
    "font_path": NOTO_SANS_REGULAR_FONT_PATH,
    "font_height": NOTO_SANS_FONT_HEIGHT,
    "foreground_color": HTSL_GENERAL_TEXT_FG,
    "background_color": HTSL_CANVAS_BG,
}

BOLD_TEXT_SETTINGS = {
    "font_path": NOTO_SANS_BOLD_FONT_PATH,
    "font_height": NOTO_SANS_FONT_HEIGHT,
    "foreground_color": HTSL_GENERAL_TEXT_FG,
    "background_color": HTSL_CANVAS_BG,
}

ITALIC_TEXT_SETTINGS = {
    "font_path": NOTO_SANS_ITALIC_FONT_PATH,
    "font_height": NOTO_SANS_FONT_HEIGHT,
    "foreground_color": HTSL_GENERAL_TEXT_FG,
    "background_color": HTSL_CANVAS_BG,
}

MARKED_TEXT_SETTINGS = {
    "font_path": NOTO_SANS_REGULAR_FONT_PATH,
    "font_height": NOTO_SANS_FONT_HEIGHT,
    "foreground_color": HTSL_GENERAL_TEXT_FG,
    "background_color": HTSL_MARKED_TEXT_BG,
}

TAG_TO_TEXT_SETTINGS = {
    "b": BOLD_TEXT_SETTINGS,
    "strong": BOLD_TEXT_SETTINGS,
    "i": ITALIC_TEXT_SETTINGS,
    "em": ITALIC_TEXT_SETTINGS,
}

### heading text settings

HEADING_TEXT_SETTINGS_MINUS_HEIGHT = {
    "font_path": NOTO_SANS_BOLD_FONT_PATH,
    "foreground_color": HTSL_HEADING_TEXT_FG,
    "background_color": HTSL_CANVAS_BG,
}


HEADING_TO_FONT_HEIGHT = {}

for i in range(1, 7):

    exec(
        f"""H{i}_FONT_HEIGHT = (

        NOTO_SANS_FONT_HEIGHT
        + ( 24 + (i * -3) )

      )
      """.strip()
    )

    exec(
        f"""HEADING_TO_FONT_HEIGHT['h{i}'] = (
        H{i}_FONT_HEIGHT
      )
      """.strip()
    )


### general code text settings

GENERAL_CODE_TEXT_SETTINGS = {
    "font_height": NOTO_SANS_MONO_MEDIUM_FONT_HEIGHT,
    "font_path": NOTO_SANS_MONO_MEDIUM_FONT_PATH,
    "foreground_color": (235, 235, 235),
    "background_color": (15, 15, 15),
}

PRE_TEXT_SETTINGS = {
    "font_height": NOTO_SANS_MONO_MEDIUM_FONT_HEIGHT,
    "font_path": NOTO_SANS_MONO_MEDIUM_FONT_PATH,
    "foreground_color": (15, 15, 15),
    "background_color": (230, 230, 235),
}

PRE_TEXT_BORDER = (145, 145, 145)
