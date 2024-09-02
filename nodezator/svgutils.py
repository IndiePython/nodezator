"""SVG-related utilities."""

### standard library imports

from collections.abc import Iterable

from xml.dom.minidom import parseString

from re import search, sub


### third-party library imports

from pygame import Rect

from pygame.math import Vector2


### local import
from .ourstdlibs.mathutils import get_rect_from_points



### constants

RECT_FORMATTER = """
<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}">

    <rect
        x="{x}" y="{y}" width="{width}" height="{height}"
        rx="{rx}" ry="{ry}"
        fill="{fill_color}" stroke="{stroke_color}" stroke-width="{stroke_width}"
    />

</svg>
""".strip().format

CIRCLE_FORMATTER = """
<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}">

    <circle
        cx="{cx}" cy="{cy}" r="{r}"
        fill="{fill_color}" stroke="{stroke_color}" stroke-width="{stroke_width}"
     />

</svg>
""".strip().format

ELLIPSE_FORMATTER = """
<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}">

    <ellipse
        cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}"
        fill="{fill_color}" stroke="{stroke_color}" stroke-width="{stroke_width}"
     />

</svg>
""".strip().format

LINE_FORMATTER = """
<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}">

    <line
        x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}"
        stroke="{stroke_color}" stroke-width="{stroke_width}"
     />

</svg>
""".strip().format


### functions

def _format_color(color):
    """Return color in format usable by 'fill' attribute of SVG shapes."""
    if isinstance(color, str):
        return color

    elif isinstance(color, Iterable):

        _r, _g, _b, *_ = color
        return f'rgb({_r}, {_g}, {_b})'

    elif color is None:
        return 'none'

    else:

        raise TypeError(
            "'color' must be None, string or iterable of integers with 3+ values"
        )


def get_rect_svg_text(
    x, y, width, height,
    rx=0, ry=0,
    fill_color=None,
    outline_color=None,
    outline_width=0,
):
    """Return SVG text representing file with a rect."""
    ### format fill color and outline color into a format
    ### used in SVG

    fill_color = _format_color(fill_color)
    stroke_color = _format_color(outline_color)

    ### define the dimensions of the SVG

    width = width + (outline_width * 2)
    height = height + (outline_width * 2)

    ### pass our data to a str.format() instance that formats the data
    ### into a string representing the contents of a svg file describing
    ### our rect, returning such string

    return (
        RECT_FORMATTER(
            width=width,
            height=height,
            x=x, y=y,
            rx=rx, ry=ry,
            fill_color=fill_color,
            stroke_color=stroke_color,
            stroke_width=outline_width,
        )
    )


def get_circle_svg_text(
    cx, cy, r,
    fill_color=None,
    outline_color=None,
    outline_width=0,
):
    """Return SVG text representing file with a circle."""

    ### format fill color and outline color into a format
    ### used in SVG

    fill_color = _format_color(fill_color)

    stroke_color = _format_color(outline_color)

    ### define the dimensions of the SVG, based on the radius and
    ### the outline width

    width = height = (r * 2) + (outline_width * 2)

    ### pass our data to a str.format() instance that formats the data
    ### into a string representing the contents of a svg file describing
    ### our circle, returning such string

    return (
        CIRCLE_FORMATTER(
            width=width,
            height=height,
            cx=cx, cy=cy, r=r,
            fill_color=fill_color,
            stroke_color=stroke_color,
            stroke_width=outline_width,
        )
    )

def get_circle_svg_text_from_radius(
    r,
    fill_color=None,
    outline_color=None,
    outline_width=0,
):
    """Return SVG text representing file with a circle given the radius.

    The remaining values are calculated based on the radius and
    outline width.
    """
    ### format fill color and outline color into a format
    ### used in SVG

    fill_color = _format_color(fill_color)

    stroke_color = _format_color(outline_color)

    ### define the dimensions of the SVG and the center of the circle,
    ### based on the radius and the outline width

    width = height = (r * 2) + (outline_width * 2)
    cx = cy = width // 2

    ### pass our data to a str.format() instance that formats the data
    ### into a string representing the contents of a svg file describing
    ### our circle, returning such string

    return (
        CIRCLE_FORMATTER(
            width=width,
            height=height,
            cx=cx, cy=cy, r=r,
            fill_color=fill_color,
            stroke_color=stroke_color,
            stroke_width=outline_width,
        )
    )

