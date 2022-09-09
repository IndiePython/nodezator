"""Facility for rectsman package doctests.

>>> ### let's import pygame.Rect and also useful fixtures
>>> from pygame import Rect
>>> from .fixtures import Simple, get_fresh_groups


Other topics part 01
********************

This document has both documentation and tests for the
RectsMan class. Here we visit topics which didn't fit
any specific major theme.


The union_rect property
========================

The RectsManager instance has a read-only property called
union_rect which returns a pygame.Rect instance which is
a union rect of all the underlying rects. This property is
used throughout the entire class for non-destructive
operations like retrieving position or size information
or conditional tests or other operations which don't have
"in place" effects.

Thus, if you plan to perform a series of non-destructive
operations, instead of using the RectsManager instance
directly (by accessing obj.rect) as usual, you might
want to obtain such union rect from obj.rect.union_rect
and use it to retrieve the information you want.

This way you might gain a bit of speed because the
RectsManager instance won't need to generate such union
rect every time.

For instance:

>>> # get group instance
>>> g1, _ = get_fresh_groups()

>>> # each operation below generates a new union rect in
>>> # order to perform the requested operation:

>>> g1.rect.x # generates union rect and returns its "x"
0
>>> # generates union and returns it inflated by (20, 20)
>>> g1.rect.inflate(20, 20)
<rect(-10, -20, 60, 70)>
>>> # generates union and check whether it contains
>>> g1.rect.contains((0, 0, 20, 20))
1

>>> # instead of doing so, you could retrieve the union rect
>>> # and then perform the operations on it:
>>> union_rect = g1.rect.union_rect

>>> # same operations and results as before, but union rect
>>> # is generated only once
>>> union_rect.x
0
>>> union_rect.inflate(20, 20)
<rect(-10, -20, 60, 70)>
>>> union_rect.contains((0, 0, 20, 20))
1

Remember however, operations that change such rect won't
affect the rects manager instance (the underlying rects),
since the union rect obtained from g1.rect.union_rect
is just a regular pygame.Rect instance.

>>> union_rect.x = 20 # we change union rect's "x" to 20
>>> g1.rect.x         # rectsman's "x" is still 0, though
0


Using the RectsManager instance by itself
=========================================

Besides having an API compatible with the one from
pygame.Rect, RectsManager instances can be passed to
functions which accept rect style objects just as
you would do with pygame.Rect instances. For instance,
pygame.draw.rect or pygame.Rect constructor:

>>> # get group instance
>>> g1, _ = get_fresh_groups()

>>> g1.rect
<rect(0, -10, 40, 50)>
>>> a_rect = Rect(g1.rect)
>>> a_rect
<rect(0, -10, 40, 50)>


Reassigning the RectsManager instance
=====================================

Sometimes, instead of resizing and repositioning a
pygame.Rect instance per se, we want to replace it
altogether. By doing something like this:

>>> # we skip it because it is just an example
>>> a_obj.rect = new_rect  # doctest: +SKIP

However, the property in g1.rect was originally read-only,
and would raise an error if we did so. This is why,
in order to keep pygame.Rect API compatibility, instead
of raising an error as would be the expected behaviour
we actually added a "setter" implementation. That is, you
can execute g1.rect = another_rect without raising an error.

But what does this accomplish? We tried to reproduce as
closely as possible what would happen with a pygame.Rect
instance.

Whenever someone replaces a pygame.Rect instance in an
application, we assume that person wants to keep using
whenever rect is in the "rect" attribute, but want to use
one with different position and/or size. That is, the person
wants to keep all the convenient pygame.Rect behaviour,
it is just that the person wants another rect to be used.

So we allow it to happen with RectsManager instances, too.
However, it is obvious that a pygame.Rect can't do the job
of a RectsManager instance (that is, manage multiple rect
instances).

Therefore, whenever a replacement occurs, the RectsManager
instance in the "rect" property of the group ends it is in
fact replaced by another rect. This new rect has the position
and size of the rect we try to use as replacement. However,
the new rect is not the old instance, nor the instance used
as a replacement. It is a new RectsManager instance which
has the same _get_all_rects attribute (thus, manages the
same rects).

This way we simulate a replacement as closely as possible.
That is, the replacement:

- causes the rect in the "rect" attribute to change (ok);
- causes the new rect to have the position and size of the
  one replacing it (ok);

The only difference for a normal replacement between
pygame.Rect instances is that the rect used as replacement
doesn't end up being the actual rect stored in the "rect"
attribute. We don't make this "replacement step" because
if we replace the RectsManager instance by another rect,
we would lose all the convenient RectsManager behaviour.

Also, when the new RectsManager instance tries to assume
the same size of the rect used as replacement, the final
result isn't guaranteed to be exactly equal in all cases.

This is so because of the possible innacuracies of size
transformations which occur in RectsManager instances as
already discussed in the "Size transformation innacuracies"
section.

>>> # get group instance
>>> g1, _ = get_fresh_groups()

>>> # before assigning a new rect to g1.rect, let's store
>>> # a reference to the current RectsManager instance
>>> rects_man = g1.rect
>>> g1.rect
<rect(0, -10, 40, 50)>
>>> # just confirming the instances are the same object
>>> # and are equal
>>> g1.rect is rects_man and g1.rect == rects_man
True

>>> # let's assign a new rect to it now
>>> new_rect = Rect(20, 20, 60, 60) # we store it first
>>> g1.rect = new_rect              # then assign it


>>> # as described, g1.rect is not the old rects_man anymore
>>> g1.rect is rects_man
False

>>> # it isn't the rect used to replace it either
>>> g1.rect is new_rect
False
>>> # but it is equal to it (has the same values)
>>> g1.rect == new_rect
True
>>> g1.rect
<rect(20, 20, 60, 60)>

The only point we couldn't emulate, as discussed earlier,
is that the pygame.Rect in the new_rect variable doesn't
actually take the place of the older instance, as would
happen in a normal attribute reassignment. However, there's
no perfect solution here, only trade-offs.

We decided that allowing g1.rect to be replaced makes more
sense even though the pygame.Rect in new_rect isn't in fact
used as replacement in the end (only its position and size
are used).

It is also the alternative that provides more flexibility
and power for the users. Imagine if executing something as
natural as "g1.rect = new_rect" were to raise an error
instead? It would be quite the departure from how
pygame.Rect instances behave.

Therefore, be aware of this whenever you perform such
operation.


Replacing with another RectsManager instance
--------------------------------------------

Also, because pygame.Rect and the RectsManager have a
compatible API, you can also use other RectsManager
instance to replace an existing one, with the same
results. That is, a new instance replaces the original,
which is neither the original, nor the replacement, but
which has position and size equal to the replacement (or
at least tries to assume the same size).

>>> # get group instances
>>> g1, g2 = get_fresh_groups()

>>> # for instance, let's assign the RectsManager from g1
>>> # to the group g2

>>> # notice first that, obviously, they are not the same
>>> g2.rect is g1.rect
False
>>> # they aren't equal either
>>> g2.rect == g1.rect
False

>>> # before replacing, let's reference the old instance
>>> old_instance = g2.rect

>>> # we now replace
>>> g2.rect = g1.rect

>>> # and check the results...

>>> # it is not the old instance
>>> g2.rect is old_instance
False

>>> # it is neither the same instance used as replacement
>>> g2.rect is g1.rect
False

>>> # but it has the same position and size as the instance
>>> # used as replacement
>>> g2.rect == g1.rect
True


Size transformation locking
===========================

There's still one thing you must be aware when performing
size transformations. Any underlying rect that has its
centerx and/or centery coordinates aligned with the
centerx and/or centery of the RectsManager instance won't
move from there when the size of the RectsManager is
resized. That is, it stays locked in that position.

To unlock it, you'll have to move the individual
rect by itself so it's centerx and/or centery don't align
with the same coordinate from the RectsManager instance
anymore.

The explanation for this is straightforward. As we said
before, resizing the RectsManager works by moving rects
away or closer to the center of the virtual union rect,
proportionally to their current distance.

So, if you double the size of the RectsManager, the
distance of the rects is also multiplied by 2.
Likewise, if you cut the size of the RectsManager
in half, the distance will be divided by 2 as well.

Thus the single rect stays locked if it is in the
centerx and/or centery of the virtual union rect of the
RectsManager instance because it's distance to the center
in that axis (or both) is 0 (zero).

That is, no matter how much you multiply or divide it, It
remains 0, because multiplying/dividing 0 always result in
zero. Let's see this in action:

>>> # get group instance
>>> g1, _ = get_fresh_groups()

>>> # create a new rect from the deflation of our
>>> # RectsManager instance (by doing this, we ensure
>>> # the rect created has the same center as the group
>>> # because inflation/deflation keeps the resulting rect
>>> # centered in the one that originated it)
>>> new_rect = g1.rect.inflate(-30, -30)

>>> # create and append a new Simple instance to the
>>> # group; the instance uses the new rect instantiated
>>> # previously
>>> new_simple = Simple(new_rect)
>>> g1.append(new_simple)

>>> # let's verify its rect center
>>> new_simple.rect.center
(20, 15)

>>> # we them enlarge the RectsManager in place and see
>>> # if the rect in the new_simple instance moved
>>> g1.rect.inflate_ip(50, 50)
>>> new_simple.rect.center # new_simple instance didn't move
(20, 15)

>>> # the same happens if we deflate the RectsManager
>>> g1.rect.inflate_ip(-20, -20)
>>> new_simple.rect.center # it didn't move either
(20, 15)


Extra behaviour
===============

The operations we're about to show were discovered as
unintended yet welcome side-effects of size transformations.
We realized that such size transformations presented very
peculiar effects which might be useful in some cases.

We plan to encapsulate those and other operations in
future designs of the RectsManager class. For more
information about such encapsulations, check the
"Other New methods" section on the test file #04_02.


Mirroring rects relative to center
----------------------------------

Let's say you inverted the signal of the RectsManager's
width, height or both (size). This causes the center of
each rect to be mirrored relative to the center of the
RectsManager isntance in the corresponding axis/axes.
The ascii art below shows a rect inside the rects manager
boundaries and the normal position of such rect, as well
as its position when each axis is mirrored and when both
are mirrored.

   (normal)          (mirror x)
 _____________      _____________
|  _          |    |          _  |
| |_| <--rect |    |         |_| |
|             |    |             |
|      .      |    |      .      |
|    center   |    |             |
|             |    |             |
|_____________|    |_____________|

  (mirror y)       (mirror x and y)
 _____________      _____________
|             |    |             |
|             |    |             |
|             |    |             |
|      .      |    |      .      |
|  _          |    |          _  |
| |_|         |    |         |_| |
|_____________|    |_____________|


>>> # get group instance
>>> g1, _ = get_fresh_groups()

>>> # since we'll change the positions of the underlying
>>> # rects in the group 1, let's store the center of its
>>> # first rect, so we know when its is back in its
>>> # original place; we'll also store the size of the
>>> # rects manager;
>>> first_center = g1[0].rect.center
>>> rects_man_size = g1.rect.size

>>> # now, let's take look at the distance between
>>> # the centerx of the first rect in the group and the
>>> # centerx of the rects manager
>>> g1[0].rect.centerx - g1.rect.centerx
-10

>>> # let's mirror all the rects relative to the center,
>>> # in the x axis by inverting the signal of the
>>> # corresponding dimension (by multiplying the width
>>> # by -1)
>>> g1.rect.width *= -1

>>> # now the centerx of the first rect is at the same
>>> # distance from the rects manager centerx, but its
>>> # signal is inverted, that is, it is at the opposite
>>> # side of the RectsManager along the horizontal axis
>>> g1[0].rect.centerx - g1.rect.centerx
10

>>> ### you can invert their y distance too, by inverting
>>> ### the height; note the centery distance below
>>> g1[0].rect.centery - g1.rect.centery
-5

>>> ### once we invert the height's signal...
>>> g1.rect.height *= -1

>>> # ...the centery of the first rect is at the same
>>> # distance from the rects manager centery as before,
>>> # but its signal is inverted, that is, it is at the
>>> # opposite side of the RectsManager along the vertical
>>> # axis
>>> g1[0].rect.centery - g1.rect.centery
5

>>> # it is important to remember that such operations
>>> # don't actually change the signal of the width or
>>> # height of the RectsManager, because such values
>>> # are always read from the union rect of all rects,
>>> # and since they just, let's say, "switched sides",
>>> # the width and height remain the same, as you can
>>> # see:
>>> g1.rect.size == rects_man_size
True

>>> ### we can also mirror the rects in both axes, by
>>> ### inverting both the width and height at the same
>>> ### time, that is, by inverting the size:
>>> g1.rect.size = tuple(-i for i in g1.rect.size)

>>> ### since we inverted the width, then the height,
>>> ### then both again by inverting the size,
>>> ### the first rect must now be in the same place
>>> ### as before we made the transformations
>>> g1[0].rect.center == first_center
True


Centering the rect on x and y axes
----------------------------------

As we saw in other section, when individual rects have their
centerx and/or centery aligned with the same coordinate
of the RectsManager (that is, when they are equal), that
rect remains locked in the respective axis and this happens
because its distance from the center in that or both axis
is 0.

Though being stuck in such way may be undesirable, it's
really good in other cases, because it leaves the rects
perfectly aligned with one or both axis, so it is good for
things like aligning objects (for instance, UI elements).

You can center all the rects in the horizontal axis by
assigning 0 (zero) to the rects manager height, or in the
vertical axis by assigning 0 to its width, or in both axes
by assigning (0, 0)  to its size.

Below you can see a demonstration in ascii art:

   (normal)        (on horizontal)
 _____________      _____________
|  _          |    |             |
| |_|         |    |             |
|             |    |  _       _  |
|      .      |    | |_|  .  |_| |
|          _  |    |             |
|         |_| |    |             |
|_____________|    |_____________|

 (on vertical)        (on both)
 _____________      _____________
|      _      |    |             |
|     |_|     |    |             |
|             |    |      _      |
|      .      |    |     |_|     |
|      _      |    |             |
|     |_|     |    |             |
|_____________|    |_____________|

Let's see some examples:

>>> # get group instance
>>> g1, _ = get_fresh_groups()

>>> # let's check the current centerx of all rects, just to
>>> # see where they are now
>>> [obj.rect.centerx for obj in g1]
[10, 20, 20, 30]

>>> # now they will all be the same when you assign 0 to
>>> # the width
>>> g1.rect.width = 0

>>> # here, check the current centerx of all rects:
>>> [obj.rect.centerx for obj in g1]
[10, 10, 10, 10]

>>> # and the same can be observed when we assign 0 to
>>> # the height: the centery coordinates all become the
>>> # same:

>>> # current centery of all rects
>>> [obj.rect.centery for obj in g1]
[10, 20, 0, 30]

>>> g1.rect.height = 0

>>> # final centery of all rects
>>> [obj.rect.centery for obj in g1]
[0, 0, 0, 0]

>>> # we can do so at once, by assigning (0, 0) to size,
>>> # let's get a new freshly instantiated group to
>>> # demonstrate
>>> g1, _ = get_fresh_groups()

>>> # the current center of all rects
>>> [obj.rect.center for obj in g1]
[(10, 10), (20, 20), (20, 0), (30, 30)]

>>> # and their centers will all be the same after we assign
>>> # (0, 0) to the size:
>>> g1.rect.size = 0, 0

>>> # as expected, all center positions are (10, 0)
>>> [obj.rect.center for obj in g1]
[(10, 0), (10, 0), (10, 0), (10, 0)]

>>> # the size won't be (0, 0) in the end, though, because
>>> # the RectsManager instance's values are the values
>>> # from an union rect of all rects; that is, though
>>> # they are all centered in the same position now,
>>> # the size of their union is still different from
>>> # (0, 0), as can be seen below:
>>> g1.rect.size
(20, 20)
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
