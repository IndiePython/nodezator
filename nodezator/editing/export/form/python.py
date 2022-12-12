"""Form for new file creation."""

### standard library imports

from pathlib import Path
from functools import partial, partialmethod


### third-paraty imports

from pygame import (
    QUIT,
    KEYUP,
    K_ESCAPE,
    K_RETURN,
    K_KP_ENTER,
    MOUSEBUTTONDOWN,
    MOUSEBUTTONUP,
)

from pygame.event import get as get_events

from pygame.display import update

from pygame.math import Vector2


### local imports

from ....config import APP_REFS

from ....translation import TRANSLATION_HOLDER as t

from ....pygameconstants import (
    SCREEN_RECT,
    FPS,
    maintain_fps,
    blit_on_screen,
)


from ....dialog import create_and_show_dialog

from ....fileman.main import select_paths

from ....ourstdlibs.behaviour import empty_function

from ....ourstdlibs.collections.general import CallList

from ....our3rdlibs.behaviour import watch_window_size

from ....our3rdlibs.button import Button

from ....classes2d.single import Object2D
from ....classes2d.collections import List2D

from ....fontsman.constants import (
    ENC_SANS_BOLD_FONT_HEIGHT,
    ENC_SANS_BOLD_FONT_PATH,
)

from ....textman.render import render_text
from ....textman.label.main import Label

from ....surfsman.cache import UNHIGHLIGHT_SURF_MAP

from ....surfsman.draw import draw_border, draw_depth_finish
from ....surfsman.render import render_rect

from ....loopman.exception import (
    QuitAppException,
    SwitchLoopException,
)

from ....our3rdlibs.iterablewidget.list import ListWidget

from ....widget.stringentry import StringEntry

from ....colorsman.colors import (
    CONTRAST_LAYER_COLOR,
    BUTTON_FG,
    BUTTON_BG,
    WINDOW_FG,
    WINDOW_BG,
)


### constants

TEXT_SETTINGS = {
    "font_height": ENC_SANS_BOLD_FONT_HEIGHT,
    "font_path": ENC_SANS_BOLD_FONT_PATH,
    "padding": 5,
    "foreground_color": WINDOW_FG,
    "background_color": WINDOW_BG,
}

BUTTON_SETTINGS = {
    "font_height": ENC_SANS_BOLD_FONT_HEIGHT,
    "font_path": ENC_SANS_BOLD_FONT_PATH,
    "padding": 5,
    "depth_finish_thickness": 1,
    "foreground_color": BUTTON_FG,
    "background_color": BUTTON_BG,
}

DEFAULT_FILENAME = (t.editing.python_export_form.default_filename) + ".py"

NEW_PYTHON_FILEPATH_CAPTION = (t.editing.python_export_form.pick_new_path) + " (.py)"

### class definition


