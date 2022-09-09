### standard library imports

from functools import partial

from copy import deepcopy


### third-party import
from pygame.mouse import get_pos as get_mouse_pos


### local imports

from ...menu.main import MenuManager

from ...graphman.presets import (
    WIDGET_DATA_PRESET_MAP,
    WIDGET_PRESET_MENU_LABEL_MAP,
)

from ..widgetpicker.main import pick_widget


class WidgetCreationPopupMenu(MenuManager):
    def __init__(self):

        menu_list = []

        command = self.trigger_subparameter_widget_instantiation

        for preset_name, widget_data in WIDGET_DATA_PRESET_MAP.items():

            label_text = WIDGET_PRESET_MENU_LABEL_MAP[preset_name]

            menu_list.append(
                {
                    "label": label_text,
                    "command": partial(
                        command,
                        widget_data,
                    ),
                }
            )

        menu_list.append(
            {
                "label": "More options...",
                "command": command,
            }
        )

        super().__init__(
            menu_list,
            is_menubar=False,
            use_outline=True,
            keep_focus_when_unhovered=True,
        )

    def trigger_simple_widget_picking(self, node, *other_references):

        self.node_waiting_widget_refs = (node, *other_references)

        self.focus_if_within_boundaries(get_mouse_pos())

    def trigger_subparameter_widget_instantiation(
        self,
        widget_data=None,
    ):

        if widget_data is None:

            ### obtain widget data
            widget_data = pick_widget()

            ### if widget data is still None, cancel the
            ### operation by returning earlier
            if widget_data is None:
                return

        else:
            widget_data = deepcopy(widget_data)

        node, *other_references = self.node_waiting_widget_refs

        node.instantiate_widget(
            widget_data,
            *other_references,
        )
