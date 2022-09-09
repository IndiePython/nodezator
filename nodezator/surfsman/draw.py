"""Drawing functions utilities."""

### standard library imports

from colorsys import rgb_to_hls, hls_to_rgb
from itertools import cycle
from math import sqrt


### third-party imports

from pygame import Surface, Rect

from pygame.math import Vector2

from pygame.transform import rotate as rotate_surface

from pygame.draw import (
    line as draw_line,
    lines as draw_lines,
    rect as draw_rect,
    ellipse as draw_ellipse,
    polygon as draw_polygon,
)


### local imports

from ..colorsman.colors import BLACK, WHITE, SHADOW_COLOR, HIGHLIGHT_COLOR


HIGHLIGHT_POINT_NAMES = ("bottomleft", "topleft", "topright")

SHADOW_POINT_NAMES = ("bottomleft", "bottomright", "topright")


def draw_depth_finish(
    surf,
    thickness=1,
    outset=True,
    highlight_color=HIGHLIGHT_COLOR,
    shadow_color=SHADOW_COLOR,
):
    """Give a finish which conveys depth.

    Such finish application consists of drawing polygons
    which work as borders of the surface to simulate
    highlights and shadows, giving depth to the surface.

    Parameters
    ==========

    surf (pygame.Surface instance)
        surface wherein to draw the lines.
    thickness (integer >= 1)
        how thick the finish must be.
    outset (boolean)
        indicates whether the depth must represent an outset
        area (when True) or an inset area (when False).
    highlight_color, shadow_color
        (pygame.Color instances or tuples of integers
        representing RGB values of colors)
        colors used for highlights and shadows, respectively.
    """
    ### if the depth is supposed to look like an inset
    ### (not an outset), swap the highlight and shadow
    ### colors

    if not outset:

        highlight_color, shadow_color = shadow_color, highlight_color

    ### retrieve a rect for the surface
    rect = surf.get_rect()

    ### due to how blitting works, the rect
    ### must be slightly repositioned and resided
    ### before we start blitting

    rect.move_ip(-1, -1)
    rect.width += 1
    rect.height += 1

    ### draw lines

    for _ in range(thickness):

        ## deflate rect
        rect.inflate_ip(-2, -2)

        ## obtain points for each color and
        ## draw the lines

        for color, point_names in (
            (shadow_color, SHADOW_POINT_NAMES),
            (highlight_color, HIGHLIGHT_POINT_NAMES),
        ):

            ## obtain points
            points = [getattr(rect, point_name) for point_name in point_names]

            ## blit lines
            draw_lines(surf, color, False, points)


def draw_border(surf, color=BLACK, thickness=1):
    """Draw a border around surf of given color and width.

    It works by drawing a sequence of rects with thickness
    1, one inside the other.

    Parameters
    ==========
    surf (pygame.Surface instance)
        surface wherein to draw the border
    color (pygame.Color instance or sequence)
        contains integers from 0 to 255 inclusive,
        representing values for red, green and blue channels
        of a color.
    thickness (integer)
        represents the desired width of the border in pixels.

    New proposed solution
    =====================

    The new proposed solution below needs to be tested and
    profiled before replacing the old one. If it is to
    replace the old one, it also needs to be properly
    commented.

    This new solution is used in the draw_border_on_area()
    function. If proven inferior, change to use the
    current solution in this function.

    ###

    rect = surf.get_rect()

    for i in range(0, thickness*2, 2):

        draw_rect(
          surf,
          color,
          rect.inflate(-i, -i),
          1
        )

    ###
    """
    ### retrieve rect for surf
    rect = surf.get_rect()

    ### for each unit in the border width, draw the rect,
    ### then perform additional setups

    for _ in range(thickness):

        ## draw rect
        draw_rect(surf, color, rect, 1)

        ## decrement dimensions by 2 units

        rect.size = tuple(dimension - 2 for dimension in rect.size)

        ## move rect one unit down and to the right
        rect.move_ip(1, 1)


### TODO refactor below


def draw_border_on_area(surf, color, area_rect, thickness=1):
    """Draw a border on surf on given area.

    It works by drawing a sequence of rects with thickness
    1, one inside the other.

    Parameters
    ==========
    surf (pygame.Surface instance)
        surface wherein to draw the border
    color (pygame.Color instance or sequence)
        contains integers from 0 to 255 inclusive,
        representing values for red, green and blue channels
        of a color.
    area_rect (pygame.Rect or compatible)
        rect describing area inside given surf wherein to
        draw the border.
    thickness (integer)
        represents the desired width of the border in pixels.
    """
    ### starting from 0 (zero), get an amount of deflation
    ### from 0 to the double of the thickness, in increments
    ### of 2

    for deflation in range(0, thickness * 2, 2):

        ## for each amount of deflation, draw a deflated
        ## rect in that area on the given surface with
        ## thickness 1

        draw_rect(surf, color, area_rect.inflate(-deflation, -deflation), 1)


