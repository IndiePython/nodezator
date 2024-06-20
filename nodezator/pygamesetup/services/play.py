
### standard library imports

from types import SimpleNamespace

from collections import defaultdict

from functools import reduce

from itertools import cycle, repeat

from datetime import datetime

from operator import or_ as bitwise_or


### third-party imports

from pygame.locals import (

    QUIT,

    KEYDOWN,
    K_F7, K_F8, K_F9,

    MOUSEMOTION, MOUSEBUTTONDOWN, MOUSEBUTTONUP,

    KMOD_NONE,

)

from pygame.color import THECOLORS

from pygame import locals as pygame_locals

from pygame.math import Vector2

from pygame.event import Event, get, set_allowed, set_blocked

from pygame.display import update, set_mode

from pygame.mouse import set_pos, set_visible as set_mouse_visibility

from pygame.draw import rect as draw_rect


### local imports

from ...config import APP_REFS

from ...ourstdlibs.pyl import load_pyl

from ...ourstdlibs.behaviour import empty_function

from ...our3rdlibs.behaviour import are_changes_saved, indicate_saved

from ...loopman.exception import ResetAppException, QuitAppException

from ...classes2d.single import Object2D

from ...textman.render import render_text

from ..constants import (

    SCREEN, SCREEN_RECT, blit_on_screen,
    GENERAL_NS,
    GENERAL_SERVICE_NAMES,
    maintain_fps,

    CancelWhenPaused, pause,

    watch_window_size,

    EVENT_KEY_STRIP_MAP,
    EVENT_COMPACT_NAME_MAP,
    EVENT_KEY_COMPACT_NAME_MAP,
    KEYS_MAP,
    SCANCODE_NAMES_MAP,
    MOD_KEYS_MAP,

)



### dictionary to store session data
SESSION_DATA = {}

### custom namespace for playing mode

PLAY_REFS = type("Object", (), {})()
PLAY_REFS.pending_test_cases = []
PLAY_REFS.ongoing_test = None
PLAY_REFS.system_testing_playback_speed = 0
PLAY_REFS.test_frames = set()

### map to store events
EVENTS_MAP = {}

## create a map to associate each frame index to the keys that were
## pressed at that frame
GETTER_FROZENSET_MAP = {}

### create a map that associates each frame index to the modifier
### keys that were pressed in that frame
BITMASK_MAP = {}

### create a list to hold all mouse position requests;
MOUSE_POSITIONS = []

### create list to hold all mouse key pressed state requests
MOUSE_PRESSED_TUPLES = []

### create virtual mouse
MOUSE_POS = Vector2(0, 0)

### create flag indicating whether real mouse must trace movements
### of virtual one
PLAY_REFS.mouse_tracing = True

### special frozenset class

class GetterFrozenSet(frozenset):
    """frozenset subclass where "obj[item]" works like "item in obj"."""
    __getitem__ = frozenset.__contains__

## create an empty special frozenset
EMPTY_GETTER_FROZENSET = GetterFrozenSet()



### TODO collections defined below lack proper commenting


REVERSE_EVENT_COMPACT_NAME_MAP = {
    value: key
    for key, value in EVENT_COMPACT_NAME_MAP.items()
}

REVERSE_SCANCODE_NAMES_MAP = {
    value: key
    for key, value in SCANCODE_NAMES_MAP.items()
}


##

def get_resulting_bitmask(mod_key_names):
    """Return bitmask by reducing all modifier keys with bitwise OR."""

    ### return iterable reduced to a single value...

    return reduce(

        ## with the bitwise OR operation
        bitwise_or,

        ## where the iterable contained the values
        ## of the named modifier keys

        (
            # modifier key value obtained from its name
            getattr(pygame_locals, mod_key_name)

            # modifier key names
            for mod_key_name in mod_key_names
        ),

    )


## event map


