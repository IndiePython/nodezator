"""Form for setting and triggering demonstration playing."""

### standard library imports
from functools import partial, partialmethod


### third-party imports

from pygame.locals import (

    QUIT,

    TEXTINPUT,
    KEYUP,
    K_ESCAPE,

    K_RETURN,
    K_KP_ENTER,

    KEYDOWN,
    KMOD_CTRL,
    K_UP, K_DOWN, K_LEFT, K_RIGHT,
    K_HOME, K_END,
    K_PAGEUP, K_PAGEDOWN,
    K_DELETE, K_BACKSPACE,

    MOUSEBUTTONDOWN,
    MOUSEBUTTONUP,

)

from pygame.key import (
    start_text_input,
    stop_text_input,
    set_text_input_rect,
)

from pygame.math import Vector2

from pygame.draw import (
    circle as draw_circle,
    line as draw_line,
    rect as draw_rect,
)


### local imports

from ....config import APP_REFS

from ....appinfo import NATIVE_FILE_EXTENSION

from ....pygamesetup import (
    SERVICES_NS, SCREEN_RECT, blit_on_screen, SCREEN,
)

from ....dialog import create_and_show_dialog

from ....fileman.main import select_paths

from ....ourstdlibs.behaviour import empty_function

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
    ResetAppException,
)

from ....colorsman.colors import (
    CONTRAST_LAYER_COLOR,
    GRAPH_BG,
    BUTTON_FG,
    BUTTON_BG,
    WINDOW_FG,
    WINDOW_BG,
)

## widgets

from ....our3rdlibs.searchbox import SearchBox

from ....our3rdlibs.listbox import ListBox

## function for injection
from .filtering import filter_demonstrations

## constants
from .constants import DEMONSTRATIONS


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


### class definition

