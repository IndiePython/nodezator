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

from ...config import APP_REFS

from ...pygamesetup import SERVICES_NS, SCREEN_RECT, blit_on_screen

from ...pygamesetup.constants import FPS

from ...dialog import create_and_show_dialog

from ...ourstdlibs.behaviour import empty_function

from ...our3rdlibs.button import Button

from ...our3rdlibs.listbox import ListBox

from ...classes2d.single import Object2D
from ...classes2d.collections import List2D

from ...fontsman.constants import (
    ENC_SANS_BOLD_FONT_HEIGHT,
    ENC_SANS_BOLD_FONT_PATH,
)

from ...textman.render import render_text

from ...surfsman.draw import draw_border, draw_depth_finish
from ...surfsman.render import render_rect, combine_surfaces
from ...surfsman.icon import render_layered_icon

from ...loopman.exception import (
    QuitAppException,
    SwitchLoopException,
    ResetAppException,
)

from ...colorsman.colors import (
    BLACK,
    BUTTON_FG,
    BUTTON_BG,
)


## widget
from ...widget.intfloatentry.main import IntFloatEntry





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


ARROW_LEFT_ICON = render_layered_icon(
    chars=[chr(ordinal) for ordinal in (50, 51)],
    dimension_name='height',
    dimension_value=19,
    padding=2,
    rotation_degrees=90,
    colors=[
        BLACK,
        (30, 130, 70),
    ],
    background_color=BUTTON_BG,
)

_TRANSP_LEFT_ARROW = render_layered_icon(
    chars=[chr(ordinal) for ordinal in (50, 51)],
    dimension_name='height',
    dimension_value=15,
    padding=0,
    rotation_degrees=90,
    colors=[
        BLACK,
        (30, 130, 70),
    ],
)

ARROW_LEFT_DOUBLE_ICON = ARROW_LEFT_ICON.copy()
ARROW_LEFT_DOUBLE_ICON.fill(BUTTON_BG)

for _topleft in (
    (4, 8),
    (0, 0),
):
    ARROW_LEFT_DOUBLE_ICON.blit(_TRANSP_LEFT_ARROW, _topleft)

ARROW_RIGHT_ICON = rotate_surface(ARROW_LEFT_ICON, 180)
ARROW_RIGHT_DOUBLE_ICON = flip_surface(ARROW_LEFT_DOUBLE_ICON, True, False)


AVAILABLE_TEST_CASE_TITLES = [
    "STC 0000 - Instantiate default objects using the popup menu",
]

MUST_SELECT_FROM_AVAILABLE = (
    "You must select at least one test case from the list"
    " of available ones in order to add the selection to the"
    " list of chosen test cases."
)

NO_MORE_AVAILABLE_ITEMS = "All available cases are already chosen."

MUST_SELECT_FROM_CHOSEN = (
    "You must select at least one test case from the list"
    " of chosen ones in order to remove the selection from it."
)