def get_ready_events(events):
    """Return preprocessed objects as pygame.event.Event instances."""

    for event_name, event_dict in events:

        ### restore the event name if it was in a custom compact form

        if event_name in REVERSE_EVENT_COMPACT_NAME_MAP:
            event_name = REVERSE_EVENT_COMPACT_NAME_MAP[event_name]

        ### restore names of keys in the event name if they were in a
        ### custom compact form

        if event_name in EVENT_KEY_COMPACT_NAME_MAP:

            for full_key, compact_key in (
                EVENT_KEY_COMPACT_NAME_MAP[event_name].items()
            ):

                if compact_key in event_dict:
                    event_dict[full_key] = event_dict.pop(compact_key)

        ### restore missing keys in the event using default values

        if event_name in EVENT_KEY_STRIP_MAP:

            for key, default in EVENT_KEY_STRIP_MAP[event_name].items():
                event_dict.setdefault(key, default)

        ### if dealing with KEY_... events, perform extra preprocessing
        ### in the event dict

        if event_name in ('KEYUP', 'KEYDOWN'):

            ## turn key name and scan code name into the respective
            ## values

            for key, treatment_operation in (

                ('key', KEYS_MAP.__getitem__),
                ('scancode', REVERSE_SCANCODE_NAMES_MAP.__getitem__),

            ):
                event_dict[key] = treatment_operation(event_dict[key])

            ## if the 'mod' key is a tuple, it contains names of
            ## modifiers, so replace it by the respective bitmask
            ## that represent the modifiers

            if type(event_dict['mod']) is tuple:

                ## get names
                mod_key_names = event_dict['mod']

                ## reassign value to 'mod'
                event_dict['mod'] = (

                    # if there's only one name, just use the key value
                    getattr(pygame_locals, mod_key_names[0])
                    if len(mod_key_names) == 1

                    # otherwise build the bitmask with all modifier
                    # values
                    else get_resulting_bitmask(mod_key_names)

                )

        ### obtain the event type
        event_type = getattr(pygame_locals, event_name)

        ### yield a pygame.event.Event object
        yield Event(event_type, event_dict)