def get_ellipse_svg_text(
    cx, cy, rx, ry,
    fill_color=None,
    outline_color=None,
    outline_width=0,
):
    """Return SVG text representing file with an ellipse."""
    ### format fill color and outline color into a format
    ### used in SVG

    fill_color = _format_color(fill_color)

    stroke_color = _format_color(outline_color)

    ### define the dimensions of the SVG

    width = (rx * 2) + (outline_width * 2)
    height = (ry * 2) + (outline_width * 2)

    ### pass our data to a str.format() instance that formats the data
    ### into a string representing the contents of a svg file describing
    ### our ellipse, returning such string

    return (
        ELLIPSE_FORMATTER(
            width=width,
            height=height,
            cx=cx, cy=cy, rx=rx, ry=ry,
            fill_color=fill_color,
            stroke_color=stroke_color,
            stroke_width=outline_width,
        )
    )

def get_line_svg_text(
    x1, y1, x2, y2,
    outline_color=None,
    outline_width=0,
):
    """Return SVG text representing file with a line."""
    ### represent points as 2d vectors

    v1 = Vector2(x1, y1)
    v2 = Vector2(x2, y2)

    ### define bounding area of points

    points_bounding_area = Rect(get_rect_from_points(v1, v2))

    ### offset it to origin, moving the points along with it by the
    ### same amount
    points_bounding_offset = -Vector2(points_bounding_area.topleft)

    points_bounding_area.move_ip(points_bounding_offset)

    v1 += points_bounding_offset
    v2 += points_bounding_offset

    ### create an additional stroke bounding area, by adding extra
    ### padding to the points bounding area;
    ###
    ### this area accounts for the extra space taken by the line
    ### thickness, that is, the thickness of the stroke
    stroke_bounding_area = points_bounding_area.inflate((outline_width,)*2)

    ### offset stroke bounding area area to origin and move points by the
    ### same amount
    ###
    ### we do not move the points bounding area because at this point we
    ### won't need it anymore

    stroke_bounding_offset = -Vector2(stroke_bounding_area.topleft)

    stroke_bounding_area.move_ip(stroke_bounding_offset)

    v1 += stroke_bounding_offset
    v2 += stroke_bounding_offset

    ### now redefine the points coordinates and the svg dimensions with
    ### the points and stroke bounding area

    x1, y1 = v1
    x2, y2 = v2

    width, height = stroke_bounding_area.size

    stroke_color = _format_color(outline_color)

    ### finally pass our data to a str.format() instance that formats
    ### the data into a string representing the contents of a svg file
    ### describing our line, returning such string

    return (
        LINE_FORMATTER(
            width=width,
            height=height,
            x1=x1, y1=y1, x2=x2, y2=y2,
            stroke_color=stroke_color,
            stroke_width=outline_width,
        )
    )


