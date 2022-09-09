"""Facility for about dialog."""

### standard library import
from textwrap import wrap


### third-party imports

from pygame import (
    QUIT,
    KEYUP,
    K_ESCAPE,
    MOUSEBUTTONUP,
    MOUSEMOTION,
)

from pygame.event import get as get_events
from pygame.display import update


### local imports

from .translation import DIALOGS_MAP

from .pygameconstants import SCREEN_RECT, blit_on_screen

from .classes2d.single import Object2D
from .classes2d.collections import List2D

from .loopman.main import LoopHolder

from .surfsman.draw import blit_aligned, draw_border
from .surfsman.render import render_rect
from .surfsman.icon import render_layered_icon

from .textman.cache import CachedTextObject
from .textman.render import render_text

from .fontsman.constants import ENC_SANS_BOLD_FONT_HEIGHT

from .surfsman.cache import UNHIGHLIGHT_SURF_MAP

from .colorsman.colors import (
    CONTRAST_LAYER_COLOR,
    BUTTON_FG,
    BUTTON_BG,
    HOVERED_BUTTON_BG,
    WINDOW_FG,
    WINDOW_BG,
    INFO_OUTLINE,
    INFO_BG,
    INFO_ICON_OUTLINE,
    INFO_ICON_FG,
    WARNING_OUTLINE,
    WARNING_BG,
    WARNING_ICON_OUTLINE,
    WARNING_ICON_FG,
    ERROR_OUTLINE,
    ERROR_BG,
    ERROR_ICON_OUTLINE,
    ERROR_ICON_FG,
    CRITICAL_OUTLINE,
    CRITICAL_BG,
    CRITICAL_ICON_OUTLINE,
    CRITICAL_ICON_FG,
)

# XXX the dialogs could have optional parameters to add
# text or buttons to the dialog on the spot; this would be
# useful to provide additional context to the dialogs and
# should be pretty straightforward to implement;
#
# edit: not sure this is relevant anymore, since it looks
# like this was implemented already; maybe we were talking
# here about the possibility of adding text and buttons to
# dialogs for which the text and buttons were already
# predefined?

# XXX whenever convenient implement changes from this
# module on other packages, since this one is the
# more complete and further developed version;

### constants

NORMAL_TEXT_SETTINGS = {
    "font_height": ENC_SANS_BOLD_FONT_HEIGHT,
    "foreground_color": WINDOW_FG,
    "background_color": WINDOW_BG,
    "padding": 5,
}

NORMAL_BUTTON_SETTINGS = {
    "font_height": ENC_SANS_BOLD_FONT_HEIGHT,
    "foreground_color": BUTTON_FG,
    "background_color": BUTTON_BG,
    "padding": 5,
    "depth_finish_thickness": 1,
}

HOVERED_BUTTON_SETTINGS = {
    "font_height": ENC_SANS_BOLD_FONT_HEIGHT,
    "foreground_color": BUTTON_FG,
    "background_color": HOVERED_BUTTON_BG,
    "padding": 5,
    "depth_finish_thickness": 1,
}


## height for font used
FONT_HEIGHT = ENC_SANS_BOLD_FONT_HEIGHT


## icons

ICON_HEIGHT = 27

ICON_MAP = {
    level_name: render_layered_icon(
        chars=[chr(ordinal) for ordinal in ordinals],
        dimension_name="height",
        dimension_value=ICON_HEIGHT,
        colors=colors,
        background_height=ICON_HEIGHT,
    )
    for level_name, ordinals, colors in (
        (
            "info",
            (167, 63, 64, 168),
            (
                INFO_OUTLINE,
                INFO_ICON_OUTLINE,
                INFO_ICON_FG,
                INFO_BG,
            ),
        ),
        (
            "warning",
            (59, 69, 70, 60),
            (
                WARNING_OUTLINE,
                WARNING_ICON_OUTLINE,
                WARNING_ICON_FG,
                WARNING_BG,
            ),
        ),
        (
            "error",
            (167, 125, 126, 168),
            (
                ERROR_OUTLINE,
                ERROR_ICON_OUTLINE,
                ERROR_ICON_FG,
                ERROR_BG,
            ),
        ),
        (
            "critical",
            (167, 67, 68, 168),
            (
                CRITICAL_OUTLINE,
                CRITICAL_ICON_OUTLINE,
                CRITICAL_ICON_FG,
                CRITICAL_BG,
            ),
        ),
    )
}

