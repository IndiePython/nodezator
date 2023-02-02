
### standard library imports

from pathlib import Path

from types import SimpleNamespace

from collections import defaultdict

from itertools import cycle, repeat

from datetime import datetime


### third-party imports

from pygame import (
    KEYUP,
    K_F9,
    KMOD_NONE,
    Rect,
    Surface,
)

from pygame.event import get, event_name

from pygame.key import get_pressed, get_mods

from pygame.mouse import (
    get_pos,
    get_pressed as mouse_get_pressed,
    set_pos as set_mouse_pos,
    set_visible as set_mouse_visibility,
)

from pygame.display import set_mode, update

from pygame.font import Font

from pygame.draw import (
    rect as draw_rect,
    ellipse as draw_ellipse,
    line as draw_line,
)


### local imports

from ..config import APP_REFS

from ..ourstdlibs.behaviour import (
    empty_oblivious_function,
    empty_function,
)

from ..ourstdlibs.path import get_timestamp

from ..ourstdlibs.pyl import save_pyl

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



### control and data-recording objects


## constants

REC_REFS = SimpleNamespace()


EVENTS_MAP = defaultdict(list)

KEY_STATE_REQUESTS = []
MOD_KEY_BITMASK_REQUESTS = []

MOUSE_POS_REQUESTS = []
MOUSE_KEY_STATE_REQUESTS = []

## reverse keys map

REVERSE_KEYS_MAP = {
    value: key
    for key, value in KEYS_MAP.items()
}

## label

render_label_text = Font(None, 24).render

def get_label(label_fg, label_bg, label_outline, padding):

    label_text = (
        render_label_text(
            "F9: toggle recording", True, label_fg, label_bg
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
        label_bg = 'black',
        label_outline = 'white',
        padding=6,
    )
)

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
    repeat(rec_indicator_turned_off_surf).__next__
)

##
label_rect.topright = SCREEN_RECT.move(-10, 40).topright
rec_indicator_rect.topright = label_rect.move(0, 5).bottomright
##

def set_behaviors_to_ignore_session_data():

    ### make it so session data is ignored

    for attr_name in (
        'process_event',
        'process_key_state',
        'process_mod_key_state',
        'process_mouse_pos',
        'process_mouse_key_state',
    ):
        setattr(REC_REFS, attr_name, empty_oblivious_function)

    ### ensure this is shown in the indicator
    REC_REFS.next_indicator_surf = get_recording_turned_off_surfs

    ### set an empty function as the frame index routine
    REC_REFS.frame_index_routine = empty_function

set_behaviors_to_ignore_session_data()

### utility functions

def toggle_recording():

    if REC_REFS.process_event is empty_oblivious_function:
        
        ### record beginning of recording session
        REC_REFS.session_start_datetime = datetime.now()

        ### set frame index to 0
        REC_REFS.frame_index = 0

        ### set frame index incrementation as the frame index routine
        REC_REFS.frame_index_routine = increment_frame_index

        ### make it so session data is recorded

        for attr_name, recording_operation in (
            ('process_event', record_event),
            ('process_key_state', record_key_states),
            ('process_mod_key_state', record_mod_key_states),
            ('process_mouse_pos', MOUSE_POS_REQUESTS.append),
            ('process_mouse_key_state', MOUSE_KEY_STATE_REQUESTS.append),
        ):
            setattr(REC_REFS, attr_name, recording_operation)

        ###
        REC_REFS.next_indicator_surf = get_recording_turned_on_surfs

    else:

        ### save recorded session data
        save_session_data()

        ### make it so session data is ignored
        set_behaviors_to_ignore_session_data()

def increment_frame_index():
    """increment frame index by 1"""
    REC_REFS.frame_index += 1


### event recording operation

def record_event(event):

    EVENTS_MAP[REC_REFS.frame_index].append([
        event.type,
        event.__dict__
    ])

append_key_states = KEY_STATE_REQUESTS.append
def record_key_states(key_states):
    append_key_states((REC_REFS.frame_index, key_states))

append_mod_key_states = MOD_KEY_BITMASK_REQUESTS.append
def record_mod_key_states(mods_bitmask):
    append_mod_key_states((REC_REFS.frame_index, mods_bitmask))

### extended session behaviours

## processing events

def get_events():

    for event in get():

        if event.type == KEYUP and event.key == K_F9:

            ### set toggle recording as the frame index routine;
            ###
            ### this will cause the recording state to be toggled
            ### (either turned on or off) at the very beginning of
            ### the next frame
            REC_REFS.frame_index_routine = toggle_recording

        else:

            REC_REFS.process_event(event)
            yield event

## processing key pressed states

def get_pressed_keys():
    state = get_pressed()
    REC_REFS.process_key_state(state)
    return state

def get_pressed_mod_keys():
    mods_bitmask = get_mods()
    REC_REFS.process_mod_key_state(mods_bitmask)
    return mods_bitmask

## processing mouse

def get_mouse_pos():
    pos = get_pos()
    REC_REFS.process_mouse_pos(pos)
    return pos

