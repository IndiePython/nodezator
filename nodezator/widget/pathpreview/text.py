"""Facility for widget to preview text(s) from path(s)."""

### standard library imports

from pathlib import Path

from xml.etree.ElementTree import Element


### third-party import
from pygame.draw import rect as draw_rect


### local imports

from ...dialog import create_and_show_dialog

from ...logman.main import get_new_logger

from ...our3rdlibs.userlogger import USER_LOGGER

from ...textman.viewer.main import view_text

from ...surfsman.draw import (
    draw_depth_finish,
    draw_not_found_icon,
)

from ...surfsman.icon import render_layered_icon

from ...fontsman.constants import (
    FIRA_MONO_BOLD_FONT_PATH,
    FIRA_MONO_BOLD_FONT_HEIGHT,
)

from ...textman.render import (
    fit_text,
    get_text_size,
    render_text,
)

from ...textman.text import render_highlighted_line

from ...colorsman.colors import (
    BLACK,
    WHITE,
    TEXTPREVIEW_FG,
    TEXTPREVIEW_BG,
)

from .base import _BasePreview

from .constants import (
    SP_BUTTON_SURFS,
    SP_BUTTON_RECTS,
    BUTTON_WIDTH,
    BUTTON_HEIGHT,
    SP_BUTTON_SVG_REPRS,
    SP_BUTTON_CALLABLE_NAMES,
    get_missing_path_repr,
)

from ...syntaxman.utils import (
    SYNTAX_TO_MAPPING_FUNCTION,
    get_ready_theme,
)

from ...syntaxman.exception import SyntaxMappingError


GENERAL_TEXT_SETTINGS = {
    "font_height": FIRA_MONO_BOLD_FONT_HEIGHT,
    "font_path": FIRA_MONO_BOLD_FONT_PATH,
    "foreground_color": TEXTPREVIEW_FG,
    "background_color": TEXTPREVIEW_BG,
}

### create logger for module
logger = get_new_logger(__name__)


### class definition


