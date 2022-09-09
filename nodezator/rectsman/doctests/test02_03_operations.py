"""Facility for rectsman package doctests.

RectsManager Rect-like operations part 03
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

>>> ### let's import pygame.Rect and also useful fixtures
>>> from pygame import Rect
>>> from .fixtures import (
... get_fresh_groups, check_error_raising
... )

RectsManager.normalize()
========================

In pygame.Rect, the "normalize" inverts the signal of the
dimensions which are negative (if any). In case any negative
dimension has the signal inverted, it also updates the
topleft coordinates of the rect so that it doesn't move
after having the dimensions' signals swapped.

The RectsManager implementation of the "normalize" method
just executes such method in each underlying rect.

However, just because there's a method to "correct negative
sizes", as pygame.Rect.normalize docstring says, it doesn't
mean having negative dimensions is something inherently bad.

For more information on this, check the section called
"Behaviour of rects with negative sizes", in the test file
#04_02.


RectsManager.contains(*args)
============================

This is a conditional test which tell us whether the rect
defined in the arguments is completely inside the rects
manager boundaries. It returns 1 for True and 0 for False.

>>> # get group instance
>>> g1, _ = get_fresh_groups()

>>> # true because the rect is completely inside
>>> g1.rect.contains((10, 10, 10, 10))
1
>>> g1.rect.contains((30, 30, 20, 20)) # this one isn't
0

Type checking and error raising is also pygame.Rect
compliant:

>>> # for instance, let's use the RectsManager instance
>>> # and the first rect in the group (since it is a
>>> # a pygame.Rect instance) and compare the error
>>> # messages when causing different errors

>>> rects_man, pygame_rect = g1.rect, g1[0].rect
>>> method_names = "contains",
>>> incorrect_args = (
...   (10, 20, 'a_string', 30), # string is an invalid arg
...   (10, 20, 30) # and here we don't have enough args
... )
>>> # as can be seen below, both objects raise the same
>>> # errors when faced with the same problems
>>> check_error_raising(
... rects_man, pygame_rect, method_names, incorrect_args)
True


RectsManager.collidepoint(*args)
================================

This is a conditional test which tell us whether the point
defined in the arguments is inside the rects manager
instance boundaries.

>>> # get group instance
>>> g1, _ = get_fresh_groups()

>>> g1.rect.collidepoint((10, 10))
1
>>> g1.rect.collidepoint((50, 50))
0

Type checking and error raising is also pygame.Rect
compliant:

>>> # for instance, let's use the RectsManager instance
>>> # and the first rect in the group (since it is a
>>> # a pygame.Rect instance) and compare the error
>>> # messages when causing different errors

>>> rects_man, pygame_rect = g1.rect, g1[0].rect
>>> method_names = "collidepoint",
>>> incorrect_args = (
...   ('a_string', 2), # string is an invalid arg
...   (2,) # and here we don't have enough args
... )
>>> # as can be seen below, both objects raise the same
>>> # errors when faced with the same problems
>>> check_error_raising(
... rects_man, pygame_rect, method_names, incorrect_args)
True


RectsManager.colliderect(*args)
===============================

This is a conditional test which tell us whether the rect
defined in the arguments overlaps with the rects manager
instance.

>>> # get group instance
>>> g1, _ = get_fresh_groups()

>>> g1.rect.colliderect((-10, -10, 20, 20))
1
>>> g1.rect.colliderect((50, 50, 20, 20))
0

Type checking and error raising is also pygame.Rect
compliant:

>>> # for instance, let's use the RectsManager instance
>>> # and the first rect in the group (since it is a
>>> # a pygame.Rect instance) and compare the error
>>> # messages when causing different errors

>>> rects_man, pygame_rect = g1.rect, g1[0].rect
>>> method_names = "colliderect",
>>> incorrect_args = (
...   (10, 20, 'a_string', 30), # string is an invalid arg
...   (10, 20, 30) # and here we don't have enough args
... )
>>> # as can be seen below, both objects raise the same
>>> # errors when faced with the same problems
>>> check_error_raising(
... rects_man, pygame_rect, method_names, incorrect_args)
True


RectsManager.collidelist and collidelistall(rects_sequence)
===========================================================

Both methods are conditional tests which test sequence
items for collision with the rects manager instance. The
difference between them is that "collidelist" returns
the index of the first item to collide or -1 if there's
no colliding items while "collidelistall" always return a
list containing all the indices containing colliding items
(which also means the list is returned empty if there's no
such items).

>>> # get group instance
>>> g1, _ = get_fresh_groups()

>>> # let's first define a list of rects, containing five
>>> # rects, two of which collide with the rects manager
>>> # instance
>>> rects_list = [
...   Rect( 50, 50, 20, 20),
...   Rect( 70, 30, 22, 22),
...   Rect(-10, 10, 20, 20), # collides (index == 2)
...   Rect( 42, 42, 12, 12),
...   Rect( 38, 38, 10, 10)  # also collides (index == 4)
... ]

>>> # as expected, the index of the first item to collide
>>> # is returned:
>>> g1.rect.collidelist(rects_list)
2
>>> # the "collidelistall", on the other hand, returns the
>>> # indices of both colliding rects
>>> g1.rect.collidelistall(rects_list)
[2, 4]

Type checking and error raising is also pygame.Rect
compliant:

>>> # for instance, let's use the RectsManager instance
>>> # and the first rect in the group (since it is a
>>> # a pygame.Rect instance) and compare the error
>>> # messages when causing different errors

>>> rects_man, pygame_rect = g1.rect, g1[0].rect
>>> method_names = "collidelist", "collidelistall"
>>> incorrect_args = (
...   [(10, 20, 'a_string', 30)], # string is invalid arg
...   [(10, 20, 30)] # and here we don't have enough args
... )
>>> # as can be seen below, both objects raise the same
>>> # errors when faced with the same problems
>>> check_error_raising(
... rects_man, pygame_rect, method_names, incorrect_args)
True


RectsManager.collidedict and collidedictall(*args)
==================================================

Both methods are conditional tests which test dictionary
elements for collision with the rects manager instance.
Such elements can be either the keys or the values of
the dictionary.

Whether keys or values are used depends on the whether you
omit or pass a second optional argument to the method and
also the value of such argument. Such value must be a
boolean or integer indicating True or False.

If you pass a false value or omit the argument, the keys
are used for collision testing. If you pass a true value
though, the values of the dictionary are used instead.
The first argument is, naturally, the dict.

The difference between "collidedict" and "collidedictall"
is that "collidedict" returns the (key, value) pair of the
first item to collide or None if there's no colliding items
while "collidedictall" always return a list containing the
(key, value) pairs of all the colliding items (which also
means the list is returned empty if there's no such items).

>>> # get group instance
>>> g1, _ = get_fresh_groups()

>>> # let's use the rect sequence created in the previous
>>> # tests to define a new dictionary using indices
>>> # as keys, one for each rect in the sequence
>>> rects_dict = dict(zip(range(5), rects_list))

>>> # we'll start by testing collidedict, using the values
>>> # for collision testings (thus using a true boolean or
>>> # integer as the second argument; also remember that
>>> # even though in recent versions of Python the dict
>>> # items keep insertion order, it is an implementation
>>> # detail, rather than a feature per se, so in theory
>>> # we shouldn't rely on it;
>>> item = g1.rect.collidedict(rects_dict, True)

>>> # as expected, item is the (key, value) pair of one
>>> # of the colliding rects (we can't tell for sure
>>> # since, as explained in the previous comment, we can't
>>> # guarantee the order)
>>> item == (2, rects_dict[2]) or item == (4, rects_dict[4])
True

>>> # the "collidedictall" on the other hand, returns a list
>>> # with all the (key, value) pairs (we'll use the values
>>> # for collision testing again)
>>> colliding_pairs = g1.rect.collidedictall(rects_dict, True)

>>> # since we can't predict the order, we'll sort the
>>> # colliding_pairs before checking whether it has the
>>> # expected values
>>> sorted_result = sorted(colliding_pairs)
>>> sorted_expected = [
...   (2, rects_dict[2]),
...   (4, rects_dict[4])
... ]
>>> sorted_result == sorted_expected
True

>>> # we can also use the keys for collision testing in
>>> # both methos, but dictionaries only accept hashable
>>> # objects as keys, which means we can't use pygame.Rect;
>>> # this means we'll for instance, need to turn our rects
>>> # into tuples when inverting the (key, value) pairs in
>>> # the dict; here we'll create a new dict to demonstrate:
>>> new_dict = {
...    tuple(value): key
...    for key, value in rects_dict.items()
... }
>>> # we can now use the keys for collision testing by
>>> # omitting the second argument or passing a false
>>> # bool or integer; the results will be the same;
>>> item = g1.rect.collidedict(new_dict) # omitting 2nd arg

>>> # the value of the (key, value) pair is either, 2 or 4
>>> # as expect (they are the original keys in "rects_dict")
>>> item[1] == 2 or item[1] == 4
True

>>> # now let's test "collidedictall" (this time instead of
>>> # omitting, we pass False; the effect is the same: keys
>>> # are used for collision testing)
>>> colliding_pairs = g1.rect.collidedictall(new_dict, False)

>>> # as expect, the (key, value) pairs returned are those
>>> # whose sorted values are 2 and 4:
>>> values = (pair[1] for pair in colliding_pairs)
>>> sorted(values) == [2, 4]
True

As a developer, I think it would make more sense for the
default behaviour of the second argument (when omitted)
to cause the values of the dictionary to be used for
collision testing. This is because, since rects are
unhashable, it is only natural to expect to find them as
values in dictionaries, not as keys.

Also, by turning them into tuples, though the collision
testing works fine, we lose all the convenient behaviour
of the pygame.Rect class.

This is why I think it's often better to store rects in
dictionaries as values, thereby using those dict-related
collision methods with the second argument set to True.

There might be, however, use-cases where storing rects in
dict keys as tuples is useful. Even though I can't think of
any. As a software designer, I just deduced the default
behaviour should favour the assumption that rects would
primarily be stored as values.

Of course, to be fair, such assumptions would have to be
compared with the userbase assumptions and daily usage of
such methods first, so it is not as if I'm assuming I have
the right answers regarding this matter. These are just my
thoughts for you to consider as you please.

Type checking and error raising is also pygame.Rect
compliant:

>>> # for instance, let's use the RectsManager instance
>>> # and the first rect in the group (since it is a
>>> # a pygame.Rect instance) and compare the error
>>> # messages when causing different errors

>>> # testing collidedict:

>>> rects_man, pygame_rect = g1.rect, g1[0].rect
>>> method_names = "collidedict",
>>> incorrect_args = (
...   {(10, 20, 'a_string', 30): 1}, # string is invalid arg
...   {(10, 20, 30): 1} # and here we don't have enough args
... )
>>> # as can be seen below, both objects raise the same
>>> # errors when faced with the same problems
>>> check_error_raising(
... rects_man, pygame_rect, method_names, incorrect_args)
True

>>> # testing collidedictall:

>>> rects_man, pygame_rect = g1.rect, g1[0].rect
>>> method_names = "collidedictall",
>>> incorrect_args = (
...   {(10, 20, 'a_string', 30): 1}, # string is invalid arg
...   {(10, 20, 30): 1} # and here we don't have enough args
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
