"""Facility with class providing rect-like behaviour.

This module provides two important objects used to make
any instance containing multiple rects to behave as if it
had a single rect.

The first object is a property with a getter and setter
to be injected in custom classes as the "rect" attribute.

The second object is a class whose purpose is to manipulate
multiple pygame.Rect instances at once."""


### standard-library imports

from contextlib import contextmanager

from functools import partialmethod


### third-party import
from pygame import Rect


### local imports (class extensions)

from .special import SpecialMethods
from .spatial import SpatialProperties
from .sizepos import SizePositionMethods
from .singlepos import PositionSingleRectsMethods

from .cluster import get_clusters


### "rect" property definition (getter and setter)


@property
def rect_property(self):
    """Return the rects manager obj."""
    return self._rects_man


@rect_property.setter
def rect_property(self, rect):
    """Create new RectsManager from pygame.Rect.

    Parameters
    ==========

    rect (pygame.Rect instance)
        rect from which to read the size and topleft
        coordinates for the new RectsManager instance.
    """
    ### copy the rects manager and store its copy in the
    ### same attribute
    self._rects_man = RectsManager(self._rects_man._get_all_rects)

    ### transfer topleft and size values of the received
    ### rect to the copy

    self._rects_man.size = rect.size
    self._rects_man.topleft = rect.topleft


### RectsManager class definition


