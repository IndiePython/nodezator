"""Form for setting and triggering session recording."""

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

## widgets

from ...widget.checkbutton import CheckButton

from ...widget.optiontray.main import OptionTray

from ...widget.stringentry import StringEntry


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


DEFAULT_RECORDING_FILENAME = "session.pyl"
DEFAULT_FILENAME_TO_LOAD = f"filename{NATIVE_FILE_EXTENSION}"

TEXT_TO_WINDOW_SIZE = {
    "HD (720p)": (1280, 720),
    "FHD (1080p)": (1920, 1080),
    "2K (1440p)": (2560, 1440),
}

TOGGLE_KEYS = frozenset({KMOD_CAPS, KMOD_NUM})


### class definition

class SessionRecordingForm(Object2D):
    """Form for session recording setting and triggering."""

    def __init__(self):
        """Setup form objects."""
        ### build surf and rect for background

        self.image = render_rect(600, 350, WINDOW_BG)
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

        if self.file_to_load_widgets[0] not in self.widgets:
            self.file_to_load_widgets.rect.move_ip(diff)

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
                    text="Set and start session recording",
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

        ### instantiate widgets for recording title

        ## label

        recording_title_label = Object2D.from_surface(
            surface=render_text(
                text="Recording session title:", **TEXT_SETTINGS
            ),
            coordinates_name="topleft",
            coordinates_value=topleft,
        )

        widgets.append(recording_title_label)

        ## entry

        topleft = recording_title_label.rect.move(0, 5).bottomleft

        self.recording_title_entry = StringEntry(
            loop_holder=self,
            value="Type title of recording here",
            width=500,
            name="recording_title",
            coordinates_name='topleft',
            coordinates_value=topleft,
        )

        widgets.append(self.recording_title_entry)


        ### update the topleft to a value a bit below
        ### the bottomleft corner of the widgets already
        ### in the versatile list
        topleft = widgets.rect.move(0, 20).bottomleft

        ### instantiate widgets for recording filepath

        ## filepath label

        new_file_label = Object2D.from_surface(
            surface=render_text(
                text="Path wherein to save recorded data:", **TEXT_SETTINGS
            ),
            coordinates_name="topleft",
            coordinates_value=topleft,
        )

        widgets.append(new_file_label)

        ## filepath change button

        topleft = new_file_label.rect.move(0, 5).bottomleft

        change_filepath_button = Button.from_text(
            text="Change path",
            command=self.change_recording_filepath,
            coordinates_name="topleft",
            coordinates_value=topleft,
            **BUTTON_SETTINGS,
        )

        draw_depth_finish(change_filepath_button.image)

        widgets.append(change_filepath_button)

        ## chosen filepath label

        midleft = change_filepath_button.rect.move(5, 0).midright

        initial_text = str(Path.home() / DEFAULT_RECORDING_FILENAME)

        self.recording_filepath_label = Label(
            text=initial_text,
            name="recording_path",
            max_width=485,
            ellipsis_at_end=False,
            coordinates_name="midleft",
            coordinates_value=midleft,
            **TEXT_SETTINGS,
        )

        widgets.append(self.recording_filepath_label)

        ### update the topleft to a value a bit below
        ### the bottomleft corner of the widgets already
        ### in the versatile list
        topleft = widgets.rect.move(0, 20).bottomleft

        ### instantiate widgets for filepath to load

        ## label

        load_file_label = Object2D.from_surface(
            render_text(
                f"Should load {NATIVE_FILE_EXTENSION} file?:",
                **TEXT_SETTINGS,
            ),
            coordinates_name="topleft",
            coordinates_value=topleft,
        )

        widgets.append(load_file_label)

        ## checkbutton

        midleft = load_file_label.rect.move(5, 0).midright

        self.load_file_checkbutton = CheckButton(
            value=False,
            name="set_file_to_load",
            command=self.toggle_extra_file_widgets,
            coordinates_name="midleft",
            coordinates_value=midleft,
        )

        widgets.append(self.load_file_checkbutton)

        ### instantiate and store extra widgets for filepath to load

        ## create a special list to hold the references
        self.file_to_load_widgets = file_to_load_widgets = List2D()

        ## "use current" button

        midleft = self.load_file_checkbutton.rect.move(10, 0).midright

        use_current_button = Button.from_text(
            text="Use currently loaded",
            command=self.set_loaded,
            coordinates_name="midleft",
            coordinates_value=midleft,
            **BUTTON_SETTINGS,
        )

        draw_depth_finish(use_current_button.image)

        file_to_load_widgets.append(use_current_button)

        ## filepath change button

        topleft = load_file_label.rect.move(0, 5).bottomleft

        change_filepath_to_load_button = Button.from_text(
            text="Change file to load",
            command=self.change_filepath_to_load,
            coordinates_name="topleft",
            coordinates_value=topleft,
            **BUTTON_SETTINGS,
        )

        draw_depth_finish(change_filepath_to_load_button.image)

        file_to_load_widgets.append(change_filepath_to_load_button)

        ## chosen filepath label

        midleft = change_filepath_to_load_button.rect.move(5, 0).midright

        initial_text = str(Path.home() / DEFAULT_FILENAME_TO_LOAD)

        self.filepath_to_load_label = Label(
            text=initial_text,
            name="path_to_load",
            max_width=445,
            ellipsis_at_end=False,
            coordinates_name="midleft",
            coordinates_value=midleft,
            **TEXT_SETTINGS,
        )

        file_to_load_widgets.append(self.filepath_to_load_label)


        ### update the topleft to a value a bit below
        ### the bottomleft corner of the "file to load widgets"
        topleft = file_to_load_widgets.rect.move(0, 20).bottomleft

        ### instantiate widgets for window size

        window_size_label = Object2D.from_surface(
            render_text("Window size:", **TEXT_SETTINGS),
            coordinates_name="topleft",
            coordinates_value=topleft,
        )

        widgets.append(window_size_label)

        ## extra label for displaying full window size

        midleft = window_size_label.rect.move(5, 0).midright

        self.window_size_label_full = Label(
            text="1280x720",
            name="full_window_size",
            max_width=None,
            ellipsis_at_end=False,
            coordinates_name="midleft",
            coordinates_value=midleft,
            **TEXT_SETTINGS,
        )

        widgets.append(self.window_size_label_full)

        ## option tray for window size

        midleft = self.window_size_label_full.rect.move(20, 0).midright

        value = next(key for key in TEXT_TO_WINDOW_SIZE if '1080p' in key)

        self.window_size_tray = OptionTray(
            value=value,
            options=tuple(TEXT_TO_WINDOW_SIZE.keys()),
            max_width=0,
            name="window_size",
            command=self.update_window_size,
            coordinates_name="midleft",
            coordinates_value=midleft,
        )

        widgets.append(self.window_size_tray)

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
            text="Start recording session",
            command=self.trigger_recording,
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

    def change_filepath(self, path_purpose='recording'):
        """Pick new path and update label using it."""

        if path_purpose == 'recording':

            caption="Select path wherein to save session recording"
            path_name=DEFAULT_RECORDING_FILENAME
            label = self.recording_filepath_label

        else:

            caption=(
                f"Select {NATIVE_FILE_EXTENSION} file to load for the"
                " recording session"
            )
            path_name=DEFAULT_FILENAME_TO_LOAD
            label = self.filepath_to_load_label

        ### pick new path
        paths = select_paths(caption=caption, path_name=path_name)

        ### if paths were given, there can only be one,
        ### it should be used as the new filepath

        if paths:
            label.set(str(paths[0]))

    change_recording_filepath = partialmethod(change_filepath, 'recording')
    change_filepath_to_load = partialmethod(change_filepath, 'to_load')

    def toggle_extra_file_widgets(self):
        """Toggle presence of widgets to pick file to load."""
        widgets = self.widgets
        file_to_load_widgets = self.file_to_load_widgets

        if file_to_load_widgets[0] in widgets:
           for obj in file_to_load_widgets:
                widgets.remove(obj)
        else:
            widgets.extend(file_to_load_widgets)

    def update_window_size(self):
        w, h = TEXT_TO_WINDOW_SIZE[self.window_size_tray.get()]
        self.window_size_label_full.set(f'{w}x{h}')

    def set_loaded(self):

        try:
            current = APP_REFS.source_path

        except AttributeError:

            create_and_show_dialog(
                f"There's no {NATIVE_FILE_EXTENSION} file loaded",
                level_name='info',
            )

        else:
            self.filepath_to_load_label.set(str(current))

    def set_session_recording(self):
        """Present form to set and trigger recording session."""
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
                    self.trigger_recording()

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

    def trigger_recording(self):
        """Treat data and, if valid, trigger session recording."""

        if any_toggle_key_on():

            answer = create_and_show_dialog(

                (
                    "A toggle key is turned on: (Caps Lock, Num Lock or both)."
                    " Unless this is your intention, we recommend turning those keys"
                    " off, since their usage increases the size of the recording data."
                    " It is okay to leave them on if it is your intention, though."
                ),

                buttons=(
                    ("Cancel", False),
                    ("Start recording", True),
                ),

                level_name='info',
            )

            if not answer: return

        ### gather data

        filepath = (
            Path(self.filepath_to_load_label.get())
            if self.load_file_checkbutton.get()
            else None
        )

        data = {
            "recording_title" : self.recording_title_entry.get(),
            "recording_path" : Path(self.recording_filepath_label.get()),
            "recording_size" : TEXT_TO_WINDOW_SIZE[self.window_size_tray.get()],
            "filepath": filepath,
        }

        ### trigger session recording
        raise ResetAppException(mode='record', data=data)

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


## utility function

def any_toggle_key_on():

    bitmask = SERVICES_NS.get_pressed_mod_keys()

    return any(
        toggle_key & bitmask
        for toggle_key in TOGGLE_KEYS
    )


## instantiating class and referencing relevant method
set_session_recording = SessionRecordingForm().set_session_recording
