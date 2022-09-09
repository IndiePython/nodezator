"""Class extension for the text cursor (Cursor class)."""

### standard library imports

from math import inf as INFINITY

from functools import partialmethod


### local import
from ..constants import NUMBER_OF_VISIBLE_LINES


### XXX
###
### 1) check in other modules/subpackages of this 'cursor'
###    subpackage, whether a sequence of steps can be
###    replaced by a simple call to
###    self.reposition()/reposition_ins()
###
### 2) since this class has just one method,
###    could we turn its method into a function for
###    injecting in the cursor class, but without losing
###    the benefit of setting extra partial methods with
###    functools.partialmethod?
###
###    I mean, this must be done in a way that isn't
###    cumbersome and everything could be set up here
###    and just be injected once, in a single line in the
###    cursor class definition.
###
###    I didn't have time to think about this. This also
###    neither urgent nor necessarily desired, but I was
###    curious about this and couldn't immediately think
###    of a way to do it.


### module constant: quantity of lines to jump when pressing
### page up/down keys
###
### by page we mean roughly the number of lines
### appearing on the editing area;
###
### in practice, instead of using the number of visible
### lines in the jump, we subtract 03 lines just to shorten
### the jump a bit;
###
### this makes it so jumps don't completely leave all
### lines in the editing area behind (at least some
### of them stay on the line);
###
### though this is an optional measure, I assume it helps
### making the movement more readable
LINES_IN_A_JUMP = NUMBER_OF_VISIBLE_LINES - 3


