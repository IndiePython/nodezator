"""Facility for creation of animation data."""

### standard library imports

from math import pi, sin, cos

from collections import deque

from itertools import cycle


### third-party import
from pygame.math import Vector2


### local import
from ..pygameconstants import FPS


### nodes animation

## define points forming a circle

# how many objects will be rotated
OBJECTS_NO = 3

# multiplicand to obtain quantity of points used
# in the circle
MULTIPLICAND = 12

# quantity of points forming the circle (must be a
# multiple of the number of objects rotated)
QUANTITY = MULTIPLICAND * OBJECTS_NO

# radius of the circle
RADIUS = 20

# create the points forming a circle

POINTS = []

for k in range(QUANTITY):

    value = (k * 2 * pi) / QUANTITY

    x = RADIUS * cos(value)
    y = RADIUS * sin(value)

    POINTS.append((x, y))

# adjust quantity of points based on fps

POINTS = sum(
    # iterable with lists of points
    [[point] for point in POINTS],
    # initial value
    [],
)


## define a general offset for the nodes
NODES_OFFSET = Vector2(-30, -15)

## node animation setting function


def set_node_animation(index, node, parent):
    """Set objects and assign anim. behaviour to node."""
    ### create/reference objects to assist in animation

    d = deque(POINTS)
    d.rotate(index * MULTIPLICAND)

    parent_rect = parent.rect
    node_rect = node.rect

    ### define animation behaviour

    def update():

        ## calculate and assign new center for node

        node_rect.center = parent_rect.topright + NODES_OFFSET + d[0]

        ## rotate points in deque
        d.rotate(1)

    ### assign the animation behaviour to the node
    node.update = update


### robot animation

## define y coordinates representing an object floating
## back and forth vertically in the air

# define initial y values and multiplier to alter their
# quantity, obtaining the values of y ('ys' list)

initial_ys = list(range(-5, 0, 1))
multipliers = [6, 5, 4, 3, 2]

ys = sum([[y] * multiplier for y, multiplier in zip(initial_ys, multipliers)], [])

# now change the 'ys' list so it has the original values,
# plus 0 and plus the original values in reversed order
# and reversed signal
ys = ys + [0] + [-y for y in reversed(ys)]

# then once more alter the 'ys' list so it has the
# same values from before, but with a copy of those
# values in reversed order added to them
ys = ys + list(reversed(ys))

# adjust quantity of points based on fps

multiplier = round(FPS / 30) or 1

ys = sum(
    # iterable with lists of points
    [[y] for y in ys],
    # initial value
    [],
)

## robot animation setting function


def set_robot_animation(robot, parent):
    """Set objects and assign anim. behaviour to robot."""
    ### create/reference objects to assist in animation

    d = deque(ys)

    robot_offset = Vector2(
        [a - b for a, b in zip(robot.rect.center, parent.rect.center)]
    )

    parent_rect = parent.rect
    robot_rect = robot.rect

    ### define animation behaviour

    def update():

        ## calculate and assign new center for robot

        robot_rect.center = parent_rect.center + robot_offset + (0, d[0])

        ## rotate points in deque
        d.rotate(1)

    ### assign the animation behaviour to the robot
    robot.update = update


### general timers

## utility function to create callables that work
## as timers


def get_timer(frames_no):
    """Return a frame-based timer callable.

    That is, the callable returns True a pre-defined
    number of times, then turns False and restarts
    the cycle again.

    Parameters
    ==========
    frames_no (positive integer)
        considering the timer is called once per frame,
        this number represents how many frames or how
        many times True will be returned by calling the
        timer created until it returns False.
    """
    ### create and return timer callable;
    ###
    ### this is actually an instance of the
    ### itertools.cycle().__next__ method

    return cycle((True,) * frames_no + (False,)).__next__


## definition of timer callables

# time during which animation is playing

frames_in_robot_animation = len(ys)
how_many_times_to_play = 3

keep_animation_playing = get_timer(frames_in_robot_animation * how_many_times_to_play)

# time during which animation is paused

quantity_of_frames_in_10_secs = 10 * FPS

keep_animation_paused = get_timer(quantity_of_frames_in_10_secs)
