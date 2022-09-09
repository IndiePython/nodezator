"""Facility for definition of rect-like 2d space properties.

This module contains a class definition which constitutes
an extension of the RectsManager class from rectsman/main.py
module.

The spatial properties defined here are those which get and
set values representing positions or dimensions in 2d space.
"""

### third-party import
from pygame.math import Vector2


class SpatialProperties:
    """Definitions of 2d space properties as in pygame.Rect.

    That is,

    x, y
    top (alias of y), left (alias of x), bottom, right,
    topleft, bottomleft, topright, bottomright,
    midtop, midbottom, midleft, midright,
    centerx, centery, center,
    w, h, size,
    width (alias of w), height (alias of h)

    Note that all the setters also set the value in a
    sample rect and then read the value from the same
    property in the sample rect which just had the value
    assigned to, all this before processing the value.

    This is done for the desired side-effect of emulating
    the same type coercion behaviour performed by an
    instance of pygame.Rect (since the union is one) and
    also to emulate pygame.Rect error raising in case
    there's something wrong with the argument(s). This is
    both simpler and probably quicker than using custom
    written Python code to perform all checks/coercions
    which are performed on pygame.Rect underlying C code.

    Furthermore, considering how similar the logic of each
    property is to each other (including the setters), a
    lot of behaviour could probably be encapsulated,
    abstracted or somehow simplified using metaprogramming
    and/or other techniques, but the code was purposefully
    kept straightforward for the sake of speed. Therefore,
    we advise to keep them the way they are now. Unless,
    of course, you have a better solution.
    """

    ### single coordinate positions

    @property
    def x(self):
        """Return x from union rect."""
        return self.union_rect.x

    @x.setter
    def x(self, value):
        """Move rects uniformly so 'x == value'."""
        self._sample_rect.x = value

        self.move_ip(self._sample_rect.x - self.x, 0)

    left = x  # alias x to left

    @property
    def y(self):
        """Return y from union rect."""
        return self.union_rect.y

    @y.setter
    def y(self, value):
        """Move rects uniformly so 'y == value'."""
        self._sample_rect.y = value

        self.move_ip(0, self._sample_rect.y - self.y)

    top = y  # alias y to top

    @property
    def bottom(self):
        """Return bottom from union rect."""
        return self.union_rect.bottom

    @bottom.setter
    def bottom(self, value):
        """Move rects uniformly so 'bottom == value'."""
        self._sample_rect.bottom = value

        self.move_ip(0, self._sample_rect.bottom - self.bottom)

    @property
    def left(self):
        """Return left from union rect."""
        return self.union_rect.left

    @left.setter
    def left(self, value):
        """Move rects uniformly so 'left == value'."""
        self._sample_rect.left = value

        self.move_ip(self._sample_rect.left - self.left, 0)

    @property
    def right(self):
        """Return right from union rect."""
        return self.union_rect.right

    @right.setter
    def right(self, value):
        """Move rects uniformly so 'right == value'."""
        self._sample_rect.right = value

        self.move_ip(self._sample_rect.right - self.right, 0)

    @property
    def centerx(self):
        """Return centerx from union rect."""
        return self.union_rect.centerx

    @centerx.setter
    def centerx(self, value):
        """Move rects uniformly so 'centerx == value'."""
        self._sample_rect.centerx = value

        self.move_ip(self._sample_rect.centerx - self.centerx, 0)

    @property
    def centery(self):
        """Return centery from union rect."""
        return self.union_rect.centery

    @centery.setter
    def centery(self, value):
        """Move rects uniformly so 'centery == value'."""
        self._sample_rect.centery = value

        self.move_ip(0, self._sample_rect.centery - self.centery)

    ### double coordinate positions

    ## center

    @property
    def center(self):
        """Return center from union rect."""
        return self.union_rect.center

    @center.setter
    def center(self, value):
        """Move rects uniformly so 'center == value'."""
        self._sample_rect.center = value

        self.move_ip(self._sample_rect.center - Vector2(self.center))

    ## corners

    @property
    def topleft(self):
        """Return topleft from union rect."""
        return self.union_rect.topleft

    @topleft.setter
    def topleft(self, value):
        """Move rects uniformly so 'topleft == value'."""
        self._sample_rect.topleft = value

        self.move_ip(self._sample_rect.topleft - Vector2(self.topleft))

    @property
    def bottomleft(self):
        """Return bottomleft from union rect."""
        return self.union_rect.bottomleft

    @bottomleft.setter
    def bottomleft(self, value):
        """Move rects uniformly so 'bottomleft == value'."""
        self._sample_rect.bottomleft = value

        self.move_ip(self._sample_rect.bottomleft - Vector2(self.bottomleft))

    @property
    def topright(self):
        """Return topright from union rect."""
        return self.union_rect.topright

    @topright.setter
    def topright(self, value):
        """Move rects uniformly so 'topright == value'."""
        self._sample_rect.topright = value

        self.move_ip(self._sample_rect.topright - Vector2(self.topright))

    @property
    def bottomright(self):
        """Return bottomright from union rect."""
        return self.union_rect.bottomright

    @bottomright.setter
    def bottomright(self, value):
        """Move rects uniformly so 'bottomright == value'."""
        self._sample_rect.bottomright = value

        self.move_ip(self._sample_rect.bottomright - Vector2(self.bottomright))

    ## midpositions

    @property
    def midtop(self):
        """Return midtop from union rect."""
        return self.union_rect.midtop

    @midtop.setter
    def midtop(self, value):
        """Move rects uniformly so 'midtop == value'."""
        self._sample_rect.midtop = value

        self.move_ip(self._sample_rect.midtop - Vector2(self.midtop))

    @property
    def midbottom(self):
        """Return midbottom from union rect."""
        return self.union_rect.midbottom

    @midbottom.setter
    def midbottom(self, value):
        """Move rects uniformly so 'midbottom == value'."""
        self._sample_rect.midbottom = value

        self.move_ip(self._sample_rect.midbottom - Vector2(self.midbottom))

    @property
    def midleft(self):
        """Return midleft from union rect."""
        return self.union_rect.midleft

    @midleft.setter
    def midleft(self, value):
        """Move rects uniformly so 'midleft == value'."""
        self._sample_rect.midleft = value

        self.move_ip(self._sample_rect.midleft - Vector2(self.midleft))

    @property
    def midright(self):
        """Return midright from union rect."""
        return self.union_rect.midright

    @midright.setter
    def midright(self, value):
        """Move rects uniformly so 'midright == value'."""
        self._sample_rect.midright = value

        self.move_ip(self._sample_rect.midright - Vector2(self.midright))

    ### dimensions

    @property
    def size(self):
        """Return size from union rect."""
        return self.union_rect.size

    @size.setter
    def size(self, value):
        """Move rects from/to center so 'size == value'.

        If possible.
        """
        self._sample_rect.size = value

        ### get an union rect
        union = self.union_rect

        ### store current topleft
        topleft = union.topleft

        ### inflate the group in place using the size
        ### difference

        ## calculate size difference
        size_difference = self._sample_rect.size - Vector2(union.size)

        ## use inflate_ip with size difference
        self.inflate_ip(size_difference)

        ### restore the inflated group to its original
        ### topleft position
        self.topleft = topleft

    @property
    def w(self):
        """Return width from union rect."""
        return self.union_rect.w

    @w.setter
    def w(self, value):
        """Use size property setter so 'width == value'."""
        self._sample_rect.width = value

        new_size = (self._sample_rect.width, self.height)
        self.size = new_size

    width = w  # alias w to width

    @property
    def h(self):
        """Return height from union rect."""
        return self.union_rect.height

    @h.setter
    def h(self, value):
        """Use size property setter so 'height == value'."""
        self._sample_rect.height = value

        new_size = (self.width, self._sample_rect.height)
        self.size = new_size

    height = h  # alias h to height
