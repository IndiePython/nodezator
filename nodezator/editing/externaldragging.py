"""Facility for managing data dragged from outside the app with the mouse.

At the time of implementation, all platforms supported dragged files and
only X11 supported dragged text.
"""

### standard library import
from pathlib import Path


### local imports


from ..config import APP_REFS

from ..pygamesetup import SERVICES_NS

from ..graphman.widget.utils import get_widget_metadata



_dragged_items = []


EXTENSION_SET_TO_WIDGET_NAME = {

    frozenset((
        '.bmp', '.gif', '.jpg', '.jpeg', '.lbm', '.pcx', '.png',
        '.pnm', '.pbm', '.pgm', '.ppm', '.qoi', '.svg', '.tga',
        '.tif', '.tiff', '.webp', '.xpm', '.xcf'
    )) : 'image_preview',

    frozenset((
        '.bin', '.dfont', '.otf', '.pfb', '.ps', '.sfd', '.ttf', '.woff',
    )) : 'font_preview',

}


def manage_dragged_from_outside():

    ###
    APP_REFS.ea.popup_spawn_pos = SERVICES_NS.get_mouse_pos()

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
            [Path(item.file) for item in _dragged_items]
        )

    else:

        if quantity == 1:
            treat_single_line_of_text(_first.text)

        else:

            treat_multiple_lines_of_text(
                '\n'.join(item.text for item in _dragged_items)
            )

    ###
    _dragged_items.clear()


def treat_filepaths(filepaths):

    used_extensions = frozenset(path.suffix.lower() for path in filepaths)

    for extensions, widget_name in EXTENSION_SET_TO_WIDGET_NAME.items():

        if used_extensions.issubset(extensions):
            break

    else:
        widget_name = 'path_preview'

    ###

    if len(filepaths) == 1:

        value = str(filepaths[0])
        type_ = str

    else:

        value = tuple(str(path) for path in filepaths)
        type_ = tuple

    ###

    APP_REFS.ea.insert_node(

        get_widget_metadata(
            {'widget_name': widget_name, 'type': type_},
            value,
        )

    )


def treat_single_line_of_text(text):
    print('one line of text')

def treat_multiple_lines_of_text(text):
    print('several lines of text')