class PythonExportForm(Object2D):
    """Form for python export settings edition."""

    def __init__(self):
        """Setup form objects."""
        ### build surf and rect for background

        self.image = render_rect(540, 270, WINDOW_BG)
        draw_border(self.image)

        self.rect = self.image.get_rect()

        ### store a semitransparent object

        self.rect_size_semitransp_obj = Object2D.from_surface(
            surface=render_rect(*self.rect.size, (*CONTRAST_LAYER_COLOR, 130)),
            coordinates_name="center",
            coordinates_value=SCREEN_RECT.center,
        )

        ### build widgets
        self.build_form_widgets()

        ### assign behaviour
        self.update = empty_function

        ### center form and also append centering method
        ### as a window resize setup

        self.center_python_export_form()

        APP_REFS.window_resize_setups.append(self.center_python_export_form)

    def center_python_export_form(self):

        diff = Vector2(SCREEN_RECT.center) - self.rect.center

        ## center rect on screen
        self.rect.center = SCREEN_RECT.center

        ##
        self.widgets.rect.move_ip(diff)

    def build_form_widgets(self):
        """Build widgets to hold settings for edition."""
        ### create list to hold widgets
        self.widgets = List2D()

        ### define an initial topleft relative to the
        ### topleft corner of the form 'rect'
        topleft = self.rect.move(5, 5).topleft

        ### instantiate a caption for the form

        caption_label = Object2D.from_surface(
            surface=render_text(
                text=(t.editing.python_export_form.caption),
                border_thickness=2,
                border_color=(TEXT_SETTINGS["foreground_color"]),
                **TEXT_SETTINGS,
            ),
            coordinates_name="topleft",
            coordinates_value=topleft,
        )

        self.widgets.append(caption_label)

        ### update the topleft to a value a bit below
        ### the bottomleft corner of the widgets already
        ### in the versatile list
        topleft = self.widgets.rect.move(0, 20).bottomleft

        ### instantiate widgets for filepath

        ## filepath label

        new_file_label = Object2D.from_surface(
            surface=render_text(
                text=(t.editing.python_export_form.new_python_file) + ":",
                **TEXT_SETTINGS,
            ),
            coordinates_name="topleft",
            coordinates_value=topleft,
        )

        self.widgets.append(new_file_label)

        ## filepath change button

        midleft = new_file_label.rect.move(5, 0).midright

        change_filepath_button = Button.from_text(
            text=(t.editing.python_export_form.change),
            command=self.change_filepath,
            coordinates_name="midleft",
            coordinates_value=midleft,
            **BUTTON_SETTINGS,
        )

        draw_depth_finish(change_filepath_button.image)

        self.widgets.append(change_filepath_button)

        ## chosen filepath label

        midleft = change_filepath_button.rect.move(5, 0).midright

        initial_text = str(Path.home() / DEFAULT_FILENAME)

        self.chosen_filepath_label = Label(
            text=initial_text,
            name="python_file_path",
            max_width=325,
            ellipsis_at_end=False,
            coordinates_name="midleft",
            coordinates_value=midleft,
            **TEXT_SETTINGS,
        )

        self.widgets.append(self.chosen_filepath_label)

        ### update the topleft to a value a bit below
        ### the bottomleft corner of the widgets already
        ### in the versatile list
        topleft = self.widgets.rect.move(0, 20).bottomleft

        ### instantiate widgets for additional levels
        ### in the folder structure

        ## additional levels label

        additional_levels_label = Object2D.from_surface(
            surface=render_text(
                text=(t.editing.python_export_form.additional_levels), **TEXT_SETTINGS
            ),
            coordinates_name="topleft",
            coordinates_value=topleft,
        )

        self.widgets.append(additional_levels_label)

        ## additional levels list widget

        topleft = additional_levels_label.rect.move(5, 10).bottomleft

        widget_factory = partial(
            StringEntry,
            loop_holder=self,
            draw_on_window_resize=self.draw,
            width=330,
            name="additional_level",
        )

        default_factory = ".".__str__

        levels_list_widget = ListWidget(
            name="additional_levels",
            value=(),
            widget_factory=widget_factory,
            default_factory=default_factory,
            coordinates_name="topleft",
            coordinates_value=topleft,
        )

        self.widgets.append(levels_list_widget)

        ### create and store behaviour for exiting the form
        ### (equivalent to setting the form data to None
        ### and the 'running' flag to False)

        self.cancel = CallList(
            (
                partial(setattr, self, "form_data", None),
                partial(setattr, self, "running", False),
            )
        )

        ### create, position and store form related buttons

        ## submit button

        self.submit_button = Button.from_text(
            text=(t.editing.python_export_form.submit),
            command=self.submit_form,
            **BUTTON_SETTINGS,
        )

        draw_depth_finish(self.submit_button.image)

        self.submit_button.rect.bottomright = self.rect.move(-10, -10).bottomright

        ## cancel button

        self.cancel_button = Button.from_text(
            text=(t.editing.python_export_form.cancel),
            command=self.cancel,
            **BUTTON_SETTINGS,
        )

        draw_depth_finish(self.cancel_button.image)

        self.cancel_button.rect.midright = self.submit_button.rect.move(-5, 0).midleft

        ## store

        self.widgets.extend((self.cancel_button, self.submit_button))

    def change_filepath(self):
        """Pick new path and update label using it."""
        ### pick new path

        paths = select_paths(
            caption=NEW_PYTHON_FILEPATH_CAPTION,
            path_name=DEFAULT_FILENAME,
        )

        ### act according to whether paths were given

        ## if paths were given, there can only be one,
        ## it should be used as the new filepath

        if paths:
            new_filepath = paths[0]

        ## if no path is given, we return earlier, since
        ## it means the user cancelled setting a new
        ## path
        else:
            return

        ### if the extension is not allowed, notify the
        ### user and cancel the operation by returning

        if new_filepath.suffix.lower() != ".py":

            create_and_show_dialog("File extension must be '.py'")

            return

        ### finally update the label using the given value
        ### as a string
        self.chosen_filepath_label.set(str(new_filepath))

    def get_python_exporting_settings(self):
        """Return settings to export a python file."""
        ### set form data to None
        self.form_data = None

        ### draw screen sized semi-transparent object,
        ### so that screen behind form appears as if
        ### unhighlighted

        blit_on_screen(UNHIGHLIGHT_SURF_MAP[SCREEN_RECT.size], (0, 0))

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

        ### blit the rect sized semitransparent obj
        ### on the screen so the form appear as if
        ### unhighlighted
        self.rect_size_semitransp_obj.draw()

        ### finally, return the form data
        return self.form_data

    def handle_input(self):
        """Process events from event queue."""
        for event in get_events():

            ### QUIT
            if event.type == QUIT:
                raise QuitAppException

            ### KEYUP

            elif event.type == KEYUP:

                if event.key == K_ESCAPE:
                    self.cancel()

                elif event.key in (K_RETURN, K_KP_ENTER):
                    self.submit_form()

            ### MOUSEBUTTONDOWN

            elif event.type == MOUSEBUTTONDOWN:

                if event.button == 1:

                    if self.rect.collidepoint(event.pos):
                        self.on_mouse_click(event)

            ### MOUSEBUTTONUP

            elif event.type == MOUSEBUTTONUP:

                if event.button == 1:

                    if self.rect.collidepoint(event.pos):
                        self.on_mouse_release(event)

                    ## cancel editing form if mouse left
                    ## button is released out of boundaries
                    else:
                        self.cancel()

    # XXX in the future, maybe a "Reset" button would be
    # nice

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

    def submit_form(self):
        """Treat data and, if valid, setup form to exit."""
        ### instantiate form_data dict and reference it
        ### in local variable
        data = self.form_data = {}

        ### populate dict

        for widget in self.widgets:

            try:
                method = widget.get
            except AttributeError:
                continue
            else:
                value = method()

            data[widget.name] = value

        ### trigger the exit of the form by setting
        ### special flag to False
        self.running = False

    def draw(self):
        """Draw itself and widgets.

        Extends Object2D.draw.
        """
        ### draw self (background)
        super().draw()

        ### draw widgets
        for widget in self.widgets:
            widget.draw()

        ### update screen (pygame.display.update)
        update()


get_python_exporting_settings = PythonExportForm().get_python_exporting_settings