def get_mouse_pressed():
    pressed_tuple = mouse_get_pressed()
    REC_REFS.process_mouse_key_state(pressed_tuple)
    return pressed_tuple


## screen updating

def update_screen():
    ###
    blit_on_screen(REC_REFS.next_indicator_surf(), rec_indicator_rect)
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
    REC_REFS.frame_index_routine()

def frame_checkups_with_fps(fps):
    """Same as frame_checkups(), but uses given fps."""
    ### keep constants fps
    maintain_fps(fps)

    ### execute frame index routine
    REC_REFS.frame_index_routine()


### session data saving operations

def save_session_data():

    session_data = {}

    ### process event map

    session_data['events_map'] = {
        frame_index : list(yield_treated_events(events))
        for frame_index, events in EVENTS_MAP.items()
    }

    ### store data

    session_data['pressed_keys_map'] = (
        get_pressed_keys_map(KEY_STATE_REQUESTS)
    )

    session_data['mod_key_bitmasks_map'] = {
        frame_index: treated_bitmask
        for frame_index, treated_bitmask
        in yield_filtered_frame_bitmask_pairs(MOD_KEY_BITMASK_REQUESTS)
    }

    session_data['mouse_pos_requests'] = tuple(MOUSE_POS_REQUESTS)

    session_data['mouse_key_state_requests'] = tuple(MOUSE_KEY_STATE_REQUESTS)

    ### store last frame index as well
    session_data['last_frame_index'] = REC_REFS.frame_index + 1

    ### save session data in file or its rotated version

    rec_path = APP_REFS.recording_path

    parent, stem = (
        getattr(rec_path, attr_name)
        for attr_name in ('parent', 'stem')
    )

    timestamp = get_timestamp(REC_REFS.session_start_datetime)

    final_path = parent / f"{stem}_{timestamp}.pyl"
    save_pyl(session_data, final_path, width=125, compact=True)

    ### clear collections

    for a_collection in (

        EVENTS_MAP,
        KEY_STATE_REQUESTS,
        MOD_KEY_BITMASK_REQUESTS,

        MOUSE_POS_REQUESTS,
        MOUSE_KEY_STATE_REQUESTS,

    ):
        a_collection.clear()

    ### clear other collections (not really needed, but in our
    ### experience memory is freed faster when collections are
    ### cleared
    session_data['events_map'].clear()

    session_data.clear()


def yield_treated_events(type_data_pairs):

    yield from (
        yield_compact_events(
            yield_named_keys_and_mod_keys(
                yield_known_events(
                    yield_named_events(type_data_pairs)
                )
            )
        )
    )


def yield_named_events(events):

    for event_type, event_dict in events:
    
        yield (
            event_name(event_type).upper(),
            event_dict
        )

def yield_known_events(events):
    for event in events:
        if event[0] != 'UNKNOWN':
            yield event

def yield_named_keys_and_mod_keys(events):

    for item in events:

        yield (

            item
            if item[0] not in ('KEYUP', 'KEYDOWN')

            else ( item[0], get_treated_key_event_dict(item[1]) )

        )

def get_treated_key_event_dict(event_dict):

    for key, get_treated in (

        ('key', REVERSE_KEYS_MAP.__getitem__),
        ('scancode', SCANCODE_NAMES_MAP.__getitem__),

    ):
        event_dict[key] = get_treated(event_dict[key])

    ## if mod != KMOD_NONE, process it

    bitmask = event_dict['mod']

    if bitmask != KMOD_NONE:
        event_dict['mod'] = get_mod_names_tuple(bitmask)

    return event_dict

def yield_compact_events(events):

    for name, a_dict in events:

        yield [

            EVENT_COMPACT_NAME_MAP.get(name, name),

            (
                a_dict
                if name not in EVENT_KEY_STRIP_MAP

                else get_compact_event_dict(EVENT_KEY_STRIP_MAP[name], a_dict)

            )

        ]

def get_compact_event_dict(map_of_values_to_strip, a_dict):

    return {

        key: value

        for key, value in a_dict.items()

        if (

            key not in map_of_values_to_strip

            or (
                key in map_of_values_to_strip
                and value != map_of_values_to_strip[key]
            )

        )
    }

def get_pressed_keys_map(time_obj_pairs):

    return {
        
        item[0]: item[1]

        for item in (

            (

                frame_index,
                tuple(key_name for key_name, key in KEYS_MAP.items() if wrapper[key])


            )

            for frame_index, wrapper in time_obj_pairs

        )

        if item[1]

    }

def yield_filtered_frame_bitmask_pairs(frame_bitmask_pairs):

    for frame_index, bitmask in frame_bitmask_pairs:

        if bitmask != KMOD_NONE:

            yield (
                frame_index,
                get_mod_names_tuple(bitmask),
            )


def get_mod_names_tuple(bitmask):

    return tuple(
        mod_key_name
        for mod_key_name, mod_key in MOD_KEYS_MAP.items()
        if bitmask & mod_key
    )
