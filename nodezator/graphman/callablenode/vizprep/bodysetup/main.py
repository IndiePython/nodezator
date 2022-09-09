"""Facility for visuals related node class extension."""

### local imports

from ...surfs import (
    NORMAL_NODE_FOOT,
    COMMENTED_OUT_NODE_FOOT,
    NORMAL_BOTTOM_CORNERS,
    COMMENTED_OUT_BOTTOM_CORNERS,
    NO_VARPARAM_NODE_BODY_MAP,
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
        self.assign_bottom_surfaces()
        self.assign_body_surface()
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

            ### assign a proper body surface for
            ### the node
            self.assign_body_surface()

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

    def assign_body_surface(self):
        """Assign an appropriate surface for the body.

        Such surface may already exist or not.

        The surface will be stored on self.body.image.
        The self.body object serves as a background for
        the midsection of the node and has areas with
        different colors and also text blitted on it
        to indicate parameters and outputs of the node.

        Executed in one of either scenarios:

        1) body height changes (when node is instantiated
           or number of subparameters change)
        2) body appearance changes (when node is commented
           out or uncommented)

        When the node's callable has no variable parameters,
        the body surfaces for the respective "commented out"
        states (either "commented out" or "uncommented") are
        created only once, when necessary, and shared between
        all nodes in the respective states using that same
        callable.

        This is so because nodes whose callables have no
        parameters of variable kind never change their size,
        since the nodes always use the same combination of
        internal objects (sockets, widgets or lack thereof,
        etc.).

        because of that, such nodes can share the same body
        surfaces for the 02 states (commented out or not)
        between all nodes which use the same callable.
        """
        ### also create a tuple containing a reference to
        ### the node's signature calalble obj and the value
        ### of its commented out state to use as a key to
        ### obtain body surfaces
        ###
        ### this key only ends up being relevant if the
        ### node's callable has no variable parameters

        body_surf_key = (self.signature_callable, self.data.get("commented_out", False))

        ### check whether the callable of the node in the
        ### current state (commented out or not) has an
        ### existing body surface associated with it, by
        ### trying to retrieve it from a special map;
        ###
        ### only body surfaces of nodes whose callables
        ### don't have parameters of variable kind end up
        ### in the map below, after being created for the
        ### first time;
        ###
        ### for more info about this, check this method's
        ### docstring

        try:
            body_surf = NO_VARPARAM_NODE_BODY_MAP[body_surf_key]

        ### if it hasn't, we will go ahead and create the
        ### surface

        except KeyError:

            body_surf = self.create_body_surface()

            ### if this node's callable has no parameters of
            ### variable kind, also store the body surface
            ### in the surface map created for such purpose
            ###
            ### this way, the next time a node using the
            ### same callable is created we can grab the
            ### surface right away instead of creating it
            ### again, which saves memory and speeds up
            ### execution of this method by skipping the
            ### body surface creation in the next time it is
            ### executed

            if not self.var_kind_map:
                NO_VARPARAM_NODE_BODY_MAP[body_surf_key] = body_surf

        ### finally, store such surface as the body surface
        self.body.image = body_surf

    def assign_unpacking_icon_surfs(self):
        """Assign proper surfaces to unpacking icons, if any."""
        if not self.var_kind_map:
            return

        is_commented_out = self.data.get("commented_out", False)

        for param_name, param_kind in self.var_kind_map.items():

            for button in self.subparam_unpacking_icon_flmap[param_name].values():

                button.image = UNPACKING_ICON_SURFS_MAP[(param_kind, is_commented_out)]
