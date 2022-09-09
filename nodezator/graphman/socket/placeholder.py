"""Facility for placeholder socket class definition."""

### standard library import
from xml.etree.ElementTree import Element


### local imports

from .surfs import (
    HOLLOW_SOCKET_CIRCLE_SURF,
)

from .base import Socket

from ...colorsman.colors import HOLLOW_SOCKET_OUTLINE


class PlaceholderSocket(Socket):
    """A socket which represents a future input socket."""

    line_color = HOLLOW_SOCKET_OUTLINE

    def __init__(self, node, parameter_name, center=(0, 0)):
        """Store arguments.

        Parameters
        ==========
        node (graphman.calnode.main.CallableNode object)
            node to which this socket belongs.
        parameter_name (string)
            represents the name of the parameter.
        """
        ### store arguments

        ## node instance
        self.node = node

        ## store parameter name argument
        self.parameter_name = parameter_name

        ### assign image and create rect from it

        self.image = HOLLOW_SOCKET_CIRCLE_SURF
        self.rect = self.image.get_rect()

        ### position rect
        setattr(self.rect, "center", center)

    def get_input_socket(self):
        """Return a new input socket from the node."""
        return self.node.get_input_socket(self.parameter_name)

    def svg_repr(self):

        socket_radius_str = str(7 - 1)

        cx_str, cy_str = map(str, self.rect.center)

        return Element(
            "circle",
            {
                "cx": cx_str,
                "cy": cy_str,
                "r": socket_radius_str,
                "class": "hollow_socket",
            },
        )
