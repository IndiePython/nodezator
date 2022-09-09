"""SocketTree extension with export support."""

### standard library import
from xml.etree.ElementTree import Element

### third-party import
from pygame.draw import line as draw_line


class ExportOperations:
    """Exporting operations for the socket tree."""

    def yield_lines_as_svg(self):
        """Yield lines as svg elements.

        Used when representing lines as svg lines
        when exporting the node graph to a .svg file.
        """
        for parent in self.parents:

            x1_str, y1_str = map(str, parent.rect.center)

            for child in parent.children:

                x2, y2 = child.rect.center

                yield Element(
                    "line",
                    {
                        "x1": x1_str,
                        "y1": y1_str,
                        "x2": str(x2),
                        "y2": str(y2),
                        "class": parent.svg_class_name,
                    },
                )

    def draw_lines_on_surf(self, surf):
        """Draw lines on provided surf.

        Used when drawing lines on another surface
        when exporting the node graph to an image file.
        """
        for parent in self.parents:

            parent_center = parent.rect.center
            segment_color = parent.line_color

            for child in parent.children:

                start, end = (parent_center, child.rect.center)

                draw_line(
                    surf,
                    segment_color,
                    parent_center,  # start
                    child.rect.center,  # end
                    4,  # width
                )
