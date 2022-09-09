### local imports

from ..exception import (
    MissingInputError,
    WaitingInputException,
)


class Execution:
    """Operations related to node execution."""

    def __init__(self):
        """Create objects to help during execution."""

        ### create a map to store input for parameters
        ### (the input comes only from other nodes)
        self.argument_map = {}

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

        ### clear the argument map
        self.argument_map.clear()

        ### setup the expects input map

        self.expects_input_map.clear()

        for input_socket in self.input_sockets:

            ### use the parameter name as key
            key = input_socket.parameter_name

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

            ## otherwise, it can only mean the node is
            ## inexecutable due to lack of input sources;
            ## we store its name on the
            ## 'lacking_data_source' list
            else:
                lacking_data_source.append(param_name)

        ### remove ready parameter names from pending set
        self.pending_param_names -= ready_param_names

        ### if parameters lacking data sources are found,
        ### raise MissingInputError

        if lacking_data_source:

            raise MissingInputError(
                self,
                lacking_data_source,
            )

        ### if there are parameters waiting for input,
        ### raise the WaitingInputException

        if waiting_input:

            raise WaitingInputException("node has parameters waiting for input")

    def receive_input(
        self,
        data,
        param_name,
        subparameter_index,
    ):
        """Store given data

        Parameters
        ==========

        data (any Python object)
            data sent by the graph manager, retrieved from
            another node.
        param_name (string)
            name of the parameter for which the data must
            be stored
        subparameter_index (None or int)
            we don't use this input in the operator node
            class, but it is receive in compliance with
            how input sockets work (its receive_input()
            method).
        """
        ### store the data in the argument map for the
        ### specified parameter
        self.argument_map[param_name] = data
