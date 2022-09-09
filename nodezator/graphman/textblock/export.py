"""Export support for the text block"""

### standard library import
from xml.etree.ElementTree import Element


### local imports

from ...textman.render import get_text_size

from ...syntaxman.utils import (
    SYNTAX_TO_MAPPING_FUNCTION,
    get_ready_theme,
)

from .constants import (
    OUTLINE_THICKNESS,
    FONT_HEIGHT,
)

from .constants import (
    FONT_HEIGHT,
    FONT_PATH,
)

from ...colorsman.colors import TEXT_BLOCK_OUTLINE


GENERAL_TEXT_KWARGS = {"font_height": FONT_HEIGHT, "font_path": FONT_PATH}

COMMENT_THEME_MAP = get_ready_theme("comment", GENERAL_TEXT_KWARGS)

get_syntax_map = SYNTAX_TO_MAPPING_FUNCTION["comment"]

TEXT_BLOCK_BG = COMMENT_THEME_MAP["background_color"]


TEXT_BLOCK_CSS = f"""
g.text_block > rect
{{
  fill         : rgb{TEXT_BLOCK_BG};
  stroke       : rgb{TEXT_BLOCK_OUTLINE};
  stroke-width : {OUTLINE_THICKNESS};
}}

g.text_block > text
{{font:bold {FONT_HEIGHT-3}px monospace;}}
"""


def svg_repr(self):
    """"""
    ### return element representing
    ### text block body

    deflation = OUTLINE_THICKNESS * 2

    rect = self.rect.inflate(
        -deflation,
        -deflation,
    )

    g = Element("g", {"class": "text_block"})

    g.append(
        Element(
            "rect",
            {
                attr_name: str(getattr(rect, attr_name))
                for attr_name in ("x", "y", "width", "height")
            },
        )
    )

    ###

    text = self.data["text"]
    highlight_data = get_syntax_map(text)

    lines = text.splitlines()

    x = rect.move(4, 4).x
    y = rect.y

    max_right = rect.right

    theme_text_settings = COMMENT_THEME_MAP["text_settings"]

    ## iterate over the visible lines and their
    ## indices, highlighting their text according
    ## to the highlighting data present

    for line_index, line_text in enumerate(lines, 0):

        y += FONT_HEIGHT

        ## try popping out the interval data from
        ## the highlight data dict with the line
        ## index

        try:
            interval_data = highlight_data.pop(line_index)

        ## if there is no such data, skip iteration
        ## of this item
        except KeyError:
            pass

        ## otherwise...
        else:

            string_kwargs_pairs = (
                (line_text[including_start:excluding_end], theme_text_settings[kind])
                for (including_start, excluding_end), kind in sorted(
                    interval_data.items(), key=lambda item: item[0]
                )
            )

            temp_x = x

            for string, text_settings in string_kwargs_pairs:

                x_increment, _ = get_text_size(
                    string,
                    font_height=FONT_HEIGHT,
                    font_path=FONT_PATH,
                )

                text_fg = text_settings["foreground_color"]

                style = f"fill:rgb{text_fg};"

                text_element = Element(
                    "text",
                    {
                        "x": str(temp_x),
                        "y": str(y),
                        "text-anchor": "start",
                        "style": style,
                    },
                )

                text_element.text = string

                g.append(text_element)

                temp_x += x_increment

    ###
    return g
