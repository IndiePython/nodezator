"""Facility for input socket class definition."""

### standard library import
from xml.etree.ElementTree import Element


### local imports

from ...config import APP_REFS

from .base import Socket

from .surfs import (
    HOLLOW_SOCKET_CIRCLE_SURF,
    CODENAME_TO_STYLE_MAP,
)

from ...colorsman.colors import HOLLOW_SOCKET_OUTLINE


class OutputSocket(Socket):
    """A socket which represents the output of a callable.

    It might actually represent part of the output, if
    the output is divided and distributed through
    multiple output sockets (in this case, the callable
    returns a dictionary, and the output sockets represent
    each existing key in that dictionary).
    """

    def __init__(
        self,
        node,
        type_codename,
        output_name="output",
        center=(0, 0),
    ):
        """Store arguments, setup image, rect and position.

        node (graphman.calnode.main.CallableNode object)
            node to which this socket belongs.
        type_codename (string)
            a name representing an specific type, used
            to pick style-related objects for the socket;
            no type enforcing is ever performed, though.
        output_name (string)
            represents the name of the output represented
            by this output socket. It can represent the
            entire output of the node's callable or, if the
            output is divided into multiple parts it is
            used as a key to retrieve the respective part
            of the output from the output of the callable,
            which in this case must be a dictionary.
        center (2-tuple of integers)
            represents the position on the screen wherein
            to center the output socket.
        """
        ### store arguments

        ## node instance
        self.node = node

        ## store output name argument
        self.output_name = output_name

        ## store type codename and perform related setups
        self.update_type_codename(type_codename)

        ### obtain rect from image and position it using
        ### the given center

        self.rect = self.image.get_rect()
        setattr(self.rect, "center", center)

    def update_type_codename(self, type_codename):
        ###
        self.type_codename = type_codename

        if type_codename is None:

            self.image = HOLLOW_SOCKET_CIRCLE_SURF
            self.line_color = HOLLOW_SOCKET_OUTLINE

            self.svg_class_name = "hollow_socket"

        else:

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

            ### update image
            self.image = self.circle_surf

    def get_id(self):
        """Return a custom id from gathered data."""
        return (self.node.id, self.output_name)

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
        APP_REFS.ea.output_socket_popup_menu.show(
            self,
            event.pos,
        )

    def svg_repr(self):
        """"""

        socket_radius_str = str(7 - 1)

        cx, cy = self.rect.center

        return Element(
            "circle",
            {
                "cx": str(cx),
                "cy": str(cy),
                "r": socket_radius_str,
                "class": self.svg_class_name,
            },
        )