class Navigation:
    """Navigation operation for Cursor class."""

    def navigate(self, rows, cols):
        """Jump number of rows and columns provided.

        Use in normal mode.

        Parameters
        ==========
        rows, cols (integers)
            represent how many rows and columns the cursor
            should be moved; the signal indicates the
            direction of the movement;
        """
        ### store current row and column

        current_row = self.row
        current_col = self.col

        ### clamp final row value so it is within existing
        ### lines indices (since row number represents index
        ### of current line)

        max_row_index = len(self.lines) - 1

        self.row = new_row = max(min(max_row_index, current_row + rows), 0)

        ### calculate how many rows we will move
        no_of_rows_to_move = new_row - current_row

        ### update our visible row index with the number of
        ### rows moved
        self.visible_row += no_of_rows_to_move

        ### if cursor...

        if (
            ### will move rows up
            no_of_rows_to_move < 0
            ### and end up in a line above the visible ones
            and self.visible_row < 0
        ):

            ## adjust the visible row index to 0, so the
            ## cursor ends up at the top visible row
            self.visible_row = 0

            ## make it so the new top visible line is the
            ## one indicated by the 'new_row' index
            self.top_visible_line_index = new_row

            ## now that you have a new top visible line
            ## set, update the visible lines
            self.update_visible_lines()

        ### otherwise, if cursor...

        elif (
            ### will move moved rows down
            no_of_rows_to_move > 0
            ### and end up in a line below the visible ones
            and self.visible_row >= NUMBER_OF_VISIBLE_LINES
        ):

            ## adjust the visible row index to the number
            ## of visible lines minus one, so the
            ## cursor ends up at the bottom visible row
            self.visible_row = NUMBER_OF_VISIBLE_LINES - 1

            ## make it so the new top visible line is the
            ## one 'x' rows behind the new row, where x equals
            ## the number of visible lines plus 1
            self.top_visible_line_index = new_row - NUMBER_OF_VISIBLE_LINES + 1

            ## now that you have a new top visible line
            ## set, update the visible lines
            self.update_visible_lines()

        ### clamp final colum value so it's within
        ### existing characters indices (since column number
        ### represents index of current character)

        max_col_index = len(self.lines[new_row]) - 1

        self.col = max(min(max_col_index, current_col + cols), 0)

        ### admin task: snap cursor to new row and column
        ### defined, also making it assume the size of the
        ### character where it sits (if there is one)

        ## try retrieving character sitting at the visible
        ## row and column we just defined

        try:
            char_obj = self.visible_lines[self.visible_row][self.col]

        ## if an IndexError occurs, it means that there is
        ## no character where the cursor sits, which we
        ## assume it is so because the line is empty, so we
        ## just place the cursor at the beginning of the line

        except IndexError:
            self.rect.topleft = self.visible_lines[self.visible_row].rect.topleft

        ## if we otherwise succeed in retrieving the char
        ## in the current column, we move the cursor to the
        ## position of that character object;
        ##
        ## we also update the cursor size to that of the
        ## character obj

        else:

            self.rect.topleft = char_obj.rect.topleft
            self.rect.size = char_obj.rect.size

    go_up = partialmethod(navigate, -1, 0)
    go_down = partialmethod(navigate, 1, 0)

    go_many_up = partialmethod(navigate, -4, 0)
    go_many_down = partialmethod(navigate, 4, 0)

    jump_page_up = partialmethod(navigate, -LINES_IN_A_JUMP, 0)
    jump_page_down = partialmethod(navigate, LINES_IN_A_JUMP, 0)

    go_left = partialmethod(navigate, 0, -1)
    go_right = partialmethod(navigate, 0, 1)

    go_to_line_start = partialmethod(navigate, 0, -INFINITY)
    go_to_line_end = partialmethod(navigate, 0, INFINITY)

    go_to_top = partialmethod(navigate, -INFINITY, 0)
    go_to_bottom = partialmethod(navigate, INFINITY, 0)

    reposition = partialmethod(navigate, 0, 0)

    def navigate_ins(self, rows, cols):
        """Jump number of rows and columns provided.

        Use in insert mode.

        Parameters
        ==========
        rows, cols (integers)
            represent how many rows and columns the cursor
            should be moved; the signal indicates the
            direction of the movement;
        """
        ### store current row and column

        current_row = self.row
        current_col = self.col

        ### clamp final row value so it is within existing
        ### lines indices (since row number represents index
        ### of current line)

        max_row_index = len(self.lines) - 1

        self.row = new_row = max(min(max_row_index, current_row + rows), 0)

        ### calculate how many rows we will move
        no_of_rows_to_move = new_row - current_row

        ### update our visible row index with the number of
        ### rows moved
        self.visible_row += no_of_rows_to_move

        ### if cursor...

        if (
            ### will move rows up
            no_of_rows_to_move < 0
            ### and end up in a line above the visible ones
            and self.visible_row < 0
        ):

            ## adjust the visible row index to 0, so the
            ## cursor ends up at the top visible row
            self.visible_row = 0

            ## make it so the new top visible line is the
            ## one indicated by the 'new_row' index
            self.top_visible_line_index = new_row

            ## now that you have a new top visible line
            ## set, update the visible lines
            self.update_visible_lines()

        ### otherwise, if cursor...

        elif (
            ### will move moved rows down
            no_of_rows_to_move > 0
            ### and end up in a line below the visible ones
            and self.visible_row >= NUMBER_OF_VISIBLE_LINES
        ):

            ## adjust the visible row index to the number
            ## of visible lines minus one, so the
            ## cursor ends up at the bottom visible row
            self.visible_row = NUMBER_OF_VISIBLE_LINES - 1

            ## make it so the new top visible line is the
            ## one 'x' rows behind the new row, where x equals
            ## the number of visible lines plus 1
            self.top_visible_line_index = new_row - NUMBER_OF_VISIBLE_LINES + 1

            ## now that you have a new top visible line
            ## set, update the visible lines
            self.update_visible_lines()

        ### clamp final colum value so it's within
        ### existing characters indices (since column number
        ### represents index of current character)

        max_col_index = len(self.lines[new_row])

        self.col = max(min(max_col_index, current_col + cols), 0)

        ### admin task: snap cursor to new row and column
        ### defined, also making it assume the size of the
        ### character where it sits (if there is one)

        ## try retrieving character sitting at the visible
        ## row and column we just defined

        try:
            char_obj = self.visible_lines[self.visible_row][self.col]

        ## if an IndexError occurs, it means that there is
        ## no character where the cursor sits, so we check
        ## which specific situation caused this

        except IndexError:

            ## it may be caused by the cursor moving to the
            ## right of the last character
            ##
            ## after checking the conditions and confirming
            ## this is the case, we just position the cursor
            ## at the right of the last character (the one
            ## sitting at the column before the current one)

            if (
                # line is not empty
                max_col_index
                # and index is an unit after the last index
                and self.col == max_col_index
            ):

                char_obj = self.visible_lines[self.visible_row][self.col - 1]

                self.rect.topleft = char_obj.rect.topright

            ## in all other scenarios we assume the line is
            ## empty, so we just place the cursor at the
            ## beginning of the line

            else:

                self.rect.topleft = self.visible_lines[self.visible_row].rect.topleft

        ## if we otherwise succeed in retrieving the char
        ## in the current column, we move the cursor to the
        ## position of that character object;
        ##
        ## we also update the cursor size to that of the
        ## character obj

        else:

            self.rect.topleft = char_obj.rect.topleft
            self.rect.size = char_obj.rect.size

    go_up_ins = partialmethod(navigate_ins, -1, 0)
    go_down_ins = partialmethod(navigate_ins, 1, 0)

    go_many_up_ins = partialmethod(navigate_ins, -4, 0)
    go_many_down_ins = partialmethod(navigate_ins, 4, 0)

    jump_page_up_ins = partialmethod(navigate_ins, -LINES_IN_A_JUMP, 0)
    jump_page_down_ins = partialmethod(navigate_ins, LINES_IN_A_JUMP, 0)

    go_left_ins = partialmethod(navigate_ins, 0, -1)
    go_right_ins = partialmethod(navigate_ins, 0, 1)

    go_to_line_start_ins = partialmethod(navigate_ins, 0, -INFINITY)
    go_to_line_end_ins = partialmethod(navigate_ins, 0, INFINITY)

    go_to_top_ins = partialmethod(navigate_ins, -INFINITY, 0)
    go_to_bottom_ins = partialmethod(navigate_ins, INFINITY, 0)

    reposition_ins = partialmethod(navigate_ins, 0, 0)

    def update_visible_lines(self):
        """Update which lines are visible in normal mode.

        Updates the contents of the 'visible_lines'
        attribute, a list with references to the
        lines that are visible on the editing area,
        """
        ### backup x of current visible lines
        x = self.visible_lines.rect.x

        ### define start and end of slice from the list
        ### of lines which contains the visible lines

        start = self.top_visible_line_index
        end = start + NUMBER_OF_VISIBLE_LINES

        ### update the visible_lines list
        self.visible_lines[:] = self.lines[start:end]

        ### position the visible lines vertically with the
        ### stored values for the y coordinate

        for y, line in zip(self.y_values, self.visible_lines):
            line.rect.topleft = x, y

        ### admin task: since we changed which lines are
        ### visible, perform the corresponding routine
        self.visible_lines_routine()
