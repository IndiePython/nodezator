"""Constants for the text editor."""

### third-party import
from pygame import Rect


### local imports

from ...fontsman.constants import (
    ENC_SANS_BOLD_FONT_PATH,
    FIRA_MONO_BOLD_FONT_PATH,
)

from ...colorsman.colors import (
    TEXT_EDITING_AREA_FG,
    TEXT_EDITING_AREA_BG,
)


### general constants

FONT_HEIGHT = 20
NUMBER_OF_VISIBLE_LINES = 28

EDITING_AREA_HEIGHT = FONT_HEIGHT * NUMBER_OF_VISIBLE_LINES

TEXT_EDITOR_WIDTH = 1000
TEXT_EDITOR_HEIGHT = EDITING_AREA_HEIGHT + 100

# note that the 100 pixels we add to the text editor's
# height above is to provide extra spacing above and below
# the editing area, where we can draw an icon for the
# editor and other objects like the "Cancel" and "Ok"
# buttons


### rects representing areas and positions; they are defined
### using some of the constants defined above

## rect representing the text editor

TEXT_EDITOR_RECT = Rect(0, 0, TEXT_EDITOR_WIDTH, TEXT_EDITOR_HEIGHT)

## rect representing the editing area
##
## defining the width isn't important here, because it is
## adjusted at the beginning of every text editing session
## and as the number of lines in the text increases/decreases
## its order of magnitude (when the number of digits needed
## to display the highest line number increases/decreases)

EDITING_AREA_RECT = Rect(0, 0, 0, EDITING_AREA_HEIGHT)
EDITING_AREA_RECT.center = TEXT_EDITOR_RECT.center


### default font settings for text;
###
### these are default settings used for sans and monospaced
### text, respectively, when no syntax highlighting is
### specified in the syntax_highlighting argument of
### the TextEditor.edit_text() call

SANS_FONT_SETTINGS = {
    "font_height": FONT_HEIGHT,
    "font_path": ENC_SANS_BOLD_FONT_PATH,
    "foreground_color": TEXT_EDITING_AREA_FG,
    "background_color": TEXT_EDITING_AREA_BG,
}

MONO_FONT_SETTINGS = {
    "font_height": FONT_HEIGHT,
    "font_path": FIRA_MONO_BOLD_FONT_PATH,
    "foreground_color": TEXT_EDITING_AREA_FG,
    "background_color": TEXT_EDITING_AREA_BG,
}
