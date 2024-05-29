"""Form for setting and triggering session playing."""

### standard library imports

from pathlib import Path

from functools import partial, partialmethod


### third-party imports

from pygame.locals import (
    QUIT,
    KEYUP,
    K_ESCAPE,
    K_RETURN,
    K_KP_ENTER,
    KMOD_CAPS,
    KMOD_NUM,
    MOUSEBUTTONDOWN,
    MOUSEBUTTONUP,
)

from pygame.math import Vector2


### local imports

from ...config import APP_REFS

from ...appinfo import NATIVE_FILE_EXTENSION

from ...pygamesetup import SERVICES_NS, SCREEN_RECT, blit_on_screen

from ...pygamesetup.constants import FPS

from ...dialog import create_and_show_dialog

from ...fileman.main import select_paths

from ...ourstdlibs.behaviour import empty_function

from ...our3rdlibs.button import Button

from ...classes2d.single import Object2D
from ...classes2d.collections import List2D

from ...fontsman.constants import (
    ENC_SANS_BOLD_FONT_HEIGHT,
    ENC_SANS_BOLD_FONT_PATH,
)

from ...textman.render import render_text
from ...textman.label.main import Label

from ...surfsman.cache import UNHIGHLIGHT_SURF_MAP

from ...surfsman.draw import draw_border, draw_depth_finish
from ...surfsman.render import render_rect

from ...loopman.exception import (
    QuitAppException,
    SwitchLoopException,
    ResetAppException,
)

from ...colorsman.colors import (
    CONTRAST_LAYER_COLOR,
    GRAPH_BG,
    BUTTON_FG,
    BUTTON_BG,
    WINDOW_FG,
    WINDOW_BG,
)

## widget
from ...widget.intfloatentry.main import IntFloatEntry


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

HIGHLIGHTED_SPEED_BUTTON_SETTINGS = {
    "font_height": ENC_SANS_BOLD_FONT_HEIGHT,
    "font_path": ENC_SANS_BOLD_FONT_PATH,
    "padding": 5,
    "depth_finish_thickness": 1,
    "foreground_color": BUTTON_FG,
    "background_color": (30, 130, 90),
}

SPEED_TO_BUTTON = {}
SPEED_BUTTON_SURF_MAP = {}



### class definition

