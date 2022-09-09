"""Facility for OOP implementation of appcommon.grid.main."""


### third-party imports

from pygame import Rect

from pygame.draw import line as draw_line


### local imports

from .main import (
    enforce_multiple,
    generate_grid_lines,
    move_grid_lines_along_axis,
)


class ScrollableGrid(object):
    """Grid object with grid line scrolling feature."""

    def __init__(
        self,
        screen,
        line_width,
        color,
        unit_rect,
        area_rect,
    ):
        """Generate and store grid-like lines.

        Works by generating and operating pairs of
        pygame.math.Vector2 objects which represent a line,
        that is,(the start and end points of a line.

        Once the class is instantiated, the resulting
        object can blit its lines on a surface to form
        a grid and can also move its lines as if the
        grid was scrolling.

        The scrolling movement always warps lines which go
        out of the boundaries to the opposite side of the
        grid so that the grid can be scrolled indefinitely.

        screen
            Any pygame.Surface instance where you want the
            lines of the grid blit.
        line_width
            Width of grid lines in pixels.
        color
            3-tuple of integers representing red, green and
            blue values respectively, from 0 to 255. List or
            pygame.Color instance are also allowed.
        unit_rect
            pygame.Rect instance representing an unit in the
            grid.
        area_rect
            pygame.Rect instance representing the area
            covered by the grid.
        """
        ### enforce "multiple-of" relationship between
        ### unit rect and area rect dimensions
        self.unit_rect, self.area_rect = enforce_multiple(unit_rect, area_rect)

        ### store remaining data

        self.screen = screen
        self.line_width = line_width
        self.color = color

        ### generate and store grid lines in both
        ### orientations

        self.h_lines, self.v_lines = generate_grid_lines(
            self.unit_rect, self.area_rect, use_vectors=True, separate_orientation=True
        )

        ## also reference all lines in a single list
        self.all_lines = [*self.h_lines, *self.v_lines]

    def draw(self):
        """Draw lines on screen."""

        for point_pair in self.all_lines:

            draw_line(
                self.screen,
                self.color,
                *point_pair,
                self.line_width,
            )

    def scroll(self, dx, dy):
        """Scroll line vectors relative to dx and dy amounts.

        dx, dy
            Integers representing amount in pixels of a
            movement in the x and y axes, respectively.
        """
        ### scroll grid vertical lines

        if dx:
            move_grid_lines_along_axis(
                self.v_lines, "x", dx, self.unit_rect, self.area_rect
            )

        ### scroll grid horizontal lines

        if dy:
            move_grid_lines_along_axis(
                self.h_lines, "y", dy, self.unit_rect, self.area_rect
            )
