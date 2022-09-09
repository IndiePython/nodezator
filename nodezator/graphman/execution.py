"""Facility with graph execution operation."""

### standard library imports

from time import time

from io import StringIO

from contextlib import redirect_stdout

from datetime import datetime

from os import linesep


### local imports

from ..config import APP_REFS

from ..userprefsman.main import USER_PREFS

from ..logman.main import get_new_logger

from ..dialog import (
    create_and_show_dialog,
    show_formatted_dialog,
)

from ..ourstdlibs.timeutils import friendly_delta_from_secs

from ..our3rdlibs.userlogger import USER_LOGGER

from ..our3rdlibs.behaviour import set_status_message

from ..textman.viewer.main import view_text

from .exception import (
    MissingInputError,
    WaitingInputException,
    NodeCallableError,
    MissingOutputError,
    PositionalSubparameterUnpackingError,
    KeywordSubparameterUnpackingError,
    ProxyNodesLackingDataError,
)

from .utils import lay_arguments_and_execute


### create logger for module
logger = get_new_logger(__name__)


class Execution:
    """Holds operations to execute the graph."""

    def __init__(self):

        ### create set to hold references to specific
        ### subsets of the existing nodes

        self.nodes_to_visit = set()
        self.nodes_to_execute = set()
        self.nodes_to_direct_data = set()
        self.executed_nodes = set()

        ### create map to track node execution time
        self.node_exec_time_map = {}

    def execute_graph(self):
        """Travel the graph, executing each node.

        Works by executing node by node until all of them
        are finished.

        Once a node is finished, it's outputs are sent to
        the inputs of other linked nodes, if any.
        """
        ### if there's no nodes in the graph, notify user
        ### via dialog and cancel operation by returning
        ### earlier

        if not self.nodes:

            create_and_show_dialog(
                "In order to execute the graph, it must have" " at least one node."
            )

            return

        ### also reference, clear and update a set to hold
        ### references of nodes to be visited, that is, all
        ### the existing ones minus the commented out ones

        nodes_to_visit = self.nodes_to_visit
        nodes_to_visit.clear()

        nodes_to_visit.update(
            node for node in self.nodes if not node.data.get("commented_out", False)
        )

        ### if there's no nodes to visit in the graph,
        ### it means all existing nodes are commented out,
        ### so notify user via dialog and cancel operation
        ### by returning
        ### earlier

        if not nodes_to_visit:

            create_and_show_dialog(
                "Can't execute graph because all nodes are"
                " commented out. We must have at least one"
                " node not commented out in order to execute"
                " the graph."
            )

            return

        ### since now we have nodes to visit, let's
        ### futher separate then into nodes meant for
        ### execution and perform related setups

        nodes_to_execute = self.nodes_to_execute
        nodes_to_execute.clear()

        nodes_to_execute.update(
            node for node in nodes_to_visit if hasattr(node, "main_callable")
        )

        for node in nodes_to_execute:
            node.perform_execution_setup()

        ### let's also separate the nodes to visit into
        ### nodes used for directing data

        nodes_to_direct_data = self.nodes_to_direct_data
        nodes_to_direct_data.clear()

        nodes_to_direct_data.update(
            node
            for node in nodes_to_visit
            if not hasattr(
                node,
                "main_callable",
            )
        )

        ### reference and clear set to store references of
        ### executed nodes

        executed_nodes = self.executed_nodes
        executed_nodes.clear()

        ### reference and clear map to store execution time
        ### of individual nodes

        node_exec_time_map = self.node_exec_time_map
        node_exec_time_map.clear()

        ### perform checks and setups related to nodes
        ### used to direct data

        try:
            self.check_and_setup_data_redirection(nodes_to_direct_data)

        except ProxyNodesLackingDataError as err:

            create_and_show_dialog(str(err))
            return

        ### mark the beginning of the node layout execution
        layout_exec_start = time()

        ### we'll now keep iterating while there are
        ### nodes left to be executed

        while nodes_to_execute:

            ### try executing each node

            try:

                ## iterate over each node

                for node in nodes_to_execute:

                    ## try executing the node in order to
                    ## obtain the elements needed to
                    ## execute its callable

                    try:
                        (main_callable, argument_map, callable_signature) = node()

                    ## if a node is just waiting input
                    ## from another one, just pass
                    except WaitingInputException:
                        pass

                    ## if node execution succeeds...

                    else:

                        ### now try executing the node's
                        ### callable by passing the needed
                        ### arguments to a function that
                        ### will execute it and return the
                        ### callable's return value

                        try:

                            node_exec_start = time()

                            return_value = lay_arguments_and_execute(
                                main_callable, argument_map, callable_signature
                            )

                            node_exec_time_map[node.id] = time() - node_exec_start

                        ### if an unexpected error occurs,
                        ### raise a custom error from the
                        ### original one

                        except Exception as err:

                            raise NodeCallableError(node) from err

                        # send its return value to
                        # other nodes as needed

                        self.send_output_from_executed(
                            node,
                            return_value,
                        )

                        # TODO should we perform exec
                        # setup as well if the node has
                        # an error (in case we go into
                        # the 'exception' clause above)?
                        # ponder

                        # perform its execution setup
                        node.perform_execution_setup()

                        # add the node to the set of
                        # executed nodes
                        executed_nodes.add(node)

                ## if iteration went ok, remove executed
                ## nodes from remaining ones
                else:
                    nodes_to_execute -= executed_nodes

            ### if an error is thrown, act according to its
            ### class

            except Exception as err:

                ## regardless of the kind of error...

                # remove executed_nodes from the
                # remaining ones
                nodes_to_execute -= executed_nodes

                # the remaining nodes have their execution
                # setup performed

                for node in nodes_to_execute:
                    node.perform_execution_setup()

                ## if the error is among the ones listed
                ## below, just notify the user via dialog,
                ## using the error converted to a string
                ## as the error message

                if isinstance(
                    err,
                    (
                        MissingInputError,
                        MissingOutputError,
                        PositionalSubparameterUnpackingError,
                        KeywordSubparameterUnpackingError,
                    ),
                ):

                    create_and_show_dialog(
                        str(err),
                        level_name="error",
                    )

                ## any other kind of error is unexpected,
                ## so we take further measures

                else:

                    ## log traceback in the user log

                    USER_LOGGER.exception(
                        "An error occurred" " during graph execution."
                    )

                    ## if the error was caused during call
                    ## or execution of a node's callable,
                    ## display a custom error message

                    if isinstance(err, NodeCallableError):

                        # grab the node wherein the
                        # error bubbled up
                        error_node = err.node

                        # grab the original error
                        original_error = err.__cause__

                        show_formatted_dialog(
                            "node_callable_error_dialog",
                            error_node.title_text,
                            error_node.id,
                            original_error.__class__.__name__,
                            str(original_error),
                        )

                    ## otherwise we just notify the user
                    ## with a custom error message

                    else:

                        error_msg = (
                            "node layout execution failed"
                            " with an unexpected error. The"
                            " following message was issued"
                            " >> {}: {}"
                        ).format(err.__class__.__name__, str(err))

                        create_and_show_dialog(
                            error_msg,
                            level_name="error",
                        )

                ## break out of the "while loop"
                break

        ### provided everything went ok, report the
        ### time taken to execute the layout in the
        ### status label

        else:

            ## XXX both layout execution time and indivual
            ## node time (as well as their sum) should also
            ## be logged in the user logger

            layout_exec_time = time() - layout_exec_start

            tracked_nodes_total = sum(
                node_exec_time_map[node.id]
                for node in executed_nodes
                if not getattr(
                    node.signature_callable, "dismiss_exec_time_tracking", False
                )
            )

            time_for_humans = friendly_delta_from_secs(tracked_nodes_total)

            set_status_message(f"Total execution time was {time_for_humans}")

    def check_and_setup_data_redirection(
        self,
        nodes_to_direct_data,
    ):

        data_sources = set()
        lacking_data = set()

        for node in nodes_to_direct_data:

            if "source_name" not in node.data:

                (data_sources if hasattr(node, "widget") else lacking_data).add(node)

        if lacking_data:
            raise ProxyNodesLackingDataError(lacking_data)

        for node in data_sources:

            ### retrieve the value from the node's widget
            value = node.widget.get()

            ### send the output retrieved to the output
            ### socket children, if it has children

            try:
                children = node.output_socket.children
            except AttributeError:
                pass
            else:

                for child in children:
                    child.receive_input(value)

    def send_output_from_executed(self, node, output):
        """Send output to outlinked nodes, if any.

        Parameters
        ==========

        node (graphman.callablenode.main.CallableNode instance)
            node from which the output was produced.
        output (any Python value)
            output produced by the given node.
        """
        ### retrieve iterable with all output sockets
        ### from the given node
        output_sockets = node.output_sockets

        ### if there's more than one socket, then the output
        ### received is a dict, its keys identify through
        ### which output socket the respective value must
        ### be sent

        if len(output_sockets) > 1:

            ## iterate over each socket, checking whether
            ## it has children and, if so, retrieving its
            ## specific value to be sent to them

            for socket in output_sockets:

                try:
                    children = socket.children

                except AttributeError:
                    pass

                else:

                    ## try retrieving value to be sent

                    try:
                        value_to_be_sent = output[socket.output_name]

                    ## if not possible, raise a missing
                    ## output error to notify user of
                    ## the problem

                    except (TypeError, KeyError) as err:

                        ## create iterator with output
                        ## names of output sockets

                        expected_outputs = (
                            socket.output_name for socket in output_sockets
                        )

                        ## pass relevant data to the
                        ## exception constructor and
                        ## raise it from the original
                        ## exception

                        raise MissingOutputError(
                            node,
                            expected_outputs,
                        ) from err

                    ## send value to each child

                    else:

                        for child in children:

                            (child.receive_input(value_to_be_sent))

        ### otherwise, the output received is itself the
        ### value to be sent to the output socket children,
        ### if it has children

        else:

            for socket in output_sockets:

                try:
                    children = socket.children

                except AttributeError:
                    pass

                else:

                    for child in children:
                        child.receive_input(output)

    def execute_with_custom_stdout(self):

        with StringIO() as custom_stdout:

            ###

            with redirect_stdout(custom_stdout):

                print("Graph execution triggered at UTC:" f" {datetime.utcnow()}")

                self.execute_graph()

                print()

            ###

            stdout_lines = APP_REFS.custom_stdout_lines

            stdout_lines.extend(custom_stdout.getvalue().splitlines())

            max_lines = USER_PREFS["CUSTOM_STDOUT_MAX_LINES"]

            stdout_lines[:] = stdout_lines[-max_lines:]

            view_text(
                text=linesep.join(stdout_lines),
                header_text="Text from custom stdout",
                general_text_settings="custom_stdout",
                text_viewer_rect="custom_stdout",
                index_to_jump_to=-1,
            )
