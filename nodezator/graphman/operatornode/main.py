### local imports

from ...config import APP_REFS

from ...ourstdlibs.meta import initialize_bases


### class extensions

from .vizprep import (
    VisualRelatedPreparations,
)

from .vizop import (
    VisualRelatedOperations,
)

from .execution import Execution

from .export import Exporting

from .constants import (
    OPERATIONS_MAP,
    OPERATIONS_SIGNATURE_MAP,
    OPERATION_ID_TO_SUBSTITUTION_CALLABLE_MAP,
    OPERATION_ID_TO_SOURCE_VIEW_TEXT,
)


class OperatorNode(
    VisualRelatedPreparations,
    VisualRelatedOperations,
    Execution,
    Exporting,
):
    """A node representing a variable within a script."""

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

        ### initialize base classes which have an __init__
        ### method of their own
        initialize_bases(self)

    def get_source_info(self):
        """Return information about node source."""

        return OPERATION_ID_TO_SOURCE_VIEW_TEXT[self.data["operation_id"]]
