"""Configuration facility."""

### standard library imports

from types import SimpleNamespace

from pathlib import Path

from subprocess import run as run_subprocess


### third-party imports

from pygame.system import get_pref_path

from pygame.font import get_fonts


### local imports

from .ourstdlibs.collections.general import CallList

from .ourstdlibs.path import TemporaryFilepathsManager

from .appinfo import APP_DIR_NAME, ORG_DIR_NAME, NATIVE_FILE_EXTENSION



### user preferences (to be populated in a dedicated subpackage)

DEFAULT_USER_PREFS = {}
USER_PREFS = {}


### an object to hold references/data used throughout the
### entire app

APP_REFS = SimpleNamespace(

    ## custom maps

    node_def_map={},
    signature_map={},
    script_path_map={},
    category_path_map={},
    category_index_map={},

    ## placeholder dict to be replaced by a dict
    ## containing the data being edited in each
    ## app session
    data={},

    ## status message
    status_message="",

    ## custom stdout lines
    custom_stdout_lines=[],

    ## window resize setup commands
    window_resize_setups=CallList(),

    ## placeholder for copy of screen
    SCREEN_COPY=None,

    ## temporary filepaths manager

    temp_filepaths_man = (
        TemporaryFilepathsManager(
            temp_dir_prefix=f'{APP_DIR_NAME}_temp_',
            temp_file_prefix='temp_',
            temp_file_suffix=NATIVE_FILE_EXTENSION,
        )
    ),

    ## flag to store system info
    system_info={},

    ## flag to lock work-in-progress features, that is,
    ## features not ready for regular usage yet
    wip_lock=True,

    ## flag to check need to save system testing settings
    ## at end of testing session
    system_testing_set=False,
)

### sorted names of detected system fonts
SORTED_SYS_FONT_NAMES = sorted(get_fonts())


### data directory and its subdirectories


DATA_DIR = Path(__file__).parent / "data"

FONTS_DIR = DATA_DIR / "fonts"

IMAGES_DIR = DATA_DIR / "images"

SYNTAX_THEMES_DIR = DATA_DIR / "syntax_themes"

APP_WIDE_WEB_DIR = DATA_DIR / "aww"

SYSTEM_TESTING_DATA_DIR = DATA_DIR / "system_testing"

APP_COLORS_FILE = DATA_DIR / "app_themes" / "emeralds_on_coal.pyl"

TRANSLATIONS_DIR = DATA_DIR / 'translations'
LANGUAGE_NAMES_FILEPATH = TRANSLATIONS_DIR / 'language_native_names.pyl'
DIALOGS_DATA_PATH = DATA_DIR / 'dialogs.pyl'

SAMPLE_UNICODE_CHARS_PATH = DATA_DIR / 'sample_unicode_characters.pyl'


### writeable paths for config/logs, etc.
WRITEABLE_PATH = Path(get_pref_path(ORG_DIR_NAME, APP_DIR_NAME))

### previous writeable path, that uses the previous name of
### nodezator's parent project
OLD_WRITEABLE_PATH = Path(get_pref_path('IndiePython', APP_DIR_NAME))


### check whether ffmpeg (and ffprobe) is available, storing
### the info as a boolean

try:

    for command_name in ("ffmpeg", "ffprobe"):

        run_subprocess([command_name, "-version"], capture_output=True, check=True)

except Exception as err:
    FFMPEG_AVAILABLE = False

else:
    FFMPEG_AVAILABLE = True
