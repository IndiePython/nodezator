### local imports

from ..exception import (
    MissingInputError,
    WaitingInputException,
    PositionalSubparameterUnpackingError,
    KeywordSubparameterUnpackingError,
)


class Execution:
    """Operations related to node execution."""

    def create_execution_support_objects(self):
        """Create objects to help during execution."""

        ### create a map to store input for (sub)parameters
        ### (the input comes from default values, widgets
        ### or other nodes)

        self.argument_map = {param_name: {} for param_name in self.var_kind_map}

        ### create a set to store the names of all
        ### pending parameters, that is, parameters
        ### which are still waiting for input from
        ### other nodes
        self.pending_param_names = set()

        ### create a map to store whether or not
        ### input sockets are expecting input from
        ### another node
        self.expects_input_map = {}

    def perform_execution_setup(self):
        """Clear input slots, set finished flag to False.

        Performed before and after a node execution.
        """
        ### update the pending parameter names set with the
        ### name of all existing parameters

        self.pending_param_names.update(self.signature_obj.parameters.keys())

        ### clear the argument map and insert empty dicts
        ### for subparameters

        self.argument_map.clear()

        for param_name in self.var_kind_map:
            self.argument_map[param_name] = {}

        ### setup the expects input map

        self.expects_input_map.clear()

        for input_socket in self.input_sockets:

            ### use the parameter name as key
            key = input_socket.parameter_name

            ### unless the subparameter index is not None,
            ### in which case the key must be a tuple
            ### containing the parameter name and
            ### subparameter index

            if input_socket.subparameter_index is not None:

                key = (
                    key,
                    input_socket.subparameter_index,
                )

            ### use the key to store whether the input
            ### socket has a 'parent' attribute or not
            ### in the map

            self.expects_input_map[key] = hasattr(
                input_socket,
                "parent",
            )

        ### set a state as 'ready
        self.state = "ready"

    def __call__(self):
        """Return objects needed to execute node's callable.

        This method always have one of three effects:

        1) return elements needed to execute the node's
        callable if the node don't need to wait for data
        from other nodes.

        2) raises a WaitingInputException, meaning the node's
        callable is not ready to be executed because it is
        waiting for input from other nodes.

        3) raises a MissingInputError, if a required
        argument cannot be provided (the argument has
        no source of data, either from another node or
        from an embedded widget).
        """
        ### check whether there are pending parameters,
        ### performing measures to obtain the needed data
        self.check_pending_parameters()

        ### if an exception is not raised by the call above,
        ### we can safely assume we received every argument
        ### needed to execute the node's callable, so we
        ### return all elements needed

        return (
            self.main_callable,
            self.argument_map,
            self.signature_obj,
        )

    def check_pending_parameters(self):
        """Perform checks on pending parameters.

        Here we check pending parameters to see whether we

        1. should raise a WaitingInputException, meaning the
        node must wait for inputs from other nodes before
        executing.
        2. only if there's no incoming data from other
        nodes, whether we should use data provided by the
        user via embedded widgets or default values from
        the callable itself.
        3. in case there's no source of data for a
        required parameter, raise an MissingInputError
        explaining the situation.
        """
        ### create a set to hold names of parameters
        ### which are not pending anymore
        ready_param_names = set()

        ### create a list to hold names of (sub)parameters
        ### waiting for input
        waiting_input = []

        ### create a list to hold names of (sub)parameters
        ### lacking a data source
        lacking_data_source = []

        ### alias the argument map using a variable of
        ### smaller character count for better code layout
        arg_map = self.argument_map

        ### iterate over each pending parameter, performing
        ### checks and acting according to their results

        for param_name in self.pending_param_names:

            ## check whether the parameter is or not of
            ## variable kind, by trying to retrieve which
            ## kind of variable parameter it is
            try:
                kind = self.var_kind_map[param_name]

            ## if it fails, it means it is not a variable
            ## parameter, so we perform suitable checks

            except KeyError:

                ## if the parameter is present in the
                ## argument map, we deem it ready

                if param_name in arg_map:
                    ready_param_names.add(param_name)

                ## if the parameter has data set to be
                ## delivered from another node output,
                ## we store its name on the 'waiting_input'
                ## list

                elif self.expects_input_map[param_name]:
                    waiting_input.append(param_name)

                ## otherwise, try retrieving values from
                ## other sources

                else:

                    # try assigning the default value for
                    # the input, if it exists, in which
                    # case you can deem the parameter as
                    # ready

                    try:
                        arg_map[param_name] = self.default_map[param_name]

                    except KeyError:
                        pass

                    else:
                        ready_param_names.add(param_name)

                    # try assigning a value from an
                    # embedded widget if such value
                    # exists in which case you can deem
                    # the parameter as ready (note that
                    # this is tried regardless of whether
                    # the previous try statement succeeds,
                    # because values set on widgets by
                    # users have precedence over the
                    # actual default values defined in the
                    # callables)

                    try:

                        arg_map[param_name] = self.data["param_widget_value_map"][
                            param_name
                        ]

                    except KeyError:
                        pass

                    else:
                        ready_param_names.add(param_name)

                    # if, after the attempted assignments
                    # above, the input still isn't
                    # available, then it can only mean the
                    # node is inexecutable due to lack of
                    # input sources; we store its name on
                    # the 'lacking_data_source' list

                    if param_name not in arg_map:

                        lacking_data_source.append(param_name)

            ## if parameter is of variable kind, check
            ## whether it has subparameters and their
            ## respective data sources (incoming data
            ## or data from a widget)

            else:

                ## retrieve a list of subparameters

                subparams = self.data["subparam_map"][param_name]

                ## if it has subparameters (list isn't
                ## empty), check whether the subparameters
                ## have appropriate data sources (incoming
                ## data from another node or data from a
                ## widget)

                if subparams:

                    # iterate over each subparameter index,
                    # checking its availability/solving
                    # problems, keeping track of whether
                    # there subparams waiting for input

                    subparams_waiting = False

                    for subparam_index in subparams:

                        # check presence of subparameter

                        try:
                            (arg_map[param_name][subparam_index])

                        # if subparameter is not present

                        except KeyError:

                            # if there's incoming data for
                            # the subparameter, store a
                            # tuple with names of parameter
                            # and subparameter on the
                            # waiting_input list and set
                            # the subparams_waiting flag
                            # to True

                            if self.expects_input_map[(param_name, subparam_index)]:

                                waiting_input.append((param_name, subparam_index))

                                subparams_waiting = True

                            # otherwise, try retrieving
                            # a value from a widget

                            else:

                                try:

                                    (arg_map[param_name][subparam_index]) = self.data[
                                        "subparam_widget_map"
                                    ][param_name][subparam_index]["widget_kwargs"][
                                        "value"
                                    ]

                                # if the attempt fails
                                # (the subparam widget map
                                # doesn't have a sub key w/
                                # the subparameter's name)
                                # it means the subparameter
                                # has no input source;
                                # we store the parameter
                                # name and subparameter
                                # index in the
                                # 'lacking_data_source' list

                                except KeyError:

                                    (
                                        lacking_data_source.append(
                                            (
                                                param_name,
                                                subparam_index,
                                            )
                                        )
                                    )

                    # if there are no subparameters waiting,
                    # it means they are all available so we
                    # can finally deem the parameter ready

                    if not subparams_waiting:

                        # deem the parameter ready
                        ready_param_names.add(param_name)

                        # retrieve subparam value map
                        subparam_value_map = arg_map[param_name]

                        # perform additional setups
                        # depending on the specific kind
                        # of variable parameter we have

                        if kind == "var_pos":

                            # obtain a list which represents
                            # the subparameters' indices,
                            # which are keys, sorted

                            sorted_indices = sorted(subparam_value_map)

                            # retrieve the list of
                            # subparameters that must
                            # be unpacked

                            subparams_for_unpacking = self.data[
                                "subparam_unpacking_map"
                            ][param_name]

                            # retrieve the values of each
                            # subparameter in the order
                            # defined in the 'sorted_indices'
                            # list, building a list with
                            # the values

                            param_args = []

                            for index in sorted_indices:

                                if index in subparams_for_unpacking:

                                    try:

                                        param_args.extend(subparam_value_map[index])

                                    except Exception as err:

                                        raise PositionalSubparameterUnpackingError(
                                            self,
                                            param_name,
                                            index,
                                        ) from err

                                else:

                                    param_args.append(subparam_value_map[index])

                            # replace the parameter data in
                            # the argument map by the list
                            # we just created
                            arg_map[param_name] = param_args

                        elif kind == "var_key":

                            # retrieve map containing
                            # name of keyword for each
                            # subparameter

                            subparam_keywords = self.data["subparam_keyword_map"]

                            # now build a new dictionary
                            # with the sorted keys from the
                            # subparam value map and its
                            # values

                            param_args = {}

                            for index in sorted(subparam_value_map):

                                value = subparam_value_map.pop(index)

                                if index in subparam_keywords:

                                    param_args[subparam_keywords[index]] = value

                                else:

                                    # note that we use '.update(**value)'
                                    # instead of '.update(value)'; this is
                                    # so because '.update(value)' would be
                                    # more lenient than the '**', and thus
                                    # not equivalent ('**' only accepts
                                    # mappings, while .update accepts
                                    # other iterables as well);
                                    #
                                    # since we are emulating the behaviour
                                    # of '**', we go with the less lenient
                                    # behaviour of only accepting mappings

                                    try:
                                        param_args.update(**value)

                                    except Exception as err:

                                        raise KeywordSubparameterUnpackingError(
                                            self,
                                            param_name,
                                            index,
                                        ) from err

                            # replace the parameter data in
                            # the argument map by the dict
                            # we just created
                            arg_map[param_name] = param_args

                        else:

                            raise RuntimeError(
                                "there shouldn't be possible"
                                " to specify a variable"
                                " parameter of a kind which"
                                " is neither 'var_pos' or"
                                " 'var_key'"
                            )

                ## otherwise, if it doesn't have any
                ## subparameters, we deem the parameter
                ## ready and assign the default value for
                ## the parameter, according to its specific
                ## variable kind: (an empty tuple for a
                ## positional-variable parameter or an
                ## empty dict for a keyword-variable
                ## parameter)

                else:

                    # deem the parameter ready
                    ready_param_names.add(param_name)

                    # define and store a default value
                    # according to the kind of parameter

                    default = () if kind == "var_pos" else {}

                    arg_map[param_name] = default

        ### remove ready parameter names from pending set
        self.pending_param_names -= ready_param_names

        ### if parameters lacking data sources are found,
        ### raise MissingInputError

        if lacking_data_source:

            raise MissingInputError(
                self,
                lacking_data_source,
            )

        ### if there are (sub)parameters waiting for input,
        ### raise the WaitingInputException

        if waiting_input:

            raise WaitingInputException("node has (sub)parameters waiting for input")

    def receive_input(self, data, param_name, subparam_index=None):
        """Store given data

        Parameters
        ==========

        data (any Python object)
            data sent by the graph manager, retrieved from
            another node.
        param_name (string)
            name of the parameter for which the data must
            be stored (if the subparameter index is not None,
            the data received must be stored for such
            parameter's subparameter instead)
        subparam_index (int or None)
            if not None, it represents the index of the
            subparameter for which the data must be stored.
        """
        ### if subparameter index is not None, store the
        ### data in the argument map for the specified
        ### subparameter

        if subparam_index is not None:

            (self.argument_map[param_name][subparam_index]) = data

        ### otherwise the data is supposed to be stored
        ### for the parameter
        else:
            self.argument_map[param_name] = data
