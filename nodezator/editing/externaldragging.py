"""Facility for managing data dragged from outside the app with the mouse.

At the time of implementation, all platforms supported dragged files and
only X11 supported dragged text.
"""

### standard library import
from pathlib import Path

### third-party import
from pygame import Rect


### local imports

from ..config import APP_REFS

from ..dialog import create_and_show_dialog

from ..pygamesetup import SERVICES_NS

from ..pygamesetup.constants import MEDIA_TYPE_TO_EXTENSIONS

from ..graphman.widget.utils import get_widget_metadata



MEDIA_TYPE_TO_PATH_PREVIEW_WIDGET_NAME = {

    'audio': 'audio_preview',
    'font' : 'font_preview',
    'image' : 'image_preview',
    'video': 'video_preview',
    'text': 'text_preview',

}

# arbitrary width and height, similar to actual stacked dialog
DIALOG_ANCHOR_RECT = Rect(0, 0, 50, 300)

_dragged_items = []


def manage_dragged_from_outside():

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


    for media_type, extensions in MEDIA_TYPE_TO_EXTENSIONS.items():

        if used_extensions.issubset(extensions):

            widget_name = MEDIA_TYPE_TO_PATH_PREVIEW_WIDGET_NAME[media_type]
            break

    else:
        widget_name = 'path_preview'

#    DIALOG_ANCHOR_RECT.midtop = APP_REFS.mouse_pos
#
#    answer = create_and_show_dialog(
#        buttons=(
#            ('Audio preview', 'audio_preview'),
#            ('Font preview', 'font_preview'),
#            ('Image preview', 'image_preview'),
#            ('Text preview', 'text_preview'),
#            ('Video preview', 'video_preview'),
#            ('Path preview', 'path_preview'),
#        ),
#        anchor_rect=DIALOG_ANCHOR_RECT,
#    )
#
#    if answer:
#        widget_name = answer
#
#    else:
#        return

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
