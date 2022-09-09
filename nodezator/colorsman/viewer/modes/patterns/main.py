"""Colors viewer extension for the patterns mode."""

### standard library import
from types import GeneratorType


### third-party imports

from pygame import (
    QUIT,
    KEYUP,
    K_ESCAPE,
    K_RETURN,
    K_KP_ENTER,
    MOUSEBUTTONUP,
)

from pygame.event import get as get_events

from pygame.display import update


### local imports

from .....pygameconstants import blit_on_screen

from .....ourstdlibs.behaviour import (
    empty_function,
    get_oblivious_callable,
)

from .....loopman.exception import QuitAppException

from .....widget.optionmenu.main import OptionMenu

from .....classes2d.single import Object2D

from .....textman.render import render_text
from .....fontsman.constants import ENC_SANS_BOLD_FONT_HEIGHT

from ....colors import BUTTON_FG, BUTTON_BG, WINDOW_FG, WINDOW_BG


## pattern drawing functions

from .waves import draw_waves
from .particles import draw_circles


### names (strings) mapped to drawing operations they
### represent

PATTERN_DRAWING_MAP = {"waves": draw_waves, "circles": draw_circles}


### class definition


class PatternsMode:
    """Has operations to draw patterns from given colors."""

    def __init__(self):
        """Create support objects for the patterns mode."""
        ### create a "Pattern:" label to indicate the
        ### option menu for choosing patterns

        self.pattern_label = Object2D.from_surface(
            surface=(
                render_text(
                    text="Pattern:",
                    font_height=ENC_SANS_BOLD_FONT_HEIGHT,
                    padding=5,
                    foreground_color=WINDOW_FG,
                    background_color=WINDOW_BG,
                )
            ),
        )

        ### create option menu from which to choose patterns

        pattern_names = sorted(PATTERN_DRAWING_MAP.keys())

        clamp_area = self.rect

        self.pattern_options = OptionMenu(
            loop_holder=self,
            value=pattern_names[0],
            options=pattern_names,
            clamp_area=clamp_area,
            command=self.redraw_pattern,
            draw_on_window_resize=self.patterns_draw,
        )

        ### create a button to redraw/change the pattern

        self.redraw_pattern_button = Object2D.from_surface(
            surface=(
                render_text(
                    text="Redraw",
                    font_height=ENC_SANS_BOLD_FONT_HEIGHT,
                    padding=5,
                    foreground_color=BUTTON_FG,
                    background_color=BUTTON_BG,
                    depth_finish_thickness=1,
                )
            ),
            on_mouse_release=(get_oblivious_callable(self.redraw_pattern)),
        )

        ### placeholder attribute for a generator closing
        ### method
        self.close_generator = empty_function

    def redraw_pattern(self):
        """Redraw the chosen pattern.

        It is also used as the preparation operation for
        the patterns mode.
        """
        ### perform the operation stored in the
        ### 'close_generator' attribute, which might be
        ### an empty function or actually close a previously
        ### created generator
        self.close_generator()

        ### if the patterns option menu isn't stored in the
        ### list of the buttons, append it along with the
        ### redraw pattern button

        if self.pattern_options not in self.buttons:

            self.labels.append(self.pattern_label)

            self.buttons.extend(
                (
                    self.pattern_options,
                    self.redraw_pattern_button,
                )
            )

        ### get the name of the chosen pattern from the
        ### options menu
        pattern_name = self.pattern_options.get()

        ### use the name to retrieve the corresponding
        ### drawing operation from the pattern drawing map
        drawing_callable = PATTERN_DRAWING_MAP[pattern_name]

        ### perform the drawing operation with the surface
        ### representing the canvas and the list of colors,
        ### catching the resulting return value

        result = drawing_callable(self.canvas.image, self.colors)

        ### set the 'update' and 'close_generator'
        ### attributes to specific objects depending on
        ### whether the result is a generator-iterator
        ### or not

        ## if the result is a generator-iterator, set the
        ## 'update' and 'close_generator' attributes to
        ## references of the generator-iterator's '__next__'
        ## and 'close' methods, respectively

        if isinstance(result, GeneratorType):

            self.update = result.__next__

            self.close_generator = result.close

        ## otherwise just set both attributes to an empty
        ## function

        else:

            self.update = self.close_generator = empty_function

    ### alias the redraw pattern as the preparation
    ### operation of the patterns mode
    patterns_prepare_mode = redraw_pattern

    def patterns_exit_mode(self):
        """Exit operation for the patterns mode."""
        ### if the pattern option menu is listed
        ### among the buttons, it means objects related
        ### to the pattern mode are present in the
        ### collections for buttons and labels, so remove
        ### such objects

        if self.pattern_options in self.buttons:

            ## remove label
            self.labels.remove(self.pattern_label)

            ## remove option menu and redraw button

            for obj in (
                self.pattern_options,
                self.redraw_pattern_button,
            ):
                self.buttons.remove(obj)

        ### perform the operation stored in the
        ### 'close_generator' attribute, which might be
        ### an empty function or actually close a previously
        ### created generator
        self.close_generator()

        ### reset the 'close_generator' attribute to an
        ### empty function
        self.close_generator = empty_function

    def patterns_event_handling(self):
        """Event handling for the patterns mode.

        Grab and process events from pygame.event.get.
        """
        for event in get_events():

            ### raise a specific exception if the user
            ### tries to quit the app
            if event.type == QUIT:
                raise QuitAppException

            ### if user releases one of following keys,
            ### trigger exiting the colors viewer by
            ### setting the 'running' flag to False

            elif event.type == KEYUP:

                if event.key in (K_ESCAPE, K_RETURN, K_KP_ENTER):
                    self.running = False

            ### if the left mouse button is released,
            ### execute the corresponding mouse action
            ### method

            elif event.type == MOUSEBUTTONUP:

                if event.button == 1:
                    self.color_list_on_mouse_release(event)

    def patterns_on_mouse_release(self, event):
        """Trigger exiting colors viewer or invoke button.

        Parameters
        ==========
        event (pygame.event.Event instance)
            event of type MOUSEBUTTONUP; its 'pos' attribute
            contains a tuple with two integers and represents
            the position of the mouse on the screen;

            check the glossary entry for the "mouse action
            protocol".
        """
        ### retrieve the position of the mouse
        mouse_pos = event.pos

        ### if the mouse is out of the area occupied by
        ### the color viewer, trigger exiting the color
        ### viewer by turning the 'running' flag off and
        ### exiting the method by returning

        if not self.rect.collidepoint(event.pos):
            self.running = False
            return

        ### if we don't return in the previous block, we
        ### look for the first button which collides with
        ### the mouse

        for button in self.buttons:

            ## if a button collides, execute its mouse
            ## release action if it has one, then break out
            ## of the "for loop"

            if button.rect.collidepoint(mouse_pos):

                try:
                    method = getattr(button, "on_mouse_release")

                except AttributeError:
                    pass

                else:
                    method(event)

                break

    def patterns_draw(self):
        """Drawing operation for the patterns mode."""
        ### draw the background of the colors viewer in
        ### the screen
        blit_on_screen(self.image, self.rect)

        ### draw the labels and buttons on the screen

        self.labels.draw()
        self.buttons.draw()

        ### draw the canvas on the screen
        self.canvas.draw()

        ### finally, update the screen
        update()  # pygame.display.update
