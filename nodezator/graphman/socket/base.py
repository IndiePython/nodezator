
from classes2d.single import Object2D


class Socket(Object2D):
    """Base class for representing nodes."""

    def __repr__(self):
        """Return an unambiguous string representation."""
        return '{}()'.format(self.__class__.__name__)

    def on_mouse_click(self, event):
        """Trigger segment definition behaviour.

        Works by triggering behaviours related to defining
        line segments and resulting links between sockets.
        """
        (
          self
          .node
          .graph_manager
          .trigger_defining_segment(self)
        )
