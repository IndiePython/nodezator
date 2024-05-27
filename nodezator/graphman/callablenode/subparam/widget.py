"""Facility for subparameter widgets addition/removal."""

### standard library import
from functools import partial


### local imports

from ....config import APP_REFS

from ....our3rdlibs.button import Button

from ....our3rdlibs.behaviour import indicate_unsaved

from ....widget.stringentry import StringEntry

from ....rectsman.main import RectsManager

from ...widget.utils import WIDGET_CLASS_MAP

from ..utils import update_with_widget

from ..surfs import (
    REMOVE_BUTTON_SURF,
    SUBP_UP_BUTTON_SURF,
    SUBP_DOWN_BUTTON_SURF,
)

from ..constants import FONT_HEIGHT, SUBPARAM_KEYWORD_ENTRY_WIDTH



class WidgetOps:
    """Widget related operations."""

    def instantiate_widget(
        self,
        widget_data,
        param_name,
    ):
        """Instantiate a new widget for a subparameter.

        The subparameter may already exist (if it was
        created by connecting its socket) or not (in which
        case we'll need to create it).

        Parameters
        ==========

        widget_data (dict)
            data for dict instantiation.
        param_name (string)
            represents the name of the parameter.
        """
        ### since we'll need it, let's reference the
        ### map for input sockets of this parameter
        param_input_sockets = self.input_socket_live_flmap[param_name]

        ### let's also alias live instances maps using
        ### variables of low character count, for better
        ### code layout

        wl_flmap = self.widget_live_flmap
        wrb_flmap = self.widget_remove_button_flmap

        ### create input socket and retrieve a reference
        ### to it

        ## create a new input socket (input sockets
        ## represent parameters/subparameters, so this
        ## is the equivalent of creating a subparameter)
        self.create_new_input_socket(param_name)

        ## update the subparam_index variable with the
        ## name of the parameter we just created; (it
        ## is a key in the map containing input sockets
        ## for the parameter, an integer which is the
        ## highest among the keys
        subparam_index = max(param_input_sockets)

        ## use the subparameter index to retrieve the
        ## input socket representing the subparameter
        input_socket = param_input_sockets[subparam_index]

        ### create and store "move subparam buttons"

        move_subparam_up = partial(self.move_subparam_up, input_socket)

        subp_up_button = Button(
            surface=SUBP_UP_BUTTON_SURF,
            command=move_subparam_up,
        )

        sub_flmap = self.subparam_up_button_flmap

        sub_flmap[param_name][subparam_index] = subp_up_button

        # this dict subclass instance must be updated
        # every time it is changed
        sub_flmap.update()

        move_subparam_down = partial(self.move_subparam_down, input_socket)

        subp_down_button = Button(
            surface=SUBP_DOWN_BUTTON_SURF,
            command=move_subparam_down,
        )

        sdb_flmap = self.subparam_down_button_flmap

        sdb_flmap[param_name][subparam_index] = subp_down_button

        # this dict subclass instance must be updated
        # every time it is changed
        sdb_flmap.update()

        ### store the widget data in the subwidgets data
        ### map for this subparameter
        self.data["subparam_widget_map"][param_name][subparam_index] = widget_data

        ### retrieve widget class using the widget
        ### name from the parameter widget metadata

        widget_name = widget_data["widget_name"]
        widget_cls = WIDGET_CLASS_MAP[widget_name]

        ### retrieve the keyword arguments
        kwargs = widget_data["widget_kwargs"]

        ### instantiate the widget using the keyword
        ### arguments from the widget data
        widget = widget_cls(name=param_name, **kwargs)

        ### store the widget instance in the live map
        ### for widgets and execute its update method
        ### (this map is a custom dict subclass that
        ### needs to be updated whenever we change it;
        ### check its documentation for more)

        wl_flmap[param_name][subparam_index] = widget
        wl_flmap.update()

        ### if variable is of keyword-variable kind
        ### instantiate a subparam keyword widget

        if self.var_kind_map[param_name] == "var_key":

            ## define a name for the keyword
            keyword_name = self.get_new_keyword_name()

            ## put together a command which takes proper
            ## measures when updating the keyword name

            command = partial(
                self.update_keyword,
                input_socket,
            )

            ## instantiate the keyword entry and take
            ## additional measures

            # instantiate

            subparam_keyword_entry = StringEntry(
                value=keyword_name,
                font_height=FONT_HEIGHT,
                width=SUBPARAM_KEYWORD_ENTRY_WIDTH,
                command=command,
            )

            # store the subparam keyword entry

            self.subparam_keyword_entry_live_map[subparam_index] = (
                subparam_keyword_entry
            )

            # also store the name of the keyword created
            # in the dedicated map for keyword names
            self.data["subparam_keyword_map"][subparam_index] = keyword_name


        ### create "remove widget" button

        ## define command
        command = partial(self.remove_subparameter_widget, widget)

        ## instantiate and store

        button = Button(
            surface=REMOVE_BUTTON_SURF,
            command=command,
        )

        ## store the button instance in the respective
        ## map and execute its update method
        ## (this map is a custom dict subclass that
        ## needs to execute this whenever we change it;
        ## check its documentation for more)

        wrb_flmap[param_name][subparam_index] = button
        wrb_flmap.update()

        ### also define a command to update the widget value in the node
        ### data and the position of the remove button (because the
        ### widget may change its size when edited, depending on the
        ### kind of widget), then assign such command to the 'command'
        ### attribute of the widget
        widget.command = partial(update_with_widget, kwargs, "value", widget, button)

        ### create a rects manager to control the rects of this
        ### new subparameter

        self.subparam_rectsman_map[param_name][subparam_index] = (
            RectsManager([].__iter__)
        )

        ### reposition all objects within the node
        self.reposition_elements()

        ### reset body's height and image
        self.reset_body_height_and_image()

        ### indicate that changes were made in the data
        indicate_unsaved()

        ### indicate birdseye view state of window manager must
        ### have its objects updated next time it is set
        APP_REFS.ea.must_update_birdseye_view_objects = True

    def remove_subparameter_widget(self, widget):
        """Remove existing widget from a subparameter.

        Parameters
        ==========
        widget (widget instance)
            reference to widget instance to be removed.
        """
        ### discover the parameter and subparameter index
        ### of the widget to be removed; once you break
        ### out of the for loops, the right names will
        ### be bound to the param_name and subparam_index
        ### variables;

        ## retrieve the parameter name and the data for
        ## widgets in its subparameters

        for param_name in self.var_kind_map:

            # retrieve subparam widgets data (a map which associates
            # the index of a subparam with its widget)
            subparam_widgets_data = self.widget_live_flmap[param_name]

            # retrieve subparameter index and its value,
            # which is a widget instance

            for subparam_index, widget_instance in subparam_widgets_data.items():

                # if the widget to be removed is the
                # widget instance, we can break out of
                # this inner "for" loop
                if widget is widget_instance:
                    break

            # if we didn't break out of the inner "for"
            # loop, this "else" clause will execute,
            # making us start again with the next item
            # in the outer "for" loop
            else:
                continue

            # otherwise, if we broke out from the inner
            # "for" loop, it means the parameter name
            # and subparameter indices stored are the ones
            # we are looking for: we can finally break
            # out of the outer "for" loop
            break

        ### alias live instances maps using variables of
        ### low character count, for better code layout

        wl_flmap = self.widget_live_flmap
        wrb_flmap = self.widget_remove_button_flmap

        ### remove widget from widget map
        widget = wl_flmap[param_name].pop(subparam_index)

        ## this dict subclass instance needs to be updated
        ## every time it is changed
        wl_flmap.update()

        ### remove the "remove widget" button
        button = wrb_flmap[param_name].pop(subparam_index)

        ## this dict subclass instance needs to be updated
        ## every time it is changed
        wrb_flmap.update()

        ### remove the widget data from the subwidgets data
        ### map for this parameter
        self.data["subparam_widget_map"][param_name].pop(subparam_index)

        ### reference the list of subparameters for
        ### unpacking locally for easier access
        subparams_for_unpacking = self.data["subparam_unpacking_map"][param_name]

        ### perform operations assuming the input socket doesn't have
        ### a source of data anymore, that is, remove the input socket
        ### and perform needed admin tasks

        ## remove input socket from live map
        self.input_socket_live_flmap[param_name].pop(subparam_index)

        # this dict subclass instance must be updated
        # whenever it changes
        self.input_socket_live_flmap.update()

        ## remove the subparam index from the list
        ## in the subparam map
        self.data["subparam_map"][param_name].remove(subparam_index)

        ## remove "move subparam" buttons
        self.subparam_up_button_flmap[param_name].pop(subparam_index)

        # this dict subclass instance must be updated
        # whenever it changes
        self.subparam_up_button_flmap.update()

        self.subparam_down_button_flmap[param_name].pop(subparam_index)

        # this dict subclass instance must be updated
        # whenever it changes
        self.subparam_down_button_flmap.update()

        ## since the input socket was removed...

        ## if the subparameter was marked to be
        ## unpacked, remove the unpacking icon from
        ## the respective map and the subparameter
        ## index from the respective list as well

        if subparam_index in subparams_for_unpacking:

            ## remove unpacking icon
            self.subparam_unpacking_icon_flmap[param_name].pop(subparam_index)

            # this special dict subclass instance must
            # be updated whenever it is changed
            self.subparam_unpacking_icon_flmap.update()

            ## remove subparameter index from list
            ## within the subparameter unpacking map
            self.data["subparam_unpacking_map"][param_name].remove(subparam_index)

        ## else if the parameter is of keyword-variable
        ## kind remove the keyword entry from the
        ## respective map and the keyword from the
        ## respective map as well

        elif self.var_kind_map[param_name] == "var_key":

            ## remove keyword entry widget
            self.subparam_keyword_entry_live_map.pop(subparam_index)

            ## remove keyword name from subparameter
            ## keyword map
            self.data["subparam_keyword_map"].pop(subparam_index)

        ## remove the subparameter rectsman from the
        ## subparameter rectsman map
        self.subparam_rectsman_map[param_name].pop(subparam_index)

        ## fix names of remaining subparameters
        self.fix_subparameter_indices(param_name)

        ### reposition all objects within the node
        self.reposition_elements()

        ### reset body's height and image
        self.reset_body_height_and_image()

        ### indicate that changes were made in the data
        indicate_unsaved()

        ### indicate birdseye view state of window manager must
        ### have its objects updated next time it is set
        APP_REFS.ea.must_update_birdseye_view_objects = True
