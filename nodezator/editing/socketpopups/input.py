### local imports

from ...config import APP_REFS

from ...menu.main import MenuManager


class InputSocketPopupMenu:
    def __init__(self):

        super().__init__()

        menu_list = [
            {
                "label": "Disconnect",
                "command": self.disconnect,
            },
        ]

        self.general_input_socket_popup = MenuManager(
            menu_list,
            is_menubar=False,
            use_outline=True,
            keep_focus_when_unhovered=True,
        )

        ###

        menu_list.extend(
            [
                {
                    "label": "Unpack",
                    "command": self.unpack,
                },
                {
                    "label": "Undo unpacking",
                    "command": self.undo_unpacking,
                },
            ]
        )

        self.subparam_input_socket_popup = MenuManager(
            menu_list,
            is_menubar=False,
            use_outline=True,
            keep_focus_when_unhovered=True,
        )

    def show(self, socket, mouse_pos):

        self.socket_under_mouse = socket

        if socket.subparameter_index is None:

            (self.general_input_socket_popup.focus_if_within_boundaries(mouse_pos))

        else:
            (self.subparam_input_socket_popup.focus_if_within_boundaries(mouse_pos))

    def disconnect(self):

        socket = self.socket_under_mouse
        APP_REFS.gm.sever_parent(socket)

    def unpack(self):

        socket = self.socket_under_mouse
        socket.mark_for_unpacking()

    def undo_unpacking(self):

        socket = self.socket_under_mouse
        socket.unmark_for_unpacking()
