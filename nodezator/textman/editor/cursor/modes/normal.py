"""Normal mode behaviour for Cursor class."""

### standard library import
from functools import partialmethod


### third-party imports

from pygame import (
    QUIT,
    KEYDOWN,
    MOUSEBUTTONUP,
    K_j,
    K_k,
    K_h,
    K_l,
    K_UP,
    K_DOWN,
    K_LEFT,
    K_RIGHT,
    KMOD_SHIFT,
    K_i,
    K_a,
    K_o,
    K_x,
    K_HOME,
    K_END,
    K_PAGEUP,
    K_PAGEDOWN,
    K_4,
    K_0,
    K_F1,
)

from pygame.event import get as get_events


### local imports

from .....loopman.exception import QuitAppException

from .....htsl.main import open_htsl_link

from ...constants import NUMBER_OF_VISIBLE_LINES

from ...line import Line


class NormalMode:
    """Behaviour for cursor's normal mode."""

    def normal_mode_handling(self):
        """Get and handle events for normal mode."""
        for event in get_events():

            if event.type == QUIT:
                raise QuitAppException

            ### key down events

            elif event.type == KEYDOWN:

                ### show help text for text editor

                if event.key == K_F1:

                    open_htsl_link(
                        "htap://help.nodezator.pysite/"
                        "text-editor-vim-like-behavior.htsl"
                    )

                ### keys to move cursor

                elif event.key in (K_h, K_LEFT):
                    self.go_left()

                elif event.key in (K_j, K_DOWN):
                    self.go_down()

                elif event.key in (K_k, K_UP):
                    self.go_up()

                elif event.key in (K_l, K_RIGHT):
                    self.go_right()

                ### keys to enter insert mode

                elif event.key == K_i:
                    self.insert_before()
                elif event.key == K_a:
                    self.insert_after()

                elif event.key == K_o:

                    if KMOD_SHIFT & event.mod:
                        self.insert_above()

                    else:
                        self.insert_bellow()

                ### delete character under cursor
                elif event.key == K_x:
                    self.delete_under()

                ### snap cursor to different edges of
                ### text

                ## using home/end keys

                elif event.key == K_HOME:

                    if KMOD_SHIFT & event.mod:
                        self.go_to_top()

                    else:
                        self.go_to_line_start()

                elif event.key == K_END:

                    if KMOD_SHIFT & event.mod:
                        self.go_to_bottom()

                    else:
                        self.go_to_line_end()

                ## using numbers from alphanumeric portion
                ## of keyboard (just like in Vim software)

                elif event.key == K_4 and KMOD_SHIFT & event.mod:
                    self.go_to_line_end()

                elif event.key == K_0:
                    self.go_to_line_start()

                ### jump a page up or down (a page is a
                ### number of lines which fits the editing
                ### area) or snap to top or bottom of text

                elif event.key == K_PAGEUP:

                    if KMOD_SHIFT & event.mod:
                        self.go_to_top()

                    else:
                        self.jump_page_up()

                elif event.key == K_PAGEDOWN:

                    if KMOD_SHIFT & event.mod:
                        self.go_to_bottom()

                    else:
                        self.jump_page_down()

            ### mouse button up event

            elif event.type == MOUSEBUTTONUP:

                ### mouse release action

                if event.button == 1:
                    self.te.mouse_release_action(event.pos)

                ### jump many lines up or down using the
                ### mousewheel

                elif event.button == 4:
                    self.go_many_up()
                elif event.button == 5:
                    self.go_many_down()

    def start_insert(self, where):
        """Enable insert mode and perform setups.

        Parameters
        ==========
        where (string)
            indicates where to begin inserting text.
        """
        ### enable insert mode
        self.enable_insert_mode()

        ### perform extra setups according to specific
        ### position from where to start inserting text

        ## if must start inserting text 'after' cursor
        ## position, just move cursor one character to the
        ## right in insert mode
        if where == "after":
            self.go_right_ins()

        ## if must start inserting text before the cursor,
        ## there's no need to do anything else
        elif where == "before":
            pass

        ## if must start inserting text above or below
        ## the current position of the cursor, call
        ## special method to perform extra setups

        elif where in ("above", "below"):
            self.add_line(where)

        ## there shouldn't possibly be another scenario,
        ## in which case we indicate it by raising an
        ## exception

        else:

            raise RuntimeError(
                (
                    "Entered 'else' block never supposed to"
                    " be entered; logic went wrong somewhere"
                )
            )

    insert_before = partialmethod(start_insert, "before")
    insert_after = partialmethod(start_insert, "after")
    insert_above = partialmethod(start_insert, "above")
    insert_bellow = partialmethod(start_insert, "below")

    def add_line(self, where):
        """Add new line above or below current one.

        Parameters
        ==========
        where (string)
            indicates whether the line is to be added
            above or below the current one.
        """
        ### define an index wherein to insert the new
        ### line, depending on whether it must be inserted
        ### above or below the current one

        ## if we want a new line above the current one,
        ## we want to insert a new line where the current
        ## line is
        if where == "above":
            index = self.row

        ## if we want a new line below the current one we
        ## use the index of the next line (current line plus
        ## one)
        elif where == "below":
            index = self.row + 1

        ## there shouldn't possibly be another scenario,
        ## in which case we indicate it by raising an
        ## exception

        else:

            raise RuntimeError(
                (
                    "Entered 'else' block never supposed to"
                    " be entered; logic went wrong somewhere"
                )
            )

        ### insert new line at the chosen index
        self.lines.insert(index, Line(""))

        ### since some change took place, we execute the
        ### edition routine;
        ###
        ### it is important to execute this before updating
        ### the visible lines, in order to prevent syntax
        ### highlighting to be applied to the visible lines,
        ### in case the syntax highlighting is enabled
        self.edition_routine()

        ### update cursor row and column according to
        ### whether the line was inserted above or below
        ### the current one

        if where == "above":

            ## update which lines are visible, since
            ## we added a new one
            self.update_visible_lines()

            ## go to the beginning of line, since it is
            ## empty; we could also just have used the
            ## reposition_ins() method here
            self.go_to_line_start_ins()

        elif where == "below":

            ## the go_down_ins() call executed after this
            ## "if block" automatically updates the visible
            ## lines when the cursor is in the last visible
            ## line;
            ##
            ## if the cursor isn't in the last visible line,
            ## though, we'll have to execute it ourselves,
            ## which is what we do here
            if self.visible_row != NUMBER_OF_VISIBLE_LINES - 1:
                self.update_visible_lines()

            ## make it so the cursor goes down one line,
            ## so it is now in the new line
            self.go_down_ins()

        ### also check the need to update the editing area
        self.check_editing_area()

    def delete_under(self):
        """Delete char under cursor."""
        ### try deleting current character (self.col) in
        ### in current line (self.row)
        try:
            del self.lines[self.row][self.col]

        ### if it fails, it just means the line is empty,
        ### so there's nothing left to do, we return early
        except IndexError:
            return

        ### if it works, though...

        ## reposition characters of current line and cursor

        self.lines[self.row].reposition_chars()
        self.reposition()

        ## execute the edition routine
        self.edition_routine()
