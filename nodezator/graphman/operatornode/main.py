### local imports

from ...config import APP_REFS

from ...ourstdlibs.meta import initialize_bases

from ...our3rdlibs.behaviour import indicate_unsaved

from ...iconfactory import ICON_MAP


### class extensions

from .vizprep import VisualRelatedPreparations

from .vizop import VisualRelatedOperations

from .execution import Execution

from .export import Exporting

from .constants import (
    OPERATIONS_MAP,
    OPERATIONS_SIGNATURE_MAP,
    OPERATION_ID_TO_SUBSTITUTION_CALLABLE_MAP,
    OPERATION_ID_TO_SOURCE_VIEW_TEXT,
)



EMPTY_TUPLE = ()


class OperatorNode(
    VisualRelatedPreparations,
    VisualRelatedOperations,
    Execution,
    Exporting,
):
    """A node representing a variable within a script."""

    normal_icon = ICON_MAP['operation_node']
    commented_out_icon = ICON_MAP['commented_out_operation_node']

    ###
    available_ids = OPERATIONS_MAP.keys()

    def __init__(self, data, midtop=None):
        """Setup attributes for storage and control.

        Parameters
        ==========

        data (dict)
            data representing this node instance.
        midtop (2-tuple of integers; or None)
            represents the absolute midtop position of
            the node on screen. If no midtop is received
            (the default None is used), then the midtop
            information is retrieved from the node data.
        """
        ### retrieve and store the main callable obj in
        ### its own attribute, also aliasing it as the
        ### signature callable

        self.signature_callable = self.main_callable = OPERATIONS_MAP[
            data["operation_id"]
        ]

        ### retrieve and store the signature object
        self.signature_obj = OPERATIONS_SIGNATURE_MAP[data["operation_id"]]

        ### retrieve and store the substitution callable

        self.substitution_callable = OPERATION_ID_TO_SUBSTITUTION_CALLABLE_MAP[
            data["operation_id"]
        ]

        ### use the operation_id as the title text
        self.title_text = data["operation_id"]

        ### store the instance data argument in its own
        ### attribute
        self.data = data

        ### store node id in its own attribute for easy
        ### access
        self.id = data["id"]

        ### store the midtop position

        self.midtop = midtop if midtop is not None else data["midtop"]

        ### create control to indicate when the node was
        ### subject to mouse click
        self.mouse_click_target = False

        ### create visuals of the node
        self.create_visual_elements()

        ### set mode

        self.set_mode(
            self.data.get('mode', 'expanded_signature'),
            indicate_changes=False,
            first_setup=True,
        )

        ### initialize base classes which have an __init__
        ### method of their own
        initialize_bases(self)

    def set_mode(self, mode_name, indicate_changes=True, first_setup=False):

        current_mode_name = self.data.get('mode', 'expanded_signature')

        ### if this is not the first mode setup and the requested and
        ### current mode are the same, prevent the method to execute by
        ### exiting

        if not first_setup and (mode_name == current_mode_name):
            return

        ### set mode

        if mode_name == 'expanded_signature':

            if current_mode_name == 'callable':
                APP_REFS.gm.sever_all_connections(self)

            self.input_sockets = self.signature_input_sockets
            self.output_sockets = self.signature_output_sockets
            self.output_socket = self.signature_output_socket

            self.visual_objects = self.signature_visual_objects

            self.rectsman = self.signature_rectsman

        elif mode_name == 'collapsed_signature':
            ## operator nodes don't have collapsed signature mode
            return

        elif mode_name == 'callable':

            if current_mode_name == 'expanded_signature': 
                APP_REFS.gm.sever_all_connections(self)

            self.input_sockets = EMPTY_TUPLE
            self.output_sockets = self.callable_output_sockets
            self.output_socket = self.callable_output_socket

            self.visual_objects = self.callable_visual_objects

            self.rectsman = self.callable_rectsman

        ###
        self.data['mode'] = mode_name

        ###
        self.update_body_surface()
        self.update_label_surface()
        self.reposition_elements()

        ### if requested, indicate that changes were made and that
        ### the birdseye view state of window manager must have its
        ### objects updated next time it is set

        if indicate_changes:

            indicate_unsaved()
            APP_REFS.ea.must_update_birdseye_view_objects = True

    def get_source_info(self):
        """Return information about node source."""
        return OPERATION_ID_TO_SOURCE_VIEW_TEXT[self.data["operation_id"]]
