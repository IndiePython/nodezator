"""Option menu class extension with lifetime operations."""

### third-party imports

from pygame import (
    QUIT,
    KEYUP,
    K_ESCAPE,
    K_RETURN,
    K_KP_ENTER,
    MOUSEBUTTONUP,
    MOUSEMOTION,
    Rect,
)

from pygame.display import update

from pygame.event import get as get_events
from pygame.draw import rect as draw_rect
from pygame.mouse import get_pos as get_mouse_pos

from pygame.math import Vector2


### local imports

from ...pygameconstants import (
    SCREEN,
    blit_on_screen,
    WINDOW_RESIZE_EVENT_TYPE,
)

from ...classes2d.single import Object2D

from ...loopman.exception import (
    QuitAppException,
    SwitchLoopException,
)

from ...colorsman.colors import BLACK


class OptionMenuLifetimeOperations(Object2D):
    """Operations for the lifetime of the OptionMenu.

    That is, operations that are mostly or only used while
    the option menu is alive, as opposed to the ones used
    to assist in instantiation/setup.
    """

    def update_image(self):
        """Update image attribute with option surface.

        Works by using especial surface of option widget
        corresponding to the current value as the surf for
        the image attribute
        """
        ### iterate over the option widgets until you
        ### find the one whose value is equal to the
        ### current set value, in which case you reference
        ### the surface in its 'chosen_surf' attribute in
        ### the 'image' attribute of our option menu and
        ### return to prevent the method to further advance
        ### to the "raise statement"

        for widget in self.option_widgets:

            if widget.value == self.value:

                self.image = widget.chosen_surf
                return

        ### unless there is a bug somewhere, this statement
        ### should never be reached

        raise RuntimeError(
            "this block should never be executed, since"
            " there must always be one option whose"
            " value equals the current set value"
        )

    def get(self):
        """Return current value of OptionMenu instance."""
        return self.value

    def set(self, value, custom_command=True):
        """Set the current value of this OptionMenu instance.

        Parameters
        ==========
        value (any python object)
            value to which the widget will be set. It must
            be inside the list in the "options" attribute;
            no type checking is performed, since the items
            of the option list are already type set;
        custom_command (boolean)
            indicates whether the custom command must be
            executed or not.
        """
        ### if the value is already set, exit the method by
        ### returning, since choosing a value which is
        ### already chosen isn't considered a change at all
        if self.value == value:
            return

        ### if value received isn't within allowed values
        ### (values inside "options" attribute), report and
        ### cancel this operation by returning

        if value not in self.options:

            print("'value' isn't among available options")
            return

        ### assign the value to the "value" attribute
        self.value = value

        ### update image so it corresponds with value
        self.update_image()

        ### execute custom command if requested
        if custom_command:
            self.command()

    def reset_value_and_options(self, value, options, custom_command=True):
        """Reset available options and set given value.

        Parameters
        ==========
        value (Python value)
            the value must be inside the options iterable
            as well, and be of one of the allowed types
            (str, int, float, bool) or must be None.
        options (iterable of values)
            values the widget is allowed to assume. Each
            value in the options must be of type str, int
            float, bool or must be None.
        custom_command (boolean)
            indicates whether the custom command must be
            executed or not.
        """
        ### make sure options is a list
        options = list(options)

        ### check conditions that justify cancelling the
        ### operation; if any of them are confirmed, just
        ### exit the method by returning

        ## the options are the same as the current ones
        ## (and in the same order)

        if options == self.options:
            return

        ## the value and options are not valid

        try:
            self.validate_value_and_options(value, options)
        except (ValueError, TypeError) as err:

            print(err)
            return

        ### if we reach this point in the method, then we
        ### can safely replace the options and set the new
        ### value

        ## backup the current topleft position
        topleft = self.rect.topleft

        ## set the value and the options

        self.value = value
        self.options = options

        ## rebuild the widget structure
        self.build_widget_structure()

        ## restore the topleft position
        self.rect.topleft = topleft

        ### execute custom command if requested
        if custom_command:
            self.command()

    def get_focus(self, event):
        """Perform setups and get focus to itself.

        Meant to be triggered by a mouse release action.

        Parameters
        ==========
        event (pygame.event.Event of pygame.MOUSEBUTTONUP
        type)
            required in order to comply with mouse action
            protocol; we use its "pos" attribute to retrieve
            the mouse position;

            check pygame.event module documentation on
            pygame website for more info about this event
            object.
        """
        ### assign behaviours

        self.draw = self.draw_expanded
        self.on_mouse_release = self.choose_option

        self.handle_input = self.handle_events_and_mouse_pos

        ### position options
        self.align_subobjects()

        ### store topleft left position for later
        ### reference if needed
        self.last_topleft = self.rect.topleft

        ### react as if mouse moved
        self.on_mouse_motion(event.pos)

        ### give focus to self by raising a manager switch
        ### exception with a reference to this widget
        raise SwitchLoopException(self)

    def align_options(self):
        self.option_widgets.rect.midtop = self.rect.midbottom

        self.option_widgets.rect.clamp_ip(self.clamp_area)

    def align_options_and_scroll_arrows(self):
        align_area = self.clamp_area

        self.option_widgets.rect.center = self.rect.center

        self.option_widgets.rect.clamp_ip(align_area)

        self.option_widgets.rect.y = (
            align_area.top + self.upper_scroll_arrow.get_height()
        )

        x = self.option_widgets.rect.x

        self.upper_arrow_pos = (x, align_area.top)

        self.lower_arrow_pos = (
            x,
            (align_area.bottom - self.lower_scroll_arrow.get_height()),
        )

    def lose_focus(self):
        """Assign behaviours and focus loop manager."""
        ### assign behaviours

        self.draw = self.draw_collapsed
        self.on_mouse_release = self.get_focus

        ### switch to the stored loop holder (if
        ### None, the default loop holder used is
        ### the WindowManager instance from the module
        ### winman.main)
        raise SwitchLoopException(self.loop_holder)

    def handle_events(self):
        """Iterate over event queue processing events."""
        for event in get_events():

            ### raise special exception if user attempts
            ### to quit the application
            if event.type == QUIT:
                raise QuitAppException

            ### lose focus if escape key is released

            elif event.type == KEYUP:

                if event.key == K_ESCAPE:
                    self.lose_focus()

                elif event.key in (K_RETURN, K_KP_ENTER):
                    self.choose_option_under_mouse()

            ### act when the mouse left or right button
            ### is released

            elif event.type == MOUSEBUTTONUP:

                if event.button in (1, 3):

                    ## if mouse is out of the body, lose
                    ## focus, regardless of the button
                    ## released

                    if self.out_of_body(event.pos):
                        self.lose_focus()

                    ## otherwise, if the button released
                    ## is the left button, trigger the
                    ## mouse release method

                    elif event.button == 1:
                        self.on_mouse_release(event)

                elif event.button in (4, 5):
                    self.on_mousewheel(event)

            ### if the mouse moves try highlighting the
            ### hovered option, if there's one

            elif event.type == MOUSEMOTION:
                self.on_mouse_motion(event.pos)

            ### if window is resized, set handle_input
            ### to a new callable that keeps handling
            ### events and mouse pos and at the same time
            ### watches out for movement of the widget

            elif event.type == WINDOW_RESIZE_EVENT_TYPE:

                self.handle_input = self.watch_out_for_movement

    def watch_out_for_movement(self):

        if self.rect.topleft != self.last_topleft:

            diff = Vector2(self.rect.topleft) - self.last_topleft

            self.last_topleft = self.rect.topleft

            self.align_subobjects()

            self.on_mouse_motion(get_mouse_pos())

            ##
            self.draw_on_window_resize()
            self.draw()

            ##
            self.handle_input = self.handle_events_and_mouse_pos

        self.handle_events_and_mouse_pos()

    def scroll_when_hovering_scroll_arrow(self):
        """"""
        mouse_pos = mouse_x, mouse_y = get_mouse_pos()

        options_rect = self.option_widgets.rect

        left = options_rect.left
        right = options_rect.right

        clamp_area = self.clamp_area

        top = clamp_area.top + self.upper_scroll_arrow.get_height()
        bottom = clamp_area.bottom - self.lower_scroll_arrow.get_height()

        if left < mouse_x < right and not (top < mouse_y < bottom):

            self.scroll_vertically(-10 if mouse_y < top else 10)

    def handle_events_and_mouse_pos(self):

        self.handle_events()
        self.handle_mouse_pos()

    def out_of_body(self, position):
        """Return True if position is outside the body.

        Parameters
        ==========
        position (2-tuple of integers)
            x and y coordinates representing the mouse
            position on the screen.
        """
        return not self.option_widgets.rect.collidepoint(position)

    def choose_option(self, event):
        """Choose option if it collides by executing method.

        Meant to be triggered by a mouse release action.

        The method in question is the mouse release
        method of the hovered option. We also make it so
        focus is lost (since the desired option was just
        set).

        Parameters
        ==========
        event (pygame.event.Event of pygame.MOUSEBUTTONUP
        type)
            parameter required in order to comply with the
            mouse action protocol; it is also necessary in
            this method, since its "pos" attribute is used
            to retrieve the mouse position;

            check pygame.event module documentation on
            pygame website for more info about this event
            object.
        """
        ### retrieve mouse position
        mouse_pos = event.pos

        ### iterate over option widgets, looking for the
        ### widget which collides with the mouse

        for widget in self.option_widgets:

            ## if you find the widget, execute its
            ## mouse release method and lose the focus
            ## of this option menu (there's no need to
            ## break out of this "for loop", since loosing
            ## the focus does so by raising an exception)

            if widget.rect.collidepoint(mouse_pos):

                widget.on_mouse_release(event)
                self.lose_focus()

    def choose_option_under_mouse(self):
        """Choose option under mouse, if any."""
        ### get mouse position
        mouse_pos = get_mouse_pos()

        ### iterate over option widgets, looking for the
        ### widget which collides with the mouse

        for widget in self.option_widgets:

            ## if you find the widget, execute its
            ## select method and lose the focus
            ## of this option menu (there's no need to
            ## break out of this "for loop", since loosing
            ## the focus does so by raising an exception)

            if widget.rect.collidepoint(mouse_pos):

                widget.select()
                self.lose_focus()

    def scroll_with_mousewheel(self, event):
        """"""
        if self.option_widgets.rect.collidepoint(event.pos):

            self.scroll_vertically(10 if event.button == 4 else -10)

    def scroll_vertically(self, dy):
        """"""
        rect = self.option_widgets.rect

        scroll_area = self.clamp_area

        rect.move_ip(0, dy)

        if dy < 0:

            bottom_limit = scroll_area.bottom - self.lower_scroll_arrow.get_height()
            if rect.bottom < bottom_limit:
                rect.bottom = bottom_limit

        elif dy > 0:

            top_limit = scroll_area.top + self.upper_scroll_arrow.get_height()
            if rect.top > top_limit:
                rect.top = top_limit

    def on_mouse_motion(self, mouse_pos):
        """Highlight option widget if position collides.

        we also unhighlight all other widgets.

        Parameters
        ==========
        mouse_pos (2-tuple of integers)
            x and y coordinates representing the mouse
            position on the screen.
        """
        ### iterate over the option widgets, highlighting
        ### the one which collides with the mouse and
        ### unhighlighting the ones which don't

        for widget in self.option_widgets:

            if widget.rect.collidepoint(mouse_pos):
                widget.highlight()

            else:
                widget.unhighlight()

    def draw_collapsed(self):
        """Draw self.image on screen.

        Extends Object2D.draw.
        """
        super().draw()

    def draw_expanded(self):
        """Draw self and widgets and update screen."""
        ### draw the option menu surface (the one in the
        ### 'image' attribute
        super().draw()

        ### draw subobjects
        self.draw_subobjects()

        ### finally, update the screen
        update()  # pygame.display.update

    def draw_options(self):

        ### draw options
        self.option_widgets.draw()

        ### draw an outline around the option widgets

        draw_rect(SCREEN, BLACK, self.option_widgets.rect.inflate(2, 2), 1)

    def draw_options_and_scroll_arrows(self):
        """"""
        draw_area = self.clamp_area

        ### draw options which collide with the draw area
        self.option_widgets.draw_colliding(draw_area)

        ### draw scroll arrows

        blit_on_screen(self.upper_scroll_arrow, self.upper_arrow_pos)

        blit_on_screen(self.lower_scroll_arrow, self.lower_arrow_pos)

        ### draw an outline around the scroll arrows and
        ### visible options

        draw_rect(
            SCREEN,
            BLACK,
            Rect(
                *self.upper_arrow_pos, self.option_widgets.rect.width, draw_area.height
            ).inflate(2, 2),
            1,
        )
