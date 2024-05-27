"""Facility for visuals related node class extension."""

### local imports

from ...surfs import (
    NORMAL_NODE_FOOT,
    COMMENTED_OUT_NODE_FOOT,
    NORMAL_BOTTOM_CORNERS,
    COMMENTED_OUT_BOTTOM_CORNERS,
    UNPACKING_ICON_SURFS_MAP,
)

## functions for injection

from .expandedcreation import get_expanded_body_surface
from .collapsedcreation import get_collapsed_body_surface
from .callablecreation import get_callable_body_surface


class BodySetupOperations:
    """Operations to set up body and other related setups.

    Class extension for the VisualPreparations class.
    """

    get_expanded_body_surface = get_expanded_body_surface
    get_collapsed_body_surface = get_collapsed_body_surface
    get_callable_body_surface = get_callable_body_surface

    ### convenience methods to execute combinations of
    ### modular operations for specific purposes

    ## for when body is instantiated

    def setup_body(self):
        """Performs several adjustments to the body."""
        self.reset_body_height_and_image()
        self.assign_bottom_surfaces()

    ## for when node is commented out/uncommented

    def perform_commenting_uncommenting_setups(self):
        """Performs several adjustments to the body."""
        ###
        self.assign_bottom_surfaces()

        ### create and store the body's surface
        self.body.image = self.create_body_surface()

        ###
        self.assign_unpacking_icon_surfs()

        ###
        self.pick_tiny_icon()

    ### methods representing modular operations

    def reset_body_height_and_image(self):
        """Calculate and set body height and create new image."""
        ### the body height is equivalent to the interval
        ### between the top rectsman's bottom and the bottom
        ### rectsman's top
        self.body.rect.height = self.bottom_rectsman.top - self.top_rectsman.bottom

        ### create and store a new surface for the body
        self.body.image = self.create_body_surface()

    def assign_bottom_surfaces(self):
        """Assign proper surfaces to node's bottom objects.

        Such bottom objects are the node's foot and bottom
        corners.

        Such surfaces are chosen based on whether the node
        is commented out or uncommented.
        """
        ### update the surfaces at the bottom of the node
        ### depending on the commented out state

        ## reference the bottom corner objects
        ##
        ## there's no need to do so for the foot, since
        ## there's an attribute which already references
        ## it
        bottomleft_corner, bottomright_corner = self.corners[2:]

        ## assign the appropriate surfaces to the 'image'
        ## attribute of the respective objects

        (self.foot.image, bottomleft_corner.image, bottomright_corner.image) = (
            ## surfaces for commented out nodes,
            ## when the node is commented out
            (COMMENTED_OUT_NODE_FOOT, *COMMENTED_OUT_BOTTOM_CORNERS)
            if self.data.get("commented_out", False)
            ## otherwise, surfaces for uncommented nodes
            else (NORMAL_NODE_FOOT, *NORMAL_BOTTOM_CORNERS)
        )

    def assign_unpacking_icon_surfs(self):
        """Assign proper surfaces to unpacking icons, if any."""
        if not self.var_kind_map:
            return

        is_commented_out = self.data.get("commented_out", False)

        for param_name, param_kind in self.var_kind_map.items():

            for button in self.subparam_unpacking_icon_flmap[param_name].values():

                button.image = UNPACKING_ICON_SURFS_MAP[(param_kind, is_commented_out)]

    def pick_tiny_icon(self):

        self.tiny_icon = getattr(
            self,
            (
                'commented_out_icon'
                if self.data.get('commented_out', False)

                else 'normal_icon'
            ),
        )
