"""Facility for memory management.

As of now, memory management consists of operations
to help freeing memory and/or keeping its usage low.
"""

### local imports

from .config import APP_REFS

from .ourstdlibs.treeutils import yield_tree_attrs

from .our3rdlibs.userlogger import USER_LOGGER

from .widget.optionmenu.main import OptionMenu

from .widget.optiontray.main import OptionTray

from .textman.cache import TEXT_SURFS_DB


def free_up_memory():
    """Free up memory by removing unused objects.

    This functions is used to free up memory by removing
    objects from previous sessions (if they exist). This
    is done by deleting attributes and clearing collections.

    This steps were tested and it was proved that they
    really help to decrease memory usage.

    See "Memory management" in the glossary to know a bit
    more.
    """
    ### retrieve a reference to the window manager
    window_manager = APP_REFS.window_manager

    ### try retrieving a reference to the graph manager
    try:
        gm = APP_REFS.gm

    ### if such attribute doesn't exist, just pass
    except AttributeError:
        pass

    ### otherwise, trigger its corresponding operation to
    ### free memory
    else:
        gm.free_up_memory()

    ### try gathering references for menus created

    menus = []

    for menu_attr in ("menubar", "canvas_popup_menu"):

        try:
            menu = getattr(window_manager, menu_attr)
        except AttributeError:
            pass
        else:
            menus.append(menu)

    ### for each menu gathered (if any), travel the tree
    ### structure they represent from each leaf until the
    ### root of the tree removing all children (by clearing
    ### the lists holding them)

    for menu in menus:

        ## obtain an iterator which yields lists of children
        ## held by the menu

        all_children_lists = yield_tree_attrs(menu, "children", "children")

        ## iterate over such lists, clearing them
        for children_list in all_children_lists:
            children_list.clear()

    ### also clear collections held in window manager
    ### attributes

    for attr_name in (
        "switches",
        "switches_update_methods",
        "switches_drawing_methods",
    ):

        try:
            obj = getattr(window_manager, attr_name)
        except AttributeError:
            pass
        else:
            obj.clear()

    ### clear items from collections stored/referenced
    ### in attributes of the APP_REFS object

    for attr_name in (
        "node_def_map",
        "signature_map",
        "script_path_map",
        "category_path_map",
        "category_index_map",
        "custom_stdout_lines",
    ):

        obj = getattr(APP_REFS, attr_name)
        obj.clear()

    ### replace the user logger contents by an empty string
    USER_LOGGER.contents = ""

    ### trigger the memory freeing operation of the
    ### OptionMenu and OptionTray widget classes

    OptionMenu.free_up_memory()
    OptionTray.free_up_memory()

    ### clear the text maps database class
    TEXT_SURFS_DB.free_up_memory()
