"""Facility for node class definition."""

### local imports

from ...ourstdlibs.behaviour import empty_oblivious_function

from ...iconfactory import ICON_MAP

from ...colorsman.colors import GENVIEWER_NODES_CATEGORY_COLOR

from .constants import (
    GENVIEWER_IDS_TO_CALLABLES_MAP,
    GENVIEWER_IDS_TO_SIGNATURES_MAP,
    GENVIEWER_IDS_TO_3RDLIB_IMPORT_MAP,
    GENVIEWER_IDS_TO_SOURCE_VIEW_TEXT,
)

## superclass
from ..callablenode.main import CallableNode

## function for injection
from .export import get_source_to_export



class GeneralViewerNode(CallableNode):
    """Handles callables defining general viewer nodes."""

    ### class attributes

    category_color = GENVIEWER_NODES_CATEGORY_COLOR

    normal_icon = ICON_MAP['default_node']
    commented_out_icon = ICON_MAP['commented_out_default_node']
    reference_tiny_icons = empty_oblivious_function

    available_ids = GENVIEWER_IDS_TO_CALLABLES_MAP.keys()

    ### injected function
    get_source_to_export = get_source_to_export

    ###

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
        ### retrieve and store the callable obj, aliasing
        ### it with different names, according to its
        ### roles in the node (both the main and signature
        ### callable)

        signature_callable = (
            self.signature_callable
        ) = self.main_callable = (
            GENVIEWER_IDS_TO_CALLABLES_MAP[data["genviewer_id"]]
        )

        ### if there are third-party imports associated with
        ### the id, store them

        try:
            self.thirdlib_import_texts = GENVIEWER_IDS_TO_3RDLIB_IMPORT_MAP[
                data["genviewer_id"]
            ]

        except KeyError:
            pass

        ### use the genviewer_id as the title text
        self.title_text = data["genviewer_id"]

        ### store the instance data argument in its own
        ### attribute
        self.data = data

        ### perform inspections/setups related to the
        ### callable used for its signature and its
        ### metadata as needed

        ## the inspection is performed only once for each
        ## different callable. Thus, if another node
        ## instance is created with the same signature
        ## callable, it will use the already created data,
        ## shared through class attributes

        if signature_callable not in self.__class__.preprocessed_callables:
            self.inspect_callable_object(signature_callable)

        ### reference maps from class attributes in
        ### instance; maps are related to the signature
        ### callable obj and are shared accross all node
        ### instances which use the same signature callable
        ### obj
        self.reference_related_data(signature_callable)

        ### check whether there's data needed
        ### to be set in the instance data
        self.set_data_defaults()

        ### store the id in its own attribute for easy
        ### access
        self.id = self.data["id"]

        ### store the midtop position

        self.midtop = midtop if midtop is not None else self.data["midtop"]

        ### create control to indicate when the node was
        ### subject to mouse click
        self.mouse_click_target = False

        ### create visuals of the node
        self.create_visual_elements()

        ### since all instances of this class are viewer nodes, it is
        ### guaranteed that functions from the viewer node protocol are
        ### available, so just create related objects

        self.create_preview_toolbar()
        self.create_preview_panel()

        ### set mode

        self.set_mode(
            self.data.get('mode', 'expanded_signature'),
            indicate_changes=False,
            first_setup=True,
        )

        ### initialize execution-related objects
        self.create_execution_support_objects()

    def get_signature(self):
        """Return signature for callable used in the node.

        Overrides super().get_signature().
        """
        return GENVIEWER_IDS_TO_SIGNATURES_MAP[self.data["genviewer_id"]]

    def get_color_identifier(self):
        """Return specific color identifier.

        Overrides super().get_color_identifier().
        """
        return "genviewer_node"

    def store_category_color_data(self):
        """Do nothing.

        This function only needs to exist in order
        to override super().store_category_color_data().

        This is because the relevant category color
        data is already set as a class attribute.
        """

    def get_source_info(self):
        """Return information about node source."""
        return GENVIEWER_IDS_TO_SOURCE_VIEW_TEXT[self.data["genviewer_id"]]
