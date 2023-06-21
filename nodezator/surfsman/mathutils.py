
### standard library import
from math import sqrt


### third-party import
from pygame.math import Vector2



def get_segment_points_cutting_ellipse(rect):
    """Return points defining a segment that cuts an ellipse.

    Ideally, the segment would represent the points in a diagonal
    of the rectangle (bounding box of ellipse) that touches the
    ellipse outline. This should be the goal for a future update
    of this function.

    For now, I use an approximation by defining an arbitrary proportion
    of the semi-major axis of the ellipse (half the length of the
    largest axis) for the x or y coordinates of one of the points of
    the desired segment.

    This works fine, but must be updated to the ideal behaviour described
    earlier when I have the time to deepen my math knowledge in order
    to reproduce such behaviour.
    """
    ### apply different formulas depending on which is longer, the width
    ### or the length

    ## if width is longer or equal to height, the equation is...
    ## 
    ##  x²     y²
    ## ---- + ---- = 1
    ##  a²     b²
    ##
    ## where:
    ##
    ## a == half the major axis (half the width)
    ## b == half the minor axis (half the height)
    ## x == an arbitrary value as a proportion of a
    ## y == ? (the value we want to find)

    if rect.width >= rect.height:

        a = rect.w / 2
        b = rect.h / 2

        a_squared = a**2
        b_squared = b**2

        x = a * .71
        x_squared = x**2

        y_squared = (1 - (x_squared / a_squared)) * b_squared
        y = sqrt(y_squared)

    ## otherwise, if width is shorter than the height, the equation is...
    ## 
    ##  x²     y²
    ## ---- + ---- = 1
    ##  b²     a²
    ##
    ## where:
    ##
    ## a == half the major axis (half the height)
    ## b == half the minor axis (half the width)
    ## y == an arbitrary value as a proportion of a
    ## x == ? (the value we want to find)

    else:

        a = rect.h / 2
        b = rect.w / 2

        a_squared = a**2
        b_squared = b**2

        y = a * .65
        y_squared = y**2

        x_squared = (1 - (y_squared / a_squared)) * b_squared
        x = sqrt(x_squared)

    ### invert signal of y
    y = -y

    ### define first point, offset by the rect's center
    p1 = Vector2(x, y) + rect.center

    ### define the second point as the inverted x and y
    ### coordinates, also offset by the rect's center
    p2 = Vector2(-x, -y) + rect.center

    ### return the points
    return p1, p2
