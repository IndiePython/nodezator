"""Tools to generate surfaces through drawing/blitting."""

### standard library import
from io import BytesIO


### third-party imports

from pygame import Surface, Rect

from pygame.draw import (
    line as draw_line,
    ellipse as draw_ellipse,
)

from pygame.transform import rotate as rotate_surface

from pygame.image import load as load_image


### local imports

from ..rectsman.main import RectsManager

from ..svgutils import get_ellipse_svg_text, get_line_svg_text

from ..colorsman.colors import (
    BLACK,
    WINDOW_BG,
    SHADOW_COLOR,
    HIGHLIGHT_COLOR,
    IMAGE_NOT_FOUND_FG,
    IMAGE_NOT_FOUND_BG,
)

from .mathutils import get_segment_points_cutting_ellipse

from .draw import draw_border, draw_depth_finish, blit_aligned



def render_rect(width, height, color=BLACK):
    """Return surface representing rect with a single color.

    Parameters
    ==========

    width (integer)
        indicates desired width of the generated surface
        or obj.
    height (integer)
        indicates desired height of the generated surface
        or obj.
    color (sequence with 3 or 4 integers)
        represents a color to fill the surface;
        the integers are in the range(256) and represent
        values of red, green and blue channels of a color
        (a fourth integer may also appear, indicating the
        value of the alpha channel, indicating the
        opacity/transparency).
    """
    ### instantiate surface taking transparency into account

    try:
        has_transparency = color[3] < 255

    except IndexError:
        has_transparency = False

    finally:

        if has_transparency:
            surf = Surface((width, height)).convert_alpha()

        else:
            surf = Surface((width, height)).convert()

    surf.fill(color)

    ### finally return the surf
    return surf


def combine_surfaces(
    surfaces,
    retrieve_pos_from="midright",
    assign_pos_to="midleft",
    offset_pos_by=(0, 0),
    padding=0,
    background_color=(*BLACK, 0),
):
    """Return new surf from given ones."""
    ### obtain rects from given surfaces
    rects = [surf.get_rect() for surf in surfaces]

    ### define rects manager
    rectsman = RectsManager(rects.__iter__)

    ### position rects

    rectsman.snap_rects_ip(
        retrieve_pos_from=retrieve_pos_from,
        assign_pos_to=assign_pos_to,
        offset_pos_by=offset_pos_by,
    )

    ### get an inflated copy of the rectsman

    inflation_amount = padding * 2

    inflated_rect = rectsman.inflate(inflation_amount, inflation_amount)

    ### position inflated copy in origin and center
    ### the rectsman on it

    inflated_rect.topleft = (0, 0)
    rectsman.center = inflated_rect.center

    ### create new surface and blit surfaces on it

    new_surf = render_rect(*inflated_rect.size, color=background_color)

    for surf, rect in zip(surfaces, rects):
        new_surf.blit(surf, rect)

    ### finally return the surf
    return new_surf


def unite_surfaces(
    surface_rect_pairs,
    padding=0,
    background_color=(*BLACK, 0),
):
    """Return a surface from surfaces' union."""
    ### separate surfaces and rects into different lists

    surfaces = []
    rects = []

    for surf, rect in surface_rect_pairs:

        surfaces.append(surf)
        rects.append(rect)

    ### obtain a rectsman for the rects
    rectsman = RectsManager(rects.__iter__)

    ### get an inflated copy of the rectsman

    inflation_amount = padding * 2

    inflated_rect = rectsman.inflate(inflation_amount, inflation_amount)

    ### obtain an offset from the inverted topleft of the
    ### inflated rect; we'll use this to obtain offset
    ### copies of each rect in order to blit the surfaces
    ### relative to the union surface
    offset = tuple(-value for value in inflated_rect.topleft)

    ### create new surface and blit surfaces on it

    new_surf = render_rect(*inflated_rect.size, color=background_color)

    for surf, rect in zip(surfaces, rects):

        new_surf.blit(
            surf,
            rect.move(offset),
        )

    ### finally return the surf
    return new_surf


