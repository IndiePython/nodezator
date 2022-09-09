"""Facility for general mathematic utilities."""

### standard library imports

from math import hypot

from itertools import chain

from string import digits


### constant

MATH_EXPRESSION_CHARS = set((digits + "+-*/" + " ."))

### functions


def get_straight_distance(point_a, point_b):
    """Calculate the straight distance between two points.

    get_straight_distance(point_a, point_b) -> float

    point_a, point_b
        Each is represented by a list or tuple with two
        values: x and y respectively. For instance: (x, y).

    Illustration:
                 ._ _
        (point a)|\   |
                 | \s |
                 |  \ |
                 |   \|
                 |_ _ .(point b)

        where s is the straight distance

    >>> a, b = (10, 10), (20, 20)
    >>> round(get_straight_distance(a, b), 2)
    14.14
    """
    x_a, y_a = point_a
    x_b, y_b = point_b

    distance_x = x_b - x_a
    distance_y = y_b - y_a

    straight_distance = hypot(distance_x, distance_y)

    return straight_distance


def offset_point(point, offset):
    """Return offset point (an int tuple of length 2).

    offset_point(point, offset) -> point

    point
        A list or tuple containing two integers representing
        a point's coordinates in space.
    offset
        A list or tuple containing two integers representing
        amounts to be added to each point coordinate.

    >>> offset_point((10, 10), (5, 5))
    (15, 15)
    >>> offset_point((10, 10), (-5, 5))
    (5, 15)
    >>> offset_point((10, 10), (5, -5))
    (15, 5)
    >>> offset_point((10, 10), (-5, -5))
    (5, 5)
    """
    x, y = point
    x_offset, y_offset = offset

    offset_point = x + x_offset, y + y_offset

    return offset_point


def invert_point(point, invert_x, invert_y):
    """Return point with inverted coordinates as requested.

    Inverting a coordinates means changing the signal.

    point
        A list or tuple with two integers representing
        x and y coordinates of a point.
    invert_x
    invert_y
        Booleans indicating whether the x and y coordinates
        should be inverted, respectively.

    >>> invert_point((10, 10), True, True)
    (-10, -10)
    >>> invert_point((10, 10), True, False)
    (-10, 10)
    >>> invert_point((10, 10), False, True)
    (10, -10)
    >>> invert_point((10, 10), False, False)
    (10, 10)
    """
    x, y = point
    new_x = -x if invert_x else x
    new_y = -y if invert_y else y
    inverted_point = (new_x, new_y)

    return inverted_point


def get_reaching_multiple(step_length, target_length):
    """Return first multiple to reach or surpass distance.

    Parameters
    ==========
    step_length (integer)
        the length of steps towards the target.
    target_length (integer)
        the total length to cover till target.

    This functions is very useful for simple scrolling
    features and was first implemented on the load game
    menu (in the main menu), on the game package.

    >>> get_reaching_multiple(2, 11)
    12
    >>> get_reaching_multiple(10, 101)
    110
    >>> get_reaching_multiple(10, 100)
    100
    >>> get_reaching_multiple(10, 10)
    10
    >>> get_reaching_multiple(10, 9)
    10
    """
    if step_length >= target_length:
        return step_length

    else:

        steps_no, rest = divmod(target_length, step_length)

        return step_length * (steps_no + 1) if rest else step_length * steps_no


### TODO review docstrings of functions below


def get_remaining_intervals(all_indices, intervals_to_subtract):
    """Yield intervals as 2-tuples from remaining indices."""
    ### start by grabbing all remaining indices (those which
    ### don't belong to the intervals to subtract)

    remaining_indices = set(
        ## make a set out of the indices
        set(all_indices)
        ## then remove indices from each interval gathered
        ## in a set
        - set(
            ## chain all the ranges together, so their
            ## indices are all gathered
            chain.from_iterable(
                ## get the ranges of all the intervals
                range(including_start, excluding_end)
                for including_start, excluding_end in intervals_to_subtract
            )
        )
    )

    ## then retrieve and return the intervals formed by
    ## the remaining indices
    return get_intervals(remaining_indices)