def get_pie_chart_svg_text(
    value_map,
    color_map,
    inner_outline_color,
    outer_outline_color,
    background_color=None,
    background_method="rect",
    fill_radius=150,
    inner_outline_width=2,
    outer_outline_width=2,
    start_degrees=-90,
    place_items_clockwise=True,
):
    """Return SVG text representing file with a pie chart."""

    total_radius = fill_radius + outer_outline_width
    width = height = total_radius * 2
    cx, cy = width // 2, height // 2

    svg_text = (
        f'<svg width="{width}"'
        f' height="{height}"'
        f' viewBox="0 0 {width} {height}">\n\n'
    )

    if background_color is not None:

        bg_color = _format_color(background_color)
        
        if background_method == 'rect':

            svg_text += (
                f'<rect x="0" y="0" width="{width}" height="{height}"'
                f' fill="{bg_color}" />\n\n'
            )

        else:

            ### for now, we only use 'rect' as the background_method,
            ### that is, we emulate a background color by using a rect
            ### shape placed behind everything (the first element after
            ### the <svg> tag)
            raise ValueError("'background_method' can only be 'rect'.")

    highest_item, *remaining_items = (
        sorted(value_map.items(), key=lambda item: item[1], reverse=True)
    )

    remaining_sum = sum(item[1] for item in remaining_items)

    fill_color = _format_color(color_map[highest_item[0]])

    svg_text += (
        f'<circle cx="{cx}" cy="{cy}"'
        f' r="{fill_radius}" fill="{fill_color}"'
        ' stroke="none" />\n\n'
    )

    inner_stroke_color = _format_color(inner_outline_color)
    outer_stroke_color = _format_color(outer_outline_color)

    if remaining_sum:

        signal_operation = (
            1. if place_items_clockwise else -1.
        ).__mul__

        clockwise_flag = int(place_items_clockwise)

        total_sum = sum(value_map.values())

        offset = Vector2(cx, cy)

        circle_origin = arc_start = (
            Vector2(fill_radius, 0).rotate(start_degrees)
        )

        cumulative_percent = 0.0

        flag = True
        lines_text = ''

        for key, value in remaining_items:

            ### if value is 0 or 0., skip item
            if not value: continue

            ### start
            abs_arc_start = arc_start + offset

            ### cumulative and angle

            cumulative_percent += value / total_sum
            angle = cumulative_percent * 360

            ### end

            arc_end = circle_origin.rotate(signal_operation(angle))
            abs_arc_end = arc_end + offset

            ### create svg

            fill_color = _format_color(color_map[key])

            ## path

            svg_text += (
                f'<path d="M{cx} {cy}'
                f' L {abs_arc_start.x} {abs_arc_start.y}'
                f' A {fill_radius} {fill_radius}'
                f' 0 0 {clockwise_flag} {abs_arc_end.x} {abs_arc_end.y} Z"'
                f' fill="{fill_color}" stroke="none" />\n\n'
            )

            ## if flag, start line

            if flag:

                flag = False

                lines_text += (
                    f'<line x1="{cx}" y1="{cy}"'
                    f' x2="{abs_arc_start.x}" y2="{abs_arc_start.y}"'
                    f' stroke="{inner_stroke_color}"'
                    f' stroke-width="{inner_outline_width}" />\n\n'
                )


            ## end line
            lines_text += (
                f'<line x1="{cx}" y1="{cy}"'
                f' x2="{abs_arc_end.x}" y2="{abs_arc_end.y}"'
                f' stroke="{inner_stroke_color}"'
                f' stroke-width="{inner_outline_width}" />\n\n'
            )


            ### alias end as new start
            arc_start = arc_end

        ### add lines
        svg_text += lines_text

        ### add a small circle at the center where the lines meet

        if inner_outline_width > 1:

            small_radius = inner_outline_width // 2

            svg_text += (
                f'<circle cx="{cx}" cy="{cy}"'
                f' r="{small_radius}" fill="{inner_stroke_color}"'
                f' stroke="none" />\n\n'
            )

    svg_text += (
        f'<circle cx="{cx}" cy="{cy}"'
        f' r="{fill_radius}" fill="none"'
        f' stroke="{outer_stroke_color}"'
        f' stroke-width="{outer_outline_width}" />\n\n'
    )

    svg_text += '</svg>'

    return svg_text



def yield_transformed_svgs(svg_text, id_string, transform_data):

    doc = parseString(svg_text)
    svg = doc.firstChild

    ###

    for element in doc.getElementsByTagName('*'):

        if element.hasAttribute('id'):
            element.setIdAttribute('id')

    ###
    element = doc.getElementById(id_string)

    for transform_name, *deltas in transform_data:

        _change_transform(element, transform_name, *deltas)
        yield svg.toxml()


def _change_transform(element, transform_name, value_string):

    if not value_string:
        raise ValueError('must provide a value_string')

    ###

    if element.hasAttribute('transform'):

        transform = element.getAttribute('transform')

        ##

        if transform_name in transform:

            new_transform = sub(
                f'({transform_name}\(.*\))',
                f'{transform_name}({value_string})',
                transform,
            )

        ##

        else:

            transform_text = f'{transform_name}({value_string})'

            if transform:
                new_transform = f'{transform} {transform_text}'

            else:
                new_transform = transform_text

    ###
    else:
        new_transform = f'{transform_name}({value_string})'

    ###
    element.setAttribute('transform', new_transform)

