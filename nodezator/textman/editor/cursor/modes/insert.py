"""Insert mode behaviour for Cursor class."""

### third-party imports

from pygame import (
    QUIT,
    KEYDOWN,
    MOUSEBUTTONUP,
    K_ESCAPE,
    K_BACKSPACE,
    K_RETURN,
    K_KP_ENTER,
    K_TAB,
    KMOD_CTRL,
    K_UP,
    K_DOWN,
    K_LEFT,
    K_RIGHT,
    K_DELETE,
    KMOD_SHIFT,
    K_HOME,
    K_END,
    K_PAGEUP,
    K_PAGEDOWN,
    K_F1,
)

from pygame.event import get as get_events


### local imports

from .....loopman.exception import QuitAppException

from .....userprefsman.main import USER_PREFS

from .....htsl.main import open_htsl_link

from ...constants import NUMBER_OF_VISIBLE_LINES

from ...line import Line


class InsertMode:
    """Behaviour for cursor's insert mode."""

    def insert_mode_handling(self):
        """Get and handle events for insert mode."""
        for event in get_events():

            if event.type == QUIT:
                raise QuitAppException

            elif event.type == KEYDOWN:

                ### show help text for text editor
                ### according to text editor behavior
                ### set

                if event.key == K_F1:

                    if USER_PREFS["TEXT_EDITOR_BEHAVIOR"] == "default":

                        open_htsl_link(
                            "htap://help.nodezator.pysite/"
                            "text-editor-default-behavior.htsl"
                        )

                    elif USER_PREFS["TEXT_EDITOR_BEHAVIOR"] == "vim-like":

                        open_htsl_link(
                            "htap://help.nodezator.pysite/"
                            "text-editor-vim-like-behavior.htsl"
                        )

                ### if escape key is pressed...

                elif event.key == K_ESCAPE:

                    ## if the text editor behavior is set
                    ## to be vim-like, exit insert mode
                    ## and update cursor position;

                    if USER_PREFS["TEXT_EDITOR_BEHAVIOR"] == "vim-like":
                        self.enable_normal_mode()

                ### move cursor

                elif event.key == K_UP:
                    self.go_up_ins()

                elif event.key == K_DOWN:
                    self.go_down_ins()

                elif event.key == K_LEFT:
                    self.go_left_ins()

                elif event.key == K_RIGHT:
                    self.go_right_ins()

                ### delete methods

                elif event.key == K_BACKSPACE:
                    self.delete_previous_or_merge_lines()

                elif event.key == K_DELETE:
                    self.delete_under_or_merge_lines()

                ### slice current line
                elif event.key in (K_RETURN, K_KP_ENTER):
                    self.break_line()

                ### TAB key adds 4 spaces

                elif event.key == K_TAB:

                    ### XXX as of now, we do have a tab
                    ### representation which is the tab
                    ### character itself ('\t'), but which
                    ### is rendered as 04 spaces (check
                    ### the textman.cache module, within
                    ### the SurfaceMap class to know more)
                    ###
                    ### for now, it can't be insert here,
                    ### though it will appear as an empty
                    ### space with the width of 04 spaces
                    ### if the tab character is already
                    ### in the text when loaded here in
                    ### this editor;
                    ###
                    ### in the future make it so the user
                    ### can configure whether pressing
                    ### the tab key inserts 04 spaces
                    ### as we do here or whether it should
                    ### insert a tab character, since we
                    ### do have a representation for it;
                    ###
                    ### furthermore, allow the user
                    ### to decide the number of spaces
                    ### the tab character representation
                    ### uses
                    self.add_text(" " * 4)

                ### ignore event if ctrl key is pressed
                ### since the combination of ctrl key and
                ### other keys doesn't produce characters
                ### of our interest (only strings like
                ### '\x08', etc.)
                elif event.mod & KMOD_CTRL:
                    pass

                ### if the keydown event has a non-empty
                ### string as its unicode attribute, add
                ### such text (character)

                elif event.unicode:
                    self.add_text(event.unicode)

                ### snap cursor to different edges of
                ### text

                elif event.key == K_HOME:

                    if KMOD_SHIFT & event.mod:
                        self.go_to_top_ins()

                    else:
                        self.go_to_line_start_ins()

                elif event.key == K_END:

                    if KMOD_SHIFT & event.mod:
                        self.go_to_bottom_ins()

                    else:
                        self.go_to_line_end_ins()

                ### jump a page up or down (a page is the
                ### number of lines which fits the editing
                ### area) or snap to top or bottom of text

                elif event.key == K_PAGEUP:

                    if KMOD_SHIFT & event.mod:
                        self.go_to_top_ins()

                    else:
                        self.jump_page_up_ins()

                elif event.key == K_PAGEDOWN:

                    if KMOD_SHIFT & event.mod:
                        self.go_to_bottom_ins()

                    else:
                        self.jump_page_down_ins()

            elif event.type == MOUSEBUTTONUP:

                if event.button == 1:
                    self.te.mouse_release_action(event.pos)

                ### jump many lines up or down by using
                ### the mousewheel

                elif event.button == 4:
                    self.go_many_up_ins()

                elif event.button == 5:
                    self.go_many_down_ins()

    def add_text(self, text):
        """Add text to current position of cursor in line.

        Parameters
        ==========
        text (string)
            characters to be added.
        """
        ### reference the current line locally
        current_line = self.lines[self.row]

        ### insert text
        current_line.insert_text(self.col, text)

        ### get length of text
        length = len(text)

        ### now navigate the number of characters added to
        ### the right
        self.navigate_ins(0, length)

        ### finally, execute the edition routine
        self.edition_routine()

    def delete_previous_or_merge_lines(self):
        """Delete char before cursor or merge lines.

        If we use it when there is a character before
        the cursor, the character is deleted.

        If there's no character before the cursor, then
        we cause the current line to merge with the line
        above the cursor (if there's one), as if eliminating
        a line separator from the text. If there's no line
        above the current one, then nothing is done.
        """
        ### if there is a character before the cursor
        ### (when cursor is currently in a column higher
        ### than 0), we delete such character

        if self.col > 0:

            ### delete the character behind the current column
            del self.lines[self.row][self.col - 1]

            ### reposition the characters in the line one
            ### beside the other, so they end up occupying
            ### the space left by the removed character
            self.lines[self.row].reposition_chars()

            ### go one character to the left, to compensate
            ### for the removed one
            self.go_left_ins()

            ### since some change took place, we execute the
            ### edition routine
            self.edition_routine()

        ### since we're about to evaluate the "elif" block
        ### below, we know the condition in the previous
        ### "if" block is False, which means there is no
        ### character before the cursor;
        ###
        ### so, if on top of that fact, there is a line
        ### above the current one (that is, the cursor is not
        ### at the first row), we merge the current line into
        ### the previous one;
        ###
        ### additionally, note that the steps taken below
        ### to position the cursor could be simplified by
        ### using a combination of existing navigation_ins()
        ### partial method implementations; however, we
        ### intentionally didn't do so because even though
        ### the outcome would be the same, some of the
        ### substeps taken would cancel each other out;
        ### setting things up manually as we did avoids
        ### extra unnecessary work

        elif self.row > 0:

            ### backup the index of the current row,
            ### the one to be removed
            index_to_remove = self.row

            ### update the row and, depending on the
            ### index of the visible row, either the
            ### index of the top visible line or the
            ### visible row itself

            ## decrement row
            self.row += -1

            ## if we're at the top visible row (index 0),
            ## then make it so the index of the top visible
            ## row in decremented
            if self.visible_row == 0:
                self.top_visible_line_index += -1

            ## otherwise decrement the visible row index
            else:
                self.visible_row += -1

            ### update the cursor column so it sits after
            ### the last character in the current line
            self.col = len(self.lines[self.row])

            ### pop and reference the removed line
            removed_line = self.lines.pop(index_to_remove)

            ### reference the current line
            current_line = self.lines[self.row]

            ### now merge the removed line into the current
            ### one and reposition the characters, so all
            ### new characters from the merged line are
            ### positioned beside the existing ones

            current_line.extend(removed_line)
            current_line.reposition_chars()

            ### since some change took place, we execute the
            ### edition routine;
            ###
            ### it is important to execute this before
            ### updating the visible lines, in order to
            ### prevent syntax highlighting to be applied
            ### to the visible lines, in case the syntax
            ### highlighting is enabled
            self.edition_routine()

            ### update the visible lines, since:
            ###
            ### 1) we just removed a line which was visible,
            ### 2) and we might also have updated the index
            ###    of the top visible line in the previous
            ###    "if block"
            ###
            ### this way, other lines (if there is any),
            ### are shifted upwards to occupy the position
            ### of the one we removed
            self.update_visible_lines()

            ### now we reposition the cursor without
            ### actually changing its row and column,
            ### just for the side-effect of causing the
            ### cursor to be properly positioned at its
            ### current row and column
            self.reposition_ins()

            ### finally, we also check the need to update
            ### the editing area
            self.check_editing_area()

        ### the only other possible scenario is that in
        ### which there's no character before the cursor
        ### and also no line before the current one;
        ### in such case, the cursor is at the very
        ### beginning of the text, and no actual change
        ### takes place, so we just pass
        else:
            pass

    def delete_under_or_merge_lines(self):
        """Delete char under cursor or merge lines.

        If we use it when there is a character under
        the cursor, the character is deleted.

        If there's no character under the cursor, then
        we cause the line below the cursor (if there's one)
        to merge with the current line, as if eliminating a
        line separator from the text. If there's no line
        below the current one, then nothing is done.
        """
        ### if there's a character sitting at the column
        ### where the cursor is (the column where the cursor
        ### sits has a number lower than the character
        ### count/length of the line) delete it

        if self.col < len(self.lines[self.row]):

            ### delete the character
            del self.lines[self.row][self.col]

            ### reposition characters of current line
            ### one beside the other, so that the empty
            ### space left by the removed character
            ### is occupied (this ends up not having any
            ### effect when the removed character was the
            ### last one, since in such case the remaining
            ### characters are already correctly positioned)
            self.lines[self.row].reposition_chars()

            ### now we reposition the cursor without
            ### actually changing its row and column,
            ### just for the side-effect of having the
            ### cursor assume the size of the character
            ### under it (if there is one)
            self.reposition_ins()

            ### since some change took place, we execute the
            ### edition routine
            self.edition_routine()

        ### if there's no character sitting at the position
        ### where cursor is, it means the cursor is sitting
        ### at the very end of the line;
        ###
        ### in such case, we try to merge the line below
        ### (if there is one) with the current line

        else:

            ### define the index of the line to be removed,
            ### the one below the current one
            index_to_remove = self.row + 1

            ### try removing the line below the current one
            try:
                removed_line = self.lines.pop(index_to_remove)

            ### if there is not such line, then there is
            ### no more text to be deleted after the cursor,
            ### which means this method has no effect in the
            ### text's contents, so we just exit earlier by
            ### returning
            except IndexError:
                return

            ### otherwise, we take measures so that the line
            ### we just removed is merged with the current
            ### one

            ## reference the current line
            current_line = self.lines[self.row]

            ## now merge the removed line into the current
            ## one and reposition the characters, so all
            ## new characters from the merged line are
            ## positioned beside the existing ones

            current_line.extend(removed_line)
            current_line.reposition_chars()

            ## since some change took place, we execute the
            ## edition routine;
            ##
            ## it is important to execute this before
            ## updating the visible lines (which may happen
            ## in the next "if block"), in order to prevent
            ## syntax highlighting to be applied to the
            ## visible lines, in case the syntax highlighting
            ## is enabled
            self.edition_routine()

            ### define the range of visible line indices;
            ### we'll need this information in the next
            ### "if block"

            visible_range = range(
                self.top_visible_line_index,
                self.top_visible_line_index + NUMBER_OF_VISIBLE_LINES,
            )

            ### if the line we removed was a visible one,
            ### (its index is within the visible range)
            ### update the visible lines, so that other
            ### lines (if there are more) are shifted
            ### upwards to occupy the position of the one
            ### we removed
            if index_to_remove in visible_range:
                self.update_visible_lines()

            ### now we reposition the cursor without
            ### actually changing its row and column,
            ### just for the side-effect of having the
            ### cursor assume the size of the character
            ### under it (if there is one)
            self.reposition_ins()

            ### finally, also check the need to update
            ### the editing area
            self.check_editing_area()

    def break_line(self):
        """Break current line in two where cursor stands."""
        ### reference current line locally
        current_line = self.lines[self.row]

        ### instantiate a new line holding the characters
        ### from the part of the line where the cursor sits
        ### and on
        new_line = Line(current_line[self.col :])

        ### make the current line hold only the part of the
        ### line before the cursor
        current_line[:] = current_line[: self.col]

        ### define the index of the new line
        new_line_index = self.row + 1

        ### insert the new line in front of the current one
        self.lines.insert(new_line_index, new_line)

        ### reposition characters of the new line, so they
        ### are all aligned with the rect in the line's
        ### 'line_rect' attribute
        new_line.reposition_chars()

        ### update the index of the cursor's row and column
        ### so that it now sits at the beginning of the
        ### new line
        self.row, self.col = new_line_index, 0

        ### define the range of visible line indices;
        ### we'll need this information in the next
        ### "if block"

        visible_range = range(
            self.top_visible_line_index,
            self.top_visible_line_index + NUMBER_OF_VISIBLE_LINES,
        )

        ### if the index of the new inserted line is within
        ### the visible range, we increment the index of the
        ### visible row
        if new_line_index in visible_range:
            self.visible_row += 1

        ### otherwise, we increment the index of the top
        ### visible line, so that when we update the visible
        ### lines, the new line now appears at the bottom
        else:
            self.top_visible_line_index += 1

        ### since some change took place, we execute the
        ### edition routine;
        ###
        ### it is important to execute this before updating
        ### the visible lines, in order to prevent syntax
        ### highlighting to be applied to the visible lines,
        ### in case the syntax highlighting is enabled
        self.edition_routine()

        ### update the visible lines, since we just added a
        ### new one
        self.update_visible_lines()

        ### now we reposition the cursor without actually
        ### changing its row and column, just for the
        ### side-effect of causing the cursor to be
        ### properly positioned at its current row and
        ### column
        self.reposition_ins()

        ### also check the need to update the editing area
        self.check_editing_area()
