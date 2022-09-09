"""Facility for rectsman package doctests.

RectsManager Introduction
*************************

This document is the first in a series of documents
containing documentation and tests for the RectsManager
class. Here we introduce the class' purpose, alternative
usage and other introductory topics.


Main goal and alternative usage
===============================

The rectsman package provide two important objects used to
make any instance containing multiple rects to behave as if
it had a single rect.

The first object is a property called "rect_property". It has
a getter and setter implementation and was created to be
injected in custom classes' in their "rect" class attribute
so that it acts as the "rect" property of the class'
instances.

Its sole purpose is to prevent direct access to the
instance of the RectsManager class which we present next.
Though we use the rect_property in the classes used for
testing in all the test files, its usage is not strictly
mandatory, as we discuss far ahead in the test file #04_02.

The second object is a class named RectsManager whose
purpose is to manipulate multiple pygame.Rect instances
at once. Its API is compatible with the pygame.Rect API
found in the online docs (except for the constructor, the
__init__ method, which has a different signature). This
means instances of this class can be manipulated just like
pygame.Rect instances.

Because such class has the same basic pygame.Rect API and
it can manipulate pygame.Rect instances, it can also, as
a result, manipulate instances of its own class, allowing
the creation of nested structures.

When creating this class, we wanted to be able to use code
such as the following:

>>> # the tests below are skipped on purpose, since we
>>> # didn't create the objects, we just mean to illustrate
>>> # the code we want to write using the RectsManager class

>>> # a group with many objects (objects which have rects
>>> # in their 'rect' attributes; for instance: sprites)
>>> group = Group() # doctest: +SKIP

>>> # this would move all rects the group contains
>>> # (group.rect is the getter implementation of
>>> # the "rect" property mentioned earlier
>>> # and it returns the RectsManager instance)
>>> group.rect.move_ip(10, 0) # doctest: +SKIP

>>> # and this would cause the collections of objects
>>> # to be centered around the specified point while
>>> # keeping their relative positions from each other
>>> group.rect.center = (30, 40) # doctest: +SKIP

In other words, the idea is to operate all rects at once
by interacting only with the "rect" property in the custom
classes' instances. Such property is used to return an
instance of the RectsManager class, which, as the name
implies, represents all the rects in the custom class.

The class indeed practically doesn't have state in itself,
since it just reads and performs operations using the
rects it manages. In this regard, it acts just like a
proxy.

The RectsManager represents the collection of rects as a
whole, that is, as if they were all a union rect of all
the rects.

This means, for instance, that "group.rect.x = 10"
illustrated above would not make each individual rect to
have their "x" coordinate changed to 10, but that all the
rects would be moved as if they were inside a large union
rect which had 10 assigned to its "x" coordinate.

Of course some operations make more sense when we consider
each individual rect rather than the union rect of them,
as we will see in tests farther ahead in the following
file.

A lot of times however the rects will be handled as a
union rect. Each of those cases will be explained as they
are presented. For now let's dive into the purpose behind
the RectsManager class creation.

The RectsManager was created with the purpose of moving and
aligning groups of rects to specific coordinates, specially
to move UI elements around. The RectsManager wasn't even
created to handle size transformations like pygame.Rect
does.

However, once we realized how handy such class is and
that it could be used in a lot of use cases, even gameplay
not related to UIs, we decided to make its API fully
compatible with the pygame.Rect API shown in the online
docs, thereby implementing size transformation as well.
Therefore, code like shown below is now possible, too:

>>> # again, since this is just a demosntration, we
>>> # skip the tests
>>> obj.rect.width = 50          # doctest: +SKIP
>>> obj.rect.width += 50         # doctest: +SKIP
>>> obj.rect.inflate_ip(40, 40)  # doctest: +SKIP


Size transformations
--------------------

Size transformations don't change the size of the managed
rects, though. In our implementation, it just changes their
position relative to the center of the virtual union rect
of them all.

In other words, positive size transformations move the rects
farther from the center while negative size transformations
move them closer. Because of that, some innacuracies occur
sometimes. We discuss this in a section further ahead
called "Size transformation innacuracies".


Other methods and behaviour/error handling specifics
----------------------------------------------------

Also, whenever we say compatible with pygame.Rect API
online docs, we mean it has the methods listed there
(except for the __init__ method).

Other methods not listed there were provided as well, with
custom implementations, like the rich comparison methods,
that is, the ones which implement the behaviour of
"==", "!=", "<", "<=", ">" and ">=".

Though we wanted the API to be fully compatible, that is,
the same methods with same interface (same parameters and
same return values), it wasn't our specific goal to aim
for full compatibility of behavior. Here it is important
to distinguish between API and behaviour. While by API we
mean the method names, signatures and return values, by
behaviour we mean how they work in particular.

Thus, it was not our goal to always emulate the behaviour
exactly, since in the end the RectsManager is indeed another
class altogether and making it emulate all the pygame.Rect
behaviour could cause confusion and even be harmful in some
aspects.

We'll give you an example: as will be discussed in a section
far ahead, in another test file, the RectsManager class
doesn't raise errors when new attributes are assigned to it,
as a pygame.Rect instance would naturlly do. This is so
because the extra conditional checks needed in the
RectsManager class would slow down its performance.

There are also some other circumstances where the errors
raised are not exactly the same as the ones raised by
pygame.Rect when facing the same problems and this is
so because in such circumstances, fully emulating the
pygame.Rect behaviour would require extra checks/steps
which would slow the operation, even if slightly so.

In other words, our main concern is to make the operations
work, not whether the error raising behaviour is exactly
the same or not.

Furthermore, we also want to add more methods beyond those
of the pygame.Rect API, to make the class even more
versatile, while at the same time keeping its full
pygame.Rect API compatibility. There are not many of
such methods, but they are being gradually added as
they are needed and the ideas behind them are perfected.

From now on we will present examples of how the rect
property and RectsManager class are meant to be used. But
let's first import them here, along with the pygame.Rect
class, which will help us demonstrate some concepts.

>>> from pygame import Rect # doctest: +ELLIPSIS
pygame 2...
Hello from the pygame community...

>>> from ..main import RectsManager, rect_property


Instantiation
=============

Now, as a first example, let's create a group class which
is helped by the RectsManager class and the related
property called "rect_property", a property with a getter
and setter implementation:

>>> class ListGroup(list):
...     
...     def __init__(self, *args):
...         
...         super().__init__(*args)
...     
...         # note that here the RectsManager class is
...         # instantiated along with the group class
...         # and it receives a callable as the sole
...         # argument; it is stored in a _rects_man
...         # attribute, to indicate it shouldn't be
...         # handled directly
...         self._rects_man = RectsManager(
...                                    self.get_all_rects)
...     
...     # here we "inject" (assign) the rect_property in
...     # the "rect" class attribute of this custom class;
...     # from now on, accessing "rect" or assiging a value
...     # to it in the RectsManager instances will call
...     # its getter or setter behaviour, respectively
...     rect = rect_property
...     
...     # the callable received by a RectsManager can be
...     # any callable which when called returns all the
...     # rects RectsManager is supposed to manage; since
...     # a group is dynamic and its contents may change,
...     # we used this method, which is a generator
...     # function which goes over all the objects in the
...     # group, yielding each rect, every time it is
...     # called and iterated;
...     def get_all_rects(self):
...         for obj in self: yield obj.rect


That is, any class using the RectsManager, will work fine
as long as its instances have a RectsManager stored in
their "_rects_man" attribute. Such RectsManager, upon
instantiation, must receive a callable which returns the
rects it manages.

Though we use a method from the custom class itself, the
callable can really be from anywhere, as long as it returns
the rects needed. The rect_property must also be assigned
to the "rect" attribute of the class.

For instance, let's say I wanted to make a dict subclass
which stored objects in its values and such objects had
pygame.Rect instances:

>>> class DictGroup(dict):
...     
...     def __init__(self, *args, **kwargs):
...         
...         super().__init__(*args, **kwargs)
...     
...         # instantiating and storing the RectsManager
...         self._rects_man = RectsManager(
...                                     self.get_all_rects)
...     
...     rect = rect_property  # we inject the property
...     
...     def get_all_rects(self):
...         for obj in self.values(): yield obj.rect

As you can see above, we pass the get_all_rects method
from the instance of DictGroup when we create. Such
callable, as can be seen, returns all rects from the
objects in the values of the dictionary (the view
returned from dict.values() method).


Representation (__repr__ method)
================================

Since the RectsManager class is meant to emulate the
behaviour of pygame.Rect, the representation of the
RectsManager class is the same adopted by pygame.Rect.

We'll use the ListGroup class defined early and the
SimpleObject class defined below to demonstrate the
RectsManager representation

>>> # define a class of simple objects which can be
>>> # appended to ListGroup class instances and holds
>>> # a pygame.Rect in its "rect" attribute
>>> class SimpleObject:
...    def __init__(self, rect):
...        self.rect = rect

>>> # let's instantiate a list group and append objects
>>> group = ListGroup()
>>> group.append(SimpleObject(Rect(0, 0, 20, 20)))
>>> group.append(SimpleObject(Rect(20, 20, 20, 40)))

>>> # let's compare the representations of the
>>> # pygame.Rect instance from the first object and
>>> # the RectsManager instance:

>>> group[0].rect # representation of rect of first object
<rect(0, 0, 20, 20)>
>>> group.rect    # representation of RectsManager instance 
<rect(0, 0, 40, 60)>


RectsManager instance on _rects_man attribute
============================================

We recommend to instantiate the RectsManager in the body
of the __init__ method of your custom class as just shown
in the previous examples. However, if you want, you can do
it after too.

It'll all work fine as long as, before accessing the "rect"
attribute of your custom group instance, you make sure
there's a RectsManager instance stored on the "_rects_man"
attribute of your class instance.

Otherwise, the property tries accessing the "_rects_man"
attribute of your group instance (the attribute which must
always be used to store the RectsManager instance) and
raises an AttributeError, since it doesn't exist.

See:

>>> # below we define a new group class which inherits
>>> # from the built-in class set

>>> class SetGroup(set):
...    def __init__(self, *args):
...        super().__init__(*args)
...    
...    rect = rect_property  # we inject the property
...     
...    def get_all_rects(self):
...        for obj in self: yield obj.rect

>>> # instantiating group and adding some objects to it
>>> set_group = SetGroup()
>>> set_group.add(SimpleObject(Rect( 0,  0,  5,  5)))
>>> set_group.add(SimpleObject(Rect(10, 20, 30, 40)))

>>> set_group.rect # doctest: +ELLIPSIS
Traceback (most recent call last):
...
AttributeError: \'SetGroup\' ... has no attr... '_rects_man'

You can solve this by simply instantiating a RectsManager
(with a callable which returns rects to it) and
attaching it to the _rects_man attribute of the group
instance. The AttributeError will then be gone:

>>> rects_manager = RectsManager(set_group.get_all_rects)
>>> set_group._rects_man = rects_manager

>>> # this works fine; here we access the rects manager
>>> # instance from the "rect" property;
>>> set_group.rect
<rect(0, 0, 40, 60)>

Finally, a last requirement for the RectsManager instance
to work fine is discussed in the following section: It is
required that the callable passed to the RectsManager
return at least one rect when called, that is, when
group.rect is accessed. Read the next section to now why.


Empty Instances: when the RectsManager receives no rects
========================================================

The RectsManager instance will also raise an error if,
when accessed, the callable stored in its '_get_all_rects'
attribute returns no rects. This callable is the one passed
to the RectsManager on instantiation.

This errors occurs because the RectsManager instances
represent 2d spatial information (position and dimensions)
of a collection of rects, so it needs to receive at least
one rect. Without rects the manager has no sensible way to
convey any spatial information.

As of now, we also couldn't think of any alternative
way to represent such lack of spatial information.
For instance, the pygame.Rect class, in its "clip" method,
returns a rects of size 0 when an invalid operation is
performed, but this is only possible because the rect
already exists and has position information which is used
in the rect created.

If we, on the other hand, were to return a rect of size 0,
which position would we use? We could use (0, 0), but this
value is misleading because (0, 0) is just another regular
position, not an indicator of a lack of anything, like
empty lists would be, for instance. The consequences of
using (0, 0) would make no sense.

Imagine this: positioning another group above our empty
group would make the other group appear above the (0, 0)
coordinates. That is, even though our group has no position
information, it would move the other group above the
coordinates origin. Why though? It makes no sense, since our
group is empty. It simply has no position nor dimensions,
because it has no objects.

That's why the RectsManager instance must only be accessed
when there are rects to be returned by the 'get_all_rects'
callable, rects which it can use to calculate its position
and dimensions. One rect is enough. Whenever there's no
rects we recommend properly dealing with the error raised
or avoiding accessing the "rect" property altogether.

Here, let's see the error raised:

>>> # here we'll create a group, but since we don't append
>>> # any objects, the callable in the _get_all_rects
>>> # attribute of the RectsManager instance won't return
>>> # any rects, because it get rects from appended objects
>>> group = ListGroup()
>>> group.rect
Traceback (most recent call last):
...
RuntimeError: '_get_all_rects' callable returns no rects

>>> # once the callable returns at least one rect, the
>>> # RectsManager can do its job, so it works properly,
>>> # raising no errors
>>> group.append(SimpleObject(Rect(0,  0,  10,  10)))
>>> group.rect
<rect(0, 0, 10, 10)>

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
