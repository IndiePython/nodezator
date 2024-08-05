"""Facility for managing data dragged from outside the app with the mouse.

At the time of implementation, all platforms supported dragged files and
only X11 supported dragged text.
"""

### standard library imports

from pathlib import Path

from ast import literal_eval


### local imports

from ..config import APP_REFS

from ..pygamesetup import SERVICES_NS

from ..pygamesetup.constants import MEDIA_TYPE_TO_EXTENSIONS

from ..graphman.widget.utils import get_widget_metadata

from ..ourstdlibs.color.utils import validate_hex_color_string



MEDIA_TYPE_TO_PATH_PREVIEW_WIDGET_NAME = {

    'audio': 'audio_preview',
    'font' : 'font_preview',
    'image' : 'image_preview',
    'video': 'video_preview',
    'text': 'text_preview',

}


_dragged_items = []


def manage_dropped_data():

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
            treat_single_line_of_text(first_item.text.strip())

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

    ### check whether text represents a Python literal

    try:
        value = literal_eval(text)

    ### if not, check suitable possibilities

    except Exception:

        if validate_hex_color_string(text):

            APP_REFS.ea.insert_node(
                get_widget_metadata(
                    {
                        'widget_name': 'color_button',
                        'widget_kwargs': {
                            'color_format': 'hex_string',
                        },
                        'type': str
                    },
                    text,
                )
            )

    ### if it does, also check possibilities for Python
    ### literals

    else:

        type_ = type(value)

        if type_ in (bool, int, float):
            APP_REFS.ea.insert_node(get_widget_metadata(type_, value))

        else:

            APP_REFS.ea.insert_node(
                get_widget_metadata({'widget_name': 'literal_entry'}, text)
            )


def treat_multiple_lines_of_text(text):
    print('several lines of text')
