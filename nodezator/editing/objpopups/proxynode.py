
### standard library import
from functools import partial


### local imports

from ...config import APP_REFS

from ...menu.main import MenuManager

from ...graphman.widget.popupdefinition import WIDGET_POPUP_STRUCTURE

from ..widgetpicker.main import pick_widget

from .constants import GeneralPopupCommands



class ProxyNodePopupMenu(GeneralPopupCommands):

    def __init__(self):

        super().__init__()

        ###

        self.redirect_node_only_popup = MenuManager(
            self.NODE_ONLY_SINGLE_COMMANDS,
            is_menubar=False,
            use_outline=True,
            keep_focus_when_unhovered=True,
        )

        ###

        data_node_menu_list = self.NODE_ONLY_SINGLE_COMMANDS.copy()

        data_node_menu_list.insert(
            0,
            {
                "label": "Edit title",
                "key_text": "t",
                "icon": "pencil",
                "command": self.edit_node_title,
            },
        )

        ###

        pick_new_widget_submenu = {
            "label": "Add or replace widget",
            "icon": "data_node",
            "children": [],
        }

        data_node_menu_list.insert(
            1,
            pick_new_widget_submenu,
        )

        children = pick_new_widget_submenu['children']

        for label_text, data in WIDGET_POPUP_STRUCTURE:

            if isinstance(data, dict):

                children.append(
                    {
                        "label": label_text,
                        "command": partial(
                            self.replace_or_add_widget,
                            data,
                        ),
                    }
                )

            elif isinstance(data, list):

                grandchildren = [

                    {
                        "label": sublabel,
                        "command": partial(
                            self.replace_or_add_widget,
                            subdata,
                        ),
                    }

                    for sublabel, subdata in data

                ]

                children.append(
                    {
                        "label": label_text,
                        "children": grandchildren,
                    }
                )

        children.append(
            {
                "label": "All available widgets...",
                "command": self.replace_or_add_widget,
            }
        )

        self.data_node_only_popup = MenuManager(
            data_node_menu_list,
            is_menubar=False,
            use_outline=True,
            keep_focus_when_unhovered=True,
        )

        ###

        self.redirect_node_and_selected_popup = MenuManager(
            (self.NODE_ONLY_SINGLE_COMMANDS + self.NODE_INCLUSIVE_COLLECTIVE_COMMANDS),
            is_menubar=False,
            use_outline=True,
            keep_focus_when_unhovered=True,
        )

        ###

        data_node_menu_list.extend(self.NODE_INCLUSIVE_COLLECTIVE_COMMANDS)

        self.data_node_and_selected_popup = MenuManager(
            data_node_menu_list,
            is_menubar=False,
            use_outline=True,
            keep_focus_when_unhovered=True,
        )

    def show(self, proxy_node, mouse_pos):

        self.obj_under_mouse = proxy_node

        if proxy_node in APP_REFS.ea.selected_objs:

            if hasattr(proxy_node.proxy_socket, "parent"):

                (
                    self.redirect_node_and_selected_popup.focus_if_within_boundaries(
                        mouse_pos
                    )
                )

            else:

                (
                    self.data_node_and_selected_popup.focus_if_within_boundaries(
                        mouse_pos
                    )
                )

        else:

            if hasattr(proxy_node.proxy_socket, "parent"):

                (self.redirect_node_only_popup.focus_if_within_boundaries(mouse_pos))

            else:

                (self.data_node_only_popup.focus_if_within_boundaries(mouse_pos))

    def edit_node_title(self):
        APP_REFS.ea.edit_data_node_title(self.obj_under_mouse)

    def replace_or_add_widget(self, widget_data=None):

        if widget_data is None:

            ### retrieve widget kwargs
            widget_data = pick_widget()

            ### if widget data is still None, cancel the operation
            ### by returning earlier
            if widget_data is None:
                return

        ###
        self.obj_under_mouse.replace_or_add_widget(widget_data)
