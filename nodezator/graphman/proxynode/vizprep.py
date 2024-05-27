"""Class extension for preparation of visual objects."""

### standard library import
from functools import partial


### third-party import
from pygame import Rect


### local imports

from ...config import APP_REFS

from ...ourstdlibs.collections.general import CallList

from ...our3rdlibs.button import Button

from ...classes2d.single import Object2D

from ...rectsman.main import RectsManager

from ..widget.utils import WIDGET_CLASS_MAP

from ..socket.surfs import type_to_codename

from .utils import update_with_widget

from .surfs import (
    LABEL_SURF_MAP,
    HEADER_SURF_MAP,
    ADD_BUTTON_SURF,
    REMOVE_BUTTON_SURF,
)

from .constants import (
    HEADER_LABEL_WIDTH_INCREMENT,
)


## classes for composition

from ..socket.proxy import ProxySocket
from ..socket.output import OutputSocket


REMOVE_BUTTON_WIDTH = REMOVE_BUTTON_SURF.get_width()


class VisualRelatedPreparations:
    """Manages creation and setup of node visuals."""

    def create_visual_elements(self):
        """Create visual elements of the node."""

        ### create lists to gather references to visual
        ### objects, their rects, and also objects
        ### responsive to the mouse for purposes of
        ### easy access for drawing, positioning and
        ### mouse-related operations

        self.visual_objects = []
        self.mouse_aware_objects = []
        self.all_rects = []

        ### create label

        label = self.label = Object2D.from_surface(
            surface=(self.get_new_label_surface()),
        )

        ### create widget add button

        command = partial(
            (APP_REFS.ea.widget_creation_popup_menu.trigger_simple_widget_picking),
            self,
        )

        self.add_button = Button(
            surface=ADD_BUTTON_SURF,
            command=command,
        )

        ### instantiate remove widget button

        self.remove_button = Button(
            surface=REMOVE_BUTTON_SURF,
            command=self.remove_widget,
        )


        ### try grabbing widget data

        try:
            widget_data = self.data["widget_data"]

        ### if we fail, set output type codename to None

        except KeyError:
            output_type_codename = None

        ### if we succeed, instantiate widget

        else:

            ### instantiate widget

            ## retrieve widget class using the widget
            ## name from the widget data

            widget_name = widget_data["widget_name"]
            widget_cls = WIDGET_CLASS_MAP[widget_name]

            ## retrieve keyword arguments to use when
            ## instantiating the widget
            kwargs = widget_data["widget_kwargs"]

            ## instantiate the widget using the keyword
            ## arguments
            widget = self.widget = widget_cls(**kwargs)

            ## also define a command to update the widget
            ## value in the node data and perform other
            ## additional admin tasks and assign such
            ## command to the 'command' attribute of the
            ## widget

            command = CallList(
                [
                    partial(
                        update_with_widget,
                        kwargs,
                        "value",
                        widget,
                    ),
                    self.check_header_width,
                    self.update_remove_button_pos,
                ]
            )

            widget.command = command

            ## define expected type for output socket

            expected_type = widget.get_expected_type()

            output_type_codename = type_to_codename(expected_type)

        ### instantiate proxy socket

        proxy_socket = self.proxy_socket = ProxySocket(
            node=self,
            type_codename=(self.data.get("source_type_codename")),
        )

        ### the proxy socket is considered a kind of
        ### input socket;
        ###
        ### all node classes must have a 'input_sockets'
        ### attribute with an iterable containing the
        ### input sockets of the node
        self.input_sockets = (proxy_socket,)

        ### instantiate output socket

        output_socket = self.output_socket = OutputSocket(
            node=self,
            type_codename=(
                self.data.get(
                    "source_type_codename",
                    output_type_codename,
                )
            ),
            output_name=self.title,
        )

        ### all node classes must have an 'output_sockets'
        ### attribute listing all output sockets
        self.output_sockets = (output_socket,)

        ### create header

        width = self.get_header_width()

        key = (
            width,
            self.data.get("commented_out", False),
        )

        self.header = Object2D.from_surface(
            HEADER_SURF_MAP[key],
            coordinates_name="midtop",
            coordinates_value=self.midtop,
        )

        ### create a rect to be used as the boundaries
        ### of the node (its position and size are properly
        ### set in the call to reposition the elements)
        self.rect = Rect(0, 0, 0, 0)

        ### also create and store a rects manager to
        ### control all the rects in the node
        self.rectsman = RectsManager(self.all_rects.__iter__)

        ### position elements relative to each other
        self.reposition_elements()

        ### pick tiny icon representing node
        self.pick_tiny_icon()

    def check_header_width(self):

        width = self.get_header_width()
        if width == self.header.rect.width:
            return

        ## adjust width and reposition

        midtop = self.header.rect.midtop

        self.header.rect.width = width

        self.header.rect.midtop = midtop

        ## change image

        key = (
            width,
            self.data.get("commented_out", False),
        )

        self.header.image = HEADER_SURF_MAP[key]

        ## reposition all elements
        self.reposition_elements()

    def update_remove_button_pos(self):
        self.remove_button.rect.topleft = self.widget.rect.topright

    def get_header_width(self):

        width = self.label.rect.width + HEADER_LABEL_WIDTH_INCREMENT

        if hasattr(self, "widget") and 'source_name' not in self.data:

            width = max(
                (self.widget.rect.width + REMOVE_BUTTON_WIDTH),
                width,
            )

        return width

    def perform_commenting_uncommenting_setups(self):

        key = (
            self.header.rect.width,
            self.data.get("commented_out", False),
        )

        self.header.image = HEADER_SURF_MAP[key]

        self.update_label_surface()

        self.pick_tiny_icon()

    def update_label_surface(self):

        self.label.image = self.get_new_label_surface()
        self.label.rect.size = self.label.image.get_size()

    def get_new_label_surface(self):

        return LABEL_SURF_MAP[
            (
                self.get_label_text(),
                self.data.get("commented_out", False),
            )
        ]

    def get_label_text(self):

        return self.data.get(
            "source_name",
            f"{self.id} : {self.title}",
        )

    def pick_tiny_icon(self):
        """Pick tiny icon representing node.

        Using when providing a bird's eye view of the graph.
        """

        self.tiny_icon = getattr(

            self,

            (

                ## if commented out

                (

                    ## if redirect node
                    'commented_out_proxy_node_icon'
                    if 'source_name' in self.data

                    ## if data node

                    else (
                        'commented_out_data_node_icon'
                        if hasattr(self, 'widget')
                        else 'commented_out_proxy_node_icon'
                    )

                )

                if self.data.get('commented_out', False)

                ## if normal

                else (

                    ## if redirect node
                    'normal_proxy_node_icon'
                    if 'source_name' in self.data

                    ## if data node
                    else (
                        'normal_data_node_icon'
                        if hasattr(self, 'widget')
                        else 'normal_proxy_node_icon'
                    )

                )

            ),
        )
