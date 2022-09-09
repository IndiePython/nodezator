"""Facility for the Surface Definition format.

A xml format to define surfaces to be created by
drawing/blitting text on a pygame surface.
"""

### standard library imports

from ast import literal_eval

from string import digits, ascii_lowercase

from xml.dom.minidom import (
    parse as dom_from_filepath,
)


### third-party imports

from pygame.math import Vector2

from pygame.draw import (
    ellipse as draw_ellipse,
    circle as draw_circle,
    line as draw_line,
    lines as draw_lines,
    polygon as draw_polygon,
)


### local imports

from .classes2d.single import Object2D

from .classes2d.collections import List2D

from .surfsman.draw import draw_border

from .surfsman.render import render_rect

from .htsl.creation import TextBlock


def surfdef_obj_from_element(surfdef_element, background_color):
    """Return surface created from surfdef xml element."""

    width, height = (
        int(surfdef_element.getAttribute(attr_name))
        for attr_name in ("width", "height")
    )

    image = render_rect(width, height, background_color)

    anchors = []

    ELEMENT_NODE = surfdef_element.ELEMENT_NODE

    for child in surfdef_element.childNodes:

        if child.nodeType != ELEMENT_NODE:
            continue

        child_name = child.tagName.lower()

        if child_name in ("rect", "ellipse"):

            x, y, width, height = (
                int(child.getAttribute(attr_name))
                for attr_name in (
                    "x",
                    "y",
                    "width",
                    "height",
                )
            )

            fill, stroke, stroke_width, = (
                child.getAttribute(attr_name) or "none"
                for attr_name in ("fill", "stroke", "stroke-width")
            )

            coordinates_name = child.getAttribute("coordinates-name") or "topleft"

            try:
                stroke_width = int(stroke_width)
            except Exception:
                stroke_width = 0

            fill_is_none = fill.lower() == "none"
            stroke_is_none = stroke.lower() == "none"

            if fill_is_none:

                shape_surf = render_rect(width, height, (0, 0, 0, 0))

            else:
                fill = literal_eval(fill)

            if not stroke_is_none:
                stroke = literal_eval(stroke)

            if child_name == "rect":

                if not fill_is_none:

                    shape_surf = render_rect(width, height, fill)

                if not stroke_is_none and stroke_width > 0:

                    draw_border(
                        shape_surf,
                        stroke,
                        thickness=stroke_width,
                    )

            else:

                if not fill_is_none:

                    shape_surf = render_rect(width, height, (0, 0, 0, 0))

                    draw_ellipse(shape_surf, fill, (0, 0, width, height))

                if not stroke_is_none and stroke_width > 0:

                    draw_ellipse(
                        shape_surf,
                        stroke,
                        (0, 0, width, height),
                        stroke_width,
                    )

            obj = Object2D.from_surface(shape_surf)

            setattr(obj.rect, coordinates_name, (x, y))

            image.blit(obj.image, obj.rect)

        elif child_name == "circle":

            cx, cy, radius = (
                int(child.getAttribute(attr_name))
                for attr_name in ("cx", "cy", "radius")
            )

            fill, stroke, stroke_width, = (
                child.getAttribute(attr_name) or "none"
                for attr_name in ("fill", "stroke", "stroke-width")
            )

            try:
                stroke_width = int(stroke_width)
            except Exception:
                stroke_width = 0

            width = height = radius * 2

            shape_surf = render_rect(width, height, (0, 0, 0, 0))

            if fill.lower() != "none":

                fill = literal_eval(fill)

                draw_circle(
                    shape_surf,
                    fill,
                    (radius, radius),
                    radius,
                )

            if not stroke.lower() == "none" and stroke_width > 0:

                stroke = literal_eval(stroke)

                draw_circle(
                    shape_surf,
                    stroke,
                    (radius, radius),
                    radius,
                    stroke_width,
                )

            obj = Object2D.from_surface(shape_surf)
            obj.rect.center = cx, cy

            image.blit(obj.image, obj.rect)

        elif child_name == "line":

            x1, y1, x2, y2 = (
                int(child.getAttribute(attr_name))
                for attr_name in ("x1", "y1", "x2", "y2")
            )

            stroke, stroke_width = (
                literal_eval(child.getAttribute(attr_name) or default)
                for attr_name, default in (
                    ("stroke", "(0, 0, 0)"),
                    ("stroke-width", "1"),
                )
            )

            draw_line(
                image,
                stroke,
                (x1, y1),
                (x2, y2),
                stroke_width,
            )

        elif child_name == "polyline":

            if child.getAttribute("points"):

                points = literal_eval(child.getAttribute("points"))

            else:
                points = points_from_directives(child.getAttribute("d"))

            stroke = literal_eval(child.getAttribute("stroke") or "(0, 0, 0)")

            stroke_width, closed = (
                literal_eval(child.getAttribute(attr_name) or default)
                for attr_name, default in (
                    ("stroke-width", "1"),
                    ("closed", "False"),
                )
            )

            draw_lines(
                image,
                stroke,
                closed,
                points,
                stroke_width,
            )

        elif child_name in ("polygon", "path"):

            if child_name == "polygon":

                points = literal_eval(child.getAttribute("points"))

            else:
                points = points_from_directives(child.getAttribute("d"))

            fill, stroke, stroke_width, = (
                child.getAttribute(attr_name) or "none"
                for attr_name in ("fill", "stroke", "stroke-width")
            )

            try:
                stroke_width = int(stroke_width)
            except Exception:
                stroke_width = 0

            fill_is_none = fill.lower() == "none"
            stroke_is_none = stroke.lower() == "none"

            if not fill_is_none:

                fill = literal_eval(fill)

                draw_polygon(
                    image,
                    fill,
                    points,
                )

            if not stroke_is_none and stroke_width > 0:

                stroke = literal_eval(stroke)

                draw_polygon(
                    image,
                    stroke,
                    points,
                    stroke_width,
                )

        elif child_name == "text":

            x, y = (int(child.getAttribute(attr_name)) for attr_name in ("x", "y"))

            try:
                max_width = int(child.getAttribute("max-width"))

            except Exception:
                max_width = float("inf")

            coordinates_name = (
                child.getAttribute("coordinates-name")
                or "bottomleft"  # just like svg text;
            )

            text_block = TextBlock(child, max_width)

            setattr(text_block.rect, coordinates_name, (x, y))

            text_block_image = text_block[0].image
            text_block_rect = text_block[0].rect

            image.blit(text_block_image, text_block_rect)

            if text_block.anchor_list:
                anchors.extend(anchor_list)

    if anchors:

        body = Object2D.from_surface(image)
        obj = List2D([body, *anchors])
        obj.anchor_list = anchors

    else:
        obj = Object2D.from_surface(image)

    return obj


### support function


def points_from_directives(directives_text):

    directives_text = directives_text.lower()

    chars = list(directives_text)

    temp_points = []

    while chars:

        point_text = ""

        while True:

            c = chars.pop()

            if c.isalpha():

                point = tuple(
                    int(coordinate) for coordinate in (point_text.strip().split())
                )

                temp_points.append(point)

                break

            else:
                point_text = c + point_text

    temp_points.reverse()

    GUIDE_POINT = Vector2(temp_points[0])

    points = [tuple(GUIDE_POINT)]

    for offset in temp_points[1:]:

        GUIDE_POINT += offset
        points.append(tuple(GUIDE_POINT))

    return points


def surfdef_obj_from_path(path, background_color):

    surfdef_element = dom_from_filepath(resource_path).getElementsByTagName("surfdef")[
        0
    ]

    obj = surfdef_obj_from_element(
        surfdef_element,
        background_color,
    )

    return obj
