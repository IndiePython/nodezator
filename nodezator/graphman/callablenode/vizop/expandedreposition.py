"""Function to extend VisualRelatedOperations class."""

### third-party import
from pygame import Rect


### local imports

from ....config import APP_REFS

from ....rectsman.main import RectsManager

from ...socket.surfs import SOCKET_DIAMETER

from ..constants import (
    FONT_HEIGHT,
    BODY_CONTENT_OFFSET,
    NODE_OUTLINE_THICKNESS,
    SUBPARAM_OFFSET_FROM_LABEL,
    DISTANCE_BETWEEN_PARAMS,
    DISTANCE_BETWEEN_SUBPARAMS,
    DISTANCE_BETWEEN_OUTPUTS,
    INPUT_OFFSET,
)



SOCKET_RADIUS = SOCKET_DIAMETER // 2


def reposition_expanded_elements(self):
    """Reposition objects inside the node in expanded signature mode.

    The repositioning is made from the input
    downwards (the top rectsman doesn't need to be
    repositioned, it always stays at the same relative
    position within the node).

    Another administrative task is performed, which is
    updating the height of self.rect.
    """
    ### reference subparameter unpacking map locally
    subparam_unpacking_map = self.data["subparam_unpacking_map"]

    ### let's also reference maps of live instances locally using
    ### variables of low character count, for better code layout

    isl_flmap = self.input_socket_live_flmap
    sub_flmap = self.subparam_up_button_flmap
    sdb_flmap = self.subparam_down_button_flmap
    wl_flmap = self.widget_live_flmap
    sui_flmap = self.subparam_unpacking_icon_flmap
    skl_map = self.subparam_keyword_entry_live_map
    wrb_flmap = self.widget_remove_button_flmap
    pab_map = self.placeholder_add_button_map
    psl_map = self.placeholder_socket_live_map

    prm_map = self.param_rectsman_map
    srm_map = self.subparam_rectsman_map

    ### reference the lists of visible widgets and remove buttons
    ### locally; and clear them

    vws = self.visible_widgets
    vbs = self.visible_remove_widget_buttons

    vws.clear()
    vbs.clear()

    ### create a rect representing the height of text
    ### surfaces used in the node
    text_rect = Rect(0, 0, 0, FONT_HEIGHT)

    ### reference the top rectsman and its sides locally

    top_rectsman = self.top_rectsman
    top_rectsman_left = top_rectsman.left
    top_rectsman_right = top_rectsman.right

    ### define a top coordinate which is the bottom of
    ### the top of the node plus the body content
    ### offset given as a constant
    top = top_rectsman.bottom + BODY_CONTENT_OFFSET

    ### position each output socket

    ## get names of output sockets (their order is defined
    ## in the node script)
    socket_names = self.ordered_output_type_map.keys()

    ## get name of last socket
    last_socket_name = list(socket_names)[-1]

    ## reference the output socket map locally
    osl_map = self.output_socket_live_map

    ## iterate over socket names, retrieving the rect of
    ## each socket in order to position it

    for output_name in socket_names:

        ## retrieve socket rect
        socket_rect = osl_map[output_name].rect

        ## position the socket horizontally
        socket_rect.centerx = top_rectsman_right

        ## align text rect center with the center of the
        ## socket, offset 2 pixels up
        text_rect.centery = socket_rect.move(0, -2).centery

        ## position text rect and socket rect together
        ## as if they were a single rect by controlling
        ## them through a temporary rects manager instance

        # instantiate rectsman
        temp_rectsman = RectsManager((text_rect, socket_rect).__iter__)

        # assign top to the temporary rectsman
        temp_rectsman.top = top

        # new top is the bottom of the temp rectsman
        top = temp_rectsman.bottom

        ## if the socket isn't the last one, increment
        ## the top with the distance between outputs
        ## given as a constant

        if output_name != last_socket_name:
            top += DISTANCE_BETWEEN_OUTPUTS

    ### position parameters

    ## retrieve parameter objects (they're ordered)
    parameters = self.signature_obj.parameters.values()

    ## if there are parameters...

    if parameters:

        ## offset the defined top by the input offset
        ## given as a constant
        top += INPUT_OFFSET

        ## also store the name of the last one (we'll use it soon)
        last_param_name = list(parameters)[-1].name

    ## iterate over parameter objects positioning each
    ## of them

    for param_obj in parameters:

        ## retrieve name of parameter
        param_name = param_obj.name

        ## retrieve the rectsman representing the
        ## parameter, as well as the list of the
        ## underlying rects it controls

        param_rectsman = prm_map[param_name]
        param_rects = param_rectsman._get_all_rects.__self__

        ## clear the list
        param_rects.clear()


        ## try retrieving the variable kind of the
        ## parameter
        try:
            kind = self.var_kind_map[param_name]

        ## if the retrieval fails, then we have
        ## a regular parameter

        except KeyError:

            ## reference the input socket
            input_socket = isl_flmap[param_name]

            ## its centerx must be the top_rectsman left
            input_socket.rect.centerx = top_rectsman_left

            ## store the input socket's rect as a
            ## parameter's rect
            param_rects.append(input_socket.rect)

            ## check whether input socket has a parent

            has_parent = (

                (self.id, param_name) in APP_REFS.gm.parented_sockets_ids
                if hasattr(APP_REFS.gm, 'parented_sockets_ids')

                else hasattr(input_socket, 'parent')

            )

            ## check wheter it has a widget
            has_widget = param_name in wl_flmap

            ## if it has a parent or doesn't have a widget,
            ## we have only the input socket, in the parameter,
            ## so we align the vertical center of both the text rect
            ## and input socket (with just a bit offset) and perform
            ## the calculation as if they were a single object by
            ## temporarily appending the text rect to the list of
            ## rects managed by the rectsman

            if has_parent or not has_widget:

                # align vertical center of both text rect and input socket
                # (with a bit offset)
                text_rect.centery = input_socket.rect.move(0, -2).centery

                # position object as one, by appending
                # text rect temporarily to the rect list

                param_rects.append(text_rect)

                param_rectsman.top = top

                top = param_rectsman.bottom

                param_rects.pop()

            ## otherwise, if we have a widget, we perform related setups

            elif has_widget:

                ## reference widget locally
                widget = wl_flmap[param_name]

                ## position it and store it as a visible one

                widget.rect.topleft = input_socket.rect.move(8, -1).topright
                vws.append(widget)

                ## store its rect among the parameter's rects
                param_rects.append(widget.rect)

                ## since the widget is beside the socket, the
                ## parameter text will be above the input socket
                ## and visible widget

                text_rect.top = top

                param_rectsman.top = text_rect.bottom + 2

                top = param_rectsman.bottom

        ## otherwise, we are dealing with a variable
        ## parameter

        else:

            ## variable parameters always start with the
            ## name of the parameter on top, so we begin
            ## by positioning the top rect on top
            text_rect.top = top

            ## the top for the next object will be below
            ## the text rect plus an offset given as a
            ## constant
            top = text_rect.bottom + SUBPARAM_OFFSET_FROM_LABEL

            ## we then retrieve the names of the
            ## subparameters sorted
            sorted_subparam_indices = sorted(self.input_socket_live_flmap[param_name])

            ## if there are indeed subparameters, store the
            ## name of the last one (we'll use it soon)

            if sorted_subparam_indices:
                last_subparam_index = sorted_subparam_indices[-1]

            ## retrieve the list of unpacked subparameter indices
            subparams_for_unpacking = subparam_unpacking_map[param_name]

            ## iterate over each subparameter index in order,
            ## repositioning each subparameter as you go

            for subparam_index in sorted_subparam_indices:

                # retrieve rectsman for the subparameter and its list
                # of rects

                subparam_rectsman = srm_map[param_name][subparam_index]
                subparam_rects = subparam_rectsman._get_all_rects.__self__

                # clear the list
                subparam_rects.clear()

                # reference input socket
                input_socket = isl_flmap[param_name][subparam_index]

                ## its centerx must be the top_rectsman left
                input_socket.rect.centerx = top_rectsman_left

                ## store the input socket's rect as a subparameter's
                ## rect
                subparam_rects.append(input_socket.rect)

                ## retrieve buttons to move the subparameter, position
                ## them and store their rects as subparameter's rects

                subp_up_button = sub_flmap[param_name][subparam_index]
                subp_down_button = sdb_flmap[param_name][subparam_index]

                offset_midright = input_socket.rect.move(2, 0).midright

                subp_up_button.rect.bottomleft = offset_midright
                subp_down_button.rect.topleft = offset_midright

                subparam_rects.append(subp_up_button.rect)
                subparam_rects.append(subp_down_button.rect)

                ## check whether the subparameter has a parent

                has_parent = (

                    (
                        (self.id, param_name, subparam_index)
                        in APP_REFS.gm.parented_sockets_ids
                    )
                    if hasattr(APP_REFS.gm, 'parented_sockets_ids')

                    else hasattr(input_socket, 'parent')

                )

                ## check whether the subparameter is unpacked
                is_unpacked = subparam_index in subparams_for_unpacking

                ## if the subparameter is unpacked, retrieve the
                ## unpacking icon rect

                if is_unpacked:
                    unpacking_icon_rect = sui_flmap[param_name][subparam_index].rect

                ## if it has a parent...

                if has_parent:
                    
                    ## if it is unpacked...

                    if is_unpacked:

                        # position the unpacking icon rect and add it to the
                        # list of subparameter rects

                        unpacking_icon_rect.midleft = (
                            subp_up_button.rect.move(3, 0).bottomright
                            if kind == 'var_pos'
                            else subp_up_button.rect.move(18, 0).bottomright
                        )

                        subparam_rects.append(unpacking_icon_rect)

                    ## if it is of keyword variable kind...

                    elif kind == 'var_key':

                        ## position the keyword entry and add its rect to the
                        ## list of rects of the subparameter

                        keyword_entry = skl_map[subparam_index]

                        keyword_entry.rect.midleft = (
                            subp_up_button.rect.move(18, 0).bottomright
                        )

                        subparam_rects.append(keyword_entry.rect)

                        ## add it to the list of visible widgets
                        vws.append(keyword_entry)

                ## if it doesn't have a parent...

                else:
                    
                    ## reference the widget and its remove button locally

                    widget = wl_flmap[param_name][subparam_index]
                    remove_button = wrb_flmap[param_name][subparam_index]

                    ## add them to the respective lists of visible objects

                    vws.append(widget)
                    vbs.append(remove_button)

                    ## position them and add their rects as part of the
                    ## subparameter

                    widget.rect.topleft = (
                        subp_up_button.rect.move(3, 0).topright
                    )

                    remove_button.rect.midleft = (
                        widget.rect.right, input_socket.rect.centery
                    )

                    subparam_rects.append(widget.rect)
                    subparam_rects.append(remove_button.rect)


                    ## if it is unpacked...

                    if is_unpacked:

                        # position the unpacking icon rect and add it to the
                        # list of subparameter rects

                        unpacking_icon_rect.bottomleft = (
                            subp_up_button.rect.move(3, -2).topright
                        )

                        subparam_rects.append(unpacking_icon_rect)

                    ## if it is of keyword variable kind...

                    elif kind == 'var_key':

                        ## position the keyword entry and add its rect to the
                        ## list of rects of the subparameter

                        keyword_entry = skl_map[subparam_index]

                        keyword_entry.rect.bottomleft = (
                            subp_up_button.rect.move(3, -2).topright
                        )

                        subparam_rects.append(keyword_entry.rect)

                        ## add it to the list of visible widgets
                        vws.append(keyword_entry)


                # assign top
                subparam_rectsman.top = top

                # define new top
                top = subparam_rectsman.bottom

                # add subparam rectsman to list of rects for the parameter
                param_rects.append(subparam_rectsman)

                # if the subparameter isn't the last one,
                # increment the top with the distance
                # between subparameters given as a constant

                if subparam_index != last_subparam_index:
                    top += DISTANCE_BETWEEN_SUBPARAMS

            ## retrieve the rects from the placeholder
            ## socket and the "add subparameter button"

            socket_rect = self.placeholder_socket_live_map[param_name].rect

            button_rect = self.placeholder_add_button_map[param_name].rect

            ## position the placeholder socket horizontally
            socket_rect.centerx = top_rectsman_left

            ## put the "add subparameter button" a bit to the
            ## right of the placeholder, both vertically
            ## aligned
            button_rect.midleft = socket_rect.move(5, 0).midright

            ## reposition socket rect and button rect
            ## together as if they were a single rect
            ## by controlling them through a temporary
            ## rects manager instance

            # instantiate rectsman
            temp_rectsman = RectsManager((socket_rect, button_rect).__iter__)

            # assign the defined top and add 4 pixels, to
            # push them just a bit down for extra padding
            temp_rectsman.top = top + 4

            # define the bottom of the rectsman as the new top
            # to be used by the next parameter
            top = temp_rectsman.bottom

            ## add the rects of the placeholder socket and add button as
            ## part of the parameter's rects

            param_rects.append(socket_rect)
            param_rects.append(button_rect)

        ## if the parameter being positioned isn't the
        ## last one, increment the top with the distance
        ## between parameters given as a constant

        if param_name != last_param_name:
            top += DISTANCE_BETWEEN_PARAMS

    ### position the id text object

    ## reference the rect of the id text object locally
    id_text_rect = self.id_text_obj.rect

    ## align its top with the last defined top; also push it
    ## 4 pixels down for extra padding
    id_text_rect.top = top + 4

    ## align the centerx of the id text object with
    ## the centerx of the top rectsman, so it is
    ## horizontally centered on the node
    id_text_rect.centerx = top_rectsman.centerx

    ### position the bottom rectsman

    ## reference the bottom rectsman in a local variable
    bottom_rectsman = self.bottom_rectsman

    ## align the centerx of the bottom rectsman with
    ## the centerx of the top rectsman, so it is
    ## horizontally centered on the node
    bottom_rectsman.centerx = top_rectsman.centerx

    ## align the bottom of the bottom rectsman with
    ## the bottom of the id text object, then push
    ## the bottom rectsman just a bit down in order
    ## to compensate for the node outline and add
    ## a bit of padding

    bottom_rectsman.bottom = id_text_rect.bottom
    bottom_rectsman.top += NODE_OUTLINE_THICKNESS + 4

    ### perform extra administrative task: update size and position
    ### of self.rect

    ## width

    left = (

        ## if there are parameters...
        self.input_rectsman.left
        if parameters

        ## otherwise...
        else top_rectsman.move(-SOCKET_RADIUS, 0).left

    )

    right = (

        ## if there are outputs (always the case, at least for now)
        self.output_rectsman.right
        if osl_map

        ## otherwise...
        else top_rectsman.move(SOCKET_RADIUS, 0).right
    )

    self.rect.width = right - left

    ## height
    self.rect.height = bottom_rectsman.bottom - top_rectsman.top

    ## midtop
    self.rect.midtop = top_rectsman.midtop
