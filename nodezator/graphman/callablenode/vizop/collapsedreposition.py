"""Function to extend VisualRelatedOperations class."""

### third-party import
from pygame import Rect


### local imports

from ....rectsman.main import RectsManager

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


def reposition_collapsed_elements(self):
    """Reposition objects inside the node in collapsed signature mode.

    The repositioning is made from the input
    downwards (the top rectsman don't need to be
    repositioned, it always stays at the same relative
    position within the node).

    Another administrative task is performed, which is
    updating the height of self.rect.
    """
    ### determine which paramaters/subparameters/outputs will
    ### be shown after hiding unconnected ones
    self.collapse_unconnected_elements()

    ### create a rect representing the height of text
    ### surfaces used in the node
    text_rect = Rect(0, 0, 0, FONT_HEIGHT)

    ### reference the top rectsman and its horizontal
    ### edges locally

    top_rectsman = self.top_rectsman

    top_rectsman_left = top_rectsman.left
    top_rectsman_right = top_rectsman.right

    ### define a top coordinate which is the bottom of
    ### the top of the node plus the body content
    ### offset given as a constant
    top = top_rectsman.bottom + BODY_CONTENT_OFFSET

    ### reference list of visible input sockets locally
    vis = self.visible_input_sockets

    ### reference map with input sockets locally
    isl_flmap = self.input_socket_live_flmap

    ### reference map of subparam unpacking icons locally
    sui_flmap = self.subparam_unpacking_icon_flmap

    ### reference map of subparam keyword entries
    skel_map = self.subparam_keyword_entry_live_map

    ### create a temporary rectsman with its list of rects

    temp_rect_list = []
    temp_rectsman = RectsManager(temp_rect_list.__iter__)


    ### position visible output sockets

    ## reference list of visible output sockets
    vos = self.visible_output_sockets

    ## reference the last visible output socket, if any
    if vos:
        last_output_socket = vos[-1]

    for output_socket in vos:

        socket_rect = output_socket.rect

        ## align text rect center with the center of the
        ## socket, then pull text rect 2 pixels up
        text_rect.centery = socket_rect.move(0, -2).centery

        # position object as one, by appending
        # text rect temporarily to the rect list

        temp_rect_list.append(socket_rect)
        temp_rect_list.append(text_rect)

        temp_rectsman.top = top

        top = temp_rectsman.bottom

        temp_rect_list.clear()

        ## if the socket isn't the last one, increment
        ## the top with the distance between outputs
        ## given as a constant

        if output_socket != last_output_socket:
            top += DISTANCE_BETWEEN_OUTPUTS

    ## if there are visible output sockets...

    if vos:

        ## reference the output rectsman locally
        output_rectsman = self.output_rectsman

        ## align the output rectsman centerx with the
        ## top rectsman's right, so that the output sockets
        ## all rest centered on the right corner of the
        ## node
        output_rectsman.centerx = top_rectsman.right


    ### position parameters

    ## offset the defined top by the input offset given as a constant,
    ## that is, if there are visible input sockets and output sockets;

    if vis and vos:
        top += INPUT_OFFSET

    ## retrieve parameter objects (they're ordered)
    parameters = self.signature_obj.parameters.values()

    ## if there are visible input sockets, store a reference
    ## to the last one

    if vis:
        last_input_socket = vis[-1]

    ## reference subparameter unpacking map locally
    subparam_unpacking_map = self.data["subparam_unpacking_map"]

    ## iterate over parameter objects positioning each
    ## of them

    for param_obj in parameters:

        ## retrieve name of parameter
        param_name = param_obj.name

        ## try retrieving the variable kind of the
        ## parameter
        try:
            kind = self.var_kind_map[param_name]

        ## if the retrieval fails, then we have
        ## a regular parameter

        except KeyError:

            ##
            input_socket = isl_flmap[param_name]

            if input_socket not in vis:
                continue

            ## we have only the input socket,
            ## so we align the vertical center of both
            ## the text rect and input socket (with just
            ## a bit offset) and perform the calculation
            ## as if they were a single object by
            ## temporarily appending the text rect to
            ## the list of rects managed by the rectsman

            # obtain socket rect
            socket_rect = input_socket.rect

            # align vertical center of both text rect
            # and input socket (with a bit offset)
            text_rect.centery = socket_rect.move(0, -2).centery

            # position object as one, by appending
            # text rect temporarily to the rect list

            temp_rect_list.append(socket_rect)
            temp_rect_list.append(text_rect)

            temp_rectsman.top = top

            top = temp_rectsman.bottom

            temp_rect_list.clear()

            # position socket horizontally
            socket_rect.centerx = top_rectsman_left


        ## otherwise, we are dealing with a variable
        ## parameter

        else:

            ## retrieve the names of the subparameters sorted
            sorted_subparam_indices = sorted(isl_flmap[param_name])

            ## if there are indeed subparameters, store a reference to the
            ## input socket of the last visible subparameter

            if sorted_subparam_indices:

                for subparam_index in reversed(sorted_subparam_indices):

                    input_socket = isl_flmap[param_name][subparam_index]

                    if input_socket in vis:

                        last_subparam_input_socket = input_socket
                        break

                else:
                    last_subparam_input_socket = False

            else:
                continue

            ##

            if last_subparam_input_socket:

                ## variable parameters always start with the
                ## name of the parameter on top, so we begin
                ## by positioning the top rect on top
                text_rect.top = top

                ## the top for the next object will be below
                ## the text rect plus an offset given as a
                ## constant
                top = text_rect.bottom + SUBPARAM_OFFSET_FROM_LABEL

            else:
                continue

            ## retrieve the list of unpacked subparameter indices
            subparams_for_unpacking = subparam_unpacking_map[param_name]

            ## iterate over each subparameter index in order,
            ## repositioning each subparameter as you go

            for subparam_index in sorted_subparam_indices:

                ## check whether the input socket is visible

                input_socket = isl_flmap[param_name][subparam_index]

                if input_socket not in vis:
                    continue

                # position socket horizontally
                input_socket.rect.centerx = top_rectsman_left

                # if subparameter is unpacked...

                if subparam_index in subparams_for_unpacking:

                    unpacking_icon = sui_flmap[param_name][subparam_index]

                    unpacking_icon.rect.midleft = (
                        input_socket.rect.move(2, 0).midright
                        if kind == 'var_pos'
                        else input_socket.rect.move(18, 0).midright
                    )

                    temp_rect_list.append(input_socket.rect)
                    temp_rect_list.append(unpacking_icon.rect)

                    temp_rectsman.top = top

                    top = temp_rectsman.bottom

                    temp_rect_list.clear()

                # if it is of keyword-variable kind...

                elif kind == 'var_key':

                    keyword_entry = skel_map[subparam_index]

                    keyword_entry.rect.midleft = (
                        input_socket.rect.move(18, 0).midright
                    )

                    temp_rect_list.append(input_socket.rect)
                    temp_rect_list.append(keyword_entry.rect)

                    temp_rectsman.top = top

                    top = temp_rectsman.bottom

                    temp_rect_list.clear()

                # otherwise...

                else:

                    # assign top
                    input_socket.rect.top = top

                    # define new top
                    top = input_socket.rect.bottom


                # if the subparameter isn't the last one,
                # increment the top with the distance
                # between subparameters given as a constant

                if subparam_index != last_subparam_input_socket.subparameter_index:
                    top += DISTANCE_BETWEEN_SUBPARAMS

        ## if the parameter being positioned isn't the
        ## last one, increment the top with the distance
        ## between parameters given as a constant

        if param_name != last_input_socket.parameter_name:
            top += DISTANCE_BETWEEN_PARAMS


    ### position the id text object

    ## reference the rect of the id text object locally
    id_text_rect = self.id_text_obj.rect

    ## align its top with the last defined top, which
    ## is the bottom of the pair last output socket
    ## and the text rect; also push it 4 pixels down
    ## for extra padding

    id_text_rect.top = top
    id_text_rect.top += 4

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

    ### perform extra administrative task: updating
    ### the height of self.rect
    self.rect.height = bottom_rectsman.bottom - top_rectsman.top
