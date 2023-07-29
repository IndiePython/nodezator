### standard library imports

from functools import partial

from copy import deepcopy



### local imports

from ...pygamesetup import SERVICES_NS

from ...menu.main import MenuManager

from ...graphman.widget.popupdefinition import WIDGET_POPUP_STRUCTURE

from ..widgetpicker.main import pick_widget


class WidgetCreationPopupMenu(MenuManager):
    def __init__(self):

        menu_list = []

        command = self.trigger_subparameter_widget_instantiation

        for label_text, data in WIDGET_POPUP_STRUCTURE:

            if isinstance(data, dict):

                menu_list.append(
                    {
                        "label": label_text,
                        "command": partial(
                            command,
                            data,
                        ),
                    }
                )

            elif isinstance(data, list):

                grandchildren = [

                    {
                        "label": sublabel,
                        "command": partial(
                            command,
                            subdata,
                        ),
                    }

                    for sublabel, subdata in data

                ]

                menu_list.append(
                    {
                        "label": label_text,
                        "children": grandchildren,
                    }
                )

        menu_list.append(
            {
                "label": "All available widgets...",
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

        self.focus_if_within_boundaries(SERVICES_NS.get_mouse_pos())

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
