
### standard library imports

from collections import defaultdict

from datetime import datetime


### third-party imports

from pygame import locals as pygame_locals

from pygame.locals import (
    KEYDOWN,
    KEYUP,
    K_F7,
    K_F8,
    K_F9,
    KMOD_NONE,
)

from pygame.color import THECOLORS

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

from pygame.display import set_mode, update


### local imports

from ...ourstdlibs.datetimeutils import get_timestamp

from ...ourstdlibs.pyl import save_pyl

from ...loopman.exception import ResetAppException

from ...classes2d.single import Object2D

from ...textman.render import render_text

from ..constants import (

    SCREEN_RECT, blit_on_screen,
    GENERAL_NS,
    GENERAL_SERVICE_NAMES,
    FPS, maintain_fps,

    CancelWhenPaused, pause,

    watch_window_size,

    EVENT_KEY_STRIP_MAP,
    EVENT_COMPACT_NAME_MAP,
    EVENT_KEY_COMPACT_NAME_MAP,
    KEYS_MAP,
    SCANCODE_NAMES_MAP,
    MOD_KEYS_MAP,

)



### control and data-recording objects


## constants

## namespace
REC_REFS = type("Object", (), {})()


EVENTS_MAP = defaultdict(list)

KEY_STATE_REQUESTS = []
append_key_states = KEY_STATE_REQUESTS.append

MOD_KEY_BITMASK_REQUESTS = []
append_mod_key_states = MOD_KEY_BITMASK_REQUESTS.append

MOUSE_POS_REQUESTS = []
append_mouse_pos_request = MOUSE_POS_REQUESTS.append

MOUSE_KEY_STATE_REQUESTS = []
append_mouse_key_state_request = MOUSE_KEY_STATE_REQUESTS.append

## reverse keys map

REVERSE_KEYS_MAP = {
    value: key
    for key, value in KEYS_MAP.items()
}


## create labels objects

LABELS = [

    Object2D.from_surface(
        render_text(
            text=text,
            foreground_color = THECOLORS['white'],
            background_color = THECOLORS['blue'],
            border_color = THECOLORS['white'],
            border_thickness = 2,
            padding = 6,
        )
    )

    for text in (
        "F7: cancel recording",
        "F8: play/pause",
        "F9: finish recording & exit",
    )
]

PAUSED_LABEL = (

    Object2D.from_surface(
        render_text(
            text = "F8: play/pause",
            foreground_color = THECOLORS['white'],
            background_color = THECOLORS['red3'],
            border_color = THECOLORS['white'],
            border_thickness = 2,
            padding = 6,
        )
    )
)


### events to keep in the recorded data;
###
### all other events aren't relevant because it is not possible for
### them to show up in recorded sessions (like video resizing events
### or QUIT) or simply because they are not used in the app, so we
### do not care to record them;
###
### this set must be updated whenever the app starts using other
### events not listed here (for instance, for new features)

NAMES_OF_EVENTS_TO_KEEP = frozenset((
    'KEYDOWN',
    'KEYUP',
    'MOUSEBUTTONDOWN',
    'MOUSEBUTTONUP',
    'MOUSEMOTION',
    'TEXTINPUT',
))


###

def set_behaviour(services_namespace, data):
    """Setup record services and data."""

    ### set record services as current ones.

    our_globals = globals()

    for attr_name in GENERAL_SERVICE_NAMES:

        value = our_globals[attr_name]
        setattr(services_namespace, attr_name, value)

    ### store recording path and recording size

    for attr_name in (
        'recording_title',
        'recording_path',
        'recording_size',
    ):

        value = getattr(data, attr_name)
        setattr(REC_REFS, attr_name, value)

    ### reset window mode (pygame.display.set_mode)
    set_mode(data.recording_size, 0)

    ### trigger setups related to window size change
    watch_window_size()

    ### create and store title label, then reposition
    ### all labels

    new_title_label = (
        Object2D.from_surface(
            render_text(
                text = data.recording_title,
                foreground_color = THECOLORS['white'],
                background_color = THECOLORS['blue'],
                border_color = THECOLORS['white'],
                border_thickness = 2,
                padding = 6,
            )
        )
    )

    LABELS.insert(0, new_title_label)

    topright = SCREEN_RECT.move(-10, 32).topright

    for label in LABELS:

        label.rect.topright = topright
        topright = label.rect.move(0, 5).bottomright

    ### ensure paused label has same position as the second one
    PAUSED_LABEL.rect.topleft = LABELS[2].rect.topleft

    ## clear any existing events
    clear()

    ## record beginning of recording session
    REC_REFS.session_start_datetime = datetime.now()

    ## set frame index to -1 (so it is set to 0 at the beginning
    ## of the loop, the first frame)
    GENERAL_NS.frame_index = -1


