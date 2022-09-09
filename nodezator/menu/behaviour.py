"""Facility for menu manager behaviours extension."""

### third-party imports

from pygame import (
    QUIT,
    KEYUP,
    K_ESCAPE,
    K_RETURN,
    K_KP_ENTER,
    MOUSEBUTTONUP,
)

from pygame.draw import rect as draw_rect
from pygame.event import get as get_events
from pygame.mouse import get_pos as get_mouse_pos
from pygame.display import update


### local imports

from ..pygameconstants import SCREEN

from ..ourstdlibs.mathutils import invert_point
from ..ourstdlibs.treeutils import yield_tree_attrs

from ..ourstdlibs.collections.general import CallList

from ..classes2d.single import Object2D

from ..surfsman.cache import cache_screen_state

from ..loopman.exception import (
    QuitAppException,
    SwitchLoopException,
)

from .common import get_nearest_attr_name

from ..colorsman.colors import BLACK


class BehaviourDefinitions(Object2D):
    """Defines handle_input, update and drawing operations."""

    def define_drawing_behaviours(self):
        """Define drawing operations.

        Also takes scrollability or lack thereof into
        account.
        """
        ### instantiate call list to hold drawing operations
        self.draw = CallList()

        ### before gathering the behaviours, let's first
        ### define behaviours for drawing menu manager with
        ### all branches collapsed, depending on various
        ### conditions

        ## create call list to gather such behaviours
        self.draw_top_items = CallList()

        ## add specific behaviour when menu manager is
        ## scrollable

        if self.is_scrollable():

            # append the super().draw method in
            # draw_top_items list
            self.draw_top_items.append(self.clean_image)

            # append method to draw items in the scroll
            # area
            self.draw_top_items.append(self.draw_items_on_scroll_area)

            # append method to draw arrows
            self.draw_top_items.append(self.draw_arrows)

            # append the super().draw method in
            # draw_top_items list
            self.draw_top_items.append(super().draw)

        ## otherwise add specific behaviour for when the
        ## menu manager items don't scroll

        else:

            # append the super().draw method in
            # draw_top_items list
            self.draw_top_items.append(super().draw)

            # draw children normally
            self.draw_top_items.append(self.children.draw)

        ## also, if an outline is requested, add method to
        ## draw it (this is an usability measure designed
        ## to be used with popup menus, that is, vertical
        ## ones; usage on menubar is possible, though not
        ## encouraged)
        if self.use_outline:
            self.draw_top_items.append(self.draw_outline)

        ### now let's gather all drawing behaviours to be
        ### executed in the draw cycle of the menu manager

        self.draw = CallList(
            [self.draw_behind, self.draw_top_items, update]  # pygame.display.update
        )

        ### also define a control attribute: the active menu
        self.active_menu = None

    def clean_image(self):
        """Clean image attribute.

        Does so by blitting the clean_bg surface (a clean
        copy of the image attribute) over the image
        attribute.
        """
        self.image.blit(self.clean_bg, (0, 0))

    def draw_items_on_scroll_area(self):
        """Draw children which collide with scroll area.

        The children are drawn in the self.image surface.
        """
        ## retrieve children to draw (the ones colliding
        ## with the scroll_area)

        children_to_draw = (
            child for child in self.children if self.scroll_area.colliderect(child.rect)
        )

        ### calculate the offset between the origin and the
        ### menu manager (which happens to be the inverse of
        ### self.rect.topleft)
        offset = invert_point(self.rect.topleft, invert_x=True, invert_y=True)

        ### iterate over children, offsetting their rects
        ### non-destructively, so they are drawn suitably
        ### in the surface in the self.image attribute

        for child in children_to_draw:
            self.image.blit(child.image, child.rect.move(offset))

    def draw_arrows(self):
        """Draw arrows on self.image."""
        ### calculate the offset between the origin and the
        ### menu manager (which happens to be the inverse of
        ### self.rect.topleft)
        offset = invert_point(self.rect.topleft, invert_x=True, invert_y=True)

        ### iterate over arrows, offsetting their rects
        ### non-destructively before drawing them on the
        ### surface in the self.image attribute

        for arrow in self.arrows:
            self.image.blit(arrow.image, arrow.rect.move(offset))

    def draw_active_branch(self):
        """Trigger drawing of active branch.

        The drawing of the active branchs works by calling
        the draw_body_and_its_contents method on the active
        menu, which triggers the same method recursively in
        the entire active branch, making it so the menus and
        their expanded bodies with their children are drawn
        one by one.
        """
        self.active_menu.draw_body_and_its_contents()

    def draw_outline(self):
        """Draw outline around self.rect.

        Used when the menu manager instance is initialized
        with the use_outline option set to True (use this
        option for popup menus).
        """
        ### draw the slightly inflated rect of the menu
        ### manager on the screen, so that it works as an
        ### outline

        draw_rect(
            SCREEN,
            BLACK,
            ## XXX in theory, we shouldn't need to move the
            ## rect as well; investigate why this is needed
            ## and explain/fix as needed;
            self.rect.inflate(2, 2).move(1, 0),
            1,
        )

    def handle_input(self):
        """Retrieve data, execute setups and handle events."""
        ### retrieve commonly used data, mouse position,
        ### and store it in a mouse_pos attribute for easy
        ### access by other methods in the class
        self.mouse_pos = get_mouse_pos()

        ### check if there's an arrow hovered and scroll it
        self.manage_scrolling()

        ### check if there's a hovered widget, performing
        ### admin tasks along the way
        self.manage_hovered_widget()

        ### process events from the event queue

        for event in get_events():
            if event.type == QUIT:
                raise QuitAppException

            elif event.type == KEYUP:

                # if released escape key, focus the
                # loop holder

                if event.key == K_ESCAPE:
                    self.focus_loop_holder()

                # otherwise, invoke the hovered widget,
                # if any

                elif event.key in (K_RETURN, K_KP_ENTER):
                    self.invoke_hovered_widget()

            ## mouse

            elif event.type == MOUSEBUTTONUP:

                # left click
                if event.button == 1:
                    self.invoke_hovered_widget()

                # right click

                elif event.button == 3:

                    # if click was out of any meaningful area
                    # focus the loop holder
                    if self.is_clicking_out():
                        self.focus_loop_holder()

                # mouse wheel

                elif event.button in (4, 5):
                    self.mouse_scroll(event.button)

    def highlight_widget_and_parents(self, widget):
        """Highlight widget and its parents recursively.

        widget (either a menu.main.MenuManager or
                menu.submenu.main.Menu or
                menu.Command instance)
        """
        ### highlight the widget
        widget.highlight()

        ### try highlighting its parent
        try:
            self.highlight_widget_and_parents(widget.parent)

        ### this will catch the attribute error when trying
        ### to execute MenuManager.highlight, since the
        ### MenuManager instance is always at the top of the
        ### hierarchy of widgets and it doesn't have a
        ### highlight method
        except AttributeError:
            pass

    def collapse_active_menu(self):
        """Collapse active menu and unhighlight it.

        The active menu is collapsed by resetting the
        active menu variable to None and removing the
        active branch draw method.

        The unhighlight method called on the active menu
        works recursively down the branch when the item is a
        menu.submenu.main.Menu instance.
        """
        ### remove draw active branch method from draw list
        ### (if present)

        try:
            self.draw.remove(self.draw_active_branch)
        except ValueError:
            pass

        ### check existence of unhighlight method
        try:
            method = self.active_menu.unhighlight

        ### if it doesn't exist, just pass, since it means
        ### there's currently no menu active (the active
        ### menu is None)
        except AttributeError:
            pass

        ### otherwise, execute the method and reset the
        ### active menu attribute

        else:

            method()
            self.active_menu = None

    def get_hovered_menu(self, mouse_pos):
        """Return True if the menu manager is hovered.

        mouse_pos (2-tuple of integers)
            represents the current mouse position.

        Meant to be used by external objects, to check
        whether the mouse hovered over the menu manager, in
        order to determine whether to give focus to the it.
        """
        ### if the menu is scrollable, return True if the
        ### menu manager rect is hovered (since in this case
        ### checking the child wouldn't be enough, because
        ### we could be hovering an arrow; also, since it is
        ### scrollable, all the area of the menu manager rect
        ### is filled with widgets, children or arrows, so
        ### checking the area for collision means something
        ### is hovered anyway)
        if self.is_scrollable():
            return self.rect.collidepoint(mouse_pos)

        ### otherwise, check its children (since checking the
        ### rect wouldn't mean a child is hovered: there may
        ### be areas inside the menu rect which have no
        ### children, depending on additional menu parameters
        ### specified when instantiating it; we are only
        ### interested if the mouse hovers a child)
        else:

            # return whether any child was found
            # colliding with the mouse position

            return any(
                child for child in self.children if child.rect.collidepoint(mouse_pos)
            )

    def focus_loop_holder(self):
        """Collapse entire menu and focus loop holder."""
        self.collapse_active_menu()
        raise SwitchLoopException(self.loop_holder)

    def get_top_menu(self, widget):
        """Get top menu of item.

        widget (either a menu.submenu.main.Menu or
                menu.command.Command instance)

        The method goes over the object parent attribute
        recursively until it reaches the widget which is
        the top menu.
        """
        ### if the widget is the top menu, return it
        if self.is_top_menu(widget):
            return widget

        ### otherwise check its parent
        else:
            return self.get_top_menu(widget.parent)

    ### state checks

    def top_menu_is_active(self, widget):
        """Return True if the top menu of widget is active.

        widget (either a menu.submenu.main.Menu or
                menu.command.Command instance)
        """
        ### return whether the top menu of the widget is
        ### the active menu
        return self.get_top_menu(widget) is self.active_menu

    def is_top_menu(self, widget):
        """Return True if widget is a top menu.

        widget (either a menu.submenu.main.Menu or
                menu.command.Command instance)

        A top menu is a widget which has children and whose
        parent is the MenuManager instance (the root of the
        whole menu structure).
        """
        ### evaluate conditions

        a = hasattr(widget, "children")
        b = isinstance(widget.parent, self.__class__)

        ### return True if both conditions are True
        return a and b

    def is_top_command(self, widget):
        """Return True if widget is a top command.

        widget (either a menu.submenu.main.Menu or
                menu.command.Command instance)

        A top command is a widget which has an 'invoke'
        attribute and whose parent is the MenuManager
        instance (the root of the whole menu structure).
        """
        ### evaluate conditions

        a = hasattr(widget, "invoke")
        b = isinstance(widget.parent, self.__class__)

        ### return True if both conditions are True
        return a and b

    def is_drawing_active_branch(self):
        """Return True if there's an active branch.

        Works by checking whether the active branch drawing
        method is present in the call list (an instance of a
        custom list subclass) located in the 'draw' attribute,
        since it means there is an active branch being drawn.
        """
        return self.draw_active_branch in self.draw

    ### positioning related methods

    def reposition_children_bodies(self):
        """Reposition body of all children.

        Works in each child which is a submenu; otherwise an
        attribute error is safely caught and ignored.
        """
        ### iterate over children checking presence of
        ### reposition_body method and executing it if it
        ### is present

        for item in self.children:

            ## store special method
            try:
                method = item.reposition_body

            ## if it doesn't exist, just pass
            except AttributeError:
                pass

            ## otherwise execute it
            else:
                method()

    def translate(self, dx, dy):
        """Move all widget's objects.

        dx, dy (integers)
            represent the distances to translate the widgets
            in the x and y axes, respectively.
        """
        ### move rect and children's rects

        self.rect.move_ip(dx, dy)
        self.children.rect.move_ip(dx, dy)

        ### if scrollable also move the arrows and the
        ### scroll area

        if self.is_scrollable():

            for arrow in self.arrows:
                arrow.rect.move_ip(dx, dy)

            self.scroll_area.move_ip(dx, dy)

    def focus_if_within_boundaries(self, mouse_pos):
        """Check whether to give menu manager focus.

        This method should be used when the menu manager is
        used as a popup menu to determine whether the mouse
        click happened within the boundaries rect defined for
        the existence of the menu, in which case the menu
        is shown.

        mouse_pos (2-tuple of integers)
            represent position of the mouse cursor. It is the
            position to which to warp the menu manager.
        """
        ### if the mouse is inside the boundaries rect,
        ### warp the menu to its position and make the menu
        ### the new loop holder

        if self.boundaries_rect.collidepoint(mouse_pos):

            self.warp(mouse_pos)
            raise SwitchLoopException(self)

    def warp(self, mouse_pos):
        """Warp menu to given position.

        Used for popup menu behaviour, in order for the menu
        manager to appear in the given mouse position.

        mouse_pos (2-tuple of integers)
            represent position of the mouse cursor. It is the
            position to which to warp the menu manager.
        """
        ### retrieve the attribute name of the boundaries
        ### rect's point nearest to the mouse position

        attr_name = get_nearest_attr_name(
            mouse_pos,
            self.boundaries_rect,
        )

        ### now calculate the deltas for the x and y axes
        ### so that the menu manager is warped to the mouse
        ### position with the point in the attribute name
        ### calculated above ending up in the mouse position

        end_x, end_y = mouse_pos
        start_x, start_y = getattr(self.rect, attr_name)

        dx, dy = end_x - start_x, end_y - start_y

        ### admin task: increment dx and dy if the attribute
        ### name used is respectively to the right and/or
        ### to the bottom of the rect
        ### (this is needed because of how rects handle
        ### collision: points in the right or bottom of the
        ### rect are not considered colliding points)

        if "right" in attr_name:
            dx += 1
        if "bottom" in attr_name:
            dy += 1

        ### handle clamping before moving

        ## before moving the menu manager in fact, simulate
        ## the movement by creating a moved copy of its
        ## rect and also simulate the clamping by creating
        ## a copy of the moved rect clamped to the boundaries
        ## rect

        moved_copy = self.rect.move(dx, dy)
        clamped_copy = moved_copy.clamp(self.boundaries_rect)

        ## if the clamped copy ends up positioned differently
        ## from the moved copy, it means our original deltas
        ## need to be adjusted so that when we move the menu
        ## in fact we already land in a clamped position

        if moved_copy != clamped_copy:

            end_x, end_y = clamped_copy.topleft
            start_x, start_y = self.rect.topleft

            dx, dy = end_x - start_x, end_y - start_y

        ### now that the deltas were properly calculate and,
        ### if it was needed, we also adjusted the clamping,
        ### we can finally translate the menu manager
        self.translate(dx, dy)

        ### we also reposition the contents of the menu
        ### manager inside the pygame.Rect stored in its
        ### 'rect' attribute
        self.reposition_menu_manager_contents()

    def reposition_menu_manager_contents(self):
        """Reposition menu manager contents inside rect.

        Used more often when warping to reposition menu
        manager items inside the menu manager self.rect
        (for popup menus), but also used in the
        build_scrolling_objects method to reposition the menu
        contents after creating the new scrolling objects.
        """
        ### get topleft coordinates of the rect, with a
        ### small offset

        offset = 1, 0
        topleft = self.rect.move(offset).topleft

        ### if scrollable, position arrows and scroll area
        ### depending on menu manager initial orientation
        ### and update the topleft coordinate to be used
        ### when repositioning the children

        if self.is_scrollable():

            ## position arrows and scroll area depending
            ## on whether menu manager is used as a
            ## menubar or not

            if self.is_menubar:

                self.left_arrow.rect.topleft = topleft

                self.scroll_area.topleft = self.left_arrow.rect.topright

                self.right_arrow.rect.topleft = self.scroll_area.topright

            else:

                self.up_arrow.rect.topleft = topleft

                self.scroll_area.topleft = self.up_arrow.rect.bottomleft

                self.down_arrow.rect.topleft = self.scroll_area.bottomleft

            ## update topleft to be used to position children
            topleft = self.scroll_area.topleft

        ### position the children, updating the topleft
        ### position of each children depending on the
        ### initial orientation of the menu manager

        ## first define the attribute name whose position
        ## is used to update the topleft coordinates of each
        ## subsequent children, according to whether the
        ## menu manager is used as a menubar or not

        if self.is_menubar:

            # children will be positioned side by side
            attr_name = "topright"

        else:

            # children will be positioned on top of each
            # other
            attr_name = "bottomleft"

        ## finally iterate over each children assigning
        ## its topleft position and them updating it for
        ## the next child

        for child in self.children:

            ## assign topleft
            child.rect.topleft = topleft

            ## update topleft
            topleft = getattr(child.rect, attr_name)

    def enter(self):
        """Update surface maps of commands.

        Such commands are those which work as widgets
        (checkbuttons or radiobuttons).
        """
        ### cache the contents of the screen
        cache_screen_state()

        ### reset variable to keep track of when the
        ### user clicked a top menu to expand it
        self.was_top_menu_expanded = False

        for method in yield_tree_attrs(
            self, "surface_map_updating_routine", "children"
        ):
            method()
