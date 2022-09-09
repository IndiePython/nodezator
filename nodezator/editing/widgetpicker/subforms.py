"""Facility for widget picker subform definitions."""

### standard library imports

from functools import partial, partialmethod

from string import ascii_lowercase

from random import choice


### local imports

from ...ourstdlibs.stringutils import VALIDATION_COMMAND_MAP

from ...textman.render import render_text

from ...fontsman.constants import ENC_SANS_BOLD_FONT_HEIGHT

from ...classes2d.single import Object2D
from ...classes2d.collections import List2D

from ...colorsman.colors import WINDOW_FG, WINDOW_BG

from ...dialog import create_and_show_dialog


## widgets

from ...widget.stringentry import StringEntry
from ...widget.literalentry import LiteralEntry
from ...widget.intfloatentry.main import IntFloatEntry

from ...widget.checkbutton import CheckButton
from ...widget.colorbutton import ColorButton
from ...widget.sortingbutton import SortingButton

from ...widget.textdisplay import TextDisplay
from ...widget.literaldisplay import LiteralDisplay

from ...widget.optionmenu.main import OptionMenu
from ...widget.optiontray.main import OptionTray

from ...widget.pathpreview.path import PathPreview
from ...widget.pathpreview.text import TextPreview
from ...widget.pathpreview.image import ImagePreview
from ...widget.pathpreview.audio import AudioPreview
from ...widget.pathpreview.video import VideoPreview
from ...widget.pathpreview.font import FontPreview


from ...our3rdlibs.iterablewidget.list import ListWidget
from ...our3rdlibs.iterablewidget.set import SetWidget


FONT_HEIGHT = ENC_SANS_BOLD_FONT_HEIGHT


### utility function


def get_text_obj(reference_rect, offset, text):
    """Create and return customized text object."""
    ### define text
    text += ":"

    ### define position data

    coordinates_name = "topleft"
    coordinates_value = reference_rect.move(offset).topleft

    ### create and return text obj

    text_obj = Object2D.from_surface(
        surface=render_text(
            text=text,
            font_height=FONT_HEIGHT,
            padding=5,
            foreground_color=WINDOW_FG,
            background_color=WINDOW_BG,
        ),
        coordinates_name=coordinates_name,
        coordinates_value=coordinates_value,
    )

    return text_obj


