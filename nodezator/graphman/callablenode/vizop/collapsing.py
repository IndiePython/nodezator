
### local import
from ....config import APP_REFS


def collapse_unconnected_elements(self):
    """Perform setups so all unconnected elements are collapsed."""
    ### store visible input sockets

    vis = self.visible_input_sockets
    vis.clear()

    isl_flmap = self.input_socket_live_flmap

    parameters = self.signature_obj.parameters.values()

    subparam_map = self.data["subparam_map"]

    for param_obj in parameters:

        param_name = param_obj.name

        try:
            kind = self.var_kind_map[param_name]

        except KeyError:

            input_socket = isl_flmap[param_name]

            ## if socket has a parent, it must be included as a
            ## visible one

            has_parent = (

                (self.id, param_name) in APP_REFS.gm.parented_sockets_ids
                if hasattr(APP_REFS.gm, 'parented_sockets_ids')

                else hasattr(input_socket, 'parent')

            )

            if has_parent:
                vis.append(input_socket)

        else:

            subparams = subparam_map[param_name]

            for subparam_index in sorted(subparams):

                ## if socket has a parent, it must be included as a
                ## visible one
                
                input_socket = isl_flmap[param_name][subparam_index]

                has_parent = (

                    (
                        (self.id, param_name, subparam_index)
                        in APP_REFS.gm.parented_sockets_ids
                    )
                    if hasattr(APP_REFS.gm, 'parented_sockets_ids')

                    else hasattr(input_socket, 'parent')

                )

                if has_parent:
                    vis.append(input_socket)

    ### store visible output sockets

    ##
    vos = self.visible_output_sockets
    vos.clear()

    ## reference output sock live map locally
    osl_map = self.output_socket_live_map

    ##

    for output_name in self.ordered_output_type_map.keys():

        output_socket = osl_map[output_name]

        ## if socket has children, it must be included as a
        ## visible one

        has_parent = (
            (self.id, output_socket_name) in APP_REFS.gm.parent_sockets_ids
            if hasattr(APP_REFS.gm, 'parent_sockets_ids')
            else hasattr(output_socket, 'children')
        )

        if has_parent:
            vos.append(output_socket)

    ###

    rectsman = self.col_rectsman

    rects = rectsman._get_all_rects.__self__
    rects.clear()

    ##
    rects.extend(self.not_collapsible_rects)

    ##
    rects.extend(
        socket.rect
        for socket in (vis + vos)
    )
