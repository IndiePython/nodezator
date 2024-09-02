"""Facility for user preferences management."""

### standard library imports

from os import environ

from shutil import copyfile

from pathlib import Path

from copy import deepcopy


### local imports

from ..config import APP_REFS, WRITEABLE_PATH

from ..appinfo import APP_DIR_NAME, NATIVE_FILE_EXTENSION

from ..logman.main import get_new_logger

from ..ourstdlibs.pyl import load_pyl, save_pyl

from ..our3rdlibs.userlogger import USER_LOGGER

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


### dictionary wherein to store user preferences; initially
### populated with default values

USER_PREFS = {
    "LANGUAGE": "English",
    "NUMBER_OF_BACKUPS": 5,
    "USER_LOGGER_MAX_LINES": 1000,
    "CUSTOM_STDOUT_MAX_LINES": 1000,
    "TEXT_EDITOR_BEHAVIOR": "default",
    "SOCKET_DETECTION_GRAPHICS": "reaching_hands",
    "DETECTION_DISTANCE": 150,
    "GRASPING_DISTANCE": 75,
}


### validate user preference defaults
validate_prefs_data(USER_PREFS)


### path to config file and other important files
###
### the locations defined here are different from the locations in
### previous versions because we are using a more reliable new
### solution (based on pygame.system.get_pref_path()) that picks
### an appropriate writeable path for us

## base location for the config directory
APP_CONFIG_DIR = WRITEABLE_PATH / 'config'

## location for specific files

BOOKMARKS_FILE = APP_CONFIG_DIR / 'bookmarks.pyl'
RECENT_FILES = APP_CONFIG_DIR / 'recent_files.pyl'
CONFIG_FILEPATH = APP_CONFIG_DIR / 'config.pyl'
KNOWN_PACKS_FILE = APP_CONFIG_DIR / 'known_packs.pyl'

TEMP_FILE_SWAP = APP_CONFIG_DIR  / f'temp_file_swap{NATIVE_FILE_EXTENSION}'


### here we have the old locations defined in previous versions
###
### why do we still define them here? because when users install the new
### version, we must guarantee that the data from the files in the old
### locations are copied into the new locations, so that data is not lost
### (configs, recent files, etc.)
###
### we don't need to do so for the temp file swap though because they are
### expected to be deleted whenever the user saves the a new untitled file
### or close the app while editing it. That is, they are not meant to persist
### in the disk

## old base location for the config directory

if "APPDATA" in environ:
    config_dir = Path(environ["APPDATA"])

elif "XDG_CONFIG_HOME" in environ:
    config_dir = Path(environ["XDG_CONFIG_HOME"])

else:
    config_dir = Path(environ["HOME"]) / ".config"

OLD_APP_CONFIG_DIR = config_dir / APP_DIR_NAME

## define the old location for each specific file

OLD_BOOKMARKS_FILE = OLD_APP_CONFIG_DIR / "bookmarks.pyl"
OLD_RECENT_FILES = OLD_APP_CONFIG_DIR / "recent_files.pyl"
OLD_CONFIG_FILEPATH = OLD_APP_CONFIG_DIR / "config.pyl"
OLD_KNOWN_PACKS_FILE = OLD_APP_CONFIG_DIR / "known_packs.pyl"


## check whether the APP_CONFIG_DIR exists and create it otherwise

if not APP_CONFIG_DIR.exists():

    try:
        APP_CONFIG_DIR.mkdir(parents=True)

    except Exception:
        USER_LOGGER.exception(CONFIG_DIR_NOT_CREATED_MESSAGE)


## if the APP_CONFIG_DIR already existed or was created in the previous
## if block, we can now check whether there is data in the old locations
## that is missing in the current locations and, if so, copy the data
## into the new locations
##
## we decided not to delete the files in the old locations, in case they
## are needed by the user somehow; the deletion must be done manually by
## the users if they desire

if APP_CONFIG_DIR.exists():

    for data_name, old_path, new_path in (
        ('file browser bookmarks', OLD_BOOKMARKS_FILE, BOOKMARKS_FILE),
        ('recent files', OLD_RECENT_FILES, RECENT_FILES),
        ('config', OLD_CONFIG_FILEPATH, CONFIG_FILEPATH),
        ('known packs', OLD_KNOWN_PACKS_FILE, KNOWN_PACKS_FILE),
    ):

        ### we only copy files in case the file exists in the old location
        ### but doesn't exist in the new location

        if (
            old_path.exists()
            and (not new_path.exists())
        ):

            ## try copying the file

            try:
                copyfile(str(old_path), str(new_path))

            ## in case an error occurs, log error

            except Exception:

                USER_LOGGER.exception(
                    "Error when copying {data_name} data from old location."
                )


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
