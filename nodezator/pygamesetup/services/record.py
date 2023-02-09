
### standard library imports

from collections import defaultdict

from datetime import datetime


### third-party imports

from pygame.locals import (
    KEYUP,
    K_F9,
    KMOD_NONE,
)

from pygame.event import clear, get, event_name

from pygame.key import get_pressed, get_mods

from pygame.mouse import (

    get_pos,
    get_pressed as mouse_get_pressed,

    # check note [1] at the bottom
    set_pos as set_mouse_pos,

    # check note [2] at the bottom
    set_visible as set_mouse_visibility,
)

from pygame.display import update


### local imports

from ...config import APP_REFS

from ...ourstdlibs.path import get_timestamp

from ...ourstdlibs.pyl import save_pyl

from ...loopman.exception import ResetAppException

from ..constants import (

    SCREEN_RECT, blit_on_screen,
    FPS, maintain_fps,

    EVENT_KEY_STRIP_MAP,
    EVENT_COMPACT_NAME_MAP,
    KEYS_MAP,
    SCANCODE_NAMES_MAP,
    MOD_KEYS_MAP,

    get_label_object,

)



### control and data-recording objects


## constants

## namespace
REC_REFS = type("Object", (), {})()


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

# create labels, their rects, and position them

LABELS = []

def instantiate_and_store_labels():

    topright = SCREEN_RECT.move(-10, 32).topright

    for text in (
        getattr(APP_REFS, "recording_title", "Untitled session"),
        "F9: finish recording & exit",
    ):

        ### create label object

        label = (
            get_label_object(
                text = text,
                label_fg = 'white',
                label_bg = 'blue',
                label_outline = 'white',
                padding = 6,
            )
        )

        ### position label
        label.rect.topright = topright

        ### store label
        LABELS.append(label)

        ### update topright
        topright = label.rect.move(0, 5).bottomright

instantiate_and_store_labels()


def set_recording_behaviour(recording_path, recording_size):

    ### store recording path and recording size

    REC_REFS.recording_path = recording_path
    REC_REFS.recording_size = recording_size

    ### make it so the frame index routine sets up recording
    REC_REFS.frame_index_routine = setup_recording


### set behaviors to record session data

def setup_recording():

    ## clear any existing events
    clear()

    ## record beginning of recording session
    REC_REFS.session_start_datetime = datetime.now()

    ## set frame index to 0
    REC_REFS.frame_index = 0

    ## set frame index incrementation as the frame index routine
    REC_REFS.frame_index_routine = increment_frame_index


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

            ### save session data
            save_session_data()

            ### reset app
            raise ResetAppException


        record_event(event)
        yield event

## processing key pressed states

def get_pressed_keys():
    state = get_pressed()
    record_key_states(state)
    return state

def get_pressed_mod_keys():
    mods_bitmask = get_mods()
    REC_REFS.record_mod_key_states(mods_bitmask)
    return mods_bitmask

## processing mouse

def get_mouse_pos():
    pos = get_pos()
    MOUSE_POS_REQUESTS.append(pos)
    return pos
def get_mouse_pressed():
    pressed_tuple = mouse_get_pressed()
    MOUSE_KEY_STATE_REQUESTS.append(pressed_tuple)
    return pressed_tuple

## screen updating

def update_screen():
    ### blit label
    blit_on_screen(label, label_rect)

    ### update the screen (pygame.display.update())
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

    ### store recording size and title

    session_data['recording_size'] = REC_REFS.recording_size

    session_data['recording_title'] = (
        getattr(APP_REFS, "recording_title", "Untitled session")
    )

    ### save session data in file or its rotated version

    parent, stem = (
        getattr(REC_REFS.recording_path, attr_name)
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



### Notes
###
### [1] note that pygame.mouse.set_pos() (aliased as set_mouse_pos())
### is not changed (overridden or extended) anywhere in this module;
### this is so because it is used as-is, we just import it so it is
### available in this module namespace;
###
### [2] read note [1] above; the same is applies to
### pygame.mouse.set_visible, which here is aliased as
### set_mouse_visibility()
