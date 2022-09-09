"""Facility for subparameter unpacking."""

### standard library import
from functools import partial


### local imports

from ....ourstdlibs.behaviour import remove_by_identity

from ....our3rdlibs.behaviour import indicate_unsaved

from ....classes2d.single import Object2D

from ....widget.stringentry import StringEntry

from ....rectsman.main import RectsManager

from ..constants import FONT_HEIGHT

from ..surfs import (
    UNPACKING_ICON_SURFS_MAP,
)


class UnpackingOps:
    """Unpacking-related operations."""

    def mark_subparameter_for_unpacking(self, input_socket):
        """Mark subparameter for unpacking.

        Parameters
        ==========
        input_socket (InputSocket instance)
            it represents the socket of an existing
            subparameter.
        """
        param_name = input_socket.parameter_name
        subparam_index = input_socket.subparameter_index

        kind = self.var_kind_map[param_name]

        ### reference the list of subparameters for
        ### unpacking locally for easier access
        subparams_for_unpacking = self.data["subparam_unpacking_map"][param_name]

        ### reference the subparam unpacking icon map
        ### locally for easier and quicker access
        sui_flmap = self.subparam_unpacking_icon_flmap

        ## retrieve the list of rects from the
        ## subrectsman

        subrectsman = self.subparam_rectsman_map[param_name][subparam_index]

        subrectsman_rects = subrectsman._get_all_rects.__self__

        ### if variable is of keyword-variable kind, we'll
        ### need to remove the keyword entry from the
        ### live map and the keyword from the data,
        ### as well as the rect of the entry from
        ### the subrectsman rects

        if kind == "var_key":

            keyword_entry = self.subparam_keyword_entry_live_map.pop(subparam_index)

            remove_by_identity(
                keyword_entry.rect,
                subrectsman_rects,
            )

            (self.data["subparam_keyword_map"].pop(subparam_index))

        # put together a bottomleft coordinate for the
        # unpacking icon;
        #
        # for the bottom use the top of the subrectsman
        # (3 pixels higher, by subtracting the amount)

        bottomleft = (input_socket.rect.right + 15, subrectsman.top - 3)

        icon_surf = UNPACKING_ICON_SURFS_MAP[
            (
                kind,
                self.data.get("commented_out", False),
            )
        ]

        unpacking_icon = Object2D.from_surface(
            surface=icon_surf,
            coordinates_name="bottomleft",
            coordinates_value=bottomleft,
        )

        # store the subparam keyword entry
        sui_flmap[param_name][subparam_index] = unpacking_icon

        # this dict subclass instance must be updated
        # every time it is changed
        sui_flmap.update()

        # store reference to unpacking icon's rect
        subrectsman_rects.append(unpacking_icon.rect)

        # mark as subparam for unpacking by appending it
        # to corresponding list
        subparams_for_unpacking.append(subparam_index)
        subparams_for_unpacking.sort()

        ### reposition all objects within the node
        self.reposition_elements()

        ### also perform setups related to the change in
        ### the node body's height
        self.perform_body_height_change_setups()

        ### indicate that changes were made in the data
        indicate_unsaved()

    def unmark_subparameter_for_unpacking(self, input_socket):
        """Unmark subparameter for unpacking.

        Parameters
        ==========
        input_socket (InputSocket instance)
            it represents the socket of an existing
            subparameter.
        """
        param_name = input_socket.parameter_name
        subparam_index = input_socket.subparameter_index

        ### reference the list of subparameters for
        ### unpacking locally for easier access
        subparams_for_unpacking = self.data["subparam_unpacking_map"][param_name]

        ### reference the subparam unpacking icon map
        ### locally for easier and quicker access
        sui_flmap = self.subparam_unpacking_icon_flmap

        ## retrieve the list of rects from the
        ## subrectsman

        subrectsman = self.subparam_rectsman_map[param_name][subparam_index]

        subrectsman_rects = subrectsman._get_all_rects.__self__

        ### remove unpacking icon
        unpacking_icon = sui_flmap[param_name].pop(subparam_index)

        # this dict subclass instance must be updated
        # every time it is changed
        sui_flmap.update()

        ### remove its rect from subrectsman
        remove_by_identity(
            unpacking_icon.rect,
            subrectsman_rects,
        )

        # unmark as subparam for unpacking by removing it
        # from corresponding list
        subparams_for_unpacking.remove(subparam_index)
        subparams_for_unpacking.sort()

        ### if variable is of keyword-variable kind, we'll
        ### need to create a keyword and keyword entry
        ### for it, as well as add the entry's rect to
        ### the list of subrectsman's rects

        if self.var_kind_map[param_name] == "var_key":

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

        ### reposition all objects within the node
        self.reposition_elements()

        ### also perform setups related to the change in
        ### the node body's height
        self.perform_body_height_change_setups()

        ### indicate that changes were made in the data
        indicate_unsaved()
