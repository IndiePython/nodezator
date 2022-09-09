"""Facility with general operations for cursor."""

### standard library import
from os import linesep


### third-party import
from pygame.draw import rect as draw_rect


### local imports

from ....pygameconstants import SCREEN, blit_on_screen

from ....ourstdlibs.behaviour import had_to_set_new_value

from ..constants import (
    TEXT_EDITOR_RECT,
    EDITING_AREA_RECT,
)


### class definition


class GeneralOperations:
    """General operations for the cursor class' lifetime."""

    def check_editing_area(self):
        """Trigger adjustment of editing area if needed.

        That is, if the number of characters needed to blit
        the highest line number increases or decreases,
        adjust width and left position of the editing area
        to compensate for the space gained or taken.
        """
        ### calculate the maximum number of characters
        ### needed to blit the number of a line

        n_of_lines = len(self.lines)
        max_char_needed = len(str(n_of_lines))

        ### the max_char_needed variable contains what we
        ### consider to be the new value of the maximum
        ### number of character needed to be used when
        ### calculating the necessary adjustments, while
        ### the value of max_char_needed attribute (if it
        ### exists) has the current value used;
        ###
        ### if we had to set the new value for the attribute
        ### (because it wasn't the same as the current
        ### one), we trigger the adjustment of the editing
        ### area right away

        if had_to_set_new_value(self, "max_char_needed", max_char_needed):
            self.adjust_editing_area_left_and_width()

    def adjust_editing_area_left_and_width(self):
        """Adjust the left and width of the editing area.

        Such adjustments are needed to make room for the
        line numbers at the left of the editing area.
        """
        ### multiply the the maximum number of characters
        ### needed by the width of a digit to obtain the
        ### maximum width occupied by the surfaces forming
        ### line numbers

        max_lineno_width = self.max_char_needed * self.__class__.DIGIT_SURF_WIDTH

        ### based on the maximum width we just calculated,
        ### define a new left for the editing area

        new_left = (
            # start from the x coordinate from where we
            # blit line numbers
            self.te.line_number_x
            # add the width which will be occupied by the
            # line numbers
            + max_lineno_width
            # add 15 pixels as padding between the line
            # numbers and the left of the text editing area
            + 15
        )

        ### the right used is always the right of the text
        ### editor itself minus 10 pixels (to serve as a
        ### padding between the right of the text editing
        ### area and the text editor's right)
        right = TEXT_EDITOR_RECT.right - 10

        ### now we obtain the new width from the difference
        ### between the right and the new left
        new_width = right - new_left

        ### we now finally have the new left and new width
        ### of the editing area, but before setting them,
        ### we'll clean the editing area where it sits now
        ### by blitting the text editor background color
        ### over the area it currently occupies
        self.te.clean_editing_area()

        ### we then update the editing area rect by
        ### assigning the new_left and new_width to their
        ### respective properties

        EDITING_AREA_RECT.left = new_left
        EDITING_AREA_RECT.width = new_width

        ### now that the editing area is rellocated and its
        ### width adjusted, we can paint it over the text
        ### editor again, along with the area for the
        ### line numbers

        self.te.paint_editing_and_lineno_areas(self.background_color, self.lineno_bg)

        ### since we changed the position of the text
        ### editing area along the x axis, we need to
        ### change the position of the cursor and the lines
        ### in that axis as well, so that they accompany the
        ### editing area

        ## calculate the difference between the left of
        ## the text editing area and the left of the text
        ## (represented here by the lines)

        delta_x = EDITING_AREA_RECT.left - self.visible_lines.rect.left

        ## offset the cursor and lines in the x axis by
        ## the obtained delta x

        self.rect.move_ip(delta_x, 0)
        self.visible_lines.rect.move_ip(delta_x, 0)

    def update(self):
        """Perform update routines."""
        self.clamp_cursor_horizontally()
        self.syntax_highlighting_routine()

    def clamp_cursor_horizontally(self):
        """Keep cursor on the editing area horizontally.

        That is, we clamp the cursor to the editign area,
        whenever it goes off to the sides, moving the visible
        lines along with it.

        Discussion
        ==========

        We don't worry about moving the cursor (nor the
        visible lines) vertically, because the visible lines
        have their vertical positions fixed and characters
        are very often all of the same height.

        There might be, though, rare cases where a character
        has a height different than that of the vast majority
        of other character.

        We didn't address this possibility yet, because on
        top of being rare, the slight difference in height
        might not be enough to justify adjusting the position
        of objects vertically.

        That is, the character might still be visible enough
        to be comfortably identified by the user editing the
        text.

        Even so, further measures should be taken in the
        future if problems arise. Until the last time this
        method was update, there never was a case where
        such possibility was observed or was a concern
        otherwise.
        """
        ### reference the cursor rect and obtain a copy of
        ### it clamped to the editing area rect

        rect = self.rect
        clamped = rect.clamp(EDITING_AREA_RECT)

        ### if such rects have the same horizontal position,
        ### it means there is no need for horizontal clamping
        ### so we just return right away
        if clamped.x == rect.x:
            return

        ### otherwise, it means we need to clamp the cursor
        ### horizontally and move the visible lines
        ### accordingly

        ## calculate the difference between the x coordinate
        ## of the clamped rect and of the original rect
        delta_x = clamped.x - rect.x

        ## offset the cursor and visible lines in the x axis
        ## by the obtained delta

        rect.move_ip(delta_x, 0)
        self.visible_lines.rect.move_ip(delta_x, 0)

    def draw_visible_lines_and_self(self):
        """Draw visible lines, line number and cursor."""
        ### reference objects/data locally for quicker and
        ### easier access

        ## width of a digit's surface
        digit_width = self.__class__.DIGIT_SURF_WIDTH

        ## digit surf map
        digit_surf_map = self.DIGIT_SURF_MAP

        ## x coordinate from where we position line numbers
        line_number_x = self.te.line_number_x

        ### iterate over each line and its respective line
        ### number

        for lineno, line in enumerate(
            self.visible_lines, self.top_visible_line_index + 1  # start lineno
        ):

            ### draw line
            line.draw_colliding(EDITING_AREA_RECT)

            ### draw line's number

            ## use the x coordinate from where we blit
            ## line numbers as the starting value of our
            ## x coordinate
            lineno_x = line_number_x

            ## reference the y coordinate of the line
            ## locally for quicker and easier access
            line_y = line.rect.y

            ## justify the line number to the right using
            ## spaces and iterate over the characters,
            ## blitting each of them while updating the x
            ## coordinate so they are blitted one beside
            ## the other

            for char in str(lineno).rjust(self.max_char_needed, " "):

                ## blit line number character on screen
                ## (character is either a space or a digit)

                blit_on_screen(digit_surf_map[char], (lineno_x, line_y))

                ## increment x coordinate of line number
                lineno_x += digit_width

        ### draw cursor rect
        draw_rect(SCREEN, self.cursor_color, self.rect, 1)

    def get_text(self):
        """Return text of lines joined with os.linesep."""
        return linesep.join(line.get() for line in self.lines)

    def get_mode(self):
        """Return current mode name as string."""
        ### return string according to handle_input method
        ### used

        if self.handle_input == self.normal_mode_handling:
            return "normal"

        elif self.handle_input == self.insert_mode_handling:
            return "insert"

        ### if no known event handling method is being used,
        ### which should not be possible, we assume
        ### something went wrong somewhere

        else:

            raise RuntimeError(
                (
                    "Entered 'else' block never supposed to"
                    " be entered; logic went wrong somewhere"
                )
            )

    def enable_normal_mode(self):
        """Assign normal mode behaviour to event handling."""
        ### store name of current mode
        mode_name = self.get_mode()

        ### change mode to normal mode by assigning the
        ### respective handle_input behaviour
        self.handle_input = self.normal_mode_handling

        ### admin task: move the cursor one character to
        ### the left if previous mode was 'insert' mode;
        ###
        ### this behaviour is the same as the one performed
        ### in the vim editor, and I assume it exists to
        ### prevent the cursor from resting at the right
        ### side of the last character, in case it is
        ### positioned there when leaving insert mode
        if mode_name == "insert":
            self.go_left()

        ### indicate the normal mode in the statusbar
        ### (by having it show nothing, just like in Vim
        ### software)
        self.te.statusbar.set("")

    def enable_insert_mode(self):
        """Assign insert mode behaviour to event handling."""
        ### change mode to insert mode by assigning the
        ### respective handle_input behaviour
        self.handle_input = self.insert_mode_handling

        ### indicate the insert mode in the statusbar
        self.te.statusbar.set("-- INSERT --")

    def free_up_memory(self):
        """Free memory by removing all text objects."""
        ### clear character objects from each line
        for line in self.lines:
            line.clear()

        ### then clear the lines themselves
        self.lines.clear()