NO_MORE_CHOSEN_ITEMS = "All chosen cases are already removed."


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
        self.scroll_area = self.rect.inflate(-10, -10)

        ### assign behaviours

        ## update
        self.update = empty_function

        ### build widgets
        self.build_widgets()

        ### center form and also append centering method
        ### as a window resize setup

        self.center_session_recording_form()

        APP_REFS.window_resize_setups.append(self.center_session_recording_form)

    def center_session_recording_form(self):

        diff = Vector2(SCREEN_RECT.center) - self.rect.center

        ## center rect and scroll area on screen
        self.rect.center = self.scroll_area.center = SCREEN_RECT.center

        ##
        self.widgets.rect.move_ip(diff)

    def build_widgets(self):
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
                    text="System testing report",
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

        ## pick tests label

        label_text = (
            "Choose test cases to perform from the list of available ones"
            " by moving them to the list of chosen ones"
        )

        pick_cases_label = Object2D.from_surface(
            surface=render_text(
                text=label_text, **TEXT_SETTINGS
            ),
            coordinates_name="topleft",
            coordinates_value=topleft,
        )

        widgets.append(pick_cases_label)

        ### available tests list box

        ## label

        topleft = pick_cases_label.rect.move(0, 10).bottomleft

        available_cases_label = Object2D.from_surface(
            surface=render_text(
                text="Available test cases", **TEXT_SETTINGS
            ),
            coordinates_name="topleft",
            coordinates_value=topleft,
        )

        widgets.append(available_cases_label)

        ## listbox

        topleft = available_cases_label.rect.move(0, 5).bottomleft

        self.available_cases_listbox = ListBox(
            items = AVAILABLE_TEST_CASE_TITLES,
            selectable_hint='all',
            no_of_visible_lines=15,
            width=520,
            padding=5,
            coordinates_name = 'topleft',
            coordinates_value = topleft,
        )

        widgets.append(self.available_cases_listbox)

        ### chosen tests list box

        ## listbox

        topleft = self.available_cases_listbox.rect.move(20, 0).topright

        self.chosen_cases_listbox = ListBox(
            items = [],
            selectable_hint='all',
            no_of_visible_lines=15,
            width=520,
            padding=5,
            coordinates_name = 'topleft',
            coordinates_value = topleft,
        )

        widgets.append(self.chosen_cases_listbox)

        ## label

        bottomleft = self.chosen_cases_listbox.rect.move(0, -5).topleft

        chosen_cases_label = Object2D.from_surface(
            surface=render_text(
                text="Chosen test cases", **TEXT_SETTINGS
            ),
            coordinates_name="bottomleft",
            coordinates_value=bottomleft,
        )

        widgets.append(chosen_cases_label)


        ### test case selection/deselection buttons

        ## add button

        add_button_text_surf = (
            render_text(
                text="Add selected",
                **BUTTON_SETTINGS,
            )
        )

        add_button_surf = combine_surfaces(
            [ARROW_RIGHT_ICON, add_button_text_surf],
            retrieve_pos_from="midright",
            assign_pos_to="midleft",
            offset_pos_by=(0, 0),
            padding=2,
            background_color=BUTTON_BG,
        )

        draw_depth_finish(add_button_surf)

        topleft = self.available_cases_listbox.rect.move(5, 10).midbottom

        add_button = (

            Button(
                add_button_surf,
                command=self.add_selected,
                coordinates_name='topleft',
                coordinates_value=topleft,
            )

        )

        widgets.append(add_button)

        ## add all button

        add_all_button_text_surf = (
            render_text(
                text="Add all",
                **BUTTON_SETTINGS,
            )
        )

        add_all_button_surf = combine_surfaces(
            [ARROW_RIGHT_DOUBLE_ICON, add_all_button_text_surf],
            retrieve_pos_from="midright",
            assign_pos_to="midleft",
            offset_pos_by=(0, 0),
            padding=2,
            background_color=BUTTON_BG,
        )

        draw_depth_finish(add_all_button_surf)

        topright = self.available_cases_listbox.rect.move(-5, 10).midbottom

        add_all_button = (

            Button(
                add_all_button_surf,
                command=self.add_all,
                coordinates_name='topright',
                coordinates_value=topright,
            )

        )

        widgets.append(add_all_button)

        ## remove button

        remove_button_text_surf = (
            render_text(
                text="Remove selected",
                **BUTTON_SETTINGS,
            )
        )

        remove_button_surf = combine_surfaces(
            [ARROW_LEFT_ICON, remove_button_text_surf],
            retrieve_pos_from="midright",
            assign_pos_to="midleft",
            offset_pos_by=(0, 0),
            padding=2,
            background_color=BUTTON_BG,
        )

        draw_depth_finish(remove_button_surf)

        topright = self.chosen_cases_listbox.rect.move(-5, 10).midbottom

        remove_button = (

            Button(
                remove_button_surf,
                command=self.remove_selected,
                coordinates_name='topright',
                coordinates_value=topright,
            )

        )

        widgets.append(remove_button)

        ## remove all button

        remove_all_button_text_surf = (
            render_text(
                text="Remove all",
                **BUTTON_SETTINGS,
            )
        )

        remove_all_button_surf = combine_surfaces(
            [ARROW_LEFT_DOUBLE_ICON, remove_all_button_text_surf],
            retrieve_pos_from="midright",
            assign_pos_to="midleft",
            offset_pos_by=(0, 0),
            padding=2,
            background_color=BUTTON_BG,
        )

        draw_depth_finish(remove_all_button_surf)

        topleft = self.chosen_cases_listbox.rect.move(5, 10).midbottom

        remove_all_button = (

            Button(
                remove_all_button_surf,
                command=self.remove_all,
                coordinates_name='topleft',
                coordinates_value=topleft,
            )

        )

        widgets.append(remove_all_button)

        ### update the topleft to a value a bit below
        ### the bottomleft corner of the widgets already
        ### in the versatile list
        topleft = widgets.rect.move(0, 20).bottomleft

        ### widgets to select play speed

        ## label

        speed_label = Object2D.from_surface(
            surface=render_text(
                text="Speed (frames/second):", **TEXT_SETTINGS
            ),
            coordinates_name="topleft",
            coordinates_value=topleft,
        )

        widgets.append(speed_label)

        ## entry

        midleft = speed_label.rect.move(10, 0).midright

        self.speed_entry = IntFloatEntry(
            value=0, # max/uncapped
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

        ### create, position and store form related buttons

        ## exit button

        self.exit_button = Button.from_text(
            text="Exit report",
            command=self.exit,
            **BUTTON_SETTINGS,
        )

        draw_depth_finish(self.exit_button.image)

        self.exit_button.rect.bottomright = (
            self.rect.move(-10, -10).bottomright
        )

        ## save button

        self.save_button = Button.from_text(
            text="Save on file",
            command=self.save_report,
            **BUTTON_SETTINGS,
        )

        draw_depth_finish(self.save_button.image)

        self.save_button.rect.midright = (
            self.exit_button.rect.move(-5, 0).midleft
        )

        ## store
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
                    self.cancel()

                elif event.key in (K_RETURN, K_KP_ENTER):
                    self.trigger_system_testing()

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
                widgets.draw_on_surf(image)

        ### draw border
        draw_border(image)

        ### draw self
        super().draw()

        ### update screen
        SERVICES_NS.update_screen()



## create instance of report viewer
report_viewer = ReportViewer()
