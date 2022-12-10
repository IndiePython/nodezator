"""IntFloatEntry extension w/ mode-related operations."""

### standard library import
from string import digits, ascii_letters


### third-party imports

from pygame import (
    ### event types
    QUIT,
    KEYDOWN,
    KEYUP,
    MOUSEBUTTONUP,
    MOUSEMOTION,
    ### keys
    K_ESCAPE,
    K_RETURN,
    K_KP_ENTER,
    K_BACKSPACE,
    K_DELETE,
    K_LEFT,
    K_RIGHT,
    K_HOME,
    K_END,
    K_LSHIFT,
    K_RSHIFT,
    KMOD_SHIFT,
    K_e,
    KMOD_CTRL,
)

from pygame.event import get as get_events
from pygame.key import get_mods as get_mods_bitmask

from pygame.mouse import (
    set_pos as set_mouse_pos,
    set_visible as set_mouse_visibility,
)

from pygame.display import update

from pygame.math import Vector2


### local imports

from ...pygameconstants import SCREEN_RECT, WINDOW_RESIZE_EVENT_TYPE

from ...ourstdlibs.behaviour import empty_function

from ...surfsman.render import render_rect

from ...classes2d.single import Object2D

from ...loopman.exception import QuitAppException


### constants

## allowed characters

ALLOWED_CHARS = (
    ### digits so users can form any number
    digits
    ### ascii letters for more complex expressions
    + ascii_letters
    ### characters used to type operators
    + "=+-/*%<>"
    ### '.' dot to mark the decimal point of floats
    + "."
    ### parentheses to help form complex numerical expressions,
    ### including some function calls
    + "()"
    ### brackets representing sequences (for instance:
    ### 'mean([33, 47, 22])'
    + "[]"
    ### comma to also help with function calls with multiple
    ### arguments
    + ","
    ### space character, to improve readability when
    ### writing complex expressions
    + " "
    ### underscore to allow for the usage of underscore in
    ### numerical literals which is possible since Python
    ### 3.6 (for instance: 100_000, 0x_FF_FF_FF_FF)
    + "_"
    ### quotes are also needed in order to type expressions
    ### like "int('0xff', 16)", "int('0b011', 2)", etc.
    + "'"
    + '"'
)


## screen center coordinates
SCREEN_CENTERX, SCREEN_CENTERY = SCREEN_RECT.center

## number with which to divide the amount of mouse movement
## before converting it into incremented/decremented value;
## this must be >= 1;
MOUSE_ATTENUATION = 50


### class definition


