"""Facility with class extension for RectsManager."""

### third-party import
from pygame.math import Vector2


class SizePositionMethods:
    """Methods to control size and pos of RectsManager.

    Contains both in place and not in place operations.
    Operations from this module are methods compatible with
    the pygame.Rect API.
    """

    def move(self, *args):
        """Return the union rect moved according to *args.

        *args is a pair of integers usually given either
        as separate arguments or together in a sequence
        like a tuple, list or pygame.math.Vector2.
        Such integers may be negative as well and they
        represent distances in pixels in 2d space, in
        x and y axes, respectively.
        """
        return self.union_rect.move(*args)

    def move_ip(self, *args):
        """Move rects in place according to *args.

        *args is a pair of integers usually given either
        as separate arguments or together in a sequence
        like a tuple, list or pygame.math.Vector2.
        Such integers may be negative as well and they
        represent distances in pixels in 2d space, in
        x and y axes, respectively.
        """
        for rect in self._get_all_rects():
            rect.move_ip(*args)

    def inflate(self, *args):
        """Return the inflated/deflated union rect.

        *args is a pair of integers usually given either
        as separate arguments or together in a sequence
        like a tuple, list or pygame.math.Vector2.
        Such integers may be negative as well and they
        represent the amount of pixels to increase/decrease
        in width and height.

        Remember the inflation/deflation keeps the rect
        centered, but, if the amount of pixels to
        increase/decrease is too small (between -2 and 2),
        the center will be off.
        """
        return self.union_rect.inflate(*args)

    # XXX the inflate_ip method does good enough job,
    # so that the following condition is almost always
    # satisfied, and even when not, the difference is too
    # small:
    #
    #   Vector2(self.size) - inflated.size == Vector2(0,0)
    #
    # however, it would be good to find a way of doing so
    # without having to loop (I'm talking about the outer
    # for loop); is there such way?

    def inflate_ip(self, *args):
        """Inflate/deflate the rectsmanager in place.

        Does so by increasing/decreasing the distance of
        each rect's center to the rectsmanager center
        proportional to the change in size, so that the
        final position of the underlying rects describes
        a union rect just like described by the inflation/
        deflation of the original union rect.

        *args is a pair of integers usually given either
        as separate arguments or together in a sequence
        like a tuple, list or pygame.math.Vector2.
        Such integers may be negative as well and they
        represent the amount of pixels to increase/decrease
        in width and height.
        """
        ### get an union rect
        union = self.union_rect

        ### store the dimensions (width and height)
        ### resulting from its inflation/deflation
        infl_w, infl_h = union.inflate(*args).size

        ### also store a vector from such dimensions
        infl_size_v = Vector2(infl_w, infl_h)

        ### loop a limited number of times trying to
        ### match the inflated/deflated dimensions;
        ### the loop is exited earlier if the results
        ### are close enough;

        ### also, as commented in the "xxx" comment above
        ### this method, there may be a more direct way of
        ### performing such calculations, but for now this
        ### is the more accurate way we found; also, we used
        ### a "while" loop before, set to stop only when
        ### the minimum accuracy was reached; however, since
        ### in some cases we can't get a result accurate
        ### enough due to rounding issues, it was causing
        ### an infinite loop; we also didn't want to loop
        ### too much when we can usually get good enough
        ### accuracy with usually 2 to 5 iterations; because
        ### of all that, we now use "for" loops and iterate
        ### a maximum of 5 times, which is a number we
        ### determined empirically, since it covers most
        ### cases encountered with enough accuracy;

        for _ in range(5):

            ### obtain the ratio of each inflated/deflated
            ### dimension relative to each union rect
            ### dimension

            w_ratio = infl_w / union.w
            h_ratio = infl_h / union.h

            ### obtain a vector from the center of the union
            union_center_v = Vector2(union.center)

            ### iterate over each underlying rect moving
            ### them closer/farther from the union center
            ### depending on the ratio between inflated/
            ### deflated union and current union rect

            for rect in self._get_all_rects():

                ### get distances x and y from center of
                ### this rect to union center
                center_dx, center_dy = rect.center - union_center_v

                ### multiply each distance by the
                ### corresponding ratio to obtain the
                ### final x and y distances from the center
                ### that the rect must assume

                center_dx = round(center_dx * w_ratio)
                center_dy = round(center_dy * h_ratio)

                ### then assign the new center x and y
                ### coordinates of the rect, obtained
                ### from adding the distances calculated
                ### in the previous step to the union
                ### center

                rect.centerx = union.centerx + center_dx
                rect.centery = union.centery + center_dy

            ### break out of the loop earlier if the
            ### size difference is too small

            ## calculate the difference between the
            ## current size and the inflated/deflated
            ## size; such difference is stored as a
            ## pygame.math.Vector2 obj
            size_difference = self.size - infl_size_v

            ## if the length of the difference is 1 or less,
            ## it is accurate enough, so we exit the loop

            if size_difference.length() <= 1:
                break

            ### otherwise, get a union rect to use in the
            ### next iteration; this union rect is
            ### already updated considering any changes
            ### in the underlying rects positions made
            ### in this loop
            else:
                union = self.union_rect

    def clamp(self, *args):
        """Return the union rect clamped using *args.

        *args is usually a single pygame.Rect instance or
        integers representing such instance (either
        isolated or in a sequence like a tuple or list).
        """
        return self.union_rect.clamp(*args)

    def clamp_ip(self, *args):
        """Move rects in place according to clamp offset.

        *args is usually a single pygame.Rect instance or
        integers representing such instance (either
        isolated or in a sequence like a tuple or list).
        """
        ### get an union rect
        union = self.union_rect

        ### use it to retrieve the position in case of
        ### clamping and the current position

        clamped_pos = union.clamp(*args).topleft
        current_pos = union.topleft

        ### then move all rects by the distance needed
        ### to reach the clamped position
        self.move_ip(clamped_pos - Vector2(current_pos))

    def clip(self, *args):
        """Return the union rect cropped according to *args.

        *args is usually a single pygame.Rect instance or
        integers representing such instance (either
        isolated or in a sequence like a tuple or list).

        Returns the union rect, but cropped to be completely
        inside the argument Rect. If the two rects do not
        overlap to begin with, a Rect with 0 size is
        returned.
        """
        return self.union_rect.clip(*args)

    def union(self, *args):
        """Return union rect joined w/ given rect from *args.

        *args is usually a single pygame.Rect instance or
        integers representing such instance (either
        isolated or in a sequence like a tuple or list).

        Returns a new rect that completely covers the area
        of the two. There may be area inside the new Rect
        that is not covered by the originals.
        """
        return self.union_rect.union(*args)

    def union_ip(self, *args):
        """Join union rect w/ given rect from *args, in place.

        Works by retrieving the union rect, using its
        union_ip method to alter it and then assigning
        its new size and topleft to our own.

        *args is usually a single pygame.Rect instance or
        integers representing such instance (either
        isolated or in a sequence like a tuple or list).
        """
        ### get union rect and perform union_ip on it using
        ### the given arguments, so that its position and
        ### size are updated; this also have the desired
        ### side-effect of type checking and error raising
        ### from a pygame.Rect instance (the union rect)

        union = self.union_rect
        union.union_ip(*args)

        ### use the topleft and size values of this updated
        ### union as our own by assigning them to ours

        self.size = union.size
        self.topleft = union.topleft

    def unionall(self, *args):
        """Return union rect joined w/ sequence of rects.

        *args is a sequence of rects or other objects
        representing rects.

        The items in the sequence may be pygame.Rect
        instances as well as tuples or lists containing
        integers representing rect instances.
        """
        return self.union_rect.unionall(*args)

    def unionall_ip(self, *args):
        """Join union rect w/ sequence of rects, in place.

        *args is a sequence of rects or other objects
        representing rects.

        Works by retrieving the union rect, using its
        unionall_ip method to alter it and then assigning
        its new size and topleft to our own.

        The items in the sequence may be pygame.Rect
        instances as well as tuples or lists containing
        integers representing rect instances.
        """
        ### get union rect and perform unionall_ip on it
        ### using the given arguments, so that its position
        ### and size are updated; this also have the desired
        ### side-effect of type checking and error raising
        ### from a pygame.Rect instance (the union rect)

        union = self.union_rect
        union.unionall_ip(*args)

        ### use the topleft and size values of this updated
        ### union as our own by assigning them to ours

        self.size = union.size
        self.topleft = union.topleft

    def fit(self, *args):
        """Return union rect moved and resized to fit another.

        *args is usually a single pygame.Rect instance or
        integers representing such instance (either
        isolated or in a sequence like a tuple or list).

        The aspect ratio of the union rect used is
        preserved, so the new rectangle may be smaller
        than the target in either width or height.
        """
        return self.union_rect.fit(*args)