### extended session behaviours

## processing events

def get_events():

    ### handle/yield events;
    ###
    ### note that we do not handle the QUIT event here; rather,
    ### it is handled by whichever object receives the yielded
    ### event;
    ###
    ### it will usually cause a QuitAppException to be raised,
    ### which causes the app to close immediately when in record
    ### mode (in play mode as well)

    for event in get():

        if event.type == KEYDOWN:

            if event.key == K_F8:

                ### indicate pause by blitting paused label
                blit_on_screen(PAUSED_LABEL.image, PAUSED_LABEL.rect)

                ### pause

                try:
                    pause()

                ### if during pause user asks to cancel recording, do
                ### it here

                except CancelWhenPaused:
                    cancel_recording()

                ### pressing F8 is part of the session recording,
                ### not the session per se, so we skip the event
                ### in order to prevent it to be recorded
                continue

            elif event.key == K_F9:

                ### save session data
                save_session_data()

                ### clear stored data
                clear_data()

                ### reset app;
                ###
                ### since this stops recording completely there's
                ### no need to use the "continue" statement as we
                ### did for the F8 key in the if-block above
                raise ResetAppException(mode='normal')

            ### cancel recording

            elif event.key == K_F7:
                cancel_recording()

        ### pressing F8 is part of the session recording,
        ### not the session per se, so we skip the event
        ### in order to prevent it from being recorded;
        ###
        ### this also applies to F9, but during the KEYDOWN event
        ### of the F9 key, the recording stops altogether due to the
        ### raised exception, so it isn't necessary to watch for it
        elif event.type == KEYUP and event.key == K_F8:
            continue

        ### record event

        EVENTS_MAP[GENERAL_NS.frame_index].append([
            event.type,
            event.__dict__
        ])

        ### yield it
        yield event

## processing key pressed states

def get_pressed_keys():

    # get key states
    key_states = get_pressed()

    # record them
    append_key_states((GENERAL_NS.frame_index, key_states))

    # return them
    return key_states

def get_pressed_mod_keys():
    # get mod bistmask
    mods_bitmask = get_mods()

    # record it
    append_mod_key_states((GENERAL_NS.frame_index, mods_bitmask))

    # return it
    return mods_bitmask

## processing mouse

def get_mouse_pos():
    # get mouse pos
    pos = get_pos()

    # record it
    append_mouse_pos_request(pos)

    # return it
    return pos

def get_mouse_pressed():
    # get mouse pressed tuple
    pressed_tuple = mouse_get_pressed()

    # record it
    append_mouse_key_state_request.append(pressed_tuple)

    # return it
    return pressed_tuple

## screen updating

def update_screen():

    ### blit labels

    for label in LABELS:
        blit_on_screen(label.image, label.rect)

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

    ### increment frame number
    GENERAL_NS.frame_index += 1

def frame_checkups_with_fps(fps):
    """Same as frame_checkups(), but uses given fps."""
    ### keep constants fps
    maintain_fps(fps)

    ### increment frame number
    GENERAL_NS.frame_index += 1


### session data saving operations

def save_session_data():

    session_data = {}

    ### process event map

    ## create

    events_map = session_data['events_map'] = {

        frame_index : list(yield_treated_events(events))
        for frame_index, events in EVENTS_MAP.items()

    }

    ## remove keys whose values (a list of events) ended up empty,
    ## (if there)

    keys_to_pop = [
        # item
        key
        # source
        for key, event_list in events_map.items()
        # filtering condition
        if not event_list
    ]

    for key in keys_to_pop:
        events_map.pop(key)

    ### store data

    session_data['key_name_to_frames_map'] = (
        get_key_to_frames_map(KEY_STATE_REQUESTS)
    )

    session_data['mod_key_name_to_frames_map'] = (
        get_mod_key_to_frames_map(MOD_KEY_BITMASK_REQUESTS)
    )

    session_data['mouse_pos_requests'] = tuple(MOUSE_POS_REQUESTS)

    session_data['mouse_key_state_requests'] = tuple(MOUSE_KEY_STATE_REQUESTS)

    ### store last frame index as well
    session_data['last_frame_index'] = GENERAL_NS.frame_index + 1

    ### store recording size and title

    session_data['recording_size'] = REC_REFS.recording_size

    session_data['recording_title'] = REC_REFS.recording_title

    ### save session data in file or its rotated version

    parent, stem = (
        getattr(REC_REFS.recording_path, attr_name)
        for attr_name in ('parent', 'stem')
    )

    timestamp = get_timestamp(REC_REFS.session_start_datetime)

    final_path = parent / f"{stem}.{timestamp}.pyl"
    save_pyl(session_data, final_path, width=125, compact=True)

    ### clear collections created in this function (not really needed,
    ### but in our experience memory is freed faster when collections
    ### are cleared)

    events_map.clear()
    session_data.clear()