class IntFloatModes(Object2D):
    """Mode-related operations for the IntFloatEntry."""

    def keyboard_edition_control(self):
        """Process events in keyboard edition mode.

        Allows edition of the widget contents using the
        keyboard.
        """
        for event in get_events():

            if event.type == QUIT:
                raise QuitAppException

            elif event.type == KEYUP:

                ### exiting the widget by either pressing
                ### escape, enter or numpad checks the
                ### need to revert back from expanded view
                ### and perform setups to resume the edition

                if event.key in (K_ESCAPE, K_RETURN, K_KP_ENTER):

                    self.check_expanded_view_reversal()
                    self.resume_editing()

            elif event.type == KEYDOWN:

                ### move cursor

                if event.key == K_LEFT:
                    self.cursor.go_left()

                elif event.key == K_RIGHT:
                    self.cursor.go_right()

                ### snap cursor to different edges of
                ### line

                elif event.key == K_HOME:
                    self.cursor.go_to_beginning()

                elif event.key == K_END:
                    self.cursor.go_to_end()

                ### remove characters

                elif event.key == K_BACKSPACE:

                    if event.mod & KMOD_CTRL:
                        self.cursor.delete_previous_word()

                    else:
                        self.cursor.delete_previous()

                elif event.key == K_DELETE:
                    self.cursor.delete_under()

                ### enable expanded view

                elif event.key == K_e and event.mod & KMOD_CTRL:
                    self.enable_expanded_view()

                ### if the keydown event has a non-empty
                ### string as its unicode attribute that
                ### is also an allowed char, add such
                ### character

                elif event.unicode and event.unicode in ALLOWED_CHARS:
                    self.cursor.add_text(event.unicode)

            ### releasing either the left or right button
            ### of the mouse out of the widget boundaries
            ### checks the need to revert back from
            ### expanded view and resumes the edition

            elif event.type == MOUSEBUTTONUP:

                if event.button in (1, 3):

                    if not self.rect.collidepoint(event.pos):

                        self.check_expanded_view_reversal()
                        self.resume_editing()

            ## if window is resized, set the movement watch
            ## out routine

            elif event.type == WINDOW_RESIZE_EVENT_TYPE:

                self.movement_watch_out_routine = self.watch_out_for_movement

        self.movement_watch_out_routine()

    def keyboard_edition_update(self):
        """Update widget state in keyboard edition mode."""
        self.update_behind()
        self.cursor.update()

    def keyboard_edition_draw(self):
        """Draw objects in keyboard edition mode.

        Extends Object2D.draw.
        """
        ### draw object behind the widget
        self.draw_behind()

        ### clean the widget image with the background
        self.image.blit(self.background, (0, 0))

        ### draw the line and the cursor on self.image
        self.cursor.draw()

        ### draw self.image
        super().draw()

        ### update the screen (pygame.display.update)
        update()

    def enable_expanded_view(self):
        """Expand widget horizontally to provide space."""
        ### check the existence of a 'backups' attribute
        try:
            self.backups

        ### if it doesn't exist, it means the expanded
        ### view isn't enabled, so we do so

        except AttributeError:

            ### backup the current background, image and
            ### rect

            self.backups = [
                self.background,
                self.image,
                self.rect,
            ]

            ### create a new rect with the same height,
            ### as self.rect but the width of the screen
            ### (except we decrease the width a bit to
            ### provide a nice margin from the boundaries
            ### of the screen)

            new_rect = SCREEN_RECT.inflate(-40, 0)
            new_rect.height = self.rect.height

            ### center the new rect vertically on self.rect
            new_rect.centery = self.rect.centery

            ### assign the new rect to self.rect
            self.rect = new_rect

            ### create a new background and image for
            ### the respective attributes

            self.background = render_rect(*self.rect.size, self.background_color)

            self.image = self.background.copy()

            ### update the image and reposition the
            ### cursor

            self.update_image()
            self.cursor.reposition()

        ### otherwise, since it is enabled already we do
        ### nothing
        else:
            pass

    def check_expanded_view_reversal(self):
        """Perform setups to exit expanded view if needed."""
        ### check the existence of a 'backups' attribute
        try:
            self.backups

        ### if such attribute doesn't exists, just pass,
        ### since there's nothing to revert
        except AttributeError:
            pass

        ### otherwise, restore the backups, delete the
        ### 'backups' attribute and update the image

        else:

            (self.background, self.image, self.rect) = self.backups

            del self.backups

            self.update_image()

    def standby_control(self):
        """Process events in standby mode.

        Allows the widget to watch out for specific events
        to define which mode to enable next.
        """
        for event in get_events():

            if event.type == QUIT:
                raise QuitAppException

            ### enable the next mode depending on the event
            ### that happens first

            ## moving the mouse

            elif event.type == MOUSEMOTION:
                self.enable_mouse_edition_mode()

            ## releasing the mouse left button

            elif event.type == MOUSEBUTTONUP:

                if event.button == 1:
                    self.enable_keyboard_edition_mode()

            ## if window is resized, set the movement watch
            ## out routine

            elif event.type == WINDOW_RESIZE_EVENT_TYPE:

                self.movement_watch_out_routine = self.watch_out_for_movement

        self.movement_watch_out_routine()

    def standby_draw(self):
        """Draw objects in standby mode."""
        ### draw object behind the widget
        self.draw_behind()

        ### draw self.image
        super().draw()

        ### update the screen (pygame.display.update)
        update()

    def mouse_edition_control(self):
        """Process event in mouse edition mode.

        Allows edition of the widget contents by dragging
        the mouse.
        """
        for event in get_events():

            if event.type == QUIT:
                raise QuitAppException

            ### if a shift key is pressed or released,
            ### change the influence of the shift key
            ### on how the mouse movement influences
            ### the displayed value of the widget
            ### (this also performs extra setups)

            ## shift key pressed

            elif event.type == KEYDOWN:

                if event.key in (K_LSHIFT, K_RSHIFT):
                    self.change_shift_influence(True)

            ## shift key released

            elif event.type == KEYUP:

                if event.key in (K_LSHIFT, K_RSHIFT):
                    self.change_shift_influence(False)

            ### if the mouse moves, change the value
            ### displayed in the widget

            elif event.type == MOUSEMOTION:
                self.change_value_by_mouse_motion(event.pos)

            ### if the left button of the mouse is
            ### released, perform exit setups for the
            ### mouse edition mode and resume editing
            ### the widget's value

            elif event.type == MOUSEBUTTONUP:

                if event.button == 1:

                    self.perform_mouse_edition_exit_setups()
                    self.resume_editing()

            ## if window is resized, set the movement watch
            ## out routine

            elif event.type == WINDOW_RESIZE_EVENT_TYPE:

                self.movement_watch_out_routine = self.watch_out_for_movement

        self.movement_watch_out_routine()

    def change_value_by_mouse_motion(self, mouse_pos):
        """Change current value according to mouse motion.

        That is, the value displayed for the widget is
        incremented/decremented by a value proportional
        to the distance between the mouse position and
        the origin of the mouse dragging movement.

        Parameters
        ==========
        mouse_pos (2-tuple of integers)
            integers represent the position of the mouse
            in the screen.
        """
        ### retrieve the position of the mouse in the x axis
        x_pos, _ = mouse_pos

        ### calculate the distance between the position of
        ### the mouse in x and the position x from where
        ### the dragging movement began
        ###
        ### the amount incremented/decremented from the
        ### value of the widget is proportional to such
        ### distance;
        delta_x_in_pixels = x_pos - self.dragging_origin_x

        ### however, before we use it, we attenuate it
        ### a bit, to compensate for the massive number
        ### of pixels the mouse can suddenly traverse
        attenuated_delta_x = delta_x_in_pixels // MOUSE_ATTENUATION

        ### we finally calculate the increment in the value
        ### of the widget using the distance we just
        ### calculated multiplied by the current increment
        value_increment = attenuated_delta_x * self.increment

        ### the value of the widget is obtained by summing
        ### the base value with the increment
        value = self.base_value + value_increment

        ### however, before using such value, we must
        ### clamp it
        clamped_value = self.clamp_max(self.clamp_min(value))

        ### we then set its text in the widget and update
        ### the image

        self.cursor.set(str(clamped_value))
        self.update_image()

        ### we must execute extra setups depending on
        ### whether the value was actually clamped or not

        ## if the value wasn't clamped, we increment the
        ## position of the mouse dragging origin with the
        ## horizontal distance between the center of the
        ## screen and the mouse position at the beginning
        ## of this method

        if clamped_value == value:
            self.dragging_origin_x += SCREEN_CENTERX - x_pos

        ## otherwise, set the clamped value as the new
        ## base value and reset the mouse dragging origin
        ## to the center of the screen

        else:

            self.base_value = clamped_value
            self.dragging_origin_x = SCREEN_CENTERX

        ### finally center the mouse in the screen
        set_mouse_pos(SCREEN_CENTERX, SCREEN_CENTERY)

    def change_shift_influence(self, shift_pressed):
        """Perform setups according to state of shift key.

        Parameters
        ==========
        shift_pressed (boolean)
            indicates whether the shift key is pressed,
            and thus whether to enable or not the influence
            of the shift button in how the mouse dragging
            affects the incrementation of the value displayed
            in the widget.
        """
        ### define the value of the increment used
        ### to increment/decrement the value displayed
        ### in the widget

        self.increment = (
            self.preciser_drag_increment
            if shift_pressed
            else self.normal_drag_increment
        )

        ### assign the current value displayed as the
        ### base value which will be the target of the
        ### incrementation/decrementation performed
        ### whenever the mouse moves
        self.base_value = self.evaluate_string(self.cursor.get())

        ### set the origin of the mouse dragging movement
        ### to the center of the screen
        self.dragging_origin_x = SCREEN_CENTERX

    def mouse_edition_draw(self):
        """Draw objects in mouse edition mode."""
        ### draw object behind the widget
        self.draw_behind()

        ### draw self.image
        super().draw()

        ### update the screen (pygame.display.update)
        update()

    def enable_standby_mode(self):
        """Assign behaviours for standby mode."""
        self.handle_input = self.standby_control
        self.update = self.update_behind
        self.draw = self.standby_draw

    def enable_keyboard_edition_mode(self):
        """Assign behaviours for keyboard edition mode."""
        self.handle_input = self.keyboard_edition_control
        self.update = self.keyboard_edition_update
        self.draw = self.keyboard_edition_draw

    def enable_mouse_edition_mode(self):
        """Perform setups to enable mouse edition mode."""
        ### assign specific behaviours

        self.update = self.update_behind
        self.draw = self.mouse_edition_draw
        self.handle_input = self.mouse_edition_control

        ### disable the mouse visibility
        set_mouse_visibility(False)

        ### position the mouse at the center of the screen
        set_mouse_pos(SCREEN_CENTERX, SCREEN_CENTERY)

        ### define the influence of the state of the
        ### shift key in how the value displayed is
        ### incremented/decremented;
        ###
        ### this also has the desired side-effects of:
        ###
        ### 1) setting the origin of the mouse dragging
        ###    movement to the center of the screen
        ### 2) setting the current value displayed in the
        ###    widget as the base value which will be
        ###    incremented/decremented whenever the mouse
        ###    moves

        self.change_shift_influence(get_mods_bitmask() & KMOD_SHIFT)

    def perform_mouse_edition_exit_setups(self):
        """Restore mouse settings and clean attributes."""
        set_mouse_pos(self.initial_mouse_pos)
        set_mouse_visibility(True)

        del self.base_value
        del self.initial_mouse_pos
        del self.increment
        del self.dragging_origin_x

    def watch_out_for_movement(self):

        last_reference_pos = self.get_reference_pos()

        if last_reference_pos == self.reference_pos:
            return

        diff = Vector2(last_reference_pos) - self.reference_pos

        self.reference_pos = last_reference_pos

        self.cursor.rect.move_ip(diff)
        self.cursor.line.rect.move_ip(diff)

        if self.get_reference_pos != self.get_topleft:
            self.rect.move_ip(diff)

        ##
        self.draw_on_window_resize()
        self.draw()

        ##
        self.movement_watch_out_routine = empty_function
