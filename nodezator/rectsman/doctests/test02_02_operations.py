"""Facility for rectsman package doctests.

RectsManager Rect-like operations part 02
*****************************************

This document contains both documentation and tests
for the RectsManager class. Here we continue presenting
operations (properties/methods) available for the class
which it has in common with the pygame.Rect API.

Such operations don't include the "special methods" (those
using double underscores), which are present in yet another
document.

Before continueing to present the operations, let's import
the pygame.Rect class and also two functions to help us
test such operations.

>>> from pygame import Rect
>>> from .fixtures import (
...   get_fresh_groups,
...   check_error_raising
... )

RectsManager.inflate and inflate_ip(*args)
==========================================

"inflate" returns an inflated union rect. To deflate it in
any dimension, just use negative values. It doesn't change
the size nor position of the underlying rects, only the
size/position of the union rect returned (it doesn't work
in place).

Though its topleft positions changes, the rect is kept
centered in the original center position, except if the
amounts received are too small (between -2 and 2), in which
case, the center will be off.

>>> # get group instance
>>> g1, _ = get_fresh_groups()

>>> # let's check the group size and center (values from
>>> # the RectsManager)
>>> g1.rect.size, g1.rect.center
((40, 50), (20, 15))

>>> # let's also check the topleft of the first rect
>>> g1[0].rect.topleft
(0, 0)

>>> # let's increase both dimensions by 20
>>> # and see if the center remains the same
>>> inflated_union = g1.rect.inflate(20, 20)

>>> # as you can see, the inflated rect returned kept it's
>>> # center and the size increase by the correct amounts:
>>> inflated_union.size, inflated_union.center
((60, 70), (20, 15))

>>> # but neither the group nor its items were affected:
>>> g1.rect.size, g1.rect.center # same as before
((40, 50), (20, 15))
>>> g1[0].rect.topleft           # same as before
(0, 0)


"inflate_ip" works just like "inflate", but works in place.
It changes the center of the individual rects so that the
distance between each rect center and the center of the
group is increased/decreased proportionally to the amount
of change in the rect's size.

In other words, RectsManager.inflate_ip operation doesn't
call "inflate_ip" on its underlying rects. Instead, it
moves them around (internally, "move_ip" is used) away from
or towards the center, so that the final positions of the
underlying rects forms an union rect which has the
resulting dimensions of the inflate operation.

>>> # let's execute the same operation from earlier, but
>>> # using "inflate_ip"; this changes the distance of the
>>> # individual rects from the group center so that the
>>> # union rect of the group now assumes the new size
>>> # resulting from the inflating operation
>>> g1.rect.inflate_ip(20, 20)
>>> g1.rect.size, g1.rect.center
((60, 70), (20, 15))

>>> # also notice the position of the first rect changed
>>> # from (0, 0), as previously observed in the "inflate"
>>> # method tests, to (-10, -3)
>>> g1[0].rect.topleft
(-10, -3)

Type checking and error raising is also pygame.Rect
compliant:

>>> # for instance, let's use the RectsManager instance
>>> # and the first rect in the group (since it is a
>>> # a pygame.Rect instance) and compare the error
>>> # messages when causing different errors

>>> rects_man, pygame_rect = g1.rect, g1[0].rect
>>> method_names = "inflate", "inflate_ip"
>>> incorrect_args = (
...   ('a_string', 2), # string is an invalid arg
...   (2,) # and here we don't have enough args
... )
>>> # as can be seen below, both objects raise the same
>>> # errors when faced with the same problems
>>> check_error_raising(
... rects_man, pygame_rect, method_names, incorrect_args)
True


RectsManager.clamp and clamp_ip(*args)
======================================

"clamp" will just return a union rect from all rects which
was clamped using the arguments. Clamping is when a rect
is moved to be completely inside another rect. This other
rect is defined in the arguments. If the rect used for
clamping is too small, the clamped rect is centered on it
instead, but the size is not changed.

>>> # get group instance
>>> g1, _ = get_fresh_groups()

>>> clamped_union = g1.rect.clamp((0, 0, 120, 100))
>>> # the size of union is the same as the group's
>>> clamped_union.size == g1.rect.size
True
>>> # but it's position isn't, since it was clamped
>>> # to the rect represented by the arguments
>>> # (0, 0, 120, 100)
>>> clamped_union.topleft == g1.rect.topleft
False


The "clamp_ip" works just like "clamp", but instead of
returning a clamped union rect, it moves all rects by
the same amount of movement which would otherwise be
performed on the union rect if using "clamp".

>>> # this means that the operation below...
>>> g1.rect.clamp_ip((0, 0, 120, 100))

>>> # ...now changes the position of the group: it now has
>>> # the same position as the union rect from the "clamp"
>>> # tests
>>> g1.rect.topleft
(0, 0)

Type checking and error raising is also pygame.Rect
compliant:

>>> # for instance, let's use the RectsManager instance
>>> # and the first rect in the group (since it is a
>>> # a pygame.Rect instance) and compare the error
>>> # messages when causing different errors

>>> rects_man, pygame_rect = g1.rect, g1[0].rect
>>> method_names = "clamp", "clamp_ip"
>>> incorrect_args = (
...   (10, 20, 'a_string', 30), # string is an invalid arg
...   (10, 20, 30) # and here we don't have enough args
... )
>>> # as can be seen below, both objects raise the same
>>> # errors when faced with the same problems
>>> check_error_raising(
... rects_man, pygame_rect, method_names, incorrect_args)
True


RectsManager.clip(*args)
========================

"clip" will just return a union rect from all rects, but
clipped using the arguments. Clipping is when a rect is
cropped using another rect, which is defined in the
arguments. In other words, it returns a new pygame.Rect
whose position and area corresponds to the area of
intersection between the two rects (the RectsManager
instance and the provided rect). Different from other
methods, "clip" doesn't have an "in place" version.

>>> # get group instance
>>> g1, _ = get_fresh_groups()

>>> g1.rect
<rect(0, -10, 40, 50)>
>>> g1.rect.clip(20, 20, 100, 100)
<rect(20, 20, 20, 20)>

Whenever the rect provided/defined on the arguments
doesn't even overlap the union rect representing the
RectsManager instance, no cropping can be done, so
a pygame.Rect with same topleft as the RectsManager
instance and size 0 is returned:

>>> g1.rect
<rect(0, -10, 40, 50)>
>>> # no overlapping:
>>> clipped_union = g1.rect.clip(200, 200, 50, 50)
>>> clipped_union
<rect(0, -10, 0, 0)>

Remember that pygame.Rect instances which have the value
0 (zero) for any or both dimensions (width and height)
evaluate to False in truth tests/when converted with
built-in bool:

>>> if clipped_union: print("This won't be printed")
>>> bool(clipped_union)
False

In other words, a pygame.Rect only returns True when it
has an area of 0, which is a pretty logical conclusion and
in my opinion a good design choice.

Though it has no "in place" equivalent, in order to
achieve an "in place" effect, you can just replace your
RectsManager instance by the resulting rect, just as
you'd do with a regular pygame.Rect instance:

>>> clipped_union = g1.rect.clip(20, 20, 100, 100)

>>> # only assign if the clipped union actually has an
>>> # area, that is, if our union rect really overlaps
>>> # with the one in the arguments
>>> if clipped_union: g1.rect = clipped_union

>>> # now the underlying rects were repositioned so that
>>> # their union rect now assumes the position and
>>> # dimensions of the clipped union rect (well, at
>>> # least approximately the same dimensions)
>>> g1.rect
<rect(20, 20, 24, 24)>

>>> # note that, due to RectsManager inherent issues
>>> # regarding rounding (see the section entitled
>>> # "Size transformation innacuracies" in the previous
>>> # test file) the dimensions don't end up exactly the
>>> # same (4 pixels of difference in each dimension)

We'll talk more about this mechanism in the test file
#04_01, "Reassigning the RectsManager instance" section.

Type checking and error raising for the "clip" method is
also pygame.Rect compliant:

>>> # for instance, let's use the RectsManager instance
>>> # and the first rect in the group (since it is a
>>> # a pygame.Rect instance) and compare the error
>>> # messages when causing different errors

>>> rects_man, pygame_rect = g1.rect, g1[0].rect
>>> method_names = "clip",
>>> incorrect_args = (
...   (10, 20, 'a_string', 30), # string is an invalid arg
...   (10, 20, 30) # and here we don't have enough args
... )
>>> # as can be seen below, both objects raise the same
>>> # errors when faced with the same problems
>>> check_error_raising(
... rects_man, pygame_rect, method_names, incorrect_args)
True


RectsManager.union, union_ip, unionall and unionall_ip
======================================================

"union" returns a rect which corresponds to the union
between all group rects and the rect received on
the arguments. "unionall" works the same way, but instead
of another rect, its argument is a sequence of rects
(or objects defining rects, like tuples and lists).

Their "in place" versions make it so the group assumes
the same position and size of the union rect that would
be returned in the normal versions. "In place" version
actually change the position of the rects in the group.

>>> # get group instance
>>> g1, _ = get_fresh_groups()

>>> # union
>>> union_rect = g1.rect.union((70, -20, 40, 40))
>>> union_rect
<rect(0, -20, 110, 60)>

>>> # union_ip
>>> # the previous operation didn't change the group:
>>> g1.rect
<rect(0, -10, 40, 50)>

>>> # but now it will (when using the "in place" version)
>>> g1.rect.union_ip((70, -20, 40, 40))
>>> # now the group has changed; it is equal to the
>>> # union rect returned by "union"
>>> g1.rect == union_rect
True

>>> # now let's try unionall and unionall_ip:

>>> # let's define a sequence (list) of rects (or, in this
>>> # case, "rect-like" objects), since unionall works with
>>> # sequences
>>> rects = [
...   (-10, -30, 20, 20),
...   (100, 100, 30, 30),
... ]
>>> unionall_rect = g1.rect.unionall(rects)
>>> unionall_rect
<rect(-10, -30, 140, 160)>

>>> # the previous operation didn't change the group:
>>> g1.rect
<rect(0, -20, 110, 60)>

>>> # but now it will (when using the "in place" version)
>>> g1.rect.unionall_ip(rects)

>>> # now the group has changed; it is equal to the
>>> # union rect returned by "unionall"
>>> g1.rect == unionall_rect
True

Type checking and error raising is also pygame.Rect
compliant:

>>> # for instance, let's use the RectsManager instance
>>> # and the first rect in the group (since it is a
>>> # a pygame.Rect instance) and compare the error
>>> # messages when causing different errors

>>> # testing union/union_ip:

>>> rects_man, pygame_rect = g1.rect, g1[0].rect
>>> method_names = "union", "union_ip"
>>> incorrect_args = (
...   (10, 20, 'a_string', 30), # string is an invalid arg
...   (10, 20, 30) # and here we don't have enough args
... )
>>> # as can be seen below, both objects raise the same
>>> # errors when faced with the same problems
>>> check_error_raising(
... rects_man, pygame_rect, method_names, incorrect_args)
True

>>> # testing unionall/unionall_ip:

>>> rects_man, pygame_rect = g1.rect, g1[0].rect
>>> method_names = "unionall", "unionall_ip"
>>> incorrect_args = (
...   [(10, 20, 'a_string', 30)], # string is invalid arg
...   [(10, 20, 30)] # and here we don't have enough args
... )
>>> # as can be seen below, both objects raise the same
>>> # errors when faced with the same problems
>>> check_error_raising(
... rects_man, pygame_rect, method_names, incorrect_args)
True


RectsManager.fit(*args)
=======================

"fit" will just return a union rect from all rects, but
with the size increased/decreased and moved to fit inside
another rect defined in the arguments.

Such change in size applied in the union rect happens
without changing its aspect ratio. Just like the "clip"
method, this operation doesn't have an "in place" version.

>>> # get group instance
>>> g1, _ = get_fresh_groups()

>>> # let's first inflate the group so it is easier to fit
>>> # it inside a smaller rect in our example; we do this
>>> # to avoid having to decrease the group from its original
>>> # size, which is relatively small and could cause
>>> # innacuracies)
>>> g1.rect.inflate_ip(100, 110)
>>> g1.rect.size
(140, 160)

>>> # fitting it inside a smaller rect
>>> fit_rect = g1.rect.fit((0, 0, 80, 40))
>>> fit_rect.size
(35, 40)

>>> # note that the aspect ratio is kept the same:
>>> 140/160 == 35/40
True
>>> # as explained, this operation also moves the union
>>> # rect so it is centered on the rect passed as argument,
>>> # though sometimes it may be off by one pixel:
>>> fit_rect.center, Rect(0, 0, 80, 40).center
((39, 20), (40, 20))
>>> # the center of the rect represented by (0, 0, 80, 40),
>>> # the one given as the argument to g1.rect.fit, is
>>> # (40, 20), but because how pygame.Rect instances are
>>> # positioned relative to one another the actual position
>>> # may be one pixel off, as happens here.

If you ever desire to perform an operation equivalent to
an "in place" version of the RectsManager.fit, you can
check the "Reassigning the RectsManager instance" section
in the test file #04_01.

Type checking and error raising is also pygame.Rect
compliant:

>>> # for instance, let's use the RectsManager instance
>>> # and the first rect in the group (since it is a
>>> # a pygame.Rect instance) and compare the error
>>> # messages when causing different errors

>>> rects_man, pygame_rect = g1.rect, g1[0].rect
>>> method_names = "fit",
>>> incorrect_args = (
...   (10, 20, 'a_string', 30), # string is an invalid arg
...   (10, 20, 30) # and here we don't have enough args
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
