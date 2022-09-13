"""Facility for menu manager (menubar and popup menus)."""

### third-party import
from pygame import Rect


### local imports

from ..pygameconstants import SCREEN_RECT

from ..ourstdlibs.behaviour import empty_function

from ..classes2d.collections import List2D

from ..surfsman.cache import (
    RECT_SURF_MAP,
    draw_cached_screen_state,
)

from ..colorsman.colors import MENU_BG

## class extensions

from .behaviour import BehaviourDefinitions
from .hover import HoveringOperations
from .scroll import Scrollability

## classes for composition

from .command import Command
from .submenu.main import Menu

## surface factory utility

from .surffactory import (
    create_top_surfaces,
    create_equal_surfaces,
)

# XXX whenever convenient, implement new changes in
# menu subpackage on other packages, since this is the
# most complete and further developed version;

### XXX small bug on popup submenus: try 'summoning' a
### pop up menu in a spot on the screen, then get out of it
### using the mouse right click instead of the left click
### and then summon it again using the right click!
### A submenu of the popup menu will appear in the previous
### spot it was (that is, it seems its as if its position
### isn't updated);
###
### in other words, it seems I must not only update the
### position of the menu when summoning it, but also of the
### submenus as well; at least that's what it seems to be
### the problem; investigate;


### XXX because of how the body of the menu may have an
### outline and the body of submenus all have a depth
### finish, the left/up arrows are positioned with a
### small offset so the arrow isn't blitted over such
### outline/finish; however, the scrollable items of the
### menu sometimes are blitted over it, depending on their
### position; this is neither urgent nor really much
### incovenient, however, after other higher priority
### tasks are performed, schedule time to solve this;


