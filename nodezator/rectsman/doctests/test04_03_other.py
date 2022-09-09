"""Facility for rectsman package doctests.

>>> ### let's import an useful fixture
>>> from .fixtures import get_fresh_groups


Other topics part 03
********************

This document has both documentation and tests for the
RectsMan class. Here we visit topics which didn't fit
any specific major theme.


The keep_rects_attrs(*attr_names) context manager
=================================================

The RectsManager has a method called keep_rects_attrs
which returns a context manager, and thus can be used
in "with blocks".

It works by saving values of specified attributes of
the rects managed by the RectsManager and restoring
such values when exiting the "with block".

It has a single variable-kind parameter which accepts
any number of strings. The string(s) must be the name(s)
of attributes of pygame.Rect which work as property(ies),
that is:

x, y,
top, left, bottom, right,
topleft, bottomleft, topright, bottomright,
midtop, midleft, midbottom, midright,
center, centerx, centery,
size, width, height, w, h

However, no check is performed to guarantee the string(s)
received comply, in order to not lose any speed. 

This method can be used when you want to do something
with the rects temporarily and then return them to their
original values. Like so:

with rectsman.keep_rects_attrs('topleft', 'size'):
    ### you can change the rects as you wish, here,
    ### since they will return to their original
    ### topleft and size values after the "with block"
    ### is left

For instance, the "snap_rects" method which will be
presented on the "rectsman/doctests/test05_align.py"
document uses this content manager so it can perform
an in-place operation temporarily in order to obtain
a union rect when the rects are positioned in a certain
way.

Let's see an example:

>>> # let's say you want to know the area occupied
>>> # by all the rects when you inflate the first
>>> # two by 20 pixels in each dimension...

>>> # get group instance
>>> g1, _ = get_fresh_groups()

>>> # let's check the topleft position and size of the rects

>>> for obj in g1: print(obj.rect)
<rect(0, 0, 20, 20)>
<rect(10, 10, 20, 20)>
<rect(10, -10, 20, 20)>
<rect(20, 20, 20, 20)>

>>> # now we can calculate such area by obtaining the
>>> # union rect of all rects after inflating them the
>>> # ones we want; however, because we do so inside the
>>> # context set by 'keep_rects_attrs', the attributes
>>> # we named are backed up before the code in the
>>> # "with block" and restored after it

>>> with g1.rect.keep_rects_attrs('topleft', 'size'):
... 
...     for n, obj in enumerate(g1):
...         if n < 2:
...             obj.rect.inflate_ip(20, 20)
... 
...     union_rect_inflated_rects = g1.rect.union_rect
... 

>>> # now let's see the union rect we obtained
>>> union_rect_inflated_rects
<rect(-10, -10, 50, 50)>

>>> # so we achieve our purpose of calculating the area
>>> # in the specific conditions; now let's see if the
>>> # rects really kept their topleft position and size...
>>> for obj in g1: print(obj.rect)
<rect(0, 0, 20, 20)>
<rect(10, 10, 20, 20)>
<rect(10, -10, 20, 20)>
<rect(20, 20, 20, 20)>

>>> # yep, everything worked as expected;
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
