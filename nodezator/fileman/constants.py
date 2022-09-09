"""Constants for the file manager subpackage."""

from ..fontsman.constants import ENC_SANS_BOLD_FONT_HEIGHT


FONT_HEIGHT = ENC_SANS_BOLD_FONT_HEIGHT  # height of font in pixels


### sizes

FILEMAN_SIZE = (800, 565)
DIR_PANEL_WIDTH = 485
BKM_PANEL_WIDTH = 280


### path objects settings

PATH_OBJ_QUANTITY = 16
PATH_OBJ_PADDING = 1

PATH_OBJ_PARENT_TEXT = ".."

### mouse setting: maximum delay for second mouse event;
### used to define the time limit to consider a second
### mouse event as part of the first mouse event (we use
### it to recognize double mouse button releases)
MAX_MSECS_TO_2ND_MOUSE_EVENT = 250
