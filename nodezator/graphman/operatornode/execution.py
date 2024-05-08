
### local imports

from ..exception import LackOfInputError

from ...ourstdlibs.behaviour import empty_function


class Execution:
    """Operations related to node execution."""

    def __init__(self):
        """Create objects to help during execution."""
        ### create a map to store input for parameters
        ### (the input comes only from other nodes)
        self.argument_map = {}

        ### create set to store ids of nodes providing incoming
        ### connections (inputs) to this one;
        ###
        ### also store references to recurrent methods

        isi = self.input_source_ids = set()

        self.clear_source_ids = isi.clear
        self.remove_source_ids = isi.difference_update
        self.add_source_id = isi.add

        ### set an empty function as the 'perform_pre_execution_setups'
        ### routine
        self.perform_pre_execution_setups = empty_function

    def perform_execution_setup(self):

        ### clear argument map
        self.argument_map.clear()

        ### clear set of ids from nodes that provide input to this one
        self.clear_source_ids()

    def send_id_to_direct_children(self):
        ### add id to direct children as source of data
        ###
        ### used for indegree tracking
        self.signature_output_socket.add_source_id(self.id)

    def check_and_setup_parameters(self):
        """Check whether parameters lack a source of daa.

        In case there's no source of data for one or more parameters,
        we raise a LackOfInputError explaining the situation.
        """
        ### create a list to hold names of parameters lacking a data source
        lacking_data_source = []

        ### iterate over each parameter, performing
        ### checks and acting according to their results

        for input_socket in self.input_sockets:

            if not hasattr(input_socket, 'parent'):
                lacking_data_source.append(input_socket.parameter_name)

        ### if parameters lacking data sources are found,
        ### raise LackOfInputError

        if lacking_data_source:
            raise LackOfInputError(self, lacking_data_source)

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
