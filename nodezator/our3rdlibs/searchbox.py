"""Facility for search box object."""

### third-party import
from pygame import Rect


### local imports

from ..pygamesetup.constants import GENERAL_NS

from ..ourstdlibs.behaviour import return_untouched

from ..ourstdlibs.color.creation import get_contrasting_bw

from ..classes2d.single import Object2D

from ..surfsman.render import render_rect

from ..fontsman.constants import (
    ENC_SANS_BOLD_FONT_HEIGHT,
    ENC_SANS_BOLD_FONT_PATH,
)

from ..colorsman.colors import BLACK, WHITE

from ..textman.entryedition.cursor import EntryCursor


class SearchBox(Object2D):
    """Search values based on given text.

    Doesn't handle display of values, this must be delegated
    to other objects. This makes this widget quite modular
    and synergetic.
    """

    def __init__(
        self,
        value="",
        font_height=ENC_SANS_BOLD_FONT_HEIGHT,
        font_path=ENC_SANS_BOLD_FONT_PATH,
        width=200,
        name="search_box",
        on_input=return_untouched,
        coordinates_name="topleft",
        coordinates_value=(0, 0),
        foreground_color=BLACK,
        background_color=WHITE,
    ):
        """Perform setups and assign data for reuse.

        Parameters
        ==========
        value (string)
            initial value of the widget.
        font_height (integer)
            desired font height in pixels.
        font_path (string, defaults to "default")
            represents font style. Check local
            font.py module for available styles. In doubt
            use 'default' for default font.
        width (integer)
            width of the widget.
        name (string)
            an arbitrary name to help identify the widget.
        on_input (callable)
            callable to be executed whenever the value
            changes (when characters are entered/deleted);
            the callable must take a single argument, which
            is the value (text) in the search box.
        coordinates_name (string)
            represents attribute name of rect wherein
            to store the position information from the
            coordinates value parameter.
        coordinates_value (2-tuple of integers)
            represents a position in 2d space; the values of
            x and y axes, respectively.
        foreground_color, background_color
            (tuple/list/pygame.color.Color instance)
            A tuple or list of r, g, b values which are
            integers ranging from 0 to 255. For the
            background color, an optional fourth value
            can be passed, which is an integer in the
            same range as the others, representing the
            image opacity (0 for full transparency and
            255 for full opacity).
        """
        ### ensure value argument received is a string

        if type(value) is not str:

            raise TypeError("'value' received must be of 'str' type")

        ### convert the colors passed into tuples for
        ### simplicity (since colors can be given as
        ### instances from other classes like
        ### pygame.Color and builtin lists too)

        background_color = tuple(background_color)
        foreground_color = tuple(foreground_color)

        ### store some of the arguments in their own
        ### attributes

        self.name = name
        self.on_input = on_input

        ### create and position a rect for this entry

        self.rect = Rect(0, 0, width, font_height)

        setattr(self.rect, coordinates_name, coordinates_value)

        ### create a background surface for the widget
        self.background = render_rect(*self.rect.size, background_color)

        ### also store a copy of it as the image
        ### representing this widget
        self.image = self.background.copy()

        ### gather the text rendering settings in a
        ### dictionary

        render_settings = {
            "font_height": font_height,
            "font_path": font_path,
            "foreground_color": foreground_color,
            "background_color": background_color,
        }

        ### instantiate the entry cursor class, which is
        ### responsible for holding and managing the text
        ### of the entry during edition (while the actual
        ### value keeps stored in the 'value' attribute,
        ### until the edition in the entry is confirmed
        ### or the value is set with self.set())

        cursor = self.cursor = EntryCursor(
            value,
            render_settings,
            self,
            get_contrasting_bw(background_color),
        )

        ###
        self.reposition_cursor()

        ###

        for method_name in (
            'update',
            'go_left',
            'go_right',
            'go_to_beginning',
            'go_to_end',
        ):

            method = getattr(cursor, method_name)
            setattr(self, method_name, method)

        ###

        for method_name in (
            'add_text',
            'delete_previous_word',
            'delete_previous',
            'delete_under',
        ):

            method = getattr(cursor, method_name)
            wrapped_method = self.report_on_input(method)
            setattr(self, method_name, wrapped_method)

    def report_on_input(self, callable_obj):

        def wrapped_callable(*args, **kwargs):
            callable_obj(*args, **kwargs)
            self.on_input(self.cursor.get())

        return wrapped_callable

    def get(self):
        """Return text content of widget."""
        return self.cursor.get()

    def set(self, value, custom_command=True):
        """Set obj value.

        value (string)
            value to be used as label text.
        """
        ### ensure value argument received is a string

        if type(value) is not str:

            ## report problem
            print("'value' received must be of 'str' type")

            ## exit method by returning early
            return

        ### return earlier if value is already set

        if value == self.get():
            return

        ### otherwise set the value

        ## set value as the search box text
        self.cursor.set(value)

        ### also, if requested, execute the custom command
        if custom_command:
            self.on_input(value)

    def draw(self):
        """Draw objects.

        Extends Object2D.draw.
        """
        ### clean image
        self.image.blit(self.background, (0, 0))

        ### draw cursor and characters
        self.cursor.draw()

        ### blit self.image on screen
        super().draw()

    def reposition_cursor(self):

        ### align line topleft with self.rect.topleft and
        ### move cursor to the end of the contents

        self.cursor.line.rect.topleft = self.rect.topleft
        self.cursor.go_to_end()

    def get_focus(self):
        """Perform setups."""
        ### if app is not in play mode, enable text editing events
        ### and set the text input rect

        if GENERAL_NS.mode_name != 'play':

            start_text_input()
            set_text_input_rect(self.rect.move(0, 20))

    def lose_focus(self):
        """Perform setups."""
        ### disable text editing events
        stop_text_input()
