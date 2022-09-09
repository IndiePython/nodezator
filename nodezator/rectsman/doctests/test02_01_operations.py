"""Facility for rectsman package doctests.

RectsManager Rect-like operations part 01
*****************************************

This document contains both documentation and tests
for the RectsManager class. Here we present operations
(properties/methods) available for the class which it
has in common with the pygame.Rect API.

Such operations don't include the "special methods" (those
using double underscores), which are present in yet another
document. That is, except for the __repr__ method, which
was presented in the previous document due to how much it is
used in other tests to obtain informative representations
of the RectsManager instance for testing.


Introduction
============

Once instantiated, the possible operations to perform are
exactly the same as the ones in the pygame.Rect class. The
only difference is the exact effect: for instance, since
the RectsManager instance represents a group of rects,
moving it "in place" makes all the rects that it represents
to move along, keeping their relative positions.

If the "in place" operation changes the RectsManager size,
however, it doesn't change the size of the rects it
represents. Instead, it changes the distance from each rect
center to the RectsManager center in the same proportion of
the size change.

Whenever the operation performed isn't "in place", a rect
representing the union rect of all rects is built and the
operation is performed on it, with the return value being
further returned.

Before presenting each operation, let's first import
two functions to help us test such operations.

>>> from .fixtures import (
...   get_fresh_groups,
...   check_error_raising
... )

The get_fresh_groups function returns two custom instances
of a class representing a group of objects. Each object
in the groupss have a "rect" attribute containing a
pygame.Rect object representing its position and
dimensions. Sections will get the groups from this
function at the beginning, using them for testing.

Since the groups returned are new instances, freshly
set, there's no effects from previous tests, so they
can be used to keep the effects of different sets of
tests independent from each other.

The check_error_raising function performs method calls
using the given method names and arguments and checks if
the expected error is raised, with the expected message,
too.  Sections will use this function to test if the
operations being tested raise errors as expected from
the given invalid/insufficient arguments.


Operations using properties
===========================

All the position properties can be both retrieved and set,
which include:

x, y,
top, left, bottom, right,
topleft, bottomleft, topright, bottomright,
midtop, midleft, midbottom, midright,
center, centerx, centery

(x and y are the same as left and top respectively; in
fact, left and top are their aliases)

Here are some related tests:

>>> # get group instances
>>> g1, g2 = get_fresh_groups()

>>> # getting different coordinates from each group
>>> g1.rect.right
40
>>> g2.rect.left
90

>>> # Now let's align the right of the first group with the
>>> # left of the second one (90, as we saw above)
>>> g1.rect.right = g2.rect.left
>>> g1.rect.right
90

The size-related properties are also available as both
getters and setters, just like in the pygame.Rect class.

size, width, height, w, h
(w and h are the same as width and height respectively;
in fact, width and height are their aliases)

>>> # get group instance
>>> g1, _ = get_fresh_groups()

>>> # let's get it's size and then increase it
>>> g1.rect.size
(40, 50)
>>> g1.rect.size = 60, 80
>>> g1.rect.size # as expected, size was updated
(60, 80)

The type checking and errors raised (when applicable)
are also compatible with pygame.Rect behaviour.

>>> # for instance, let's use the first rect in the
>>> # group (since it is a pygame.Rect instance) and the
>>> # RectsManager instance itself and compare the error
>>> # messages when causing different errors

>>> # get group instance
>>> g1, _ = get_fresh_groups()

>>> # passing invalid values

>>> try: g1[0].rect.left = 'a string'
... except Exception as e:
...     rect_error_type = type(e)
...     rect_error_msg  = str(e)

>>> try: g1.rect.left = 'a string'
... except Exception as e:
...     manager_error_type = type(e)
...     manager_error_msg  = str(e)

>>> rect_error_type == manager_error_type # same error type
True
>>> rect_error_msg == manager_error_msg # same error message
True

>>> # not passing enough values

>>> try: g1[0].rect.size = 10      # pygame.Rect instance
... except Exception as e:
...     rect_error_type = type(e)
...     rect_error_msg  = str(e)

>>> try: g1.rect.size = 10         # RectsManager instance
... except Exception as e:
...     manager_error_type = type(e)
...     manager_error_msg  = str(e)

>>> rect_error_type == manager_error_type # same error type
True
>>> rect_error_msg == manager_error_msg # same error message
True

Curiosity: when we were writing this documentation, we
noticed inconsistencies between errors raised from the
pygame.Rect class (different errors types being raised
for operations of the same nature).

For instance, all properties of pygame.Rect were raising
a TypeError with the "invalid rect assignment" message,
except for the "width" property, which was raising
SystemError with a different message. By the time you're
reading this, these issues might already be solved, since
they were already reported in the "issues" section of the
pygame online repository in the following link:
https://github.com/pygame/pygame/issues/1205

Just rest assured that the RectsManager will mirror the
behaviour of a pygame.Rect instance regarding errors
raised for wrong assignments, no matter the behaviour.

Size transformation innacuracies
================================

Just beware that size transformation isn't always
accurate because of the rounding that is applied in
the distance from center of all underlying rects when
positioning them. Size transformations are also limited
by the size of the underlying rects.

For instance, if the smallest rect managed by the
RectsManager instance has the size (20, 20), them the
RectsManager will never be able to assume a smaller size,
because, as said many times, the current implementation
of the RectsManager doesn't change the size of its
managed rects, but move them away or close to the
center.

Even when working with bigger values the rounding can
still cause innacuracies, though much smaller, usually
a difference of one pixel.

Here are some demonstrations

>>> # get group instance
>>> g1, _ = get_fresh_groups()

>>> g1.rect.size
(40, 50)
>>> # if we resize the g1 group to (20, 20), don't be
>>> # surprised when you check the actual size and
>>> # realize it is in fact not (20, 20)
>>> g1.rect.size = (20, 20)
>>> g1.rect.size
(24, 24)
>>> # let's try other values...
>>> g1.rect.size = (38, 38)
>>> g1.rect.size
(34, 34)
>>> g1.rect.size = (39, 39)
>>> g1.rect.size
(38, 38)
>>> g1.rect.size = (40, 40)
>>> g1.rect.size
(38, 38)
>>> g1.rect.size = (42, 42)
>>> g1.rect.size
(40, 40)

>>> # in the case of this group, it seems size changes
>>> # above 42 yield accurate results
>>> g1.rect.size = (44, 44)
>>> g1.rect.size
(44, 44)

>>> # though, now, that the group assumed (44, 44) in size,
>>> # it can somehow be resized to (42, 42)
>>> g1.rect.size = (42, 42)
>>> g1.rect.size
(42, 42)


We're not sure there is a satisfactory solution to these
innacuracies due to different trade offs between the
possible solutions. However, we consider this to be a
minor issue, and even a natural one which is a result
of the design choices made and its related calculations.

Had we opted to go for a design which allowed resizing
the underlying rects, we would have even more possibilities
to explore to come up with a solution, but then the
underlying rects would lose even more of their "autonomy"
to the RectsManager class, which can already move it
around as it pleases.

We don't consider changing the size of the underlying
rects to be appropriate behaviour for our purpose, but we
acknowledge that there may be legitimate use cases where
this ability could be desirable and we even address the
possibility in the "Possible future design" section of
the test file #04_02.

In the next sections we present a lot of RectsManager
operations available as methods. Except where explicitly
explained, they work just like their pygame.Rect
equivalents. All the positional variable arguments
(the ones named "*args") work just like in the pygame.Rect
methods.


RectsManager.move and move_ip(*args)
====================================

"move" returns the union rect of all the rects, but as if
moved using the arguments. This operation, just like in
pygame.Rect, doesn't change the position in place.

>>> # get group instance
>>> _, g2 = get_fresh_groups()

>>> g2.rect               # g2 rects manager
<rect(90, 0, 60, 40)>
>>> g2.rect.move(-30, 50) # g2 moved union
<rect(60, 50, 60, 40)>
>>> g2.rect               # g2 rect remains the same
<rect(90, 0, 60, 40)>

"move_ip" ("ip" stands for "in place") moves all rects in
place, that is, it actually changes the positions of the
rects. For instance:

>>> # below we can see the values of each individual rect
>>> for obj in g2: print(obj.rect)
<rect(100, 0, 20, 20)>
<rect(110, 10, 20, 20)>
<rect(90, 20, 20, 20)>
<rect(130, 0, 20, 20)>

>>> # now we move g2 using move_ip
>>> g2.rect.move_ip(-30, 50)

>>> # now the entire group moved, that is, each underlying
>>> # rect moved
>>> for obj in g2: print(obj.rect)
<rect(70, 50, 20, 20)>
<rect(80, 60, 20, 20)>
<rect(60, 70, 20, 20)>
<rect(100, 50, 20, 20)>

>>> # as expected, the values of the rects manager now
>>> # reflect the new positions of the rects
>>> g2.rect
<rect(60, 50, 60, 40)>

Type checking and error raising is also pygame.Rect
compliant:

>>> # for instance, let's use the RectsManager instance
>>> # and the first rect in the group (since it is a
>>> # a pygame.Rect instance) and compare the error
>>> # messages when causing different errors

>>> rects_man, pygame_rect = g2.rect, g2[0].rect
>>> method_names = "move", "move_ip"
>>> incorrect_args = (
...   ('a_string', 2), # string is an invalid arg
...   (2,)             # not enough args
... )
>>> # as can be seen below, both objects raise the same
>>> # errors when faced with the same problems
>>> check_error_raising(
... rects_man, pygame_rect, method_names, incorrect_args)
True
"""

from doctest import DocTestSuite


def load_tests(loader, tests, pattern):
    """Return a test suite.

    This function is used for test discovery and its name,
    signature and return value are defined by the load_tests
    protocol described in the standard library unittest
    module online documentation.
    """
    ### return a test suite from the doctests in this module
    return DocTestSuite()