class DemonstrationSessionForm(Object2D):
    """Form for setting and triggering a demonstration session."""

    ### inject function to use as method
    filter_demonstrations = filter_demonstrations

    ### initialize instance

    def __init__(self):
        """Setup form objects."""
        ### build surf and rect for background

        self.image = render_rect(800, 490, WINDOW_BG)
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

        ### create attributes to keep track of references/values

        ## focused obj
        self.focused_obj = None

        ## last text in search box
        self.last_filter_text = ''

        ### reposition cursor

        sb = self.search_box
        sb.reposition_cursor()

        ### draw magnifying glass

        ### XXX replace drawing below by an icon

        circle_center = Vector2(sb.rect.x - 18, sb.rect.centery) + (0, -2)

        draw_circle(self.image, 'white', circle_center, 8, 2)
        draw_line(self.image, 'white', circle_center + (-6, 4), circle_center + (-14, 12), 4)

        ### assign behaviour
        self.update = self.search_box.update

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
        self.search_box.reposition_cursor()


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
                    text="Choose and start demonstration",
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

        ### instantiate widgets for filtering/selecting
        ### demonstration

        ## label

        filter_select_label = Object2D.from_surface(
            surface=render_text(
                text="Filter/select a demonstration:", **TEXT_SETTINGS
            ),
            coordinates_name="topleft",
            coordinates_value=topleft,
        )

        widgets.append(filter_select_label)

        ## search box

        topleft = filter_select_label.rect.move(0, 5).bottomleft

        sb = self.search_box = SearchBox(
            value='',
            width=705,
            on_input = self.filter_demonstrations,
            coordinates_name='topleft',
            coordinates_value=topleft,
        )

        ## position search box a bit to the right

        sb_x_offset = 35
        sb.rect.x += sb_x_offset

        widgets.append(sb)

        ## create button to clear search box text

        self.clear_button = Button.from_text(
            text="Clear",
            command=partial(sb.set, ''),
            **BUTTON_SETTINGS,
        )

        draw_depth_finish(self.clear_button.image)

        self.clear_button.rect.midleft = sb.rect.move(5, 0).midright

        widgets.append(self.clear_button)


        ## list of available demonstrations

        # the compensate the sb_x_offset
        topleft = sb.rect.move(-sb_x_offset, 10).bottomleft

        # list box
        self.list_box = ListBox(
            items = DEMONSTRATIONS,
            selectable_hint='one',
            no_of_visible_lines=12,
            width=790,
            padding=5,
            coordinates_name = 'topleft',
            coordinates_value = topleft,
        )

        widgets.append(self.list_box)

        ### update the topleft to a value a bit below
        ### the bottomleft corner of the widgets already
        ### in the versatile list
        topleft = widgets.rect.move(0, 20).bottomleft

        ### create and store behaviour for exiting the form
        ### (equivalent to setting the 'running' flag to False)
        self.cancel = partial(setattr, self, "running", False)

        ### create, position and store form related buttons

        ## start button

        start_button = Button.from_text(
            text="Start demonstration",
            command=self.trigger_demonstration,
            **BUTTON_SETTINGS,
        )

        draw_depth_finish(start_button.image)

        start_button.rect.bottomright = self.rect.move(-10, -10).bottomright

        ## cancel button

        cancel_button = Button.from_text(
            text="Cancel",
            command=self.cancel,
            **BUTTON_SETTINGS,
        )

        draw_depth_finish(cancel_button.image)

        cancel_button.rect.midright = start_button.rect.move(-5, 0).midleft

        ## store
        widgets.extend((cancel_button, start_button))

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

    def set_demonstration_session(self):
        """Present form to set and trigger demonstration session."""
        ### exit with a dialog if feature is not ready for usage yet

        if APP_REFS.wip_lock:
            create_and_show_dialog("This feature is a work in progress.")
            return

        ### draw screen sized semi-transparent object, so that screen
        ### behind form appears as if unhighlighted
        blit_on_screen(UNHIGHLIGHT_SURF_MAP[SCREEN_RECT.size], (0, 0))

        ###
        self.search_box.reposition_cursor()

        start_text_input()
        set_text_input_rect(
            self.search_box.rect.move(0, 20)
        )

        self.focused_obj = self.search_box

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

                ## if we leave the inner loop, also exit the outer one
                break

            except SwitchLoopException as err:

                ## use the loop holder in the err
                ## attribute of same name
                self.loop_holder = err.loop_holder

            ### we don't need to catch the QuitAppException,
            ### since it is caught in the main loop


        ### disable text editing events if search box
        ### is focused

        if self.focused_obj is self.search_box:
            stop_text_input()

        ### blit the rect sized semitransparent obj
        ### on the screen so the form appear as if
        ### unhighlighted
        self.rect_size_semitransp_obj.draw()

    def handle_input(self):
        """Process events from event queue."""
        for event in SERVICES_NS.get_events():

            ### QUIT
            if event.type == QUIT:

                ### disable text editing events if search box
                ### is focused

                if self.focused_obj is self.search_box:
                    stop_text_input()

                ###
                raise QuitAppException

            ### if we have text being input, add the text

            elif event.type == TEXTINPUT:
                self.search_box.add_text(event.text)

            ### KEYDOWN

            elif event.type == KEYDOWN:

                if event.key == K_UP:
                    self.list_box.walk(-1)

                elif event.key == K_DOWN:
                    self.list_box.walk(1)

                ### move search box cursor

                elif event.key == K_LEFT:

                    self.search_box.go_left()

                    if self.focused_obj is not self.search_box:

                        start_text_input()
                        set_text_input_rect(
                            self.search_box.rect.move(0, 20)
                        )

                        self.focused_obj = self.search_box

                elif event.key == K_RIGHT:

                    self.search_box.go_right()

                    if self.focused_obj is not self.search_box:

                        start_text_input()
                        set_text_input_rect(
                            self.search_box.rect.move(0, 20)
                        )

                        self.focused_obj = self.search_box

                ###

                elif event.key == K_HOME:

                    if self.focused_obj is self.search_box:
                        self.search_box.go_to_beginning()

                    else:
                        self.list_box.go_to_top()

                elif event.key == K_END:

                    if self.focused_obj is self.search_box:
                        self.search_box.go_to_end()

                    else:
                        self.list_box.go_to_bottom()

                elif event.key == K_PAGEUP:
                    self.list_box.walk(-5)

                elif event.key == K_PAGEDOWN:
                    self.list_box.walk(5)

                ### remove characters

                elif event.key == K_BACKSPACE:

                    if self.focused_obj is not self.search_box:

                        start_text_input()
                        set_text_input_rect(
                            self.search_box.rect.move(0, 20)
                        )

                        self.focused_obj = self.search_box

                    if event.mod & KMOD_CTRL:
                        self.search_box.delete_previous_word()

                    else:
                        self.search_box.delete_previous()

                elif event.key == K_DELETE:

                    if self.focused_obj is not self.search_box:

                        start_text_input()
                        set_text_input_rect(
                            self.search_box.rect.move(0, 20)
                        )

                        self.focused_obj = self.search_box

                    self.search_box.delete_under()

            ### KEYUP

            elif event.type == KEYUP:

                if event.key == K_ESCAPE:
                    self.cancel()

                elif event.key in (K_RETURN, K_KP_ENTER):
                    self.trigger_demonstration()


            ### MOUSEBUTTONDOWN

            elif event.type == MOUSEBUTTONDOWN:

                if event.button == 1:

                    if self.rect.collidepoint(event.pos):
                        self.on_mouse_click(event)

            ### MOUSEBUTTONUP

            elif event.type == MOUSEBUTTONUP:

                ### if mouse button is released within boundaries,
                ### process event with corresponding method

                if self.rect.collidepoint(event.pos):
                    self.on_mouse_release(event)

                ### otherwise, cancel editing form
                else:
                    self.cancel()

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

        ###

        fo = self.focused_obj
        sb = self.search_box
        lb = self.list_box

        if (colliding_obj is self.clear_button) and (fo is not sb):

            start_text_input()
            set_text_input_rect(
                self.search_box.rect.move(0, 20)
            )

            self.focused_obj = sb

        elif (fo is sb) and (colliding_obj is not sb):
            stop_text_input()

            ###
            self.focused_obj = colliding_obj

        elif (fo is not sb) and (colliding_obj is sb):

            start_text_input()
            set_text_input_rect(
                self.search_box.rect.move(0, 20)
            )

            ###
            self.focused_obj = colliding_obj


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

    def trigger_demonstration(self):
        """Treat data and, if valid, trigger demonstration session."""
        selected = self.list_box.get()

        if not selected:

            create_and_show_dialog(
                (
                    "You must first select a demonstration"
                    " in order to play it"
                ),
                level_name='info',
            )

            return

        ### gather data
        data = {"demonstration_name": selected[0]}

        ###
        create_and_show_dialog("Not implemented", level_name='info')
        return
        ###

        ### disable text editing events if search box
        ### is focused

        if self.focused_obj is self.search_box:
            stop_text_input()

        ### trigger demonstration session
        raise ResetAppException(mode='play', data=data)

    def draw(self):
        """Draw itself and widgets.

        Extends Object2D.draw.
        """
        ### draw self (background)
        super().draw()

        ### draw widgets
        self.widgets.call_draw()

        ###
        if self.focused_obj is self.search_box:
            draw_rect(SCREEN, 'yellow', self.search_box.rect.inflate(2, 2), 1)

        ### update screen
        SERVICES_NS.update_screen()


## instantiating class and referencing relevant method
set_demonstration_session = DemonstrationSessionForm().set_demonstration_session
