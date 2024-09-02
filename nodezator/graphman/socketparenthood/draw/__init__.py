"""Facility with class extension with drawing operations."""

### third-party import
from pygame.draw import line as draw_line


### local imports

from ....pygamesetup import SERVICES_NS, SCREEN

from ....colorsman.colors import CUTTING_SEGMENT

from ....userprefsman.main import USER_PREFS

from ..utils import clip_segment

from .connectionassist import CONNECTION_ASSISTING_DRAWING_METHODS_MAP



class DrawingOperations:
    """Drawing operations for the socket trees."""

    ### inject methods

    for method in CONNECTION_ASSISTING_DRAWING_METHODS_MAP.values():
        locals()[method.__name__] = method

    ###

    def reference_socket_detection_graphics(self):

        graphics_setting_name = USER_PREFS['SOCKET_DETECTION_GRAPHICS']

        method_name = (
            CONNECTION_ASSISTING_DRAWING_METHODS_MAP
            [graphics_setting_name]
            .__name__
        )

        self.draw_temp_segment = getattr(self, method_name)

    def draw_lines(self):
        """Draw lines which cross the screen."""

        for parent in self.parents:

            parent_center = parent.rect.center
            segment_color = parent.line_color

            for child in parent.children:

                try:
                    start, end = clip_segment(
                        parent_center,
                        child.rect.center,
                    )

                except ValueError:
                    pass

                else:

                    draw_line(
                        SCREEN,
                        segment_color,
                        start,
                        end,
                        4,
                    )

    def draw_temp_cutting_segment(self):
        """Draw temporary segment between point and mouse.

        Used while defining a line segment which will cut
        all segments which are crossed by it. This draws
        a line from the position in the 'cut_start_pos'
        attribute)to the current mouse position.
        """
        ### since in the state this is executed there can
        ### be no scrolling, the points are always on the
        ### screen, so there's no need to clip them to
        ### the screen, you can retrieve and draw them
        ### right away

        draw_line(
            SCREEN,
            CUTTING_SEGMENT,
            self.cut_start_pos,  # start
            SERVICES_NS.get_mouse_pos(),  # end
            3,
        )
