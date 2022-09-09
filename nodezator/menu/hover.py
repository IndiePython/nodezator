"""Facility for menu manager hovering methods extension."""

### local imports

from ..loopman.exception import SwitchLoopException

from ..logman.main import get_new_logger


### create logger for module
logger = get_new_logger(__name__)


### class definition


class HoveringOperations:
    """Hovering-related methods."""

    def manage_hovered_widget(self):
        """Verify whether a menu item is being hovered.

        Performs administrative tasks depending on whether
        or not a hovered widget was found, which kind of
        widget it is and other specific details.
        """
        ### return the hovered widget or None (if none was
        ### found)
        hovered = self.get_hovered_widget()

        ### before going on, also store the hovered
        ### variable in an attribute for reference
        ### outside this method
        self.hovered_widget = hovered

        ### admin tasks in case there's a hovered widget

        if hovered:

            ## evaluate conditions

            is_top_command = self.is_top_command(hovered)
            is_top_menu = self.is_top_menu(hovered)

            ## if an active branch is being drawn, perform
            ## special tasks based on additional conditions

            if self.is_drawing_active_branch():

                # if item is a top command, we are only
                # interested in collapsing the active
                # branch

                if is_top_command:

                    self.active_menu = None
                    self.draw.remove(self.draw_active_branch)

                # if item is a top menu, we turn it into
                # the active menu

                elif is_top_menu:
                    self.active_menu = hovered

            ## otherwise, we start doing so if we have
            ## a top menu and a top menu was expanded
            ## before

            elif is_top_menu and self.was_top_menu_expanded:

                self.active_menu = hovered

                (
                    self.draw.insert(
                        -1,
                        self.draw_active_branch,
                    )
                )

            # if the widget is on top, regardless of it
            # being a command or a menu, unhighlight all
            # other top items

            if is_top_menu or is_top_command:

                for child in self.children:

                    if child is not hovered:
                        child.unhighlight()

            ## finally, since a hovered widget was found,
            ## we highlight it along with its parents in the
            ## active branch
            self.highlight_widget_and_parents(hovered)

        ### admin tasks in case there's no hovered widget

        ## if there isn't a hovered_arrow, there's no
        ## active branch and the keep_focus_when_unhovered
        ## attribute is set to False, then the menu manager
        ## must loose its focus to the loop holder (in
        ## other words, the user isn't hovering any visible
        ## element of the menu manager and there's no
        ## expanded menu); notice that by requiring the
        ## absence of an active branch to loose focus we are
        ## ensuring that the user can freely maneuver the
        ## mouse cursor when there's an active branch
        ## without causing the menu manager to loose focus
        ## (it is an usability choice);
        ## the value of the keep_focus_when_unhovered is
        ## also an usability choice made upon instantiation
        ## (for more information check the parameter
        ## description in the __init__ method docstring)

        elif (
            not self.is_drawing_active_branch()
            and not self.hovered_arrow
            and not self.keep_focus_when_unhovered
        ):
            self.focus_loop_holder()

        ## if no active branch exists, but there's an
        ## arrow hovered, unhighlight the active menu

        elif not self.is_drawing_active_branch() and self.hovered_arrow:
            self.collapse_active_menu()

    def get_hovered_widget(self):
        """Return either the last widget hovered or None."""
        ### get all hovered widgets
        hovered_widgets = self.gather_hovered(self, [])

        ### retrieve the last one
        try:
            hovered = hovered_widgets[-1]

        ### if there isn't a last one, then there's no
        ### hovered widget, so we assign None to the variable
        except IndexError:
            hovered = None

        ### finally return the object stored in hovered
        return hovered

    def gather_hovered(self, menu, hovered_widgets):
        """Gather all menu items over which the mouse hovers.

        menu (either a menu.main.MenuManager instance or a
              menu.submenu.main.Menu instance)
            contains children which are either Menu instances
            and/or menu.command.Command instances.
        hovered_widgets (list)
            list of hovered widgets found so far, which is
            updated recursively as we travel through the
            active branch. The way we travel the branch and
            update the list makes it so the contents are
            always sorted from the widgets nearest to the
            MenuManager instance (root) to the ones farthest
            from it. This ordering is intended and needed
            for the use for which this list was designed.
            The list might be empty if no hovered widget
            was found.

        As an additional administrative task, we unhighlight
        widgets over which the mouse doesn't hover, as long
        as they are not expanded.

        The pygame.Rect from the 'rect' attribute of the
        menu is used for the collision. Collision with the
        pygame.Rect stored in the 'body' attribute is also
        checked in some circunstance to handle admin tasks.
        """
        ### alias mouse position
        mouse_pos = self.mouse_pos

        ### create an 'expanded_child' variable to hold
        ### the expanded child of the menu if we detect
        ### one while iterating
        expanded_child = None

        ### also create a flag to determine whether any of
        ### the children have collided with the mouse
        any_child_collided = 0

        ### iterate over the children, checking if they are
        ### hovered or not and performing setups and admin
        ### tasks as needed

        for child in menu.children:

            ## evaluate conditions

            is_top_command = self.is_top_command(child)
            is_top_menu = self.is_top_menu(child)

            collided = child.rect.collidepoint(mouse_pos)

            try:
                is_expanded = child.is_expanded
            except AttributeError:
                is_expanded = False

            ## disregard collision if the menu is scrollable
            ## and the mouse doesn't hover the scroll area

            if menu.is_scrollable() and not menu.scroll_area.collidepoint(mouse_pos):
                collided = 0

            ## admin task: update flag
            any_child_collided = max(any_child_collided, collided)

            ## if a collision was detected, check the
            ## preliminary conditions for the widget to be
            ## added to the hovered widget list

            if collided:

                # if the widget is either a top command or
                # a top menu or, in case it is neither, its
                # top menu is active and its direct parent
                # is expanded we append the child to the
                # list of hovered widgets

                if (
                    is_top_command
                    or is_top_menu
                    or (self.top_menu_is_active(child) and child.parent.is_expanded)
                ):
                    hovered_widgets.append(child)

            ## if no collision was detected, though, just
            ## unhighlight the child if it is not expanded
            ## (admin task)

            else:

                if not is_expanded:
                    child.unhighlight()

            ## regardless of whether the child is hovered
            ## by the mouse or not, if it is expanded,
            ## store a reference to it
            if is_expanded:
                expanded_child = child

        ### extra measure in case no collision is detected
        ### for any child

        if not any_child_collided:

            ## in case we the menu is not self (that is,
            ## not the MenuManager instance) we check the
            ## rect in the menu's body for collision and if
            ## there's one, we consider the menu itself as
            ## the hovered widget;
            ##
            ## this is to prevent a submenu to loose focus
            ## to the one behind it when hovering only arrows
            ## (since the arrows are not checked for
            ## collision here);
            ##
            ## thus, even if no child is hovered by the
            ## mouse, as long as the cursor is in the body
            ## of the menu, the menu is kept expanded;

            if menu is not self:

                if menu.body.rect.collidepoint(mouse_pos):
                    hovered_widgets.append(menu)

        ### now we treat the expanded_child object if there
        ### is one; here we further check the children of the
        ### expanded child recursively for hovered widgets,
        ### extending the hovered_widgets variable with the
        ### return value (which might or not be an empty
        ### list)

        if expanded_child:

            hovered_on_child = self.gather_hovered(expanded_child, [])
            hovered_widgets.extend(hovered_on_child)

        ### finally return the hovered widgets list
        return hovered_widgets

    def invoke_hovered_widget(self):
        """Invoke widget over which the mouse hovers, if any.

        Administrative tasks are also performed depending on
        the type of the hovered widget and other specific
        details.
        """
        ### try retrieving the invoke method of the hovered
        ### widget
        try:
            method = self.hovered_widget.invoke

        ### this attribute error will be triggered by either
        ### of the following scenarios:
        ### 1) there's no 'invoke' method
        ### 2) the hovered_widget attribute is None, it also
        ###    doesn't have a 'invoke' method
        ### in any of these cases, perform extra checks to
        ### determine what to do

        except AttributeError:

            ## if the hovered widget exists, check if the
            ## hovered widget is a top menu, in which case
            ## make it the active menu and perform other
            ## extra tasks

            if self.hovered_widget:

                if self.is_top_menu(self.hovered_widget):

                    self.active_menu = self.hovered_widget

                    # although the hovered widget would
                    # have its body automatically
                    # repositioned anyway, when visiting
                    # the 'manage_hovered_widget', such
                    # visit would happen only in the next
                    # loop, after executing the 'draw'
                    # method, which would draw the body
                    # even if it wasn't in the right
                    # position;
                    #
                    # to prevent this, we reposition the
                    # body in advance here
                    self.hovered_widget.reposition_body()

                    # if drawing the active branch, we
                    # stop doing so and collapse it
                    #
                    # we also update a related control
                    # variable

                    if self.is_drawing_active_branch():

                        self.active_menu = None

                        self.draw.remove(self.draw_active_branch)

                        (self.hovered_widget.collapse_self_and_children())

                        self.was_top_menu_expanded = False

                    # otherwise we start doing so by
                    # inserting the active branch drawing
                    # method in the drawing list (insert it
                    # just before the last item)
                    #
                    # we also update a related control
                    # variable

                    else:

                        (
                            self.draw.insert(
                                -1,
                                self.draw_active_branch,
                            )
                        )

                        self.was_top_menu_expanded = True

            ## otherwise, if click was out of any meaningful
            ## area, focus the loop holder

            elif self.is_clicking_out():
                self.focus_loop_holder()

        ### if however, the method exists, try executing
        ### it, performing extra administrative tasks

        else:

            ### first of all, log the call we are about
            ### to attemp

            logger.info(
                "About to invoke menu command: "
                + self.hovered_widget.get_formatted_tree()
            )

            ### try executing the method
            try:
                method()

            ### if a manager switch exception is raised,
            ### it means we are about to give control of
            ### the application loop to another object,
            ### so we collapse the active menu tree and
            ### reraise the exception so it is caught
            ### and handled elsewhere

            except SwitchLoopException:

                self.collapse_active_menu()
                raise  # reraises the SwitchLoopException

            ### otherwise we just give focus back to
            ### the loop holder saved in this menu
            ### (this also causes the active menu tree
            ### to be collapsed)
            else:
                self.focus_loop_holder()

    def is_clicking_out(self):
        """Return True if mouse is out of any meaningful area.

        Used in conditional statements to decide whether to
        make the menu manager loose focus to the update
        manager.

        Evaluates the absence of multiple conditions
        previously checked in other methods to determine
        if the position of the mouse (retrieved in the
        'handle_input' method) really is outside any meaningful
        area related to the menu manager.

        This is the logic used:

        if there is no self.hovered_widget (it is None) and
        there's no arrow hovered, it means the user clicked
        out of the menu widgets with the intention of having
        the menu manager loose its focus.
        """
        return not self.hovered_widget and not self.hovered_arrow
