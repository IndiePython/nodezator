"""Facility for proxy socket class definition."""

### standard library import
from xml.etree.ElementTree import Element


### local imports

from ...config import APP_REFS

from .surfs import (
    HOLLOW_SOCKET_CIRCLE_SURF,
    CODENAME_TO_STYLE_MAP,
)

from .base import Socket

from ...colorsman.colors import HOLLOW_SOCKET_OUTLINE


class ProxySocket(Socket):
    """Represents empty spot for incomming data."""

    def __init__(
        self,
        node,
        type_codename=None,
        center=(0, 0),
    ):
        """Store arguments.

        Parameters
        ==========
        node (graphman.proxynode.main.ProxyNode object)
            node to which this socket belongs.
        """
        ### store arguments

        ## node instance
        self.node = node

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

        else:

            ### obtain and store style objects for the
            ### type codename (outline color, fill color,
            ### svg class name and surfaces)

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

        return (
            self.node.id,
            self.node.title,
        )

    def signal_connection(self):
        ## change style as needed
        self.update_type_codename(self.parent.type_codename)
        ##
        self.node.signal_connection()

    def signal_severance(self):
        ## change style as needed
        self.update_type_codename(None)

        ##
        self.node.signal_severance(self)

    def receive_input(self, data):
        """Pass data on to output socket children.

        Parameters
        ==========
        data (any Python object)
            data sent by the graph manager, retrieved from
            another node.
        """
        try:
            children = self.node.output_socket.children
        except AttributeError:
            pass
        else:
            for child in children:
                child.receive_input(data)

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
        APP_REFS.ea.proxy_socket_popup_menu.show(
            self,
            event.pos,
        )

    def add_source_id(self, source_id):

        out_socket = self.node.output_socket

        if hasattr(out_socket, 'children'):

            for child in out_socket.children:
                child.add_source_id(source_id)

    def svg_repr(self):

        socket_radius_str = str(7 - 1)

        cx_str, cy_str = map(str, self.rect.center)

        svg_class_name = (
            "hollow_socket"
            if self.image is HOLLOW_SOCKET_CIRCLE_SURF
            else self.svg_class_name
        )

        return Element(
            "circle",
            {
                "cx": cx_str,
                "cy": cy_str,
                "r": socket_radius_str,
                "class": svg_class_name,
            },
        )
