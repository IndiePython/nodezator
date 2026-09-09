"""Facility for user preferences management."""

### standard library imports

from os import environ

from shutil import copyfile

from pathlib import Path

from copy import deepcopy

from warnings import warn


### third-party imports

from pygame import error as PygameError

from pygame.font import Font, match_font


### local imports

from ..config import (
    APP_REFS,
    DEFAULT_USER_PREFS,
    USER_PREFS,
    WRITEABLE_PATH,
    OLD_WRITEABLE_PATH,
)

from ..appinfo import APP_DIR_NAME, NATIVE_FILE_EXTENSION

from ..logman.main import get_new_logger

from ..ourstdlibs.pyl import load_pyl, save_pyl

from ..our3rdlibs.userlogger import USER_LOGGER

from ..fontsman.cache import FONTS_DB

from ..fontsman.constants import (
    ENC_SANS_BOLD_FONT_PATH,
    FIRA_MONO_BOLD_FONT_PATH,
)

from .validation import (
    AVAILABLE_SOCKET_DETECTION_GRAPHICS,
    validate_prefs_data,
)



### module level logger
logger = get_new_logger(__name__)


### messages

ERROR_LOADING_USER_PREFS_MESSAGE = """
Error while trying to load user configuration. Default
configuration will be used instead
""".strip()

INVALID_USER_PREFS_MESSAGE = """
User configuration loaded didn't validate; Default
configuration will be used instead
""".strip()

UNEXISTENT_USER_PREFS_MESSAGE = """
User configuration doesn't exist. Default configuration
will be used instead
""".strip()

CONFIG_DIR_NOT_CREATED_MESSAGE = """
Couldn't create specific directory/ies within config directory to
store user files; we won't be able to save a custom configuration
neither custom data like recent files and bookmarks.
""".strip()

### names of config files

CONFIG_FILE_NAMES = (
    'bookmarks.pyl',
    'recent_files.pyl',
    'config.pyl',
    'known_packs.pyl',
)


### path to config file and other important files
###
### the locations defined here are different from the locations in
### previous versions because WRITEABLE_PATH uses a new org name
### (the new name of nodezator's parent project) and even older versions
### didn't use pygame.system.get_pref_path() either

## current base location for the config directory
APP_CONFIG_DIR = WRITEABLE_PATH / 'config'

## current locations for specific files

_current_locations_map = {
    filename: APP_CONFIG_DIR / filename
    for filename in CONFIG_FILE_NAMES
}

## the temp file swap just uses the current app config dir because it is
## not meant to persist in disk
TEMP_FILE_SWAP = APP_CONFIG_DIR  / f'temp_file_swap{NATIVE_FILE_EXTENSION}'


### create variables to hold the paths for the config files

BOOKMARKS_FILE = APP_CONFIG_DIR / "bookmarks.pyl"
RECENT_FILES = APP_CONFIG_DIR / "recent_files.pyl"
CONFIG_FILEPATH = APP_CONFIG_DIR / "config.pyl"
KNOWN_PACKS_FILE = APP_CONFIG_DIR / "known_packs.pyl"


### below we define old versions of the previous paths
###
### why do we do that? Because when users install the new versions,
### we must guarantee that the data from the files in the old locations
### are copied into the new locations, so that data is not lost
### (configs, recent files, etc.)

## path to config file and other important files using old
## parent project name

OLD_PROJ_NAME_APP_CONFIG_DIR = OLD_WRITEABLE_PATH / 'config'

_old_projname_locations_map = {
    filename: OLD_PROJ_NAME_APP_CONFIG_DIR / filename
    for filename in CONFIG_FILE_NAMES
}

## path to config file and other important files using that didn't
## rely on pygame.system.get_pref_path()

# old base location for the config directory

if "APPDATA" in environ:
    config_dir = Path(environ["APPDATA"])

elif "XDG_CONFIG_HOME" in environ:
    config_dir = Path(environ["XDG_CONFIG_HOME"])

else:
    config_dir = Path(environ["HOME"]) / ".config"

