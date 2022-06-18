
### class extensions

from graphman.proxynode.vizprep import (
                                VisualRelatedPreparations,
                              )

from graphman.proxynode.vizop.main import (
                                 VisualRelatedOperations,
                               )

from graphman.proxynode.widget import WidgetOps

from graphman.proxynode.segment import SegmentOps

from graphman.proxynode.export import Exporting


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

    ### placeholders for class attributes

    graph_manager              = None
    widget_creation_popup_menu = None

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

        ### store some values from the node data in their
        ### own attributes for easy access

        for attr_name in ('id', 'label_text'):
            setattr(self, attr_name, self.data[attr_name])

        ### store the midtop position

        self.midtop = (

          midtop
          if midtop is not None 

          else self.data['midtop']

        )

        ### create controls to indicate when the node was
        ### subject to mouse events

        self.mouse_release_target = False
        self.mouse_click_target   = False

        ### create visuals of the node
        self.create_visual_elements()
