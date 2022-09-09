"""Facility for text displaying/editing widget."""

### standard library imports

from functools import partialmethod

from xml.etree.ElementTree import Element


### third-party import
from pygame.draw import rect as draw_rect


### local imports

from ..ourstdlibs.behaviour import empty_function

from ..ourstdlibs.stringutils import VALIDATION_COMMAND_MAP

from ..surfsman.draw import blit_aligned, draw_depth_finish
from ..surfsman.render import render_rect, combine_surfaces
from ..surfsman.icon import render_layered_icon

from ..classes2d.single import Object2D

from ..textman.text import render_highlighted_line
from ..textman.render import (
    fit_text,
    get_text_size,
    render_text,
)

from ..textman.viewer.main import view_text
from ..textman.editor.main import edit_text

from ..fontsman.constants import (
    ENC_SANS_BOLD_FONT_HEIGHT,
    ENC_SANS_BOLD_FONT_PATH,
    FIRA_MONO_BOLD_FONT_PATH,
)

from ..syntaxman.utils import (
    AVAILABLE_SYNTAXES,
    SYNTAX_TO_MAPPING_FUNCTION,
    get_ready_theme,
)

from ..syntaxman.exception import SyntaxMappingError

from ..colorsman.colors import (
    BLACK,
    WHITE,
    TEXT_DISPLAY_BG,
    TEXT_DISPLAY_TEXT_FG,
    TEXT_DISPLAY_TEXT_BG,
)


### surface representing an icon for the text editor

ICON_SURF = combine_surfaces(
    [
        render_layered_icon(
            chars=[chr(ordinal) for ordinal in (35, 36)],
            dimension_name="height",
            dimension_value=18,
            colors=[BLACK, WHITE],
            offset_pos_by=(-1, 0),
            background_width=20,
            background_height=20,
        ),
        render_layered_icon(
            chars=[chr(ordinal) for ordinal in range(115, 119)],
            dimension_name="height",
            dimension_value=14,
            colors=[BLACK, (255, 225, 140), (255, 255, 0), (255, 170, 170)],
        ),
    ],
    retrieve_pos_from="bottomright",
    assign_pos_to="bottomright",
)

ICON_WIDTH, ICON_HEIGHT = ICON_SURF.get_size()


### map associating keys with font paths

FONT_PATH_MAP = {
    "sans_bold": ENC_SANS_BOLD_FONT_PATH,
    "mono_bold": FIRA_MONO_BOLD_FONT_PATH,
}


### class definition


