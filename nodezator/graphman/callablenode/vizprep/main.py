"""Class extension for preparation of visual objects."""

### third-party import
from pygame import Rect


### local imports

from ....config import APP_REFS

from ....ourstdlibs.collections.fldict.main import FlatListDict

from ....classes2d.single import Object2D

from ....textman.render import render_text

from ....rectsman.main import RectsManager

from ....colorsman.colors import (
    NODE_CATEGORY_COLORS,
    NODE_TITLE,
    BLACK,
)

from ...socket.surfs import type_to_codename

from ..constants import (
    FONT_HEIGHT,
    NODE_WIDTH,
)


## functions for injection

from .param import create_parameter_objs

from .varparam import create_var_parameter_objs

## class extension
from .bodysetup.main import BodySetupOperations

## class for composition
from ...socket.output import OutputSocket


## other objects for composition

from ..surfs import (
    NODE_ROOFS_MAP,
    TOP_CORNERS_MAP,
    NORMAL_BOTTOM_CORNERS,
    NORMAL_NODE_FOOT,
)


class VisualRelatedPreparations(BodySetupOperations):
    """Manages creation and setup of node visuals."""

    ### extend class by injecting functions

    create_parameter_objs = create_parameter_objs
    create_var_parameter_objs = create_var_parameter_objs

    ### define remaining methods

    def create_visual_elements(self):
        """Create visual elements of the node."""
        ### start by storing the nodes category color
        self.store_category_color_data()

        ### create elements situated on top of the node
        self.create_top_objects()

        ### create title of node
        self.create_title_object()

        ### create input related widgets
        self.create_input_related_objects()

        ### create output sockets
        self.create_output_sockets()

        ### create elements situated on bottom of the node
        self.create_bottom_objects()

        ### create text object representing node id
        self.create_node_id_text()

        ### create a body for the node

        body_topleft = self.top_rectsman.bottomleft
        body_size = (NODE_WIDTH, 0)

        self.body = Object2D(rect=Rect(body_topleft, body_size))

        ### gather references to "background" and text
        ### elements for easy retrieval and drawing

        self.background_and_text_elements = (
            *self.corners,
            self.roof,
            self.body,
            self.foot,
            self.title_text_obj,
            self.id_text_obj,
        )

        ### create a rect to be used as the boundaries
        ### of the node (its height is properly set when
        ### repositioning the other objects inside the
        ### node in the next step; its width and position
        ### position are set just after the next step)
        self.rect = Rect(0, 0, 0, 0)

        ### reposition all objects within the node (also
        ### sets height of self.rect)
        self.reposition_elements()

        ### perform several body-related setups
        self.setup_body()

        ### store input rectsman locally if it exists
        ### (that is, if the callable the node represents
        ### has parameters)
        try:
            input_rectsman = self.input_rectsman
        except AttributeError:
            pass

        ### set width of self.rect depending on existence
        ### of the input rectsman

        try:
            input_rectsman

        except NameError:

            width = self.output_rectsman.right - self.top_rectsman.left

        else:

            width = self.output_rectsman.right - input_rectsman.left

        self.rect.width = width

        ### position self.rect
        self.rect.midtop = self.midtop

        ### also create and store a rects manager to
        ### control all the rects in the node

        ## create a list containing the rects to be managed
        ## and get its __iter__ method to use as a callable
        ## which returns the rects to be managed by the
        ## rects manager instance

        all_rects = [
            self.rect,
            self.top_rectsman,
            self.title_text_obj.rect,
            self.body.rect,
            self.output_rectsman,
            self.id_text_obj.rect,
            self.bottom_rectsman,
        ]

        get_all_rects = all_rects.__iter__

        ## also add the input rectsman in the list,
        ## if it exists

        try:
            input_rectsman
        except NameError:
            pass
        else:
            all_rects.append(input_rectsman)

        ## use the callable to instantiate the rects
        ## manager and then store it
        self.rectsman = RectsManager(get_all_rects)

        ### finally, if there's no input rectsman (and thus
        ### no parameters), adjust the self.rect to be just
        ### a little wider, so its left outline is clearly
        ### visible (this isn't needed when there is an input
        ### rectsman, because the input socket(s) hanging off
        ### its left side make up for the extra width needed)

        try:
            input_rectsman
        except NameError:
            self.rect.inflate_ip(6, 0)

    def store_category_color_data(self):
        """Store category related color data for the node.

        This color will be used for some elements of the
        node. All nodes in the same category have the same
        color.

        The functionality in this method was isolated
        so that it can be overriden by subclasses as
        neeeded.
        """
        self.color_index = APP_REFS.category_index_map[self.data["script_id"][:2]]

        self.category_color = NODE_CATEGORY_COLORS[self.color_index]

    def create_top_objects(self):
        """Create objects that lie on top of the node."""
        ### create and position roof and top corner objects
        ### using surfaces from imported maps

        ## roof

        self.roof = Object2D()
        self.roof.image = NODE_ROOFS_MAP[self.category_color]
        self.roof.rect = self.roof.image.get_rect()

        ## create list to store corners
        self.corners = []

        # topleft corner

        topleft_corner = Object2D()
        topleft_corner.image = TOP_CORNERS_MAP[self.category_color][0]

        topleft_corner.rect = topleft_corner.image.get_rect()

        topleft_corner.rect.topright = self.roof.rect.topleft

        # topright corner

        topright_corner = Object2D()
        topright_corner.image = TOP_CORNERS_MAP[self.category_color][1]

        topright_corner.rect = topright_corner.image.get_rect()

        topright_corner.rect.topleft = self.roof.rect.topright

        self.corners.append(topleft_corner)
        self.corners.append(topright_corner)

        ### store a rects manager to manage the position
        ### of the objects on top of the node

        ## get a callable which returns the rects to be
        ## managed

        get_top_rects = (
            topleft_corner.rect,
            topright_corner.rect,
            self.roof.rect,
        ).__iter__

        ## use it to instantite the rects manager and
        ## store it in its own attribute
        self.top_rectsman = RectsManager(get_top_rects)

        ## align the top rectsman midtop with the
        ## midtop coordinates of the node
        self.top_rectsman.midtop = self.midtop

    def create_title_object(self):
        """Instatiate object representing title of the node.

        Create and store a text object to represent the
        node's title. We use the name of the callable the
        node represents as the text.
        """
        ### reference the roof's rect
        roof_rect = self.roof.rect

        ### create text object for title

        ## calculate midtop for title object so that it has
        ## its midtop coordinate just a bit below the
        ## midtop of the roof of the node
        title_midtop = roof_rect.move(0, 3).midtop

        ## instantiate text object

        self.title_text_obj = Object2D.from_surface(
            surface=render_text(
                # text for surface
                text=self.title_text,
                # font settings (note that we use the
                # roof width as the max width)
                font_height=FONT_HEIGHT,
                foreground_color=NODE_TITLE,
                background_color=self.category_color,
                max_width=roof_rect.width,
            ),
            coordinates_name="midtop",
            coordinates_value=title_midtop,
        )

    def create_input_related_objects(self):
        """Create objects representing the node' inputs."""
        ### create maps to hold button instances
        ### for subparameters and for placeholder sockets

        self.widget_add_button_flmap = FlatListDict()
        self.widget_remove_button_flmap = FlatListDict()
        self.placeholder_add_button_map = {}

        self.subparam_up_button_flmap = FlatListDict()
        self.subparam_down_button_flmap = FlatListDict()

        ### instantiate a special input socket map to hold
        ### input socket instances
        self.input_socket_live_flmap = FlatListDict()

        ### instantiate a placeholder socket map to hold
        ### placeholder socket instances
        self.placeholder_socket_live_map = {}

        ### instantiate a dict to hold widget instances
        self.widget_live_flmap = FlatListDict()

        ### instantiate a dict to hold objects indicating
        ### that a subparameter must be unpacked when
        ### the node is executed
        self.subparam_unpacking_icon_flmap = FlatListDict()

        ### instantiate a subparam keyword live map to
        ### hold entry widget instances representing
        ### keywords for subparameters of a
        ### keyword-variable parameter
        self.subparam_keyword_entry_live_map = {}

        ### regarding the maps created earlier, also store
        ### their 'flat_values' attribute or '.values()'
        ### view in dedicated attributes for easier access
        ### to their values

        self.input_sockets = self.input_socket_live_flmap.flat_values

        self.subparam_up_buttons = self.subparam_up_button_flmap.flat_values

        self.subparam_down_buttons = self.subparam_down_button_flmap.flat_values

        self.placeholder_sockets = self.placeholder_socket_live_map.values()

        self.placeholder_add_buttons = self.placeholder_add_button_map.values()

        self.live_widgets = self.widget_live_flmap.flat_values

        self.widget_add_buttons = self.widget_add_button_flmap.flat_values

        self.widget_remove_buttons = self.widget_remove_button_flmap.flat_values

        self.unpacking_icons = self.subparam_unpacking_icon_flmap.flat_values

        self.live_keyword_entries = self.subparam_keyword_entry_live_map.values()

        ### create and store a map to hold rects manager
        ### instances for each group of objects related to
        ### a specific parameter
        self.param_rectsman_map = {}

        ### create and store a map to hold rects manager
        ### instances for each group of objects related to
        ### a specific subparameter
        self.subparam_rectsman_map = {}

        ### iterate over each parameter, instantiating its
        ### related widgets

        parameters = self.signature_obj.parameters.values()

        for param_obj in parameters:

            ## manage socket(s) and widget(s) creation
            ## for parameter depending on whether the
            ## parameter is of variable kind or not

            if param_obj.name in self.var_kind_map:
                self.create_var_parameter_objs(param_obj)

            else:
                self.create_parameter_objs(param_obj)

        ### execute the update method on the maps created,
        ### so the list in their flat_values attribute is
        ### updated

        self.input_socket_live_flmap.update()
        self.widget_live_flmap.update()

        ### if there are indeed parameters, create a rects
        ### manager instance to control the position of all
        ### the input related objects

        if parameters:

            get_param_rectsmans = [
                item for item in self.param_rectsman_map.values()
            ].__iter__

            self.input_rectsman = RectsManager(get_param_rectsmans)

        ### update values in flat list dict instances
        ### related to subparameters

        self.widget_add_button_flmap.update()
        self.widget_remove_button_flmap.update()

        self.subparam_up_button_flmap.update()
        self.subparam_down_button_flmap.update()

    def create_output_sockets(self):
        """Instantiate and store output sockets."""
        ### create a new dictionary holding output socket
        ### instances mapped to the name of the output
        ### they represent (also reference it locally);
        ###
        ### here we use key-value pairs from the ordered
        ### output map, which is an ordered dict where
        ### each key is the name of the output and the
        ### value is the expected type of the output to be
        ### sent;
        ###
        ### the value is called "expected type" because
        ### the type isn't enforced, it only serves to
        ### indicate which type to expected, just like
        ### regular type hints in Python, but in this
        ### case for return values instead of parameters

        self.output_socket_live_map = {
            output_name: OutputSocket(
                node=self,
                output_name=output_name,
                type_codename=(type_to_codename(expected_type)),
            )
            for output_name, expected_type in self.ordered_output_type_map.items()
        }

        ### also store a view of its values in a
        ### dedicated attribute

        self.output_sockets = self.output_socket_live_map.values()

        ### gather the rects of the output sockets in a list
        ### in order to use its __iter__ method to create a
        ### rects manager instance which you'll use to
        ### control the rects (and thus the position of the
        ### sockets

        ## reference output sock live map locally
        osl_map = self.output_socket_live_map

        ## create mentioned list

        rect_list = [
            osl_map[output_name].rect
            for output_name in self.ordered_output_type_map.keys()
        ]

        ## finally, instantiate and store the rects
        ## manager
        self.output_rectsman = RectsManager(rect_list.__iter__)

    def create_bottom_objects(self):
        """Create objects that lie at the node's bottom."""
        ### create and position foot and remaining corners
        ### using imported surfaces
        ###
        ### the actual surfaces used for the foot and
        ### bottom corners might change if the node is
        ### currently commented out, but we we don't need
        ### to worry about it here (this is taken care of
        ### in another module)

        ## foot

        self.foot = Object2D()
        self.foot.image = NORMAL_NODE_FOOT
        self.foot.rect = self.foot.image.get_rect()

        ## corners

        # bottomleft corner

        bottomleft_corner = Object2D()
        bottomleft_corner.image = NORMAL_BOTTOM_CORNERS[0]
        bottomleft_corner.rect = bottomleft_corner.image.get_rect()
        bottomleft_corner.rect.topright = self.foot.rect.topleft

        # bottomright corner

        bottomright_corner = Object2D()
        bottomright_corner.image = NORMAL_BOTTOM_CORNERS[1]
        bottomright_corner.rect = bottomright_corner.image.get_rect()
        bottomright_corner.rect.topleft = self.foot.rect.topright

        self.corners.append(bottomleft_corner)
        self.corners.append(bottomright_corner)

        ### create and store a rects manager to manage the
        ### position of the objects on the bottom of the
        ### node

        ## get a callable which returns the rects to be
        ## managed

        get_bottom_rects = (
            bottomleft_corner.rect,
            bottomright_corner.rect,
            self.foot.rect,
        ).__iter__

        ## use it to instantiate the rects manager and
        ## store it on its own attribute
        self.bottom_rectsman = RectsManager(get_bottom_rects)

    def create_node_id_text(self):
        """Create text object to representing node's id.

        It won't be positioned yet, just created for now.
        """
        ### instantiate

        self.id_text_obj = Object2D.from_surface(
            render_text(
                ### use node id as the text
                text=" {} ".format(self.id),
                # font settings (note that we use the
                # foot width as the max width)
                font_height=FONT_HEIGHT,
                foreground_color=NODE_TITLE,
                background_color=self.category_color,
                border_thickness=1,
                border_color=BLACK,
                max_width=self.foot.rect.width,
            )
        )