OLD_NON_GET_PREF_PATH_APP_CONFIG_DIR = config_dir / APP_DIR_NAME

_old_non_get_pref_path_locations_map = {
    name: OLD_NON_GET_PREF_PATH_APP_CONFIG_DIR / name
    for name in CONFIG_FILE_NAMES
}


### populate dictionaries wherein to store user preferences

DEFAULT_USER_PREFS.update(

{
    'LOCALE': 'en_us',
    'NUMBER_OF_BACKUPS': 5,
    'USER_LOGGER_MAX_LINES': 1000,
    'CUSTOM_STDOUT_MAX_LINES': 1000,
    'TEXT_EDITOR_BEHAVIOR': 'default',
    'SOCKET_DETECTION_GRAPHICS': 'reaching_hands',
    'DETECTION_DISTANCE': 150,
    'GRASPING_DISTANCE': 75,
    'GENERAL_FONT_HEIGHT': 17,
    'MONO_FONT_HEIGHT': 20,
    'GENERAL_FONT_KIND': 'default',
    'GENERAL_FONT_TO_USE': '',
    'MONO_FONT_KIND': 'default',
    'MONO_FONT_TO_USE': '',
}

)

USER_PREFS.update(DEFAULT_USER_PREFS)


### validate user preference defaults
validate_prefs_data(USER_PREFS)


### TODO
### must make sure USER_LOGGER entries logged here (if at all),
### persist in the user logger;
###
### that is: although the records are kept after this function,
### the window manager cleans the user logger with a call of
### a function from memoryman; that call is actually important,
### so I don't want to get rid of it; instead, it is probably
### best to allow all such logs to persist indefinitely in the
### session, or at least store much more; this could be done but
### saving them in the temp folder; then, instead of using the
### text viewer for seeing the entire log, we could create a
### dedicated interface to list all entries (the user could then
### click each entry to display its contents in the text viewer);
###
### this could be integrated with a notification system;

