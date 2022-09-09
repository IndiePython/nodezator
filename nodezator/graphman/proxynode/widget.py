"""Facility for widget addition/removal."""

### standard library import
from functools import partial


### local imports

from ...config import APP_REFS

from ...ourstdlibs.behaviour import remove_by_identity

from ...ourstdlibs.collections.general import CallList

from ...our3rdlibs.button import Button

from ...our3rdlibs.behaviour import indicate_unsaved

from ...widget.stringentry import StringEntry

from ...rectsman.main import RectsManager

from ..widget.utils import WIDGET_CLASS_MAP

from ..socket.surfs import type_to_codename

from .utils import update_with_widget

from .surfs import (
    ADD_BUTTON_SURF,
    REMOVE_BUTTON_SURF,
)


class WidgetOps:
    """Widget related operations."""

    def instantiate_widget(self, widget_data):
        """Instantiate a widget for the node."""
        add_button = self.add_button

        viz_objs = self.visual_objects
        mouse_aware_objs = self.mouse_aware_objects

        rectsman_rects = self.rectsman._get_all_rects.__self__

        ###

        del self.add_button
        viz_objs.remove(add_button)
        mouse_aware_objs.remove(add_button)
        remove_by_identity(add_button.rect, rectsman_rects)

        ### create "remove widget" button

        remove_button = self.remove_button = Button(
            surface=REMOVE_BUTTON_SURF,
            command=self.remove_widget,
        )

        ### add the widget data to the node's data
        self.data["widget_data"] = widget_data

        ### retrieve widget class using the widget
        ### name from the parameter widget metadata

        widget_name = widget_data["widget_name"]
        widget_cls = WIDGET_CLASS_MAP[widget_name]

        ### retrieve the keyword arguments
        kwargs = widget_data["widget_kwargs"]

        ### instantiate the widget using the keyword
        ### arguments from the widget data
        widget = self.widget = widget_cls(**kwargs)

        ### also define a command to update the
        ### widget value and perform other related
        ### admin tasks

        command = CallList(
            [
                partial(
                    update_with_widget,
                    kwargs,
                    "value",
                    widget,
                ),
                self.check_header_width,
                self.update_remove_button_pos,
            ]
        )

        widget.command = command

        ### store the widget and remove_button instances
        ### and their rects in the appropriate collections

        viz_objs.append(widget)
        mouse_aware_objs.append(widget)
        rectsman_rects.append(widget.rect)

        viz_objs.append(remove_button)
        mouse_aware_objs.append(remove_button)
        rectsman_rects.append(remove_button.rect)

        ### check header width
        self.check_header_width()

        ### reposition all objects within the node
        self.reposition_elements()

        ### update sockets type_codename if needed

        try:
            self.data["source_type_codename"]

        except KeyError:

            expected_type = widget.get_expected_type()

            type_codename = type_to_codename(expected_type)

            output_socket = self.output_socket

            output_socket.update_type_codename(type_codename)

            self.propagate_output(
                self.title,
                type_codename,
            )

        ### indicate that changes were made in the data
        indicate_unsaved()

    def remove_widget(self):
        """Remove existing widget."""
        widget = self.widget
        remove_button = self.remove_button

        viz_objs = self.visual_objects
        mouse_aware_objs = self.mouse_aware_objects

        rectsman_rects = self.rectsman._get_all_rects.__self__

        for name in ("widget", "remove_button"):

            obj = getattr(self, name)

            delattr(self, name)

            viz_objs.remove(obj)
            mouse_aware_objs.remove(obj)

            remove_by_identity(obj.rect, rectsman_rects)

        ### remove the widget data
        del self.data["widget_data"]

        ### create and store add_button

        command = partial(
            (APP_REFS.ea.widget_creation_popup_menu.trigger_simple_widget_picking), self
        )

        add_button = self.add_button = Button(
            surface=ADD_BUTTON_SURF,
            command=command,
        )

        ## add add_button and its rect to relevant
        ## collections

        viz_objs.append(add_button)
        mouse_aware_objs.append(add_button)
        rectsman_rects.append(add_button.rect)

        ### check header width
        self.check_header_width()

        ### reposition all objects within the node
        self.reposition_elements()

        ### update sockets type_codename if needed

        try:
            self.data["source_type_codename"]

        except KeyError:

            type_codename = None

            output_socket = self.output_socket

            output_socket.update_type_codename(type_codename)

            self.propagate_output(
                self.title,
                type_codename,
            )

        ### indicate that changes were made in the data
        indicate_unsaved()
