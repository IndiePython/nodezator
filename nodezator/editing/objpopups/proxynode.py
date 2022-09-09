### local imports

from ...config import APP_REFS

from ...menu.main import MenuManager

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
