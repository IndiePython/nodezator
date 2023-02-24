
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
    K_F8, K_F9,

    MOUSEMOTION, MOUSEBUTTONDOWN, MOUSEBUTTONUP,

    KMOD_NONE,

)

from pygame import (
    Surface,
    locals as pygame_locals,
)

from pygame.math import Vector2

from pygame.event import Event, get, set_allowed, set_blocked

from pygame.display import update, set_mode

from pygame.mouse import set_pos, set_visible as set_mouse_visibility


### local imports

from ...ourstdlibs.pyl import load_pyl

from ...ourstdlibs.behaviour import empty_function

from ...loopman.exception import ResetAppException


from ..constants import (

    SCREEN_RECT, blit_on_screen,
    GENERAL_SERVICE_NAMES,
    FPS, maintain_fps,

    watch_window_size,

    EVENT_KEY_STRIP_MAP,
    EVENT_COMPACT_NAME_MAP,
    KEYS_MAP,
    SCANCODE_NAMES_MAP,
    MOD_KEYS_MAP,

    get_label_object,

)



### dictionary to store session data
SESSION_DATA = {}

### custom namespace for playing mode
PLAY_REFS = type("Object", (), {})()

### map to store events
EVENTS_MAP = {}

## create a map to associate each frame index to the keys that were
## pressed at that frame
NON_EMPTY_GETTER_FROZENSETS = {}

### create a map that associates each frame index to the modifier
### keys that were pressed in that frame
NO_KMOD_NONE_BITMASKS = {}

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
    """Return bitmask by "bitwise ORing" all named modifier keys."""
    ### return reduced iterable

    return reduce(

        ## with the bitwise OR operation
        bitwise_or,

        ## where the iterable contains the values
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

    ### set play services as current ones

    our_globals = globals()

    for attr_name in GENERAL_SERVICE_NAMES:

        value = our_globals[attr_name]
        setattr(services_namespace, attr_name, value)

    ### load session data
    SESSION_DATA.update(load_pyl(data['input_data_path']))

    ### reset window mode (pygame.display.set_mode)
    set_mode(SESSION_DATA['recording_size'], 0)

    ### trigger setups related to window size change
    watch_window_size()

    ### create and store title label, then reposition
    ### all labels

    new_title_label = (
        get_label_object(
            text = SESSION_DATA['recording_title'],
            label_fg = 'white',
            label_bg = 'blue',
            label_outline = 'white',
            padding = 6,
        )
    )

    LABELS.insert(0, new_title_label)

    topright = SCREEN_RECT.move(-10, 32).topright

    for label in LABELS:

        label.rect.topright = topright
        topright = label.rect.move(0, 5).bottomright

    ### since the app will be playing recorded events, we are not interested
    ### in new ones generated while playing, so we block most of them, leaving
    ### just a few that we may use to during playback

    set_blocked(None)
    set_allowed([QUIT, KEYDOWN])

    ###
    PLAY_REFS.last_frame_index = SESSION_DATA['last_frame_index']

    ### prepare events

    EVENTS_MAP.update(

        (frame_index, list(get_ready_events(compact_events)))

        for frame_index, compact_events
        in SESSION_DATA['events_map'].items()

    )


    ### prepare key states: update map with non empty frozensets

    NON_EMPTY_GETTER_FROZENSETS.update(

        (
            frame_index,

            GetterFrozenSet(
                getattr(pygame_locals, key_name)
                for key_name in pressed_key_names
            )

        )

        for frame_index, pressed_key_names
        in SESSION_DATA['pressed_keys_map'].items()

    )


    ### prepare modifier key states: update map with bitmasks

    NO_KMOD_NONE_BITMASKS.update(

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
        in SESSION_DATA['mod_key_bitmasks_map'].items()
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

    ### set playing mode setup as the frame index routine
    PLAY_REFS.frame_index_routine = setup_playing_mode


### constants


## set with mouse event types
MOUSE_EVENTS = frozenset({MOUSEMOTION, MOUSEBUTTONDOWN, MOUSEBUTTONUP})

## label creation

# create labels

LABELS = [

    get_label_object(
        text = text,
        label_fg = 'white',
        label_bg = 'blue',
        label_outline = 'white',
        padding = 6,
    )

    for text in (
        "F9: play/pause",
        "F8: toggle mouse tracing",
    )

]


### create function to setup playing mode and assign it as the
### frame index routine

def setup_playing_mode():

    ### set frame index to 0
    PLAY_REFS.frame_index = 0

    ### set frame index setup as the frame index routine
    PLAY_REFS.frame_index_routine = increment_frame_index


### create function to increment the frame index by 1

def increment_frame_index():
    """Increment frame index by 1."""
    PLAY_REFS.frame_index += 1


### function to pause session replaying

def pause():

    running = True

    while running:

        ### keep constants fps
        maintain_fps(FPS)

        ### process events

        for event in get():

            if event.type == QUIT:
                print("Tried quitting")

            elif event.type == KEYDOWN and event.key == K_F9:
                running = False

        ### update the screen
        update()


### session behaviours

## processing events

def get_events():

    ### reset app if frame is last one

    if PLAY_REFS.frame_index == PLAY_REFS.last_frame_index:

        ### clear collections

        for collection in (
            EVENTS_MAP,
            NON_EMPTY_GETTER_FROZENSETS,
            NO_KMOD_NONE_BITMASKS,
            MOUSE_POSITIONS,
            MOUSE_PRESSED_TUPLES,
        ):
            collection.clear()

        ### remove title label
        del LABELS[0]

        ### reset app
        raise ResetAppException(mode='normal')

    ### process QUIT or KEYDOWN event (for the F9 key) if
    ### they are thrown

    for event in get():

        if event.type == QUIT:
            print("Tried quitting")

        elif event.type == KEYDOWN:

            if event.key == K_F8:
                PLAY_REFS.mouse_tracing = not PLAY_REFS.mouse_tracing

            elif event.key == K_F9:
                pause()

    ### play the recorded events

    ## if there are events for the current frame index in the event map,
    ## iterate over them

    if PLAY_REFS.frame_index in EVENTS_MAP:

        for event in EVENTS_MAP[PLAY_REFS.frame_index]:

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

        ### return a non empty GetterFrozenSet for the current
        ### frame index if there's one
        NON_EMPTY_GETTER_FROZENSETS[PLAY_REFS.frame_index]
        if PLAY_REFS.frame_index in NON_EMPTY_GETTER_FROZENSETS

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
        NO_KMOD_NONE_BITMASKS[PLAY_REFS.frame_index]
        if PLAY_REFS.frame_index in NO_KMOD_NONE_BITMASKS

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
    ### blit labels

    for label in LABELS:
        blit_on_screen(label.image, label.rect)

    ### update the screen
    update()


### frame checkup operations

def frame_checkups():
    """Perform various checkups.

    Meant to be used at the beginning of each frame in the
    app loop.
    """
    ### keep constants fps
    maintain_fps(FPS)

    ### execute frame index routine
    PLAY_REFS.frame_index_routine()

def frame_checkups_with_fps(fps):
    """Same as frame_checkups(), but uses given fps."""
    ### keep constants fps
    maintain_fps(fps)

    ### execute frame index routine
    PLAY_REFS.frame_index_routine()
