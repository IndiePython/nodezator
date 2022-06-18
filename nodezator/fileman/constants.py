"""Constants for the file manager subpackage."""

from fontsman.constants import ENC_SANS_BOLD_FONT_HEIGHT


FONT_HEIGHT = ENC_SANS_BOLD_FONT_HEIGHT # height of font in pixels


### sizes/positions

### XXX instead of being fixed as they are now, it would
### be cool if the toplefts of the panels were defined
### dynamically based on the position of the objects that
### lie above them; as things are now, if someone ever
### desires to change the size of the file manager, it
### would also be necessary to change the toplefts
### (which is something simple enough, but could be further
### improved); similarly, the width of the panels could
### be defined as fixed percentages of the file manager's
### width;
###
### edit: an even better solution: after finishing other
### tasks of higher priority in the app, make it so the file
### manager measures/positions are defined dynamically
### just like we did with the splash screen;

FILEMAN_SIZE = (800, 565)

DIR_PANEL_WIDTH   = 485
DIR_PANEL_TOPLEFT = (546, 180)

BKM_PANEL_WIDTH = 280
BKM_PANEL_TOPLEFT = (250, 180)


### path objects settings

PATH_OBJ_QUANTITY = 16
PATH_OBJ_PADDING = 1

PATH_OBJ_PARENT_TEXT = ".."

### mouse setting: maximum delay for second mouse event;
### used to define the time limit to consider a second
### mouse event as part of the first mouse event (we use
### it to recognize double mouse button releases)
MAX_MSECS_TO_2ND_MOUSE_EVENT = 250
