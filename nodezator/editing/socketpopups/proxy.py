### local imports

from ...config import APP_REFS

from ...menu.main import MenuManager


class ProxySocketPopupMenu(MenuManager):
    def __init__(self):

        menu_list = [
            {
                "label": "Disconnect",
                "command": self.disconnect,
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

    def disconnect(self):

        socket = self.socket_under_mouse
        APP_REFS.gm.sever_parent(socket)