def draw_checker_pattern(
    surf, color_a=WHITE, color_b=BLACK, rect_width=10, rect_height=10
):
    """Draw checker pattern on given surf.

    Parameters
    ==========
    surf (pygame.Surface instance)
        surface wherein to draw the checker pattern.
    color_a, color_b (sequence with 3 integers)
        colors to be used in the checker pattern;
        integers are such that 0 <= integer <= 255 and
        together they represent the values of the red,
        green and blue channels of a color;
    rect_width, rect_height (positive integers)
        represent the dimensions of the rect used to
        draw each rect of the checker pattern.
    """
    ### retrieve a rect from the surf
    surf_rect = surf.get_rect()

    ### create a color cycler from the received colors
    next_color = cycle((color_a, color_b)).__next__

    ### create a rect with the provided dimensions, called
    ### unit rect, since it represents an unit or tile in
    ### the checker pattern
    unit_rect = Rect(0, 0, rect_width, rect_height)

    ### use the unit rect width and height as offset
    ### amounts in the x and y axes

    x_offset = rect_width
    y_offset = rect_height

    ### "walk" the surface while blitting the checker
    ### pattern until the surface the entire area of
    ### the surface is covered by the checker pattern

    while True:

        ## if the unit rect isn't touching the
        ## surface area, invert the x_offset,
        ## move it back using such new x_offset and
        ## move it down using the y_offset

        if not surf_rect.colliderect(unit_rect):

            x_offset = -x_offset
            unit_rect.move_ip(x_offset, y_offset)

        ## if even after the previous "if block" the
        ## unit rect still doesn't touch the surface
        ## area, break out of the while loop
        if not surf_rect.colliderect(unit_rect):
            break

        ## otherwise draw the unit rect...
        draw_rect(surf, next_color(), unit_rect)

        ## and move it in the x axis using the x_offset
        unit_rect.move_ip(x_offset, 0)


def draw_linear_gradient(
    surf,
    color,
    start_percentage=0.125,
    stop_percentage=1,
    max_lightness_percentage=1.0,
    min_lightness_percentage=0.2,
    direction="left_to_right",
):
    """Draw linear gradient on given surface.

    Since operations are done in-place in the given surface,
    nothing meaningful is returned.

    Parameters
    ==========
    surf (pygame.Surface instance)
        surface wherein to draw the gradient.
    color (sequence of RGB values)
        the rgb values are integers such that
        0 <= integer <= 255, representing values for
        red, green and blue channels respectively;
        a fourth integer may be present, representing
        the alpha, but it is ignored anyway; these
        values represent the base color for the gradient.
    start_percentage, stop_percentage (0.0 <= float <= 1.0)
        represent the interval of the surface's width
        in percentage wherein the color goes from
        maximum lightness to minimum lightness.
    max_lightness_percentage,
    min_lightness_percentage (0.0 <= float <= 1.0)
        represent the maximum and minimum percentage of
        the original lightness used in the gradient; that
        is, the color will go from the max lightness to
        the minimum lightness in the gradient.
    direction (string)
        indicates the direction of the gradient; must be
        one of the following: 'left_to_right',
        'right_to_left', 'top_to_bottom' or 'bottom_to_top'.
    """
    ### if the gradient is vertical (from bottom to top or
    ### vice-versa), backup the original surf and obtain
    ### a new surf rotated 90 degrees

    if direction in ("bottom_to_top", "top_to_bottom"):

        backup_surf = surf
        surf = rotate_surface(surf, 90)

    ### store needed data for future calculations

    width, height = surf.get_size()

    start = round(width * start_percentage)
    stop = round(width * stop_percentage)
    total = stop - start

    lightness_factor = 1.0 - min_lightness_percentage

    ### define the hue, lightness and saturation of the
    ### base color

    hue, lightness, saturation = rgb_to_hls(*[v / 255 for v in color[:3]])

    ### iterate over all vertical sections of the
    ### surface represented by all possible values of
    ### x within the width of the surface

    for x in range(width):

        ## if x is before or at the start, the max
        ## lightness percentage is used as the percentage
        if x <= start:
            percent = max_lightness_percentage

        ## if x is at or after the stop, the min
        ## lightness percentage is used as the percentage
        elif x >= stop:
            percent = min_lightness_percentage

        ## if it is between the start and stop, though,
        ## we use the max lightness percentage minus
        ## the progress towards the stop

        elif start < x < stop:

            progress = (x - start) / total

            percent = max_lightness_percentage - (progress * lightness_factor)

        ## we then calculate the lightness
        current_lightness = lightness * percent

        ## obtain the resulting color

        color = [
            round(value * 255)
            for value in hls_to_rgb(hue, current_lightness, saturation)
        ]

        ## and use it to draw a line on the vertical section
        draw_line(surf, color, (x, 0), (x, height), 1)

    ### direction setups

    ## if the direction is right to left, just obtain a new
    ## surface corresponding to the current one rotated
    ## 180 degrees then blit such surface over the current
    ## one (resulting in the current surface being overriden
    ## by the rotated one)

    if direction == "right_to_left":

        new_surf = rotate_surface(surf, 180)
        surf.blit(new_surf, (0, 0))

    ## if the direction is vertical, specific setups are
    ## needed

    elif direction in ("bottom_to_top", "top_to_bottom"):

        # define the amount of rotation needed according
        # to the specific vertical direction
        rotation_amount = 90 if direction == "bottom_to_top" else -90

        # rotate the current surface by negative 90 degrees
        # and blit it over the backup surf (which is a
        # reference to the original surf before being
        # rotated)

        new_surf = rotate_surface(surf, rotation_amount)
        backup_surf.blit(new_surf, (0, 0))

    ### for debugging: uncomment drawing command below to
    ### see line from where the gradient begin to shift
    ### (when the direction is 'left_to_right')
    ###
    ### draw_line(
    ###   surf, (255,)*3, (start, 0), (start, height), 1
    ### )


