"""Quick utilities for the menu.submenu.main.Menu class."""


def is_top_menu(obj):
    """Return True if obj is a top menu.

    obj (a menubar.widget.Menu instance)

    A top menu is an instance of menu.submenu.main.Menu
    class which has a menu.main.MenuManager instance
    referenced in the 'parent' attribute, while regular
    menus have another Menu instance as the parent
    attribute.

    Thus, if the obj 'parent' attribute isn't of the same
    class we can safely tell that the instance is a top
    menu.
    """
    return not isinstance(obj.parent, obj.__class__)


def get_boundaries(obj):
    """Return the boundaries_rect attribute of menu manager.

    obj (a menubar.widget.Menu instance)

    Checks the parent of obj, then the parent of its parent
    and so on until it reaches a parent which isn't of the
    same class of the child. A parent which isn't of the
    same class of the child is, by consequence, the
    MenuManager instance (because of how the relationship
    between the instances of those classes is designed).

    Once the MenuManager instance is found, the pygame.Rect
    instance in its boundaries_rect attribute is returned.
    """
    ### loop indefinitely until the breaking condition is
    ### met

    while True:

        ## retrieve the parent of the obj
        parent = obj.parent

        ## breaking condition: if the parent isn't of the
        ## same class of obj (its child), we can break of
        ## the loop
        if not isinstance(parent, obj.__class__):
            break

        ## otherwise we just consider the parent as the
        ## obj for the next iteration
        else:
            obj = parent

    ### once we break out of the while loop, we return the
    ### boundaries_rect attribute of the parent
    return parent.boundaries_rect
