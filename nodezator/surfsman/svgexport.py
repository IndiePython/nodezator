
### standard library import
from xml.etree.ElementTree import Element


### local imports

from ..colorsman.colors import (
    IMAGE_NOT_FOUND_FG,
    IMAGE_NOT_FOUND_BG,
)

from .mathutils import get_segment_points_cutting_ellipse



GENERAL_SURFACES_CSS = f"""

g.file_not_found_shapes > rect {{
  fill: rgb{IMAGE_NOT_FOUND_BG};
  stroke: none;
}}

g.file_not_found_shapes > ellipse {{
  stroke: rgb{IMAGE_NOT_FOUND_FG};
  stroke-width: 15px;
  fill:none;
}}

g.file_not_found_shapes > line {{
  stroke: rgb{IMAGE_NOT_FOUND_FG};
  stroke-width: 15px;
}}

"""


def get_not_found_surface_svg_repr(rect):

    g = Element("g", {"class": "file_not_found_shapes"})

    g.append(
        Element(
            "rect",
            {
                **{
                    attr_name: str(getattr(rect, attr_name))
                    for attr_name in ("x", "y", "width", "height")
                },
            },
        ),
    )

    ellipse_rect = rect.inflate(-16, -16)

    g.append(
        Element(
            "ellipse",
            {
                "cx": str(ellipse_rect.centerx),
                "cy": str(ellipse_rect.centery),
                "rx": str(ellipse_rect.width // 2),
                "ry": str(ellipse_rect.height // 2),
            },
        ),
    )

    ###
    p1, p2 = get_segment_points_cutting_ellipse(ellipse_rect)
    ###

    g.append(
        Element(
            "line",
            {
                **{
                    key: value
                    for key, value in (
                        zip(
                            ("x1", "y1"),
                            map(str, p1),
                        )
                    )
                },
                **{
                    key: value
                    for key, value in (
                        zip(
                            ("x2", "y2"),
                            map(str, p2),
                        )
                    )
                },
            },
        ),
    )

    ###
    return g
