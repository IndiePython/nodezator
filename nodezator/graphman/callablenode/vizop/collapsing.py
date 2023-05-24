
### local import
from ....config import APP_REFS


def collapse_unconnected_elements(self):
    """Perform setups so all unconnected elements are collapsed."""
    ### reference and clear relevant lists

    vis = self.visible_input_sockets
    vis.clear()

    vuirs = self.visible_unpacking_icon_rects
    vuirs.clear()

    vws = self.visible_widgets
    vws.clear()

    ###

    isl_flmap = self.input_socket_live_flmap

    parameters = self.signature_obj.parameters.values()

    subparam_map = self.data["subparam_map"]

    sui_flmap = self.subparam_unpacking_icon_flmap
    skel_map = self.subparam_keyword_entry_live_map

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

                ### if socket has a parent, it must be included as a
                ### visible one
                
                input_socket = isl_flmap[param_name][subparam_index]

                has_parent = (

                    (
                        (self.id, param_name, subparam_index)
                        in APP_REFS.gm.parented_sockets_ids
                    )
                    if hasattr(APP_REFS.gm, 'parented_sockets_ids')

                    else hasattr(input_socket, 'parent')

                )

                ###
                if not has_parent:
                    continue

                ###

                vis.append(input_socket)

                unpacking_icon = sui_flmap[param_name].get(subparam_index)

                if unpacking_icon:
                    vuirs.append(unpacking_icon.rect)

                if kind == 'var_key' and subparam_index in skel_map:
                    vws.append(skel_map[subparam_index])

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
            (self.id, output_name) in APP_REFS.gm.parent_sockets_ids
            if hasattr(APP_REFS.gm, 'parent_sockets_ids')
            else hasattr(output_socket, 'children')
        )

        if has_parent:
            vos.append(output_socket)

    ###

    rects = self.col_rectsman._get_all_rects.__self__
    rects.clear()

    ##
    rects.extend(self.not_collapsible_rects)

    ##

    rects.extend(vuirs)

    rects.extend(
        obj.rect
        for obj in (vis + vos + vws)
    )
