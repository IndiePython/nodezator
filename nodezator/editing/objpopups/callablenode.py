
### standard library import
from functools import partialmethod


### local imports

from ...config import APP_REFS

from ...menu.main import MenuManager

from .constants import (
    GeneralPopupCommands,
    get_node_info,
)

from ...graphman.callablenode.main import CallableNode


class CallableNodePopupMenu(GeneralPopupCommands):

    get_node_info = get_node_info

    def __init__(self):

        super().__init__()

        ###

        mode_switching_submenu = {

            "label": "Change mode to",
            "children": [
                {
                    "label": "Expanded signature",
                    "command": self.obj_to_expanded_signature,
                },
                {
                    "label": "Collapsed signature",
                    "command": self.obj_to_collapsed_signature,
                },
                {
                    "label": "Callable",
                    "command": self.obj_to_callable,
                },
            ],

        }

        ###

        user_def_node_menu_list = self.NODE_ONLY_SINGLE_COMMANDS.copy()

        for obj_data in (
            mode_switching_submenu,
            {
                "label": "View main callable info",
                "key_text": "Shift+i",
                "icon": "python_viewing",
                "command": self.view_callable_info,
            },
            {
                "label": "View node script",
                "key_text": "i",
                "icon": "python_viewing",
                "command": self.view_node_script,
            },
        ):

            user_def_node_menu_list.insert(1, obj_data)

        self.user_def_node_only_popup = MenuManager(
            user_def_node_menu_list,
            is_menubar=False,
            use_outline=True,
            keep_focus_when_unhovered=True,
        )

        ###

        user_def_node_menu_list.extend(self.NODE_INCLUSIVE_COLLECTIVE_COMMANDS)

        self.user_def_node_and_selected_popup = MenuManager(
            user_def_node_menu_list,
            is_menubar=False,
            use_outline=True,
            keep_focus_when_unhovered=True,
        )

        ###

        app_def_node_menu_list = self.NODE_ONLY_SINGLE_COMMANDS.copy()

        for obj_data in (
            mode_switching_submenu,
            {
                "label": "Get source info",
                "key_text": "i",
                "icon": "python_viewing",
                "command": self.get_node_info,
            },
        ):
            app_def_node_menu_list.insert(1, obj_data)

        self.app_def_node_only_popup = MenuManager(
            app_def_node_menu_list,
            is_menubar=False,
            use_outline=True,
            keep_focus_when_unhovered=True,
        )

        ###

        app_def_node_menu_list.extend(self.NODE_INCLUSIVE_COLLECTIVE_COMMANDS)

        self.app_def_node_and_selected_popup = MenuManager(
            app_def_node_menu_list,
            is_menubar=False,
            use_outline=True,
            keep_focus_when_unhovered=True,
        )

    def show(self, node, mouse_pos):

        self.obj_under_mouse = node

        if type(node) == CallableNode:

            if node in APP_REFS.ea.selected_objs:

                (
                    self.user_def_node_and_selected_popup.focus_if_within_boundaries(
                        mouse_pos
                    )
                )

            else:

                (self.user_def_node_only_popup.focus_if_within_boundaries(mouse_pos))

        else:

            if node in APP_REFS.ea.selected_objs:

                (
                    self.app_def_node_and_selected_popup.focus_if_within_boundaries(
                        mouse_pos
                    )
                )

            else:

                (self.app_def_node_only_popup.focus_if_within_boundaries(mouse_pos))

    def view_node_script(self):

        APP_REFS.ea.view_info(
            self.obj_under_mouse,
            "node_script",
        )

    def view_callable_info(self):

        APP_REFS.ea.view_info(
            self.obj_under_mouse,
            "callable_info",
        )

    def obj_to_mode(self, mode_name):
        self.obj_under_mouse.set_mode(mode_name)

    obj_to_expanded_signature = partialmethod(obj_to_mode, 'expanded_signature')
    obj_to_collapsed_signature = partialmethod(obj_to_mode, 'collapsed_signature')
    obj_to_callable = partialmethod(obj_to_mode, 'callable')
