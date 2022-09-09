"""TextViewer class extension for text preparation."""

### standard library import
from string import digits


### third-party import
from pygame.math import Vector2


### local imports

from ...config import APP_REFS

from ...dialog import create_and_show_dialog

from ...syntaxman.exception import SyntaxMappingError

from ...syntaxman.utils import get_ready_theme

from ...fontsman.constants import FIRA_MONO_BOLD_FONT_PATH

from ...ourstdlibs.timeutils import get_friendly_time
from ...ourstdlibs.behaviour import empty_function

from ...classes2d.single import Object2D

from ...surfsman.draw import draw_border
from ...surfsman.render import render_rect

from ...surfsman.cache import RECT_SURF_MAP

from ..render import (
    get_text_size,
    render_text,
)

from ..text import (
    get_normal_lines,
    get_highlighted_lines,
)

## common constants
from .constants import (
    DEFAULT_TEXT_SETTINGS,
    TEXT_SETTINGS_PRESETS_MAP,
    TEXT_VIEWER_RECT,
    RECT_PRESETS_MAP,
)


class TextPreparation:
    """Provides methods for receiving and preparing text.

    Class meant as an extension of the TextViewer class.

    Methods are operations for receiving and preparing text
    to be displayed along with given arguments to enable
    additional features like line numbering and syntax
    highlighting.
    """

    def view_text(
        self,
        text,
        *,
        general_text_settings="default",
        text_viewer_rect="default",
        show_caption=True,
        header_text="",
        syntax_highlighting="",
        show_line_number=False,
        index_to_jump_to=0,
    ):
        """Prepare received text for displaying.

        Executes setups like creating objects, setting
        specific line drawing behaviour and more.

        Parameters
        ==========
        text (string)
            text to be displayed.
        syntax_highlighting (string)
            represents the name of a syntax used to
            highlight the text (for instance 'python');
            if an empty string, which is the default value,
            or the name of an unsupported syntax is given,
            syntax highlighting isn't applied;
            if, otherwise, it indicates an available syntax,
            we render the text highlighted with such syntax;
            however, even when using an available syntax,
            if highlighting fails for any reason, the text
            is rendered with no highlighting at all.
        show_line_number (boolean)
            indicates whether to display the lines' numbers
            or not; default is False, meaning numbers are
            not shown.
        index_to_jump_to (integer)
            index of a line to which to jump once you
            start the text viewing session. For instance,
            if you are displaying a log, you might want
            the user to go straight to the end of the
            text, so you would pass -1 as the argument
            to make the viewer jump to the last line;
            Default is 0.
        """
        ### define general text preset if a string is
        ### received

        if isinstance(general_text_settings, str):

            general_text_settings = TEXT_SETTINGS_PRESETS_MAP.get(
                general_text_settings, DEFAULT_TEXT_SETTINGS
            )

        ### define text viewer rect preset if a string is
        ### received

        if isinstance(text_viewer_rect, str):

            text_viewer_rect = RECT_PRESETS_MAP.get(text_viewer_rect, TEXT_VIEWER_RECT)

        ### define line height based on general text
        ### settings

        _, self.line_height = get_text_size(
            "dummy text",
            general_text_settings["font_height"],
            general_text_settings["font_path"],
        )

        ### store rect
        self.rect = text_viewer_rect

        ### define the scroll area
        self.scroll_area = text_viewer_rect.inflate(-20, -20)

        ### define page height based on general text
        ### settings
        ###
        ### that is, how much pixels to skip when pressing
        ### page up/down keys (we use a value a bit lower
        ### than the height of the scroll area);
        ###
        ### in practice, instead of using the number of
        ### pixels in the scroll area, we subtract the
        ### number of pixels equivalent to 03 lines;
        ###
        ### this makes it so jumps don't completely leave
        ### all lines in the editing area behind (at least
        ### some of them stay on the line);
        ###
        ### though this is an optional measure, I assume
        ### it helps making the movement more readable

        self.page_height = self.scroll_area.height - (self.line_height * 3)

        ### store the inverted self.rect.topleft to use as
        ### an offset to draw lines on self.image
        self.offset = -Vector2(self.rect.topleft)

        ### make syntax_highlighting string lowercase
        ### so users don't need to worry about
        ### capitalization when providing the value
        syntax_highlighting = syntax_highlighting.lower()

        ### try retrieving a theme map for the requested
        ### syntax highlighting

        try:
            theme_map = get_ready_theme(
                syntax_highlighting,
                general_text_settings,
            )

        ### if you can't retrieve the theme map, it means
        ### the syntax highlighting requested isn't among
        ### the available ones, so turn the feature off
        ### by setting the corresponding variable to an
        ### empty string
        except KeyError:
            syntax_highlighting = ""

        ### otherwise, if you can, create the text objects
        ### representing the lines of the text according
        ### to such syntax

        else:

            ## try rendering highlighted lines

            try:

                self.lines = get_highlighted_lines(
                    syntax_highlighting,
                    text,
                    syntax_settings_map=(theme_map["text_settings"]),
                )

            ## if a syntax mapping error occurs...

            except SyntaxMappingError:

                ## notify user via dialog

                create_and_show_dialog(
                    "Error while applying syntax"
                    " highlighting. Text will be"
                    " displayed without it."
                )

                ## also turn off the syntax highlighting by
                ## setting the corresponding variable to an
                ## empty string
                syntax_highlighting = ""

            ## if the rendering succeeds, though, we assign
            ## a background image surface with the theme
            ## color

            else:

                self.background = RECT_SURF_MAP[
                    (
                        *text_viewer_rect.size,
                        theme_map["background_color"],
                    )
                ]

        ## if by this point no highlighting is specified,
        ## we render normal lines and use the general
        ## background color as the color of the background
        ## surface

        if not syntax_highlighting:

            self.lines = get_normal_lines(
                text,
                general_text_settings,
            )

            self.background = RECT_SURF_MAP[
                (*text_viewer_rect.size, general_text_settings["background_color"])
            ]

        ### position text objects representing lines one
        ### below the other

        self.lines.rect.snap_rects_ip(
            retrieve_pos_from="bottomleft", assign_pos_to="topleft"
        )

        ### align the topleft of the text with the topleft
        ### of the scroll area
        self.lines.rect.topleft = self.scroll_area.topleft

        ### perform setups according to whether displaying
        ### the line numbers was required or not

        if show_line_number:

            ## set line drawing behaviour to draw both
            ## lines and their respective line numbers
            self.draw_lines = self.draw_lines_and_lineno

            ## define line number text settings and
            ## background color according to presence
            ## or absence of syntax highlighting

            if syntax_highlighting:

                text_settings = theme_map["text_settings"]

                try:
                    lineno_settings = text_settings["line_number"]

                except KeyError:
                    lineno_settings = text_settings["normal"]

                background_color = theme_map["background_color"]

            else:

                lineno_settings = general_text_settings

                background_color = general_text_settings["background_color"]

            ## create digits surfaces based on the
            ## lineno settings
            self.setup_lineno_surfs(lineno_settings)

            ## calculate the number of digits needed to
            ## display the number of the last line
            max_chars = len(str(len(self.lines)))

            ## create temporary line number panel

            # width of panel is total width occupied
            # by max_chars plus 2 additional characters
            # used as padding
            width = (max_chars + 2) * self.digit_surf_width

            # instantiate panel and draw border on its
            # surface

            self.lineno_panel = Object2D.from_surface(
                surface=(render_rect(width, self.rect.height, background_color)),
                coordinates_name="topright",
                coordinates_value=self.rect.topleft,
            )

            draw_border(self.lineno_panel.image, thickness=2)

            ## store the right coordinate minus the width
            ## of a digit two times; we'll use this 'right'
            ## coordinte to blit line numbers on the screen
            ## from the last to the first character, from
            ## right to left;

            self.lineno_right = self.lineno_panel.rect.right - (
                self.digit_surf_width * 2
            )

        else:

            ## set line drawing behaviour to draw both
            ## lines and their respective line numbers
            self.draw_lines = self.draw_lines_only

        ### if the index of line to which to jump is
        ### not 0, ensure the corresponding line is visible
        if index_to_jump_to:
            self.jump_to_line_index(index_to_jump_to)

        ###

        try:
            self.image = self.canvas_map[self.background.get_size()]

        except KeyError:

            self.image = self.canvas_map[
                self.background.get_size()
            ] = self.background.copy()

        ###

        ###

        self.caption.rect.bottomleft = self.rect.move(0, -3).topleft

        ### assign caption drawing routine depending on
        ### 'show_caption' flag

        self.caption_drawing_routine = (
            self.caption.draw if show_caption else empty_function
        )

        ### perform setups according to whether a header
        ### text was given or not

        if header_text:

            self.header_drawing_routine = self.header_label.draw

            self.header_label.set(f":: {header_text} ::")

            if show_caption:

                self.header_label.rect.midleft = self.caption.rect.move(5, 0).midright

            else:

                self.header_label.rect.bottomleft = self.rect.move(0, -3).topleft

        else:
            self.header_drawing_routine = empty_function

        ### position the help icon and help text objects
        ### near the bottomright corner of the text viewer

        self.help_icon.rect.bottomright = self.rect.move(-10, -10).bottomright

        self.help_text_obj.rect.bottomright = self.rect.move(-10, -35).bottomright

        ### finally run the text viewer loop
        self.run()

    def setup_lineno_surfs(self, text_settings):
        """Create digit surfaces used to show line number.

        Parameters
        ==========
        text_settings (dict)
            contains settings to render surfaces for the
            digits used to blit the line numbers beside
            the lines when displaying the text;
        """
        ### define digits text settings and update with
        ### the received ones

        digits_text_settings = {}
        digits_text_settings.update(text_settings)

        ### override the font style settings to force the
        ### digits to use a monospaced font
        digits_text_settings["font_path"] = FIRA_MONO_BOLD_FONT_PATH

        ### iterate over the digits, creating key-value
        ### pairs of each digit string and its corresponding
        ### surface

        self.digits_surf_map = {
            digit: render_text(digit, **digits_text_settings) for digit in digits
        }

        ### also store the width of any digit (here we use
        ### zero) in the digit_surf_width attribute,
        ### which we use when blitting the digit surfaces
        ### beside each visible line

        self.digit_surf_width = self.digits_surf_map["0"].get_width()

    def jump_to_line_index(self, index):
        """Ensure the line indicated by index is visible."""
        ### retrieve number of lines and use it to define
        ### the maximum and minimum possible values
        ### for indices

        length = len(self.lines)

        max_value = length - 1
        min_value = -length

        ### clamp index
        clamped_index = min(max(index, min_value), max_value)

        ### check whether the line from the clamped index is
        ### visible in the scroll area;
        ###
        ### if it is not, adjust the position of the text
        ### (all the lines), so the line is visible

        ## obtain the rect of the line
        line_rect = self.lines[clamped_index].rect

        ## if the line's bottom is below the scroll area's
        ## bottom, move the text so the line has its bottom
        ## aligned to the bottom of the scroll area

        if line_rect.bottom > self.scroll_area.bottom:

            y_delta = self.scroll_area.bottom - line_rect.bottom

            self.lines.rect.move_ip(0, y_delta)

        ## if the line's top is above the scroll area's
        ## top, move the text so the line has its top
        ## aligned to the top of the scroll area

        elif line_rect.top < self.scroll_area.top:

            y_delta = self.scroll_area.top - line_rect.top
            self.lines.rect.move_ip(0, y_delta)
