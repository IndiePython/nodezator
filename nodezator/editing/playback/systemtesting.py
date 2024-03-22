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

from ...surfsman.cache import UNHIGHLIGHT_SURF_MAP
from ...surfsman.draw import draw_border, draw_depth_finish
from ...surfsman.render import render_rect, combine_surfaces
from ...surfsman.icon import render_layered_icon

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

from ...colorsman.colors import BLACK


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
    "foreground_color": BUTTON_FG,
    "background_color": BUTTON_BG,
}


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

class SystemTestingSessionForm(Object2D):
    """Form for system testing session setting and triggering."""

    def __init__(self):
        """Setup form objects."""
        ### build surf and rect for background

        self.image = render_rect(1070, 650, WINDOW_BG)
        draw_border(self.image)

        self.rect = self.image.get_rect()

        ### store a semitransparent object

        self.rect_size_semitransp_obj = Object2D.from_surface(
            surface=(render_rect(*self.rect.size, (*CONTRAST_LAYER_COLOR, 130))),
            coordinates_name="center",
            coordinates_value=SCREEN_RECT.center,
        )

        ### assign behaviours

        ## update
        self.update = empty_function

        ### behaviour for exiting the form
        ### (equivalent to setting the 'running' flag to False)
        self.cancel = partial(setattr, self, 'running', False)

        ### build widgets
        self.build_form_widgets()

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
                    text="Set and start system testing session",
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

        ### update the topleft to a value a bit below
        ### the bottomleft corner of the widgets already
        ### in the versatile list
        topleft = widgets.rect.move(0, 20).bottomleft

        ### available tests list box

        ## label

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

        ### create, position and store form related buttons

        ## start button

        self.start_button = Button.from_text(
            text="Start system testing session",
            command=self.trigger_system_testing,
            **BUTTON_SETTINGS,
        )

        draw_depth_finish(self.start_button.image)

        self.start_button.rect.bottomright = (
            self.rect.move(-10, -10).bottomright
        )

        ## cancel button

        self.cancel_button = Button.from_text(
            text="Cancel",
            command=self.cancel,
            **BUTTON_SETTINGS,
        )

        draw_depth_finish(self.cancel_button.image)

        self.cancel_button.rect.midright = (
            self.start_button.rect.move(-5, 0).midleft
        )

        ## store
        widgets.extend((self.cancel_button, self.start_button))

    def exchange_selection(
        self,
        source_name,
        dest_name,
        must_select_message,
        no_more_items_message,
    ):

        source_listbox = getattr(self, source_name)
        dest_listbox = getattr(self, dest_name)

        ###

        if source_listbox.items:

            selected_values = source_listbox.get()

            if selected_values:

                source_listbox.remove_items(selected_values)
                dest_listbox.extend(selected_values)
                dest_listbox.sort()

            else:
                create_and_show_dialog(must_select_message, level_name='info')

        else:
            create_and_show_dialog(no_more_items_message, level_name='info')

    add_selected = (
        partialmethod(
            exchange_selection,
            'available_cases_listbox',
            'chosen_cases_listbox',
            MUST_SELECT_FROM_AVAILABLE,
            NO_MORE_AVAILABLE_ITEMS,
        )
    )

    remove_selected = (
        partialmethod(
            exchange_selection,
            'chosen_cases_listbox',
            'available_cases_listbox',
            MUST_SELECT_FROM_CHOSEN,
            NO_MORE_CHOSEN_ITEMS,
        )
    )

    def exchange_all(
        self,
        source_name,
        dest_name,
        no_more_items_message,
    ):

        source_listbox = getattr(self, source_name)
        dest_listbox = getattr(self, dest_name)

        ###

        if source_listbox.items:

            values = source_listbox.items.copy()

            source_listbox.remove_items(values)
            dest_listbox.extend(values)
            dest_listbox.sort()

        else:
            create_and_show_dialog(no_more_items_message, level_name='info')

    add_all = (
        partialmethod(
            exchange_all,
            'available_cases_listbox',
            'chosen_cases_listbox',
            NO_MORE_AVAILABLE_ITEMS,
        )
    )

    remove_all = (
        partialmethod(
            exchange_all,
            'chosen_cases_listbox',
            'available_cases_listbox',
            NO_MORE_CHOSEN_ITEMS,
        )
    )

    def set_system_testing_session(self):
        """Present form to set and trigger system testing session."""
        ### draw screen sized semi-transparent object,
        ### so that screen behind form appears as if
        ### unhighlighted
        blit_on_screen(UNHIGHLIGHT_SURF_MAP[SCREEN_RECT.size], (0, 0))

        ### loop until running attribute is set to False

        self.running = True
        self.loop_holder = self

        while self.running:

            ### perform various checkups for this frame;
            ###
            ### stuff like maintaing a constant framerate and more
            SERVICES_NS.frame_checkups()

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

    def trigger_system_testing(self):
        """Trigger system testing session.

        That is, if at least one test case was chosen.
        """

        if not self.chosen_cases_listbox.items:

            create_and_show_dialog(
                "At least one test case must be chosen.",
                level_name='info',
            )

            return

        ### grab test case keys
        test_cases_keys = ['stc0000']

        ### trigger system testing session (it uses play mode)

        raise (

            ResetAppException(
                mode='play',
                data={'test_cases_keys': test_cases_keys}
            )

        )

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
set_system_testing_session = SystemTestingSessionForm().set_system_testing_session
