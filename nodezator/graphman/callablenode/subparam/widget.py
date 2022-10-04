"""Facility for subparameter widgets addition/removal."""

### standard library import
from functools import partial


### local imports

from ....config import APP_REFS

from ....ourstdlibs.behaviour import remove_by_identity

from ....our3rdlibs.button import Button

from ....our3rdlibs.behaviour import indicate_unsaved

from ....widget.stringentry import StringEntry

from ....rectsman.main import RectsManager

from ...widget.utils import WIDGET_CLASS_MAP

from ..utils import update_with_widget

from ..surfs import (
    ADD_BUTTON_SURF,
    REMOVE_BUTTON_SURF,
    SUBP_UP_BUTTON_SURF,
    SUBP_DOWN_BUTTON_SURF,
)

from ..constants import FONT_HEIGHT


class WidgetOps:
    """Widget related operations."""

    def instantiate_widget(
        self,
        widget_data,
        param_name,
        input_socket=None,
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
        input_socket (InputSocket instance or None)
            when an input socket instance is provided,
            it represents the socket of an existing
            subparameter. When None is provided, a new
            subparameter must be created to which the widget
            must be attached.
        """
        ### since we'll need it, let's reference the
        ### map for input sockets of this parameter

        param_input_sockets = self.input_socket_live_flmap[param_name]

        ### let's also alias live instances maps using
        ### variables of low character count, for better
        ### code layout

        wl_flmap = self.widget_live_flmap
        wrb_flmap = self.widget_remove_button_flmap
        wab_flmap = self.widget_add_button_flmap

        ### if subparameter index wasn't provided (is None),
        ### then it didn't exist, so store this information
        ### to help make decisions further ahead
        input_socket_not_provided = input_socket is None

        ### if the input socket wasn't created, there's two
        ### things to do, in that order:
        ### 1) create one and retrieve it using its name
        ### 2) create and store "move subparam buttons"

        if input_socket_not_provided:

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

            bottomleft = input_socket.rect.move(2, 0).midright

            move_subparam_up = partial(self.move_subparam_up, input_socket)

            subp_up_button = Button(
                surface=SUBP_UP_BUTTON_SURF,
                command=move_subparam_up,
                coordinates_name="bottomleft",
                coordinates_value=bottomleft,
            )

            sub_flmap = self.subparam_up_button_flmap

            (sub_flmap[param_name][subparam_index]) = subp_up_button

            # this dict subclass instance must be updated
            # every time it is changed
            sub_flmap.update()

            topleft = bottomleft

            move_subparam_down = partial(self.move_subparam_down, input_socket)

            subp_down_button = Button(
                surface=SUBP_DOWN_BUTTON_SURF,
                command=move_subparam_down,
                coordinates_name="topleft",
                coordinates_value=topleft,
            )

            sdb_flmap = self.subparam_down_button_flmap

            (sdb_flmap[param_name][subparam_index]) = subp_down_button

            # this dict subclass instance must be updated
            # every time it is changed
            sdb_flmap.update()

        ### otherwise, just retrieve its index
        else:
            subparam_index = input_socket.subparameter_index

        ### store the widget data in the subwidgets data
        ### map for this subparameter

        (self.data["subparam_widget_map"][param_name][subparam_index]) = widget_data

        ### retrieve widget class using the widget
        ### name from the parameter widget metadata

        widget_name = widget_data["widget_name"]
        widget_cls = WIDGET_CLASS_MAP[widget_name]

        ### retrieve the keyword arguments
        kwargs = widget_data["widget_kwargs"]

        ### put together position data for the widget

        topleft_pos = input_socket.rect.move(15, -1).topright

        pos_data = {"coordinates_name": "topleft", "coordinates_value": topleft_pos}

        ### instantiate the widget using the keyword
        ### arguments from the widget data as well as the
        ### position data

        widget = widget_cls(name=param_name, **kwargs, **pos_data)

        ### store the widget instance in the live map
        ### for widgets and execute its update method
        ### (this map is a custom dict subclass that
        ### needs to be updated whenever we change it;
        ### check its documentation for more)

        wl_flmap[param_name][subparam_index] = widget
        wl_flmap.update()

        ### still considering the case where the
        ### subparameter didn't exist before (the input
        ### socket wasn't provided), we create a list
        ### to hold rects related to the new subparameter
        ### and use it to create a new RectsManager
        ### instance (we use it elsewhere, to position
        ### objects collectively whenever needed)

        if input_socket_not_provided:

            ### create a list to gather rects which will be
            ### used to create a rects manager instance to
            ### control this subparameter
            subrectsman_rects = []

            ### gather the input socket's rect
            subrectsman_rects.append(input_socket.rect)

            ### gather the "move subparam" buttons' rects

            subrectsman_rects.append(subp_up_button.rect)
            subrectsman_rects.append(subp_down_button.rect)

            ### gather the widget's rect
            subrectsman_rects.append(widget.rect)

            ### with the gathered rects, we already
            ### create a subrectsman for this subparameter
            ### (even though we may yet need to add the
            ### keyword entry and definitely will add the
            ### remove button rect); we also add it to the
            ### subparam rectsman map and include it in
            ### the list of rects retrieved from the
            ### param rectsman from its
            ### ('_get_all_rects.__self__' attribute)

            subrectsman = RectsManager(subrectsman_rects.__iter__)

            (self.subparam_rectsman_map[param_name][subparam_index]) = subrectsman

            rect_list = self.param_rectsman_map[param_name]._get_all_rects.__self__

            rect_list.append(subrectsman)

        ### if the subparameter already existed, though,
        ### we just retrieve such RectsManager instance
        ### using the subparam index and get it's list of
        ### rects from its '_get_all_rects.__self__'
        ### attribute, then add the rect for the widget;
        ###
        ### we also remove the add widget button from its
        ### respective live instances map and remove its
        ### rect from the subrectsman for this subparameter

        else:

            ## retrieve the list of rects from the
            ## subrectsman

            subrectsman = self.subparam_rectsman_map[param_name][subparam_index]

            subrectsman_rects = subrectsman._get_all_rects.__self__

            ## gather the widget's rect
            subrectsman_rects.append(widget.rect)

            ## remove add button from its live instance
            ## map and remove its rect from the
            ## subrectsman rects

            # remove add button
            add_button = wab_flmap[param_name].pop(subparam_index)

            # this dict subclass instance needs to be
            # updated every time it is changed
            wab_flmap.update()

            # remove add button rect

            remove_by_identity(
                add_button.rect,
                subrectsman_rects,
            )

        ### if variable is of keyword-variable kind and
        ### the subparam didn't exist before (the input
        ### socket wasn't provided at the beginning)
        ### instantiate a subparam keyword widget (because,
        ### if the subparameter did exist before, such
        ### widget would already exist too)

        if self.var_kind_map[param_name] == "var_key":

            if input_socket_not_provided:

                ## use the left of the widget and the top
                ## of the subrectsman (3 pixels higher by
                ## subtracting the amount) to define a
                ## bottomleft coordinate for the keyword
                ## entry widget

                bottomleft = (input_socket.rect.right + 15, subrectsman.top - 3)

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
                    width=155,
                    command=command,
                    coordinates_name="bottomleft",
                    coordinates_value=bottomleft,
                )

                # store the subparam keyword entry

                (
                    self.subparam_keyword_entry_live_map[subparam_index]
                ) = subparam_keyword_entry

                # gather the subparam keyword rect

                subrectsman_rects.append(subparam_keyword_entry.rect)

                # also store the name of the keyword created
                # in the dedicated map for keyword names

                (self.data["subparam_keyword_map"][subparam_index]) = keyword_name

            ### otherwise we just update the keyword entry
            ### bottom so it takes the widget into account
            ### (that is, between the input socket, subparam
            ### up button and the widget, whichever is
            ### higher)

            else:

                # retrieve the subparam keyword entry

                subparam_keyword_entry = self.subparam_keyword_entry_live_map[
                    subparam_index
                ]

                # choose highest top among input socket,
                # widget and the subparam up button

                subparam_up_rect = self.subparam_up_button_flmap[param_name][
                    subparam_index
                ].rect

                highest_top = min(
                    input_socket.rect.top, widget.rect.top, subparam_up_rect.top
                )

                # define a new bottom for the entry widget
                # which is placed 3 pixels above the highest
                # top we just calculated

                bottom = highest_top - 3
                subparam_keyword_entry.rect.bottom = bottom

        ### create "remove widget" button

        ## define midleft coordinates for the button

        x = widget.rect.right

        midleft = x, input_socket.rect.centery

        ## define command

        command = partial(self.remove_subparameter_widget, widget)

        ## instantiate and store

        button = Button(
            surface=REMOVE_BUTTON_SURF,
            command=command,
            coordinates_name="midleft",
            coordinates_value=midleft,
        )

        ## store the button instance in the respective
        ## map and execute its update method
        ## (this map is a custom dict subclass that
        ## needs to execute this whenever we change it;
        ## check its documentation for more)

        wrb_flmap[param_name][subparam_index] = button
        wrb_flmap.update()

        ## gather the button rect
        subrectsman_rects.append(button.rect)

        ### also define a command to update the
        ### widget value in the node data and
        ### the position of the remove button
        ### (because the widget may change its width
        ### when edited, depending on the kind of
        ### widget), then assign such command to the
        ### 'command' attribute of the widget

        command = partial(update_with_widget, kwargs, "value", widget, button)

        widget.command = command

        ### reposition all objects within the node
        self.reposition_elements()

        ### also perform setups related to the change in
        ### the node body's height
        self.perform_body_height_change_setups()

        ### indicate that changes were made in the data
        indicate_unsaved()

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

        (self.data["subparam_widget_map"][param_name].pop(subparam_index))

        ### remove widget's and remove button's rects from
        ### rects manager for this parameter

        subrectsman = self.subparam_rectsman_map[param_name][subparam_index]

        subrectsman_rects = subrectsman._get_all_rects.__self__

        remove_by_identity(widget.rect, subrectsman_rects)
        remove_by_identity(button.rect, subrectsman_rects)

        ### reference the list of subparameters for
        ### unpacking locally for easier access
        subparams_for_unpacking = self.data["subparam_unpacking_map"][param_name]

        ### retrieve the corresponding input socket instance

        input_socket = self.input_socket_live_flmap[param_name][subparam_index]

        ### perform operations depending on whether the
        ### input socket has a source of data or not

        ## if the input socket has a parent, we just
        ## add a new "add widget" button, for whenever
        ## the user feels like having a widget for the
        ## subparameter again;
        ##
        ## if the parameter is of keyword-variable kind,
        ## we also adjust the keyword entry bottom or
        ## the unpacking icon (if it has one)

        if hasattr(input_socket, "parent"):

            midleft = input_socket.rect.move(15, 0).midright

            command = partial(
                (APP_REFS.ea.widget_creation_popup_menu.trigger_simple_widget_picking),
                self,
                param_name,
                input_socket,
            )

            button = Button(
                surface=ADD_BUTTON_SURF,
                command=command,
                coordinates_name="midleft",
                coordinates_value=midleft,
            )

            wab_flmap = self.widget_add_button_flmap
            wab_flmap[param_name][subparam_index] = button

            ## this custom dict subclass also need its
            ## "update" method executed whenever it is
            ## changed
            wab_flmap.update()

            ## also add the add button rect to the
            ## list of rects managed by this subparameter's
            ## rects manager
            subrectsman_rects.append(button.rect)

            ## since the widget was removed, we should also
            ## reposition the keyword entry or unpacking
            ## icon bottom, that is, if the input has
            ## either, to take into account the height
            ## of the remaining elements;

            if (
                self.var_kind_map[param_name] == "var_key"
                or subparam_index in subparams_for_unpacking
            ):

                obj_to_reposition = (
                    (self.subparam_unpacking_icon_flmap[param_name][subparam_index])
                    if subparam_index in subparams_for_unpacking
                    else (self.subparam_keyword_entry_live_map[subparam_index])
                )

                # retrieve the subparam keyword entry

                # choose highest top among input socket and
                # subparam_up button

                subparam_up_rect = self.subparam_up_button_flmap[param_name][
                    subparam_index
                ].rect

                highest_top = min(input_socket.rect.top, subparam_up_rect.top)

                # define a new bottom for the entry widget
                # which is placed 3 pixels above the highest
                # top we just calculated

                bottom = highest_top - 3
                obj_to_reposition.rect.bottom = bottom

        ## if there's no source of data, that is, no line
        ## segment to an output socket, remove the
        ## input socket and perform needed admin tasks

        else:

            ## remove input socket from live map

            (self.input_socket_live_flmap[param_name].pop(subparam_index))

            # this dict subclass instance must be updated
            # whenever it changes
            self.input_socket_live_flmap.update()

            ## remove the subparam index from the list
            ## in the subparam map

            (self.data["subparam_map"][param_name].remove(subparam_index))

            ## remove "move subparam" buttons

            (self.subparam_up_button_flmap[param_name].pop(subparam_index))

            # this dict subclass instance must be updated
            # whenever it changes
            self.subparam_up_button_flmap.update()

            (self.subparam_down_button_flmap[param_name].pop(subparam_index))

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

                (self.subparam_unpacking_icon_flmap[param_name].pop(subparam_index))

                # this special dict subclass instance must
                # be updated whenever it is changed
                self.subparam_unpacking_icon_flmap.update()

                ## remove subparameter index from list
                ## within the subparameter unpacking map

                (self.data["subparam_unpacking_map"][param_name].remove(subparam_index))

            ## else if the parameter is of keyword-variable
            ## kind remove the keyword entry from the
            ## respective map and the keyword from the
            ## respective map as well

            elif self.var_kind_map[param_name] == "var_key":

                ## remove keyword entry widget

                (self.subparam_keyword_entry_live_map.pop(subparam_index))

                ## remove keyword name from subparameter
                ## keyword map

                (self.data["subparam_keyword_map"].pop(subparam_index))

            ## also update the rectsman hierarchy in order
            ## to take the removal of the subparameter into
            ## account

            # remove the subparameter rectsman from the
            # subparameter rectsman map (we don't need
            # to catch the reference returned, because
            # we already have a reference from a previous
            # block in this same method)

            (self.subparam_rectsman_map[param_name].pop(subparam_index))

            # remove the subrectsman from list in the
            # __self__ attribute of the parameter rectsman
            # _get_all_rects attribute (it contains the
            # bound __iter__ method of the list)

            rect_list = self.param_rectsman_map[param_name]._get_all_rects.__self__

            remove_by_identity(subrectsman, rect_list)

            ## fix names of remaining subparameters
            self.fix_subparameter_indices(param_name)

        ### reposition all objects within the node
        self.reposition_elements()

        ### also perform setups related to the change in
        ### the node body's height
        self.perform_body_height_change_setups()

        ### indicate that changes were made in the data
        indicate_unsaved()
