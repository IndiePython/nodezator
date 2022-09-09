### local imports

## class extensions

from .vizprep import (
    VisualRelatedPreparations,
)

from .vizop.main import (
    VisualRelatedOperations,
)

from .widget import WidgetOps

from .segment import SegmentOps

from .export import Exporting

## function for injection
from .titleupdate import update_title


class ProxyNode(
    VisualRelatedPreparations,
    VisualRelatedOperations,
    WidgetOps,
    SegmentOps,
    Exporting,
):
    """Represents a data source within a script.

    Such data source can be a variable or the output
    from other node.
    """

    update_title = update_title

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
        ### store the instance data argument in its own
        ### attribute
        self.data = data

        ### set a 'title' key on the data if not present
        ### yet;
        ###
        ### it is important that the default value here
        ### is 'output', because it is the default
        ### output name of OutputSockets used before
        ### the titles of data nodes became editable,
        ### so it is needed in order not to break things;

        if "title" not in self.data:
            self.data["title"] = "output"

        ### store some values from the node data in their
        ### own attributes for easy access

        for attr_name in ("id", "title"):
            setattr(self, attr_name, self.data[attr_name])

        ### store the midtop position

        self.midtop = midtop if midtop is not None else self.data["midtop"]

        ### create control to indicate when the node was
        ### subject to mouse click
        self.mouse_click_target = False

        ### create visuals of the node
        self.create_visual_elements()
