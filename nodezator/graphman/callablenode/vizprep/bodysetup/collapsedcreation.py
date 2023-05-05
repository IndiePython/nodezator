"""Facility for visuals related node class extension."""

### third-party imports

from pygame import Rect

from pygame.draw import line as draw_line


### local imports

from .....config import APP_REFS

from .....surfsman.draw import blit_aligned
from .....surfsman.render import render_rect

from .....classes2d.single import Object2D

from .....textman.render import render_text

from ...surfs import BODY_HEAD_SURFS_MAP

from ...constants import (
    NODE_WIDTH,
    FONT_HEIGHT,
    NODE_OUTLINE_THICKNESS,
)

from .....colorsman.colors import (
    NODE_OUTLINE,
    NODE_BODY_BG,
    COMMENTED_OUT_NODE_BG,
    NODE_LABELS,
)



def get_collapsed_body_surface(self):
    """Return surface for node's body in collapsed signature mode."""
    ### reference the top rectsman locally
    top_rectsman = self.top_rectsman

    ### reference the body's height locally
    body_height = self.body.rect.height

    ### define color used for body and labels bg, based
    ### on the "commented out" state

    node_light_bg_color = (
        COMMENTED_OUT_NODE_BG if self.data.get("commented_out", False) else NODE_BODY_BG
    )

    ### create a surface for the body of the node
    body_surf = render_rect(NODE_WIDTH, body_height, node_light_bg_color)

    ### obtain body head surf from corresponding map
    BODY_HEAD_SURF = BODY_HEAD_SURFS_MAP[self.category_color]

    ### blit the body head surface in the top of the
    ### body surface; such head surface has a color equal
    ### to that of the top of the node, so it makes the top
    ### part of the body appear as if merged with its top

    blit_aligned(
        ## surface to blit
        BODY_HEAD_SURF,
        ## target surface
        body_surf,
        "midtop",  ## retrieve pos from this
        "midtop",  ## assign pos to this
    )

    ### create a rect representing the height of text
    ### surfaces used in the node
    text_rect = Rect(0, 0, 0, FONT_HEIGHT)

    ### in order to blit surfaces in the body surface
    ### relative to the surface's origin, define an offset
    ### equal to the body's topleft coordinates inverted

    offset = tuple(-value for value in self.body.rect.topleft)

    ### reference input socket map locally for easier/quick access
    isl_flmap = self.input_socket_live_flmap

    ### iterate over the name of each parameter, blitting
    ### text surfaces representing them on the body of
    ### the node in the appropriate locations

    parameters_names = self.signature_obj.parameters.keys()

    for param_name in parameters_names:

        ### retrieve the rectsman of the parameter
        param_rectsman = self.param_rectsman_map[param_name]

        ### position the text rect in the appropriate place
        ### so we can use its topleft as the spot wherein
        ### to blit the surface we're about to create;
        ###
        ### in this part we also define the text to be used
        ### for the parameter (either its own name or
        ### its name slightly altered if it is a parameter
        ### of variable kind)

        ## try retrieving the variable kind of the parameter
        try:
            var_kind = self.var_kind_map[param_name]

        ## if a KeyError is raised, then we have a regular
        ## parameter here...

        except KeyError:

            ## skip this parameter if it doesn't have a parent

            has_parent = (

                (self.id, param_name) in APP_REFS.gm.parented_sockets_ids
                if hasattr(APP_REFS.gm, 'parented_sockets_ids')

                else hasattr(isl_flmap[param_name], 'parent')

            )

            if not has_parent:
                continue

            ## position the text rect horizontally,
            ## 10 pixels from the left side of the
            ## node's left (which you can retrieve
            ## from the top rectsman)
            text_rect.left = top_rectsman.left + 10

            ## position the text rect vertically

            # retrieve the list of rects controlled by
            # the rects manager of the parameter;
            #
            # the first one is the input socket's rect
            rect_list = param_rectsman._get_all_rects.__self__
            input_socket_rect = rect_list[0]

            # the text is positioned vertically centered on the
            # input socket, lifted just 2 pixels up
            text_rect.centery = input_socket_rect.centery
            text_rect.top += -2

            ## define text
            text = param_name

        ## otherwise, we have a parameter of variable kind
        ## here...

        else:

            ## skip this parameter if none of its subparameters
            ## has a parent

            if hasattr(APP_REFS.gm, 'parented_sockets_ids'):

                parented_sockets_ids = APP_REFS.gm.parented_sockets_ids

                for subparam_index in isl_map[param_name]:

                    if (self.id, param_name, subparam_index) in parented_sockets_ids:

                        has_parent = True
                        break

                else:
                    has_parent = False

            else:

                for input_socket in isl_flmap[param_name].values():

                    if hasattr(input_socket, 'parent'):

                        has_parent = True
                        break
                else:
                    has_parent = False

            if not has_parent:
                continue

            ## position the text rect horizontally,
            ## 5 pixels from the left side of the node's
            ## left (which you can retrieve from the
            ## top rectsman)
            text_rect.left = top_rectsman.left + 5

            ## position vertically

            text_rect.bottom = param_rectsman.top
            text_rect.top += -2

            ## define text (instead of just using the
            ## parameter's name, we add one or two
            ## additional asterisks, to indicate that
            ## the parameter is of variable kind and
            ## the specific variable kind)

            asterisks = "*" if var_kind == "var_pos" else "**"

            text = asterisks + param_name

        ### define coordinates info

        coordinates_name = "topleft"
        coordinates_value = text_rect.topleft

        ### instantiate positioned text object

        text_obj = Object2D.from_surface(
            surface=render_text(
                text=text,
                ## text settings
                font_height=FONT_HEIGHT,
                foreground_color=NODE_LABELS,
                background_color=node_light_bg_color,
                max_width=170,
            ),
            coordinates_name=coordinates_name,
            coordinates_value=coordinates_value,
        )

        ### reposition the object relative to the
        ### surface's origin and blit the obj's surface
        ### on the body surface

        text_obj.rect.move_ip(offset)
        text_obj.draw_on_surf(body_surf)

    ### blit labels on the body surface, beside each output
    ### socket so the name of each output socket is visible
    ### on the node

    ## retrieve name of socket in the order they appear
    ordered_socket_names = self.ordered_output_type_map.keys()

    ## retrieve map wherein to find the output sockets
    osl_map = self.output_socket_live_map

    ## position the text rect 10 pixels to the left of
    ## the right side of the node (we use the right of
    ## the top_rectsman)
    text_rect.right = top_rectsman.right - 10

    ## also assign 'topright' as the name of
    ## the coordinates from where we'll position
    ## the text objects we'll be creating
    coordinates_name = "topright"

    ## iterate over names of output sockets;
    ##
    ## for those with children create the text surface
    ## for their respective names and blit them in the
    ## body surface

    for output_socket_name in ordered_socket_names:

        ## grab the output socket
        output_socket = osl_map[output_socket_name]

        ## if the socket has children, skip

        has_parent = (
            (self.id, output_socket_name) in APP_REFS.gm.parent_sockets_ids
            if hasattr(APP_REFS.gm, 'parent_sockets_ids')
            else hasattr(output_socket, 'children')
        )

        if not has_parent:
            continue

        ## align the text rect vertically with the
        ## output socket and lift the text rect 2 pixels;
        ##
        ## we don't need to do any more positioning
        ## than this, since the sockets are already
        ## positioned suitably (they were already
        ## positioned on the self.reposition_elements
        ## method relative to the text);
        ##
        ## here we just want to get the suitable position
        ## to blit the text

        text_rect.centery = output_socket.rect.centery
        text_rect.top += -2

        ## grab the topright coordinate from the
        ## text rect
        coordinates_value = text_rect.topright

        ## instantiate the text object in the given position

        text_obj = Object2D.from_surface(
            surface=(
                render_text(
                    text=output_socket_name,
                    font_height=FONT_HEIGHT,
                    foreground_color=NODE_LABELS,
                    background_color=(node_light_bg_color),
                    max_width=170,
                )
            ),
            coordinates_name=coordinates_name,
            coordinates_value=coordinates_value,
        )

        ## reposition the object relative to the
        ## surface's origin and blit the obj's surface
        ## on the body surface

        text_obj.rect.move_ip(offset)
        text_obj.draw_on_surf(body_surf)

    ### outline the sides of the body surface

    ## define lines represented by pairs of points

    # calculate and store the result from subtracting
    # the outline thickness from the body width
    # (which is equivalent to the NODE_WIDTH);
    #
    # we'll call this the 'offset_width', and it is
    # the x coordinate from where we'll define the points
    # of the line on the right side of the node;
    #
    # this is needed because the thickness of the lines
    # are blitted from left to right and thus
    # wouldn't appear if the line were placed
    # right on top of the right side; instead, it must be
    # offset to the left by subtracting the thickness
    offset_width = NODE_WIDTH - NODE_OUTLINE_THICKNESS

    # defining lines

    lines = (
        # line on left side
        ((0, 0), (0, body_height)),
        # line on right side
        ((offset_width, 0), (offset_width, body_height)),
    )

    # drawing lines

    for point_a, point_b in lines:

        draw_line(body_surf, NODE_OUTLINE, point_a, point_b, NODE_OUTLINE_THICKNESS)

    ### separate body head from rest of the body by drawing
    ### a horizontal line between those areas

    line_y = BODY_HEAD_SURF.get_height()

    draw_line(body_surf, NODE_OUTLINE, (0, line_y), (body_surf.get_width(), line_y), 2)

    ### finally return the body surface
    return body_surf
