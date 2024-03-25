"""Form for setting and triggering system testing session."""

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
    MOUSEBUTTONDOWN,
    MOUSEBUTTONUP,
)

from pygame.math import Vector2

from pygame.transform import (
    rotate as rotate_surface,
    flip as flip_surface,
)


### local imports

from ..config import APP_REFS

from ..pygamesetup import SERVICES_NS, SCREEN_RECT

from ..ourstdlibs.behaviour import empty_function

from ..our3rdlibs.button import Button

from ..classes2d.single import Object2D
from ..classes2d.collections import List2D

from ..fontsman.constants import (
    ENC_SANS_BOLD_FONT_HEIGHT,
    ENC_SANS_BOLD_FONT_PATH,
)

from ..textman.render import render_text

from ..surfsman.draw import draw_border, draw_depth_finish
from ..surfsman.render import render_rect

from ..loopman.exception import QuitAppException, SwitchLoopException

from ..colorsman.colors import (
    BLACK,
    BUTTON_FG,
    BUTTON_BG,
)


## widget
from ..widget.intfloatentry.main import IntFloatEntry



### constants

REPORT_BG = (235, 235, 250)
REPORT_FG = (28, 28, 28)

TEXT_SETTINGS = {
    "font_height": ENC_SANS_BOLD_FONT_HEIGHT,
    "font_path": ENC_SANS_BOLD_FONT_PATH,
    "padding": 5,
    "foreground_color": REPORT_FG,
    "background_color": REPORT_BG,
}

BUTTON_SETTINGS = {
    "font_height": ENC_SANS_BOLD_FONT_HEIGHT,
    "font_path": ENC_SANS_BOLD_FONT_PATH,
    "padding": 5,
    "foreground_color": BUTTON_FG,
    "background_color": BUTTON_BG,
}


### class definition

class ReportViewer(Object2D):
    """Displays a system testing report."""

    def __init__(self):
        """Setup objects."""
        ### build surf and rect for background

        self.image = render_rect(1070, 650, REPORT_BG)
        self.rect = self.image.get_rect()

        ### store copy for cleaning the image
        self.clean_bg = self.image.copy()

        ### store slightly smaller area for scrolling/safe display
        self.scroll_area = self.rect.inflate(-20, -20)

        ### assign behaviours

        ## update
        self.update = empty_function

        ### special collection to store widgets
        self.widgets = List2D()

        ### build widgets
        self.create_general_widgets()

        ### create placeholder attribute to hold next loop holder
        self.loop_holder = None

        ### center form and also append centering method
        ### as a window resize setup

        self.center_session_recording_form()

        APP_REFS.window_resize_setups.append(
            self.center_session_recording_form
        )

    def center_session_recording_form(self):

        diff = Vector2(SCREEN_RECT.center) - self.rect.center

        ## center rect and scroll area on screen
        self.rect.center = self.scroll_area.center = SCREEN_RECT.center

        ##
        self.widgets.rect.move_ip(diff)

    def create_general_widgets(self):
        """Build general widgets to use/reuse in reports."""
        ### define an initial topleft relative to the
        ### topleft corner of the form 'rect'
        topleft = self.rect.move(10, 10).topleft

        ### instantiate a caption for the form

        self.caption_label = Object2D.from_surface(
            surface=(
                render_text(
                    text="System testing report",
                    **{**TEXT_SETTINGS, 'font_height': 40},
                )
            ),
            coordinates_name="topleft",
            coordinates_value=topleft,
        )

        self.widgets.append(self.caption_label)


        ### create report related buttons

        ## exit button

        bottomright = self.rect.move(-10, -10).bottomright

        self.exit_button = Button.from_text(
            text="Exit report",
            command=self.exit,
            coordinates_name='bottomright',
            coordinates_value=bottomright,
            **BUTTON_SETTINGS,
        )

        draw_depth_finish(self.exit_button.image)


        ## save button

        midright = self.exit_button.rect.move(-10, 0).midleft

        self.save_button = Button.from_text(
            text="Save as html",
            command=self.save_report,
            coordinates_name='midright',
            coordinates_value=midright,
            **BUTTON_SETTINGS,
        )

        draw_depth_finish(self.save_button.image)

        ## store them
        self.widgets.extend((self.save_button, self.exit_button))

    def prepare_report(self, report_data):
        """"""
        ### reference widgets locally
        widgets = self.widgets

        ### clear widgets
        widgets.clear()

        ### reposition and store caption

        self.caption_label.rect.topleft = self.rect.move(10, 10).topleft
        widgets.append(self.caption_label)

        ### create report-related visuals

        topleft = self.caption_label.rect.move(0, 10).bottomleft

        result_label = Object2D.from_surface(
            surface=(
                render_text(
                    text=report_data['overall_result'],
                    **{
                        **TEXT_SETTINGS,
                        'font_height': 40,
                        'foreground_color': (130, 30, 70)
                    },
                )
            ),
            coordinates_name="topleft",
            coordinates_value=topleft,
        )

        widgets.append(result_label)

        ### position and store buttons

        self.exit_button.rect.bottomright = (
            self.rect.right - 10,
            widgets.rect.bottom + 10,
        )

        self.save_button.rect.midright = (
            self.exit_button.rect.move(-10, 0).midleft
        )

        widgets.extend((self.save_button, self.exit_button))

    def handle_input(self):
        """Process events from event queue."""
        for event in SERVICES_NS.get_events():

            ### QUIT
            if event.type == QUIT:
                raise QuitAppException

            ### KEYUP

            elif event.type == KEYUP:

                if event.key == K_ESCAPE:
                    self.exit()

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

                ## otherwise cancel editing form

                else:
                    self.exit()

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
        ### reference image locally
        image = self.image

        ### clean image
        image.blit(self.clean_bg, (0, 0))

        ### draw widgets on self

        ## reference rect locally
        rect = self.rect

        ## draw widgets

        for widget in self.widgets:

            if widget.rect.colliderect(rect):
                widget.draw_relative(self)

        ### draw border
        draw_border(image)

        ### draw self
        super().draw()

        ### update screen
        SERVICES_NS.update_screen()

    def save_report(self):
        ...

    def exit(self):
        """Exit report viewer."""
        raise SwitchLoopException(self.loop_holder)



## create instance of report viewer
report_viewer = ReportViewer()
