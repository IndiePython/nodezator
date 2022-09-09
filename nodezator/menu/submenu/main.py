"""Facility for managing widgets for menubar."""

### local imports

from ...ourstdlibs.behaviour import empty_function

from ...surfsman.draw import draw_depth_finish
from ...surfsman.render import render_rect

from ...classes2d.single import Object2D
from ...classes2d.collections import List2D

from ...colorsman.colors import MENU_BG, MENU_HOVERED_BG

## class for composition
from ..command import Command

## class extension
from .scroll import MenuScrolling

## utility for surface creation
from ..surffactory import create_equal_surfaces

## utilities
from .utils import is_top_menu, get_boundaries


### XXX instead of creating the labels twice (once upon
### instantiation and again when adjusting the size),
### we could use textman.render.get_text_size() to
### calculate this beforehand and pass the value to the
### constructor of each child


### XXX consider removing the excessive self.children
### attribute error catching blocks, since from the
### beginning the menus are only supposed to be
### instantiated if they have children, so there's no
### point in checking again after every object is
### instantiated and the application is already running
###
### edit: there might be a reason for not assuming the
### children exist right away, though, so check such
### possibility before performing any changes;

### XXX there's so many calculations which are performed
### for each menu unnecessarilly instead of being
### performed only once (like the ones involving the font
### size for the arrows); eliminate those inneficiencies;


