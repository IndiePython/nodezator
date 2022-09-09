"""Facility for line class definition."""

### third-party import
from pygame import Rect


### local imports

from ...classes2d.collections import List2D

from ..cache import CachedTextObject


class EntryLine(List2D):
    """Manages text objects representing characters."""

    def __init__(self, text, topleft, font_settings):
        """Process and store given data.

        Parameters
        ==========
        text (string)
            contents to form the line.
        topleft (collection with two integers)
            represents the topleft position of the line.
        font_settings (dict)
            settings to render text (characters).
        """
        ### initialize superclass
        super().__init__()

        ### store font settings
        self.font_settings = font_settings

        ### define height for a special "line rect"
        line_rect_height = font_settings["font_height"]

        ### instantiate a special rect for the line
        ### (don't store it on self.rect, since self.rect
        ### is the setter of a property inherited from
        ### List2D)
        self.line_rect = Rect(topleft, (0, line_rect_height))

        ### extend list with text received using a method
        ### which turns the characters into special text
        ### objects
        self.extend_from_string(text)

    def get_all_rects(self):
        """Return rects composing this line.

        This includes the line rect plus the rects of each
        text object in this list.

        Extends appcommon.classes.List2D.get_all_rects.
        """
        yield self.line_rect
        yield from super().get_all_rects()

    def extend_from_string(self, text):
        """Extend list w/ text objs created from given text.

        Each character in the text is turned into a special
        text object.

        Characters are also repositioned at the end of the
        method.

        Parameters
        ==========
        text (string)
            its characters will be used to instantiate
            text objects with which to extend this list.
        """
        ### extend line with objects from each character

        self.extend(CachedTextObject(char, self.font_settings) for char in text)

        ### finally, reposition the characters
        self.reposition_chars()

    def insert_text(self, index, text):
        """Insert text into line in given index.

        Each character in the text is turned into
        a special text object before being inserted.

        Characters are also repositioned at the end of the
        method.

        Parameters
        ==========
        index (integer)
            specific index wherein to begin inserting
            the instantiated objects using list.insert.
        text (string)
            characters used to instantiate text objects
            to be inserted into the line.
        """
        ### iterate over the characters of the text, keeping
        ### track of the index number as you go

        for index, char in enumerate(text, start=index):

            ## insert...

            self.insert(
                ## ...at the current index...
                index,
                ## a special text object instantiated
                ## from the character, using the
                ## stored font settings
                CachedTextObject(char, self.font_settings),
            )

        ### finally, reposition the characters
        self.reposition_chars()

    def reposition_chars(self):
        """Reposition characters one beside the other.

        The topright coordinates from one character are
        assigned as the topleft coordinates of the next
        character and so on. The first topright value used
        is the topright value of the rect in the 'line_rect'
        attribute.
        """
        self.rect.snap_rects_ip("topright", "topleft")

    def get(self):
        """Return text held by line.

        Works by joining the text held by each text object
        representing a character in the line.
        """
        return "".join(obj.text for obj in self)
