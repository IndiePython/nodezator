"""Class extension for preparation of visual objects."""

### third-party import
from pygame import Rect


### local imports

from ....config import APP_REFS

from ....classes2d.single import Object2D

from ....textman.render import render_text

from ....rectsman.main import RectsManager

from ....iconfactory import ICON_MAP

from ....colorsman.colors import (
    NODE_CATEGORY_COLORS,
    NODE_TITLE,
    BLACK,
)

from ..constants import FONT_HEIGHT, NODE_WIDTH


## class extensions

from .bodysetup.main import BodySetupOperations

from .sigmode import SignatureModeVisualPreparations
from .calmode import CallableModeVisualPreparations


## other objects for composition

from ..surfs import (
    NODE_ROOFS_MAP,
    TOP_CORNERS_MAP,
    NORMAL_BOTTOM_CORNERS,
    NORMAL_NODE_FOOT,
    SIGMODE_TOGGLE_BUTTON_MAP,
)


class VisualPreparations(
    BodySetupOperations,
    SignatureModeVisualPreparations,
    CallableModeVisualPreparations,
    ):
    """Manages creation and setup of node visuals."""

    ### define remaining methods

    def create_visual_elements(self):
        """Create visual elements for node."""
        ### start by storing the nodes category color
        self.store_category_color_data()

        ### reference and pick tiny icons representing this node when
        ### commented out or not

        self.reference_tiny_icons()
        self.pick_tiny_icon()

        ### create elements situated on top of the node
        self.create_top_objects()

        ### create title of node
        self.create_title_object()

        ### create sigmode toggle button
        self.create_sigmode_toggle_button()

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
        ### of the node
        self.rect = Rect(0, 0, 0, 0)

        ### create expanded signature mode visuals
        self.create_exp_mode_visual_elements()

        ### create collapsed signature mode visuals
        self.create_col_mode_visual_elements()

        ### create callable mode visuals
        self.create_callable_mode_visual_elements()


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

    def reference_tiny_icons(self):
        """Reference tiny icons representing the node.

        Icons represent node in commented out and normal state.

        Icons are used when displaying a bird's eye view of the graph.
        """
        index = self.color_index

        normal_key = f'color_index_{index}_node'
        commented_out_key = f'commented_out_{normal_key}'

        self.normal_icon = ICON_MAP[normal_key]
        self.commented_out_icon = ICON_MAP[commented_out_key]

    def create_top_objects(self):
        """Create objects that lie on top of the node."""
        ### create and position roof and top corner objects
        ### using surfaces from imported maps

        ## roof

        roof = self.roof = Object2D()
        roof.image = NODE_ROOFS_MAP[self.category_color]
        roof.rect = roof.image.get_rect()

        ## create list to store corners
        self.corners = []

        # topleft corner

        topleft_corner = Object2D()
        topleft_corner.image = TOP_CORNERS_MAP[self.category_color][0]

        topleft_corner.rect = topleft_corner.image.get_rect()

        topleft_corner.rect.topright = roof.rect.topleft

        # topright corner

        topright_corner = Object2D()
        topright_corner.image = TOP_CORNERS_MAP[self.category_color][1]

        topright_corner.rect = topright_corner.image.get_rect()

        topright_corner.rect.topleft = roof.rect.topright

        self.corners.append(topleft_corner)
        self.corners.append(topright_corner)

        ### store a rects manager to manage the position
        ### of the objects on top of the node

        ## get a callable which returns the rects to be
        ## managed

        get_top_rects = (
            roof.rect,
            topleft_corner.rect,
            topright_corner.rect,
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

    def create_sigmode_toggle_button(self):
        """Instatiate button to toggle between signature modes."""
        button = self.sigmode_toggle_button = Object2D()
        button.image = SIGMODE_TOGGLE_BUTTON_MAP[self.category_color][0]
        button.rect = button.image.get_rect()
        button.rect.topleft = self.top_rectsman.move(2, 0).bottomleft
        button.on_mouse_release = self.toggle_sigmode

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
