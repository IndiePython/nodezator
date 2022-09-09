"""Facility for rectsman package doctests.

>>> ### let's import an useful fixture
>>> from .fixtures import get_fresh_groups


Other topics part 02
********************

This document has both documentation and tests for the
RectsMan class. Here we visit topics which didn't fit
any specific major theme.


Swapping managed rects (overriding _get_all_rects attribute)
============================================================

Though we recommended not overriding any RectsManager
attribute in the "No custom attribute setting (__setattr__
method)" section, in the previous test file, there is
indeed one exception.

As explained in the "Instantiation" section in the first
test file, the _get_all_rects attribute stores a callable
which returns all managed rects. In other words, this
callable is the only link between the RectsManager and
the rects it manages. In this sense, as stated in previous
sections, the RectsManager works just like a proxy.

This means that, whenever you want a RectsManager instance
to manage an entirely different group of rects, the only
thing you need to do is assign another callable to the
_get_all_rects attribute, as long as this callable
returns that group of rects you want the RectsManager
to manage.

This extra flexibility is the reason why it is our purpose
to always leave this attribute overrideable, regardless of
whether we make it so other attributes in the class cannot
be created or reassigned (we discussed this possibility
in the "No custom attribute setting..." section mentioned
at the beginning of this section).

Below we demonstrate this RectsManager "swapping" ability:

>>> # get group instances
>>> g1, g2 = get_fresh_groups()

>>> # see how the different groups of rects occupy
>>> # different areas
>>> g1.rect
<rect(0, -10, 40, 50)>
>>> g2.rect
<rect(90, 0, 60, 40)>

>>> # but once we assign the callable stored in the
>>> # _get_all_rects attribute of the second group to
>>> # the _get_all_rects of the first group, the first
>>> # group is now a manager of those rects too, along
>>> # with the second group:
>>> g1.rect._get_all_rects = g2.rect._get_all_rects

>>> g1.rect
<rect(90, 0, 60, 40)>

>>> # this also means that changes made through the
>>> # RectsManager instance in the first group affect the
>>> # RectsManager instances in the second group; in other
>>> # words, they are like proxies of the same group of
>>> # rects, they manage the same rects now
>>> g1.rect.move_ip(20, 0)
>>> g1.rect
<rect(110, 0, 60, 40)>
>>> g2.rect
<rect(110, 0, 60, 40)>

This can be very useful for game mechanics as well as
manipulating GUI elements.


Nestable
========

Demonstration
-------------

Let's demonstrate something curious. For this we'll need
two freshly instantiated and populated groups:

>>> # get group instances
>>> g1, g2 = get_fresh_groups()

g1 and g2 are instances of a group class which pass a method
to their respective RectsManager instances when they are
created. This method is a generator function which visits
each item and yields its "rect" attribute. This group class
is just like the ListGroup we created in the test file #01.

In other words, the only requirement for the groups to
work is to have items which have a rect in their "rect"
attribute.

Then, what do you think will happen if, instead of another
object, we actually append the second group to the first
one? Let's see this happening!

>>> ### g1.rect without any changes:
>>> g1.rect
<rect(0, -10, 40, 50)>

>>> ### g1.rect after appending g2 to g1:
>>> g1.append(g2)
>>> g1.rect
<rect(0, -10, 150, 50)>

As you can see above, the RectsManager from the group 1
changed its values. This is so because it is now
managing its items plus the RectsManager instance of
the group 2. Why?

Because, as we said earlier, the callable from the
RectsManager isntance of the group 1 visits all of
g1 items and yields their whichever is in their "rect"
attribute, using all of the rects in their calculations.

By why this work, then, if g2.rect isn't a pygame.Rect
instance? Because the RectsManager has a compatible API
with pygame.Rect, so what happens is what is expected
in any OOP application, the RectsManager from g1 just
thinks it is handling a regular pygame.Rect.

In other words, since RectsManager instances were created
to manipulate pygame.Rect instances and they also have an
API compatible with the pygame.Rect's API, RectsManager
instances can also manipulate its own instances, which
also can manipulate other RectsManager instances or
pygame.Rect instances.

Conclusion: RectsManager instances are nestable!

They can be used to create tree structures of any height
with multiple branches, as long as there's always at least
one pygame.Rect instance as a leaf in each branch.

If you have trouble with the tree data structure terminology
used in the previous paragraph, that is, "branch", "height",
"leaf", please read this wikipedia article, or at least take
a look at the "Terminology used in tree" section:
https://en.wikipedia.org/wiki/Tree_(data_structure)


Implications
------------

This has different implications depending on the operations
being performed. Such different implications are inherent
to the specific implementations of each method/operation.

For instance, the move_ip method propagates the call
through all managed rects. This means that using move_ip
on g1.rect will make it so it is used individually in all
its managed rects.

That is, the "move_ip" operation will be applied to each
"rect" of each item in group 1. When the operation reaches
the "rect" from g2, which is now an item of g1, since
g2.rect is a RectsManager instance, it will naturally
execute its g2.rect.move_ip operation, which in turn will
apply the same move_ip operation to each individual rect
managed by g2. In other words, it works like a cascading
effect.

>>> ### check all rects managed in g1.rect (the last one
>>> ### is the RectsManager instance from g2.rect)
>>> for rect in g1.rect._get_all_rects(): print(rect)
<rect(0, 0, 20, 20)>
<rect(10, 10, 20, 20)>
<rect(10, -10, 20, 20)>
<rect(20, 20, 20, 20)>
<rect(90, 0, 60, 40)>
>>> ### these are the rects managed by g2.rect:
>>> for rect in g2.rect._get_all_rects(): print(rect)
<rect(100, 0, 20, 20)>
<rect(110, 10, 20, 20)>
<rect(90, 20, 20, 20)>
<rect(130, 0, 20, 20)>


>>> ### once we move g1.rect, all of them will move together
>>> g1.rect.move_ip(10, 10)

>>> ### managed by g1:
>>> for rect in g1.rect._get_all_rects(): print(rect)
<rect(10, 10, 20, 20)>
<rect(20, 20, 20, 20)>
<rect(20, 0, 20, 20)>
<rect(30, 30, 20, 20)>
<rect(100, 10, 60, 40)>
>>> ### managed by g2:
>>> for rect in g2.rect._get_all_rects(): print(rect)
<rect(110, 10, 20, 20)>
<rect(120, 20, 20, 20)>
<rect(100, 30, 20, 20)>
<rect(140, 10, 20, 20)>

The inflate_ip operation, on the other hand, works
differently. It doesn't propagate the call through
its items. Instead, as we saw in the section explaining
the inflate_ip method in another test file, the inflate_ip
works by moving each individual rect around from or to
the center, in order to shrink or expand in size.

So, calling g1.rect.inflate_ip won't end up calling the
same operation of g2.rect, as would be the case with a
call to g1.rect.move_ip was we just saw.

That is, the rects from g2 will be moved as if they were a
single union rect, ignoring the real distance between
g1.rect.center and the center of each rect managed by
g2.rect.

>>> # let's check the values of g1.rect and g2.rect:
>>> g1.rect
<rect(10, 0, 150, 50)>
>>> g2.rect
<rect(100, 10, 60, 40)>

>>> # and then inflate g1.rect
>>> g1.rect.inflate_ip(40, 40)

>>> # let's again check the values of g1.rect and g2.rect:

>>> # as expected from an inflation with positive values,
>>> # the size increased in g1.rect
>>> g1.rect
<rect(-13, -20, 190, 90)>

>>> # g2.rect didn't change in size, though; this was also
>>> # expected, since, as we just discussed, the "inflate_ip"
>>> # operation from RectsManager doesn't call "inflate_ip" 
>>> # on the underlying rects, just "move_ip", to move them
>>> # around in order to achieve the desired size
>>> g2.rect
<rect(117, 17, 60, 40)>

These differences in how each operation propagates or not
aren't bad nor good. They are just a consequence of the
chosen design. They are useful in some circumstances and
not useful in others. It all depends on your use-cases.

Though we already consider the current implementation of
the RectsManager very useful, powerful and flexible, in the
next section you'll read about how we plan to turn the
RectsManager class even more flexible than it is now.

We plan to make it more flexible while at the same time
keeping it compatible with the pygame.Rect API, retaining
all the current functionality, but offering even more
alternative behaviours for the current methods/operations.


Possible future design
======================

In the future, rather than having an unique implementation
of a RectsManager class, multiple classes should be
assembled from different implementations of the methods.
That is, we plan to be able to have a selection of
RectsManager classes programatically built from a
selection of different behaviours of the operations,
even though they will still keep the same name, signature
and return values.

For instance, the inflate_ip could inflate the rects it
manages instead of just moving them away from or towards
the center to shrink/expand the RectsManager size.

Of course, we don't plan on leaving the users to choose
between multiple implementations helplessly, or even make
them assemble the classes if they don't want to bother with
this.

We will provide default implementations ready to be used
from which they can choose. Only if some specialization
is needed, they may want to assemble their own class.

The purpose is to provide as much variety, versatility and
flexibility as possible while at the same time making the
process of selecting the suitable class as simple as
possible.

The RectsManager itself as it is now will be one of the
default implementations mentioned from which the user
can choose right away and begin working.

Another default implementation could be one which allows
the RectsManager to change the size of the underlying rects.

Collision tests could also have variants which tested each
rect for collisions rather than only the union rect.

Ideally, default implementations would have the most common
use cases, so that users would seldom have to assemble their
own custom classes.

These are just thoughts for the future, though. Without the
proper testing and analysis, we don't know if this will
be a succesful implementation. The only thing we know is
that the alternative behaviours for the methods/operations
are desirable, useful to solve problems that the present
implementation cannot (for instance, the ability to resize
the underlying rects or the collision tests being performed
in the underlying rects).

Regardless of the changes performed or not in the future,
what should remain the same is the fact that the API is
compatible with the pygame.Rect class (that is, same methods
and properties with same signatures and return values).

Question: if you have a more or less clear idea of what
you want, why not implement it right away?

Answer: because of 02 factors. First, I have other tasks
which are of higher priority and it will take time to
finish them. Second, I assume such new behaviours
implemented will bring with them a lot of edge cases and
particularities which will need much testing, study,
analysis and documentation.

For instance, the inflate_ip alternative implementation
which changes the size of the managed rects have some
particularities of which I can think (and these are not
all of them):

- Will the values used with inflate_ip be used in the
  managed rects as well, or will they be applied
  proportionally to the size of each rect?
- If the absolute value is used, them it is not good
  to have rects whose difference in size is too large
  managed by the same RectsManager, right? Otherwise, let's
  say we have a tiny rect and a large rect and the user
  wants to deflate the RectsManager instance: the user will
  have to be careful not to use values greater than the
  size of the tiny rect, right? Otherwise the tiny rect
  may become almost invisible. This is just a few questions
  that pops up when pondering about these implementations.

Therefore, as you can see, these changes will be implemented
only after I finish other higher priority tasks. Then, I'll
be sure to take all the time and diligence needed to
properly implement, test and document the proposed
changes.


Behaviour of rects with negative sizes
======================================

As stated before when explaining/testing the "normalize"
method of the RectsManager class, just because that method
serves to "correct negative sizes", it doesn't mean having
negative dimensions is something inherently bad.

When a rect, either a pygame.Rect or a RectsManager instance
has negative sizes, it behaves differently, because of the
calculations carried internally by the pygame.Rect class.

Such different behaviours are often regarded as "irregular"
and of course they may indeed be incovenient in most cases,
but they can be quite useful in some circumstances.

We didn't test the behaviour of pygame.Rect and RectsManager
instances with negative sizes properly nor comprehensively
enough, but some preliminar experimentations show useful
behaviours displayed by such rects.

We know that some operations like union operations change
significantly when the rect passed as the argument has
negative dimensions.

Let's say, for instance, that we have a normalized
pygame.Rect or RectsManager instance and we use their
union_ip method, giving a rect with both width and height
dimensions containing negative values.

Instead of performing a regular union, what happens is that
our rect instance is "stretched" until it "touches" the rect
with negative sizes. However, this only happens if there's
was no intersection between them prior to the union_ip
operation. If they already intersected before the operation,
then the operation does nothing.

What must be highlighted is: just by giving a rect with
negative sizes, we change the meaning of the "union_ip"
operation completely!

Of course, this doesn't mean we would need to make the
dimensions of the rects permanently negative to achieve
so. Whenever we want to perform such operations, we could
just take the rect we want to which we want to "stretch"
our rect and either copy it and make its dimensions negative
(and change the position accordingly) or just do so in
place in the original rect and then revert it back to the
original values.

As exciting and useful as those new behaviors potentially
are, testing and documenting them properly would need a
lot of time, though.

Besides, those behaviours (at least the few ones we
observed) can be reproduced using the already known and
tested pygame.Rect API, even though sometimes a higher
number of steps would be needed.

For example, we can reproduce the "stretch" effect we
described earlier in a number of ways, by repositioning
and resizing the rect. Being able to perform such operations
in a single step and encapsulating them would still very
useful though. This is why these new behaviours allowed by
negative rects must be properly studied, tested, implemented
and documented.

However, though it is important to test and document those
new possibilities, it is more sensible to postpone such
research for the time being in favour of other tasks with
higher priority. Even more so considering such behaviours
can be more or less achieved by the existing API.

This is why, despite my excitement about these new
possibilities, I'll have to resign myself to pursue
them in a later date.

Observation 01: the behaviour described for the union_ip
method some paragraphs back could become a new "reach"
method, which would receive a rect, temporarily make their
sizes negative and them "stretch" its dimensions until it
touches the given rect.

Observation 02: The step of making a rect negative described
in the previous observation could be encapsulated in its own
method (maybe call it "denormalize", "make_negative" or
something like that). I'm not sure of anything, it all would
need appropriate testing/research, but as explained, it
shall be done. God willing.

Observation 03: while toying a bit with negative rects,
just for curiosity, I also discovered that under some
circumstances the width of the RectsManager might become
0 and cause a ZeroDivisionError in some operations like
union_ip. Unfortunately I can't reproduce that error,
since I was just toying, not testing under controlled
conditions. I recorded the traceback generated and
provided some commentary though, which you can find
in the "observations.txt" file in this directory, in the
section entitled "Negative rects and ZeroDivisionError".


Other New methods
=================

As observed in the "Extra Behaviour" section of the test
file #04_01, the synergy between the RectsManager instances,
pygame.Rect instances and their methods provides us with
a variety of behaviours, sometimes unexpected, which
arise from the different ways the operations can be
combined.

Because of this richness of behaviour, we plan to expand
the class with new methods which provide even more
extra behaviour for other alternative usages of the
RectsManager class beyond the scope of the pygame.Rect
API.

We might begin by encapsulating the behaviours presented
in the "Extra Behaviour" we just mentioned, that is, the
"mirroring" and "centering" of the individual rects. We
will provide partial implementations of such methods, too,
which act in individual axes.

There are also very useful behaviours portrayed in the
"Align and Distribute" panel (invoked by pressing the
ctrl + shift + A keys) of the Inkscape software which
I want to implement in this class.

As a matter of fact, I must consider all these methods
mentioned together when implementing them, so they can be
well integrated, with partial implementations, tests and
documentations and refactorings and so on.

Since this will take a lot of time and is also something
which, though very useful and cool, isn't urgent, I will
postpone such implementation.

Despite my excitement, just like I'm doing with the
redesign (multiple classes) and with the behaviours of
negative rects, I'm having too leave it alone for now.


Other useful usage
==================

Though we designed the RectsManager assuming it would be
used with the rect_property, there's nothing stopping you
from not doing so. In fact, it may be actually very useful
to avoid using the rect_property in some cases.

For instance, let's say you have a class with lots of
rects and you want to manage different rects between them
at each time.

In this case you can create methods that return rects from
each desired group, and then create a different RectsManager
instance using each method, so you can use each instance as
a handle to control their respective group of rects.

Alternatively, you can also create only one RectsManager
instance and switch its _get_all_rects attribute with the
method specific to the group you want to control at each
time. In this case, may or may not use want to use the
rect_property. It's up to you.

Remember: the rect_property exists solely to make it a bit
more difficult to override the RectsManager instance
directly, that is, the property's setter implementation
creates a new RectsManager whenever we try to override
the "rect" attribute with another rect, so that it
guarantees that final object in the "rect" attribute
(which is in fact the property) is always a RectsManager
instance.

Therefore, if your use-cases foresee no overriding taking
place, you may use the RectsManager however you want, with
or without the rect_property.
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
