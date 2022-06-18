"""Configuration facility."""

### standard library imports

from types import SimpleNamespace

from pathlib import Path

from subprocess import run as run_subprocess


### an object to hold references/data used throughout the
### entire app

APP_REFS = SimpleNamespace(

             ## custom maps

             node_def_map       = {},
             signature_map      = {},
             id_map             = {},
             script_path_map    = {},
             category_path_map  = {},
             category_index_map = {},

             ## placeholder dict to be replaced by a dict
             ## containing the data being edited in each
             ## app session
             data = {},

             ## status message
             status_message = "",

             ## custom stdout lines
             custom_stdout_lines = [],

           )



DATA_DIR = Path('data')

FONTS_DIR = DATA_DIR / 'fonts'

IMAGES_DIR = DATA_DIR / 'images'

SYNTAX_THEMES_DIR = DATA_DIR / 'syntax_themes'

APP_COLORS_FILE = (
  DATA_DIR / 'app_themes' / 'emeralds_on_coal.pyl'
)


### check whether ffmpeg (and ffprobe) is available, storing
### the info as a boolean

try:

    for command_name in ('ffmpeg', 'ffprobe'):

        run_subprocess(
          [command_name, '-version'],
          capture_output=True,
          check=True
        )

except Exception as err:
    FFMPEG_AVAILABLE = False

else: FFMPEG_AVAILABLE = True
