
### standard library imports

from pathlib import Path

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
    K_F9,

    MOUSEMOTION, MOUSEBUTTONDOWN, MOUSEBUTTONUP,

    KMOD_NONE,

)

from pygame import (
    Surface,
    quit as quit_pygame,
    locals as pygame_locals,
)

from pygame.math import Vector2

from pygame.event import Event, get, set_allowed, set_blocked

from pygame.display import set_mode, update

from pygame.mouse import set_pos, set_visible as set_mouse_visibility

from pygame.font import SysFont

from pygame.draw import rect as draw_rect


### local imports

from ..config import APP_REFS

from ..ourstdlibs.pyl import load_pyl

from ..ourstdlibs.behaviour import empty_function


from .constants import (

    DEPTH, FPS, maintain_fps,

    DEFAULT_SIZE, FLAG,

    EVENT_KEY_STRIP_MAP,
    EVENT_COMPACT_NAME_MAP,
    KEYS_MAP,
    SCANCODE_NAMES_MAP,
    MOD_KEYS_MAP,

)


### pygame constants

SCREEN = set_mode(DEFAULT_SIZE, FLAG, DEPTH)

SCREEN_RECT = SCREEN.get_rect()
blit_on_screen = SCREEN.blit


### block all events except pygame.QUIT and pygame.KEYDOWN

set_blocked(None)
set_allowed([QUIT, KEYDOWN])


### references for playing mode
PLAY_REFS = SimpleNamespace()

### create virtual mouse
MOUSE_POS = Vector2(0, 0)



###

REVERSE_EVENT_COMPACT_NAME_MAP = {
    value: key
    for key, value in EVENT_COMPACT_NAME_MAP.items()
}

REVERSE_SCANCODE_NAMES_MAP = {
    value: key
    for key, value in SCANCODE_NAMES_MAP.items()
}

### load session inputs

input_path = APP_REFS.input_path

data = load_pyl(input_path)

PLAY_REFS.last_frame_index = data['last_frame_index']

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


### prepare events

EVENTS_MAP = {

    frame_index : list(get_ready_events(compact_events))

    for frame_index, compact_events in data['events_map'].items()

}


### prepare key states

## define special frozenset class

class GetterFrozenSet(frozenset):
    """Same as frozenset, but obj[item] works like "item in obj"."""
    __getitem__ = frozenset.__contains__

## create an empty special frozenset
EMPTY_GETTER_FROZENSET = GetterFrozenSet()

## create a map associating each frame index to the keys that were
## pressed at that frame

NON_EMPTY_GETTER_FROZENSETS = {

    frame_index: (

        GetterFrozenSet(
            getattr(pygame_locals, key_name)
            for key_name in pressed_key_names
        )

    )

    for frame_index, pressed_key_names
    in data['pressed_keys_map'].items()

}


### prepare modifier key states;
###
### create a map that associates each frame index to the modifier
### keys that were pressed in that frame

NO_KMOD_NONE_BITMASKS = {

    frame_index : (

        ## if there's only one modifier key pressed, get its value
        ## from pygame.locals
        getattr(pygame_locals, mod_key_names[0])
        if len(mod_key_names) == 1

        ## otherwise get the bitmask that results from combining
        ## the values of all pressed modifiers
        else get_resulting_bitmask(mod_key_names)

    )

    for frame_index, mod_key_names
    in data['mod_key_bitmasks_map'].items()
}

### create a list containing all mouse position requests;
###
### then reverse its orders so the first ones are the first
### ones to be popped from the list

MOUSE_POSITIONS = list(data['mouse_pos_requests'])
MOUSE_POSITIONS.reverse()

### do the same as above to a list of all mouse key pressed
### state requests (create and reverse it)

MOUSE_PRESSED_TUPLES = list(data['mouse_key_state_requests'])
MOUSE_PRESSED_TUPLES.reverse()


### constants


## label creation

# define callables to assist in creating label

render_label_text = SysFont('Arial', 16, bold=True).render

def get_label(text, label_fg, label_bg, label_outline, padding):

    ### render the text itself

    label_text = render_label_text(
        text,
        True,
        label_fg,
        label_bg,
    )

    ### create a surface with the sides incremented by
    ### double the padding

    label = (

        Surface(

            tuple(
                v + (padding * 2)
                for v in label_text.get_size()
            )

        ).convert()

    )

    ### fill the surface with the outline color
    label.fill(label_outline)

    ### draw a slightly smaller rect inside the surface with the
    ### filling color
    draw_rect(label, label_bg, label.get_rect().inflate(-2, -2))

    ### blit the text inside the surface where the padding
    ### ends
    label.blit(label_text, (padding, padding))

    ### finally return the label
    return label

# create label, its rect, and position it

label = (
    get_label(
        text = "F9: play/pause toggle",
        label_fg = 'white',
        label_bg = 'blue',
        label_outline = 'white',
        padding=6,
    )
)

label_rect = label.get_rect()

label_rect.topright = SCREEN_RECT.move(-10, 40).topright


### create function to setup playing mode and assign it as the
### frame index routine

def setup_playing_mode():

    ### set frame index to 0
    PLAY_REFS.frame_index = 0

    ### set frame index setup as the frame index routine
    PLAY_REFS.frame_index_routine = perform_frame_index_setups

### set playing mode setup as the frame index routine
PLAY_REFS.frame_index_routine = setup_playing_mode


### create function to perform setups related to the frame index

def perform_frame_index_setups():

    ### increment frame index by 1
    PLAY_REFS.frame_index += 1

    ### act according to whether frame is last one

    if PLAY_REFS.frame_index == PLAY_REFS.last_frame_index:

        quit_pygame()
        quit()

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
            

## TODO keep refactoring from here


### session behaviours

## processing events

MOUSE_EVENTS = MOUSEMOTION, MOUSEBUTTONDOWN, MOUSEBUTTONUP

def get_events():

    for event in get():

        if event.type == QUIT:
            print("Tried quitting")

        elif event.type == KEYDOWN and event.key == K_F9:
            pause()

    for event in (

        #
        EVENTS_MAP[PLAY_REFS.frame_index]
        if PLAY_REFS.frame_index in EVENTS_MAP

        #
        else ()

    ):
        if event.type in MOUSE_EVENTS:
            set_mouse_pos(event.pos)

        yield event

## processing key pressed states

def get_pressed_keys():

    return (

        #
        NON_EMPTY_GETTER_FROZENSETS[PLAY_REFS.frame_index]
        if PLAY_REFS.frame_index in NON_EMPTY_GETTER_FROZENSETS

        #
        else EMPTY_GETTER_FROZENSET

    )

def get_pressed_mod_keys():

    return (

        #
        NO_KMOD_NONE_BITMASKS[PLAY_REFS.frame_index]
        if PLAY_REFS.frame_index in NO_KMOD_NONE_BITMASKS

        #
        else KMOD_NONE

    )

## processing mouse

def get_mouse_pos():

    pos = MOUSE_POSITIONS.pop()
    set_mouse_pos(pos)

    return pos

get_mouse_pressed = MOUSE_PRESSED_TUPLES.pop

def set_mouse_pos(pos):
    MOUSE_POS.update(pos)
    set_pos(pos)

### screen updating

def update_screen():
    blit_on_screen(label, label_rect)

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

