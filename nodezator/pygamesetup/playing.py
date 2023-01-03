
### standard library imports

from pathlib import Path

from types import SimpleNamespace

from collections import defaultdict

from functools import reduce

from itertools import cycle, repeat

from datetime import datetime

from operator import or_ as bitwise_or


### third-party imports

from pygame import (
    QUIT,

    KEYDOWN,
    K_F9,

    MOUSEMOTION, MOUSEBUTTONDOWN, MOUSEBUTTONUP,

    KMOD_NONE,
    Surface,

    quit as quit_pygame,
)

from pygame import locals as pygame_locals

from pygame.math import Vector2

from pygame.event import get, set_allowed, set_blocked

from pygame.display import set_mode, update

from pygame.mouse import set_pos, set_visible as set_mouse_visibility

from pygame.font import Font

from pygame.draw import rect as draw_rect


### local imports

from ..config import APP_REFS

from ..ourstdlibs.pyl import load_pyl


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

    return reduce(

        ##
        bitwise_or,

        ## mod keys
        (
            # mod key
            getattr(pygame_locals, mod_key_name)

            # for each mod key name
            for mod_key_name in mod_key_names
        )

    )


## event map


def get_events_ready(events):

    for event_name, event_dict in events:

        ### restore name if needed

        if event_name in REVERSE_EVENT_COMPACT_NAME_MAP:
            event_name = REVERSE_EVENT_COMPACT_NAME_MAP[event_name]

        ###
        if event_name in EVENT_KEY_STRIP_MAP:

            for key, default in EVENT_KEY_STRIP_MAP[event_name].items():
                event_dict.setdefault(key, default)

        ###
        if event_name in ('KEYUP', 'KEYDOWN'):

            for key, get_treated in (

                ('key', KEYS_MAP.__getitem__),
                ('scancode', REVERSE_SCANCODE_NAMES_MAP.__getitem__),

            ):
                event_dict[key] = get_treated(event_dict[key])

            ##

            if type(event_dict['mod']) is tuple:

                mod_key_names = event_dict['mod']

                event_dict['mod'] = (

                    #
                    getattr(pygame_locals, mod_key_names[0])
                    if len(mod_key_names) == 1

                    #
                    else get_resulting_bitmask(mod_key_names)

                )

        ###
        event_type = getattr(pygame_locals, event_name)

        yield SimpleNamespace(type=event_type, **event_dict)

events_map = data['events_map']

EVENTS_MAP = (

    {
        frame_index : list(get_events_ready(compact_events))
        for frame_index, compact_events in events_map.items()
    }
    if events_map

    else {}

)


## key states

class GetterFrozenSet(frozenset):
    __getitem__ = frozenset.__contains__

NON_EMPTY_GETTER_FROZENSETS = {

    key: (

        GetterFrozenSet(
            getattr(pygame_locals, key_name)
            for key_name in key_names
        )

    )

    for key, key_names in data['pressed_keys_map'].items()

}

EMPTY_GETTER_FROZENSET = GetterFrozenSet()

### mod key states

NO_KMOD_NONE_BITMASKS = {

    frame_index : (

        ##
        getattr(pygame_locals, mod_key_names[0])
        if len(mod_key_names) == 1

        ##
        else get_resulting_bitmask(mod_key_names)

    )

    for frame_index, mod_key_names
    in data['mod_key_bitmasks_map'].items()
}

MOUSE_POSITIONS = list(data['mouse_pos_requests'])
MOUSE_POSITIONS.reverse()

MOUSE_PRESSED_TUPLES = list(data['mouse_key_state_requests'])
MOUSE_PRESSED_TUPLES.reverse()


## constants


## label

render_label_text = Font(None, 24).render

def get_label(label_fg, label_bg, label_outline, padding):

    label_text = (
        render_label_text(
            "F9: pause + regain control of mouse", True, label_fg, label_bg
        )
    )

    label = Surface(label_text.get_rect().inflate(padding*2, padding*2).size).convert()
    label.fill(label_outline)
    draw_rect(label, label_bg, label.get_rect().inflate(-2, -2))

    label.blit(label_text, (padding, padding))

    return label

label = (
    get_label(
        label_fg = 'white',
        label_bg = 'blue',
        label_outline = 'white',
        padding=6,
    )
)

label_rect = label.get_rect()

label_rect.topright = SCREEN_RECT.move(-10, 40).topright
##


def setup_playing_mode():

    ### set frame index to 0
    PLAY_REFS.frame_index = 0

    ### set frame index setup as the frame index routine
    PLAY_REFS.frame_index_routine = perform_frame_index_setups

### set playing mode setup as the frame index routine
PLAY_REFS.frame_index_routine = setup_playing_mode


def perform_frame_index_setups():
    ### increment frame index by 1
    PLAY_REFS.frame_index += 1

    ### act according to whether frame is last one

    if PLAY_REFS.frame_index == PLAY_REFS.last_frame_index:

        quit_pygame()
        quit()



### session behaviours

## processing events

MOUSE_EVENTS = MOUSEMOTION, MOUSEBUTTONDOWN, MOUSEBUTTONUP

def get_events():

    for event in get():

        if event.type == QUIT:
            print("Tried quitting")

        elif event.type == KEYDOWN and event.key == K_F9:
            print("Pressed F9")

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