def render_separator(
    length,
    is_horizontal=True,
    padding=5,
    thickness=5,
    background_color=WINDOW_BG,
    foreground_color=SHADOW_COLOR,
    highlight_color=HIGHLIGHT_COLOR,
):
    """Return a tkinter.Separator-like surface.

    Parameters
    ==========

    length (integer)
        integer representing the length of the separator
        in pixels, used for either the width or height,
        depending on the desired orientation.
    is_horizontal (boolean, default is True)
        Hints the separator line orientation. If False, the
        separator surface will be rotated at the end to
        assume a vertical orientation.
    padding (integer, default is 5)
        padding to be added at the edges of the surface, so
        that the separator line don't touch them (if desired).
        It is an integer representing the amount of pixels.
    thickness (integer, default is 5)
        how thick the separator surface is.
    background_color
    foreground_color
    highlight_color
    (tuple or list of r, g, b integer values ranging from 0
    to 255)
        represents colors for background, foreground (the
        line) and highlight color (another line just below
        the foreground).
    """
    ### create the surface
    surf = render_rect(length, thickness, background_color)

    ### define variables for common usage

    start_y = end_y = (thickness // 2) - 1

    start_x = 0 + padding
    end_x = length - padding

    ### draw separator

    start = start_x, start_y
    end = end_x, end_y

    draw_line(surf, foreground_color, start, end, 1)

    ### draw depth highlight

    highlight_start = start_x, start_y + 1
    highlight_end = end_x, end_y + 1

    draw_line(surf, highlight_color, highlight_start, highlight_end, 1)

    ### if requested, put surface in vertical position

    if not is_horizontal:

        # we rotate minus 90 degrees so highlight end up
        # to the left of the separator line which
        # simulates the direction from which a fictious
        # source of light hits the surface;
        surf = rotate_surface(surf, -90)

    ### finally, return the surface
    return surf

def render_surface_from_svg_text(svg_text):
    """Return surface representing SVG given as text.

    The SVG renderer used by pygame doesn't support all SVG features,
    so a bit of experimentation is needed sometimes.
    """
    with BytesIO(
        bytes(svg_text, encoding='utf-8')
    ) as bytestream:

        return load_image(bytestream)


def render_not_found_icon(size):
    """Return surface with icon representing an image not found.

    Icon is formed by an ellipse with a diagonal slash.

    Parameters
    ==========
    size (2-tuple of integers)
        Integers represent width and height of surface, respecively.
    """
    ### render an ellipse outline surface

    ## define ellipse data

    # outline thickness

    smaller_dimension = min(size)

    outline_thickness = (
        smaller_dimension // 10 if smaller_dimension > 10 else 1
    )

    # cx, cy, rx, ry

    cx, cy = (dimension/2 for dimension in size)

    rx = cx - (outline_thickness/2)
    ry = cy - (outline_thickness/2)

    ## render

    ellipse_outline_surf = (

        render_surface_from_svg_text(

            get_ellipse_svg_text(
                cx,
                cy,
                rx,
                ry,
                outline_color=IMAGE_NOT_FOUND_FG,
                outline_width=outline_thickness,
            )

        )

    )

    ### render a diagonal line surface

    ## find points of segment cutting ellipse

    rect = Rect(0, 0, *size)

    if outline_thickness > 1:

        deflation = -(outline_thickness - 1)
        rect.inflate_ip(deflation, deflation)

    (x1, y1), (x2, y2) = get_segment_points_cutting_ellipse(rect)

    ## render

    diagonal_line_surf = (

        render_surface_from_svg_text(

            get_line_svg_text(
                x1,
                y1,
                x2,
                y2,
                outline_color=IMAGE_NOT_FOUND_FG,
                outline_width=outline_thickness,
            )

        )

    )

    ### create base surface and blit other surfaces over it

    ellipse_surf = render_rect(*size, IMAGE_NOT_FOUND_BG)

    ellipse_surf.blit(ellipse_outline_surf, (0, 0))

    blit_aligned(
        surface_to_blit=diagonal_line_surf,
        target_surface=ellipse_surf,
        retrieve_pos_from='center',
        assign_pos_to='center',
    )

    ### finallly return the surface we created
    return ellipse_surf
