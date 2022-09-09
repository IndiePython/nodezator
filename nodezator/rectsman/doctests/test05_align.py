"""Facility for rectsman package doctests.

>>> ### let's import an useful fixture
>>> from .fixtures import get_fresh_groups


RectsManager align operations
*****************************

This document contains both documentation and tests
for the RectsManager class. Here we present methods
available for the class which related to alignment
(positioning) of the rects it manages.


RectsManager.snap_rects and snap_rects_ip()
=============================================

The snap_rects_ip method is used to reposition the rects
relative to each other. It works by taking position
information from a rect and assign it to the next rect.

It accepts 3 arguments. The first one is the name of the
rect attribute from which to retrieve the position
information. It defaults to 'topright'. The second one
is also the name of a rect attribute, but this time it is
the attribute wherein to store position information in the
next rect, and defaults to 'topleft'.

Those default arguments result in the rects being
positioned one beside the other, from left to right,
just like the order by which western text is written,
specially English. This is an arbitrary choice, as any
other choices would be equally fine.

Finally, the user may provide a third argument which is
an offset to be applied to the position information. It
defaults to (0, 0), meaning no offset is applied at all.

For instance, snap_rects_ip('topright', 'topleft') would
have this effect:

rects before     |   rects after
(could be any    |   (topright of first rect used as
position)        |   topleft of the next one and so on)
-----------------|-------------------------------------
   ☐             |   ☐☐☐☐
      ☐          |
  ☐              |
     ☐           |
        
This method may be used to reach many different effects.
For instance, to slide square platforms relative to each
other, to form steps or just move in a way to make
difficult for players (try using snap_rects_ip with
'midbottom' and 'midtop', varying the offset from
(-20, 0) to (20, 0) gradually).

The snap_rects() is the "not in place" version of the
snap_rects_ip method, and works by returning the union
rect of the group as if snap_rects_ip were executed
with the arguments passed to snap_rects.

Below we present tests for the snap_rects_ip and
its "not in place" counterpart called snap_rects:

>>> # get group instances
>>> g1, _ = get_fresh_groups()

>>> # check the topleft position of each rect in the group 1
>>> for obj in g1: print(obj.rect.topleft)
(0, 0)
(10, 10)
(10, -10)
(20, 20)

>>> # now let's position the objects so that each of them
>>> # are beside the other by assigning the topright of
>>> # the rect of one object to the topleft of rect of the
>>> # next one
>>> g1.rect.snap_rects_ip('topright', 'topleft')

>>> # then let's check whether the topright of one rect
>>> # is indeed to topleft of the next one...
>>> for obj in g1:
...     print(obj.rect.topleft, obj.rect.topright)
(0, 0) (20, 0)
(20, 0) (40, 0)
(40, 0) (60, 0)
(60, 0) (80, 0)

As you can see above, the topright of one object is being
used as the topleft of the next one and so on.

You can also apply an offset:

>>> # get a new group instance
>>> g1, _ = get_fresh_groups()

>>> # now let's perform a similar alignment, but offset
>>> # the position by 10 pixels horizontally before
>>> # assigning each position to the next rect
>>> g1.rect.snap_rects_ip('topright', 'topleft', (10, 0))

>>> # then let's check whether the topright of one rect
>>> # is indeed to topleft of the next one...
>>> for obj in g1:
...     print(obj.rect.topleft, obj.rect.topright)
(0, 0) (20, 0)
(30, 0) (50, 0)
(60, 0) (80, 0)
(90, 0) (110, 0)

As you can see above, the topright of one object after
being offset by 10 pixels in the x axis is being used
as the topleft of the next one and so on.

We now present tests for the snap_rects() method. Remember
that snap_rects() is not supposed to change the position
of the rects, just return an union rect as if the rects
had their position changed by snap_rects_ip (even though,
in practice, the method works by changing the position of
the rects, obtaining the union rect, then returning the
rects to their original positions afterwards).

>>> # get a new group instance
>>> g1, _ = get_fresh_groups()

>>> # let's look at the rects manager and the rects of its
>>> # objects

>>> g1.rect
<rect(0, -10, 40, 50)>

>>> for obj in g1: print(obj.rect)
<rect(0, 0, 20, 20)>
<rect(10, 10, 20, 20)>
<rect(10, -10, 20, 20)>
<rect(20, 20, 20, 20)>

>>> # since all objects in the group have rects 20 pixels
>>> # long by 20 pixels high, and the topleft of the rect
>>> # of the first object is positioned at (0, 0), by
>>> # aligning the topright with topleft we expect to
>>> # end up with a union rect starting from (0, 0) and
>>> # 80 pixels long (4 rects of 20 pixels) by 20 pixels
>>> # high (all rects are at the same height and have the
>>> # same height);
>>> # so, let's see if snap_rects works as expected;
>>> g1.rect.snap_rects('topright', 'topleft')
<rect(0, 0, 80, 20)>

>>> # it indeed returned the union rect we expected; let's
>>> # also see if the rects manager and its objects remain
>>> # the same...

>>> g1.rect
<rect(0, -10, 40, 50)>

>>> for obj in g1: print(obj.rect)
<rect(0, 0, 20, 20)>
<rect(10, 10, 20, 20)>
<rect(10, -10, 20, 20)>
<rect(20, 20, 20, 20)>

>>> # again, the method behaved as expected

Furthermore, the method has some interesting outcome
when combined with the fit() method. If, for instance,
you align the objects one beside the other, like we just
did in the previous tests, and then fit() them to another
rect, the objects will be positioned evenly distributed
horizontally inside the rect in which you want to fit the
group.

Many other interesting outcomes may exist from combinations
and variations of different methods with snap_rects_ip,
but research on this will have to wait until other tasks
of higher priority are done.
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
