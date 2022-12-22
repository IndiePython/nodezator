
### standard library imports

from pathlib import Path

from types import SimpleNamespace

from collections import defaultdict

from itertools import cycle

from datetime import datetime


### third-party imports

from pygame import (
    KEYUP,
    K_F9,
    Rect,
    Surface,
)

from pygame.event import (
    get,
    event_name,
)

from pygame.key import (
    get_pressed,
    get_mods,
)

from pygame.mouse import (
    get_pos,
    get_pressed as mouse_get_pressed,
    set_pos,
    set_visible,
)

from pygame.display import (
    update,
    get_surface,
)

from pygame.font import Font

from pygame.draw import (
    rect as draw_rect,
    ellipse as draw_ellipse,
    line as draw_line,
)

from pygame.time import get_ticks as get_msecs


### local imports

from ..config import APP_REFS

from ..ourstdlibs.behaviour import empty_oblivious_function

from ..ourstdlibs.path import get_timestamp

from ..ourstdlibs.pyl import save_pyl


### set import constants/module-level objects here

screen = get_surface()
blit_on_screen = screen.blit
screen_rect = screen.get_rect()

REC_REFS = SimpleNamespace()


EVENTS_MAP = defaultdict(list)

KEY_STATE_REQUESTS = []
MOD_KEY_BITMASK_REQUEST = []

MOUSE_POS_REQUESTS = []
MOUSE_KEY_STATE_REQUESTS = []

MOUSE_POS_SETUPS = []
MOUSE_VISIBILITY_SETUPS = []


## label

label_text = (
    Font(None, 24).render('F9: toggle recording', True, 'white', 'black')
)

label = Surface(label_text.get_rect().inflate(4, 4).size).convert()
label.fill('white')
draw_rect(label, 'black', label.get_rect().inflate(-2, -2))

label.blit(label_text, (2, 2))
label_rect = label.get_rect()

## recording indicator

rec_text = Font(None, 28).render('rec', True, 'white', 'black')

w, h = rec_text.get_size()

h += 4
w += h

rec_indicator_rect = Rect(0, 0, w, h)

rec_indicator_base_surf = Surface(rec_indicator_rect.size).convert()
rec_indicator_base_surf.fill('white')

draw_rect(
    rec_indicator_base_surf,
    'black',
    rec_indicator_rect.inflate(-2, -2),
)

rec_indicator_base_surf.blit(rec_text, (2, 1))
rec_indicator_turned_on_surf = rec_indicator_base_surf.copy()

red_circle = Font(None, 70).render('\N{bullet}', True, 'red')
red_circle = red_circle.subsurface(red_circle.get_bounding_rect())

rec_indicator_turned_on_surf.blit(red_circle, (w - 18, 5))

get_recording_turned_on_surfs = (
    cycle(
        (rec_indicator_base_surf,) * 20
        + (rec_indicator_turned_on_surf,) * 20
    ).__next__
)

#

rec_indicator_turned_off_surf = rec_indicator_base_surf.copy()

ellipse_rect = Rect(0, 0, h-8, h-8)
ellipse_rect.topright = rec_indicator_rect.move(-3, 4).topright

draw_ellipse(
    rec_indicator_turned_off_surf,
    'red',
    ellipse_rect,
    2,
)

small_ellipse_rect = ellipse_rect.inflate(-6, -6).move(-1, 0)

draw_line(
    rec_indicator_turned_off_surf,
    'red',
    small_ellipse_rect.topright,
    small_ellipse_rect.bottomleft,
    2,
)

get_recording_turned_off_surfs = (
    cycle(
        (rec_indicator_base_surf,) * 20
        + (rec_indicator_turned_off_surf,) * 20
    ).__next__
)

##
rec_indicator_rect.topright = screen_rect.move(-10, 40).topright
label_rect.topright = rec_indicator_rect.move(0, 5).bottomright
##

###
REC_REFS.next_indicator_surf = get_recording_turned_off_surfs

### utility functions