class TextPreview(_BasePreview):

    height = 163 + 20

    button_rects = SP_BUTTON_RECTS

    button_callable_names = SP_BUTTON_CALLABLE_NAMES

    button_surfs = list(SP_BUTTON_SURFS)

    button_surfs[1] = render_layered_icon(
        chars=[chr(ordinal) for ordinal in (37, 36)],
        dimension_name="height",
        dimension_value=18,
        colors=[BLACK, WHITE],
        background_width=BUTTON_WIDTH,
        background_height=BUTTON_HEIGHT,
    )

    ###

    button_svg_reprs = list(SP_BUTTON_SVG_REPRS)
    button_svg_reprs[1] = [
        (
            (
                "m5 3"
                " l13 0"
                " q-4 4 0 8"
                " q4 4 0 8"
                " l-13 0"
                " q4 -4 0 -8"
                " q-4 -4 0 -8"
                " Z"
            ),
            ("fill:white;" "stroke:black;" "stroke-width:2;"),
        ),
        (
            ("m6 7" " l8 0" " Z"),
            ("fill:none;" "stroke:black;" "stroke-width:2;"),
        ),
        (
            ("m8 11" " l8 0" " Z"),
            ("fill:none;" "stroke:black;" "stroke-width:2;"),
        ),
        (
            ("m9 15" " l8 0" " Z"),
            ("fill:none;" "stroke:black;" "stroke-width:2;"),
        ),
    ]

    def preview_paths(self):
        """Preview text from current path."""
        path = Path(self.current_path)

        try:
            text = path.read_text(encoding="utf-8")

        except IsADirectoryError:

            view_text("Can't view current path, it is a directory")

            return

        except FileNotFoundError:

            view_text("Can't view current path, it wasn't found")

            return

        view_text(
            text=text,
            show_line_number=True,
            syntax_highlighting=(
                "python" if path.suffix.lower() in (".py", ".pyl") else ""
            ),
        )

    def update_previews(self):
        self.update_image()

    def blit_path_representation(self):
        """Blit representation of text in current path."""

        rect = (
            1,
            BUTTON_HEIGHT + 2,
            self.width - 2,
            self.height - ((BUTTON_HEIGHT * 2) + 2),
        )

        image = self.image

        ###
        width, height = self.width, self.height

        path = Path(self.current_path)

        try:
            text = path.read_text(
                encoding="utf-8",
                errors="ignore",
            )

        except (
            FileNotFoundError,
            IsADirectoryError,
            PermissionError,
        ):

            try:
                subsurf = self.path_repr_subsurf

            except AttributeError:

                subsurf = self.path_repr_subsurf = image.subsurface(rect)

            draw_not_found_icon(subsurf, (255, 0, 0))

            super().blit_path_representation()
            return

        except Exception as err:

            ## log traceback in regular
            ## log and and user log

            msg = (
                "An unexpected error ocurred"
                " while trying to load the text from"
                " the path."
            )

            logger.exception(msg)
            USER_LOGGER.exception(msg)

            ## notify user via dialog

            create_and_show_dialog(
                (
                    "An error ocurred while"
                    " trying to load the text"
                    " from the path. Check the user"
                    " log for details"
                    " (click <Ctrl+Shift+J> after"
                    " leaving this dialog)."
                ),
                level_name="error",
            )

            try:
                subsurf = self.path_repr_subsurf

            except AttributeError:

                subsurf = self.path_repr_subsurf = image.subsurface(rect)

            draw_not_found_icon(subsurf, (255, 0, 0))

            super().blit_path_representation()
            return

        no_of_visible_lines = 7
        show_line_number = True
        font_height = FIRA_MONO_BOLD_FONT_HEIGHT
        font_path = FIRA_MONO_BOLD_FONT_PATH

        syntax_highlighting = "python" if path.suffix.lower() in (".py", ".pyl") else ""

        if syntax_highlighting:

            theme_map = get_ready_theme(
                syntax_highlighting,
                GENERAL_TEXT_SETTINGS,
            )

            get_syntax_map = SYNTAX_TO_MAPPING_FUNCTION[syntax_highlighting]

            ## define text settings for the line numbers

            # reference the theme text settings locally
            theme_text_settings = theme_map["text_settings"]

            # if the line number settings from the theme
            # are available, use them
            try:
                lineno_settings = theme_text_settings["line_number"]

            # otherwise use the settings for normal text of
            # the theme for the line number settings

            except KeyError:

                lineno_settings = theme_text_settings["normal"]

            ## store the colors

            lineno_fg = lineno_settings["foreground_color"]

            lineno_bg = lineno_settings["background_color"]

            ### define the background color for the text
            background_color = theme_map["background_color"]

        else:

            foreground_color = lineno_fg = GENERAL_TEXT_SETTINGS["foreground_color"]

            background_color = lineno_bg = GENERAL_TEXT_SETTINGS["background_color"]

        draw_rect(image, background_color, rect)

        if show_line_number:

            lineno_width, _ = get_text_size(
                "01", font_height=font_height, font_path=FIRA_MONO_BOLD_FONT_PATH
            )

            draw_rect(
                image,
                lineno_bg,
                (1, BUTTON_HEIGHT + 2, lineno_width - 2, height - BUTTON_HEIGHT + 2),
            )

        else:
            lineno_width = 0

        lines = text.splitlines()[:no_of_visible_lines]

        if syntax_highlighting:

            try:
                highlight_data = get_syntax_map(text)

            except SyntaxMappingError:

                highlight_data = {
                    ## store a dict item where the line index
                    ## is the key and another dict is the value
                    line_index: {
                        ## in this dict, an interval representing
                        ## the indices of all items of the line
                        ## (character objects) is used as the
                        ## key, while the 'normal' string is used
                        ## as value, indicating that all content
                        ## must be considered normal text
                        (0, len(line_text)): "normal"
                    }
                    ## for each line_index and respective line
                    for line_index, line_text in enumerate(lines)
                    ## but only if the line isn't empty
                    if line_text
                }

            ##
            x = lineno_width + 4
            y = BUTTON_HEIGHT + 2

            theme_text_settings = theme_map["text_settings"]

            ## iterate over the visible lines and their
            ## indices, highlighting their text according
            ## to the highlighting data present

            for line_index, line_text in enumerate(lines, 0):

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

                    line_surf = render_highlighted_line(
                        line_text, interval_data, theme_text_settings, join_objects=True
                    ).image

                    image.blit(line_surf, (x, y))

                y += font_height

        else:

            y = BUTTON_HEIGHT + 2

            x = lineno_width + 4 if show_line_number else 4

            for line_number, line_text in enumerate(lines, 1):

                if line_number > no_of_visible_lines:
                    break

                surf = render_text(
                    text=line_text,
                    font_height=font_height,
                    font_path=font_path,
                    foreground_color=foreground_color,
                    background_color=background_color,
                )

                image.blit(surf, (x, y))

                y += font_height

        ###

        if show_line_number:

            y = BUTTON_HEIGHT + 2

            for line_number, line_text in enumerate(lines, 1):

                surf = render_text(
                    text=str(line_number).rjust(2, "0"),
                    font_height=font_height,
                    font_path=FIRA_MONO_BOLD_FONT_PATH,
                    foreground_color=lineno_fg,
                    background_color=lineno_bg,
                )

                image.blit(surf, (2, y))

                y += font_height

        draw_depth_finish(image)

        ###
        super().blit_path_representation()

    def svg_path_repr(self):

        g = Element("g")

        ###

        rect = self.rect.move(1, BUTTON_HEIGHT + 2)

        rect.size = (self.width - 2, self.height - ((BUTTON_HEIGHT * 2) + 2))

        ###
        path = Path(self.current_path)

        try:
            text = path.read_text(encoding="utf-8")

        except (FileNotFoundError, IsADirectoryError):

            g.append(get_missing_path_repr(rect))
            g.append(super().svg_path_repr())
            return g

        no_of_visible_lines = 7
        show_line_number = True
        font_height = FIRA_MONO_BOLD_FONT_HEIGHT

        syntax_highlighting = "python" if path.suffix.lower() in (".py", ".pyl") else ""

        if syntax_highlighting:

            theme_map = get_ready_theme(
                syntax_highlighting,
                GENERAL_TEXT_SETTINGS,
            )

            get_syntax_map = SYNTAX_TO_MAPPING_FUNCTION[syntax_highlighting]

            ## define text settings for the line numbers

            # reference the theme text settings locally
            theme_text_settings = theme_map["text_settings"]

            # if the line number settings from the theme
            # are available, use them
            try:
                lineno_settings = theme_text_settings["line_number"]

            # otherwise use the settings for normal text of
            # the theme for the line number settings

            except KeyError:

                lineno_settings = theme_text_settings["normal"]

            ## store the colors

            lineno_fg = lineno_settings["foreground_color"]

            lineno_bg = lineno_settings["background_color"]

            ### define the background color for the text
            background_color = theme_map["background_color"]

        else:

            foreground_color = lineno_fg = GENERAL_TEXT_SETTINGS["foreground_color"]

            background_color = lineno_bg = GENERAL_TEXT_SETTINGS["background_color"]

        g.append(
            Element(
                "rect",
                {
                    **{
                        attr_name: str(getattr(rect, attr_name))
                        for attr_name in ("x", "y", "width", "height")
                    },
                    **{"style": f"fill:rgb{background_color};"},
                },
            )
        )

        if show_line_number:

            max_lineno_text = str(len(text.splitlines()))
            lineno_digits = len(max_lineno_text)

            lineno_width, _ = get_text_size(
                max_lineno_text,
                font_height=font_height,
                font_path=FIRA_MONO_BOLD_FONT_PATH,
            )

            lineno_rect = rect.copy()
            lineno_rect.width = lineno_width - 2

            g.append(
                Element(
                    "rect",
                    {
                        **{
                            attr_name: str(getattr(lineno_rect, attr_name))
                            for attr_name in ("x", "y", "width", "height")
                        },
                        **{"style": f"fill:rgb{lineno_bg};"},
                    },
                )
            )

        else:
            lineno_width = 0

        lines = text.splitlines()[:no_of_visible_lines]

        if syntax_highlighting:

            try:
                highlight_data = get_syntax_map(text)

            except SyntaxMappingError:

                highlight_data = {
                    ## store a dict item where the line index
                    ## is the key and another dict is the value
                    line_index: {
                        ## in this dict, an interval representing
                        ## the indices of all items of the line
                        ## (character objects) is used as the
                        ## key, while the 'normal' string is used
                        ## as value, indicating that all content
                        ## must be considered normal text
                        (0, len(line_text)): "normal"
                    }
                    ## for each line_index and respective line
                    for line_index, line_text in enumerate(lines)
                    ## but only if the line isn't empty
                    if line_text
                }

            ##

            x = rect.x + lineno_width + 4
            y = rect.y

            theme_text_settings = theme_map["text_settings"]

            ## iterate over the visible lines and their
            ## indices, highlighting their text according
            ## to the highlighting data present

            for line_index, line_text in enumerate(lines, 0):

                y += font_height

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
                        (
                            line_text[including_start:excluding_end],
                            theme_text_settings[kind],
                        )
                        for (including_start, excluding_end), kind in sorted(
                            interval_data.items(), key=lambda item: item[0]
                        )
                    )

                    max_right = x + (125 - lineno_width)

                    temp_x = x

                    for string, text_settings in string_kwargs_pairs:

                        x_increment, _ = get_text_size(
                            string,
                            font_height=font_height,
                            font_path=FIRA_MONO_BOLD_FONT_PATH,
                        )

                        text_fg = text_settings["foreground_color"]

                        style = "font:bold 13px monospace;" f"fill:rgb{text_fg};"

                        if temp_x + x_increment <= max_right:

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

                        else:

                            try:
                                string = fit_text(
                                    text=string,
                                    max_width=max_right - temp_x,
                                    ommit_direction="right",
                                    font_height=font_height,
                                    font_path=FIRA_MONO_BOLD_FONT_PATH,
                                    padding=0,
                                )
                            except ValueError:
                                string = "\N{horizontal ellipsis}"

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

                            break

        else:

            y = rect.y

            x = rect.x + (lineno_width + 4 if show_line_number else 4)

            style = "font:bold 13px monospace;" f"fill:rgb{foreground_color};"

            for line_number, line_text in enumerate(lines, 1):

                y += font_height

                if line_number > no_of_visible_lines:
                    break

                line_text = fit_text(
                    text=line_text,
                    max_width=125,
                    ommit_direction="right",
                    font_height=font_height,
                    font_path=FIRA_MONO_BOLD_FONT_PATH,
                    padding=0,
                )

                text_element = Element(
                    "text",
                    {
                        "x": str(x),
                        "y": str(y),
                        "text-anchor": "start",
                        "style": style,
                    },
                )

                text_element.text = line_text

                g.append(text_element)

        ###

        if show_line_number:

            x = rect.x + 4
            y = rect.y

            style = "font:bold 13px monospace;" f"fill:rgb{lineno_fg};"

            for line_number, line_text in enumerate(lines, 1):

                y += font_height

                text_element = Element(
                    "text",
                    {
                        "x": str(x),
                        "y": str(y),
                        "text-anchor": "start",
                        "style": style,
                    },
                )

                text_element.text = text = str(line_number).rjust(lineno_digits, "0")

                g.append(text_element)

        ###
        g.append(super().svg_path_repr())

        ###
        return g
