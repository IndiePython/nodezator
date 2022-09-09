"""Facility for operations on subparameters via segments."""

### standard library import
from functools import partial


### local imports

from ....config import APP_REFS

from ....ourstdlibs.behaviour import remove_by_identity

from ....our3rdlibs.button import Button

from ....widget.stringentry import StringEntry

from ....rectsman.main import RectsManager

from ..surfs import (
    ADD_BUTTON_SURF,
    SUBP_UP_BUTTON_SURF,
    SUBP_DOWN_BUTTON_SURF,
)

from ..constants import FONT_HEIGHT


class SegmentOps:
    """Segment related operations on subparameters."""

    def get_input_socket(self, param_name):
        """Return new input socket for named parameter.

        Parameters
        ==========

        param_name (string)
            represents name of the parameter for which the
            new input socket will be created and returned
        """
        ### reference the map for input sockets for this
        ### parameter
        param_input_sockets = self.input_socket_live_flmap[param_name]

        ### create a new input socket (input sockets
        ### represent parameters/subparameters, so this
        ### is the equivalent of creating a subparameter)
        self.create_new_input_socket(param_name)

        ### retrieve the subparameter index for the
        ### subparameter we just created; it is a key in
        ### the map containing input sockets for the
        ### parameter; the keys are integers and
        ### the one we want is the highest among them all
        subparam_index = max(param_input_sockets)

        ### use the subparameter index to retrieve the
        ### input socket representing the subparameter
        input_socket = param_input_sockets[subparam_index]

        ### create a list to hold rects for a new
        ### subparameter rect, which we create on the spot

        ## create a list to gather rects which will be
        ## used to create a rects manager instance to
        ## control this subparameter
        subrectsman_rects = []

        ## gather the input socket's rect
        subrectsman_rects.append(input_socket.rect)

        ### create new "move subparam" buttons to be put
        ### alongside the created socket

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

        # gather the button's rect
        subrectsman_rects.append(subp_up_button.rect)

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

        # gather the button's rect
        subrectsman_rects.append(subp_down_button.rect)

        ### create a new "add widget" button to be put
        ### alongside the created socket,
        ### so that users can optionally create a
        ### subparameter widget for the input socket
        ### whenever they want

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

        ## gather the add button's rect
        subrectsman_rects.append(button.rect)

        ## with the gathered rects, we already
        ## create a subrectsman for this subparameter
        ## (even though we may yet need to add the
        ## keyword entry); we also add it to the
        ## subparam rectsman map and include it in
        ## the list of rects retrieved from the
        ## param rectsman from its
        ## ('_get_all_rects.__self__' attribute)

        subrectsman = RectsManager(subrectsman_rects.__iter__)

        (self.subparam_rectsman_map[param_name][subparam_index]) = subrectsman

        rect_list = self.param_rectsman_map[param_name]._get_all_rects.__self__

        rect_list.append(subrectsman)

        ### if variable is of keyword-variable kind
        ### instantiate a subparam keyword widget

        if self.var_kind_map[param_name] == "var_key":

            ## use the left of the add button and the top
            ## of the subrectsman (3 pixels higher by
            ## subtracting the amount) to define a
            ## bottomleft coordinate for the keyword
            ## entry widget

            bottomleft = (input_socket.rect.right + 15, subrectsman.top - 3)

            ## define a name for the keyword
            keyword_name = self.get_new_keyword_name()

            ## put together a command which takes proper
            ## measures when updating the keyword name
            command = partial(self.update_keyword, input_socket)

            ## instantiate the keyword entry and take
            ## additional measures

            # instantiate

            subparam_keyword_entry = StringEntry(
                value=keyword_name,
                font_height=FONT_HEIGHT,
                width=155,
                coordinates_name="bottomleft",
                coordinates_value=bottomleft,
                command=command,
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

        ### reposition all objects within the node
        self.reposition_elements()

        ### also perform extra admin tasks, related to
        ### the change in the node body's height
        self.perform_body_height_change_setups()

        ### finally, return a reference to the new input
        ### socket created
        return input_socket

    def react_to_severance(self, input_socket):
        """Check need to react to severance.

        Works by checking if input socket which just lost
        its line segment has a widget. If not, the
        subparameter must be removed and related admin tasks
        must be performed

        Parameters
        ==========
        input_socket (input socket instance)
            input socket for subparameter which just had
            its line segment severed.
        """
        ### obtain parameter name and subparameter index
        ### from input socket

        param_name = input_socket.parameter_name
        subparam_index = input_socket.subparameter_index

        ### use the parameter name to obtain a map of
        ### subparameter widgets
        subparam_widgets = self.widget_live_flmap[param_name]

        ### reference the list of subparameters for
        ### unpacking locally for easier access
        subparams_for_unpacking = self.data["subparam_unpacking_map"][param_name]

        ### try accessing a widget instance for the
        ### subparameter using its index
        try:
            subparam_widgets[subparam_index]

        ### if the attempt fails, then the recently severed
        ### input socket must be removed, since it has no
        ### widget from which to obtain data when executed

        except KeyError:

            ## remove input socket

            (self.input_socket_live_flmap[param_name].pop(subparam_index))

            # this dict subclass instance must be updated
            # whenever it changes
            self.input_socket_live_flmap.update()

            ## remove the subparam index from list inside
            ## subparam map

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

            ## remove the add widget button for the
            ## subparameter

            (self.widget_add_button_flmap[param_name].pop(subparam_index))

            # this special dict subclass instance must
            # be updated whenever it is changed
            self.widget_add_button_flmap.update()

            ## also update the rectsman hierarchy in order
            ## to take the removal of the subparameter into
            ## account

            # remove the subparameter rectsman from the
            # subparameter rectsman map

            subrectsman = self.subparam_rectsman_map[param_name].pop(subparam_index)

            # remove the subrectsman from list in the
            # __self__ attribute of the parameter rectsman
            # _get_all_rects attribute (it contains the
            # bound __iter__ method of the list)

            rect_list = self.param_rectsman_map[param_name]._get_all_rects.__self__

            remove_by_identity(subrectsman, rect_list)

            ## fix names of remaining subparameters
            self.fix_subparameter_indices(param_name)

            ## reposition all objects within the node
            self.reposition_elements()

            ### also perform extra admin tasks, related to
            ### the change in the node body's height
            self.perform_body_height_change_setups()

        ### if accessing the widget is sucessful, then no
        ### additional measure is needed, since the input
        ### socket is kept because it has a source of data
        ### (the widget); this is why this try/except clause
        ### doesn't need an additional 'else' clause;