def set_behaviour(services_namespace, data):
    """Setup play services and data."""

    pending_cases = PLAY_REFS.pending_test_cases

    ### define flag based on existence of key in given data
    starting_system_testing_session = hasattr(data, 'test_cases_ids')

    ### setup test cases if we are starting a system testing session

    if starting_system_testing_session:

        APP_REFS.playsupport.prepare_system_testing_session(
            data.test_cases_ids,
            data.playback_speed,
        )

        pending_cases.extend(
            sorted(data.test_cases_ids, reverse=True)
        )

        PLAY_REFS.system_testing_playback_speed = data.playback_speed


    ### if there are pending test cases, pick last one and make preparations
    ### to perform it if needed

    if pending_cases:

        ## pop test case id from list of pending case and it in the
        ## PLAY_REFS namespace
        PLAY_REFS.ongoing_test = pending_cases.pop()

        ## execute test setups as needed
        APP_REFS.playsupport.perform_test_setup(PLAY_REFS.ongoing_test, data)

        ## define the playback speed
        data.playback_speed = PLAY_REFS.system_testing_playback_speed

        ## make sure the set holding frame indices is clear and, if there are
        ## test frame indices in data, store then in the set

        PLAY_REFS.test_frames.clear()

        if hasattr(data, 'test_frames'):
            PLAY_REFS.test_frames.update(data.test_frames)

        ## ensure app indicates that there are no unsaved changes and perform
        ## extra clean up, if needed
        ##
        ## this is needed to prevent the app from complaining there are
        ## unsaved changes when in fact we just want to ignore them, since
        ## we expect they were made in the previous test case, that already
        ## finished

        if not are_changes_saved():

            indicate_saved()
            APP_REFS.wm.clean_loaded_file_data()


    ### set play services as current ones

    our_globals = globals()

    for attr_name in GENERAL_SERVICE_NAMES:

        value = our_globals[attr_name]
        setattr(services_namespace, attr_name, value)

    ### load session data

    if hasattr(data, 'input_data_path'):
        SESSION_DATA.update(load_pyl(data.input_data_path))

    else:
        SESSION_DATA.update(data.input_data)

    ### retrieve playback speed and last frame index

    playback_speed = data.playback_speed
    last_frame_index = SESSION_DATA['last_frame_index']

    ### store playback speed, last frame index and recording width

    PLAY_REFS.fps = playback_speed
    PLAY_REFS.last_frame_index = last_frame_index
    PLAY_REFS.recording_width = SESSION_DATA['recording_size'][0]

    ### only reset the display mode (pygame.display.set_mode), if...
    ###
    ### - we are not in the middle of a system testing session
    ### - or, if we are, it is just getting started
    ###
    ### this way we avoid resetting the display mode needlessly, since
    ### we only need to reset it for a simple play session or for the
    ### first in a series of test cases (even when the series has only
    ### that case)

    if PLAY_REFS.ongoing_test is None or starting_system_testing_session:
        set_mode(SESSION_DATA['recording_size'], 0)

    ### trigger setups related to window size change
    watch_window_size()

    ### create and store title and duration label, then reposition
    ### all labels

    new_title_label = (
        Object2D.from_surface(
            render_text(
                text = SESSION_DATA['recording_title'],
                padding = 6,
                foreground_color = THECOLORS['white'],
                background_color = THECOLORS['blue'],
                border_color = THECOLORS['white'],
                border_thickness=2,
            )
        )
    )

    if playback_speed:

        duration = (

            get_formatted_duration(
                frame_quantity=last_frame_index,
                frames_per_second=playback_speed,
            )

        )

        duration_text = f"Duration: ~{duration}"

    else:
        duration_text = "No duration (uncapped speed)"

    duration_label = (
        Object2D.from_surface(
            render_text(
                text = duration_text,
                padding = 6,
                foreground_color = THECOLORS['white'],
                background_color = THECOLORS['blue'],
                border_color = THECOLORS['white'],
                border_thickness=2,
            )
        )
    )

    LABELS.insert(0, new_title_label)
    LABELS.append(duration_label)

    topright = SCREEN_RECT.move(-10, 32).topright

    for label in LABELS:

        label.rect.topright = topright
        topright = label.rect.move(0, 5).bottomright

    ### ensure paused label has same position as the second one
    PAUSED_LABEL.rect.topleft = LABELS[2].rect.topleft

    ### since the app will be playing recorded events, we are not interested
    ### in new ones generated while playing, so we block most of them, leaving
    ### just a few that we may use to during playback

    set_blocked(None)
    set_allowed([QUIT, KEYDOWN])

    ### prepare events

    EVENTS_MAP.update(

        (frame_index, list(get_ready_events(compact_events)))

        for frame_index, compact_events
        in SESSION_DATA['events_map'].items()

    )


    ### prepare key states

    ## convert from compact to suitable format to use

    frame_to_keys_map = defaultdict(list)

    for key_name, frames in SESSION_DATA['key_name_to_frames_map'].items():

        for frame in frames:
            frame_to_keys_map[frame].append(key_name)


    ## update map with frozensets

    GETTER_FROZENSET_MAP.update(

        (
            frame_index,

            GetterFrozenSet(
                getattr(pygame_locals, key_name)
                for key_name in pressed_key_names
            )

        )

        for frame_index, pressed_key_names
        in frame_to_keys_map.items()

    )


    ### prepare modifier key states

    ## convert from compact to suitable format to use

    frame_to_mod_key_names = defaultdict(list)

    for mod_key_name, frames in SESSION_DATA['mod_key_name_to_frames_map'].items():

        for frame in frames:
            frame_to_mod_key_names[frame].append(mod_key_name)

    ## update map with bitmasks

    BITMASK_MAP.update(

        (
            frame_index,

            (

                ## if there's only one modifier key pressed, get its value
                ## from pygame.locals
                getattr(pygame_locals, mod_key_names[0])
                if len(mod_key_names) == 1

                ## otherwise get the bitmask that results from combining
                ## the values of all pressed modifiers
                else get_resulting_bitmask(mod_key_names)

            )

        )

        for frame_index, mod_key_names
        in frame_to_mod_key_names.items()
    )

    ### update list containing all mouse position requests;
    ###
    ### then reverse its orders so the first ones are the first
    ### ones to be popped from the list

    MOUSE_POSITIONS.extend(SESSION_DATA['mouse_pos_requests'])
    MOUSE_POSITIONS.reverse()

    ### do the same as above to list of all mouse key pressed
    ### state requests (create and reverse it)

    MOUSE_PRESSED_TUPLES.extend(SESSION_DATA['mouse_key_state_requests'])
    MOUSE_PRESSED_TUPLES.reverse()

    ### set frame index to -1 (so when it is incremented at the beginning
    ### of the loop it is set to 0, the first frame)
    GENERAL_NS.frame_index = -1


### constants


## set with mouse event types
MOUSE_EVENTS = frozenset({MOUSEMOTION, MOUSEBUTTONDOWN, MOUSEBUTTONUP})

## label creation

# create labels

