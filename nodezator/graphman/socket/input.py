"""Facility for definition of input socket class."""

### standard library import
from xml.etree.ElementTree import Element


### local imports

from ...config import APP_REFS

from ...our3rdlibs.behaviour import (
    indicate_unsaved,
    set_status_message,
)

from .base import Socket

from .surfs import CODENAME_TO_STYLE_MAP


class InputSocket(Socket):
    """Socket representing (sub)parameter from a callable."""

    def __init__(
        self,
        node,
        type_codename,
        parameter_name,
        subparameter_index=None,
        center=(0, 0),
    ):
        """Store arguments, setup image, rect and position.

        Parameters
        ==========

        node (graphman.calnode.main.CallableNode reference)
            node to which this socket belongs
        type_codename (string)
            a name representing an specific type, used
            to pick style-related objects for the socket;
            no type enforcing is ever performed, though.
        parameter_name (string)
            represents the name of the parameter
        subparameter_index (None or integer >= 0)
            if given, it is a string which represents the
            name of the subparameter; we use stringified
            integers which are generated automatically
            whenenver a new subparameter is created.
        center (2-tuple of integers)
            represents the position on the screen wherein
            to center the input socket.
        """
        ### store arguments

        ## node instance
        self.node = node

        ## store parameter name and subparameter index

        self.parameter_name = parameter_name
        self.subparameter_index = subparameter_index

        ## store type codename and perform related setups
        self.update_type_codename(type_codename)

        ### obtain rect from image and position it using
        ### the given center

        self.rect = self.image.get_rect()
        setattr(self.rect, "center", center)

    def update_type_codename(self, type_codename):
        ###
        self.type_codename = type_codename

        ### obtain and store style objects for the
        ### type codename (outline color, fill color,
        ### svg class name and surface)

        (
            self.outline_color,
            self.fill_color,
            self.svg_class_name,
            self.circle_surf,
        ) = CODENAME_TO_STYLE_MAP[type_codename]

        self.line_color = self.fill_color
        self.image = self.circle_surf

    def on_right_mouse_release(self, event):
        """React to right mouse button release.

        Parameters
        ==========

        event (pygame.event.Event of pygame.MOUSEBUTTONUP
        type)

            required in order to comply with protocol
            used;

            Check pygame.event module documentation on
            pygame website for more info about this event
            object.
        """
        APP_REFS.ea.input_socket_popup_menu.show(
            self,
            event.pos,
        )

    def mark_for_unpacking(self):

        if self.subparameter_index in (
            self.node.data["subparam_unpacking_map"][self.parameter_name]
        ):

            ## create status message

            status_message = "Didn't need to unpack: input" " unpacked already."

        else:

            ## mark subparameter for unpacking

            (self.node.mark_subparameter_for_unpacking(self))

            ## create status message
            status_message = "Marked input for unpacking"

            ## since we changed the data, mark it
            ## as unsaved
            indicate_unsaved()

        ## display statusbar message
        set_status_message(status_message)

    def unmark_for_unpacking(self):

        if self.subparameter_index in (
            self.node.data["subparam_unpacking_map"][self.parameter_name]
        ):

            ## unmark subparameter for unpacking

            (self.node.unmark_subparameter_for_unpacking(self))

            ## create status message
            status_message = "Undid unpacking"

            ## since we changed the data, mark it
            ## as unsaved
            indicate_unsaved()

        else:

            ## create status message

            status_message = (
                "Didn't need to undo unpacking: input" " already not unpacked"
            )

        ## inform user of change in statusbar
        set_status_message(status_message)

    def get_id(self):
        """Return a custom id from gathered data."""

        return (
            (
                self.node.id,
                self.parameter_name,
            )
            if self.subparameter_index is None
            else (
                self.node.id,
                self.parameter_name,
                self.subparameter_index,
            )
        )

    def signal_severance(self):
        """Signal severance of segment to node.

        Only applies if this input socket represents
        a subparameter (in which case its
        'subparameter_index' attribute is not None).

        Used to make the node aware of severance, so
        measures can be taken, if needed.
        """
        if self.subparameter_index is not None:
            self.node.react_to_severance(self)

    def receive_input(self, data):
        """Send received input to node.

        Parameters
        ==========
        data (any Python object)
            data sent by the graph manager, retrieved from
            another node.
        """
        self.node.receive_input(
            data,
            self.parameter_name,
            self.subparameter_index,
        )

    def svg_repr(self):
        """"""
        socket_radius_str = str(7 - 1)

        cx_str, cy_str = map(str, self.rect.center)

        return Element(
            "circle",
            {
                "cx": cx_str,
                "cy": cy_str,
                "r": socket_radius_str,
                "class": self.svg_class_name,
            },
        )
