"""Facility for rectsman package doctests.

Special methods 02
******************

This documents is part of a series containing both
documentation and tests for the RectsManager class.
In this document we continue presenting operations
performed by special methods, that is, those which
use double underscores in their names.

The __repr__ method, however, was presented much earlier,
in a previous test file, due to how informative it is
about the values in RectsManager instances.

Not all special methods have custom implementations,
though. This is so because either such methods are not
needed or because the default implementation from the
"object" type is used instead.

>>> ### let's import Rect and also useful fixtures
>>> from pygame import Rect
>>> from .fixtures import (
... Simple, ListGroup, get_fresh_groups
... )


String conversion (__str__ method)
==================================

The output of the __str__ method is exactly the same as
the one from the __repr__ method:

>>> # get group instance
>>> g1, _ = get_fresh_groups()

>>> repr(g1.rect) == str(g1.rect)
True


Truth value testing/boolean conversion (__bool__ method)
========================================================

This method returns "bool(union_rect)", since the union
rect represents the rect values of the RectsManager
instance.

In pygame.Rect (of which our union rect is an instance),
this operation returns False if either the width or height
or both are 0 (zero). In other words, we could say a rect
returns False for truth value testing if it's area is 0.

All other combinations where neither the width nor the
height is 0 (zero) return True, regardless of whether
they are positive or negative, as long as they aren't 0.

>>> # get group instance
>>> g1, _ = get_fresh_groups()

>>> g1.rect
<rect(0, -10, 40, 50)>
>>> bool(g1.rect)
True

>>> # building a group which would result in False for
>>> # truth value testing (because its height equals 0):
>>> gx = ListGroup((
...   Simple(Rect( 0, 0, 10, 0)),
...   Simple(Rect(20, 0, 10, 0))
... ))
>>> gx.rect # height == 0
<rect(0, 0, 30, 0)>
>>> bool(gx.rect)
False


Handling missing attributes (__getattr__ method)
================================================

__getattr__, as we know, is called with the name of
an attribute (or method) when __getattribute__ can't find
it in the instance dictionary.

In our implementation we attempt returning
"getattr(union rect, name)", so that the missing
attribute in the union rect raises an error from a
pygame.Rect instance (which the union rect is), thus
fully emulating the behaviour of that class.

>>> # get group instance
>>> g1, _ = get_fresh_groups()

>>> # for instance, let's use the RectsManager instance
>>> # and the first rect in the group (since it is a
>>> # a pygame.Rect instance) and compare the error
>>> # messages when causing different errors;

>>> rects_man, pygame_rect = g1.rect, g1[0].rect

>>> # as can be seen below, both objects raise the same
>>> # errors when faced with the same problems

>>> # pygame.Rect behaviour:
>>> pygame_rect.hello
Traceback (most recent call last):
...
AttributeError: 'pygame.Rect' object has no attribute 'hello'

>>> # RectsManager has same behaviour:
>>> rects_man.hello
Traceback (most recent call last):
...
AttributeError: 'pygame.Rect' object has no attribute 'hello'


No custom attribute setting (__setattr__ method)
================================================

Even though we managed to develop a satisfactory __setattr__
method, we decided not to implement it. We wanted a custom
__setattr__ implementation for the sole purpose of emulating
the pygame.Rect error raising behaviour since pygame.Rect
instances don't allow new attributes.

And we developed it, but we decided not to implement such
solution because it made assigning values to properties a
bit slower, about 30%. Even more so because manipulating
the values of properties is a vital feature of a rect
instance, so that the small loss is multiplied many times
by all the property access which is so common when
handling rects.

Also, there's no inherent problem in ommiting a __setattr__
implementation. The RectsManager still works just like a
pygame.Rect for all regular usage. The only difference is
that it won't complain if you create new attributes or
overrides existing ones, so you just must be careful,
that's all.

And besides, not being able to set attributes in
pygame.Rect instances seems to be more a side-effect of
its C implementation than something intentional. Though
this is just a conjecture.

Even so, we'd like to recommend not setting new attributes
nor overriding existing ones in RectsManager instances,
since this ability is more an implementation detail than
a feature of itself.

Finally, because it can be useful one day, we present
here our custom implementation of the __setattr__ method
and accompanying class attribute which we decided not to
implement:

    ### class attribute to hold names of attributes that
    ### can be overrided
    ###
    ### _allowed_names = (
    ###
    ###    ### spatial properties:
    ###    'left', 'top', 'right', 'bottom', 'x', 'y',
    ###    'topleft', 'topright', 'bottomleft',
    ###    'bottomright', 'center', 'centerx', 'centery',
    ###    'midleft', 'midright', 'midtop', 'midbottom',
    ###    'width', 'height', 'size', 'w', 'h',
    ###
    ###    ### make _get_all_rects attribute overrideable
    ###    '_get_all_rects'
    ###
    ### )

    ### method definition
    ### def __setattr__(self, name, value):

        ### if attribute being set is allowed to be set,
        ### delegate to object.__setattr__, where everything
        ### is handled appropriately

        ### if name in self._allowed_names:
            ### super().__setattr__(name, value)

        ### otherwise delegate to the __setattr__ of a
        ### pygame.Rect instance, where a proper error will
        ### be raised (since it is not in the pygame.Rect
        ### API and new names can't be set on pygame.Rect
        ### instances)

        ### else:
            ### setattr(self._sample_rect, name, value)

Even if someday we design a way to implement this
functionality without slowing down the operation, we'll
still leave the "_get_all_rects" attribute overridable,
though, as you can see in the code shown above. We explain
why in the "Swapping managed rect (overriding _get_all_rects
attribute)" sections in the next test file.


Attribute deletion (__delattr__ method)
=======================================

Attribute deletion in RectsManager instances delegates the
deletion to the union rect instance, in order to emulate
pygame.Rect behaviour when raising errors, since the union
rect is an instance of that class.

This means that besides not being able to delete the union
rect attributes, which is natural behaviour, you also won't
be able to delete attributes inherent to the RectsManager
class, like "_get_all_rects", for instance.

However, as this tests were being written, some issues
were observed when trying to delete properties. Such issues
were submitted to the pygame online repository in this link:

https://github.com/pygame/pygame/issues/1231

Since some of those issues cause fatal errors, we couldn't
implement tests for them, because such errors force the
tests to exit. You can check the link for more information
as well as to verify if the issue was already solved.

The other part of the issue regards only irregularities in
error type and message, and thus they can be reproduced
here.

As you can read in the issue linked above, a recent fix for
those erros seem to be on the way, if not already
implemented by the time you are reading this. Such fix
will make all attempted deletions to raise AttributeError,
which is the expected behaviour.

>>> # get group instance
>>> g1, _ = get_fresh_groups()

>>> # the deletion of attributes like width and height
>>> # raise attribute errors

>>> del g1.rect.width # doctest: +ELLIPSIS
Traceback (most recent call last):
...
AttributeError: can...t delete attribute

>>> del g1.rect.height # doctest: +ELLIPSIS
Traceback (most recent call last):
...
AttributeError: can...t delete attribute

>>> del g1.rect.topleft # doctest: +ELLIPSIS
Traceback (most recent call last):
...
AttributeError: can...t delete attribute

>>> del g1.rect.size # doctest: +ELLIPSIS
Traceback (most recent call last):
...
AttributeError: can...t delete attribute

>>> # as discussed, trying to delete RectsManager attributes
>>> # will fail too, because this tries to delete the same
>>> # attribute in the union rect instead
>>> del g1.rect._get_all_rects # doctest: +ELLIPSIS
Traceback (most recent call last):
...
AttributeError: 'pygame.Rect' ... has no ... '_get_all_rects'

>>> # that is intentional, since it is the same error
>>> # raise when trying this with a regular pygame.Rect
>>> # (and emulate pygame.Rect to a sensible extent is
>>> # the goal of the RectsManager class) as can be seen
>>> # below:
>>> del Rect(5, 5, 5, 5)._get_all_rects # doctest: +ELLIPSIS
Traceback (most recent call last):
...
AttributeError: 'pygame.Rect' ... has no ... '_get_all_rects'


Rich comparison methods (==, !=, <, >, <=, >=)
==============================================

Rich comparison methods work by delegating to the union
rect. This means the pygame.Rect implementation is used.
Such implementation causes the four indices of rects to
be compared just like tuples do with their items, that is,
one by one.

>>> # get group instance
>>> g1, _ = get_fresh_groups()

>>> ### just like tuples, the rich comparison methods compare
>>> ### each item to define the result

>>> ## if all items are equal, the rects are equal too:
>>> g1.rect
<rect(0, -10, 40, 50)>
>>> g1.rect == Rect(0, -10, 40, 50)
True
>>> ## but change one and the result is False
>>> g1.rect == Rect(0, -10, 40, 51) # height is different
False

>>> ## ">" and "<" return the comparison between the first
>>> ## different pair of items:

>>> # the first different item is the 3rd one, which is
>>> # smaller than the 3rd item of our RectsManager
>>> # instance, so the result is True
>>> g1.rect > Rect(0, -10, 39, 50)
True
>>> # here, though the 3rd item is smaller, it is not the
>>> # first different item (this would be the 2nd one);
>>> # since the 2nd item is the first different one,
>>> # it is used for comparison and since it is greater,
>>> # the result of g1.rect > Rect(0, -9, 39, 50) evaluates
>>> # to False
>>> g1.rect > Rect(0, -9, 39, 50)
False

>>> ## if there's no first different items (they are all
>>> ## equal), though, ">" and "<" will naturally return
>>> ## False, and ">=" and "<=" will return True, since
>>> ## equality is also tested

>>> g1.rect > Rect(0, -10, 40, 50)
False
>>> g1.rect < Rect(0, -10, 40, 50)
False

>>> g1.rect >= Rect(0, -10, 40, 50)
True
>>> g1.rect <= Rect(0, -10, 40, 50)
True

>>> ## if there's any different indices, "!=" evaluates to
>>> ## True
>>> g1.rect != Rect(0, -10, 40, 51)
True


Length retrieval (__len__ method)
=================================

As happens with all pygame.Rect instances, len(instance)
returns 4. However, even though the return value is always
4 for rects, we didn't just make the method to return 4.
Instead we return "len(union rect)", that is, we delegate
to the union rect.

We do this because if forces the instance to build the
union rect before returning so that, in the case the
RectsManager has no underlying rects (_get_all_rects
returns no rects), an error is raised to indicate this.
Otherwise the method would return 4 no matter what, even
when the instance has no rects.

>>> # get group instance
>>> g1, _ = get_fresh_groups()

>>> len(g1.rect)
4
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
