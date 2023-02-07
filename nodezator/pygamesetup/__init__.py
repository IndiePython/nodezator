"""App constants."""

### third-party imports

from pygame import init as init_pygame

#


from pygame.key import set_repeat

from pygame.display import set_icon, set_caption

from pygame.image import load as load_image

from pygame.mixer import pre_init as pre_init_mixer


### local imports

from ..appinfo import FULL_TITLE, ABBREVIATED_TITLE

from ..config import APP_REFS, DATA_DIR


### pygame initialization setups

## pygame mixer pre-initialization
pre_init_mixer(44100, -16, 2, 4096)

## pygame initialization
init_pygame()


### post-initialization local import
from .constants import clean_temp_files



### set caption and icon for window

set_caption(FULL_TITLE, ABBREVIATED_TITLE)

image_path = str(DATA_DIR / "app_icon.png")

set_icon(load_image(image_path))


### set key repeating (unit: milliseconds)

set_repeat(
    500, # delay (time before repetition begins)
    30, # interval (interval between repetitions)
)


### overridable constants/behavior;
###
### you can import values/objects/behaviours below from different
### modules to change the app's behavior;


## if a recording path was given, we import values and behaviors
## so app is launched in recording mode

if APP_REFS.recording_path:

    from .recording import (

        SCREEN,
        SCREEN_RECT,
        blit_on_screen,

        get_events,

        get_pressed_keys,
        get_pressed_mod_keys,

        get_mouse_pos,
        get_mouse_pressed,

        set_mouse_pos,
        set_mouse_visibility,

        update_screen,

        frame_checkups,
        frame_checkups_with_fps,

    )

## if an input path was given, we import values and behaviors
## so app is launched in input playing mode

elif APP_REFS.input_path:

    from .playing import (

        SCREEN,
        SCREEN_RECT,
        blit_on_screen,

        get_events,

        get_pressed_keys,
        get_pressed_mod_keys,

        get_mouse_pos,
        get_mouse_pressed,

        set_mouse_pos,
        set_mouse_visibility,

        update_screen,

        frame_checkups,
        frame_checkups_with_fps,

    )

## otherwise we set values and behaviors so app runs normally

else:

    from .usingnormally import (

        SCREEN,
        SCREEN_RECT,
        blit_on_screen,

        get_events,

        get_pressed_keys,
        get_pressed_mod_keys,

        get_mouse_pos,
        get_mouse_pressed,

        set_mouse_pos,
        set_mouse_visibility,

        update_screen,

        frame_checkups,
        frame_checkups_with_fps,

    )
