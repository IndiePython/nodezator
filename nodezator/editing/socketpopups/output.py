### local imports

from ...config import APP_REFS

from ...menu.main import MenuManager


class OutputSocketPopupMenu(MenuManager):
    def __init__(self):

        menu_list = [
            {
                "label": "Disconnect all children",
                "command": self.disconnect_all_children,
            },
        ]

        super().__init__(
            menu_list,
            is_menubar=False,
            use_outline=True,
            keep_focus_when_unhovered=True,
        )

    def show(self, socket, mouse_pos):

        self.socket_under_mouse = socket
        self.focus_if_within_boundaries(mouse_pos)

    def disconnect_all_children(self):

        socket = self.socket_under_mouse
        APP_REFS.gm.sever_children(socket)
