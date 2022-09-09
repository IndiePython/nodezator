"""Facility for grid related operations."""

### third-party imports

from pygame import Rect
from pygame.math import Vector2


### local import
from ...ourstdlibs.mathutils import get_reaching_multiple


def enforce_multiple(unit_rect, area_rect):
    """Guarantee area rect's size is multiple of unit rect's.

    The area rect dimensions being multiple of the unit
    rect dimensions is a requirement to produce a grid
    whose lines are equidistant and scroll smoothly.

    By doing so we keep the illusion of indefinite
    scrolling whenever moving lines forming a grid.
    Otherwise, if we were to allow the area rect
    dimensions to not be multiple of the unit rect
    the last line in the non-multiple orientation(s)
    would always have a different distance from the
    others, thus preventing the proper representation
    of a grid.

    unit_rect
        pygame.Rect instance representing an unit in the
        grid.
    area_rect
        pygame.Rect instance representing the area covered
        by the grid.
    """
    ### reference unit rect and area rect dimensions

    unit_width, unit_height = unit_rect.size
    area_width, area_height = area_rect.size

    ### if any of the area rect dimensions aren't
    ### a multiple of the respective unit rect dimension,
    ### create a new area rect positioned at the same
    ### topleft position of the original one, but with
    ### dimensions extended just enough to reach the
    ### nearest multiple

    if area_width % unit_width or area_height % unit_height:

        new_width = get_reaching_multiple(unit_width, area_width)
        new_height = get_reaching_multiple(unit_height, area_height)

        area_rect = Rect(*area_rect.topleft, new_width, new_height)

    return unit_rect, area_rect


def generate_grid_lines(
    unit_rect,
    area_rect,
    use_vectors=False,
    separate_orientation=False,
):
    """Generate and return a list of grid-like lines.

    The list items are tuples containing two points each,
    representing the start and end points of a line.

    E.g.: [((0, 0), (10, 10)), ((3, 3), (5, 5))...]

    unit_rect
        pygame.Rect instance representing an unit in the
        grid.
    area_rect
        pygame.Rect instance representing the area covered
        by the grid.
    use_vectors
        Boolean indicating whether to convert points from
        tuples instances (default behaviour) to
        pygame.math.Vector2 instances.
    separate_orientation
        Boolean indicating whether to return both horizontal
        and vertical lines as a single list (default
        behaviour) or return them in two different lists.
    """
    unit_width, unit_height = unit_rect.size

    if (area_rect.width < unit_width) or (area_rect.height < unit_height):
        raise ValueError("area_rect mustn't be smaller than unit_rect.")

    ### get rect edges

    top, bottom = area_rect.top, area_rect.bottom
    left, right = area_rect.left, area_rect.right

    ### get value for cross sections in x and y axes

    x_sections = list(range(left, right, unit_width))
    y_sections = list(range(top, bottom, unit_height))

    ### store start and end point pairs for each orientation

    vert_start_points = [(x, top) for x in x_sections]
    vert_end_points = [(x, bottom) for x in x_sections]

    horiz_start_points = [(left, y) for y in y_sections]
    horiz_end_points = [(right, y) for y in y_sections]

    ### if requested, convert points into vectors

    if use_vectors:
        vert_start_points = list(map(Vector2, vert_start_points))
        vert_end_points = list(map(Vector2, vert_end_points))
        horiz_start_points = list(map(Vector2, horiz_start_points))
        horiz_end_points = list(map(Vector2, horiz_end_points))

    ### pair start and end points in each orientation;
    ### the paired points represent straight lines,
    ### so that's how they're called;

    vert_lines = list(zip(vert_start_points, vert_end_points))

    horiz_lines = list(zip(horiz_start_points, horiz_end_points))

    ### if requested, return both horizontal and vertical
    ### lines as they are, separated by orientation
    if separate_orientation:
        return horiz_lines, vert_lines

    ### otherwise, return a concatenated single list
    else:
        return horiz_lines + vert_lines