LABELS = [

    Object2D.from_surface(
        render_text(
            text = text,
            padding = 6,
            foreground_color = THECOLORS['white'],
            background_color = THECOLORS['blue'],
            border_color = THECOLORS['white'],
            border_thickness=2,
        )
    )

    for text in (
        "F7: leave playing mode",
        "F8: play/pause",
        "F9: toggle mouse control",
    )

]

PAUSED_LABEL = (
    Object2D.from_surface(
        render_text(
            text = "F8: play/pause",
            padding = 6,
            foreground_color = THECOLORS['white'],
            background_color = THECOLORS['red3'],
            border_color = THECOLORS['white'],
            border_thickness=2,
        )
    )
)


### session behaviours

## processing events

def get_events():

    ### leave playing mode if frame is last one

    if GENERAL_NS.frame_index == PLAY_REFS.last_frame_index:
        leave_playing_mode()

    ### process QUIT or KEYDOWN event (for the F9 key) if
    ### they are thrown

    for event in get():

        if event.type == QUIT:
            raise QuitAppException

        elif event.type == KEYDOWN:

            ### pause playing

            if event.key == K_F8:

                ### indicate pause by blitting paused label
                blit_on_screen(PAUSED_LABEL.image, PAUSED_LABEL.rect)

                ### pause

                try:
                    pause()

                ### if during pause user asks to cancel playing, do
                ### it here

                except CancelWhenPaused:
                    leave_playing_mode(manually_triggered=True)

            ### toggle mouse tracing

            elif event.key == K_F9:
                PLAY_REFS.mouse_tracing = not PLAY_REFS.mouse_tracing

            ### leave playing mode

            elif event.key == K_F7:
                leave_playing_mode(manually_triggered=True)

    ### play the recorded events

    ## if there are events for the current frame index in the event map,
    ## iterate over them

    if GENERAL_NS.frame_index in EVENTS_MAP:

        for event in EVENTS_MAP[GENERAL_NS.frame_index]:

            ## if we have a mouse event, we use it to position the mouse
            if event.type in MOUSE_EVENTS:
                set_mouse_pos(event.pos)

            ## finally yield the event, regardless of its type
            yield event


## processing key pressed states

def get_pressed_keys():
    """Emulates pygame.key.get_pressed().

    That is, the return value despite being a different object, works
    just like the return value of pygame.key.get_pressed().
    """

    return (

        ### return a GetterFrozenSet for the current
        ### frame index if there's one
        GETTER_FROZENSET_MAP[GENERAL_NS.frame_index]
        if GENERAL_NS.frame_index in GETTER_FROZENSET_MAP

        ### otherwise return an empty GetterFrozenSet
        else EMPTY_GETTER_FROZENSET

    )


## processing modifier key pressed states

def get_pressed_mod_keys():
    """Emulates pygame.key.get_mods().

    That is, the return value is also a bitmask or pygame.locals.KMOD_NONE.
    """

    return (

        ### return a bitmask for the current frame index if there's one
        BITMASK_MAP[GENERAL_NS.frame_index]
        if GENERAL_NS.frame_index in BITMASK_MAP

        ### otherwise return pygame.locals.KMOD_NONE
        else KMOD_NONE

    )


## processing mouse position getting and setting

def get_mouse_pos():
    """Emulates pygame.mouse.get_pos(); performs additional setups."""
    ### grab recorded position
    pos = MOUSE_POSITIONS.pop()

    ### set mouse pointer to the position
    set_mouse_pos(pos)

    ### return position
    return pos


def set_mouse_pos(pos):
    """Extends pygame.mouse.set_pos()."""
    ### update position of virtual mouse with given pos
    MOUSE_POS.update(pos)

    ### if mouse tracing is on, set position of real mouse as well,
    ### (using pygame.mouse.set_pos())
    ###
    ### this is done so that the real mouse traces the movement of the
    ### virtual one
    PLAY_REFS.mouse_tracing and set_pos(pos)


## processing mouse button pressed state;
##
## this get_mouse_pressed() callable is used to emulate the
## pygame.mouse.get_pressed() function and return the same kind
## of value
get_mouse_pressed = MOUSE_PRESSED_TUPLES.pop


### screen updating

def update_screen():
    """Extends pygame.display.update()."""
    ### draw progress

    width = round(
        abs(GENERAL_NS.frame_index / PLAY_REFS.last_frame_index) # progress
        * PLAY_REFS.recording_width                              # full width
    )

    draw_rect(SCREEN, 'red', (0, 0, width, 3))

    ### blit labels

    for label in LABELS:
        blit_on_screen(label.image, label.rect)

    ### update the screen
    update()