def cancel_recording():

    clear_data()
    raise ResetAppException(mode='normal')

def clear_data():

    ### clear collections

    for a_collection in (

        EVENTS_MAP,
        KEY_STATE_REQUESTS,
        MOD_KEY_BITMASK_REQUESTS,

        MOUSE_POS_REQUESTS,
        MOUSE_KEY_STATE_REQUESTS,

    ):
        a_collection.clear()

    ### remove title label
    del LABELS[0]

def yield_treated_events(events_type_and_dict_pairs):

    yield from (

        yield_compact_events(
            yield_named_keys_and_mod_keys(
                yield_events_to_keep(
                    yield_named_events(
                        events_type_and_dict_pairs
                    )
                )
            )
        )

    )


def yield_named_events(events_type_and_dict_pairs):

    for event_type, event_dict in events_type_and_dict_pairs:
    
        yield (
            event_name(event_type).upper(),
            event_dict
        )

def yield_events_to_keep(events_name_and_dict):
    """Only yield events we are interested in recording."""
    for name_and_dict in events_name_and_dict:
        if name_and_dict[0] in NAMES_OF_EVENTS_TO_KEEP:
            yield name_and_dict

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
        event_dict['mod'] = get_mod_key_names_tuple(bitmask)

    return event_dict

def yield_compact_events(events):

    for name, a_dict in events:

        yield [

            ## use a compact name if there's one
            EVENT_COMPACT_NAME_MAP.get(name, name),

            ## use the dict after changing it to be more compact
            get_compact_event_dict(name, a_dict),

        ]

def get_compact_event_dict(name, a_dict):

    ### strip keys with the most common values;
    ###
    ### since they are so common, removing them saves a lot of space;
    ###
    ### this doesn't cause loss of info, because since we know which
    ### values we are stripping, we just put them back when we are
    ### about to play the session in the session playing mode;

    if name in EVENT_KEY_STRIP_MAP:

        map_of_values_to_strip = EVENT_KEY_STRIP_MAP[name]

        for key, value in map_of_values_to_strip.items():
            
            if key in a_dict and a_dict[key] == value:
                a_dict.pop(key)

    ### replace some keys with compact versions of their names
    ###
    ### since they are so common, the extra characters removed by
    ### using a more compact name saves a lot of space;
    ###
    ### again, this doesn't cause loss of info, because since we know
    ### which keys we are making compact, we just invert the operation
    ### when we are about to play the session in the session playing
    ### mode;

    if name in EVENT_KEY_COMPACT_NAME_MAP:

        map_of_keys_to_make_compact = EVENT_KEY_COMPACT_NAME_MAP[name]

        for key, compact_key in map_of_keys_to_make_compact.items():
            
            if key in a_dict:
                a_dict[compact_key] = a_dict.pop(key)

    ### return the dict
    return a_dict


def get_key_to_frames_map(time_obj_pairs):

    ### this format is okay, but it can be more compact

    frame_to_key_names_map = {
        
        item[0]: item[1]

        for item in (

            (

                ## item 0
                frame_index,

                ## item 1
                tuple(
                    key_name # item
                    for key_name, key in KEYS_MAP.items() # source
                    if wrapper[key] # filtering condition
                )


            )

            for frame_index, wrapper in time_obj_pairs

        )

        if item[1]

    }

    ### the format below, the one we actually return, is used
    ### because it is more compact

    key_name_to_frames_map = defaultdict(list)

    for frame, key_names in frame_to_key_names_map.items():

        for key_name in key_names:
            key_name_to_frames_map[key_name].append(frame)

    ###
    return dict(key_name_to_frames_map)

def get_mod_key_to_frames_map(frame_bitmask_pairs):

    ### this format is okay, but it can be more compact

    frame_to_mod_key_names_map = {
        frame_index: mod_key_names
        for frame_index, mod_key_names
        in yield_frame_and_mod_keys_names(frame_bitmask_pairs)
    }

    ### the format below, the one we actually return, is used
    ### because it is more compact

    mod_key_name_to_frames_map = defaultdict(list)

    for frame, mod_key_names in frame_to_mod_key_names_map.items():

        for key in mod_key_names:
            mod_key_name_to_frames_map[key].append(frame)

    ###
    return dict(mod_key_name_to_frames_map)


def yield_frame_and_mod_keys_names(frame_bitmask_pairs):

    for frame_index, bitmask in frame_bitmask_pairs:

        if bitmask != KMOD_NONE:

            yield (
                frame_index,
                get_mod_key_names_tuple(bitmask),
            )


def get_mod_key_names_tuple(bitmask):

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