def get_intervals(indices):
    """Yield intervals between gaps in indices as 2-tuples.

    Works by yielding the different intervals contained
    in the given indices after sorting them. The intervals
    are defined by the gaps between them (differences of
    more than one unit).

    Parameters
    ==========
    indices (iterable/iterator of integers)
        indices to be separated into intervals by the
        gaps between them (differences of more than one
        unit)

    For instance...

    >>> # here we give the indices already sorted
    >>> list(get_intervals([3, 4, 5, 6, 22, 23, 24, 33]))
    [(3, 7), (22, 25), (33, 34)]

    >>> # but it isn't required...
    >>> list(get_intervals([3, 23, 5, 6, 22, 33, 4, 24]))
    [(3, 7), (22, 25), (33, 34)]

    >>> # if you provide an empty iterable, nothing is
    >>> # yielded...
    >>> list(get_intervals([]));
    []

    The tuples represent, in math notation, [a, b[
    intervals, that is, intervals where a <= x < b,
    also called left-closed, right-open intervals.

    Those intevals are useful, for instance, to create
    range() or slice() objects.
    """
    ### sort indices, obtaining an iterator from them
    indices_iterator = iter(sorted(indices))

    ### assign the first index from the iterator as the
    ### left boundary of an interval
    ###
    ### note that it is ok if a StopIteration exception
    ### is raised here, when next() is executed, because
    ### raising such kind of exception is valid behaviour
    ### inside generators
    including_left_boundary = next(indices_iterator)

    ### we expect the next index from the iterator to
    ### be equal to the current index (the left boundary)
    ### plus one unit, so we define a variable representing
    ### this
    expected_index = including_left_boundary + 1

    ### iterate over the remaining indices in the iterator,
    ### yielding intervals every time you find gaps between
    ### the indices (differences of more than one unit)

    for current_index in indices_iterator:

        ### if the index isn't equal to the expected value
        ### (which is one unit higher than the previous
        ### index), then it can only be higher, since we
        ### assume the indices to be sorted; this means we
        ### have a gap here;
        ###
        ### in this case we yield the current interval
        ### and set a new including_left_boundary for the
        ### next time we yield another interval

        if current_index != expected_index:

            ### yield the 2 indices representing the
            ### boundaries of the current interval (the
            ### left boundary and the expected index,
            ### which work as the excluding right boundary);
            yield (including_left_boundary, expected_index)

            ### we also set the current index as the left
            ### boundary, so it is used for the next
            ### interval (once we find another gap again)
            including_left_boundary = current_index

        ### update the expected index, which is always the
        ### current index plus one unit
        expected_index = current_index + 1

    ### once you leave the "for loop", you'll still have
    ### a including_left_boundary set, waiting for its
    ### right boundary;
    ###
    ### thus we use the expected index as such excluding
    ### right boundary, yielding the last interval
    yield (including_left_boundary, expected_index)


def get_rect_from_points(point_a, point_b):
    """Return rect-like tuple from given points.

    Each of the four elements of the tuple is an integer
    representing, respectively, the left coordinate, the
    top coordinate, the width and the height.
    """
    ### get tuples gathering x's and y's from both points
    xs, ys = zip(point_a, point_b)

    ### calculate left and right, then width

    left, right = (func(xs) for func in (min, max))

    width = right - left

    ### calculate top and bottom, then height

    top, bottom = (func(ys) for func in (min, max))

    height = bottom - top

    ### finally return the tuple
    return (left, top, width, height)


def math_eval(expression_str):
    """Safe evaluation of math expression."""
    if set(expression_str).issubset(MATH_EXPRESSION_CHARS):
        return eval(expression_str)