### other operations

def leave_playing_mode(manually_triggered=False):
    """Perform setups to leave playing mode.

    Sometimes, leaving playing mode means that we'll reenter it.
    For instance, when performing a system testing session (performing
    multiple system tests).

    Parameters
    ==========

    manually_triggered (bool)
        Whether leaving playing mode was triggered manually by the user
        or not. Only relevant when in the middle of a system testing
        session.
    """

    ### clear stored data
    clear_data()

    ### act depending on...
    ### - whether we are performing tests or not
    ### - whether there are more pending tests
    ### - whether leaving playing mode was manually or naturally triggered

    if PLAY_REFS.ongoing_test is not None:

        ## if leaving playing mode was triggered by the user

        if manually_triggered:

            ##

            APP_REFS.playsupport.finish_system_testing_session_earlier(
                PLAY_REFS.ongoing_test
            )

            ##

            PLAY_REFS.pending_test_cases.clear()
            PLAY_REFS.ongoing_test = None

            ##

            if APP_REFS.system_testing_set:
                APP_REFS.system_testing_set = False

            ##

            raise (
                ResetAppException(
                    mode='normal',
                    data={'left_system_testing_midway': True},
                )
            )

        else:

            # clear set of test frames
            PLAY_REFS.test_frames.clear()

            # perform final assertions, store test results and perform teardown

            APP_REFS.playsupport.finish_test_case(
                PLAY_REFS.ongoing_test,
                PLAY_REFS.last_frame_index,
            )

            # act according to existence of pending test cases

            if PLAY_REFS.pending_test_cases:
                raise ResetAppException(mode='play')

            else:

                PLAY_REFS.ongoing_test = None

                tests_report_data = (
                    APP_REFS
                    .playsupport
                    .finish_system_testing_session_and_get_report()
                )

                raise (

                    ResetAppException(
                        mode='normal',
                        data={'tests_report_data': tests_report_data},
                    )

                )

    else:
        raise ResetAppException(mode='normal')

def clear_data():
    ### clear collections

    for collection in (
        EVENTS_MAP,
        GETTER_FROZENSET_MAP,
        BITMASK_MAP,
        MOUSE_POSITIONS,
        MOUSE_PRESSED_TUPLES,
    ):
        collection.clear()

    ### remove title and duration labels

    del LABELS[0]
    del LABELS[-1]


### frame checkup operations

def frame_checkups():
    """Perform various checkups.

    Meant to be used at the beginning of each frame in the
    app loop.
    """
    ### keep constants fps
    maintain_fps(PLAY_REFS.fps)

    ### increment frame number
    GENERAL_NS.frame_index += 1

    ### if there is an ongoing test, check whether
    ### an assertion must be executed in the current
    ### frame and do so if it is the case

    if (
        PLAY_REFS.ongoing_test is not None
        and GENERAL_NS.frame_index in PLAY_REFS.test_frames
    ):

        (
            APP_REFS
            .playsupport
            .perform_frame_assertions
            (PLAY_REFS.ongoing_test, GENERAL_NS.frame_index)
        )


def frame_checkups_with_fps(fps):
    """Same as frame_checkups(), but uses given fps."""
    ### keep constants fps
    maintain_fps(fps)

    ### increment frame number
    GENERAL_NS.frame_index += 1

    ### if there is an ongoing test, check whether
    ### an assertion must be executed in the current
    ### frame and do so if it is the case

    if (
        PLAY_REFS.ongoing_test is not None
        and GENERAL_NS.frame_index in PLAY_REFS.test_frames
    ):

        (
            APP_REFS
            .playsupport
            .perform_frame_assertions
            (PLAY_REFS.ongoing_test, GENERAL_NS.frame_index)
        )


### small utility

def get_formatted_duration(frame_quantity, frames_per_second):
    """Return specially formatted duration."""
    duration = ""

    total_seconds = round(frame_quantity/frames_per_second)

    minutes, seconds = divmod(total_seconds, 60)

    if minutes >= 1:

        duration += f"{minutes}min"

        if minutes >= 2:
            duration += "s"

    if seconds >= 1:

        duration += f"{seconds}sec"

        if seconds >= 2:
            duration += "s"

    return duration
