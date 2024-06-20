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

from ...pygamesetup.constants import FPS, GENERAL_NS

from ...dialog import create_and_show_dialog

from ...ourstdlibs.behaviour import empty_function

from ...our3rdlibs.behaviour import are_changes_saved

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

from ...systemtesting.constants import TEST_ID_TO_TITLE, ID_FORMAT_SPEC

from ...userprefsman.main import USER_PREFS
from ...userprefsman.constants import TEST_SESSION_SETTINGS_KEY

from ...colorsman.colors import (
    BLACK,
    CONTRAST_LAYER_COLOR,
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


TEST_ID_TO_LABEL_TEXT = {

    index: 'STC ' + format(index, ID_FORMAT_SPEC) + " - " + title

    for index, title in TEST_ID_TO_TITLE.items()

}

LABEL_TEXT_TO_TEST_ID = {v: k for k, v in TEST_ID_TO_LABEL_TEXT.items()}

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

CANT_TRIGGER_TESTS_DURING_PLAY_RECORD = (
    "System testing sessions can't be triggered during play or record mode"
)

MUST_SAVE_OR_CLOSE_TO_TRIGGER_TESTS = (
    "System testing sessions can't be triggered when there are unsaved"
    " changes. Save the changes first or close the file, then try triggering"
    " tests again."
)

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
            items = sorted(TEST_ID_TO_LABEL_TEXT.values()),
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
        ### if we are in play or record mode, test sessions can't be
        ### triggered, so notify user via dialog and prevent rest of
        ### method from executing by returning earlier

        if GENERAL_NS.mode_name in ('play', 'record'):

            create_and_show_dialog(CANT_TRIGGER_TESTS_DURING_PLAY_RECORD)
            return

        ### we can't trigger a test session when there are unsaved changes;
        ###
        ### notify user of that via dialog and prevent rest of method from
        ### executing by returning earlier

        if not are_changes_saved():

            create_and_show_dialog(MUST_SAVE_OR_CLOSE_TO_TRIGGER_TESTS)
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

                ## if we leave the inner loop, exit the outer one
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

        ### grab test cases ids

        test_cases_ids = [
            LABEL_TEXT_TO_TEST_ID[item]
            for item in self.chosen_cases_listbox.items
        ]

        ### turn on a flag for saving the test settings for reuse
        ### after the tests are finished
        APP_REFS.system_testing_set = True

        ### trigger system testing session

        raise (

            ResetAppException(
                mode='play',
                data={
                    'test_cases_ids': test_cases_ids,
                    'playback_speed': self.speed_entry.get(),
                }
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


### instantiate class and reference relevant method
set_system_testing_session = SystemTestingSessionForm().set_system_testing_session


### utility functions

def rerun_previous_test_session():
    """Trigger system testing session reusing previous settings."""
    ### if we are in play or record mode, test sessions can't be
    ### triggered, so notify user via dialog and prevent rest of
    ### method from executing by returning earlier

    if GENERAL_NS.mode_name in ('play', 'record'):

        create_and_show_dialog(CANT_TRIGGER_TESTS_DURING_PLAY_RECORD)
        return

    ### we can't trigger a test session when there are unsaved changes;
    ###
    ### notify user of that via dialog and prevent rest of method from
    ### executing by returning earlier

    if not are_changes_saved():

        create_and_show_dialog(MUST_SAVE_OR_CLOSE_TO_TRIGGER_TESTS)
        return

    ### notify user if there is no saved test settings in the user data

    if TEST_SESSION_SETTINGS_KEY not in USER_PREFS:

        create_and_show_dialog(
            "It seems you didn't run any test(s) previously."
            " Run a test session first so that its settings can"
            " be saved and reused."
        )

    ### otherwise, trigger test session after referencing the saved testing
    ### data and making appropriate checks; additional setups as also made
    ### when needed

    else:

        ### grab saved test settings
        test_settings = USER_PREFS[TEST_SESSION_SETTINGS_KEY]

        ### define a set holding the requested test case ids saved on disk
        saved_ids = set(test_settings['test_cases_ids'])

        ### define another set containing only the ids from the previous
        ### set that in fact still exist
        existing_ids = saved_ids.intersection(TEST_ID_TO_TITLE.keys())

        ### if there are saved ids that don't exist anymore, turn on
        ### a flag that causes the saved data on disk to be updated
        ### at the end of the testing session

        if saved_ids != existing_ids:
            APP_REFS.system_testing_set = True

        ### if none of the ids exist, use all available ones

        if not existing_ids:
            existing_ids.update(TEST_ID_TO_TITLE.keys())

        ### trigger system testing session

        raise (

            ResetAppException(
                mode='play',
                data={
                    'test_cases_ids': sorted(existing_ids),
                    'playback_speed': test_settings['playback_speed'],
                }
            )

        )


def run_all_cases_at_max_speed():
    """Trigger system testing session with all test cases at maximum speed."""
    ### if we are in play or record mode, test sessions can't be
    ### triggered, so notify user via dialog and prevent rest of
    ### method from executing by returning earlier

    if GENERAL_NS.mode_name in ('play', 'record'):

        create_and_show_dialog(CANT_TRIGGER_TESTS_DURING_PLAY_RECORD)
        return

    ### we can't trigger a test session when there are unsaved changes;
    ###
    ### notify user of that via dialog and prevent rest of method from
    ### executing by returning earlier

    if not are_changes_saved():

        create_and_show_dialog(MUST_SAVE_OR_CLOSE_TO_TRIGGER_TESTS)
        return

    ### turn on a flag for saving the test settings for reuse
    ### after the tests are finished
    APP_REFS.system_testing_set = True

    ### trigger system testing session

    raise (

        ResetAppException(
            mode='play',
            data={
                'test_cases_ids': sorted(TEST_ID_TO_TITLE.keys()),
                'playback_speed': 0,
            }
        )

    )