ICON_OBJECT = Object2D.from_surface(surface=ICON_MAP["info"])

### class definition


class DialogManager(Object2D, LoopHolder):
    """Prints a message box like in tkinter.

    This class is instantiated only once in the end of the
    module and its main method is aliased to be used
    wherever needed in the entire package.
    """

    def show_dialog_from_key(self, key):
        """Create a dialog with data from dialogs map.

        Parameters
        ==========
        key (string)
            used as a key to retrieve data from the
            dialogs map with which to generate the dialog.
        """
        data = DIALOGS_MAP[key]
        return self.create_and_show_dialog(**data)

    def show_formatted_dialog(self, key, *args):
        """Like show_dialog_from_key(), can format message.

        Parameters
        ==========
        key (string)
            used as a key to retrieve data from the
            dialogs map with which to generate the dialog.
        args (iterable)
            contains arguments to pass to str.format.
        """
        ### note the data must be copied, since it is
        ### edited each time it is retrieved
        data = DIALOGS_MAP[key].copy()

        ### edit message
        data["message"] = data["message"].format(*args)

        ### create dialog
        return self.create_and_show_dialog(**data)

    ### TODO the unhighlight_obj parameter could probably
    ### be much more versatile, think about it; it could
    ### also be renamed;

    def create_and_show_dialog(
        self,
        message,
        buttons=None,
        level_name="info",
        unhighlighter_obj=None,
        ## button layout
        button_pos_from="topright",
        button_pos_to="topleft",
        button_offset_by=(10, 0),
        ## dialog clamping and anchoring
        clamping_rect=None,
        anchor_rect=None,
        dialog_pos_from="center",
        dialog_pos_to="center",
        dialog_offset_by=(0, 0),
        ## flag
        dismissable=False,
    ):
        """Create a dialog with/out buttons.

        Parameters
        ==========
        message (string)
            message to be displayed on top of the dialog
            box.
        level_name (string)
            indicates the level of severity of the dialog
            message; available levels are 'info', 'warning',
            'error' and 'critical'. We don't work with
            messages of level 'debug', since they are not
            relevant for users and thus don't appear in
            dialogs (they must instead be logged elsewhere);
            this level name is used as a key to pick an
            appropriate icon to convey the severity to the
            user.
        buttons (iterable of 2-tuples)
            each 2-tuple represents a button. The first
            value is a string for the button text and the
            second value is an arbitrary value to be
            returned by that button, if clicked.
        unhighlighter_obj (obj with draw method or None)
            object used to unhighlight what's behind the
            dialog box.
        """
        ### store dismissable flag
        self.dismissable = dismissable

        ### ensure screen rect is used if specific rects
        ### are None

        if clamping_rect is None:
            clamping_rect = SCREEN_RECT

        if anchor_rect is None:
            anchor_rect = SCREEN_RECT

        ### create objects and their surfaces/rects

        self.create_message(message)

        self.create_buttons(
            buttons,
            button_pos_from,
            button_pos_to,
            button_offset_by,
        )

        self.create_and_position_dialog(
            level_name,
            clamping_rect,
            anchor_rect,
            dialog_pos_from,
            dialog_pos_to,
            dialog_offset_by,
        )

        self.rect_sized_semitransp_obj = Object2D.from_surface(
            surface=(
                render_rect(
                    *self.rect.size,
                    (*CONTRAST_LAYER_COLOR, 130),
                )
            ),
            coordinates_name="topleft",
            coordinates_value=self.rect.topleft,
        )

        ### store a default value
        self.value = None

        ### blit a semitransparent surface in the canvas
        ### to increase constrast between the dialog
        ### and whatever is behind it (making what's behind
        ### appear unhighlighted)

        ## if an object was received, draw it
        if unhighlighter_obj is not None:
            unhighlighter_obj.draw()

        ## otherwise perform a custom operation to draw
        ## such surface

        else:
            blit_on_screen(UNHIGHLIGHT_SURF_MAP[SCREEN_RECT.size], (0, 0))

        ### draw objects created
        self.draw_once()

        ### loop
        self.loop()

        ### blit semitransparent obj (make the dialog
        ### appear unhighlighted; this is important in
        ### case the portions of the screen showing the
        ### dialog aren't updated by the next object
        ### managing the screen once we leave this
        ### method)
        self.rect_sized_semitransp_obj.draw()

        ### free up memory from text objects and buttons
        self.free_up_memory()

        ### finally return the value picked
        return self.value

    def create_message(self, message_text):
        """Create and position message text object(s).

        Parameters
        ==========

        message_text (string)
            used to generate text surfaces for the
            message.
        """
        ### determine a maximum width in characters for the
        ### text object(s) representing the message.
        max_character_number = 110

        ### wrap the message text into lines of an specific
        ### width in characters
        str_list = wrap(message_text, max_character_number)

        ### generate, position and store text objects

        ## instantiate and store a special list to hold
        ## the objects

        self.message = List2D(
            Object2D.from_surface(
                surface=render_text(text=string, **NORMAL_TEXT_SETTINGS)
            )
            for string in (str_list)
        )

        ### position objects relative to each other

        self.message.rect.snap_rects_ip(
            retrieve_pos_from="bottomleft",
            assign_pos_to="topleft",
        )

    def create_buttons(
        self,
        buttons,
        button_pos_from,
        button_pos_to,
        button_offset_by,
    ):
        """Create buttons for the dialog.

        Parameters
        ==========

        buttons (iterable with 2-tuples or None)
            Each 2-tuple represents a button. The first
            value is a string for the button text and the
            second value is an arbitrary value to be
            returned by that button.
        """
        ### create special list to store button objects
        self.buttons = List2D()

        ### if buttons parameter is None, create a single
        ### "ok" button

        if buttons is None:

            self.buttons.append(
                CachedTextObject(
                    text="Ok",
                    text_settings=(NORMAL_BUTTON_SETTINGS),
                    value=None,
                )
            )

        ### otherwise create a button for each action

        else:

            self.buttons.extend(
                CachedTextObject(
                    text=button_text,
                    text_settings=(NORMAL_BUTTON_SETTINGS),
                    value=button_value,
                )
                for button_text, button_value in buttons
            )

        ### position buttons relative to each other

        ## XXX in the future maybe constrain width of
        ## buttons to that of message by snapping them
        ## intermittenlty (using the corresponding
        ## rectsman.main.RectsManager method)

        self.buttons.rect.snap_rects_ip(
            retrieve_pos_from=button_pos_from,
            assign_pos_to=button_pos_to,
            offset_pos_by=button_offset_by,
        )

    def create_and_position_dialog(
        self,
        level_name,
        clamping_rect,
        anchor_rect,
        dialog_pos_from,
        dialog_pos_to,
        dialog_offset_by,
    ):
        """Create image for dialog and position it."""
        ### assign proper icon surface to icon object
        ICON_OBJECT.image = ICON_MAP[level_name]

        ### position message relative to icon
        self.message.rect.midleft = ICON_OBJECT.rect.move(5, 0).midright

        ### group message and icons in same special list
        a_list = List2D([self.message, ICON_OBJECT])

        ### position buttons relative to special list
        self.buttons.rect.midtop = a_list.rect.move(0, 8).midbottom

        ### append buttons to special list
        a_list.append(self.buttons)

        ### position them relative to the given anchor

        offset_anchor_rect = anchor_rect.move(dialog_offset_by)

        pos = getattr(
            offset_anchor_rect,
            dialog_pos_from,
        )

        setattr(a_list.rect, dialog_pos_to, pos)

        ### obtain inflated copy of their area
        inflated_copy = a_list.rect.inflate(20, 20)

        ### move the objects by the different in position
        ### between the inflated copy and a new clamped
        ### copy, if any

        a_list.rect.move_ip(
            [
                a - b
                for a, b in zip(
                    ## topleft of clamped copy
                    inflated_copy.clamp(clamping_rect).topleft,
                    inflated_copy.topleft,
                )
            ]
        )

        ### generate surf

        self.image = render_rect(*inflated_copy.size, WINDOW_BG)

        draw_border(self.image)

        ### assign inflated copy as the rect
        self.rect = inflated_copy

        ### center it on the list, since it
        ### is clamped
        self.rect.center = a_list.rect.center

    def handle_input(self):
        """Retrieve and handle events."""
        for event in get_events():

            if event.type == QUIT:
                self.quit()

            elif self.dismissable and event.type == KEYUP and event.key == K_ESCAPE:
                self.exit_dialog()

            elif event.type == MOUSEMOTION:
                self.on_mouse_motion(event)

            elif event.type == MOUSEBUTTONUP:

                if event.button == 1:
                    self.on_mouse_release(event)

    def on_mouse_motion(self, event):
        """If button collides, highlight it.

        Parameters
        ==========
        event (pygame.event.Event instance)
            event.type == pygame.MOUSEMOTION;

            represents data about a button the mouse
            pointer moving;

            we use the value of its "pos" attribute which
            represents the position of the mouse to check
            whether a button from the dialog collided with
            the mouse pointer.
        """
        ### retrieve the position of the mouse
        mouse_pos = event.pos

        ### iterate over the dialog buttons, setting
        ### text render settings to hovered if they
        ### collide and to normal if not

        for button in self.buttons:

            button.change_text_settings(
                HOVERED_BUTTON_SETTINGS
                if button.rect.collidepoint(mouse_pos)
                else NORMAL_BUTTON_SETTINGS
            )

        ### finally redraw the buttons
        self.buttons.draw()

    def on_mouse_release(self, event):
        """If button collides, store its value and exit loop.

        Parameters
        ==========
        event (pygame.event.Event instance)
            event.type == pygame.MOUSEBUTTONUP;

            represents data about a button of the mouse
            being released; specifically, the left button,
            since event.button == 1;

            we use the value of its "pos" attribute which
            represents the position of the mouse when the
            mouse button was released to check whether a
            button from the dialog collided with the mouse.
        """
        ### retrieve the position of the mouse
        mouse_pos = event.pos

        ### iterate over the dialog buttons

        for button in self.buttons:

            ### if you find a colliding button, store its
            ### value and trigger the exit of the dialog
            ### loop
            ###
            ### you can also break out of the "for loop" in
            ### such case

            if button.rect.collidepoint(mouse_pos):

                self.value = button.value
                self.exit_loop()

                break

        else:

            if self.dismissable and not self.rect.collidepoint(mouse_pos):
                self.exit_dialog()

    def exit_dialog(self):

        self.value = None
        self.exit_loop()

    def draw_once(self):
        """Draw objects on screen."""
        ### draw the 'image' surface, which works as a
        ### background/body for the dialog
        super().draw()

        ### draw the icon object
        ICON_OBJECT.draw()

        ### draw the text objects representing the
        ### message
        self.message.draw()

        ### draw the buttons
        self.buttons.draw()

    def draw(self):
        """Update screen continuously."""
        ### pygame.display.update
        update()

    def free_up_memory(self):
        """Free memory by clearing collections."""
        self.message.clear()
        self.buttons.clear()


### instantiate dialog manager and reference its relevant
### methods in the module level, so they can be easily
### imported from anywhere else in the package

_ = DialogManager()

create_and_show_dialog = _.create_and_show_dialog
show_dialog_from_key = _.show_dialog_from_key
show_formatted_dialog = _.show_formatted_dialog
