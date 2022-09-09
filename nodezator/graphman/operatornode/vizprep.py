"""Class extension for preparation of visual objects."""

### standard library import
from inspect import _empty


### local imports

from ...classes2d.single import Object2D

from ...rectsman.main import RectsManager

from .surfs import (
    NORMAL_SURFS,
    COMMENTED_OUT_SURFS,
    LABEL_SURF_MAP,
)

from .constants import (
    LABEL_AREA_HEIGHT,
    CHAR_FILTERING_MAP,
)

from ..socket.surfs import type_to_codename

## classes for composition

from ..socket.input import InputSocket
from ..socket.output import OutputSocket


TYPE_CODENAME = type_to_codename(_empty)


class VisualRelatedPreparations:
    """Manages creation and setup of node visuals."""

    def create_visual_elements(self):
        """Create visual elements of the node."""
        ### create and position node body

        body = self.body = Object2D.from_surface(
            self.get_node_surf(),
            coordinates_name="midtop",
            coordinates_value=self.midtop,
        )

        ### create label

        label = self.label = Object2D.from_surface(
            surface=(self.get_new_label_surface()),
            coordinates_name="topleft",
            coordinates_value=(body.rect.move(6, 4).topleft),
        )

        ### input sockets

        input_sockets = self.input_sockets = []

        operation_id = self.data["operation_id"]

        params = [
            char
            for char, flag in zip(operation_id, CHAR_FILTERING_MAP[operation_id])
            if flag
        ]

        divisions = len(params) + 1

        jump_height = (body.rect.height - (LABEL_AREA_HEIGHT // 2)) // divisions

        centery = body.rect.y + LABEL_AREA_HEIGHT + jump_height

        for char in params:

            input_socket = InputSocket(
                node=self,
                type_codename=TYPE_CODENAME,
                parameter_name=char,
                center=(
                    body.rect.left,
                    centery,
                ),
            )

            input_sockets.append(input_socket)

            centery += jump_height

        ### output socket

        socket_center = body.rect.move(0, LABEL_AREA_HEIGHT // 2).midright

        output_socket = self.output_socket = OutputSocket(
            node=self,
            type_codename=TYPE_CODENAME,
            center=socket_center,
        )

        ### all node classes must have an 'output_sockets'
        ### attribute listing all output sockets
        self.output_sockets = (output_socket,)

        ### gather all visual objects in the same
        ### collection

        self.visual_objects = (
            body,
            label,
            output_socket,
            *(socket for socket in input_sockets),
        )

        ### also create and store a rects manager to
        ### control all the rects in the node

        ## list containing all rects

        all_rects = [obj.rect for obj in self.visual_objects]

        ## get the __iter__ method of the tuple containing
        ## rects to use as a callable which returns the
        ## rects to be managed by the rects manager
        ## instance
        get_all_rects = all_rects.__iter__

        ## use the callable to instantiate the rects
        ## manager and then store it
        self.rectsman = RectsManager(get_all_rects)

        ### obtain a copy of the rectsman to represent
        ### the entire node; note that the copy is
        ### slightly horizontally inflated and moved
        self.rect = self.rectsman.inflate(5, 0).move(-5, 0)

        ### also append such rect to the list of the rects
        ### managed by the rectsman
        all_rects.append(self.rect)

    def get_node_surf(self):

        return (
            COMMENTED_OUT_SURFS
            if self.data.get("commented_out", False)
            else NORMAL_SURFS
        )[self.data["operation_id"]]

    ## alias update label surface method as the one
    ## to be called for commenting/uncommenting setups

    ## TODO write
    def perform_commenting_uncommenting_setups(self):

        self.body.image = self.get_node_surf()
        self.update_label_surface()

    def update_label_surface(self):

        self.label.image = self.get_new_label_surface()
        self.label.rect.size = self.label.image.get_size()

    def get_new_label_surface(self):

        return LABEL_SURF_MAP[
            (
                f"{self.id}",
                self.data.get("commented_out", False),
            )
        ]
