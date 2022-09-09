"""Facility for line class definition."""

### third-party import
from pygame import Rect


### local imports

from ...classes2d.collections import List2D

from ...syntaxman.utils import (
    AVAILABLE_SYNTAXES,
    get_ready_theme,
)

from ...fontsman.constants import FIRA_MONO_BOLD_FONT_PATH

from ..cache import CachedTextObject

from .constants import (
    SANS_FONT_SETTINGS,
    MONO_FONT_SETTINGS,
)


class Line(List2D):
    """Manages text objects representing characters."""

    def __init__(self, contents):
        """Extend this list instance with given contents.

        Parameters
        ==========
        contents (string or list of CachedTextObject objects)
            contents to form the line.
        """
        ### initialize superclass
        super().__init__()

        ### instantiate a rect for the line (don't store
        ### it on self.rect, since it is the setter of
        ### a property inherited from List2D)
        self.line_rect = Rect((0, 0), (0, self.char_height))

        ### extend list with contents received, according
        ### to its type

        if isinstance(contents, str):
            self.extend_from_string(contents)

        elif isinstance(contents, list):
            self.extend(contents)

        ### if an unexpected type is received, raise an
        ### error explaining the problem

        else:

            raise TypeError("'contents' must be of type 'str'" " or 'list'")

    def get_all_rects(self):
        """Return rects from this line.

        This includes the line rect plus the rects of each
        item of this list.

        Extends appcommon.classes.List2D.get_all_rects.
        """
        yield self.line_rect
        yield from super().get_all_rects()

    ### XXX as the char_height class attribute is used
    ### now, it doesn't have enough flexibility;
    ###
    ### it should probably be defined by a 'font_height'
    ### field from text rendering data passed when
    ### starting a text editing session, and reflect on
    ### the final height of the text editing area;
    ###
    ### for now, the font heights used are locked in the
    ### same value, and the height of the text editing area
    ### is defined only at the application startup;
    ###
    ### this is important but not urgent, since we have
    ### other pending tasks that will be even more useful
    ### for users;

    @classmethod
    def set_normal_render_settings(cls, font_path, syntax_highlighting):
        """Reference the render settings for normal text.

        Normal text is either text rendered with default
        settings or, when syntax highlighting is enabled,
        text from syntax highlight themes which are
        categorized as 'normal'.

        Parameters
        ==========

        font_path (string)
            indicates the font style of the text.
        syntax_highlighting (string)
            represents the name of a syntax used to
            highlight the text (for instance, 'python');
            can be an empty string as well; when an
            empty string is received, or the syntax named
            isn't available, the default settings are used.
        """
        ### define default render settings, based on the
        ### value of the 'font_path' argument

        default_render_settings = (
            MONO_FONT_SETTINGS
            if font_path == FIRA_MONO_BOLD_FONT_PATH
            else SANS_FONT_SETTINGS
        )

        ### pick render settings to use based on the value
        ### of the 'syntax_highlighting' argument

        render_settings = (
            ## if an available syntax is given, use the
            ## normal text settings from a theme representing
            ## the syntax
            get_ready_theme(syntax_highlighting, default_render_settings)[
                "text_settings"
            ]["normal"]
            if syntax_highlighting in AVAILABLE_SYNTAXES
            ## otherwise, just use the default render settings
            else default_render_settings
        )

        ### finally store references to the render settings
        ### and its font height in their own dedicated
        ### class attributes

        cls.render_settings = render_settings
        cls.char_height = render_settings["font_height"]

    def extend_from_string(self, text):
        """Extend list w/ objs created from given text.

        Also rearranges the positions of the objects.

        Parameters
        ==========
        text (string)
            its characters will be used to instantiate
            instances of a special class called
            CachedTextObject; such instance are used to
            which to extend this list.
        """
        ### extend list with the objects as you create them
        ### from each character in the text

        self.extend(CachedTextObject(char, self.render_settings) for char in text)

        ### then reposition the objects
        self.reposition_chars()

    def insert_text(self, index, text):
        """Instantiate objects from characters and insert.

        index (integer)
            specific index before which to begin inserting
            the instantiated objects.
        text (string)
            characters to be inserted in the line.

        Rearrange positions at the end.
        """
        for next_index, char in enumerate(text, start=index):

            self.insert(next_index, CachedTextObject(char, self.render_settings))

        self.reposition_chars()

    def reposition_chars(self):
        """Reposition characters relative to line rect.

        This is a convenience method to call the
        self.rect.snap_rects_ip() method.

        snap_rects_ip() is the method from an instance of
        a special class called rectsman.main.RectsManager,
        and is used to align the rect instances managed
        by it. In the case of this Line instance, such rects
        are the rect in the 'line_rect' attribute plus the
        rect of each CachedTextObject stored in the Line
        itself (since it is a list subclass).

        The effect is that the CachedTextObject (which
        represent the characters in the line) are
        positioned one beside the other.

        To be specific, the topright coordinates from one
        character are assigned as the topleft of the next
        character and so on. The first topright value used is
        the topright value of the rect in the 'line_rect'
        attribute.
        """
        self.rect.snap_rects_ip(
            "topright",  # retrieve_pos_from argument
            "topleft",  # assign_pos_to argument
        )

    def get(self):
        """Return line contents as string."""
        return "".join(obj.text for obj in self)
