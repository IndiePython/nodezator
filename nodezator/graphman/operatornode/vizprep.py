"""Class extension for preparation of visual objects."""

### standard library imports

from inspect import _empty
from collections.abc import Callable


### third-party import
from pygame import Rect


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
CALLABLE_CODENAME = type_to_codename(Callable)
CALLABLE_OUTPUT_NAME = 'operation'


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

        ### alias body's rect
        self.body_rect = body.rect

        ### create id label
        label = self.label = Object2D.from_surface(self.get_new_label_surface())

        ### signature mode input sockets

        operation_id = self.data["operation_id"]

        params = [

            char

            for char, flag
            in zip(operation_id, CHAR_FILTERING_MAP[operation_id])

            if flag

        ]

        signature_input_sockets = self.signature_input_sockets = [

            InputSocket(
                node=self,
                type_codename=TYPE_CODENAME,
                parameter_name=char,
            )

            for char in params

        ]

        ### signature mode output socket

        signature_output_socket = self.signature_output_socket = OutputSocket(
            node=self,
            type_codename=TYPE_CODENAME,
        )

        self.signature_output_sockets = (signature_output_socket,)

        ### callable mode output socket

        callable_output_socket = self.callable_output_socket = OutputSocket(
            node=self,
            type_codename=CALLABLE_CODENAME,
            output_name=CALLABLE_OUTPUT_NAME,
        )

        self.callable_output_sockets = (callable_output_socket,)

        ### gather all visual objects in the same
        ### collections

        self.signature_visual_objects = (
            body,
            label,
            signature_output_socket,
            *(socket for socket in signature_input_sockets),
        )

        ###

        self.callable_visual_objects = (
            body,
            label,
            callable_output_socket,
        )

        ### create rect representing entire node
        self.rect = Rect(0, 0, 0, 0)

        ### also create and store a rects managers to
        ### control all the rects in the node in different modes

        self.signature_rectsman = (
            RectsManager([obj.rect for obj in self.signature_visual_objects].__iter__)
        )

        self.callable_rectsman = (
            RectsManager([obj.rect for obj in self.callable_visual_objects].__iter__)
        )

        ### add self.rect to them

        for rectsman in (self.signature_rectsman, self.callable_rectsman):

            ## retrieve and use list's append method to add rect
            rectsman._get_all_rects.__self__.append(self.rect)

        ### pick tiny icon representing node
        self.pick_tiny_icon()

    def get_node_surf(self):

        return (
            COMMENTED_OUT_SURFS
            if self.data.get("commented_out", False)
            else NORMAL_SURFS
        )[
            ## use this tuple to get item from mapping

            (
                self.data["operation_id"],
                self.data.get('mode', 'expanded_signature')
            )

        ]

    def perform_commenting_uncommenting_setups(self):

        self.body.image = self.get_node_surf()
        self.update_label_surface()
        self.pick_tiny_icon()

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

    def pick_tiny_icon(self):
        """Pick tiny icon representing node.

        Used when providing a bird's eye view of the graph.
        """

        self.tiny_icon = getattr(

            self,

            (

                'commented_out_icon'
                if self.data.get('commented_out', False)

                else 'normal_icon'

            ),

        )
