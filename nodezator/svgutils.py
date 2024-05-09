"""SVG-related utilities."""

### standard library import
from collections.abc import Iterable


### third-party library import
from pygame.math import Vector2



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

    fill_color = _format_color(fill_color)
    stroke_color = _format_color(outline_color)

    width = width + (outline_width * 2)
    height = height + (outline_width * 2)

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

    fill_color = _format_color(fill_color)

    stroke_color = _format_color(outline_color)

    width = height = (r * 2) + (outline_width * 2)

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

    fill_color = _format_color(fill_color)

    stroke_color = _format_color(outline_color)

    width = height = (r * 2) + (outline_width * 2)
    cx = cy = width // 2

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