class SessionPlayingForm(Object2D):
    """Form for session recording setting and triggering."""

    def __init__(self):
        """Setup form objects."""
        ### build surf and rect for background

        self.image = render_rect(600, 220, WINDOW_BG)
        draw_border(self.image)

        self.rect = self.image.get_rect()

        ### store a semitransparent object

        self.rect_size_semitransp_obj = Object2D.from_surface(
            surface=(render_rect(*self.rect.size, (*CONTRAST_LAYER_COLOR, 130))),
            coordinates_name="center",
            coordinates_value=SCREEN_RECT.center,
        )

        ### build widgets
        self.build_form_widgets()

        ### assign behaviour
        self.update = empty_function

        ### center form and also append centering method
        ### as a window resize setup

        self.center_session_recording_form()

        APP_REFS.window_resize_setups.append(self.center_session_recording_form)

    def center_session_recording_form(self):

        diff = Vector2(SCREEN_RECT.center) - self.rect.center

        ## center rect on screen
        self.rect.center = SCREEN_RECT.center

        ##
        self.widgets.rect.move_ip(diff)

    def build_form_widgets(self):
        """Build widgets to hold settings for edition."""
        ### create special list to hold widgets
        widgets = self.widgets = List2D()

        ### define an initial topleft relative to the
        ### topleft corner of the form 'rect'
        topleft = self.rect.move(5, 5).topleft

        ### instantiate a caption for the form

        caption_label = Object2D.from_surface(
            surface=(
                render_text(
                    text="Set and start session playing",
                    border_thickness=2,
                    border_color=(TEXT_SETTINGS["foreground_color"]),
                    **TEXT_SETTINGS,
                )
            ),
            coordinates_name="topleft",
            coordinates_value=topleft,
        )

        widgets.append(caption_label)

        ### update the topleft to a value a bit below
        ### the bottomleft corner of the widgets already
        ### in the versatile list
        topleft = widgets.rect.move(0, 20).bottomleft

        ### instantiate widgets for filepath to play

        ## filepath label

        new_file_label = Object2D.from_surface(
            surface=render_text(
                text="File with input data to play:", **TEXT_SETTINGS
            ),
            coordinates_name="topleft",
            coordinates_value=topleft,
        )

        widgets.append(new_file_label)

        ## filepath change button

        topleft = new_file_label.rect.move(0, 5).bottomleft

        change_filepath_button = Button.from_text(
            text="Change path",
            command=self.change_filepath,
            coordinates_name="topleft",
            coordinates_value=topleft,
            **BUTTON_SETTINGS,
        )

        draw_depth_finish(change_filepath_button.image)

        widgets.append(change_filepath_button)

        ## chosen filepath label

        midleft = change_filepath_button.rect.move(5, 0).midright

        self.filepath_label = Label(
            text="(no path selected)",
            name="input_data_path",
            max_width=485,
            ellipsis_at_end=False,
            coordinates_name="midleft",
            coordinates_value=midleft,
            **TEXT_SETTINGS,
        )

        widgets.append(self.filepath_label)

        ### update the topleft to a value a bit below
        ### the bottomleft corner of the widgets already
        ### in the versatile list
        topleft = widgets.rect.move(0, 20).bottomleft

        ### instantiate widgets for playback speed

        speed_label = Object2D.from_surface(
            render_text("Speed (frames/second):", **TEXT_SETTINGS),
            coordinates_name="topleft",
            coordinates_value=topleft,
        )

        widgets.append(speed_label)

        ## entry to pick speed

        midleft = speed_label.rect.move(5, 0).midright

        self.speed_entry = IntFloatEntry(
            value=FPS,
            min_value = 0,
            numeric_classes_hint='int_float',
            loop_holder=self,
            command=self.check_speed_button_surfs,
            width=100,
            coordinates_name="midleft",
            coordinates_value=midleft,
        )

        widgets.append(self.speed_entry)

        ## extra buttons for speed

        midleft = self.speed_entry.rect.move(10, 0).midright

        set_speed = self.speed_entry.set

        for text, speed in (
            ("0.25x", FPS//4),
            ("0.5x", FPS//2),
            ("1x", FPS),
            ("2x", FPS*2),
            ("4x", FPS*4),
            ("max/uncapped", 0),
        ):

            speed_button = Button.from_text(
                text=text,
                command=partial(set_speed, speed),
                coordinates_name="midleft",
                coordinates_value=midleft,
                **BUTTON_SETTINGS,
            )

            highlighted_surf = (
                render_text(
                    text=text,
                    **HIGHLIGHTED_SPEED_BUTTON_SETTINGS,
                )
            )

            SPEED_TO_BUTTON[speed] = speed_button

            SPEED_BUTTON_SURF_MAP[speed_button] = (
                speed_button.image, highlighted_surf
            )

            midleft = speed_button.rect.midright

            draw_depth_finish(speed_button.image)

            widgets.append(speed_button)

        ### update speed button surfs
        self.check_speed_button_surfs()

        ### update the topleft to a value a bit below
        ### the bottomleft corner of the widgets already
        ### in the versatile list
        topleft = widgets.rect.move(0, 20).bottomleft

        ### create and store behaviour for exiting the form
        ### (equivalent to setting the 'running' flag to False)
        self.cancel = partial(setattr, self, "running", False)

        ### create, position and store form related buttons

        ## start button

        self.start_button = Button.from_text(
            text="Start playing session",
            command=self.trigger_playing,
            **BUTTON_SETTINGS,
        )

        draw_depth_finish(self.start_button.image)

        self.start_button.rect.bottomright = self.rect.move(-10, -10).bottomright

        ## cancel button

        self.cancel_button = Button.from_text(
            text="Cancel",
            command=self.cancel,
            **BUTTON_SETTINGS,
        )

        draw_depth_finish(self.cancel_button.image)

        self.cancel_button.rect.midright = self.start_button.rect.move(-5, 0).midleft

        ## store
        widgets.extend((self.cancel_button, self.start_button))

    def change_filepath(self):
        """Pick new path and update label using it."""
        ### pick new path
        paths = select_paths(caption="Select session data file to play")

        ### if paths were given, there can only be one,
        ### it should be used as the new filepath

        if paths:
            self.filepath_label.set(str(paths[0]))

    def check_speed_button_surfs(self):
        """Highlight/unhighlighted speed button surfaces.

        If the current speed correspond to the speed set by
        an specific button, that button is highlighted, otherwise
        it is unhighlighted.
        """
        ### get current speed
        current_speed = self.speed_entry.get()

        ### reassign surfaces to each button, depending on whether
        ### their respective speed matches the current one

        for speed, button in SPEED_TO_BUTTON.items():

            index = 1 if current_speed == speed else 0
            button.image = SPEED_BUTTON_SURF_MAP[button][index]

    def set_session_playing(self):
        """Present form to set and trigger playing session."""
        ### exit with a dialog if feature is not ready for usage yet

        if APP_REFS.wip_lock:

            create_and_show_dialog(
                "This feature is a work in progress.",
                level_name='info',
            )

            return

        ### draw screen sized semi-transparent object,
        ### so that screen behind form appears as if
        ### unhighlighted
        blit_on_screen(UNHIGHLIGHT_SURF_MAP[SCREEN_RECT.size], (0, 0))

        ### loop until running attribute is set to False

        self.running = True
        self.loop_holder = self

        while True:

            try:

                while self.running:

                    ### perform various checkups for this frame;
                    ###
                    ### stuff like maintaing a constant framerate and more
                    SERVICES_NS.frame_checkups()

                    ### execute the handle_input/update/draw methods
                    ###
                    ### the SwitchLoopException thrown when focusing in and
                    ### out of some widgets is caught in the try clause;

                    self.loop_holder.handle_input()
                    self.loop_holder.update()
                    self.loop_holder.draw()

                ## if we leave the inner loop, also leave the outer one
                break

            except SwitchLoopException as err:

                ## use the loop holder in the err
                ## attribute of same name
                self.loop_holder = err.loop_holder

            ### we don't need to catch the QuitAppException,
            ### since it is caught in the main loop


        ### blit the rect sized semitransparent obj
        ### on the screen so the form appear as if
        ### unhighlighted
        self.rect_size_semitransp_obj.draw()


    def handle_input(self):
        """Process events from event queue."""
        for event in SERVICES_NS.get_events():

            ### QUIT
            if event.type == QUIT:
                raise QuitAppException

            ### KEYUP

            elif event.type == KEYUP:

                if event.key == K_ESCAPE:
                    self.cancel()

                elif event.key in (K_RETURN, K_KP_ENTER):
                    self.trigger_playing()

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

    def trigger_playing(self):
        """Treat data and, if valid, trigger session recording."""
        label_text = self.filepath_label.get()

        if label_text == '(no path selected)':

            create_and_show_dialog(
                "Must select file with input data to start playing",
                level_name='info',
            )

            return

        ### gather data

        data = {
            "input_data_path" : Path(self.filepath_label.get()),
            "playback_speed" : self.speed_entry.get(),
        }

        ### trigger session recording
        raise ResetAppException(mode='play', data=data)

    def draw(self):
        """Draw itself and widgets.

        Extends Object2D.draw.
        """
        ### draw self (background)
        super().draw()

        ### draw widgets
        self.widgets.draw()

        ### update screen
        SERVICES_NS.update_screen()


## instantiating class and referencing relevant method
set_session_playing = SessionPlayingForm().set_session_playing
