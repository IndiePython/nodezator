"""Form for setting and triggering session playing."""

### standard library imports
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

from ..config import APP_REFS

from ..pygamesetup import SERVICES_NS, SCREEN_RECT, blit_on_screen

from ..pygamesetup.constants import FPS

from ..ourstdlibs.behaviour import empty_function

from ..our3rdlibs.button import Button

from ..classes2d.single import Object2D
from ..classes2d.collections import List2D

from ..fontsman.constants import (
    ENC_SANS_BOLD_FONT_HEIGHT,
    ENC_SANS_BOLD_FONT_PATH,
)

from ..textman.render import render_text

from ..textman.label.main import Label

from ..surfsman.cache import UNHIGHLIGHT_SURF_MAP

from ..surfsman.draw import draw_border
from ..surfsman.render import render_rect

from ..loopman.exception import (
    QuitAppException,
    SwitchLoopException,
)

from ..colorsman.colors import (
    CONTRAST_LAYER_COLOR,
    WINDOW_FG,
    WINDOW_BG,
    BUTTON_FG,
    BUTTON_BG,
)

## widget
from ..widget.intfloatentry.main import IntFloatEntry



### constants

TEXT_SETTINGS = {
    "font_height": ENC_SANS_BOLD_FONT_HEIGHT,
    "font_path": ENC_SANS_BOLD_FONT_PATH,
    "padding": 5,
    "foreground_color": WINDOW_FG,
    "background_color": WINDOW_BG,
}

ERROR_TEXT_SETTINGS = {
    "font_height": ENC_SANS_BOLD_FONT_HEIGHT,
    "font_path": ENC_SANS_BOLD_FONT_PATH,
    "padding": 5,
    "foreground_color": (235, 80, 80),
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

_SECS_TO_REMOVE_ERROR_LABEL = 2

_FRAMES_TO_REMOVE_ERROR_LABEL = (1,) * round(FPS * _SECS_TO_REMOVE_ERROR_LABEL)

ERROR_LABEL_FRAME_COUNTDOWN = []


### class definition

class JumpToNodeForm(Object2D):
    """Form for jumping to node by providing its id."""

    def __init__(self):
        """Setup form objects."""
        ### build surf and rect for background

        self.image = render_rect(300, 120, WINDOW_BG)
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
                    text="Type id to move to respective node",
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

        ### instantiate widgets for picking node id

        ## node id label

        node_id_label = Object2D.from_surface(
            surface=render_text(
                text="Node id:", **TEXT_SETTINGS
            ),
            coordinates_name="topleft",
            coordinates_value=topleft,
        )

        widgets.append(node_id_label)

        ## id intfloat entry

        midleft = node_id_label.rect.move(5, 0).midright

        self.id_entry = IntFloatEntry(
            value=0,
            min_value = 0,
            numeric_classes_hint='int',
            loop_holder=self,
            command=self.check_id_and_jump,
            width=100,
            coordinates_name='midleft',
            coordinates_value=midleft,
        )

        widgets.append(self.id_entry)

        ## go button

        midleft = self.id_entry.rect.move(5, 0).midright

        go_button = Button.from_text(
            text="Go to node",
            command=self.check_id_and_jump,
            coordinates_name='midleft',
            coordinates_value=midleft,
            **BUTTON_SETTINGS,
        )

        widgets.append(go_button)

        ## error label

        topleft = node_id_label.rect.move(0, 5).bottomleft

        self.error_label = Label(
            text='',
            coordinates_name='topleft',
            coordinates_value=topleft,
            **ERROR_TEXT_SETTINGS,
        )

        widgets.append(self.error_label)

        ### create and store behaviour for exiting the form
        ### (equivalent to setting the 'running' flag to False)
        self.leave = partial(setattr, self, "running", False)

    def check_id_and_jump(self):

        ### obtain id
        node_id = self.id_entry.get()

        ### check whether id exists;

        try:
            node = APP_REFS.gm.node_map[node_id]

        ### if it doesn't notify user via special temporary error label
        ### and leave method by returning earlier

        except KeyError:

            self.error_label.set(f"Node of id {node_id} doesn't exist!")

            ERROR_LABEL_FRAME_COUNTDOWN.clear()
            ERROR_LABEL_FRAME_COUNTDOWN.extend(_FRAMES_TO_REMOVE_ERROR_LABEL)

            self.update = self.update_error_label_countdown

            return

        ### otherwise, we'll perform operations to move canvas to requested
        ### node and leave this form

        ea = APP_REFS.ea

        ea.deselect_all()

        ea.add_obj_to_selection(node)

        ea.scroll(
            *(Vector2(SCREEN_RECT.center) - node.rect.center)
        )

        self.leave()


    def present_jump_to_node_form(self):
        """Present form for jumping to node by providing its id."""
        ### draw screen sized semi-transparent object,
        ### so that screen behind form appears as if
        ### unhighlighted
        blit_on_screen(UNHIGHLIGHT_SURF_MAP[SCREEN_RECT.size], (0, 0))

        ### reset update operation
        self.update = empty_function

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
                    ### out of some widgets is caught by the try clause;

                    self.loop_holder.handle_input()
                    self.loop_holder.update()
                    self.loop_holder.draw()

                ## if we leave the inner loop, also leave the outer loop
                break

            except SwitchLoopException as err:

                ## use the loop holder in the err
                ## attribute of same name
                self.loop_holder = err.loop_holder


            ### we don't need to catch QuitAppException,
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
                    self.leave()

                elif event.key in (K_RETURN, K_KP_ENTER):
                    self.check_id_and_jump()

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

                    ## leave form if mouse left button is released
                    ## out of boundaries
                    else:
                        self.leave()

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

    def update_error_label_countdown(self):

        if ERROR_LABEL_FRAME_COUNTDOWN:
            ERROR_LABEL_FRAME_COUNTDOWN.pop()

        else:

            self.error_label.set('')
            self.update = empty_function

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
present_jump_to_node_form = JumpToNodeForm().present_jump_to_node_form