def load_and_preprocess_user_preferences():

    ### check whether the APP_CONFIG_DIR exists and create it otherwise

    if not APP_CONFIG_DIR.exists():

        try:
            APP_CONFIG_DIR.mkdir(parents=True)

        except Exception:
            USER_LOGGER.exception(CONFIG_DIR_NOT_CREATED_MESSAGE)


    ### if the APP_CONFIG_DIR already existed or was created in the previous
    ### if block, we can now check whether there is data in the old locations
    ### that is missing in the current locations and, if so, copy the data
    ### into the new locations
    ###
    ### we decided not to delete the files in the old locations, in case they
    ### are needed by the user somehow; the deletion must be done manually by
    ### the users if they desire

    if APP_CONFIG_DIR.exists():

        for filename in CONFIG_FILE_NAMES:

            ### old paths used for that filename

            old_paths = (

                # the ones on top get the preference when more than one file
                # exists

                _old_projname_locations_map[filename],
                _old_non_get_pref_path_locations_map[filename],

            )

            ### current path used for that filename
            current_path = _current_locations_map[filename]

            ### we only try copying from old locations in case the file doesn't
            ### exist in the current location

            if not current_path.exists():

                for old_path in old_paths:

                    ## also, we only try copying from the old path if it exists

                    if old_path.exists():

                        ## try copying

                        try:
                            copyfile(str(old_path), str(current_path))

                        ## in case an error occurs, log error

                        except Exception:

                            USER_LOGGER.exception(
                                "Error when copying {filename} data from"
                                " {old_path} to {current_path}."
                            )

                        ## otherwise, break out of this loop
                        else:
                            break


    ### now we can finally load the config data, if it exists

    ## if file exists, try loading it

    if CONFIG_FILEPATH.exists():

        try:
            user_config_data = load_pyl(CONFIG_FILEPATH)

        except Exception:
            USER_LOGGER.exception(ERROR_LOADING_USER_PREFS_MESSAGE)

        else:

            try:
                validate_prefs_data(user_config_data)

            except Exception:
                USER_LOGGER.exception(INVALID_USER_PREFS_MESSAGE)

            else:
                USER_PREFS.update(**user_config_data)

    ## otherwise, log this info

    else:
        USER_LOGGER.info(UNEXISTENT_USER_PREFS_MESSAGE)

    ### apply user configuration where needed
    USER_LOGGER.max_lines = USER_PREFS["USER_LOGGER_MAX_LINES"]

    ### preprocess values for fonts to be used

    for keys in (
        ('GENERAL_FONT_KIND', 'GENERAL_FONT_TO_USE', 'GENERAL_FONT_HEIGHT'),
        ('MONO_FONT_KIND', 'MONO_FONT_TO_USE', 'MONO_FONT_HEIGHT'),
    ):

        kind, value, height = (USER_PREFS[key] for key in keys)

        is_general = 'GENERAL' in keys[0]

        font_key_attr_name = 'general_font_key' if is_general else 'mono_font_key'

        setattr(

            APP_REFS,
            ('general_font_height' if is_general else 'mono_font_height'),
            height,

        )

        if kind == 'default':

            setattr(

                APP_REFS,
                font_key_attr_name,

                (
                    ENC_SANS_BOLD_FONT_PATH
                    if is_general

                    else FIRA_MONO_BOLD_FONT_PATH

                ),

            )

        elif kind == 'system_font':

            if match_font(value) is not None:

                try:
                    FONTS_DB[value][height]

                except (PygameError, Exception) as err:

                    key = keys[1]

                    message = (
                        "Could not properly load and render text with system"
                        f" font named {value!r} (config key is {key!r}) set on"
                        f" user preferences using height {height} (also set on"
                        " user preferences). As a result, we are using default"
                        " font instead."
                    )

                    warn(message)
                    USER_LOGGER.warning(message)

                    setattr(

                        APP_REFS,
                        font_key_attr_name,

                        (
                            ENC_SANS_BOLD_FONT_PATH
                            if is_general

                            else FIRA_MONO_BOLD_FONT_PATH

                        ),

                    )

                else:
                    setattr(APP_REFS, font_key_attr_name, value)

            else:

                key = keys[1]

                message = (
                    "Could not find system font set on user preferences"
                    f" for {key} ({value!r}). Using default font instead."
                )

                warn(message)
                USER_LOGGER.warning(message)

                setattr(

                    APP_REFS,
                    font_key_attr_name,

                    (
                        ENC_SANS_BOLD_FONT_PATH
                        if is_general

                        else FIRA_MONO_BOLD_FONT_PATH

                    ),

                )

        elif kind == 'font_file':

            if not Path(value).exists():

                key = keys[1]

                message = (
                    "Could not find font file on path set on user preferences for"
                    f" {key} ({value!r})."
                    " Using default font instead."
                )

                warn(message)
                USER_LOGGER.warning(message)

                setattr(

                    APP_REFS,
                    font_key_attr_name,

                    (
                        ENC_SANS_BOLD_FONT_PATH
                        if is_general

                        else FIRA_MONO_BOLD_FONT_PATH

                    ),

                )

            else:

                try:
                    FONTS_DB[Path(value)][height]

                except (PygameError, Exception):

                    key = keys[1]

                    message = (
                        "Could not properly load and render text with font file"
                        " from path set on user preferences for"
                        f" {key} ({value!r}). Using default font instead."
                    )

                    warn(message)
                    USER_LOGGER.warning(message)

                    setattr(

                        APP_REFS,
                        font_key_attr_name,

                        (
                            ENC_SANS_BOLD_FONT_PATH
                            if is_general

                            else FIRA_MONO_BOLD_FONT_PATH

                        ),

                    )

                else:
                    setattr(APP_REFS, font_key_attr_name, Path(value))


### function for updating socket detection graphics

def update_socket_detection_graphics(graphics_string_key):

    if graphics_string_key not in AVAILABLE_SOCKET_DETECTION_GRAPHICS:
        return

    USER_PREFS['SOCKET_DETECTION_GRAPHICS'] = graphics_string_key

    try:
        save_pyl(USER_PREFS, CONFIG_FILEPATH)

    except Exception:
        return

    else:
        APP_REFS.gm.reference_socket_detection_graphics()
