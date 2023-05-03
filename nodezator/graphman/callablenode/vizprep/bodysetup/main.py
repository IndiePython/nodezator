"""Facility for visuals related node class extension."""

### local imports

from ...surfs import (
    NORMAL_NODE_FOOT,
    COMMENTED_OUT_NODE_FOOT,
    NORMAL_BOTTOM_CORNERS,
    COMMENTED_OUT_BOTTOM_CORNERS,
    UNPACKING_ICON_SURFS_MAP,
)

## function for injection
from .creation import create_body_surface


class BodySetupOperations:
    """Operations to set up body and other related setups.

    Class extension for the VisualRelatedPreparations class.
    """

    create_body_surface = create_body_surface

    ### convenience methods to execute combinations of
    ### modular operations for specific purposes

    ## for when body is instantiated

    def setup_body(self):
        """Performs several adjustments to the body."""
        self.perform_body_height_change_setups()
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

    ### methods representing modular operations

    def perform_body_height_change_setups(self):
        """Calculate and set body height.

        The body height is obtained from the difference
        between the top of the node's bottom and the bottom
        of the node's top.
        """
        ### the body height is equivalent to the interval
        ### between the top rectsman's bottom and the bottom
        ### rectsman's top

        new_body_height = self.bottom_rectsman.top - self.top_rectsman.bottom

        ### store the current height locally
        current_body_height = self.body.rect.height

        ### if the new body height is indeed different than
        ### the current one...

        if new_body_height != current_body_height:

            ### update the height of the body's rect
            self.body.rect.height = new_body_height

            ### create and store the body's surface
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
