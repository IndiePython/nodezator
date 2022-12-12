"""Form to create/return new path from file manager."""

### standard library import
from functools import partialmethod


### third-party imports

from pygame import (
    QUIT,
    KEYDOWN,
    MOUSEBUTTONDOWN,
    MOUSEBUTTONUP,
)

from pygame.event import get as get_events
from pygame.display import update

from pygame.math import Vector2


### local imports

from ...config import APP_REFS

from ...translation import TRANSLATION_HOLDER as t

from ...pygameconstants import (
    SCREEN_RECT,
    FPS,
    maintain_fps,
)

from ...dialog import create_and_show_dialog

from ...ourstdlibs.behaviour import empty_function

from ...ourstdlibs.collections.general import CallList

from ...our3rdlibs.behaviour import watch_window_size

from ...our3rdlibs.button import Button

from ...classes2d.single import Object2D
from ...classes2d.collections import List2D

from ...fontsman.constants import ENC_SANS_BOLD_FONT_HEIGHT
from ...textman.label.main import Label

from ...surfsman.draw import draw_border, draw_depth_finish
from ...surfsman.render import render_rect

from ...loopman.exception import (
    QuitAppException,
    SwitchLoopException,
)

from ...colorsman.colors import (
    BUTTON_FG,
    BUTTON_BG,
    WINDOW_FG,
    WINDOW_BG,
)

from ..surfs import FILE_ICON, FOLDER_ICON


## widget
from ...widget.stringentry import StringEntry


### XXX
### considering how simple this form is, this is a good
### candidate for the new way of generating forms I
### discussed on paper (small notebook 2020-03-12);

### XXX
### maybe putting the path together could be done
### outside the form; ponder;
###
### edit: this may actually have been done already, check;


