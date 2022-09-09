"""Facility for management of Menu class scrolling."""

from functools import partialmethod

### third-party import
from pygame import Rect

### local imports

from ...surfsman.draw import blit_aligned, draw_depth_finish
from ...surfsman.render import render_rect

from ...classes2d.single import Object2D

from ...colorsman.colors import MENU_BG

## common constants/tools

from ..common import UP_ARROW_SURF, DOWN_ARROW_SURF, SCROLL_SPEED

## utilities
from .utils import get_boundaries


class MenuScrolling:
    """Scrolling related methods for Menu class."""

    def check_clean_bg(self):
        """Store a clean bg if scrollable.

        This method also perform this same check recursively
        in all children.
        """
        ### if the menu is scrollable, copy the body
        ### image into a clean_bg attribute, which will
        ### be used to clean the body image attribute

        if self.is_scrollable():
            self.clean_bg = self.body.image.copy()

        ### check children, too

        for child in self.children:

            ## store method if it exists
            try:
                method = child.check_clean_bg

            ## if it doesn't, just pass
            except AttributeError:
                pass

            ## otherwise, execute it
            else:
                method()

    def draw_scrollable_contents(self):
        """Draw body, children and scrolling objects.

        Used when the menu is scrollable and in addition to
        drawing the body and children must also clean the
        image surface first and also draw the scrolling
        arrows.
        """
        ### draw contents on body after cleaning it then
        ### finally draw the body on the screen with a
        ### special outline to convey depth

        ## clean body
        self.body.image.blit(self.clean_bg, (0, 0))

        ## draw children colliding with the scroll area
        self.draw_children_on_scroll_area()

        ## draw arrows
        self.draw_arrows()

        ## draw the body
        self.body.draw()

        ### check if there's a expanded child in the
        ### scrollable area and call the drawing method
        ### stored in its draw_body_and_its_contents
        ### attribute

        ## retrieve children on scroll_area

        visible_children = (
            child for child in self.children if self.scroll_area.colliderect(child.rect)
        )

        ## iterate over children looking for the expanded
        ## menu

        for child in visible_children:

            # check the existence of an 'is_expanded'
            # attribute
            try:
                is_expanded = child.is_expanded

            # it might be however, that it doesn't
            # have an is_expanded attribute, in which
            # case it is a command; just pass, then;
            except AttributeError:
                pass

            # if 'is_expanded' attribute is True, call its
            # draw_body_and_its_contents method; in this
            # case also break out of the for loop, since
            # there can't be more than one expanded
            # child between siblings at the same time
            # (that is, this is the only one we'll find)

            else:

                if is_expanded:

                    child.draw_body_and_its_contents()
                    break

    ### XXX since children collection is an instance of
    ### classes2d.collections.List2D it might already have
    ### a method to do what is performed in method below

    def draw_children_on_scroll_area(self):
        """Draw children colliding w/ the scroll area.

        The children colliding with the scroll area are
        drawn in the body surface.
        """
        ### retrieve child to draw (children colliding with
        ### the scroll_area

        children_to_draw = (
            child for child in self.children if self.scroll_area.colliderect(child.rect)
        )

        ### calculate the offset between the body rect
        ### topleft coordinates and the origin of the screen,
        ### which happens to be equal to the inverse of the
        ### topleft coordinates
        offset = tuple(-n for n in self.body.rect.topleft)

        ### iterate over children, blitting them on the
        ### body surface using the offset to move their
        ### rects non-destructively, so they are drawn
        ### in the appropriate position in the body surface

        for child in children_to_draw:
            self.body.image.blit(child.image, child.rect.move(offset))

    def draw_arrows(self):
        """Draw arrows on the body surface."""
        ### calculate the offset between the body rect
        ### topleft coordinates and the origin of the screen,
        ### which happens to be equal to the inverse of the
        ### topleft coordinates
        offset = tuple(-n for n in self.body.rect.topleft)

        ### iterate over arrows, blitting them on the
        ### body surface using the offset to move their
        ### rects non-destructively, so they are drawn
        ### in the appropriate position in the body surface

        for arrow in self.arrows:
            self.body.image.blit(arrow.image, arrow.rect.move(offset))

    def check_scrollability(self):
        """Check need to turn menu scrollable.

        If the need is confirmed, perform the setups.
        """
        ### fetch boundaries rect from menu manager
        boundaries_rect = get_boundaries(self)

        ### if the body height is taller than the
        ### boundaries, build the objects to support the
        ### scrolling feature by triggering the appropriate
        ### method

        if self.body.rect.height > boundaries_rect.height:
            self.build_scrolling_objects()

    def build_scrolling_objects(self):
        """Build objects to support scrollability."""
        ### fetch boundaries rect from menu manager
        boundaries_rect = get_boundaries(self)

        ### make the body assume the same height of the
        ### boundaries
        self.body.rect.height = boundaries_rect.height

        ### instantiate new surface for body with the new
        ### dimensions of its rect and the depth finish

        self.body.image = render_rect(*self.body.rect.size, MENU_BG)

        draw_depth_finish(self.body.image)

        ### create arrow objects and assign surfaces and
        ### rects to them

        up_arrow = Object2D()
        up_arrow.image = UP_ARROW_SURF
        up_arrow.rect = up_arrow.image.get_rect()

        down_arrow = Object2D()
        down_arrow.image = DOWN_ARROW_SURF
        down_arrow.rect = down_arrow.image.get_rect()

        ### get the combined height of the arrows
        arrows_height = up_arrow.rect.height + down_arrow.rect.height

        ### calculate the dimensions for the scrollable area
        ### and create it

        scrollable_height = self.body.rect.height - arrows_height

        dimensions = self.body.rect.width, scrollable_height

        self.scroll_area = Rect((0, 0), dimensions)

        ### expand the up and down arrow surfaces and
        ### rects horizontally so that they fit the
        ### self.body.rect.width

        ## define width and height of arrows (height
        ## is preserved as can be seen)

        arrows_width = self.children[0].rect.width
        arrows_height = up_arrow.rect.height

        ## replace arrows surfaces by new ones,
        ## blitting the original surfaces right on the
        ## middle of the new surfaces

        for arrow in (up_arrow, down_arrow):

            ## backup the original surface
            original_surf = arrow.image

            ## replace by new one

            arrow.image = render_rect(
                arrows_width,
                arrows_height,
                MENU_BG,
            )

            ## blit original over the new one

            blit_aligned(
                surface_to_blit=original_surf,
                target_surface=arrow.image,
                retrieve_pos_from="center",
                assign_pos_to="center",
            )

            ## update size of arrow's rect
            arrow.rect.size = arrow.image.get_size()

        ### reference scroll methods on the arrows

        up_arrow.scroll = self.scroll_up
        down_arrow.scroll = self.scroll_down

        ### store both arrows in attributes

        self.up_arrow = up_arrow
        self.down_arrow = down_arrow

        ### also reference them together in a container
        ### stored in a 'arrows' attribute
        self.arrows = self.up_arrow, self.down_arrow

        ### finally, since we just create new contents for
        ### the body, let's reposition all of them and the
        ### children as well inside the body
        self.reposition_scrollable_contents()

    def scroll(self, dy, collapse_expanded_child=True):
        """Scroll children up/down if needed.

        dy (integer)
            represent how much to move in y axis.

        collapse_expanded_child (boolean, defaults to True)
            defines whether or not the expanded child must be
            collapsed when scrolling. It is True when used
            normally, that is, when autoscrolling by hovering
            the scroll arrows, so the expanded child
            collapses.

            If we don't collapse the body of the moving
            expanded child when autoscrolling the arrows we
            would have to add extra complexity to the code
            in order to control/predict the position of the
            moving body.

            We deem such complexity unnecessary because we
            assume that when users scroll the menu they do
            so in order to reach something which isn't
            visible, otherwise there would be no need to
            scroll. Thus, getting rid of the excess of what
            is visible (the body of the expanded child)
            shouldn't cause any problem.

            There is, though, a scenario wherein we don't
            collapse the body of the expanded child (that
            is the parameter is set to False: only when
            scrolling using the mousewheel. This is so
            because it would otherwise be confusing/
            unpleasant to have the expanded body suddenly
            vanish when scrolling the menu with the mouse
            still hovering the child.

            When scrolling the menu with the mousewheel,
            the child may still collapse though, even with
            this argument being False, that is, when the
            menu scrolls, the child changes its position and
            other child may end up being hovered by the
            mouse, in which case the now unhovered child
            will naturally collapse. This is a desired
            effect.

            This parameter and its effect is not a
            requirement though, but rather an usability
            measure so the menu behaviour is more pleasing/
            less confusing.
        """
        ### check if there's need to scroll based on
        ### presence/absence of first or last child
        ### in the scroll area

        first_rect = self.children[0].rect
        last_rect = self.children[-1].rect

        ## if scrolling children into the positive y
        ## direction (children are being moved down), but
        ## the first rect is already on the scroll area,
        ## cancel the scrolling by returning early
        if dy > 0:
            if self.scroll_area.contains(first_rect):
                return

        ## if scrolling children into the negative y
        ## direction (moving children up), but the last
        ## rect is already on the scroll area, cancel the
        ## scrolling by returning early
        elif dy < 0:
            if self.scroll_area.contains(last_rect):
                return

        ### provided we didn't return early, the scrolling
        ### is legal, so move the rects using the provided
        ### delta for the y axis
        self.children.rect.move_ip(0, dy)

        ### eliminate excessive scrolling: we close any gap
        ### that may exist between first child/first arrow
        ### or last child/last arrow when they are scrolled
        ### inwards the scroll area
        self.fix_scrolling()

        ### if requested, collapse the expanded child (see
        ### the docstring of this method about this
        ### collapse_expanded_child parameter)

        if collapse_expanded_child:

            ## iterate over each child checking the
            ## existence of the 'is_expanded' attribute
            ## and executing the collapsing method of the
            ## child if such attribute is True

            for child in self.children:

                # try storing the value of the attribute
                try:
                    is_expanded = child.is_expanded

                # if it doesn't exist, just pass
                except AttributeError:
                    pass

                # if the attribute exists and its value is
                # True, collapse the child using the proper
                # method

                else:

                    if is_expanded:
                        child.collapse_self_and_children()

        ### if the children shouldn't be collapsed though,
        ### we should reposition the body of each child
        ### recursively; this is a measure to adjust the
        ### children, since they must follow the position
        ### of their scrolling parent, when the parent is
        ### being hovered by the mouse, an usability
        ### measure

        else:

            ## iterate over each child checking the
            ## existence of the 'reposition_body' method
            ## and executing it if it is found

            for child in self.children:

                # store method if it exists
                try:
                    method = child.reposition_body

                # if method doesn't exist, just pass
                except AttributeError:
                    pass

                # otherwise execute the stored method
                else:
                    method()

        ### collapse the expanded child if there is one and
        ### it doesn't collide with the scroll area (this
        ### is needed to prevent the expanded body to be
        ### still hoverable when the expanded child rect is
        ### not visible); the ommission of this measure
        ### would in specific cases cause the expanded body
        ### to be hoverable while invisible, causing
        ### confusion and preventing the user to use the
        ### menu properly

        for child in self.children:

            ## try retrieving the value of the 'is_expanded'
            ## attribute
            try:
                is_expanded = child.is_expanded

            ## if it doesn't even exist, just pass
            except AttributeError:
                pass

            ## otherwise, if it exists and is True and the
            ## expanded child don't collide with the scroll
            ## area, collapse it

            else:

                # evaluate condition
                child_touches_scroll_area = self.scroll_area.colliderect(child.rect)

                # check if conditions are met and execute
                # the collapsing method

                if is_expanded and not child_touches_scroll_area:
                    child.collapse_self_and_children()

    scroll_up = partialmethod(scroll, SCROLL_SPEED)
    scroll_down = partialmethod(scroll, -SCROLL_SPEED)

    def fix_scrolling(self):
        """Eliminate excessive scrolling.

        Closes gap between first child/first arrow or
        last child/last_arrow if it exists. Such gap is
        sometimes formed when scrolling the first or last
        child inwards the scroll area, since their width
        isn't a multiple of the scrolling speed.
        """
        ### retrieve rects of first and last children

        first_rect = self.children[0].rect
        last_rect = self.children[-1].rect

        ### before starting to check if there's an gap we
        ### must check if at least one of the children
        ### is completely inside the scroll area, because
        ### since there can't be any gap if the neither
        ### children is inside such area there would be no
        ### point in checking anyway

        ## check whether each child is completely inside the
        ## scroll area

        first_inside = self.scroll_area.contains(first_rect)
        last_inside = self.scroll_area.contains(last_rect)

        ## if neither the first nor the last rect are
        ## completely inside the scroll area, cancel the
        ## execution of the rest of the method by returning
        ## earlier
        if not first_inside and not last_inside:
            return

        ### now determine which of the children is the one
        ### inside the the scroll area (they can't be both
        ### completely inside, otherwise there would be no
        ### need to make the menu scrollable in the first
        ### place) and whether there's a gap and fix it if
        ### it is the case

        ## if the first_rect is inside the scroll area
        ## and its top isn't aligned with the up arrow
        ## bottom it means there's a gap, so align them by
        ## moving the children by the difference between
        ## them

        if first_inside and first_rect.top != self.up_arrow.rect.bottom:

            # calculate the difference
            y_offset = self.up_arrow.rect.bottom - first_rect.top

            # move children
            self.children.rect.move_ip(0, y_offset)

        ## otherwise if it is the last_rect which is inside
        ## the scroll area and its bottom isn't aligned with
        ## the down arrow top, then there's a gap, so align
        ## them by moving the children by the difference
        ## between them

        elif last_inside and last_rect.bottom != self.down_arrow.rect.top:

            # calculate the difference
            y_offset = self.down_arrow.rect.top - last_rect.bottom

            # move children
            self.children.rect.move_ip(0, y_offset)

    def is_scrollable(self):
        """Return True if children are scrollable.

        Works by verifying the presence of a scroll area
        attribute, which implies the scrollability of the
        menu.
        """
        try:
            return self.scroll_area
        except AttributeError:
            pass

    def reposition_scrollable_contents(self):
        """Reposition contents inside the body.

        Contents are the arrows, scroll area and children.
        As implied by the contents list in the previous
        sentence, this method is used to reposition the
        contents of body inside it when besides the children
        the menu also have additional objects to support
        scrolling which must also be positioned in the
        menu's body.
        """
        ### get topleft coordinates of the body rect,
        ### with a small offset

        offset = 1, 1
        topleft = self.body.rect.move(offset).topleft

        ### position arrows and scroll area relative to
        ### the topleft defined above and one another

        self.up_arrow.rect.topleft = topleft

        self.scroll_area.topleft = self.up_arrow.rect.bottomleft

        self.down_arrow.rect.topleft = self.scroll_area.bottomleft

        ### position children relative to the scroll area
        ### topleft coordinates

        self.children.rect.topleft = self.scroll_area.topleft

        ## position children one on top of the other

        self.children.rect.snap_rects_ip(
            retrieve_pos_from="bottomleft",
            assign_pos_to="topleft",
        )