class SubformCreation:
    def create_checkbutton_subform(self):
        """Create form for checkbutton arguments."""
        ### define an starting offset
        offset = 5, 30

        ### create list to hold widget
        checkbutton_subform = List2D()

        ### instantiate value argument widgets

        ## define argument name
        arg_name = "value"

        ## instantiate and store text object

        text_obj = get_text_obj(reference_rect=self.rect, offset=offset, text=arg_name)

        checkbutton_subform.append(text_obj)

        ## define needed arguments, instantiate and store
        ## widget for the value argument

        # define widget name
        widget_name = arg_name

        # define position data

        offset = 60, offset[1] + 5
        coordinates_name = "topleft"
        coordinates_value = self.rect.move(offset).topleft

        # instantiate and store

        value_check = CheckButton(
            value=False,
            name=widget_name,
            coordinates_name=coordinates_name,
            coordinates_value=coordinates_value,
        )

        checkbutton_subform.append(value_check)

        ### finally store the subform list in the
        ### subform map
        self.subform_map["check_button"] = checkbutton_subform

    def create_string_entry_subform(self):
        """Create form for string entry arguments."""
        ### define an starting offset
        offset = 5, 30

        ### create list to hold widget
        string_entry_subform = List2D()

        ### instantiate value argument widgets

        ## define argument name
        arg_name = "value"

        ## instantiate and store text object

        text_obj = get_text_obj(reference_rect=self.rect, offset=offset, text=arg_name)

        string_entry_subform.append(text_obj)

        ## define needed arguments, instantiate and store
        ## widget for the string entry value

        ## define widget name
        widget_name = arg_name

        ## define position data

        offset = 65, offset[1] + 5
        coordinates_name = "topleft"
        coordinates_value = self.rect.move(offset).topleft

        ## instantiate and store

        value_entry = StringEntry(
            loop_holder=self,
            name=widget_name,
            draw_on_window_resize=self.draw,
            coordinates_name=coordinates_name,
            coordinates_value=coordinates_value,
        )

        string_entry_subform.append(value_entry)

        ### instantiate validation_command argument widgets

        ## define argument name
        arg_name = "validation_command"

        ## update offset
        offset = 5, offset[1] + 25

        ## instantiate and store text object

        text_obj = get_text_obj(reference_rect=self.rect, offset=offset, text=arg_name)

        string_entry_subform.append(text_obj)

        ### define needed arguments, instantiate and store
        ### widget for the string entry validation_command
        ### argument

        ## define widget name
        widget_name = arg_name

        ## define position data

        offset = 170, offset[1] + 5
        coordinates_name = "topleft"
        coordinates_value = self.rect.move(offset).topleft

        ## define options
        options = list(VALIDATION_COMMAND_MAP.keys())

        ## instantiate and store

        validation_command_option_menu = OptionMenu(
            name=widget_name,
            loop_holder=self,
            value=options[0],
            options=options,
            draw_on_window_resize=self.draw,
            coordinates_name=coordinates_name,
            coordinates_value=coordinates_value,
        )

        string_entry_subform.append(validation_command_option_menu)

        def update_value_entry_validation():
            """Update validation command of string entry."""
            value = validation_command_option_menu.get()

            try:
                value_entry.validation_command = value

            except Exception as err:

                ### set option menu value to None
                validation_command_option_menu.set(None)

                ### communicate the problem to the user

                msg = (
                    "The validation could not be set because"
                    " the value doesn't comply. The following"
                    " error message was given: {}"
                ).format(str(err))

                create_and_show_dialog(msg)

        validation_command_option_menu.command = update_value_entry_validation

        ### finally store the subform list in the
        ### subform map
        self.subform_map["string_entry"] = string_entry_subform

    def create_literal_entry_subform(self):
        """Create form for literal entry arguments."""
        ### define an starting offset
        offset = 5, 30

        ### create list to hold widget
        literal_entry_subform = List2D()

        ### instantiate value argument widgets

        ## define argument name
        arg_name = "value"

        ## instantiate and store text object

        text_obj = get_text_obj(reference_rect=self.rect, offset=offset, text=arg_name)

        literal_entry_subform.append(text_obj)

        ## define needed arguments, instantiate and store
        ## widget for the string entry value

        ## define widget name
        widget_name = arg_name

        ## define position data

        offset = 65, offset[1] + 5
        coordinates_name = "topleft"
        coordinates_value = self.rect.move(offset).topleft

        ## instantiate and store

        value_entry = LiteralEntry(
            loop_holder=self,
            name=widget_name,
            draw_on_window_resize=self.draw,
            coordinates_name=coordinates_name,
            coordinates_value=coordinates_value,
        )

        literal_entry_subform.append(value_entry)

        ### finally store the subform list in the
        ### subform map
        self.subform_map["literal_entry"] = literal_entry_subform

    def create_text_display_subform(self):
        """Create form for text display arguments."""
        ### define an starting offset
        offset = 5, 30

        ### create list to hold widget
        text_display_subform = List2D()

        ### instantiate font style argument widgets

        ## define argument name
        arg_name = "font_path"

        ## instantiate and store text object

        text_obj = get_text_obj(reference_rect=self.rect, offset=offset, text=arg_name)

        text_display_subform.append(text_obj)

        ### define needed arguments, instantiate and store
        ### widget for the text_display's font_path argument

        ## define widget name
        widget_name = arg_name

        ## define position data

        offset = 100, offset[1] + 5
        coordinates_name = "topleft"
        coordinates_value = self.rect.move(offset).topleft

        ## define options
        options = ["sans_bold", "mono_bold"]

        ## instantiate and store

        font_path_option_menu = OptionMenu(
            name=widget_name,
            value=options[0],
            loop_holder=self,
            options=options,
            draw_on_window_resize=self.draw,
            coordinates_name=coordinates_name,
            coordinates_value=coordinates_value,
        )

        text_display_subform.append(font_path_option_menu)

        def change_font_path():
            value_text_display.reset_font_path(font_path_option_menu.get())

        font_path_option_menu.command = change_font_path

        ### instantiate syntax highlighting argument widgets

        ## define argument name
        arg_name = "syntax_highlighting"

        ## update offset
        offset = 5, offset[1] + 25

        ## instantiate and store text object

        text_obj = get_text_obj(reference_rect=self.rect, offset=offset, text=arg_name)

        text_display_subform.append(text_obj)

        ### define needed arguments, instantiate and
        ### store widget for the text_display's
        ### syntax_highlighting argument

        ## define widget name
        widget_name = arg_name

        ## define position data

        offset = 165, offset[1] + 5
        coordinates_name = "topleft"
        coordinates_value = self.rect.move(offset).topleft

        ## define options
        options = ["", "python"]

        ## instantiate and store

        syntax_highlighting_option_menu = OptionMenu(
            name=widget_name,
            loop_holder=self,
            value=options[0],
            options=options,
            draw_on_window_resize=self.draw,
            coordinates_name=coordinates_name,
            coordinates_value=coordinates_value,
        )

        text_display_subform.append(syntax_highlighting_option_menu)

        def change_syntax_highlighting():
            value_text_display.reset_syntax_highlighting(
                syntax_highlighting_option_menu.get()
            )

        syntax_highlighting_option_menu.command = change_syntax_highlighting

        ### instantiate show_line_number argument widgets

        ## define argument name
        arg_name = "show_line_number"

        ## update offset
        offset = 5, offset[1] + 25

        ## instantiate and store text object

        text_obj = get_text_obj(reference_rect=self.rect, offset=offset, text=arg_name)

        text_display_subform.append(text_obj)

        ### define needed arguments, instantiate and store
        ### widget for the text_display's show_line_number
        ### argument

        ## define widget name
        widget_name = arg_name

        ## define position data

        offset = 150, offset[1] + 5
        coordinates_name = "topleft"
        coordinates_value = self.rect.move(offset).topleft

        ## instantiate and store

        show_line_number_checkbutton = CheckButton(
            value=False,
            name=widget_name,
            coordinates_name=coordinates_name,
            coordinates_value=coordinates_value,
        )

        text_display_subform.append(show_line_number_checkbutton)

        def change_show_line_number():
            value_text_display.reset_show_line_number(
                show_line_number_checkbutton.get()
            )

        show_line_number_checkbutton.command = change_show_line_number

        ### instantiate value argument widgets

        ## define argument name
        arg_name = "value"

        ## update offset
        offset = 5, offset[1] + 25

        ## instantiate and store text object

        text_obj = get_text_obj(reference_rect=self.rect, offset=offset, text=arg_name)

        text_display_subform.append(text_obj)

        ## define needed arguments, instantiate and store
        ## widget for the string entry value

        ## define widget name
        widget_name = arg_name

        ## define position data

        offset = 65, offset[1] + 5
        coordinates_name = "topleft"
        coordinates_value = self.rect.move(offset).topleft

        ## instantiate and store

        value_text_display = TextDisplay(
            name=widget_name,
            value="",
            coordinates_name=coordinates_name,
            coordinates_value=coordinates_value,
        )

        text_display_subform.append(value_text_display)

        ### finally store the subform list in the subform map
        self.subform_map["text_display"] = text_display_subform

    def create_literal_display_subform(self):
        """Create form for literal display arguments."""
        ### define an starting offset
        offset = 5, 30

        ### create list to hold widget
        literal_display_subform = List2D()

        ### instantiate show_line_number argument widgets

        ## define argument name
        arg_name = "show_line_number"

        ## update offset
        offset = 5, offset[1] + 25

        ## instantiate and store text object

        text_obj = get_text_obj(reference_rect=self.rect, offset=offset, text=arg_name)

        literal_display_subform.append(text_obj)

        ### define needed arguments, instantiate and store
        ### widget for the literal_display's show_line_number
        ### argument

        ## define widget name
        widget_name = arg_name

        ## define position data

        offset = 150, offset[1] + 5
        coordinates_name = "topleft"
        coordinates_value = self.rect.move(offset).topleft

        ## instantiate and store

        show_line_number_checkbutton = CheckButton(
            value=False,
            name=widget_name,
            coordinates_name=coordinates_name,
            coordinates_value=coordinates_value,
        )

        literal_display_subform.append(show_line_number_checkbutton)

        def change_show_line_number():
            value_literal_display.reset_show_line_number(
                show_line_number_checkbutton.get()
            )

        show_line_number_checkbutton.command = change_show_line_number

        ### instantiate value argument widgets

        ## define argument name
        arg_name = "value"

        ## update offset
        offset = 5, offset[1] + 25

        ## instantiate and store text object

        text_obj = get_text_obj(reference_rect=self.rect, offset=offset, text=arg_name)

        literal_display_subform.append(text_obj)

        ## define needed arguments, instantiate and store
        ## widget for the string entry value

        ## define widget name
        widget_name = arg_name

        ## define position data

        offset = 65, offset[1] + 5
        coordinates_name = "topleft"
        coordinates_value = self.rect.move(offset).topleft

        ## instantiate and store

        value_literal_display = LiteralDisplay(
            name=widget_name,
            value=None,
            coordinates_name=coordinates_name,
            coordinates_value=coordinates_value,
        )

        literal_display_subform.append(value_literal_display)

        ### finally store the subform list in the subform map
        self.subform_map["literal_display"] = literal_display_subform

    def create_fontpreview_subform(self):
        """Create form for font display arguments."""
        ### define an starting offset
        offset = 10, 30

        ### create list to hold widget
        fontpreview_subform = List2D()

        ### instantiate value argument widgets

        ## define argument name
        arg_name = "value"

        ## instantiate and store text object

        text_obj = get_text_obj(reference_rect=self.rect, offset=offset, text=arg_name)

        fontpreview_subform.append(text_obj)

        ## define needed arguments, instantiate and store
        ## widget for the font display value

        # define widget name
        widget_name = arg_name

        # define position data

        offset = 65, offset[1] + 5
        coordinates_name = "topleft"
        coordinates_value = self.rect.move(offset).topleft

        # instantiate and store

        value_fontpreview = FontPreview(
            name=widget_name,
            loop_holder=self,
            draw_on_window_resize=self.draw,
            coordinates_name=coordinates_name,
            coordinates_value=coordinates_value,
        )

        fontpreview_subform.append(value_fontpreview)

        ### finally store the subform list in the
        ### subform map
        self.subform_map["font_preview"] = fontpreview_subform

    def create_int_float_entry_subform(self):
        """Create form for int float entry arguments."""
        ### define an starting offset
        offset = 5, 30

        ### create list to hold widget
        int_float_entry_subform = List2D()

        ### instantiate value argument widgets

        ## define argument name
        arg_name = "value"

        ## instantiate and store text object

        text_obj = get_text_obj(reference_rect=self.rect, offset=offset, text=arg_name)

        int_float_entry_subform.append(text_obj)

        ## define needed arguments, instantiate and store
        ## widget for the int float entry value

        # define widget name
        widget_name = arg_name

        # define position data

        offset = 190, offset[1] + 5
        coordinates_name = "topleft"
        coordinates_value = self.rect.move(offset).topleft

        # instantiate and store

        value_int_float_entry = IntFloatEntry(
            loop_holder=self,
            value=0,
            numeric_classes_hint="int_float",
            allow_none=True,
            draw_on_window_resize=self.draw,
            name=widget_name,
            coordinates_name=coordinates_name,
            coordinates_value=coordinates_value,
        )

        int_float_entry_subform.append(value_int_float_entry)

        ### instantiate numeric_classes_hint argument
        ### widgets

        ## define argument name
        arg_name = "numeric_classes_hint"

        ## update offset
        offset = 5, offset[1] + 25

        ## instantiate and store text object

        text_obj = get_text_obj(reference_rect=self.rect, offset=offset, text=arg_name)

        int_float_entry_subform.append(text_obj)

        ### define needed arguments, instantiate and store
        ### widget for the int float entry
        ### numeric_classes_hint argument

        ## define widget name
        widget_name = arg_name

        ## define position data

        offset = 190, offset[1] + 5
        coordinates_name = "topleft"
        coordinates_value = self.rect.move(offset).topleft

        ## define options
        options = ["int", "float", "int_float"]

        ## instantiate and store

        numeric_classes_hint_option_tray = OptionTray(
            name=widget_name,
            value=options[0],
            options=options,
            coordinates_name=coordinates_name,
            coordinates_value=coordinates_value,
        )

        int_float_entry_subform.append(numeric_classes_hint_option_tray)

        ### instantiate multiple argument widgets:

        for arg_name in (
            "normal_drag_increment",
            "preciser_drag_increment",
            "normal_click_increment",
            "preciser_click_increment",
            "min_value",
            "max_value",
        ):
            ## update offset
            offset = 5, offset[1] + 25

            ## instantiate and store text object

            text_obj = get_text_obj(
                reference_rect=self.rect, offset=offset, text=arg_name
            )

            int_float_entry_subform.append(text_obj)

            ## update offset
            offset = 190, offset[1] + 5

            ## define widget name
            widget_name = arg_name

            ## define position data

            coordinates_value = self.rect.move(offset).topleft

            ## instantiate and store

            arg_int_float_entry = IntFloatEntry(
                loop_holder=self,
                name=widget_name,
                value=None,
                numeric_classes_hint="int_float",
                allow_none=True,
                draw_on_window_resize=self.draw,
                coordinates_name="topleft",
                coordinates_value=coordinates_value,
            )

            int_float_entry_subform.append(arg_int_float_entry)

        ### instantiate allow_none argument widgets

        ## define argument name
        arg_name = "allow_none"

        ## update offset
        offset = 5, offset[1] + 25

        ## instantiate and store text object

        text_obj = get_text_obj(reference_rect=self.rect, offset=offset, text=arg_name)

        int_float_entry_subform.append(text_obj)

        ## define needed arguments, instantiate and store
        ## widget for the int float entry allow_none
        ## argument

        # define widget name
        widget_name = arg_name

        # define position data

        offset = 190, offset[1] + 5
        coordinates_name = "topleft"
        coordinates_value = self.rect.move(offset).topleft

        # instantiate and store

        allow_none_check = CheckButton(
            value=False,
            name=widget_name,
            coordinates_name=coordinates_name,
            coordinates_value=coordinates_value,
        )

        int_float_entry_subform.append(allow_none_check)

        ### finally store the subform list in the
        ### subform map
        self.subform_map["int_float_entry"] = int_float_entry_subform

    def create_pathpreview_subform(self):
        """Create form for path preview arguments."""
        ### define an starting offset
        offset = 10, 30

        ### create list to hold widget
        pathpreview_subform = List2D()

        ### instantiate value argument widgets

        ## define argument name
        arg_name = "value"

        ## instantiate and store text object

        text_obj = get_text_obj(reference_rect=self.rect, offset=offset, text=arg_name)

        pathpreview_subform.append(text_obj)

        ## define needed arguments, instantiate and store
        ## widget for the path button value

        # define widget name
        widget_name = arg_name

        # define position data

        offset = 65, offset[1] + 5
        coordinates_name = "topleft"
        coordinates_value = self.rect.move(offset).topleft

        # instantiate and store

        value_pathpreview = PathPreview(
            name=widget_name,
            loop_holder=self,
            draw_on_window_resize=self.draw,
            coordinates_name=coordinates_name,
            coordinates_value=coordinates_value,
        )

        pathpreview_subform.append(value_pathpreview)

        ### finally store the subform list in the
        ### subform map
        self.subform_map["path_preview"] = pathpreview_subform

    def create_textpreview_subform(self):
        """Create form for text preview arguments."""
        ### define an starting offset
        offset = 10, 30

        ### create list to hold widget
        textpreview_subform = List2D()

        ### instantiate value argument widgets

        ## define argument name
        arg_name = "value"

        ## instantiate and store text object

        text_obj = get_text_obj(reference_rect=self.rect, offset=offset, text=arg_name)

        textpreview_subform.append(text_obj)

        ## define needed arguments, instantiate and store
        ## widget for the path button value

        # define widget name
        widget_name = arg_name

        # define position data

        offset = 65, offset[1] + 5
        coordinates_name = "topleft"
        coordinates_value = self.rect.move(offset).topleft

        # instantiate and store

        value_textpreview = TextPreview(
            name=widget_name,
            loop_holder=self,
            draw_on_window_resize=self.draw,
            coordinates_name=coordinates_name,
            coordinates_value=coordinates_value,
        )

        textpreview_subform.append(value_textpreview)

        ### finally store the subform list in the
        ### subform map
        self.subform_map["text_preview"] = textpreview_subform

    def create_imagepreview_subform(self):
        """Create form for image display arguments."""
        ### define an starting offset
        offset = 10, 30

        ### create list to hold widget
        imagepreview_subform = List2D()

        ### instantiate value argument widgets

        ## define argument name
        arg_name = "value"

        ## instantiate and store text object

        text_obj = get_text_obj(reference_rect=self.rect, offset=offset, text=arg_name)

        imagepreview_subform.append(text_obj)

        ## define needed arguments, instantiate and store
        ## widget for the image display value

        # define widget name
        widget_name = arg_name

        # define position data

        offset = 65, offset[1] + 5
        coordinates_name = "topleft"
        coordinates_value = self.rect.move(offset).topleft

        # instantiate and store

        value_imagepreview = ImagePreview(
            name=widget_name,
            loop_holder=self,
            draw_on_window_resize=self.draw,
            coordinates_name=coordinates_name,
            coordinates_value=coordinates_value,
        )

        imagepreview_subform.append(value_imagepreview)

        ### finally store the subform list in the
        ### subform map
        self.subform_map["image_preview"] = imagepreview_subform

    def create_audiopreview_subform(self):
        """Create form for audiopreview arguments."""
        ### define an starting offset
        offset = 10, 30

        ### create list to hold widget
        audiopreview_subform = List2D()

        ### instantiate value argument widgets

        ## define argument name
        arg_name = "value"

        ## instantiate and store text object

        text_obj = get_text_obj(reference_rect=self.rect, offset=offset, text=arg_name)

        audiopreview_subform.append(text_obj)

        ## define needed arguments, instantiate and store
        ## widget for the image display value

        # define widget name
        widget_name = arg_name

        # define position data

        offset = 65, offset[1] + 5
        coordinates_name = "topleft"
        coordinates_value = self.rect.move(offset).topleft

        # instantiate and store

        value_audiopreview = AudioPreview(
            name=widget_name,
            loop_holder=self,
            draw_on_window_resize=self.draw,
            coordinates_name=coordinates_name,
            coordinates_value=coordinates_value,
        )

        audiopreview_subform.append(value_audiopreview)

        ### finally store the subform list in the
        ### subform map
        self.subform_map["audio_preview"] = audiopreview_subform

    def create_videopreview_display_subform(self):
        """Create form for video preview display."""
        ### define an starting offset
        offset = 10, 30

        ### create list to hold widget
        videopreview_display_subform = List2D()

        ### instantiate value argument widgets

        ## define argument name
        arg_name = "value"

        ## instantiate and store text object

        text_obj = get_text_obj(reference_rect=self.rect, offset=offset, text=arg_name)

        videopreview_display_subform.append(text_obj)

        ## define needed arguments, instantiate and store
        ## widget for the image display value

        # define widget name
        widget_name = arg_name

        # define position data

        offset = 65, offset[1] + 5
        coordinates_name = "topleft"
        coordinates_value = self.rect.move(offset).topleft

        # instantiate and store

        value_videopreview_display = VideoPreview(
            name=widget_name,
            loop_holder=self,
            draw_on_window_resize=self.draw,
            coordinates_name=coordinates_name,
            coordinates_value=coordinates_value,
        )

        videopreview_display_subform.append(value_videopreview_display)

        ### finally store the subform list in the
        ### subform map
        self.subform_map["video_preview"] = videopreview_display_subform

    def create_colorbutton_subform(self):
        """Create form for color button arguments."""
        ### define an starting offset
        offset = 5, 30

        ### create list to hold widget
        colorbutton_subform = List2D()

        ### instantiate value argument widgets

        ## define argument name
        arg_name = "value"

        ## instantiate and store text object

        text_obj = get_text_obj(reference_rect=self.rect, offset=offset, text=arg_name)

        colorbutton_subform.append(text_obj)

        ## define needed arguments, instantiate and store
        ## widget for the color button value

        # define widget name
        widget_name = arg_name

        # define position data

        offset = 55, offset[1] + 5
        coordinates_name = "topleft"
        coordinates_value = self.rect.move(offset).topleft

        # instantiate and store

        value_colorbutton = ColorButton(
            name=widget_name,
            coordinates_name=coordinates_name,
            coordinates_value=coordinates_value,
        )

        colorbutton_subform.append(value_colorbutton)

        ### instantiate color format argument widgets

        ## define argument name
        arg_name = "color_format"

        ## update offset
        offset = 5, offset[1] + 25

        ## instantiate and store text object

        text_obj = get_text_obj(reference_rect=self.rect, offset=offset, text=arg_name)

        colorbutton_subform.append(text_obj)

        ## define needed arguments, instantiate and store
        ## widget for the color button unit class name

        # define widget name
        widget_name = arg_name

        # define position data

        offset = 160, offset[1] + 5
        coordinates_name = "topleft"
        coordinates_value = self.rect.move(offset).topleft

        # define options
        options = ["rgb_ints", "hex_string"]

        # instantiate and store
        color_format_option_menu = OptionMenu(
            name=widget_name,
            loop_holder=self,
            value=options[0],
            options=options,
            draw_on_window_resize=self.draw,
            coordinates_name=coordinates_name,
            coordinates_value=coordinates_value,
        )

        colorbutton_subform.append(color_format_option_menu)

        ### instantiate single value format argument widgets

        ## define argument name
        arg_name = "alone_when_single"

        ## update offset
        offset = 5, offset[1] + 25

        ## instantiate and store text object

        text_obj = get_text_obj(reference_rect=self.rect, offset=offset, text=arg_name)

        colorbutton_subform.append(text_obj)

        ## define needed arguments, instantiate and store
        ## widget for the color button single value format

        # define widget name
        widget_name = arg_name

        # define position data

        offset = 160, offset[1] + 5
        coordinates_name = "topleft"
        coordinates_value = self.rect.move(offset).topleft

        # instantiate and store

        alone_when_single_checkbutton = CheckButton(
            value=True,
            name=widget_name,
            coordinates_name=coordinates_name,
            coordinates_value=coordinates_value,
        )

        colorbutton_subform.append(alone_when_single_checkbutton)

        ### create command for both option menus to
        ### update format of color button's value
        ### and assign such command to the option menus

        def update_format():
            """Update format of color button value."""
            color_format = color_format_option_menu.get()

            alone_when_single = alone_when_single_checkbutton.get()

            value_colorbutton.set_format(color_format, alone_when_single)

        color_format_option_menu.command = (
            alone_when_single_checkbutton.command
        ) = update_format

        ### finally store the subform list in the
        ### subform map
        self.subform_map["color_button"] = colorbutton_subform

    def create_option_menu_subform(self, kind_of_content):
        """Create option menu subform for given kind.

        Parameters
        ==========
        kind_of_content (string)
            either "strings" or "intfloats", which are
            the available kinds of content here (the
            option menu actually also accepts None,
            True and False).
        """
        ### ensure the value of kind_of_content is within
        ### the allowed ones
        assert kind_of_content in ("strings", "intfloats")

        ### depending on the kind of content, define
        ### available default options; the first value
        ### in the options is used as the initial value
        ### and the whole list is used as the default
        ### options in the list widget;

        if kind_of_content == "strings":

            available_options = ["option_a", "option_b", "option_c"]

            default_factory = lambda: choice(ascii_lowercase)

        elif kind_of_content == "intfloats":

            available_options = [0, 1, 2]
            default_factory = lambda: choice(range(100))

        ### define an starting offset
        offset = 5, 30

        ### create list to hold widget
        option_menu_subform = List2D()

        ### instantiate 'value' argument widgets

        ## define argument name
        arg_name = "value"

        ## instantiate and store text object

        text_obj = get_text_obj(reference_rect=self.rect, offset=offset, text=arg_name)

        option_menu_subform.append(text_obj)

        ## define needed arguments, instantiate and store
        ## option menu widget for the option menu 'value'

        # define widget name
        widget_name = arg_name

        offset = 80, offset[1] + 5
        coordinates_name = "topleft"
        coordinates_value = self.rect.move(offset).topleft

        value_option_menu = OptionMenu(
            name=widget_name,
            loop_holder=self,
            value=available_options[0],
            options=available_options,
            draw_on_window_resize=self.draw,
            coordinates_name=coordinates_name,
            coordinates_value=coordinates_value,
        )

        option_menu_subform.append(value_option_menu)

        ### instantiate 'options' argument widgets

        ## define argument name
        arg_name = "options"

        ## update offset
        offset = 5, offset[1] + 25

        ## instantiate and store text object

        text_obj = get_text_obj(reference_rect=self.rect, offset=offset, text=arg_name)

        option_menu_subform.append(text_obj)

        ## define needed arguments, instantiate and store
        ## list widget for the option menu 'options'

        # define widget name
        widget_name = arg_name

        # define position data

        offset = 80, offset[1] + 5
        coordinates_name = "topleft"
        coordinates_value = self.rect.move(offset).topleft

        # define widget factory

        if kind_of_content == "strings":

            widget_factory = partial(
                StringEntry,
                loop_holder=self,
                draw_on_window_resize=self.draw,
                name="option_item",
            )

        elif kind_of_content == "intfloats":

            widget_factory = partial(
                IntFloatEntry,
                loop_holder=self,
                draw_on_window_resize=self.draw,
                name="option_item",
                allow_none=True,
            )

        # instantiate and store widget list

        options_list_widget = ListWidget(
            name=widget_name,
            value=available_options,
            min_len=1,
            widget_factory=widget_factory,
            default_factory=default_factory,
            quantity_command=self.reposition_form_elements,
            coordinates_name=coordinates_name,
            coordinates_value=coordinates_value,
        )

        option_menu_subform.append(options_list_widget)

        ### create custom command for the list widget and
        ### assign it to its 'command' attribute

        def command():
            """Updates values in the option menu.

            Values of the option menu are updated with
            the values in the list widget whenever the user
            edits values in the list widget.
            """
            ### retrieve values

            list_widget_values = options_list_widget.get()
            option_menu_options = value_option_menu.options

            ### if options in the list widget are different
            ### (or in different order) than those on the
            ### option menu, update the options on the
            ### option menu so they are equal

            if option_menu_options != list_widget_values:

                option_menu_value = value_option_menu.get()

                value = (
                    option_menu_value
                    if option_menu_value in list_widget_values
                    else list_widget_values[0]
                )

                value_option_menu.reset_value_and_options(
                    value=value, options=(list_widget_values)
                )

        options_list_widget.command = command

        ### format the subform key according to the kind
        ### of content used

        subform_key = "option_menu_with_{}".format(kind_of_content)

        ### finally store the subform list in the map
        self.subform_map[subform_key] = option_menu_subform

    create_option_menu_subform_with_strings = partialmethod(
        create_option_menu_subform, "strings"
    )

    create_option_menu_subform_with_intfloats = partialmethod(
        create_option_menu_subform, "intfloats"
    )

    def create_option_tray_subform(self, kind_of_content):
        """Create option tray subform for given kind.

        Parameters
        ==========
        kind_of_content (string)
            either "strings" or "intfloats", which are
            the available kinds of content here (the
            option tray actually also accepts None,
            True and False).
        """
        ### ensure the value of kind_of_content is within
        ### the allowed ones
        assert kind_of_content in ("strings", "intfloats")

        ### depending on the kind of content, define
        ### available default options; the first value
        ### in the options is used as the initial value
        ### and the whole list is used as the default
        ### options in the list widget;

        if kind_of_content == "strings":

            available_options = ["word1", "word2", "word3"]
            default_factory = lambda: choice(ascii_lowercase)

        elif kind_of_content == "intfloats":

            available_options = [0, 1, 2]
            default_factory = lambda: choice(range(100))

        ### define an starting offset
        offset = 5, 30

        ### create list to hold widget
        option_tray_subform = List2D()

        ### instantiate 'value' argument widgets

        ## define argument name
        arg_name = "value"

        ## instantiate and store text object

        text_obj = get_text_obj(reference_rect=self.rect, offset=offset, text=arg_name)

        option_tray_subform.append(text_obj)

        ## define needed arguments, instantiate and store
        ## option tray widget for the option tray 'value'

        # define widget name
        widget_name = arg_name

        offset = 80, offset[1] + 5
        coordinates_name = "topleft"
        coordinates_value = self.rect.move(offset).topleft

        value_option_tray = OptionTray(
            name=widget_name,
            value=available_options[0],
            options=available_options,
            coordinates_name=coordinates_name,
            coordinates_value=coordinates_value,
        )

        option_tray_subform.append(value_option_tray)

        ### instantiate 'options' argument widgets

        ## define argument name
        arg_name = "options"

        ## update offset
        offset = 5, offset[1] + 25

        ## instantiate and store text object

        text_obj = get_text_obj(reference_rect=self.rect, offset=offset, text=arg_name)

        option_tray_subform.append(text_obj)

        ## define needed arguments, instantiate and store
        ## list widget for the option tray 'options'

        # define widget name
        widget_name = arg_name

        # define position data

        offset = 80, offset[1] + 5
        coordinates_name = "topleft"
        coordinates_value = self.rect.move(offset).topleft

        # define widget factory

        if kind_of_content == "strings":

            widget_factory = partial(
                StringEntry,
                loop_holder=self,
                draw_on_window_resize=self.draw,
                name="option_item",
            )

        elif kind_of_content == "intfloats":

            widget_factory = partial(
                IntFloatEntry,
                loop_holder=self,
                draw_on_window_resize=self.draw,
                name="option_item",
                allow_none=True,
            )

        # instantiate and store widget list

        options_list_widget = ListWidget(
            name=widget_name,
            value=available_options,
            min_len=1,
            widget_factory=widget_factory,
            default_factory=default_factory,
            quantity_command=(self.reposition_form_elements),
            coordinates_name=coordinates_name,
            coordinates_value=coordinates_value,
        )

        option_tray_subform.append(options_list_widget)

        ### create custom command for list widget and
        ### assign it to its 'command' attribute

        def command():
            """Updates values in the option tray.

            Values of the option tray are updated with
            the values in the list widget whenever the user
            edits values in the list widget.
            """
            ### retrieve values

            list_widget_values = options_list_widget.get()
            option_tray_options = value_option_tray.options

            ### if options in the list widget are different
            ### (or in different order) than those on the
            ### option tray, update the options on the
            ### option tray so they are equal

            if option_tray_options != list_widget_values:

                option_tray_value = value_option_tray.get()

                value = (
                    option_tray_value
                    if option_tray_value in list_widget_values
                    else list_widget_values[0]
                )

                value_option_tray.reset_value_and_options(
                    value=value, options=(list_widget_values)
                )

        options_list_widget.command = command

        ### format the subform key according to the kind
        ### of content used

        subform_key = "option_tray_with_{}".format(kind_of_content)

        ### finally store the subform list in the map
        self.subform_map[subform_key] = option_tray_subform

    create_option_tray_subform_with_strings = partialmethod(
        create_option_tray_subform, "strings"
    )

    create_option_tray_subform_with_intfloats = partialmethod(
        create_option_tray_subform, "intfloats"
    )

    def create_sorting_button_subform(self, kind_of_content):
        """Create sorting button subform for given kind.

        Parameters
        ==========
        kind_of_content (string)
            either "strings" or "intfloats", which are
            the available kinds of content.
        """
        ### ensure the value of kind_of_content is within
        ### the allowed ones
        assert kind_of_content in ("strings", "intfloats")

        ### depending on the kind of content, define
        ### value, available items and default factory

        if kind_of_content == "strings":

            value = ("a",)
            available_items = {"a", "b", "c"}

            default_factory = lambda: choice(ascii_lowercase)

        elif kind_of_content == "intfloats":

            value = (0,)
            available_items = {0, 1, 2}
            default_factory = lambda: choice(range(100))

        ### define an starting offset
        offset = 5, 30

        ### create list to hold widget
        sorting_button_subform = List2D()

        ### instantiate 'value' argument widgets

        ## define argument name
        arg_name = "value"

        ## instantiate and store text object

        text_obj = get_text_obj(reference_rect=self.rect, offset=offset, text=arg_name)

        sorting_button_subform.append(text_obj)

        ## define needed arguments, instantiate and store
        ## sorting button widget for the 'value' sorting
        ## button

        # define widget name
        widget_name = arg_name

        offset = 60, offset[1] + 5
        coordinates_name = "topleft"
        coordinates_value = self.rect.move(offset).topleft

        value_sorting_button = SortingButton(
            name=widget_name,
            value=value,
            available_items=available_items,
            coordinates_name=coordinates_name,
            coordinates_value=coordinates_value,
        )

        sorting_button_subform.append(value_sorting_button)

        ### instantiate 'available items' argument widgets

        ## define argument name
        arg_name = "available_items"

        ## update offset
        offset = 5, offset[1] + 25

        ## instantiate and store text object

        text_obj = get_text_obj(
            reference_rect=self.rect,
            offset=offset,
            text=arg_name,
        )

        sorting_button_subform.append(text_obj)

        ## define needed arguments, instantiate and store
        ## list widget for the option tray 'options'

        # define widget name
        widget_name = arg_name

        # define position data

        offset = 80, offset[1] + 5 + 20  # 20 added
        coordinates_name = "topleft"
        coordinates_value = self.rect.move(offset).topleft

        # define widget factory

        if kind_of_content == "strings":

            widget_factory = partial(
                StringEntry,
                loop_holder=self,
                draw_on_window_resize=self.draw,
                name="available_item",
            )

        elif kind_of_content == "intfloats":

            widget_factory = partial(
                IntFloatEntry,
                value=0,
                loop_holder=self,
                draw_on_window_resize=self.draw,
                name="available_item",
                allow_none=False,
            )

        # instantiate and store widget list

        items_set_widget = SetWidget(
            name=widget_name,
            value=list(available_items),
            min_len=1,
            widget_factory=widget_factory,
            default_factory=default_factory,
            quantity_command=(self.reposition_form_elements),
            coordinates_name=coordinates_name,
            coordinates_value=coordinates_value,
        )

        sorting_button_subform.append(items_set_widget)

        ### create custom command for list widget and
        ### assign it to its 'command' attribute

        def command():
            """Updates values in the sorting button.

            Values of the sorting button are updated with
            the values in the list widget whenever the user
            edits values in the list widget.
            """
            ### retrieve values

            set_widget_values = items_set_widget.get()

            available_items = value_sorting_button.available_items

            ### if items in the list widget are different
            ### than those on the sorting button, update
            ### the available items on the sorting button

            if set_widget_values and set_widget_values != available_items:

                sorting_button_value = value_sorting_button.get()

                value = (
                    sorting_button_value
                    if set(sorting_button_value).issubset(set_widget_values)
                    else tuple(set_widget_values)[:1]
                )

                (
                    value_sorting_button.reset_value_and_available_items(
                        value=value,
                        available_items=(set_widget_values),
                    )
                )

        items_set_widget.command = command

        ### format the subform key according to the kind
        ### of content used

        subform_key = "sorting_button_with_{}".format(kind_of_content)

        ### finally store the subform list in the map
        self.subform_map[subform_key] = sorting_button_subform

    create_sorting_button_subform_with_strings = partialmethod(
        create_sorting_button_subform, "strings"
    )

    create_sorting_button_subform_with_intfloats = partialmethod(
        create_sorting_button_subform, "intfloats"
    )
