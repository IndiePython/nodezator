### local imports

from ...config import APP_REFS

from ...our3rdlibs.behaviour import (
    indicate_unsaved,
    set_status_message,
)

from ..socket.surfs import type_to_codename


def update_title(self, new_title):
    """Update node's title, performing needed setups."""

    output_socket = self.output_socket

    old_id = output_socket.get_id()

    output_socket.output_name = new_title

    if hasattr(output_socket, "children"):

        APP_REFS.gm.fix_output_socket_id(output_socket, old_id)

    self.title = new_title

    self.data["title"] = new_title

    ## update label surface
    self.update_label_surface()

    ## check header width
    self.check_header_width()

    ###

    try:
        widget = self.widget

    except AttributeError:
        type_codename = None

    else:

        expected_type = widget.get_expected_type()

        type_codename = type_to_codename(expected_type)

    ###
    self.propagate_output(new_title, type_codename)

    ###

    set_status_message("Changed data node's title.")

    indicate_unsaved()
