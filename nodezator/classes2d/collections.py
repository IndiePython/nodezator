"""Facility w/ custom collections for general usage."""

### standard library import
from functools import partialmethod


### third-party import
from pygame.math import Vector2


### local imports

from ..pygameconstants import (
    blit_on_screen,
    SCREEN_RECT,
)

from ..rectsman.main import (
    rect_property,
    RectsManager,
)


### main collection base class


class Collection2D:
    """Mixin class for custom 2D-handling collections.

    Can be used in any class with an  __iter__ method.
    Whether such method was inherited, overridden or
    extended is not relevant.
    """

    ### initializing method

    def __init__(self, *args, **kwargs):
        """Initialize superclass, create RectsManager."""
        super().__init__(*args, **kwargs)
        self._rects_man = RectsManager(self.get_all_rects)

    ### methods related to collision

    def get_on_screen(self):
        """Return iterator with all objects on screen.

        Objects on screen are those which collide with it.
        """
        return (obj for obj in self if SCREEN_RECT.colliderect(obj.rect))

    def get_colliding(self, rect):
        """Return iterator of objects colliding w/ rect.

        rect (instance of pygame.Rect)
        """
        return (obj for obj in self if rect.colliderect(obj.rect))

    def get_contained(self, rect):
        """Return iterator of objects contained in given rect.

        rect (instance of pygame.Rect)
        """
        return (obj for obj in self if rect.contains(obj.rect))

    ### clustering method

    def get_clusters(self, *inflation):
        """Return clusters formed by close objects.

        Parameters
        ==========
        inflation (two integers or iterable containing them)
            amount of size to inflate each object's rect
            in order to check by collision whether they
            are close enough to be considered in the same
            cluster.
        """
        ### define map associating the id of a rect to the
        ### object to which it belongs

        rect_id_to_obj = {id(obj.rect): obj for obj in self}

        ### for each cluster yielded (list of rects), yield
        ### a new list containing the objects associated with
        ### the rects in the cluster

        for cluster in self.rect.get_clusters(*inflation):

            yield [rect_id_to_obj[id(rect)] for rect in cluster]

    ## method to update

    def call_update(self):
        """Call the update method on all objects.

        The function is called 'call_update' because using
        'update' instead would cause name clashes with
        methods from some built-in classes like set.
        """
        for obj in self:
            obj.update()

    ## mouse related methods

    def mouse_method_on_collision(self, method_name, event):
        """Invoke inner widget if it collides with mouse.

        Parameters
        ==========

        method_name (string)
            name of method to be called on the colliding
            widget.
        event (event object of MOUSEBUTTON[...] type)
            it is required in order to comply with
            mouse interaction protocol used; here we
            use it to retrieve the position of the
            mouse when the first button was released.

            Check pygame.event module documentation on
            pygame website for more info about this event
            object.
        """
        ### retrieve position from attribute in event obj
        mouse_pos = event.pos

        ### search for a colliding obj

        for obj in self:

            if obj.rect.collidepoint(mouse_pos):

                colliding_obj = obj
                break

        else:
            return

        ### if you manage to find a colliding obj, execute
        ### the requested method on it, passing along the
        ### received event, if it has such method

        try:
            method = getattr(colliding_obj, method_name)
        except AttributeError:
            pass
        else:
            method(event)

    on_mouse_click = partialmethod(
        mouse_method_on_collision,
        "on_mouse_click",
    )

    on_right_mouse_release = partialmethod(
        mouse_method_on_collision,
        "on_right_mouse_release",
    )

    on_mouse_release = partialmethod(
        mouse_method_on_collision,
        "on_mouse_release",
    )

    ## methods related to drawing

    def draw(self):
        """Blit obj.image at obj.rect coordinates.

        Naturally, it should only be used if objects have
        both an image attribute containing a pygame.Surface
        instance and a rect attribute containing a
        pygame.Rect instance.
        """
        for obj in self:
            blit_on_screen(obj.image, obj.rect)

    def draw_on_screen(self):
        """Like self.draw, but check if obj is onscreen.

        Naturally, it should only be used if objects have
        both an image attribute containing a pygame.Surface
        instance and a rect attribute containing a
        pygame.Rect instance.
        """
        for obj in self.get_on_screen():
            blit_on_screen(obj.image, obj.rect)

    def draw_on_surf(self, surf):
        """Work as self.draw, but blit on specified surf.

        surf
            Any pygame.Surface instance. If such instance
            is also the surface returned by
            pygame.display.set_mode then it is recommended
            to use the self.draw or self.draw_on_screen
            method instead.
        """
        for obj in self:
            surf.blit(obj.image, obj.rect)

    def draw_contained(self, rect):
        """Draw obj on screen if contained in rect.

        rect
            Any instance of pygame.Rect.
        """
        for obj in self:
            if rect.contains(obj.rect):
                blit_on_screen(obj.image, obj.rect)

    def draw_colliding(self, rect):
        """Draw obj on screen if collides with given rect.
        rect
            Any instance of pygame.Rect
        """
        for obj in self:
            if rect.colliderect(obj.rect):
                blit_on_screen(obj.image, obj.rect)

    def draw_relative(self, obj):
        """Draw objects relative to position of given one."""
        negative_topleft = -Vector2(obj.rect.topleft)

        for current_obj in self:

            obj.image.blit(current_obj.image, current_obj.rect.move(negative_topleft))

    def call_draw(self):
        """Call the draw method on all objects."""
        for obj in self:
            obj.draw()

    def call_draw_on_screen(self):
        """Call draw method of all objects on screen."""
        for obj in self.get_on_screen():
            obj.draw()

    ## property and method to complement the usage of the
    ## RectsManager class from the rectsman subpackage

    rect = rect_property

    def get_all_rects(self):
        """Yield rect of each object."""
        for obj in self:
            yield obj.rect


