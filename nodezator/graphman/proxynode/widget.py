"""Facility for widget addition/removal."""

### standard library import
from functools import partial


### local imports

from ...config import APP_REFS

from ...ourstdlibs.collections.general import CallList

from ...our3rdlibs.behaviour import indicate_unsaved

from ...dialog import create_and_show_dialog

from ..widget.utils import WIDGET_CLASS_MAP

from ..socket.surfs import type_to_codename

from .utils import update_with_widget


class WidgetOps:
    """Widget related operations."""

    def instantiate_widget(self, widget_data):
        """Instantiate a widget for the node."""
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

        ### check header width
        self.check_header_width()

        ### reposition all objects within the node
        self.reposition_elements()

        ### update sockets type_codename

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

        ### indicate birdseye view state of window manager must
        ### have its objects updated next time it is set
        APP_REFS.ea.must_update_birdseye_view_objects = True

    def replace_or_add_widget(self, widget_data):

        if not hasattr(self, 'widget'):

            self.instantiate_widget(widget_data)
            return

        ### retrieve widget class using the widget
        ### name from the parameter widget metadata

        widget_name = widget_data["widget_name"]
        widget_cls = WIDGET_CLASS_MAP[widget_name]

        ### retrieve the keyword arguments
        kwargs = widget_data["widget_kwargs"]

        ### instantiate the widget using the keyword
        ### arguments from the widget data
        widget = widget_cls(**kwargs)

        ### try updating new widget with data from current
        ### one

        try:
            widget.set(self.widget.get())

        except Exception:

            create_and_show_dialog(
                "Data from current widget is not compatible with new widget."
                " The operation was cancelled."
            )

            return

        ### store new widget in attribute
        self.widget = widget

        ### update value on widget kwargs
        ###
        ### note that we retreive the value again, this
        ### we ensure it is updated to use specific formatting
        ### if the new widget requires
        kwargs['value'] = widget.get()

        ### add the widget data to the node's data
        self.data['widget_data'] = widget_data

        ### also define a command to update the
        ### widget value and perform other related
        ### admin tasks

        command = CallList(
            [
                partial(
                    update_with_widget,
                    kwargs,
                    'value',
                    widget,
                ),
                self.check_header_width,
                self.update_remove_button_pos,
            ]
        )

        widget.command = command

        ### check header width
        self.check_header_width()

        ### reposition all objects within the node
        self.reposition_elements()

        ### update sockets type_codename

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

        ### indicate birdseye view state of window manager must
        ### have its objects updated next time it is set
        APP_REFS.ea.must_update_birdseye_view_objects = True

    def remove_widget(self):
        """Remove existing widget."""
        ### delete reference to widget
        del self.widget

        ### remove the widget data
        del self.data["widget_data"]

        ### check header width
        self.check_header_width()

        ### reposition all objects within the node
        self.reposition_elements()

        ### update sockets type_codename

        type_codename = None

        output_socket = self.output_socket

        output_socket.update_type_codename(type_codename)

        self.propagate_output(
            self.title,
            type_codename,
        )

        ### indicate that changes were made in the data
        indicate_unsaved()

        ### indicate birdseye view state of window manager must
        ### have its objects updated next time it is set
        APP_REFS.ea.must_update_birdseye_view_objects = True