class TextDisplay(Object2D):
    """A display widget for storing/displaying text."""

    ### TODO make it so font height is automatically set
    ### to be either ENC_SANS_BOLD_FONT_HEIGHT or FIRA_MONO_BOLD...
    ### depending on the value of font_path, in a class
    ### method which should receive values set by user
    ### on node callable

    def __init__(
        self,
        value="",
        font_height=ENC_SANS_BOLD_FONT_HEIGHT,
        font_path="sans_bold",
        width=155,
        no_of_visible_lines=7,
        syntax_highlighting="",
        show_line_number=False,
        name="text_display",
        command=empty_function,
        validation_command=None,
        coordinates_name="topleft",
        coordinates_value=(0, 0),
    ):
        """Store data and perform setups.

        Parameters
        ==========

        value (string)
            text used as value of the widget.
        syntax_highlighting (string)
            string hinting the syntax highlighting behaviour;
            if empty, no syntax highlighting is applied
            when editing the text; if not empty, the string
            must indicate which syntax to use for the
            highlighting; for now, only 'python' (for
            Python code syntax) and 'comment' (a subset
            of Python code highlighting to highlight
            special "todo" words) are available.
        show_line_number (bool)
            indicates whether to show the line numbers
            or not, when editing the text.
        font_path (string)
            indicates the font style to be used when
            editing the contents. Defaults to 'sans_bold',
            which uses the normal font of the app. You can
            also use 'mono_bold', which uses a monospace
            font when editing the text (for instance, if
            the text you want to edit is code).
        width (integer)
            width of the widget.
        no_of_visible_lines (positive integer)
            number of lines that can be seen in the
            widget.
        name (string)
            an arbitrary name to help identify the widget;
            it is assigned to the 'name' attribute.
        validation_command (None, string or callable)
            if it is None, the instance is set up so that
            no validation is done.

            If it is a string, it must be a key in a
            preset map used to grab a valid command.

            If it is a callable, it must accept a single
            argument and its return value is used to
            determine whether validation passed (when the
            return value is truthy value) or not (when it
            is not truthy).
        coordinates_name (string)
            represents attribute name of a pygame.Rect
            instance wherein to store the position
            information from the coordinates value parameter.
        coordinates_value (sequence w/ 2 integers)
            represents the x and y coordinates of a
            position in 2d space.
        """
        ### ensure value argument received is a string

        if type(value) is not str:

            raise TypeError("'value' received must be of 'str' type")

        ### ensure there is at least one visible line

        if no_of_visible_lines < 1:

            raise ValueError("'no_of_visible_lines' must be >= 1")

        ### process and store the font_path argument;
        ###
        ### besides the font path, the font path itself
        ### may also be a key from the FONT_PATH_MAP,
        ### in which case it is replaced by the
        ### proper path

        try:
            font_path = FONT_PATH_MAP[font_path]
        except KeyError:
            pass

        self.font_path = font_path

        ### store other arguments

        self.value = value
        self.font_height = font_height

        self.syntax_highlighting = syntax_highlighting
        self.show_line_number = show_line_number

        self.width = width
        self.no_of_visible_lines = no_of_visible_lines

        self.command = command
        self.name = name

        ### setup validation: since 'validation_command'
        ### is a property with setter implementation, this
        ### assignment triggers setups for the validation
        ### command
        self.validation_command = validation_command

        ### create a surface to clean the image attribute
        ### surface every time the value changes

        height = ICON_HEIGHT + (font_height * no_of_visible_lines) + 3

        self.clean_surf = render_rect(width, height, TEXT_DISPLAY_BG)

        ### use blit aligned to blit icon aligned to the
        ### topleft

        blit_aligned(
            ICON_SURF,
            self.clean_surf,
            retrieve_pos_from="topleft",
            assign_pos_to="topleft",
            offset_pos_by=(1, 1),
        )

        ### create an image from the clean surf
        self.image = self.clean_surf.copy()

        ### prepare style data
        self.prepare_style_data()

        ### update the image contents with the value
        self.update_image()

        ### create rect from the image attribute and
        ### position it

        self.rect = self.image.get_rect()
        setattr(self.rect, coordinates_name, coordinates_value)

    @property
    def validation_command(self):
        """Return stored validation command."""
        return self._validation_command

    @validation_command.setter
    def validation_command(self, validation_command):
        """Setup validation according to received argument.

        Parameters
        ==========
        validation_command (None, string or callable)
            check __init__ method's docstring for more
            info.
        """
        ### check whether the value received is present
        ### in the validation command map

        try:
            command = VALIDATION_COMMAND_MAP[validation_command]

        ### if it is absent, though...

        except KeyError:

            ## use the value as the command itself, if
            ## it is callable

            if callable(validation_command):
                command = validation_command

            ## otherwise, it means no valid validation
            ## command was given

            else:

                msg = (
                    "'validation_command' received invalid"
                    " input: {} (it must be a valid string"
                    " or callable)"
                ).format(repr(validation_command))

                raise ValueError(msg)

        ### check whether the value received is valid

        ## try validating
        try:
            value = command(self.value)

        ## if an exception occurred while validating,
        ## catch the exception and raise a new exception
        ## from it, explaining the context of such
        ## error

        except Exception as err:

            raise RuntimeError(
                "An exception was raised while using the"
                " specified validation command on the"
                " provided value"
            ) from err

        ## if validation works, but the result is false,
        ## raise a value error

        else:

            if not value:

                raise ValueError(
                    "the 'validation_command' received"
                    " doesn't validate the 'value' received."
                )

        ### finally, let's store the validation command
        self._validation_command = command

    def on_mouse_release(self, event):
        """Act according to mouse release position.

        Parameters
        ==========
        event (pygame.event.Event of pygame.MOUSEBUTTONUP
        type)
            it is required in order to comply with the
            mouse action protocol used; we retrieve the
            mouse position from its "pos" attribute;

            check pygame.event module documentation on
            pygame website for more info about this event
            object.
        """
        ### retrieve x coordinate of mouse position
        mouse_x, _ = event.pos

        ### if click was more to the left, where the icon
        ### is, we call the method responsible for
        ### calling the text editor to edit the value
        if mouse_x < (self.rect.x + 17):
            self.edit_value()

        ### otherwise the user clicked on the portion of
        ### the button which hints the contents of the
        ### widget, so we display the widget value
        ### in the text viewer

        else:

            view_text(
                text=self.value,
                syntax_highlighting=self.syntax_highlighting,
                show_line_number=self.show_line_number,
            )

    def get(self):
        """Return the widget value."""
        return self.value

    def set(self, value, custom_command=True):
        """Set the value of the widget.

        Parameters
        ==========
        value (string)
            the value of the widget, which represents a
            text (usually a multiline string, but any
            string can be passed, as long as it is
            considered valid by the validation_command
            callable).
        custom_command (boolean)
            indicates whether the custom command should be
            called after updating the value.
        """
        ### ensure value argument received is a string

        if type(value) is not str:

            ## report problem
            print("'value' received must be of 'str' type")

            ## exit method by returning early
            return

        ### changes are only performed if the new value is
        ### indeed different from the current one

        if self.value != value and self.validation_command(value):

            ### store new value
            self.value = value

            ### update image
            self.update_image()

            ### if requested, execute the custom command
            if custom_command:
                self.command()

    def update_image(self):
        """Update widget image."""
        ### reference image locally for quicker access

        image = self.image
        width, height = image.get_size()

        ### clean image surface
        image.blit(self.clean_surf, (0, 0))

        ###

        draw_rect(
            image,
            self.background_color,
            # subarea
            (1, ICON_HEIGHT + 2, width - 2, height - ICON_HEIGHT - 1),
        )

        ###

        no_of_visible_lines = self.no_of_visible_lines
        show_line_number = self.show_line_number
        font_height = self.font_height
        font_path = self.font_path
        syntax_highlighting = self.syntax_highlighting

        if show_line_number:

            lineno_width, _ = get_text_size(
                "01", font_height=font_height, font_path=FIRA_MONO_BOLD_FONT_PATH
            )

            draw_rect(
                image,
                self.lineno_bg,
                (1, ICON_HEIGHT + 2, lineno_width - 2, height - ICON_HEIGHT - 1),
            )

        else:
            lineno_width = 0

        lines = self.value.splitlines()[:no_of_visible_lines]

        if syntax_highlighting:

            try:
                highlight_data = self.get_syntax_map(self.value)

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
            y = ICON_HEIGHT + 2

            theme_text_settings = self.theme_map["text_settings"]

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

            y = ICON_HEIGHT + 2

            x = lineno_width + 4 if show_line_number else 4

            foreground_color = self.foreground_color
            background_color = self.background_color

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

            y = ICON_HEIGHT + 2

            lineno_fg = self.lineno_fg
            lineno_bg = self.lineno_bg

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

    def prepare_style_data(self):

        general_text_settings = {
            "font_height": self.font_height,
            "font_path": self.font_path,
            "foreground_color": TEXT_DISPLAY_TEXT_FG,
            "background_color": TEXT_DISPLAY_TEXT_BG,
        }

        ###
        ###
        syntax_highlighting = self.syntax_highlighting

        if syntax_highlighting in AVAILABLE_SYNTAXES:

            ### store a theme map ready for usage with the
            ### syntax name and default settings

            self.theme_map = get_ready_theme(syntax_highlighting, general_text_settings)

            ### store specific syntax mapping behaviour
            self.get_syntax_map = SYNTAX_TO_MAPPING_FUNCTION[syntax_highlighting]

            ### define foreground and background colors for
            ### the line numbers

            ## define text settings for the line numbers

            # reference the theme text settings locally
            theme_text_settings = self.theme_map["text_settings"]

            # if the line number settings from the theme
            # are available, use them
            try:
                lineno_settings = theme_text_settings["line_number"]

            # otherwise use the settings for normal text of
            # the theme for the line number settings

            except KeyError:

                lineno_settings = theme_text_settings["normal"]

            ## store the colors

            self.lineno_fg = lineno_settings["foreground_color"]

            self.lineno_bg = lineno_settings["background_color"]

            ### define the background color for the text

            self.background_color = self.theme_map["background_color"]

        ### otherwise, no syntax highlighting is applied,
        ### but other setups are needed

        else:

            ### we define foreground and background colors
            ### for general text and line number text

            self.foreground_color = self.lineno_fg = general_text_settings[
                "foreground_color"
            ]

            self.background_color = self.lineno_bg = general_text_settings[
                "background_color"
            ]

    def reset_style(self, style_name, new_style_value):
        current_style_value = getattr(self, style_name)

        if new_style_value != current_style_value:

            setattr(self, style_name, new_style_value)
            self.prepare_style_data()
            self.update_image()

    reset_show_line_number = partialmethod(reset_style, "show_line_number")

    reset_syntax_highlighting = partialmethod(reset_style, "syntax_highlighting")

    reset_font_path = partialmethod(reset_style, "font_path")

    def edit_value(self):
        """Edit value of widget on the text editor."""
        ### retrieve edited text: this triggers the
        ### text editor edition session, which returns
        ### the edited text when the user finishes editing
        ### the text (or None, if the user decides to
        ### cancel the operation)

        text = edit_text(
            text=self.value,
            font_path=self.font_path,
            syntax_highlighting=self.syntax_highlighting,
            validation_command=self.validation_command,
        )

        ### if there is an edited text (it is not None)
        ### and it is different from the current value,
        ### set such text as the new value

        if text is not None and text != self.value:
            self.set(text)

    def get_expected_type(self):
        return str

    def svg_repr(self):

        g = Element("g", {"class": "text_display"})

        rect = self.rect.inflate(-2, -2)

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

        x, y = rect.topleft

        for path_directives, style in (
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
            (
                ("m11 21" "l2 -7" "l5 3" " Z"),
                (
                    "fill:white;"
                    "stroke:black;"
                    "stroke-width:2px;"
                    "stroke-linejoin:round;"
                ),
            ),
            (
                ("m13 14" "l5 3" "l6 -6" "-5 -3" "l-6 6" " Z"),
                (
                    "fill:yellow;"
                    "stroke:black;"
                    "stroke-width:2px;"
                    "stroke-linejoin:round;"
                ),
            ),
            (
                ("m19 8" "l5 3" "l4 -4" "l-5 -3" " Z"),
                "fill:red;stroke:black;stroke-width:2px;stroke-linejoin:round;",
            ),
        ):

            path_directives = f"M{x} {y}" + path_directives

            g.append(
                Element(
                    "path",
                    {
                        "d": path_directives,
                        "style": style,
                    },
                )
            )

        #########

        rect = rect.move(0, ICON_HEIGHT)
        rect.height += -ICON_HEIGHT

        ###

        style = f"fill:rgb{self.background_color};"

        g.append(
            Element(
                "rect",
                {
                    "style": style,
                    **{
                        attr_name: str(getattr(rect, attr_name))
                        for attr_name in ("x", "y", "width", "height")
                    },
                },
            )
        )

        ###

        no_of_visible_lines = self.no_of_visible_lines
        show_line_number = self.show_line_number
        font_height = self.font_height
        font_path = self.font_path

        syntax_highlighting = self.syntax_highlighting

        if show_line_number:

            max_lineno_text = str(len(self.value.splitlines))
            lineno_digits = len(max_lineno_text)

            lineno_width, _ = get_text_size(
                max_lineno_text,
                font_height=font_height,
                font_path=FIRA_MONO_BOLD_FONT_PATH,
            )

            lineno_rect = rect.copy()
            lineno_rect.width = lineno_width - 2

            style = f"fill:rgb{self.lineno_bg};"

            g.append(
                Element(
                    "rect",
                    {
                        "style": style,
                        **{
                            attr_name: str(getattr(lineno_rect, attr_name))
                            for attr_name in ("x", "y", "width", "height")
                        },
                    },
                )
            )

        else:
            lineno_width = 0

        lines = self.value.splitlines()[:no_of_visible_lines]

        if syntax_highlighting:

            try:
                highlight_data = self.get_syntax_map(self.value)

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

            theme_text_settings = self.theme_map["text_settings"]

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

                        ## try squeezing...
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

            foreground_color = self.foreground_color

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
                    font_path=font_path,
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

            lineno_fg = self.lineno_fg

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
        return g
