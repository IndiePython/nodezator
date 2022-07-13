"""Constants shared by the text viewer modules."""

### third-party import
from pygame import Rect

### local imports

from ...pygameconstants import SCREEN_RECT

from ...fontsman.constants import (
                          FIRA_MONO_BOLD_FONT_HEIGHT,
                          FIRA_MONO_BOLD_FONT_PATH,
                        )

from ...colorsman.colors import (
                        TEXT_VIEWER_FG,
                        TEXT_VIEWER_BG,
                        CUSTOM_STDOUT_FG,
                        CUSTOM_STDOUT_BG,
                      )


### general text settings presets

DEFAULT_TEXT_SETTINGS = {
  'font_height'      : FIRA_MONO_BOLD_FONT_HEIGHT,
  'font_path'        : FIRA_MONO_BOLD_FONT_PATH,
  'foreground_color' : TEXT_VIEWER_FG,
  'background_color' : TEXT_VIEWER_BG,
}

CUSTOM_STDOUT_TEXT_SETTINGS = {
  'font_height'      : FIRA_MONO_BOLD_FONT_HEIGHT,
  'font_path'        : FIRA_MONO_BOLD_FONT_PATH,
  'foreground_color' : CUSTOM_STDOUT_FG,
  'background_color' : CUSTOM_STDOUT_BG,
}


TEXT_SETTINGS_PRESETS_MAP = {
  'default'       : DEFAULT_TEXT_SETTINGS,
  'custom_stdout' : CUSTOM_STDOUT_TEXT_SETTINGS,
}


### rect

TEXT_VIEWER_RECT = Rect(0, 0, 900, 576)
TEXT_VIEWER_RECT.center = SCREEN_RECT.center

CUSTOM_STDOUT_RECT = SCREEN_RECT.copy()

CUSTOM_STDOUT_RECT.height *= .4
CUSTOM_STDOUT_RECT.inflate_ip(-20, 0)

CUSTOM_STDOUT_RECT.midbottom = (
  SCREEN_RECT.move(0, -80).midbottom
)

RECT_PRESETS_MAP = {
  'default'       : TEXT_VIEWER_RECT,
  'custom_stdout' : CUSTOM_STDOUT_RECT,
}
