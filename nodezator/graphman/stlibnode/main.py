"""Facility for node class definition."""

### standard library import
from itertools import takewhile


### local imports

from .constants import (
    STLIB_IDS_TO_CALLABLES_MAP,
    STLIB_IDS_TO_SIGNATURES_MAP,
    STLIB_IDS_TO_SIGNATURE_CALLABLES_MAP,
    STLIB_IDS_TO_STLIB_IMPORT_TEXTS,
    STLIB_IDS_TO_SOURCE_VIEW_TEXT,
)

from ...colorsman.colors import STANDARD_LIB_NODES_CATEGORY_COLOR

## superclass
from ..callablenode.main import CallableNode


class StandardLibNode(CallableNode):
    """Handles callables from Python standard library."""

    category_color = STANDARD_LIB_NODES_CATEGORY_COLOR
    available_ids = STLIB_IDS_TO_CALLABLES_MAP.keys()

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
        ### its own attribute
        self.main_callable = STLIB_IDS_TO_CALLABLES_MAP[data["stlib_id"]]

        ### also retrieve and store the callable used to
        ### obtain the signature

        signature_callable = (
            self.signature_callable
        ) = STLIB_IDS_TO_SIGNATURE_CALLABLES_MAP[data["stlib_id"]]

        ### store import statement text
        self.stlib_import_text = STLIB_IDS_TO_STLIB_IMPORT_TEXTS[data["stlib_id"]]

        ### set title text

        self.title_text = "".join(
            takewhile(
                lambda c: c != "(",
                data["stlib_id"],
            )
        )

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
        self.reference_related_maps(signature_callable)

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

        ### initialize execution-related objects
        self.create_execution_support_objects()

    def get_signature(self):
        """Return signature for callable used in the node.

        Overrides super().get_signature().
        """
        return STLIB_IDS_TO_SIGNATURES_MAP[self.data["stlib_id"]]

    def get_color_identifier(self):
        """Return specific color identifier.

        Overrides super().get_color_identifier().
        """
        return "stlib_node"

    def store_category_color_data(self):
        """Do nothing.

        This function only needs to exist in order
        to override super().store_category_color_data().

        This is because the relevant category color
        data is already set as a class attribute.
        """

    def get_source_info(self):
        """Return information about node source."""

        return STLIB_IDS_TO_SOURCE_VIEW_TEXT[self.data["stlib_id"]]
