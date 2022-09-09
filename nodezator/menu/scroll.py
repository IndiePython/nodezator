"""Facility for menu manager scrollability extension."""

### standard library import
from functools import partialmethod


### third-party import
from pygame import Rect


### local imports

from ..classes2d.single import Object2D

from ..surfsman.draw import blit_aligned
from ..surfsman.render import render_rect

from .common import (
    LEFT_ARROW_SURF,
    RIGHT_ARROW_SURF,
    UP_ARROW_SURF,
    DOWN_ARROW_SURF,
    SCROLL_SPEED,
)

from ..colorsman.colors import MENU_BG


class Scrollability:
    """Methods to manage scrollability on menu manager.

    Also helps with the scrollability of the
    menu.submenu.main.Menu class, since its instances also
    have their own scrollability feature which depends on
    the feature implemented in this class extension.
    """

    def check_scrollability(self):
        """Checks if the menu manager needs scrollability.

        If so, triggers the method responsible for building
        special objects to support the scrollability feature.

        The scroll orientation also depends on the initial
        orientation of the menu manager.
        """
        ### check need to build scrolling support objects
        ### according to whether or not the children trepass
        ### the maximum dimensions defined; depends on
        ### whether the menu manager is a menubar

        if self.is_menubar:

            ## calculate width occupied by children by
            ## measuring the distance between the first
            ## child's left corner and the last child's right
            ## corner

            first_child_left = self.children[0].rect.left
            last_child_right = self.children[-1].rect.right

            children_width = last_child_right - first_child_left

            ## if the children width ends up surpassing
            ## the acceptable width for the menu manager,
            ## build the scrolling objects
            if children_width > self.max_width:
                self.build_scrolling_objects()

        else:

            ## calculate height occupied by children by
            ## measuring the distance between the last
            ## child's bottom corner and the first child's
            ## top corner

            last_child_bottom = self.children[-1].rect.bottom
            first_child_top = self.children[0].rect.top

            children_height = last_child_bottom - first_child_top

            ## if the children height ends up surpassing
            ## the acceptable height for the menu manager,
            ## build the scrolling objects
            if children_height > self.max_height:
                self.build_scrolling_objects()

    def build_scrolling_objects(self):
        """Build objects to support scrolling.

        Only called if menu items go out of the boundaries
        defined upon instantiation (defaults to the screen
        boundaries).

        In addition to build the new objects, we also
        reposition the children inside the scroll area
        created here.

        Note: the entire hierarchy of children will also
        need repositioning, but this will be done at the end
        of the menu manager __init__ method.
        """
        if self.is_menubar:

            ### create arrow objects (left and right arrows),
            ### assigning appropriate surfaces and their
            ### rects to them

            left_arrow = Object2D(
                image=LEFT_ARROW_SURF, rect=LEFT_ARROW_SURF.get_rect()
            )

            right_arrow = Object2D(
                image=RIGHT_ARROW_SURF, rect=RIGHT_ARROW_SURF.get_rect()
            )

            ### get the their combined width
            arrows_width = left_arrow.rect.width + right_arrow.rect.width

            ### calculate the dimensions for the scrollable
            ### area and create it

            scrollable_width = self.max_width - arrows_width
            height = self.children[0].rect.height
            dimensions = scrollable_width, height

            self.scroll_area = Rect((0, 0), dimensions)

            ### reference scroll methods on the arrows

            left_arrow.scroll = self.scroll_left
            right_arrow.scroll = self.scroll_right

            ### store both arrows in attributes

            self.left_arrow = left_arrow
            self.right_arrow = right_arrow

            ### also store them together in a container
            self.arrows = self.left_arrow, self.right_arrow

        else:

            ### create arrow objects (up and down arrows),
            ### assigning appropriate surfaces and their
            ### rects to them

            up_arrow = Object2D(image=UP_ARROW_SURF, rect=UP_ARROW_SURF.get_rect())

            down_arrow = Object2D(
                image=DOWN_ARROW_SURF, rect=DOWN_ARROW_SURF.get_rect()
            )

            ## get their combined height
            arrows_height = up_arrow.rect.height + down_arrow.rect.height

            ## calculate the dimensions for the scrollable
            ## area and create it

            scrollable_height = self.max_height - arrows_height
            width = self.children[0].rect.width
            dimensions = width, scrollable_height

            self.scroll_area = Rect((0, 0), dimensions)

            ### expand the up and down arrow surfaces and
            ### rects horizontally so that they fit the
            ### scroll_area width

            ## define width and height of arrows (height
            ## is preserved as can be seen)

            arrows_width = self.scroll_area.width
            arrows_height = up_arrow.rect.height

            ## replace arrows surfaces by new ones,
            ## blitting the original surfaces right on the
            ## middle of the new surfaces

            for arrow in (up_arrow, down_arrow):

                ## backup the original surface
                original_surf = arrow.image

                ## replace by new one

                arrow.image = render_rect(arrows_width, arrows_height, MENU_BG)

                ## blit original over the new one

                blit_aligned(
                    surface_to_blit=original_surf,
                    target_surface=arrow.image,
                    retrieve_pos_from="center",
                    assign_pos_to="center",
                )

                ## update size of arrow's rect
                arrow.rect.size = arrow.image.get_size()

            ### reference scroll methods on the respective
            ### arrows

            up_arrow.scroll = self.scroll_up
            down_arrow.scroll = self.scroll_down

            ### store both arrows in attributes

            self.up_arrow = up_arrow
            self.down_arrow = down_arrow

            ### also store them together in a container
            self.arrows = self.up_arrow, self.down_arrow

        ### finally reposition all the new object and the
        ### children inside the menu manager
        self.reposition_menu_manager_contents()

    def is_scrollable(self):
        """Return a truthful value if menu is scrollable.

        Used to define if a menu is scrollable based on the
        return value (either the scroll area if scrollable,
        or None, if not). That is, the presence of a scroll
        area attribute implies the scrollability of the menu.
        """
        try:
            return self.scroll_area
        except AttributeError:
            pass

    def manage_scrolling(self):
        """Scroll colliding arrow farthest from root.

        The root being the menu manager.

        The ordering is important, so even if arrows end up
        on top of each other, we scroll the correct one
        (the one on top, that is, the one farthest on the
        menu hierarchy, which is why it is drawn last and
        thus appears on top of the others).
        """
        ### admin task: create/reset a hovered_arrow
        ### to hold a hovered arrow if we find one
        self.hovered_arrow = None

        ### list all arrows from closest to menu manager to
        ### the farthest ones down the active branch
        all_arrows = self.gather_arrows(self, [])

        ### reverse the order, which makes the iteration
        ### start from the farthest one when iterating
        reversed_arrows = reversed(all_arrows)

        ### iterate over each arrow from the farthest one
        ### from the menu manager to the closest one; as
        ### soon as you find a colliding one, scroll it and
        ### stop iterating by breaking out of loop

        for arrow in reversed_arrows:

            if arrow.rect.collidepoint(self.mouse_pos):

                arrow.scroll()

                ## as an admin task, also store a reference
                ## to the collided arrow in the hovered_arrow
                ## attribute (it is used in other methods)
                self.hovered_arrow = arrow

                break

    def gather_arrows(self, menu, all_arrows):
        """Gather arrows from menu manager to active branch.

        Works recursively from the menu to the active branch
        (if there is one, otherwise only the arrows in the
        menu manager itself are gathered, if it has arrows).

        menu (either the menu.main.MenuManager or a
             a menu.submenu.main.Menu instance)
            object which may have an 'arrows' attribute
            containing arrows.

        all_arrows (list)
            contains arrows found while iterating the
            hierarchy recursively (might also be empty if
            none was found).

        We take measures to only gather visible arrows,
        that is, those on the top menu and/or the active
        branch, if there's one. This is because if a menu
        isn't a top menu or is in the active branch, than it
        can't be visible and thus the user won't acknowledge
        its existence, much less interact with it.
        """
        ### check whether the menu object has arrows
        try:
            arrows = menu.arrows

        ### if it doesn't, just pass
        except AttributeError:
            pass

        ### otherwise, check preliminary conditions for the
        ### arrows to be taken into account

        else:

            ### for its arrows to be added, the menu must
            ### either:
            ### 1) be the MenuManager instance
            ### 2) be the active menu
            ### 3) its top parent must the active menu and
            ###    it should be expanded

            if (
                menu is self
                or menu is self.active_menu
                or (self.top_menu_is_active(menu) and menu.is_expanded)
            ):

                ## since one of the preliminary conditions
                ## was met, we are ready to append the
                ## arrows to the all_arrows list, but
                ## before doing that, if the menu is not
                ## self (that is, not the MenuManager
                ## instance), we must eliminate past arrows
                ## from the list if the mouse is touching
                ## the body of the menu;
                ## this is done because if the cursor is on
                ## the body of a expanded submenu, it means
                ## we are not interested in the arrows
                ## before it in the hierarchy;

                if menu is not self:

                    ## get the rect in the body attribute
                    rect = menu.body.rect

                    ## use it to check for the collision
                    if rect.collidepoint(self.mouse_pos):
                        all_arrows.clear()

                ## now you can finally append the arrows
                ## (by extending the list with them)
                all_arrows.extend(arrows)

        ### also check the menu children for the presence of
        ### arrows

        try:
            children = menu.children

        except AttributeError:
            pass

        else:

            for child in children:

                all_arrows = self.gather_arrows(child, all_arrows)

        ### finally, return the arrows gathered
        return all_arrows

    def scroll(self, dx, dy, collapse_expanded_child=True):
        """Scroll children if needed.

        dx, dy (integers)
            represent how much to move in x and y axes,
            respectively.

        collapse_expanded_child (boolean, defaults to True)
            defines whether or not the active menu must be
            collapsed when scrolling. It is True when used
            normally, that is, when autoscrolling by hovering
            the scroll arrows, so the expanded child
            collapses (that is, the active menu).

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
        ### retrieve the last and first child rects

        first_rect = self.children[0].rect
        last_rect = self.children[-1].rect

        ### check need to scroll; look into the appropriate
        ### axis depending on the whether the menu manager
        ### is a menubar

        if self.is_menubar:

            ## if scrolling children into the positive x
            ## direction, but the first rect is already on
            ## the scroll area, cancel the scrolling by
            ## returning early
            if dx > 0:
                if self.scroll_area.contains(first_rect):
                    return

            ## if scrolling children into the negative x
            ## direction, but the last rect is already on
            ## the scroll area, cancel the scrolling by
            ## returning early
            elif dx < 0:
                if self.scroll_area.contains(last_rect):
                    return

        else:

            ## if scrolling children into the positive y
            ## direction (children are being moved down),
            ## but the first rect is already on the scroll
            ## area, cancel the scrolling by returning early
            if dy > 0:
                if self.scroll_area.contains(first_rect):
                    return

            ## if scrolling children into the negative y
            ## direction (moving children up), but the last
            ## rect is already on the scroll area, cancel
            ## the scrolling by returning early
            elif dy < 0:
                if self.scroll_area.contains(last_rect):
                    return

        ### provided we didn't return early, the scrolling
        ### is legal, so move the rects using the provided
        ### deltas for each axis
        self.children.rect.move_ip(dx, dy)

        ### eliminate excessive scrolling: we close any gap
        ### that may exist between first child/first arrow
        ### or last child/last arrow when they are scrolled
        ### inwards the scroll area
        self.fix_scrolling()

        ### if requested, collapse the expanded child (in
        ### this case the active menu; see docstring about
        ### the collapse_expanded_child parameter)
        if collapse_expanded_child:
            self.collapse_active_menu()

        ### if the expanded child shouldn't be collapsed
        ### though, we should reposition the body of each
        ### child recursively; this is a measure adopted so
        ### the children follow the position of their
        ### scrolling parent, when the mouse is hovering
        ### the parent, an usability measure
        else:
            self.reposition_children_bodies()

        ### collapse the active menu if there is one and it
        ### doesn't collide with the scroll area (this
        ### is needed to prevent the expanded branch to be
        ### hoverable when the active menu rect is not
        ### visible); the ommission of this measure would in
        ### specific cases cause the expanded menu to be
        ### hoverable while invisible, causing confusion and
        ### preventing the user to use the menu properly

        if self.active_menu and not self.scroll_area.colliderect(self.active_menu.rect):

            self.collapse_active_menu()

    scroll_left = partialmethod(scroll, SCROLL_SPEED, 0)
    scroll_right = partialmethod(scroll, -SCROLL_SPEED, 0)
    scroll_up = partialmethod(scroll, 0, SCROLL_SPEED)
    scroll_down = partialmethod(scroll, 0, -SCROLL_SPEED)

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

        ### now check the need for correction based on
        ### whether the menu manager is a menuar and
        ### on which of the children is the one inside the
        ### scroll area (they can't be both completely
        ### inside, otherwise there would be no need to make
        ### the menu scrollable in the first place)

        if self.is_menubar:

            ## if the first_rect is inside the scroll area
            ## and its left isn't aligned with the left
            ## arrow right it means there's a gap, so align
            ## them by moving the children by the difference
            ## between them

            if first_inside and first_rect.left != self.left_arrow.rect.right:

                # calculate the difference
                x_offset = self.left_arrow.rect.right - first_rect.left

                # move children
                self.children.rect.move_ip(x_offset, 0)

            ## if the last_rect is inside the scroll area
            ## and its right isn't aligned with the down
            ## arrow left it means there's a gap, so align
            ## them by moving the children by the difference
            ## between them

            elif last_inside and last_rect.right != self.right_arrow.rect.left:

                # calculate the difference
                x_offset = self.right_arrow.rect.left - last_rect.right

                # move children
                self.children.rect.move_ip(x_offset, 0)

        else:

            ## if the first_rect is inside the scroll area
            ## and its top isn't aligned with the up arrow
            ## top it means there's a gap, so align them by
            ## moving the children by the difference between
            ## them

            if first_inside and first_rect.top != self.up_arrow.rect.bottom:

                # calculate the difference
                y_offset = self.up_arrow.rect.bottom - first_rect.top

                # move children
                self.children.rect.move_ip(0, y_offset)

            ## if the last_rect is inside the scroll area
            ## and its bottom isn't aligned with the down
            ## arrow top it means there's a gap, so align
            ## them by moving the children by the difference
            ## between them

            elif last_inside and last_rect.bottom != self.down_arrow.rect.top:

                # calculate the difference
                y_offset = self.down_arrow.rect.top - last_rect.bottom

                # move children
                self.children.rect.move_ip(0, y_offset)

    def mouse_scroll(self, button):
        """Check if needs to scroll and the direction.

        button (integer in {4, 5})
            represents a mouse button pressed (in this case
            the "buttons" on the mouse wheel). More precisely
            whether the user scrolled the mouse wheel up
            (button==4) or down (button==5).
        """
        ### check if the parent of the hovered widget has
        ### an 'arrows' attribute
        try:
            arrows = self.hovered_widget.parent.arrows

        ### an attribute error may be raise though for
        ### either of those reasons (in which case you
        ### should just pass):
        ### 1) hovered widget is None and thus have
        ### no 'parent' attribute
        ### 2) the parent attribute is a command and thus
        ### never has an 'arrows' attribute
        ### 3) the paretn attribute is a menu, but doesn't
        ### have an 'arrows' attribute
        except AttributeError:
            pass

        ### otherwise, in case there really are arrows make
        ### extra checks to guarantee one of the arrows
        ### must be scrolled and which one

        else:

            ## make extra checks to guarantee one of the
            ## arrows must be scrolled; those checks are
            ## usability measures meant to make menu usage
            ## more pleasing or less confusing; they are not
            ## requirements per se;

            # if there is a hovered arrow and it is not one
            # of the retrieved arrows, cancel the scrolling
            # by returning early
            if self.hovered_arrow and self.hovered_arrow not in arrows:
                return

            # alias the parent of the hovered widget for
            # better code spacing
            hovered_parent = self.hovered_widget.parent

            # if the hovered_parent is the menu
            # manager itself, but the mouse isn't hovering
            # the pygame.Rect in its 'rect' attribute,
            # cancel the scrolling by returning early

            if hovered_parent is self:
                if not hovered_parent.rect.collidepoint(self.mouse_pos):
                    return

            # if the hovered_parent is a regular menu,
            # but the mouse isn't hovering the pygame.Rect
            # in its 'body.rect' attribute, cancel the
            # scrolling by returning early

            else:

                if not hovered_parent.body.rect.collidepoint(self.mouse_pos):
                    return

            ## finally pick and scroll the proper arrow
            ## depending on the direction of the scroll wheel
            ## used (either button 4 for scrolling the mouse
            ## wheel up or 5 for scrolling down)

            # pick the arrow
            if button == 4:
                chosen_arrow = arrows[0]
            elif button == 5:
                chosen_arrow = arrows[1]

            # call the scroll method on the chosen arrow
            # with collapse_expanded_child argument set to
            # False (for more information check the
            # 'scroll' method docstring in either the
            # menu/scroll.py or menu/submenu/scroll.py
            # module, where the collapse_expanded_child
            # parameter is explained)
            chosen_arrow.scroll(collapse_expanded_child=False)