def toggle_recording():

    if REC_REFS.process_event is empty_oblivious_function:
        
        ### record beginning of recording session
        REC_REFS.session_start_datetime = datetime.now()

        ### make it so session data is recorded

        for attr_name, recording_operation in (
            ('process_event', record_event),
            ('process_key_state', record_key_state),
            ('process_mod_key_state', record_mod_key_state),
            ('process_mouse_pos', record_mouse_pos),
            ('process_mouse_key_state', record_mouse_key_state),
            ('process_mouse_pos_setup', record_mouse_pos_setup),
            ('process_mouse_visibility_setup', record_mouse_visibility_setup),
        ):
            setattr(REC_REFS, attr_name, recording_operation)

        ###
        REC_REFS.next_indicator_surf = get_recording_turned_on_surfs

    else:

        ### save recorded session
        save_recorded_session()

        ### make it so session data is ignored

        for attr_name in (
            'process_event',
            'process_key_state',
            'process_mod_key_state',
            'process_mouse_pos',
            'process_mouse_key_state',
            'process_mouse_pos_setup',
            'process_mouse_visibility_setup',
        ):
            setattr(REC_REFS, attr_name, empty_oblivious_function)

        ###
        REC_REFS.next_indicator_surf = get_recording_turned_off_surfs

### events

def record_event(event):

    EVENTS_MAP[REC_REFS.event_msecs].append([
        event_name(event.type).upper(),
        event.__dict__
    ])

REC_REFS.process_event = empty_oblivious_function


### key requests

record_key_state = KEY_STATE_REQUESTS.append
record_mod_key_state = MOD_KEY_BITMASK_REQUEST.append

### mouse requests/setups

record_mouse_pos = MOUSE_POS_REQUESTS.append
record_mouse_key_state = MOUSE_KEY_STATE_REQUESTS.append

record_mouse_pos_setup = MOUSE_POS_SETUPS.append
record_mouse_visibility_setup = MOUSE_VISIBILITY_SETUPS.append

###

def save_recorded_session():
    
    session_data = {}

    ### events map

    ## process

    if EVENTS_MAP:

        first_msecs = min(EVENTS_MAP.keys())

        session_data['events_map'] = {
            a_time - first_msecs: events
            for a_time, events in EVENTS_MAP.items()
        }

    ## clear
    EVENTS_MAP.clear()

    ### store lists

    session_data['key_state_requests'] = KEY_STATE_REQUESTS
    session_data['mod_key_bitmask_request'] = MOD_KEY_BITMASK_REQUEST

    session_data['mouse_pos_requests'] = MOUSE_POS_REQUESTS
    session_data['mouse_key_state_requests'] = MOUSE_KEY_STATE_REQUESTS

    session_data['mouse_pos_setups'] = MOUSE_POS_SETUPS
    session_data['mouse_visibility_setups'] = MOUSE_VISIBILITY_SETUPS

    ### save session data in file or its rotated version

    rec_path = APP_REFS.recording_path

    parent, stem, suffix = (
        getattr(rec_path, attr_name)
        for attr_name in ('parent', 'stem', 'suffix')
    )

    timestamp = get_timestamp(REC_REFS.session_start_datetime)

    final_path = parent / f"{stem}_{timestamp}{suffix}"

    save_pyl(session_data, final_path)

    ### clear stuff

    for a_list in (
        KEY_STATE_REQUESTS,
        MOD_KEY_BITMASK_REQUEST,

        MOUSE_POS_REQUESTS,
        MOUSE_KEY_STATE_REQUESTS,

        MOUSE_POS_SETUPS,
        MOUSE_VISIBILITY_SETUPS,
    ):
        a_list.clear()

    ### clear other collections (not really needed, but in our
    ### experience memory is freed faster when collections are
    ### cleared

    if 'events_map' in session_data:
        session_data['events_map'].clear()

    session_data.clear()


### processing events

def get_events():

    REC_REFS.event_msecs = get_msecs()

    for event in get():

        if event.type == KEYUP and event.key == K_F9:
            toggle_recording()

        else:
            REC_REFS.process_event(event)
            yield event

### processing key pressed states

def get_pressed_keys():
    state = get_pressed()
    REC_REFS.process_key_state(state)
    return state

def get_pressed_mod_keys():
    return get_mods()


### processing mouse states

def get_mouse_pos():
    return get_pos()

def get_mouse_pressed():
    return mouse_get_pressed()

def set_mouse_pos(pos):
    set_pos(pos)

def set_mouse_visibility(boolean):
    set_visible(boolean)

def update_screen():
    ###
    blit_on_screen(REC_REFS.next_indicator_surf(), rec_indicator_rect)
    blit_on_screen(label, label_rect)

    ### update the screen
    update()


### store needed behaviors in a custom namespace 

recording_ns = SimpleNamespace(

    get_events = get_events,

    get_pressed_keys = get_pressed_keys,
    get_pressed_mod_keys = get_pressed_mod_keys,

    get_mouse_pos = get_mouse_pos,
    get_mouse_pressed = get_mouse_pressed,

    set_mouse_pos = set_mouse_pos,
    set_mouse_visibility = set_mouse_visibility,

    update_screen = update_screen,

)
