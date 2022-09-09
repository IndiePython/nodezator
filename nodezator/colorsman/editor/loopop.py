"""Class extension w/ colors editor' loop operations."""

### standard library import
from functools import partialmethod


### third-party imports

from pygame import (
    QUIT,
    MOUSEBUTTONDOWN,
    MOUSEBUTTONUP,
    KEYDOWN,
    K_LEFT,
    K_a,
    K_RIGHT,
    K_d,
    K_HOME,
    K_END,
    K_DELETE,
    KEYUP,
    K_ESCAPE,
    K_RETURN,
    K_KP_ENTER,
)

from pygame.event import get as get_events

from pygame.display import update


### local imports

from ...pygameconstants import blit_on_screen

from ...classes2d.single import Object2D

from ...loopman.main import LoopHolder

from ...surfsman.cache import UNHIGHLIGHT_SURF_MAP

from ...ourstdlibs.color.custom import custom_format_color


class LoopOperations(Object2D, LoopHolder):
    """Loop-related operations for the ColorsEditor."""

    def edit_colors(
        self,
        color_value=((255, 0, 0),),
        color_format="rgb_tuple",
        alone_when_single=True,
    ):
        """Display dialog to edit/pick colors.

        Note that, during the editing session, the color
        value is treated as though the color_format and
        alone_when_single parameters are set to 'rgb_ints'
        and False, respectively, regardless of the values
        provided by the user.

        The values provided by the user for those parameters
        are relevant, though. Such actual values received
        are used when returning the value back at the end
        of the editing session, if the user doesn't cancel
        the editing session.

        Parameters
        ==========

        color_value (special value)

            if an special value, it must be an object
            representing one or multiple color values;

            it may be in different formats:

            1) a tuple of RGB(A) values (integers so that
               0 <= integer <= 255), representing a
               single color;
            2) a string representing a color in hex
               format using '#ffffff' or '#ffffffff'
               format, representing a single color;
            3) a tuple in which each item represents a
               color; such items must all be in the
               format specified in either the item 1)
               or item 2), never both.

        color_format (string)

            either 'rgb_tuple', if individual colors
            must use the representation described in
            the item (1) of the 'color_value' parameter
            explanation above or 'hex_string', if the
            format in item (2) must be used instead;

        alone_when_single (boolean)

            when True, instead of a tuple of colors, the
            color itself is used as the value when the
            color value represents a single color (that is,
            when True, if only one color is stored, it will
            be either a string or a tuple of integers
            representing a single color, instead of a tuple
            containing such color);

            for instance, for
            color_format='hex_string' and
            alone_when_single=True, say the value of the
            button is ['#ffffff', '#00ff00aa'], if you
            go and delete any color (for instance, the
            second one), instead of ['#ffffff'] as the
            value of the button, you'll end up with
            '#ffffff' (that is, the string itself).
        """
        ### set a edition session cancelation flag to False
        self.cancel_edition = False

        ### treat the color properly in order to obtain a
        ### tuple of full rgb colors

        ## convert color value to a tuple of rgb colors

        try:
            colors = custom_format_color(color_value, "rgb_tuple", False)

        ## XXX maybe show a dialog with the
        ## error message here? or just print on the
        ## screen? probably also log the error;
        ## ponder;

        ## if a value error is raised, though,
        ## it means  there's something wrong with
        ## the given value, so we return earlier
        except ValueError:
            return None

        ### set the full rgb colors into the colors panel
        self.colors_panel.set_colors(colors)

        ### loop
        self.loop()

        ### blit a semitransparent surface over the screen
        ### on the area occupied by self.rect to leave the
        ### area temporarily darkened in case it keeps
        ### showing even after leaving this color picker
        ### (in some cases the loop holder which called
        ### this method might not care to update the area
        ### of the screen previously occupied by this color
        ### picker, making it so it keeps appearing as if
        ### it was still active on the screen)
        self.unhighlight()

        ### define appropriate value to return according
        ### to the value of the "cancel edition flag"

        to_return = (
            ## if the "cancel edition flag" is turned on,
            ## the value is None
            None
            if self.cancel_edition
            ## otherwise, it is the edited color(s) from
            ## the colors panel, converted according to
            ## the settings given as the 'color_format'
            ## and 'alone_when_single' arguments
            else custom_format_color(
                self.colors_panel.get_colors(), color_format, alone_when_single
            )
        )

        ### finally, return the value after freeing up
        ### memory used by the colors panel

        self.colors_panel.free_up_memory()

        return to_return

    def handle_input(self):
        """Get and handle events from event queue."""
        ### iterate over the events from the event queue,
        ### processing the relevant ones accoding to their
        ### settings

        for event in get_events():

            ### quit the application
            if event.type == QUIT:
                self.quit()

            ### perform the corresponding action if the user
            ### presses the left mouse button, passing the
            ### event object as an argument of the operation

            elif event.type == KEYUP:

                if event.key == K_ESCAPE:

                    self.cancel()
                    break

                elif event.key in (K_RETURN, K_KP_ENTER):
                    self.exit_loop()

            elif event.type == MOUSEBUTTONDOWN:

                if event.button == 1:
                    self.on_mouse_click(event)

            ### act according to the release of the
            ### mouse left and right buttons

            elif event.type == MOUSEBUTTONUP:

                ## if button isn't the left or right mouse
                ## button, skip this event by using the
                ## 'continue' statement, since we are
                ## not interested in the other buttons
                ## here
                if event.button not in (1, 3):
                    continue

                ## if the left or right mouse buttons are
                ## released outside the colors editor
                ## boundaries, trigger the cancellation
                ## of the editing session and exit this
                ## method earlier by breaking out of the
                ## "for loop"

                if not self.rect.collidepoint(event.pos):

                    self.cancel()
                    break

                ## if we are inside boundaries, though
                ## (the "if block" above fails), and the
                ## mouse button is the left one,
                ## perform the corresponding mouse action
                ## using the event as an argument
                elif event.button == 1:
                    self.on_mouse_release(event)

            ### perform actions when specific keys were
            ### pressed

            elif event.type == KEYDOWN:

                if event.key in (K_LEFT, K_a):
                    self.colors_panel.go_left()

                elif event.key in (K_RIGHT, K_d):
                    self.colors_panel.go_right()

                elif event.key == K_HOME:
                    self.colors_panel.go_to_start()

                elif event.key == K_END:
                    self.colors_panel.go_to_end()

                elif event.key == K_DELETE:
                    self.colors_panel.remove_color_widgets()

    def on_mouse_action(self, method_name, event):
        """Call colliding object if has appropriate method.

        The object may be the colors panel or one of the
        buttons.

        Parameters
        ==========

        method_name (string)
            name of method to look for in object.
        event (pygame.event.Event instance)
            event.type is either pygame.MOUSEBUTTONDOWN
            or MOUSEBUTTONUP;

            we use its 'pos' attribute, which contains
            the position of the mouse when the event
            occurred;

            required in order to comply with mouse
            action protocol;

            Check pygame.event module documentation on
            pygame website for more info about this event
            object;
        """
        ### retrieve the mouse position
        mouse_pos = event.pos

        ### iterate over the colors panel and the buttons

        for obj in (self.colors_panel, *self.buttons):

            ## check whether the object being iterated
            ## collides with the mouse

            if obj.rect.collidepoint(mouse_pos):

                ## now that we now this object collides
                ## with the mouse, check whether the
                ## object has an attribute named according
                ## to the value in the 'method_name'
                ## argument
                try:
                    method = getattr(obj, method_name)

                ## if it hasn't, then we just pass
                except AttributeError:
                    pass

                ## otherwise we execute the method contained
                ## in such attribute, passing the event
                ## object as an argument
                else:
                    method(event)

                ## regardless of whether or not the object
                ## had an operation retrieved and executed
                ## in the last clauses, break out of the
                ## "for loop"
                break

    ## partial implementations of the on_mouse_action
    ## method, named to comply with the mouse action
    ## protocol

    on_mouse_click = partialmethod(on_mouse_action, "on_mouse_click")

    on_mouse_release = partialmethod(on_mouse_action, "on_mouse_release")

    def update(self):
        """Update colors panel and scales."""
        self.colors_panel.update()
        self.scales.call_update()

    def draw(self):
        """Draw the color editor and other objects.

        Extends Object2D.draw.
        """
        ### draw the 'image' surface of the colors editor,
        ### which works as a background
        super().draw()

        ### draw the colors panel
        self.colors_panel.draw()

        ### draw objects which comprise scales
        self.scales.call_draw()

        ### draw buttons (which include entries) and labels

        self.buttons.draw()
        self.labels.draw()

        ### finally, update the screen
        update()  # pygame.display.update

    def unhighlight(self):
        """Draw semitransparent surface on self.rect area.

        The goal is to make the colors editor appear
        unhighlighted, so the next loop holder appears
        highlighted.
        """
        blit_on_screen(UNHIGHLIGHT_SURF_MAP[self.rect.size], self.rect)
