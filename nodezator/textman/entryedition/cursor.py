"""Facility for text cursor definition."""

### standard library imports

from math import inf as INFINITY

from functools import partialmethod


### third-party imports

from pygame import Rect

from pygame.math import Vector2
from pygame.draw import rect as draw_rect


### local imports

from .line import EntryLine

from ...colorsman.colors import BLACK


class EntryCursor:
    """Simple text cursor for entry-like widgets."""

    def __init__(
        self,
        text,
        font_settings,
        entry_widget,
        cursor_color=BLACK,
    ):
        """Store variables and perform setups.

        Parameters
        ==========

        text (string)
            text being edited.
        font_settings (dict)
            settings passed to the line instance to render
            the characters.
        entry_widget (entry widget instance)
            entry object whose text the cursor will manage.
        cursor_color (color)
            color of the cursor.
        """
        ### store reference to entry widget
        self.entry_widget = entry_widget

        ### retrieve the font height from the font settings
        ### to use as the height of this cursor
        height = font_settings["font_height"]

        ### create a rect for the cursor

        ## define an arbitrary width for the rect (we use a
        ## third of the height since it looks good, but this
        ## is arbitrary and is really just an initial value;
        ## the cursor assumes the width of characters under
        ## it anyway, so it's width should change multiple
        ## times over the widget editing session)
        arbitrary_width = height // 3

        ## instantiate and store a rect for the cursor
        self.rect = Rect((0, 0), (arbitrary_width, height))

        ### instantiate an empty line

        self.line = EntryLine("", self.entry_widget.rect.topleft, font_settings)

        ### set text on line and perform additional setups;
        ### from now on, the line will be holding the text
        self.set(text)

        ### store the cursor color
        self.cursor_color = cursor_color

    ### data related methods

    def get(self):
        """Return text of line."""
        return self.line.get()

    def set(self, value):
        """Set value on line and perform extra setups."""
        ### clear the current text on line (if any)
        self.line.clear()

        ### set text on line by using a special extending
        ### method
        self.line.extend_from_string(value)

        ### set the cursor's column number to the length of
        ### the line, which has the effect of leaving the
        ### cursor positioned at the end of the text
        self.col = len(self.line)

        ### reposition cursor so that it sits in the
        ### appropriate position according to its column
        ### number
        self.reposition()

    ### loop related methods

    def update(self):
        """Keep cursor inside the entry's rect.

        This clamps the cursor to the entry's rect, moving
        the line along by the same amount of movement.
        """
        ### reference the cursor rect locally and obtain
        ### a copy of it clamped to the entry's rect

        rect = self.rect
        clamped = rect.clamp(self.entry_widget.rect)

        ### if such rects are equal, it means the clamping
        ### didn't need to move the cursor's copy, cause it
        ### was already inside the entry's rect; if this is
        ### the case, there's nothing left to do, so we can
        ### return right away
        if clamped == rect:
            return

        ### otherwise, it means we need to clamp the cursor
        ### and move the text (represented here by the line)
        ### along with it

        ## calculate the difference between the topleft
        ## of the clamped rect and the topleft of the
        ## original rect
        delta = Vector2(clamped.topleft) - rect.topleft

        ## finally offset the cursor and line with the delta

        rect.move_ip(delta)
        self.line.rect.move_ip(delta)

    def draw(self):
        """Draw visible characters and cursor."""
        ### reference the entry's image and rect locally

        entry_image = self.entry_widget.image
        entry_rect = self.entry_widget.rect

        ### define offset
        offset = -Vector2(entry_rect.topleft)

        ### draw characters

        for char_obj in self.line:

            if char_obj.rect.colliderect(entry_rect):

                entry_image.blit(char_obj.image, char_obj.rect.move(offset))

        ### draw cursor rect

        draw_rect(entry_image, self.cursor_color, self.rect.move(offset), 1)

    ### navigation method

    def navigate(self, cols):
        """Jump number of columns provided.

        Parameters
        ==========
        cols (integer)
            represents how many columns the cursor should be
            moved; the signal of the integer indicates the
            direction of the movement.
        """
        ### obtain new column number by adding up the current
        ### column number with the given number of columns
        ### to jump
        new_col = self.col + cols

        ### clamp the new colum number so it's within
        ### the length of the line;
        ###
        ### that is, the cursor can sit from 0 to the length
        ### of the line;
        ###
        ### note that this means the cursor can either sit
        ### on top of a character in the line but also after
        ### the last character or at the beginning of the
        ### line when the line is empty

        max_col_index = len(self.line)

        self.col = max(min(max_col_index, new_col), 0)

        ### admin task: snap cursor to new column we just
        ### defined

        ## try retrieving character sitting at the column we
        ## just defined
        try:
            char_obj = self.line[self.col]

        ## if an IndexError occurs, it means that there is
        ## no character where the cursor sits, so we
        ## check which specific situation caused this

        except IndexError:

            ## it may be caused by the cursor moving to the
            ## right of the last character

            if (
                # line is not empty
                max_col_index
                # and index is an unit after the last index
                and self.col == max_col_index
            ):

                # if this is the case, we just position the
                # cursor at the right of the last character
                # (the one sitting at the column before the
                # current one)

                char_obj = self.line[self.col - 1]
                self.rect.topleft = char_obj.rect.topright

            ## in all other scenarios we assume the line is
            ## empty, so we just place the cursor at the
            ## beginning of the line
            else:
                self.rect.topleft = self.line.rect.topleft

        ## if we otherwise succeed in retrieving the char
        ## in the current column, we move the cursor to the
        ## position of that character object;
        ##
        ## we also update the cursor size to that of the
        ## character obj

        else:

            self.rect.topleft = char_obj.rect.topleft
            self.rect.size = char_obj.rect.size

    go_left = partialmethod(navigate, -1)
    go_right = partialmethod(navigate, 1)

    go_to_beginning = partialmethod(navigate, -INFINITY)
    go_to_end = partialmethod(navigate, INFINITY)

    reposition = partialmethod(navigate, 0)

    ### text editing operations

    def add_text(self, text):
        """Add text to current position of cursor in line.

        Parameters
        ==========
        text (string)
            characters to be added.
        """
        ### reference the line locally
        line = self.line

        ### insert given text
        line.insert_text(self.col, text)

        ### get length of given text
        length = len(text)

        ### we use the length to update the column of the
        ### cursor
        self.col += length

        ### we then reposition cursor so that it sits in
        ### the appropriate position according to its column
        ### number; this also update its size when suitable
        self.reposition()

    def delete_previous(self):
        """Delete char before cursor.

        If we use it when there is a character before
        the cursor, the character is deleted.

        If there's no character before the cursor, then
        nothing happens.
        """
        ### if self.col equals 0, there's no character
        ### before the cursor to delete, so we can leave
        ### the method right away
        if self.col == 0:
            return

        ### otherwise we delete the character before the
        ### cursor

        ## pop the character behind the current column
        ## from the line, referencing it
        char_obj = self.line.pop(self.col - 1)

        ## reposition the characters in the line one
        ## beside the other, so they end up occupying
        ## the space left by the removed character
        self.line.reposition_chars()

        ## since the cursor went back one column,
        ## decrement the current column by one unit
        self.col += -1

        ### we then reposition cursor so that it sits in
        ### the appropriate position according to its column
        ### number; this also update its size when suitable
        self.reposition()

    def delete_under(self):
        """Delete char under cursor.

        If we use it when there is a character under
        the cursor, the character is deleted.

        If there's no character under the cursor, then
        nothing happens.
        """
        ### if the column where the cursor is sitting has a
        ### number lower than the character count (length)
        ### of the line, then there is no character sitting
        ### under the cursor for us to delete, so we leave
        ### the method right away
        if self.col >= len(self.line):
            return

        ### otherwise we delete the character under the
        ### cursor

        ## delete the character
        del self.line[self.col]

        ## try retrieving a char object under the cursor
        try:
            char_obj = self.line[self.col]

        ## if there's no character (an index error occurs),
        ## it means we deleted the character in the last
        ## position in the line, so there's no character
        ## under the cursor now;
        ##
        ## there's no problem with this, so we just pass
        except IndexError:
            pass

        ## if the char object exists, though, we need to
        ## perform extra tasks

        else:

            # reposition the characters of the line one
            # beside the other, so that the empty space
            # left by the removed character is occupied
            self.line.reposition_chars()

            # assign the size of the character currently
            # under the cursor to the cursor
            self.rect.size = char_obj.rect.size

    def delete_previous_word(self):
        """Delete word before cursor.

        If we use it when there are characters before
        the cursor, the characters are deleted until the
        next space.

        If there are no characters before the cursor, then
        nothing happens.
        """
        while True:

            ### if self.col equals 0, there's no character
            ### before the cursor to delete, so we can leave
            ### the method right away
            if self.col == 0:
                return

            ### otherwise we delete the character before the
            ### cursor

            # Check if the next character is a new word. If
            # so we are done.
            char_obj = self.get()[self.col - 1]
            if char_obj == " ":
                self.delete_previous()
                return

            ## pop the character behind the current column
            ## from the line, referencing it
            char_obj = self.line.pop(self.col - 1)

            ## reposition the characters in the line one
            ## beside the other, so they end up occupying
            ## the space left by the removed character
            self.line.reposition_chars()

            ## since the cursor went back one column,
            ## decrement the current column by one unit
            self.col += -1

            ### we then reposition cursor so that it sits in
            ### the appropriate position according to its column
            ### number; this also update its size when suitable
            self.reposition()
