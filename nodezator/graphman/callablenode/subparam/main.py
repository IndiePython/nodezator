"""Class extension for subparameter operations."""

### standard library import
from functools import partialmethod


### local imports

from ....config import APP_REFS

from ....dialog import create_and_show_dialog

from ....our3rdlibs.behaviour import indicate_unsaved

from ...socket.input import InputSocket

from ...socket.surfs import type_to_codename

## class extensions

from .widget import WidgetOps
from .segment import SegmentOps
from .unpacking import UnpackingOps


class SubparameterHandling(
    WidgetOps,
    SegmentOps,
    UnpackingOps,
):
    """Methods for handling subparameter operations.

    Subparameters have somewhat complex handling. They
    can be created by providing a source of data. This
    source can be either a connection to an output socket
    of another node or a new widget provided to it.

    In the same manner, if such sources of data are removed,
    the subparameters disappears and the existing ones
    must be rearranged and renamed to reflect the actual
    number of existings subparameters for a parameter.
    """

    def create_new_input_socket(self, param_name):
        """Create a new input socket.

        Works by creating an input socket representing
        a new subparameter.

        Parameters
        ==========
        param_name (string)
            name of the variable kind parameter for which
            we'll create a new subparameter.
        """
        ### retrieve subparam indices map for the parameter
        subparam_indices = self.data["subparam_map"][param_name]

        ### create a subparam index by going through the
        ### existing keys and incrementing the highest one

        ## try obtaining the highest the keys which
        ## represents the highest integer
        try:
            highest_key = max(subparam_indices)

        ## max will fail with a ValueError if the iterable
        ## it receives is empty (dict has no keys); in such
        ## case, use the default "0" as the subparameter
        ## name
        except ValueError:
            subparam_index = 0

        ## otherwise increment the highest key
        else:
            subparam_index = highest_key + 1

        ### append the new subparam index to the subparam
        ### names map for the parameter representing the
        ### socket data and also alias it in a local
        ### variable called "socket_data"
        subparam_indices.append(subparam_index)

        ### also retrieve the expected type of the
        ### parameter and use it to obtain a string
        ### representing a codename for the type;
        ###
        ### no type enforcement is ever performed,
        ### though

        expected_type = self.type_map[param_name]
        type_codename = type_to_codename(expected_type)

        ### define a temporary center for the input socket
        center = self.top_rectsman.left, 0

        ### instantiate input socket

        input_socket = InputSocket(
            node=self,
            type_codename=type_codename,
            parameter_name=param_name,
            subparameter_index=subparam_index,
            center=center,
        )

        ### store the input socket instance in the live
        ### instance map for input sockets (this custom
        ### dict subclass also need its "update" method
        ### executed whenever it is changed)

        (self.input_socket_live_flmap[param_name][subparam_index]) = input_socket

        self.input_socket_live_flmap.update()

    def get_new_keyword_name(self):
        """Return a new unique keyword name."""
        ### retrieve iterable of existing keywords
        existing_keywords = self.data["subparam_keyword_map"].values()

        ### retrieve their quantity
        number_of_keywords = len(existing_keywords)

        ### iterate over the indices from zero up to
        ### one unit after the number of existing
        ### keyword names, generating a new keyword based
        ### on each index and breaking out of the loop
        ### if it isn't present among the existing ones
        ### (this way, it is guaranteed that we'll find a
        ### non-existent keyword name, since we are checking
        ### more combinations than the number of available
        ### names)

        for index in range(number_of_keywords + 1):

            ## create a keyword name
            keyword_name = "keyword_" + str(index)

            ## if the name isn't used, you can break
            ## out of the loop
            if keyword_name not in existing_keywords:
                break

        ### since the algorithm for this method guarantees
        ### that we'll break out of the for loop above,
        ### we should not enter this 'else' clause, so we
        ### raise an error to indicate something is wrong
        ### with the implementation if such happens

        else:

            raise RuntimeError(
                "this 'else' clause shouldn't execute, so"
                " please, verify this method's implementation"
            )

        ### if we broke out of the 'for' loop successfully,
        ### then an available keyword_name was found; we
        ### can now return it
        return keyword_name

    def update_keyword(self, input_socket):
        """Store the new name of the keyword.

        Note that the name of the parameter isn't needed,
        since a function can only have one single
        keyword-variable parameter anyway.

        Parameters
        ==========

        input_socket (input socket object)
            input socket representing subparameter to which
            the keyword is associated.
        """
        ### retrieve the index of the subparameter from the
        ### input socket
        subparam_index = input_socket.subparameter_index

        ### retrieve the respective keyword entry and
        ### its value using the subparameter index (instead
        ### of just storing the value, we also store a
        ### reference to the entry widget, because we might
        ### use it further ahead); the value in question is
        ### the new keyword name to be set

        keyword_entry = self.subparam_keyword_entry_live_map[subparam_index]

        new_keyword = keyword_entry.get()

        ### retrieve subparam_keyword_map
        subparam_keyword_map = self.data["subparam_keyword_map"]

        ### set an appropriate error message according to
        ### whether the new keyword name is available or not
        ### (the "if" and "elif" blocks below represent
        ### actual forbidden situations which cause
        ### SyntaxError when they happen in a function call).
        ###
        ### I'd prefer to handle the SyntaxError during the
        ### actual function call, but we are forced to do
        ### it here because during execution of the node
        ### the inputs for each subparameter are stored in
        ### a map using the keyword names as keys.
        ###
        ### This would make the duplicate keyword override
        ### the original one, causing the value of the
        ### original keyword to be lost and making the
        ### function not complain, which in summary would
        ### a bug.

        if new_keyword in subparam_keyword_map.values():

            error_msg = (
                "subparameter keyword can't be the same as"
                " other existing subparameter keywords"
            )

        elif (
            new_keyword in self.signature_obj.parameters.keys()
            and new_keyword not in self.var_kind_map.keys()
        ):

            error_msg = (
                "subparameter keyword can't be the same as"
                " the name of a regular parameter"
            )

        else:
            error_msg = ""

        ### if an error message was not set, you can
        ### safely store the new keyword

        if not error_msg:

            subparam_keyword_map[subparam_index] = new_keyword

        ### otherwise, you must revert to the previous
        ### keyword and inform the user with the error
        ### message (which is slightly incremented)

        else:

            ## retrieve old keyword
            previous_keyword = subparam_keyword_map[subparam_index]

            ## set the old value back on the keyword entry
            ## passing False along the value, to prevent
            ## this method to be called again recursively
            keyword_entry.set(previous_keyword, False)

            ## inform user of the situation

            # increment error message

            error_msg += ". The keyword was set back to its previous" " value"

            # display it in a dialog box
            create_and_show_dialog(error_msg)

    def fix_subparameter_indices(self, param_name):
        """Fix subparameter which doesn't conform to design.

        Works by ensuring subparameter indices go from 0 to n
        in increments of 1 (n = length - 1), that is, that
        there's no gap between the numbers.

        While looking for gaps in the subparameter indices,
        this function puts together a list with the data
        needed to fix the problem and delegates the actual
        corrections to another method.
        """
        ### reference list of subparam indices for this
        ### parameter
        subparam_indices = self.data["subparam_map"][param_name]

        ### obtain a new list from it, sorting the contents
        sorted_subparam_indices = sorted(subparam_indices)

        ### iterate over the sorted subparam indices,
        ### discovering the ones which need to be fixed

        ## create list to store changes needed
        needed_changes = []

        ## iterate

        for right_index, subparam_index in enumerate(sorted_subparam_indices):

            ## alias the subparam_index as the current
            ## one
            current_index = subparam_index

            ## if the current name is different from
            ## the expected right name, we store a
            ## tuple with both names in the 'changes'
            ## list

            if current_index != right_index:

                needed_changes.append((current_index, right_index))

        ### now that you put together a list containing
        ### the data for the changes to be made, you can
        ### finally delegate the actual changing operations
        ### to another method (this is ok even if the list
        ### of needed changes is empty)

        self.change_subparameter_indices(
            param_name,
            needed_changes,
        )

    def move_subparam(self, input_socket, orientation):
        """Move subparameter one position up or down.

        Works by making the subparameter swap positions
        with its neighbour subparameter above or below it.
        """
        ### store parameter name in local variable
        param_name = input_socket.parameter_name

        ### reference list of subparam indices for this
        ### parameter
        subparam_indices = self.data["subparam_map"][param_name]

        ### retrieve the number of existing subparameters
        ### (length)
        length = len(subparam_indices)

        ### if length is only one, return earlier, since
        ### there's no position to change
        if length == 1:
            return

        ### give special names to some specific subparameters

        first_subparam_index = 0
        last_subparam_index = max(subparam_indices)

        ### retrieve the subparameter index (it represents
        ### its order/position from top to bottom)
        our_subparam_index = input_socket.subparameter_index

        ### otherwise, act according to orientation of
        ### movement and current position of the
        ### subparameter represented by the input socket

        if orientation == "up":

            ### if the subparameter is already the
            ### first one, return earlier, since there's
            ### no way to move it up any further
            if our_subparam_index == first_subparam_index:
                return

            ### otherwise, define an integer representing
            ### the distance between the current subparameter
            ### position to the desired one
            distance = -1

        elif orientation == "down":

            ### if the subparameter is already the
            ### last one, return earlier, since there's
            ### no way to move it down any further
            if our_subparam_index == last_subparam_index:
                return

            ### otherwise, define an integer representing
            ### the distance between the current subparameter
            ### position to the desired one
            distance = 1

        else:

            raise ValueError(
                "There shouldn't be another" " orientation besides 'up' or 'down'"
            )

        ### with the distance defined before, obtain the
        ### name of the neighbour subparameter whose
        ### position we want for our subparameter
        neighbour_subparam_index = our_subparam_index + distance

        ### create a temporary subparameteter name (note
        ### that a subparameter with this name don't exist
        ### yet)
        temp_subparam_index = last_subparam_index + 1

        ### swap the positions between the names we have,
        ### so that in the end our original subparam index
        ### ends up with the name of its neighbour and
        ### vice-versa

        ## list pairs indicating a subparameter index and
        ## the index which it should assume, the order is
        ## important in order to avoid having the indices
        ## overlap each other (that is, an index must
        ## always be changed to one which don't exist at
        ## the time of the change)

        changes = [
            (neighbour_subparam_index, temp_subparam_index),
            (our_subparam_index, neighbour_subparam_index),
            (temp_subparam_index, our_subparam_index),
        ]

        ## apply changes
        self.change_subparameter_indices(param_name, changes)

        ### reposition all objects within the node
        self.reposition_elements()

        ### indicate that changes were made in the data
        indicate_unsaved()

    move_subparam_up = partialmethod(move_subparam, orientation="up")

    move_subparam_down = partialmethod(move_subparam, orientation="down")

    def change_subparameter_indices(
        self,
        param_name,
        changes,
    ):
        """Change the name of subparameters listed.

        Parameters
        ==========

        param_name (string)
            name of the parameters whose subparameters
            will have their names changes
        changes (list of 2-tuples)
            contains pairs of indices where the first
            index represents the current index of the
            subparameter and the second one the new
            index to be assumed by it. It is ok if it
            is empty, in which case no changes take
            place.
        """
        ### reference list of subparam indices for this
        ### parameter
        subparam_indices = self.data["subparam_map"][param_name]

        ### reference list of subparams for unpacking for
        ### the parameter
        subparams_for_unpacking = self.data["subparam_unpacking_map"][param_name]

        ### reference map containing subparam unpacking
        ### icon flmap for the parameter

        unpacking_icon_flmap_for_param = self.subparam_unpacking_icon_flmap[param_name]

        ### list all maps that need to be fixed in case any
        ### subparameter needs to have its name fixed

        maps_to_fix = (
            self.data["subparam_widget_map"][param_name],
            self.input_socket_live_flmap[param_name],
            self.subparam_up_button_flmap[param_name],
            self.subparam_down_button_flmap[param_name],
            self.widget_live_flmap[param_name],
            self.widget_add_button_flmap[param_name],
            self.widget_remove_button_flmap[param_name],
            self.subparam_rectsman_map[param_name],
        )

        ### iterate over needed changes, performing them
        ### one by one

        for current_index, right_index in changes:

            ## fix subparam index

            i = subparam_indices.index(current_index)
            subparam_indices[i] = right_index

            ## fix maps

            for item in maps_to_fix:

                # if the current index exists in the
                # map, pop its value and assign it
                # to the right name

                try:
                    value = item.pop(current_index)
                except KeyError:
                    pass
                else:
                    item[right_index] = value

                # using 'update' without arguments
                # has no effect in built-in dict
                # instances, but has a special
                # effect on a special dict subclass
                # we use, which needs this operation
                # whenever it is changed
                item.update()

            ## if the subparameter is marked for
            ## unpacking, fix the index in related
            ## maps

            if current_index in subparams_for_unpacking:

                (
                    unpacking_icon_flmap_for_param[right_index]
                ) = unpacking_icon_flmap_for_param.pop(current_index)

                ## since the flat values list didn't
                ## actually change, the call which is
                ## commented out below isn't actually
                ## needed, but we keep it just to
                ## serve as an example where changing
                ## flat list dict instances doesn't
                ## require it to be updated
                ## self.subparam_unpacking_icon_flmap.update()

                ###

                subparams_for_unpacking.remove(current_index)

                subparams_for_unpacking.append(right_index)

                subparams_for_unpacking.sort()

            ## else if the parameter is of keyword variable
            ## kind, fix the index in the related maps

            elif self.var_kind_map[param_name] == "var_key":

                (
                    self.subparam_keyword_entry_live_map[right_index]
                ) = self.subparam_keyword_entry_live_map.pop(current_index)

                (self.data["subparam_keyword_map"][right_index]) = self.data[
                    "subparam_keyword_map"
                ].pop(current_index)

            ## retrieve a reference to the input socket

            input_socket = self.input_socket_live_flmap[param_name][right_index]

            ## store its current custom id and update its
            ## subparameter index with the right name

            old_id = input_socket.get_id()
            input_socket.subparameter_index = right_index

            ## if the input socket has a parent, fix the
            ## socket tree data to take the change in the
            ## subparameter index into account

            try:
                input_socket.parent

            except AttributeError:
                pass

            else:
                APP_REFS.gm.fix_input_socket_id(
                    input_socket,
                    old_id,
                )