class PathForm(Object2D):
    """Form to create/return new path from file manager."""

    def __init__(self):
        """Setup form objects."""
        ### build surf and rect for background

        self.image = render_rect(470, 140, WINDOW_BG)
        draw_border(self.image)

        self.rect = self.image.get_rect()

        ### build widgets
        self.build_form_widgets()

        ### assign update behaviour
        self.update = empty_function

        ### center form and append centerin method
        ### as a window resize setup

        self.center_new_path_form()

        APP_REFS.window_resize_setups.append(self.center_new_path_form)

    def center_new_path_form(self):

        diff = Vector2(SCREEN_RECT.center) - self.rect.center

        self.rect.center = SCREEN_RECT.center
        self.widgets.rect.move_ip(diff)

    def build_form_widgets(self):
        """Build widgets which compose the form."""
        ### create special list to hold widgets
        self.widgets = List2D()

        ### define an initial topleft relative to the
        ### topleft corner of the form 'rect'
        topleft = self.rect.move(5, 5).topleft

        ### instantiate a caption for the form

        self.caption_label = Label(
            text=(t.file_manager.new_path_form.caption),
            font_height=ENC_SANS_BOLD_FONT_HEIGHT,
            foreground_color=WINDOW_FG,
            background_color=WINDOW_BG,
            coordinates_name="topleft",
            coordinates_value=topleft,
        )

        self.widgets.append(self.caption_label)

        ### update the topleft to a value a bit below
        ### the bottomleft corner of the widgets already
        ### in the versatile list, and also a bit to the
        ### right
        topleft = self.widgets.rect.move(5, 10).bottomleft

        ### instantiate icon object

        self.icon = Object2D()

        self.icon.image = FILE_ICON
        self.icon.rect = self.icon.image.get_rect()
        self.icon.rect.topleft = topleft

        self.widgets.append(self.icon)

        ### instantiate type name label

        self.type_name_label = Label(
            text=(t.file_manager.new_path_form.type_path_name + ":"),
            font_height=ENC_SANS_BOLD_FONT_HEIGHT,
            foreground_color=WINDOW_FG,
            background_color=WINDOW_BG,
            coordinates_name="midleft",
            coordinates_value=self.icon.rect.midright,
        )

        self.widgets.append(self.type_name_label)

        ### update the topleft to a value a bit below
        ### the bottomleft corner of the widgets already
        ### in the versatile list, and a bit to the right
        topleft = self.widgets.rect.move(5, 5).bottomleft

        ### instantiate path name entry

        self.path_name_entry = StringEntry(
            value="",
            loop_holder=self,
            width=self.rect.width - 20,
            font_height=ENC_SANS_BOLD_FONT_HEIGHT,
            draw_on_window_resize=(
                CallList(
                    [
                        lambda: APP_REFS.fm.draw(),
                        self.draw,
                    ]
                )
            ),
            coordinates_name="topleft",
            coordinates_value=topleft,
        )

        self.widgets.append(self.path_name_entry)

        ### create, position and store form related buttons

        bottomright = self.rect.move(-10, -10).bottomright

        for attr_name, text, mouse_release_action in (
            (
                "create_button",
                t.file_manager.new_path_form.create,
                self.submit_form,
            ),
            ("cancel_button", t.file_manager.new_path_form.cancel, self.cancel_form),
        ):

            ## create button

            button = Button.from_text(
                text=text,
                font_height=ENC_SANS_BOLD_FONT_HEIGHT,
                padding=5,
                foreground_color=BUTTON_FG,
                background_color=BUTTON_BG,
                coordinates_name="bottomright",
                coordinates_value=bottomright,
                command=mouse_release_action,
            )

            ## improve surface style by giving a finish
            ## to convey depth
            draw_depth_finish(button.image)

            ## store in dedicated attribute
            setattr(self, attr_name, button)

            ## update the bottomright for the next button
            bottomright = button.rect.move(-5, 0).bottomleft

        ## also store buttons on the widgets special list

        self.widgets.extend(
            (
                self.create_button,
                self.cancel_button,
            )
        )

    def cancel_form(self):
        """Cancel form edition.

        Works by setting the new_path to None and 'running'
        flag to False.
        """
        self.new_path = None
        self.running = False

    def submit_form(self):
        """Store new path and trigger its submission."""

        ### try retrieve name from entry name and building
        ### path using self.parent as the parent
        try:
            path = self.parent / self.path_name_entry.get()

        except Exception as err:

            ### TODO display a proper error message

            create_and_show_dialog(
                "Something went wrong.",
                level_name="error",
            )

        ### if the pathlib.Path object is successfully built,
        ### set it as the new path
        else:
            self.new_path = path

        ### trigger form exit by setting special flag to
        ### False
        self.running = False

    def get_path(self, parent, is_file):
        """Return new path after user edits form."""
        ### store parent
        self.parent = parent

        ### set icon surface according to whether the path
        ### is meant for a file or folder

        self.icon.image = FILE_ICON if is_file else FOLDER_ICON

        ### set caption and "type name" labels' text
        ### according to whether the path is meant for
        ### a file or folder

        ## caption label

        self.caption_label.set(
            t.file_manager.new_path_form.get_new_file
            if is_file
            else t.file_manager.new_path_form.get_new_folder
        )

        draw_border(self.caption_label.image, color=WINDOW_FG, thickness=2)

        ## type name label

        self.type_name_label.set(
            t.file_manager.new_path_form.type_file_name
            if is_file
            else t.file_manager.new_path_form.type_folder_name
        )

        ### set new path to None
        self.new_path = None

        ### TODO loop_holder attribute in block below and
        ### within "while block" could probably be just
        ### a local variable instead; check;

        ### loop until running attribute is set to False

        self.running = True
        self.loop_holder = self

        while self.running:

            maintain_fps(FPS)

            watch_window_size()

            ### put the handle_input/update/draw method
            ### execution inside a try/except clause
            ### so that the SwitchLoopException
            ### thrown when focusing in and out of some
            ### widgets is caught; also, you don't
            ### need to catch the QuitAppException,
            ### since it is caught in the main loop

            try:

                self.loop_holder.handle_input()
                self.loop_holder.update()
                self.loop_holder.draw()

            except SwitchLoopException as err:

                ## use the loop holder in the err
                ## attribute of same name
                self.loop_holder = err.loop_holder

        ### finally, return the new path
        return self.new_path

    def handle_input(self):
        """Process events from event queue."""
        for event in get_events():

            if event.type == QUIT:
                raise QuitAppException

            elif event.type == MOUSEBUTTONDOWN:

                if event.button == 1:

                    if self.rect.collidepoint(event.pos):
                        self.on_mouse_click(event)

            elif event.type == MOUSEBUTTONUP:

                if event.button == 1:

                    if self.rect.collidepoint(event.pos):
                        self.on_mouse_release(event)

    def mouse_method_on_collision(self, method_name, event):
        """Invoke inner widget if it collides with mouse.

        Parameters
        ==========

        method_name (string)
            name of method to be called on the colliding
            widget.
        event (event object of MOUSEBUTTON[...] type)
            it is required in order to comply with
            mouse interaction protocol used; here we
            use it to retrieve the position of the
            mouse when the first button was released.

            Check pygame.event module documentation on
            pygame website for more info about this event
            object.
        """
        ### retrieve position from attribute in event obj
        mouse_pos = event.pos

        ### search for a colliding obj among the widgets

        for obj in self.widgets:

            if obj.rect.collidepoint(mouse_pos):
                colliding_obj = obj
                break

        else:
            return

        ### if you manage to find a colliding obj, execute
        ### the requested method on it, passing along the
        ### received event

        try:
            method = getattr(colliding_obj, method_name)
        except AttributeError:
            pass
        else:
            method(event)

    on_mouse_click = partialmethod(mouse_method_on_collision, "on_mouse_click")

    on_mouse_release = partialmethod(mouse_method_on_collision, "on_mouse_release")

    def draw(self):
        """Draw itself and widgets.

        Extends Object2D.draw.
        """
        ### draw self (background)
        super().draw()

        ### draw widgets
        self.widgets.draw()

        ### update screen (pygame.display.update)
        update()


get_path = PathForm().get_path
