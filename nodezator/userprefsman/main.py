"""Facility for user preferences management."""

### standard library imports

from os import environ

from pathlib import Path


### local imports

from ..appinfo import APP_DIR_NAME, NATIVE_FILE_EXTENSION

from ..our3rdlibs.userlogger import USER_LOGGER

from ..ourstdlibs.pyl import load_pyl

from .validation import validate_prefs_dict

from ..logman.main import get_new_logger


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
}


### validate user preference defaults
validate_prefs_dict(USER_PREFS)


### defining path to config file

if "APPDATA" in environ:
    config_dir = Path(environ["APPDATA"])

elif "XDG_CONFIG_HOME" in environ:
    config_dir = Path(environ["XDG_CONFIG_HOME"])

else:
    config_dir = Path(environ["HOME"]) / ".config"


APP_CONFIG_DIR = config_dir / APP_DIR_NAME

BOOKMARKS_FILE = APP_CONFIG_DIR / "bookmarks.pyl"
RECENT_FILES = APP_CONFIG_DIR / "recent_files.pyl"
CONFIG_FILEPATH = APP_CONFIG_DIR / "config.pyl"
KNOWN_PACKS_FILE = APP_CONFIG_DIR / "known_packs.pyl"

TEMP_FILE_SWAP = APP_CONFIG_DIR  / f"temp_file_swap{NATIVE_FILE_EXTENSION}"

## if file exists, try loading it

if CONFIG_FILEPATH.exists():

    try:
        user_config_data = load_pyl(CONFIG_FILEPATH)

    except Exception:

        USER_LOGGER.exception(ERROR_LOADING_USER_PREFS_MESSAGE)

    else:

        try:
            validate_prefs_dict(user_config_data)

        except Exception:

            USER_LOGGER.exception(INVALID_USER_PREFS_MESSAGE)

        else:
            USER_PREFS.update(**user_config_data)

else:

    USER_LOGGER.info(UNEXISTENT_USER_PREFS_MESSAGE)

    if not APP_CONFIG_DIR.exists():

        try:
            APP_CONFIG_DIR.mkdir(parents=True)

        except Exception:

            USER_LOGGER.exception(CONFIG_DIR_NOT_CREATED_MESSAGE)

### apply user configuration where needed
USER_LOGGER.max_lines = USER_PREFS["USER_LOGGER_MAX_LINES"]
