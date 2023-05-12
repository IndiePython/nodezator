"""Facility with function for injection."""

### standard library import
from functools import partial


### local imports

from ....our3rdlibs.button import Button

from ....widget.stringentry import StringEntry

from ....rectsman.main import RectsManager

from ..surfs import (
    SUBP_UP_BUTTON_SURF,
    SUBP_DOWN_BUTTON_SURF,
)

from ..constants import FONT_HEIGHT, SUBPARAM_KEYWORD_ENTRY_WIDTH



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

    ### create new "move subparam" buttons to be put
    ### alongside the created socket

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

    ###
    self.subparam_rectsman_map[param_name][subparam_index] = (
        RectsManager([].__iter__)
    )

    ### if variable is of keyword-variable kind
    ### instantiate a subparam keyword widget

    if self.var_kind_map[param_name] == "var_key":

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

    ### store reference to input socket in a dedicated attribute
    self.new_subparam_input_socket = input_socket

    ### finally, return a reference to the new input
    ### socket created
    return input_socket