class MenuManager(
    BehaviourDefinitions,
    HoveringOperations,
    Scrollability,
):
    """Manages menus, their its items and subitems.

    This class, along with the classes used for composition
    (Menu and Command) were design to work together to
    reproduce a behaviour similar to the one observed in
    tkinter.Menu widgets.

    The menu manager works as a container for other
    menu-like items and/or their subitems. Such items and
    subitems consist of (sub)menus and commands.

    The menu manager structure, is a tree-like structure,
    which starts with the MenuManager instance as the
    root and always end up in a command. We present
    a visual representation of this tree-like structure
    in a comment just after this class docstring
    (because keeping the backslash character at the
    end of a line inside a docstring causes the
    black formatter to fail).

    As can be seen in the visual representation, the
    MenuManager object can have both menu.submenu.main.Menu
    and menu.command.Command objects directly attached
    to it. Menu objects, on the other hand, can have other
    menus attached to them, or a command object.

    However, if you aim to use the menu manager as a
    menubar, don't add commands directly to it, but first
    attach Menu objects and only them put commands on them.
    There's no technical need to do so, it is just an
    usability measure, because it seems users expects the
    words on a menubar to refer to submenus, not commands
    (for instance: file menu, edit menu, which people
    expect to have commands and submenus under them, not
    for themselves to be commands).

    However, the ability to have commands added directly
    under the menu manager has a purpose: do so if you
    intended to use the menu manager as a popup menu.
    In that case, the user won't have a problem with popup
    menus having commands on them, because that's pretty
    usual for popup menus.

    If a widget has other widgets attached to it, then those
    widgets are considered its children, and are stored in
    the 'children' attribute. This is true for both the
    MenuManager and the Menu classes.

    Each widget also has a 'parent' attribute wherein they
    store a reference to its parent widget, except for the
    menu.main.MenuManager instance, since it works like a
    root for the structure, being the highest parent.

    A menu or command whose parent is the MenuManager
    (instead of other menu object) is called a top item
    (also a top menu or top command, depending on its type).

    When the mouse hovers of a top menu and left-click, its
    children become visible and we say that the menu is
    expanded. Before that, when no child of a top menu is
    visible, we say that the top menu is collapsed.

    The default behaviour is for all the top menus to be
    collapsed. Once a top menu is expanded, all submenus
    which are hovered automatically expand, without the
    need to left-clicking them.

    The branch or hierarchy of the top menu and all its
    items and subitems until the last expanded menu is
    called the active branch.

    Only the children, grandchildren, etc. of a single top
    menu can be visible at a time, that is, only one top menu
    is expanded at a time, while all the others are collapsed.

    Of course, all this expanded/collapsed discusion doesn't
    apply to commands, since the concepts don't apply to
    them, since they don't have children.

    In the future other widgets may be added, possibly as
    subclasses of Command:

    1) a checkbutton menu item whose invocation toggles a
       boolean (and changes its surface to show whether the
       boolean is toggled or not).
    2) a separator widget should be added, too, for better
       layout/aesthetics/usability. Such separator would
       probably be just a widget like Command but with no
       effects nor highlighted surfaces just the surface of
       a line with a slight depth.

    Commands should also be further developed in the future
    to have a normal/disabled states, which should probably
    be controlled by a custom callable passed to them which
    returns a boolean.
    """

    ### visual representation of MenuManager tree-like
    ### structure:
    ###
    ###
    ###         Menu - Menu - Command
    ###        /
    ###    MenuManager - Menu - [...] - Command
    ###        \
    ###         Command
    ###
    ###    For instance:
    ###
    ###         File (menu)
    ###         /    > Open (command)
    ###        /     > Open recent... (menu)
    ###       /      > Close (command)  |
    ###      /                          |
    ###    MenuManager                   > Open file 01 (command)
    ###       \   \                      > Open file 02 (command)
    ###        \   \
    ###         \   Edit (menu) > Preferences (command)
    ###          \
    ###           Undo (command)

    def __init__(
        self,
        menu_list,
        loop_holder=None,
        draw_behind=draw_cached_screen_state,
        boundaries_rect=SCREEN_RECT,
        coordinates_name="topleft",
        coordinates_value=(0, 0),
        is_menubar=True,
        horiz_bg_width=0,
        vertical_bg_height=0,
        use_outline=False,
        keep_focus_when_unhovered=False,
    ):
        """Assign variables and perform setups.

        Parameters
        ==========

        menu_list (list of dicts)
            contains data about menu manager items. Each dict
            in the list represents an item which can be a
            command or a submenu with more items.

        loop_holder (any python object with handle_input,
            update and draw methods)
            the loop holder related to this instance, the
            one to which the menu manager should give focus
            once it gets out of focus itself.

        draw_behind (callable)
            callable used to draw objects behind the menu.
            Defaults to a function which draws a cached
            copy of the screen over the screen.

        boundaries_rect (pygame.Rect instance)
            provides a limit which should be respected by
            the menu.

        coordinates_name (string)
            represents an attribute name of a pygame.Rect
            instance wherein to store the position
            information from the coordinates value parameter.

        coordinates_value (2-tuple/list of integers)
            position information in the form of a tuple or
            list containing integers representing the
            coordinates in the x and y axes, respectively.

        is_menubar (bool)
            Defines whether the top menus should be side by
            side (True) or on top of each other (False).
            In other words, this defines whether the menu
            manager is being used as a menubar or as a
            context menu. All the children submenus and so
            on are always on top of each other, regardless
            of the value of this argument.

        horiz_bg_width (integer; defaults to 0)
            width of background. If 0, will use sum of
            children's widths. Can never be bigger than the
            screen's width. Only relevant if is_menubar
            == True. Also, only affects the menu manager,
            since the regular menus always respect only
            the boundaries_rect provided.

        vertical_bg_height (integer; defaults to 0)
            height of background. If 0, will use sum of
            children's heights. Can never be bigger than
            the screen's height. Only relevant if menu
            manager is not a menubar. Also, only affects
            the menu manager, since the regular menus
            always respect only the boundaries_rect
            provided.

        use_outline (boolean, defaults to False)
            if True, an outline is drawn using the rect
            attribute every loop. Use this when making a
            popup menu, to make constrast between the menu
            manager and what is behind it.

        keep_focus_when_unhovered
        (boolean, defaults to False)
            defines whether to keep the focus when the
            mouse isn't hovering any meaning object in the
            menu manager and there's no active branch.
            It should be set to True only when using the
            menu as a popup menu, for improved usability.
        """
        ### check condition, if a menubar is being created,
        ### its top items must all be submenus;

        if is_menubar and any("children" not in item for item in menu_list):
            raise ValueError(
                "all top items in a menubar"
                " (when is_menubar == True) must be"
                " submenus"
            )

        ### store arguments

        self.loop_holder = loop_holder
        self.draw_behind = draw_behind
        self.boundaries_rect = boundaries_rect
        self.is_menubar = is_menubar
        self.use_outline = use_outline

        self.keep_focus_when_unhovered = keep_focus_when_unhovered

        ### assign an empty update operation to the
        ### instance, since it is a loop holder
        self.update = empty_function

        ### instantiate rect
        self.rect = Rect((0, 0), (0, 0))

        ### process data in the menu list using appropriate
        ### function to create surfaces for the menu
        ### elements

        surface_maps = (create_top_surfaces if is_menubar else create_equal_surfaces)(
            menu_list
        )

        ### process the data in the menu list to instantiate
        ### children widgets
        self.instantiate_children(menu_list, surface_maps)

        ### calculate the maximum dimensions for the
        ### menu according to whether it is a menubar

        if is_menubar:

            ## if not provided, use children width as
            ## horiz_bg_width

            if not horiz_bg_width:
                horiz_bg_width = self.children.rect.width

            ## restrain horiz_bg_width to boundaries width

            self.max_width = min(horiz_bg_width, self.boundaries_rect.width)

        else:

            ## if not provided, use children height as
            ## vertical_bg_height

            if not vertical_bg_height:
                vertical_bg_height = self.children.rect.height

            ## restrain vertical_bg_height to boundaries
            ## height

            self.max_height = min(vertical_bg_height, self.boundaries_rect.height)

        ### define rect dimensions

        if is_menubar:

            ## use the max width for the width
            width = self.max_width

            ## use height of children
            height = self.children.rect.height

        else:

            ## use children width
            width = self.children.rect.width

            ## use the max height for height
            height = self.max_height

        ### update rect with size
        self.rect.size = width, height

        ### check need to make children scrollable
        ### according to whether or not they trespass the
        ### maximum dimensions defined (either
        ### horiz_bg_width or vertical_bg_height) depending
        ### on whether this menu manager is a menubar or
        ### not
        self.check_scrollability()

        ### position rect using provided coordinates data

        setattr(self.rect, coordinates_name, coordinates_value)

        ### instantiate a surface to be store in the image
        ### attribute and used as background and also
        ### perform related setups

        ## instantiate background, storing it on the
        ## image attribute, using the rect size

        self.image = RECT_SURF_MAP[(*self.rect.size, MENU_BG)]

        ## if the menu manager is scrollable, copy the
        ## background into a clean_bg attribute, which
        ## will be used to clean the image attribute
        ## whenever needed
        if self.is_scrollable():
            self.clean_bg = self.image.copy()

        ### define drawing behaviours for the menu manager
        self.define_drawing_behaviours()

        ### trigger extra setups recursively on children
        self.perform_extra_setups()

        ### admin task: since many changes in position may
        ### happen while setting up the menu manager in many
        ### of the previous steps, we reposition each child's
        ### body
        self.reposition_children_bodies()

        ### create a variable to keep track of when the
        ### user clicked a top menu to expand it
        self.was_top_menu_expanded = False

    def instantiate_children(
        self,
        menu_list,
        top_surf_data,
    ):
        """Instantiate children widgets.

        menu_list (list of dicts)
            contains data about menu manager items. See
            __init__ docstring for additional information.
        """
        children = self.children = List2D()

        ### iterate over menu data instantiating the
        ### top items (if an item is a menu.submenu.main.Menu
        ### instance, its children, grandchildren and so on
        ### are instantiated recursively inside its __init__
        ### method)

        for item_data, surface_map in zip(menu_list, top_surf_data):

            ## choose top item class based on presence/
            ## absence of attribute and instantiate it

            # try retrieving children data
            try:
                item_data["children"]

            # not having children data means the data
            # describes a command, so instantiate one

            except KeyError:
                widget = Command(self, item_data, surface_map)

            # otherwise the data really describes a menu
            # and its children, so instantiate a menu

            else:

                # instantiate menu (all its children are
                # instantiated recursively in this step)

                widget = Menu(self, item_data, surface_map)

            children.append(widget)

        ###

        retrieve_pos_from = "topright" if self.is_menubar else "bottomleft"

        children.rect.snap_rects_ip(
            retrieve_pos_from=retrieve_pos_from,
            assign_pos_to="topleft",
        )

    def perform_extra_setups(self):
        """Call the perform_extra_setups method on children.

        This goes through each child and its own children
        recursively, executing special methods. For more
        information, check the menu/submenu/main.py module.
        """
        ### iterate over each child executing the
        ### perform_extra_setups if it exists

        for child in self.children:

            try:
                method = child.perform_extra_setups

            except AttributeError:
                pass

            else:
                method()

    def __repr__(self):
        """Return nearest unambiguous string representation.

        Since the menu manager object is too complex to
        have its instantiation call or contents faithfully
        communicated through a string representation, we
        stick to returning the some of the most relevant
        __init__ arguments and the string representation
        of each children.

        Overrides object.__repr__.
        """
        ### define a base text
        base_text = "MenuManager instance\n"

        ### add the number of direct children info
        base_text += "Direct children: " + str(len(self.children))

        ### change the base text to indicate the menu is
        ### scrollable if it is the case
        if self.is_scrollable():
            base_text += ", scrollable"

        ### gather some of the menu manager more relevant
        ### __init__ arguments using a special format and
        ### add them to the base text

        ## gather names of attribute containing relevant
        ## data

        attr_names = (
            "loop_holder",
            "boundaries_rect",
            "is_menubar",
        )

        ## retrieve the maximum length between the names
        ## and increment by 2 to compensate for padding

        max_len = max(len(attr_name) for attr_name in attr_names)

        max_len += 2

        ## define the padding, the separator and a final
        ## string variable to gather the formated text
        ## displaying the arguments data

        padding = "  "
        sep = " : "
        final_str = ""

        ## iterate over the attr names building custom
        ## formated strings with data about the relevant
        ## arguments

        for attr_name in attr_names:

            # key is the some padding plus the attr_name
            key = padding + attr_name

            # adjust key to be left justified using the
            # max_len
            key = key.ljust(max_len, " ")

            # value is the repr string of the attribute
            value = repr(getattr(self, attr_name))

            # put together the custom formated string for
            # this piece of data
            custom_formatted_str = key + sep + value

            # finally concatenate the formatted string with
            # the accumulated pieces of data in the final
            # string variable
            final_str += custom_formatted_str + ",\n"

        ## add another piece of text implying the menu
        ## manager has more data which were not disclosed
        final_str += "  [...]"

        ### increment the base text with the final string
        ### containing the data about the arguments
        base_text += ", {\n" + final_str + "\n}"

        ### increment the base text again with a caption to
        ### indicate we'll be listing the menu tree
        base_text += "\n\nTree structure:\n"

        ### finally return the base text plus each children
        ### string representation, separated by a new line
        ### character

        return "\n".join([base_text, *map(repr, self.children)])