### definition of custom collections

## classes' definitions


class Set2D(Collection2D, set):
    """Set object w/ 2D handling capabilities."""


class List2D(Collection2D, list):
    """List object w/ 2D handling capabilities.

    About slicing
    =============

    Normally we would extend list.__getitem__ so it
    returned slices of List2D type when sliced;

    However, we purposefully don't do so in order to
    avoid the extra checks needed for this, which would
    slow down the __getitem__ operation,  which may be
    used a lot in some cases;

    Doing this is even more desirable when we realize
    that slicing is usually much less performed and,
    whenever needed, explicitly converting the resulting
    slice is pretty straightforward;
    """


class Iterable2D(Collection2D):
    """General iterable object w/ 2D handling capabilities.

    Iteration is performed using the given callable.

    This class is useful for providing extra functionality
    for groups of objects returned by a callable. The
    objects returned by the callable are expected to
    have a pygame.Surface in their 'image' attribute and
    a pygame.Rect or equivalent in their 'rect' attribute.

    For instance, you could pass the dict.values().__iter__
    bound method of a dict instance, to iterate over the
    values of a dictionary (if such objects fit the
    criteria explained above).

    You could also provide your own generator function
    for custom iteration over arbitrary groups of objects,
    which makes this class even more versatile.
    """

    def __init__(self, callable_obj):
        """Store callable object and create RectsManager.

        The callable obj is an object which, once called,
        returns objects with a pygame.Surface object in its
        'image' attribute and a pygame.Rect obj or
        equivalent in its 'rect' attribute, probably in
        the form of an iterator.
        """
        self.callable_obj = callable_obj
        self._rects_man = RectsManager(self.get_all_rects)

    def __iter__(self):
        """Return the return value of callable_obj.

        Check the __init__ method's docstring for additional
        info about this callable.
        """
        return self.callable_obj()

    def __len__(self):
        """Return length.

        Works by counting how many iterations it takes
        to finish iteration.
        """
        ### start a count variable
        count = 0

        ### increment the count as you iterate
        for _ in self.callable_obj():
            count += 1

        ### return the count
        return count

    def __bool__(self):
        """Return True if there's at least one item."""
        ### if iteration is performed, return True
        for _ in self.callable_obj():
            return True

        ### if no iteration was performed, though, it means
        ### there are no items, so we return False
        return False