def move_grid_lines_along_axis(lines, axis_name, delta, unit_rect, area_rect):
    """Move vectors so they are always inside grid area.

    lines
        An iterable of pygame.math.Vector2 pairs
        representing the start and end points of a line.
    axis_name
        String which equals either 'x' or 'y'.
    delta
        Integer. The amount of movement in pixels.
    unit_rect
        pygame.Rect instance representing an unit in the
        grid.
    area_rect
        pygame.Rect instance representing the area covered
        by the grid.

    The vectors are scrolled relative to delta, the amount
    of movement in pixels. We say we scroll the vectors
    'relative to' delta because the lines aren't exactly
    moved by the exact amount, but rather by the remainder
    of such amount in relation to the respective unit rect
    dimension (width for x axis and height for y axis).

    This is because lines which go out of the grid area
    are 'warped' to the opposite side of the grid area as to
    appear that the grid is moving indefinitely, thus
    there's no need to move by all the amount, just the
    fraction of it which represents the true movement
    performed.

    ####### extra explanation

    If you're still struggling to grasp the concept,
    you can simulate it by using an instance of
    collections.deque. Try creating the following deque:

    d = deque([1, 0, 0, 0, 0])

    now notice that it doesn't matter if you rotate it
    5, 50 or 500 units (try using the rotate method of
    the deque), the integer 1 always end up in the
    same position.

    Also try rotating it by 1 unit and then by 6 units.
    It always end up only "walking" one position, right?
    Thus, in the end, if you use the remainder of the
    rotation relative to the deque length (5 in this case)
    you obtain the number of positions effectively walked.

    for instance:
      48 % 5 = 3; that is, walking 48 steps is equivalent
                  of walking 3 in terms of final position;
      50 % 5 = 0; that is, walking 50 steps is equivalent
                  of walking no steps at all as far as
                  the final position is concerned;
    """
    ### based on axis_name, define attributes or raise error

    if axis_name == "x":
        length_attr = "width"
    elif axis_name == "y":
        length_attr = "height"
    else:
        raise ValueError("axis_name must be 'x' or 'y'.")

    ### store variables/alias

    t = getattr(area_rect, length_attr)  # total_length
    u = getattr(unit_rect, length_attr)  # unit_length
    d = delta

    ### if movement is greater or equal to an unit length,
    ### decrease movement to remainder; otherwise
    ### just use movement as is.

    if d > 0:
        amount = d % u if d >= u else d
    else:
        amount = d % -u if -d >= u else d

    ### for each in each line, perform movement;
    ### also perform offsets if needed.
    for line in lines:
        for vector in line:
            ## perform movement
            v = getattr(vector, axis_name)  # v 'means' value
            setattr(vector, axis_name, v + amount)

            ## perform offset if needed

            v = getattr(vector, axis_name)

            # if vector reaches or surpasses the edge of
            # the total length, move it back by one total
            # length
            if v >= t:
                setattr(vector, axis_name, v + -t)

            # if, on the contrary, vector goes back beyond
            # the origin, move it forward by one total
            # length
            elif v < 0:
                setattr(vector, axis_name, v + t)


def get_grid_rects(pos, scroll_x, scroll_y, unit_rect):
    """Return screen and level grid rects.

    The position given (usually from mouse cursor) is
    constrained to a grid of whose unit is represented by
    the unit rect provided. The net amount of scrolling in
    x and y axes is also taken into account.

    Screen rect is the one 'touched' by the pos parameter
    on the screen, considering its slight offset caused by
    the scrolling.

    The level rect is obtained by moving the screen rect by
    the reverse scrolling amount, so to reflect its position
    as if the level was never scrolled.

    pos
        2-tuple of integers representing a position in the
        screen (usually from the mouse cursor) in the
        x and y axes, respectively.
    scroll_x, scroll_y
        Integers indicating the amount of scrolling already
        performed in the x and y axes, respectively.
    unit_rect
        pygame.Rect instance indicating an unit in the grid.
    """
    ### store variables
    x, y = pos
    unit_width, unit_height = unit_size = unit_rect.size

    ### calculate topleft position of the grid unit where
    ### the provided position 'touches' the screen;
    ### we store it in a vector object

    horizontal_rest = scroll_x % unit_width
    vertical_rest = scroll_y % unit_height

    x_rest = (x - horizontal_rest) % unit_width
    y_rest = (y - vertical_rest) % unit_height

    grid_x = x - x_rest
    grid_y = y - y_rest

    topleft = grid_x, grid_y

    ### generate and return rects

    screen_rect = Rect(topleft, unit_size)

    level_rect = screen_rect.move(-scroll_x, -scroll_y)

    return screen_rect, level_rect
