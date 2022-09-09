### local imports

from contextlib import suppress

from ...config import APP_REFS

from ...loopman.exception import ContinueLoopException

from ...ourstdlibs.behaviour import get_suppressing_callable


class GeneralPopupCommands:
    def __init__(self):

        cls = self.__class__

        if not hasattr(cls, "SINGLE_COMMANDS"):

            cls.SINGLE_COMMANDS = [
                {
                    "label": "Move",
                    "icon": "moving",
                    "command": self.move_obj,
                },
                {
                    "label": "Duplicate",
                    "icon": "duplication",
                    "command": self.duplicate_obj,
                },
                {
                    "label": "Delete",
                    "icon": "delete",
                    "command": self.delete_obj,
                },
            ]

            cls.NODE_ONLY_SINGLE_COMMANDS = cls.SINGLE_COMMANDS + [
                {
                    "label": "Comment/uncomment",
                    "icon": "hash",
                    "command": (self.toggle_commenting_state_of_node),
                }
            ]

            cls.COLLECTIVE_COMMANDS = [
                {"label": "---"},
                {
                    "label": "Move selected",
                    "key_text": "g",
                    "icon": "moving",
                    "command": get_suppressing_callable(
                        APP_REFS.ea.start_moving,
                        ContinueLoopException,
                    ),
                },
                {
                    "label": "Duplicate selected",
                    "key_text": "Ctrl+d",
                    "icon": "duplication",
                    "command": get_suppressing_callable(
                        (APP_REFS.ea.duplicate_selected),
                        ContinueLoopException,
                    ),
                },
                {
                    "label": "Delete selected",
                    "key_text": "Delete",
                    "icon": "delete",
                    "command": APP_REFS.ea.remove_selected,
                },
            ]

            cls.NODE_INCLUSIVE_COLLECTIVE_COMMANDS = cls.COLLECTIVE_COMMANDS + [
                {
                    "label": "Comment/uncomment selected",
                    "key_text": "Shift+#",
                    "icon": "hash",
                    "command": (APP_REFS.ea.comment_uncomment_selected_nodes),
                }
            ]

    def move_obj(self):

        APP_REFS.ea.deselect_all()

        APP_REFS.ea.add_obj_to_selection(self.obj_under_mouse)

        with suppress(ContinueLoopException):
            APP_REFS.ea.start_moving()

    def duplicate_obj(self):

        APP_REFS.ea.deselect_all()

        APP_REFS.ea.add_obj_to_selection(self.obj_under_mouse)

        with suppress(ContinueLoopException):
            APP_REFS.ea.duplicate_selected()

    def delete_obj(self):

        APP_REFS.ea.deselect_all()

        APP_REFS.ea.add_obj_to_selection(self.obj_under_mouse)

        APP_REFS.ea.remove_selected()

    def toggle_commenting_state_of_node(self):

        APP_REFS.ea.comment_uncomment_nodes([self.obj_under_mouse])


## function for injection


def get_node_info(self):
    APP_REFS.ea.view_info(self.obj_under_mouse)
