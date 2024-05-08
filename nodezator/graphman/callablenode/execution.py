### local imports

from ..exception import (
    LackOfInputError,
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

        self.argument_map = {
            param_name: {}
            for param_name in self.var_kind_map
        }

        ### create set to store ids of nodes providing incoming
        ### connections (inputs) to this one;
        ###
        ### also store references to recurrent methods

        isi = self.input_source_ids = set()

        self.clear_source_ids = isi.clear
        self.remove_source_ids = isi.difference_update
        self.add_source_id = isi.add

    def perform_execution_setup(self):
        """Clear input slots, set finished flag to False.

        Performed before and after a node execution.
        """
        ### clear the argument map and insert empty dicts
        ### for subparameters

        self.argument_map.clear()

        for param_name in self.var_kind_map:
            self.argument_map[param_name] = {}

        ### update set of ids from nodes that provide input to this one
        self.clear_source_ids()

    def send_id_to_direct_children(self):
        ### add id to direct children as source of data
        ###
        ### used for indegree tracking

        for output_socket in self.output_sockets:
            output_socket.add_source_id(self.id)

    def check_and_setup_parameters(self):
        """Perform checks/setups on parameters.

        Here we check each parameter (and corresponding subparameters, if any)
        to see whether whether they expect...

        - expect incoming data from another node
        - have available data from widgets
        - lack input source

        In case one or more of them lack a source of data, we raise a
        LackOfInputError explaining the situation.
        """
        ### create a list to hold names of (sub)parameters
        ### lacking a data source
        lacking_data_source = []

        ### reference/alias relevant maps locally for quicker
        ### and easier access

        arg_map = self.argument_map
        var_kind_map = self.var_kind_map
        isl_flmap = self.input_socket_live_flmap

        ### iterate over the name of each parameter, performing
        ### checks and acting according to their results

        for param_name in self.signature_obj.parameters.keys():

            ## if parameter is of variable kind, check
            ## whether it has subparameters and their
            ## respective data sources (incoming data
            ## or data from a widget)

            if param_name in var_kind_map:
                
                ## retrieve kind
                kind = var_kind_map[param_name]

                ## retrieve a list of subparameters
                subparams = self.data['subparam_map'][param_name]

                ## if it has subparameters (list isn't
                ## empty), check whether we need to retrieve data
                ## from its widget or not

                if subparams:

                    for subparam_index in subparams:

                        # if respective input socket doesn't have a parent,
                        # store data from widget as the argument

                        input_socket = isl_flmap[param_name][subparam_index]

                        if not hasattr(input_socket, 'parent'):

                            # retrieve value from a widget

                            arg_map[param_name][subparam_index] = (
                                self.data
                                ['subparam_widget_map']
                                [param_name]
                                [subparam_index]
                                ['widget_kwargs']
                                ['value']
                            )

                ## otherwise, if it doesn't have any subparameters, we assign
                ## the default value for the parameter, according to
                ## its specific variable kind:
                ##
                ## - an empty tuple for a positional-variable parameter, or
                ## - an empty dict for a keyword-variable parameter

                else:
                    arg_map[param_name] = () if kind == "var_pos" else {}

            ## if the param name is not in the variable kind map,
            ## it means it is not a variable parameter,
            ## so we perform suitable checks

            else:

                ## if the parameter's input socket lacks a parent,
                ## try retrieving values from other sources

                input_socket = isl_flmap[param_name]

                if not hasattr(input_socket, 'parent'):

                    # try assigning the default value for the input,
                    # if it exists

                    try:
                        arg_map[param_name] = self.default_map[param_name]

                    except KeyError:
                        pass

                    # try assigning a value from an embedded widget
                    # if such value exists, (note that this is tried
                    # regardless of whether the previous try statement
                    # succeeds, because values set on widgets by users
                    # have precedence over the actual default values
                    # defined in the callables)

                    try:

                        arg_map[param_name] = (
                            self.data
                            ['param_widget_value_map']
                            [param_name]
                        )

                    except KeyError:
                        pass

                    # if, after the attempted assignments above, the input
                    # still isn't available, then it can only mean the
                    # node is inexecutable due to lack of input sources;
                    #
                    # we store its name on the 'lacking_data_source' list

                    if param_name not in arg_map:
                        lacking_data_source.append(param_name)

        ### if parameters lacking data sources were found,
        ### raise a LackOfInputError

        if lacking_data_source:
            raise LackOfInputError(self, lacking_data_source)

    def perform_pre_execution_setups(self):
        """If unpack data received in subparameters if requested."""

        ### reference and alias argument map locally for quicker
        ### and easier access
        arg_map = self.argument_map

        ### iterate over the name of each parameter, performing
        ### checks and acting according to their results

        for param_name, kind in self.var_kind_map.items():

            ## retrieve subparam value map
            subparam_value_map = arg_map[param_name]

            ## iterate over existing subparameters (if any),
            ## unpacking the argument if requested

            for subparam_index in self.data['subparam_map'][param_name]:

                # perform additional setups depending on the
                # specific kind of variable parameter we have

                if kind == 'var_pos':

                    # retrieve the list of subparameters that must
                    # be unpacked
                    subparams_for_unpacking = (
                        self.data['subparam_unpacking_map'][param_name]
                    )

                    # retrieve the values of each subparameter in the
                    # order defined by the subparameter indices
                    # building a list with the values

                    param_args = []

                    for index in sorted(subparam_value_map):

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

                    # replace the parameter data in the argument map
                    # by the list we populated
                    arg_map[param_name] = param_args

                elif kind == 'var_key':

                    # retrieve map containing name of keyword for each
                    # subparameter
                    subparam_keywords = self.data['subparam_keyword_map']

                    # now build a new dictionary with the sorted keys
                    # from the subparam value map and its values

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
                        "there shouldn't be possible to specify a variable"
                        " parameter of a kind which is neither 'var_pos' or"
                        " 'var_key'"
                    )


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
