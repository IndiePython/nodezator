"""Facility with class extension with drawing operations."""

### third-party imports

from pygame.mouse import get_pos as get_mouse_pos
from pygame.draw import line as draw_line


### local imports

from ...pygameconstants import SCREEN

from .utils import clip_segment

from ...colorsman.colors import CUTTING_SEGMENT


class DrawingOperations:
    """Drawing operations for the socket trees."""

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

    def draw_temp_segment(self):
        """Draw temporary segment between point and mouse.

        Used while defining a new line segment. This draws
        a line from 'socket a' (the socket from where the
        line segment will be defined) to the current mouse
        position.
        """
        try:
            start, end = clip_segment(
                self.socket_a.rect.center,
                get_mouse_pos(),
            )

        except ValueError:
            pass

        else:

            draw_line(
                SCREEN,
                self.socket_a.line_color,
                start,
                end,
                3,
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
            get_mouse_pos(),  # end
            3,
        )
