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
    OUTPUT_OFFSET,
)


def reposition_elements(self):
    """Reposition objects inside the node.

    The repositioning is made from the input
    downwards (the top rectsman don't need to be
    repositioned, it always stays at the same relative
    position within the node).

    Another administrative task is performed, which is
    updating the height of self.rect.
    """
    ### create a rect representing the height of text
    ### surfaces used in the node
    text_rect = Rect(0, 0, 0, FONT_HEIGHT)

    ### reference the top rectsman locally
    top_rectsman = self.top_rectsman

    ### define a top coordinate which is the bottom of
    ### the top of the node plus the body content
    ### offset given as a constant
    top = top_rectsman.bottom + BODY_CONTENT_OFFSET

    ### position parameters

    ## retrieve parameter objects (they're ordered)
    parameters = self.signature_obj.parameters.values()

    ## if there are parameters, store the name of the last
    ## one (we'll use it soon)

    if parameters:
        last_param_name = list(parameters)[-1].name

    ## iterate over parameter objects positioning each
    ## of them

    for param_obj in parameters:

        ## retrieve name of parameter
        param_name = param_obj.name

        ## try retrieving the variable kind of the
        ## parameter
        try:
            self.var_kind_map[param_name]

        ## if the retrieval fails, then we have
        ## a regular parameter

        except KeyError:

            ## retrieve the rectsman representing the
            ## parameters, as well as the list of the
            ## underlying rects controlled by the rectsman

            param_rectsman = self.param_rectsman_map[param_name]

            rect_list = param_rectsman._get_all_rects.__self__

            ## if there's more than one rect in the
            ## parameter, it means there's a widget
            ## accompanying the socket;
            ##
            ## such socket won't be beside the parameter
            ## text, but beside the widget, both below the
            ## area where we'll ultimately blit the
            ## parameter text (not in this method, though),
            ## so we move the parameter down

            if len(rect_list) > 1:

                text_rect.top = top

                param_rectsman.top = text_rect.bottom + 2

                top = param_rectsman.bottom

            ## otherwise, we have only the input socket,
            ## so we align the vertical center of both
            ## the text rect and input socket (with just
            ## a bit offset) and perform the calculation
            ## as if they were a single object by
            ## temporarily appending the text rect to
            ## the list of rects managed by the rectsman

            else:

                # obtain socket rect
                socket_rect = rect_list[0]

                # align vertical center of both text rect
                # and input socket (with a bit offset)

                text_rect.centery = socket_rect.centery
                text_rect.top += -2

                # position object as one, by appending
                # text rect temporarily to the rect list

                rect_list.append(text_rect)

                param_rectsman.top = top

                top = max(param_rectsman.bottom, socket_rect.bottom)

                del rect_list[-1]

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

            ## iterate over each subparameter index in order,
            ## repositioning each subparameter as you go

            for subparam_index in sorted_subparam_indices:

                # retrieve rectsman for the subparameter

                subparam_rectsman = self.subparam_rectsman_map[param_name][
                    subparam_index
                ]

                # assign top
                subparam_rectsman.top = top

                # define new top
                top = subparam_rectsman.bottom

                # if the subparameter isn't the last one,
                # increment the top with the distance
                # between subparameters given as a constant

                if subparam_index != last_subparam_index:
                    top += DISTANCE_BETWEEN_SUBPARAMS

            ## retrieve the rects from the placeholder
            ## socket and the "add subparameter button"

            socket_rect = self.placeholder_socket_live_map[param_name].rect

            button_rect = self.placeholder_add_button_map[param_name].rect

            ## put the "add subparameter button" a bit to the
            ## right of the placeholder, both vertically
            ## aligned
            button_rect.midleft = socket_rect.move(5, 0).midright

            ## reposition socket rect and button rect
            ## together as if they were a single rect
            ## by controlling them through a temporary
            ## rects manager instance

            # instantiate rectsman

            rectsman = RectsManager((socket_rect, button_rect).__iter__)

            # assign the defined top and add 4 pixels, to
            # push them just a bit down for extra padding
            rectsman.top = top + 4

            # define the bottom of the rectsman as the new
            # to be used by the next parameter
            top = rectsman.bottom

        ## if the parameter being positioned isn't the
        ## last one, increment the top with the distance
        ## between parameters given as a constant

        if param_name != last_param_name:
            top += DISTANCE_BETWEEN_PARAMS

    ### position each output socket

    ## get names of output sockets (their order is defined
    ## in the node script)
    socket_names = self.ordered_output_type_map.keys()

    ## get name of last socket
    last_socket_name = list(socket_names)[-1]

    ## reference the output socket map locally
    osl_map = self.output_socket_live_map

    ## also offset the defined top by the output offset
    ## given as a constant, that is, if there are parameters
    if parameters:
        top += OUTPUT_OFFSET

    ## iterate over socket names, retrieving the rect of
    ## each socket in order to position it

    for output_name in socket_names:

        ## retrieve socket rect

        output_socket = osl_map[output_name]
        socket_rect = output_socket.rect

        ## align text rect center with the center of the
        ## socket, then pull text rect 2 pixels up

        text_rect.centery = socket_rect.centery
        text_rect.top += -2

        ## position text rect and socket rect together
        ## as if they were a single rect by controlling
        ## them through a temporary rects manager instance

        # instantiate rectsman
        rectsman = RectsManager((text_rect, socket_rect).__iter__)

        # assign top to the temporary rectsman
        rectsman.top = top

        # new top is the bottom of the temp rectsman
        top = rectsman.bottom

        ## if the socket isn't the last one, increment
        ## the top with the distance between outputs
        ## given as a constant

        if output_name != last_socket_name:
            top += DISTANCE_BETWEEN_OUTPUTS

    ## reference the output rectsman locally
    output_rectsman = self.output_rectsman

    ## align the output rectsman centerx with the
    ## top rectsman's right, so that the output sockets
    ## all rest centered on the right corner of the
    ## node
    output_rectsman.centerx = top_rectsman.right

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
