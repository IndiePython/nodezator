"""Utility functions for line segment management.

The clipping utilities in this module were based on the
so called Cohen Sutherland algorithm:

https://en.wikipedia.org/
wiki/Cohen%E2%80%93Sutherland_algorithm

The code was based on code from this page:

https://www.geeksforgeeks.org/
line-clipping-set-1-cohen-sutherland-algorithm/

The page attributes the contribution to Saket Modi and
further references the wikipedia article we just mentioned
above.

The code was further refactored and commented by me
(Kennedy Richard - https://kennedyrichard.com)
"""

### local imports

from ...config import APP_REFS

from ...pygameconstants import SCREEN_RECT


### clipping utilities

## the Cohen-Sutherland algorithm used to clip line segments
## defines 9 conceptual regions/areas which it uses to define
## whether clipping is needed based on the position
## of points in those regions (the central region is the
## collision area); here we define codes that represent
## the different sides of the clipping area; combined, they
## represent the 9 different regions
##
##          |           |
##   (1001) |   (1000)  | (1010)
##          |           |
##  -----------------------------
##          |           |
##          | collision |
##   (0001) |   area    | (0010)
##          |  (0000)   |
##  -----------------------------
##          |           |
##   (0101) |  (0100)   | (0110)
##          |           |
##
## e.g.:
##
##              bottom
##               |
##            top|
##              ||
##     region:  1001
##                ||
##            right|
##                 left
##

INSIDE = 0  # 0000
LEFT = 1  # 0001
RIGHT = 2  # 0010
BOTTOM = 4  # 0100
TOP = 8  # 1000


def define_clipping_area_boundaries_on_module_level():

    ## when drawing line segments, we want to draw as
    ## little as possible, thus we only draw the portion
    ## of the segments which are inside the screen,
    ## that is, we clip the segments to the visible area;
    ##
    ## however, since the segments have some thickness,
    ## we compensate by using a rect just a bit larger
    ## than the screen for the clipping, specially since
    ## the size of the clipping area doesn't slow down
    ## the calculations
    clipping_area = SCREEN_RECT.inflate(4, 4)

    ## define x_max, y_max, x_min and y_min values on
    ## module level
    ##
    ## they represent the boundaries of the clipping area
    ## and are defined on module level so that other
    ## functions can reference the values directly as
    ## needed

    globals_dict = globals()

    globals_dict["x_max"] = clipping_area.right
    globals_dict["y_max"] = clipping_area.bottom
    globals_dict["x_min"] = clipping_area.left
    globals_dict["y_min"] = clipping_area.top


## store function above as a window resize setup and
## execute it

APP_REFS.window_resize_setups.append(define_clipping_area_boundaries_on_module_level)

define_clipping_area_boundaries_on_module_level()


def get_region_code(x, y):
    """Return region code for a point(x,y).

    Works by performing bitwise OR operations (the ones
    using the '|=' operator) on the code of the inside
    region based on the relationship between the
    coordinates' values and the values of the clipping
    area boundaries.
    """
    code = INSIDE

    if x < x_min:
        code |= LEFT  # to left of clipping area
    elif x > x_max:
        code |= RIGHT  # to right of clipping area

    if y < y_min:
        code |= BOTTOM  # below clipping area
    elif y > y_max:
        code |= TOP  # above clipping area

    return code


def clip_segment(start_point, end_point):
    """Return points for clipped segment.

    Parameters
    ==========
    start_point (iterable with two real numbers)
        represents the starting point of the line segment.
    end_point (iterable with two real numbers)
        represents the ending point of the line segment.

    Uses the Cohen-Sutherland algorithm to obtain the
    points for the clipped segment. If the segment doesn't
    touch the clipping area, a ValueError is raised.
    """
    ### reference individual coordinates of each point

    x1, y1 = start_point
    x2, y2 = end_point

    ### compute region codes for start_point, end_point

    code1 = get_region_code(x1, y1)
    code2 = get_region_code(x2, y2)

    ### calculate the new coordinates for the start and
    ### end points of the clipped segment

    while True:

        ### act based on one of the 03 possible scenarios:

        ## (1) if both points lie within the clipping area,
        ## that is, the bitwise OR of regions of two end
        ## points of the segment is 0, it means both points
        ## are inside the rectangle, so we can return them
        ## immediately

        if code1 == 0 and code2 == 0:

            start_point = x1, y1
            end_point = x2, y2

            return start_point, end_point

        ## (2) both points share at least one outside
        ## region, which implies that the segment does not
        ## cross the clipping area, so we raise a ValueError;
        ## (bitwise AND of endpoints != 0)

        elif (code1 & code2) != 0:
            raise ValueError("No collision detected")

        ## (3) otherwise, we must perform a clipping
        ## operation, that is, we must recalculate the
        ## coordinates of the point(s) of the segment
        ## so the final coordinates form the part of the
        ## segment which is inside the clipping area

        else:

            ## since the code for the points didn't pass
            ## the test for any of the previous scenarios
            ## (1 and 2), we know that at least one of the
            ## points is outside the rectangle, that is,
            ## its region code is different from 0, so if
            ## the code for the start point (code1) isn't
            ## 0 we pick it, otherwise we assume the code
            ## for the end point (code2) is the one
            ## different from 0;
            code_out = code1 if code1 != 0 else code2

            ## now find the intersection point using the
            ## following formulas, depending on the region
            ## of the point
            ##
            ##  slope = (y2 - y1) / (x2 - x1)
            ##
            ##  x = x1 + (1 / slope) * (ym - y1)
            ##  (where ym is y_min or y_max)
            ##
            ##  y = y1 + slope * (xm - x1)
            ##  (where xm is x_min or x_max)
            ##
            ## also, there's no need to worry about
            ## ZeroDivisionError because, in each case, the
            ## outcode bit being tested guarantees the
            ## denominator is non-zero

            # point is above the clipping area

            if code_out & TOP:

                x = x1 + (x2 - x1) * (y_max - y1) / (y2 - y1)
                y = y_max

            # point is below the clipping area

            elif code_out & BOTTOM:

                x = x1 + (x2 - x1) * (y_min - y1) / (y2 - y1)
                y = y_min

            # point is to the right of the clipping area

            elif code_out & RIGHT:

                x = x_max
                y = y1 + (y2 - y1) * (x_max - x1) / (x2 - x1)

            # point is to the left of the clipping area

            elif code_out & LEFT:

                x = x_min
                y = y1 + (y2 - y1) * (x_min - x1) / (x2 - x1)

            ## depending on which point you picked, update
            ## the coordinates of the corresponding point
            ## with the new coordinates calculated, and
            ## recalculate the region code of this new
            ## point

            if code_out == code1:

                x1, y1 = x, y
                code1 = get_region_code(x1, y1)

            else:

                x2, y2 = x, y
                code2 = get_region_code(x2, y2)


### segment crossing utility


def do_segments_cross(segment_ab, segment_cd):
    """Return whether two segments cross each other."""
    ### name points

    a, b = segment_ab
    c, d = segment_cd

    ### return whether segments cross each other based on
    ### the orientation of each different triplet between
    ### the four points

    return ccw(a, b, c) != ccw(a, b, d) and ccw(c, d, a) != ccw(c, d, b)


def ccw(a, b, c):
    """Return whether points are oriented counterclockwise."""
    return (c[1] - a[1]) * (b[0] - a[0]) > (b[1] - a[1]) * (c[0] - a[0])
