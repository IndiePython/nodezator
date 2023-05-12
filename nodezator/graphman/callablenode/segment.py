"""Facility with function for injection."""

class SegmentOperations:

    def signal_connection(self, input_socket):

        ### if node is not expanded, exit method right away

        if not self.data.get('mode', 'expanded_signature') == 'expanded_signature':
            return

        ## if we are dealing with a parameter input socket,
        ## extra checks before deciding to exit right away

        elif input_socket.subparameter_index is None:

            ## there's no visible widget

            if not (

                input_socket.parameter_name in self.widget_live_flmap

                and (
                    self.widget_live_flmap[input_socket.parameter_name]
                    in self.visible_widgets
                )
            ):
                return

        ### if we are dealing with a subparameter input socket...

        else:

            ## if it is a new one, just delete the attribute referencing
            ## it

            if (
                hasattr(self, 'new_subparam_input_socket')
                and input_socket is self.new_subparam_input_socket
            ):
                del self.new_subparam_input_socket

            ## if it has a widget which is not visible, pass

            elif (
                input_socket.subparameter_index in
                self.widget_live_flmap[input_socket.parameter_name]
                and (
                    self.widget_live_flmap[input_socket.parameter_name]
                    .get(input_socket.subparameter_index, None) in
                    self.visible_widgets
                )
            ):
                pass

            ## otherwise exit right away
            else:
                return

        ## reposition all objects within the node
        self.reposition_elements()

        ## reset body's height and image
        self.reset_body_height_and_image()


    def signal_severance(self, socket=None):

        mode_name = self.data.get('mode', 'expanded_signature')

        if mode_name == 'callable':
            return

        ### if socket is none, perform setups regarding severance
        ### of connections to stored sockets

        if socket is None:

            repositioning_and_new_body_required = False

            param_input_sockets = self.disconnected_param_input_sockets

            if mode_name == 'collapsed_signature':
                repositioning_and_new_body_required = True

            else:

                for input_socket in param_input_sockets:

                    ## there's a widget which is not visible

                    if (

                        input_socket.parameter_name in self.widget_live_flmap

                        and (
                            self.widget_live_flmap[input_socket.parameter_name]
                            not in self.visible_widgets
                        )
                    ):

                        repositioning_and_new_body_required = True
                        break

            param_input_sockets.clear()

            if self.disconnected_subparam_input_sockets:

                self.perform_severance_setups()
                repositioning_and_new_body_required = True

            if repositioning_and_new_body_required:

                ## reposition all objects within the node
                self.reposition_elements()

                ## reset body's height and image
                self.reset_body_height_and_image()

        ### if we have a subparameter input socket, store it
        ### for later setups
        elif getattr(socket, 'subparameter_index', None) is not None:
            self.disconnected_subparam_input_sockets.append(socket)

        ### if we have a parameter input socket, store it for later
        ### setups
        elif hasattr(socket, 'parameter_name'):
            self.disconnected_param_input_sockets.append(socket)

    def perform_severance_setups(self):

        ###

        wl_flmap = self.widget_live_flmap
        isl_flmap = self.input_socket_live_flmap
        sub_flmap = self.subparam_up_button_flmap
        sdb_flmap = self.subparam_down_button_flmap
        sui_flmap = self.subparam_unpacking_icon_flmap
        skl_map = self.subparam_keyword_entry_live_map
        srm_map = self.subparam_rectsman_map

        subparam_map = self.data["subparam_map"]
        subparam_unpacking_map = self.data["subparam_unpacking_map"]
        subparam_keyword_map = self.data["subparam_keyword_map"]

        ###

        var_kind_map = self.var_kind_map
        var_params_to_fix = set()

        ###

        sub_input_sockets = self.disconnected_subparam_input_sockets

        while sub_input_sockets:

            ### retrieve input socket
            sub_input_socket = sub_input_sockets.pop()

            ### store parameter's name and subparameter index

            param_name = sub_input_socket.parameter_name
            subparam_index = sub_input_socket.subparameter_index

            ### use the parameter name to obtain a map of
            ### subparameter widgets
            subparam_widgets = wl_flmap[param_name]

            ### reference the list of subparameters for
            ### unpacking locally for easier access
            subparams_for_unpacking = self.data["subparam_unpacking_map"][param_name]

            ### try accessing a widget instance for the
            ### subparameter using its index
            try:
                widget = subparam_widgets[subparam_index]

            ### if the attempt fails, then the recently severed
            ### input socket must be removed, since it has no
            ### widget from which to obtain data when executed

            except KeyError:

                ## add parameter name to list of variable
                ## parameters to fix
                var_params_to_fix.add(param_name)

                ## remove input socket
                isl_flmap[param_name].pop(subparam_index)

                # this dict subclass instance must be updated
                # whenever it changes
                isl_flmap.update()

                ## remove the subparam index from list inside
                ## subparam map
                subparam_map[param_name].remove(subparam_index)

                ## remove "move subparam" buttons
                sub_flmap[param_name].pop(subparam_index)

                # this dict subclass instance must be updated
                # whenever it changes
                sub_flmap.update()

                sdb_flmap[param_name].pop(subparam_index)

                # this dict subclass instance must be updated
                # whenever it changes
                sdb_flmap.update()

                ## since the input socket was removed...

                ## if the subparameter was marked to be
                ## unpacked, remove the unpacking icon from
                ## the respective map and the subparameter
                ## index from the respective list as well

                if subparam_index in subparams_for_unpacking:

                    ## remove unpacking icon
                    sui_flmap[param_name].pop(subparam_index)

                    # this special dict subclass instance must
                    # be updated whenever it is changed
                    sui_flmap.update()

                    ## remove subparameter index from list of
                    ## subparameter's for unpacking
                    subparams_for_unpacking.remove(subparam_index)

                ## else if the parameter is of keyword-variable
                ## kind remove the keyword entry from the
                ## respective map and the keyword from the
                ## respective map as well

                elif var_kind_map[param_name] == "var_key":

                    ## remove keyword entry widget
                    skl_map.pop(subparam_index)

                    ## remove keyword name from subparameter
                    ## keyword map
                    subparam_keyword_map.pop(subparam_index)


                ## remove the subparameter rectsman from the
                ## subparameter rectsman map
                srm_map[param_name].pop(subparam_index)


        ## fix names of subparameters

        while var_params_to_fix:
            self.fix_subparameter_indices(var_params_to_fix.pop())