def draw_not_found_icon(surf, color):
    """Draw icon representing an image not found.

    Draws a circle with a diagonal slash on given surf.

    Parameters
    ==========
    surf (pygame.Surface instance)
        surface wherein to draw the icon.
    color (sequence of integers)
        color to be used for drawing the icon; the integers
        represent the values of the red, green and blue
        channels and must be in the range(0, 256) interval.
    """
    rect = surf.get_rect()

    ### draw circle (uses pygame.draw.ellipse())

    ## define ellipse thickness

    smaller_dimension = min(rect.size)

    ellipse_thickness = smaller_dimension // 10 if smaller_dimension > 10 else 1

    ## draw
    draw_ellipse(surf, color, rect, ellipse_thickness)

    ### draw diagonal

    ## find diagonal points

    v1 = Vector2(rect.bottomleft)
    v2 = Vector2(rect.topright)

    d1 = v1.lerp(v2, 0.175)
    d2 = v2.lerp(v1, 0.175)

    ## draw diagonal based on ellipse thickness

    if ellipse_thickness >= 3:

        dimension_size = round(ellipse_thickness / sqrt(2))

        small_rect = Rect(0, 0, dimension_size, dimension_size)

        coordinate_names = ("topleft", "bottomright")

        small_rect.center = d1

        p1, p2 = (
            getattr(small_rect, coordinate_name) for coordinate_name in coordinate_names
        )

        small_rect.center = d2

        p3, p4 = (
            getattr(small_rect, coordinate_name) for coordinate_name in coordinate_names
        )

        draw_polygon(surf, color, (p1, p3, p4, p2))

    else:
        draw_line(surf, color, d1, d2, ellipse_thickness)


def blit_aligned(
    surface_to_blit,
    target_surface,
    retrieve_pos_from="topleft",
    assign_pos_to="topleft",
    offset_pos_by=(0, 0),
):
    """Align and blit a surface into another.

    Works by aligning the position of the rects of two
    surfaces with an offset. The first surface is
    then blitted into the other one.

    Parameters
    ==========
    surface_to_blit (pygame.Surface instance)
        surface to be blitted into the other one.
    target_surface (pygame.Surface instance)
        surface wherein the first one will be blitted.
    retrieve_pos_from (string)
        name of pygame.Rect attribute from which to
        retrieve position information from the rect
        of the target surf.
    assign_pos_to (string)
        name of pygame.Rect attribute to which assign
        the position information in the rect of the
        surface to blit.
    offset_pos_by (tuple/list containing 02 integers)
        represent an offset applied to the rect of the
        surface to be blitted after the positions are
        aligned.
    """
    ### get pygame.Rect instances for both surfaces

    rect_for_blitting = surface_to_blit.get_rect()
    target_rect = target_surface.get_rect()

    ### align the positions between the two rects

    ## get the position from the target rect attribute
    target_pos = getattr(target_rect, retrieve_pos_from)

    ## assign the position to the rect of the surface
    ## to be blitted
    setattr(rect_for_blitting, assign_pos_to, target_pos)

    ### apply the offset to the rect of the surface to
    ### be blitted
    rect_for_blitting.move_ip(offset_pos_by)

    ### finally blit
    target_surface.blit(surface_to_blit, rect_for_blitting)
