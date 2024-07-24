"""Facility for managing data dragged from outside the app with the mouse.

At the time of implementation, all platforms supported dragged files and
only X11 supported dragged text.
"""

### standard library import
from pathlib import Path


### local imports


from ..config import APP_REFS

from ..pygamesetup import SERVICES_NS



_dragged_items = []


def manage_dragged_from_outside():

    ###
    mouse_pos = SERVICES_NS.get_mouse_pos()

    ###

    dragged_from_outside = APP_REFS.dragged_from_outside

    _dragged_items.extend(dragged_from_outside)
    dragged_from_outside.clear()

    ###

    quantity = len(_dragged_items)
    first_item = _dragged_items[0]

    ###
    if not quantity: return

    elif hasattr(first_item, 'file'):

        treat_filepaths(
            [Path(item.file) for item in _dragged_items],
            mouse_pos,
        )

    else:

        if quantity == 1:
            treat_single_line_of_text(_first.text, mouse_pos)

        else:

            treat_multiple_lines_of_text(
                '\n'.join(item.text for item in _dragged_items),
                mouse_pos,
            )

    ###
    _dragged_items.clear()


def treat_filepaths(filepaths, mouse_pos):

    if len(filepaths) == 1:
        print('one filepath')

    else:
        print('several filepaths')

def treat_single_line_of_text(text, mouse_pos):
    print('one line of text')

def treat_multiple_lines_of_text(text, mouse_pos):
    print('several lines of text')
