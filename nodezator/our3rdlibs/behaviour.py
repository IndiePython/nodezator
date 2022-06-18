"""Facility for third party behaviour related tools."""

### standard library import
from functools import partial


### third-party imports
from pygame.display import get_caption, set_caption


### local imports

from config import APP_REFS

from pygameconstants import _CLOCK

from loopman.exception import QuitAppException

from translation import STATUS_MESSAGES_MAP


### utility functions

set_status_message = \
    partial(setattr, APP_REFS, 'status_message')

def set_status_message_from_key(key):
    set_status_message(STATUS_MESSAGES_MAP[key])

def remove_buffer():
    """Remove swap file if present."""
    try: APP_REFS.swap_path.unlink()
    except AttributeError: pass

def quit_app():
    """Raise a quit app exception."""
    raise QuitAppException

def are_changes_saved():
    """Return True if there are no unsaved changes."""
    ### retrieve the title in the window
    title, _ = get_caption()

    ### the absence of a '*' character at the beginning
    ### of the window title marks the absence of unsaved
    ### changes
    if not title.startswith("*"): return True

def toggle_caption(indicate_saved):
    """Toggle caption to indicate saved/unsaved state.

    That is, to indicate whether there are changes in the
    positions which aren't saved on file.

    indicate_saved (boolean)
        hints to whether or not we should indicate that
        changes made are saved.
    """
    title, icontitle = get_caption()

    ### remove asterisk

    if indicate_saved:

        if not are_changes_saved():

            title     = title    [1:]
            icontitle = icontitle[1:]

    ### add asterisk

    else:

        if are_changes_saved():

            title     = "*" + title
            icontitle = "*" + icontitle

    ### set the caption using the resulting
    ### title and icontitle
    set_caption(title, icontitle)

indicate_saved   = partial(toggle_caption, True)
indicate_unsaved = partial(toggle_caption, False)


def get_current_fps():
    """Return current fps custom formatted.

    Gets the fps from the clock object then round it and
    turn it into a string like this:

     9.18484242 -> '09'
    29.18484242 -> '29'
    """
    return str(round(_CLOCK.get_fps())).rjust(2, "0")