class RectsManager(
    SpecialMethods,
    SizePositionMethods,
    SpatialProperties,
    PositionSingleRectsMethods,
):
    """Controls multiple pygame.Rect instances.

    This class has the same basic API of pygame.Rect found
    in the online docs (except for the constructor, the
    __init__ method), which means instances of this class
    can be manipulated just like pygame.Rect instances.

    Additionally, since this class has the same basic
    pygame.Rect API and it can manipulate pygame.Rect
    instances, it can also manipulate instances of itself,
    nested or not.

    Check the "doctests" directory to find extensive
    documentation and doctests regarding the usage of
    this class.

    Such documentation also has a discussion regarding a
    future/possible redesign, which keeps the pygame.Rect
    API compatibility but has even more flexible behaviour
    and also new ones beyond the pygame.Rect API.

    For now, there is only two methods provided which are
    beyond the pygame.Rect API, which is the '__iter__'
    method from the 'special.py' module (even though the
    pygame.Rect is compatible with iteration in Python
    via its __getitem__ method) and the 'snap_rects'
    method from the 'align.py' module.
    """

    ### making instances unhashable
    __hash__ = None

    ### mapping indices to corresponding properties to use
    ### in item assignement (__setitem__ method)

    _index_to_property = {
        0: "left",
        1: "top",
        2: "width",
        3: "height",
        -4: "left",
        -3: "top",
        -2: "width",
        -1: "height",
    }

    ### define sample rect for emulating pygame.Rect
    ### type checking, type coercion and error raising
    _sample_rect = Rect(0, 0, 0, 0)

    ### inject function to work as a method
    get_clusters = get_clusters

    def __init__(self, get_all_rects):
        """Store callable used to get all rect instances."""
        ### store the callable to get all rects
        self._get_all_rects = get_all_rects

    ### TODO refactor method below
    @classmethod
    def from_iterable(cls, iterable):
        return cls(iterable.__iter__)

    ### special property

    @property
    def union_rect(self):
        """Return union of all rects."""
        ### separate first rect and remaining rects
        try:
            first_rect, *remaining_rects = self._get_all_rects()

        ### if a value error occurs (when self.get_all_rects
        ### returns no rects), raise a RuntimeError from it
        ### with a custom message

        except ValueError as err:

            msg = "'_get_all_rects' callable returns no rects"

            raise RuntimeError(msg) from err

        ### if everything goes ok, though, just return
        ### the union of all rects
        return first_rect.unionall(remaining_rects)

    ### special context manager

    @contextmanager
    def keep_rects_attrs(self, *attr_names):
        """Restore initial size/pos of rects when resuming."""
        ### map rect ids to the values of the attributes
        ### named

        backup = {
            id(rect): tuple(getattr(rect, name) for name in attr_names)
            for rect in self._get_all_rects()
        }

        ### suspend execution by yielding;
        ###
        ### exceptions occurring in this step are
        ### purposefully not caught;
        yield

        ### restore size and position of rects

        for rect in self._get_all_rects():

            for name, value in zip(attr_names, backup[id(rect)]):
                setattr(rect, name, value)

    ### some pygame.Rect API methods

    def copy(self):
        """Return a union rect.

        The union rect per se already works as a "copy"
        since it has the correct rect values representing
        the RectsManager position and dimensions:
        (left, top, width, height).
        """
        return self.union_rect

    ## aliasing copy to __copy__, which pygame.Rect also
    ## implements; __copy__ is the behaviour used by the
    ## standard library function copy.copy
    __copy__ = copy

    def normalize(self):
        """Normalize all rects.

        Normalizing is described in the online docs as
        an operation that "corrects negative sizes".

        This is so because rects with negative dimensions
        present irregular behaviour which seems to be
        regarded as an incovenience.

        We'd just like to add that such irregular behaviour
        might in fact be useful in some cases. We can't
        tell for sure since we didn't test and document
        such behaviours, though, but you can found a brief
        discussion about such behaviours in the extensive
        documentation referenced in this class' docstring.
        """
        for rect in self._get_all_rects():
            rect.normalize()

    ## conditional tests

    def contains(self, *args):
        """Return whether a rect is inside our union rect.

        *args is usually a single pygame.Rect instance or
        integers representing such instance (either
        isolated or in a sequence like a tuple or list).
        """
        return self.union_rect.contains(*args)

    ## collision tests

    def collidepoint(self, *args):
        """Return whether a point is inside our union rect.

        A point along the right or bottom edge is not
        considered to be inside the rect.

        *args is usually a pair of integers either given
        as separate arguments or together in a sequence
        like a tuple, list or pygame.math.Vector2.
        Such integers may be negative as well and they
        represent the point in question.
        """
        return self.union_rect.collidepoint(*args)

    def colliderect(self, *args):
        """Return whether a rect overlaps our union rect.

        Having top + bottom and/or left + right aligned
        isn't considered overlapping.

        *args is usually a single pygame.Rect instance or
        integers representing such instance (either
        isolated or in a sequence like a tuple or list).
        """
        return self.union_rect.colliderect(*args)

    def collidelist(self, *args):
        """Return index of overlapping rect from sequence.

        *args is a sequence of rects or other objects
        representing rects.

        You may use a sequence like a list or tuple. The
        items don't need to be pygame.Rect instances, they
        may be sequences of integers representing rect
        instances.

        We test whether this rectsmanager union rect
        overlaps with any rect from a given sequence.
        The index of the first collision found is returned.
        If no collisions are found, -1 is returned.
        """
        return self.union_rect.collidelist(*args)

    def collidelistall(self, *args):
        """Return indices of overlapping rects from sequence.

        *args is a sequence of rects or other objects
        representing rects.

        You may use a sequence like a list or tuple. The
        items don't need to be pygame.Rect instances, they
        may be sequences of integers representing rect
        instances.

        Returns a list with indices of the rects that
        collide with our union rect. If no intersecting rects
        are found, an empty list is returned.
        """
        return self.union_rect.collidelistall(*args)

    def collidedict(self, *args):
        """Return (key, value) of 1st colliding dict element.

        Or None, if no element collides.

        The "elements" mentioned are either the keys or
        the values of the dictionary.

        This method can receive one or two arguments. The
        first argument is required. It is a dict containing
        the elements to be tested for collision. The second
        argument is optional and must be a boolean or integer
        indicating True or False.

        Passing False or omitting the argument altogether,
        makes it so the keys in the dict are used for
        collision testing (they'll probably be tuples, since
        keys in dictionaries must be hashable, which lists
        and pygame.Rect instances are not, they can only be
        used as values).

        If you pass True instead, the opposite happens, that
        is, the values of the dict are used for collision
        testing.
        """
        return self.union_rect.collidedict(*args)

    def collidedictall(self, *args):
        """Return list w/ dict items whose value collides.

        If no value collides, the returned list is empty.

        The "elements" mentioned are either the keys or
        the values of the dictionary.

        This method can receive one or two arguments. The
        first argument is required. It is a dict containing
        the elements to be tested for collision. The second
        argument is optional and must be a boolean or integer
        indicating True or False.

        Passing False or omitting the argument altogether,
        makes it so the keys in the dict are used for
        collision testing (they'll probably be tuples, since
        keys in dictionaries must be hashable, which lists
        and pygame.Rect instances are not, they can only be
        used as values).

        If you pass True instead, the opposite happens, that
        is, the values of the dict are used for collision
        testing.
        """
        return self.union_rect.collidedictall(*args)

    ### extra non-destructive operations

    def union_from_temporary_operation(self, in_place_method_name, *args, **kwargs):
        """Return union rect as if rects were changed.

        That is, as if an "in place" operation were
        performed permanently.
        """
        ### while keeping original position and size of
        ### each rect...

        with self.keep_rects_attrs("topleft", "size"):

            ### execute 'in place' method

            getattr(self, in_place_method_name)(*args, **kwargs)

            ### return union rect of rects
            return self.union_rect

    snap_rects = partialmethod(union_from_temporary_operation, "snap_rects_ip")

    snap_rects_intermittently = partialmethod(
        union_from_temporary_operation, "snap_rects_intermittently_ip"
    )

    lay_rects_like_table = partialmethod(
        union_from_temporary_operation, "lay_rects_like_table_ip"
    )

    snap_rects_to_points = partialmethod(
        union_from_temporary_operation, "snap_rects_to_points_ip"
    )