class Menu(Object2D, MenuScrolling):
    """Menu object for the menu.main.MenuManager class.

    It can have other menus (instances of its own class and/
    or commands as children. A menu always has a 'parent'
    attribute, which is either other menu or the
    menu.main.MenuManager class, in which case it is said to
    be a top menu.
    """

    def __init__(
        self,
        parent,
        data,
        surface_map,
    ):
        """Store variables and perform setups.

        parent (instance of menu.main.MenuManager class or
                this Menu class)
            object regarded as the parent of this Menu
            instance.
        label_text (string)
            used to generate the text surface for the menu.
        children_data (list of dicts)
            data used to describe children of this menu
            (commands and/or other menus) for instantiation.
        """
        ### store variables

        self.parent = parent
        self.label_text = data["label"]
        self.surface_map = surface_map

        ### reference the normal surface as the 'image'
        ### attribute of this menu instance and also
        ### obtain a rect from it
        ### create 'image' and 'rect' attributes

        self.image = self.surface_map["normal"]
        self.rect = self.image.get_rect()

        ### assign default expanded state
        self.is_expanded = False

        ###
        surface_maps = create_equal_surfaces(data["children"])

        ### instantiate children recursively

        self.instantiate_children(
            data["children"],
            surface_maps,
        )

        ### create and position 'body' object

        body_rect = self.children.rect.inflate(2, 2)

        self.body = Object2D.from_surface(
            surface=(
                render_rect(
                    *body_rect.size,
                    MENU_BG,
                )
            ),
            coordinates_name="topleft",
            coordinates_value=body_rect.topleft,
        )

        draw_depth_finish(self.body.image)

    def instantiate_children(
        self,
        children_data,
        surface_maps,
    ):
        """Instantiate each child using children data.

        children_data (list of dicts)
            data used to describe children of this menu
            (commands and/or other menus) for instantiation.
        """
        children = self.children = List2D()

        for child_data, surface_map in zip(children_data, surface_maps):

            ### check existence of children data inside
            ### the child data
            try:
                child_data["children"]

            ### if there's no grandchildren, then the data
            ### describes a command, so instantiate a
            ### command widget

            except KeyError:

                ## instantiate command widget
                widget = Command(
                    self,
                    child_data,
                    surface_map,
                )

            ### if otherwise, there is children referenced in
            ### the data, then we are dealing with a menu,
            ### so instantiate it, passing along the
            ### its children data (grandchildren)

            else:

                ## instantiate menu widget
                widget = Menu(
                    self,
                    child_data,
                    surface_map,
                )

            ### append the widget
            children.append(widget)

        ### finally, position children relative to this
        ### menu and relative to each other

        ## assign topleft

        children.rect.topleft = (
            # if parent is menu.MenuManager, laid
            # horizontally, align the topleft of the new
            # child with the bottomleft of the pygame.Rect
            # instance in the 'rect' attribute
            self.rect.bottomleft
            if is_top_menu(self) and self.parent.is_menubar
            # all other scenarios demand that the topleft of
            # the new child should be aligned with the
            # topright of the pygame.Rect instance in the
            # 'rect' attribute
            else self.rect.topright
        )

        ## position relative to each other

        children.rect.snap_rects_ip(
            retrieve_pos_from="bottomleft", assign_pos_to="topleft"
        )

    def perform_extra_setups(self):
        """Perform specific checks/setups recursively.

        This method is called recursively from the menu
        manager instance __init__ method to setup all
        submenus recursively. It only needs to be called
        once.
        """
        ### check need to make children scrollable according
        ### to whether or not they trespass the boundaries
        self.check_scrollability()

        ### manage scrollability and behaviours on
        ### children recursively
        self.check_clean_bg()

        ### define behaviours depending on scrollability or
        ### lack thereof
        self.define_behaviours()

        ### execute this method on the each child, if it has
        ### such method (this cause the method to execute
        ### recursively until the last item in the branch)

        for child in self.children:

            try:
                method = child.perform_extra_setups
            except AttributeError:
                pass
            else:
                method()

    def define_behaviours(self):
        """Define behaviours depending on scrollability."""
        ### assign specialized methods for body and children
        ### drawing and also for children repositioning based
        ### on whether this menu instance is scrollable

        if self.is_scrollable():

            ## assign a body and children drawing method
            ## with a scrollable interface
            self.draw_body_and_its_contents = self.draw_scrollable_contents

            ## assign a body contents repositioning method
            ## with a scrollable interface
            self.reposition_body_contents = self.reposition_scrollable_contents

        else:

            ## assign a body and children drawing method
            ## without a scrollable interface
            self.draw_body_and_its_contents = self.draw_body_and_children

            ## assign a body contents repositioning method
            ## without a scrollable interface (only the
            ## children need repositioning)
            self.reposition_body_contents = self.reposition_children

    def draw_body_and_children(self):
        """Draw body and children.

        Used when there's no objects for scrolling support
        to be drawn, just the body itself and the children.
        """
        ### draw the body object first; it serves as a common
        ### background for all children
        self.body.draw()

        ### now you'll iterate over the children
        ### drawing all of them, except if it is
        ### expanded, in which case it will be stored
        ### so it can be drawn last

        ## create variable to hold expanded child if it is
        ## found
        expanded_child = None

        for child in self.children:

            ## draw the child
            child.draw()

            ## if child is_expanded attribute is True,
            ## store it

            try:

                if child.is_expanded:
                    expanded_child = child

            ## it might be however, that it doesn't even
            ## have an 'is_expanded' attribute (if it is a
            ## command), in which case just pass
            except AttributeError:
                pass

        ### now we check if we stored an expanded child;
        ### if so, we call its draw_body_and_its_contents
        ### method; we saved it for last because by
        ### being drawn last there's no way for its
        ### siblings to be drawn over its children in the
        ### screen; it is an aesthetic/usability measure,
        ### making the behaviour more intuitive for the user;

        if expanded_child:
            expanded_child.draw_body_and_its_contents()

    def highlight(self):
        """Change image to highlighted surface and expand."""
        self.image = self.surface_map["highlighted"]
        self.expand()

    def unhighlight(self):
        """Change image to normal surface and collapse."""
        self.image = self.surface_map["normal"]
        self.collapse_self_and_children()

    def expand(self):
        """Collapse sibling menus then expand self."""
        ### if the parent has an 'active_menu' attribute
        ### which is False, cancel execution of the rest
        ### of the method by returning earlier
        ###
        ### in other words, returning here means that
        ### this menu is a top menu but there's no active
        ### menu, which means it mustn't expand at all

        try:
            if not self.parent.active_menu:
                return
        except AttributeError:
            pass

        ### admin task: if the 'is_expanded' attribute is
        ### set to False, reposition the body to ensure it
        ### is properly positioned within the boundaries
        if not self.is_expanded:
            self.reposition_body()

        ### collapse every sibling menu and self

        for child in self.parent.children:

            if isinstance(child, self.__class__):
                child.is_expanded = False

        ### expand self
        self.is_expanded = True

    def collapse_self_and_children(self):
        """Collapse self and children menus."""
        self.is_expanded = False
        for child in self.children:
            child.unhighlight()

    def reposition_body(self):
        """Position body near self.rect."""
        ### define the topleft coordinates for the body rect
        ### (notice a little offset is always applied as a
        ### minor usability measure to always keep the menu
        ### body slightly in front of the menu label)

        ## if this instance is a top menu (parent is
        ## menu.MenuManager), the menu manager is used as
        ## a menubar and the extra conditions defined on
        ## the body_fits_below method are satisfied, assign
        ## the slightly offset self.rect bottomleft
        ## coordinates to be used as the new topleft of the
        ## body rect, making it so the body is positioned
        ## below the self.rect;

        if is_top_menu(self) and self.parent.is_menubar and self.body_fits_below():
            topleft = self.rect.move(0, -1).bottomleft

        ## otherwise assign the slightly offset self.rect
        ## topright coordinates to be used as the new topleft
        ## of the body rect, making it so the body is
        ## positioned to the right of the self.rect;
        else:
            topleft = self.rect.move(-1, 0).topright

        ### reposition the body using the coordinates
        ### retrieved
        self.body.rect.topleft = topleft

        ### even with the body positioned where we want it,
        ### nothing guarantees the body is within the
        ### boundaries (any rect passed to the menu manager
        ### boundaries_rect parameter, default to the screen
        ### rect), so we clamp the body to such boundaries to
        ### ensure it is inside it
        self.clamp_body()

        ### finally, since the previous operations might
        ### change the body original position, we reposition
        ### its contents inside it
        self.reposition_body_contents()

    def body_fits_below(self):
        """Return True if we can fit the body below self.rect.

        To be able to fit the body below the self.rect, two
        conditions must be met:

        1) the body must fit in the space between the bottom
           of the pygame.Rect in the 'rect' attribute and the
           bottom of the boundaries rect; that is, if the
           difference between bottom of 'rect' and bottom
           of boundaries is equal or greater than the
           body's height.
        2) there must be enough space between the left side of
           the rect in the 'rect' attribute and the right
           side of the boundaries rect to fit the body;
           that is, if the difference between the
           boundaries right coordinate and the left
           coordinate of the pygame.Rect in the 'rect'
           attribute is equal or greater than the body's
           width.
        """
        ### retrieve coordinates needed to calculate
        ### conditions from the menu 'rect' attribute and
        ### from the body rect;
        ### notice the body height is reduced by one pixel,
        ### to compensate for the offset by one pixel which
        ### is always applied when the body is laid below the
        ### menu 'rect' as an usability measure

        rect_bottom = self.rect.bottom
        rect_left = self.rect.left

        body_height = self.body.rect.height - 1
        body_width = self.body.rect.width

        ### fetch boundaries rect from menu manager and
        ### retrieve needed coordinates from it

        boundaries_rect = get_boundaries(self)

        boundaries_bottom = boundaries_rect.bottom
        boundaries_right = boundaries_rect.right

        ### calculate conditions

        ## calculate whether the difference between the
        ## bottom of 'rect' and the bottom of the boundaries
        ## rect is equal or greater than the body height
        condition_a = boundaries_bottom - rect_bottom >= body_height

        ## calculate whether there's enough space between
        ## the left side of the rect in the 'rect' attribute
        ## and the right side of the boundaries rect to fit
        ## the body.
        condition_b = boundaries_right - rect_left >= body_width

        ### return whether both conditions are met or not
        return condition_a and condition_b

    def reposition_children(self):
        """Reposition children inside body.

        Used to reposition contents of the body inside it
        when the only contents are the children themselves
        (there are no arrows nor a scroll area).
        """
        self.children.rect.topleft = self.body.rect.move(1, 1).topleft

        self.children.rect.snap_rects_ip(
            retrieve_pos_from="bottomleft", assign_pos_to="topleft"
        )

    def clamp_body(self):
        """Clamp body to the boundaries rect.

        The pygame.Rect.clamp_ip method ensures that a
        pygame.Rect instance is inside another one by moving
        it if needed. Here we use it to ensure the body of
        the menu is inside the boundaries rect.

        Extreme case: if the body of the menu is larger than
        the boundaries the clamp operation aligns the center
        of the menu body with the center of the boundaries.

        This is not the intended behaviour, but the way the
        clamp_ip method of the pygame.Rect class naturally
        deals with this kind of problem and is kept since it
        is the most reasonable behaviour for this situation.

        This extreme case however only happens when you use a
        font size extremely big and most likely unreasonable,
        font sizes, so this clamping feature is safe for
        everyday usage. For additional information about
        font sizes and clamping, check the docstring of the
        menu/common.py module.
        """
        ### fetch boundaries rect from the menu manager
        boundaries_rect = get_boundaries(self)

        ### store the left and topleft of the body
        left, _ = topleft = self.body.rect.topleft

        ### clamp the body
        self.body.rect.clamp_ip(boundaries_rect)

        ### if the body's position didn't change, cancel the
        ### execution of the rest of the method by returning
        ### early since no extra adjustments are needed
        if self.body.rect.topleft == topleft:
            return

        ### if the body is to the left of its original
        ### position, though, perform extra adjustements

        if self.body.rect.left < left:

            ### align its right coordinate to the left
            ### coordinate of the pygame.Rect instance in the
            ### 'rect' attribute
            self.body.rect.right = self.rect.left

            ### admin task: offset body just a bit to the
            ### right; this is to keep the symmetry between
            ### menus laying on left and menus laying on the
            ### right side of the rect in the 'rect'
            ### attribute, since menus laying on the right
            ### side also are also moved one pixel in the
            ### opposite direction in the reposition_body
            ### method; this is a minor usability measure to
            ### keep expanded menu's bodies just a bit in
            ### front of the menu label
            self.body.rect.move_ip(1, 0)

            ### finally clamp the body again just to be sure
            ### the moving operation above didn't bring it
            ### outside the boundaries rect again
            self.body.rect.clamp_ip(boundaries_rect)

    def __repr__(self):
        """Return nearest unambiguous string representation.

        Since the menu object is too complex to have its
        instantiation call or contents faithfully
        communicated through a string representation, we
        stick to returning the menu label and the string
        representation of each child.

        Overrides object.__repr__.
        """
        ### define a base text
        base_text = 'Menu "{}"'

        ### add the number of direct children
        base_text += " ({} direct children)".format(len(self.children))

        ### change the base text to indicate the menu is
        ### scrollable if it is the case
        if self.is_scrollable():
            base_text += " (scrollable)"

        ### finally return the base text plus each children
        ### string representation, separated by a new line
        ### character plus double dashes '--' multiplied
        ### by the number of parents until the top (the
        ### height of the menu branch)

        ## build the separator string

        # calculate height

        widget = self
        height = 0

        while True:

            try:
                parent = widget.parent

            except AttributeError:
                break

            else:

                height += 1
                widget = parent

        # use height to concatenate the separator
        sep = "\n" + "--" * height

        ## return the string representation
        return sep.join([base_text.format(self.label_text), *map(repr, self.children)])
