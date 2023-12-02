"""Facility with graph execution operation."""

### standard library imports

from time import time

from io import StringIO

from contextlib import redirect_stdout

from datetime import datetime

from os import linesep


### local imports

from ..config import APP_REFS

from ..appinfo import (
    BACKDOOR_INDICATIVE_VAR_NAMES,
    SIDEVIZ_FROM_OUTPUT_VAR_NAME,
    LOOPVIZ_FROM_OUTPUT_VAR_NAME,
)

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

from .utils import lay_arguments_and_execute, yield_upstream_nodes


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
        self.nodes_to_reference_callable = set()
        self.executed_nodes = set()

        ### create map to track node execution time
        self.node_exec_time_map = {}

    def execute_graph(self, nodes_to_visit=None):
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

        ### if the nodes to be visited were not specified, we use all
        ### the existing ones minus the commented out ones

        if nodes_to_visit is None:

            ### reference, clear and update a set to hold
            ### references of nodes to be visited

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

        ### if the nodes to be visited were specified, though, we filter out
        ### the commented out ones before using the remaining ones (if any)

        else:

            nodes_to_visit = {
                node
                for node in nodes_to_visit
                if not node.data.get("commented_out", False)
            }

            ### if there's no remaining nodes to visit among the given ones,
            ### it means they were all commented out, so notify user via
            ### dialog and cancel operation by returning earlier

            if not nodes_to_visit:

                create_and_show_dialog(
                    "Can't execute given nodes because they are all"
                    " commented out."
                )

                return


        ### since now we have nodes to visit, let's futher separate
        ### them into nodes meant for execution and perform related
        ### setups

        nodes_to_execute = self.nodes_to_execute
        nodes_to_execute.clear()

        nodes_to_execute.update(

            node
            for node in nodes_to_visit

            ## only include nodes with a main callable
            if hasattr(node, "main_callable")

            ## but exclude those in 'callable' mode
            if node.data.get('mode') != 'callable'

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

        ### let's also separate the nodes to visit into
        ### nodes used for referencing their callable

        nodes_to_reference_callable = self.nodes_to_reference_callable
        nodes_to_reference_callable.clear()

        nodes_to_reference_callable.update(
            node
            for node in nodes_to_visit
            if hasattr(node, "main_callable")
            if node.data.get('mode') == 'callable'
        )

        ### reference and clear set to store references of
        ### executed nodes

        executed_nodes = self.executed_nodes
        executed_nodes.clear()

        ### reference and clear map to store execution time
        ### of individual nodes

        node_exec_time_map = self.node_exec_time_map
        node_exec_time_map.clear()

        ### perform checks and redict data from the corresponding
        ### set of nodes

        try:
            self.check_nodes_and_redirect_data(nodes_to_direct_data)

        except ProxyNodesLackingDataError as err:

            create_and_show_dialog(str(err))
            return

        ### reference callables from the corresponding set of nodes
        self.reference_callables(nodes_to_reference_callable)

        ### mark the beginning of the node layout execution
        layout_exec_start = time()

        ### we'll now keep iterating while there are
        ### nodes left to be executed
        last_err = None
        while nodes_to_execute:

            ### try executing each node

            try:

                ## iterate over each node

                for node in nodes_to_execute:

                    ## check whether node is ready for
                    ## execution

                    try:
                        node.check_pending_parameters()

                    ## if a node is just waiting input
                    ## from another one, just pass
                    except WaitingInputException:
                        pass

                    ## if check doesn't raise an error...

                    else:

                        ## check whether node has a callable used as a
                        ## backdoor to retrieve visuals from it, storing
                        ## such backdoor if so

                        for var_name in BACKDOOR_INDICATIVE_VAR_NAMES:

                            if hasattr(node, var_name):
                                backdoor = getattr(node, var_name)
                                break

                        else:
                            backdoor = None

                        ## pick appropriate callable object depending on
                        ## whether the backdoor exists
                        callable_obj = backdoor if backdoor else node.main_callable

                        ### try executing the callable by passing the needed
                        ### arguments to a function that will execute it and
                        ### return the callable's return value

                        try:

                            ## execute

                            node_exec_start = time()

                            return_value = lay_arguments_and_execute(
                                callable_obj, node.argument_map, node.signature_obj
                            )

                            node_exec_time_map[node.id] = time() - node_exec_start

                            output_to_send = return_value

                        ### if an unexpected error occurs,
                        ### raise a custom error from the
                        ### original one

                        except Exception as err:
                            raise NodeCallableError(node) from err

                        ### if needed:
                        ###   - redefine output to be sent to downstream nodes
                        ###   - set visuals/looping

                        try:

                            if backdoor:

                                node.set_visual(return_value['in_graph_visual'])

                                if hasattr(node, 'loop_entering_command'):

                                    node.loop_data = return_value['loop_data']

                                    if node.preview_toolbar.check_button.get():
                                        node.loop_entering_command()

                                output_to_send = return_value.get('output')

                            elif hasattr(node, SIDEVIZ_FROM_OUTPUT_VAR_NAME):

                                node.set_visual(
                                    node.get_sideviz_from_output(return_value)
                                )

                                ###

                                loop_data_retrieval_op = (
                                    getattr(node, LOOPVIZ_FROM_OUTPUT_VAR_NAME, None)
                                )

                                if loop_data_retrieval_op:

                                    node.loop_data = loop_data_retrieval_op(return_value)

                                    if node.preview_toolbar.check_button.get():
                                        node.loop_entering_command()

                        except Exception as err:

                            raise RuntimeError(
                                "Error while setting visual/looping/output."
                            ) from err


                        ###

                        # send its return value to
                        # other nodes as needed

                        self.send_output_from_executed(
                            node,
                            output_to_send,
                        )

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

                ## clear all stored arguments
                self.clear_arguments()
                last_err = err
                ## break out of the "while loop"
                break

        ### provided everything went ok...

        else:

            ### clear all stored arguments
            self.clear_arguments()

            ### report the time taken to execute the layout in the
            ### status label

            ## XXX both layout execution time and indivual
            ## node time (as well as their sum) should also
            ## be logged in the user logger

            layout_exec_time = time() - layout_exec_start

            tracked_nodes_total = sum(

                ## item
                node_exec_time_map[node.id]

                ## source
                for node in executed_nodes

                ## filter
                if not getattr(
                    node.signature_callable, "dismiss_exec_time_tracking", False
                )
            )

            time_for_humans = friendly_delta_from_secs(tracked_nodes_total)

            set_status_message(f"Total execution time was {time_for_humans}")
            
        if last_err is None:
            return
            
        ## if the error is among the ones listed
        ## below, just notify the user via dialog,
        ## using the error converted to a string
        ## as the error message

        if isinstance(
            last_err,
            (
                MissingInputError,
                MissingOutputError,
                PositionalSubparameterUnpackingError,
                KeywordSubparameterUnpackingError,
            ),
        ):

            create_and_show_dialog(
                str(last_err),
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

            if isinstance(last_err, NodeCallableError):

                # grab the node wherein the
                # error bubbled up
                error_node = last_err.node

                # grab the original error
                original_error = last_err.__cause__

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
                ).format(last_err.__class__.__name__, str(last_err))

                create_and_show_dialog(
                    error_msg,
                    level_name="error",
                )

        

    def check_nodes_and_redirect_data(self, nodes_to_direct_data):

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

    def reference_callables(self, nodes_to_reference_callable):

        for node in nodes_to_reference_callable:

            ### send callable reference to the output socket children, if it has

            try:
                children = node.callable_output_socket.children
            except AttributeError:
                pass
            else:

                callable_reference = node.main_callable

                for child in children:
                    child.receive_input(callable_reference)

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

        if hasattr(node, 'output_socket_live_map'):
            output_sockets = node.output_socket_live_map.values()
        else:
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

                print(f"Graph executed at {datetime.now()} (local date/time)")

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

    def execute_node_after_upstream_ones(self, node):
        self.execute_graph(set(yield_upstream_nodes(node)))

    def clear_arguments(self):
        """Clear arguments from nodes.

        After a node is executed, its arguments are already cleared
        indirectly in the call to their perform_execution_setup()
        method. However, when it has other connected nodes downstream,
        such connected nodes will receive and store the output as
        argument(s).

        However, if an error happens and the graph execution is
        cancelled, this method is important to ensure those other
        nodes which didn't get to be called have the arguments received
        cleared.

        Additionally, if we are only executing a portion of the
        existing nodes, for instance, when we use the
        execute_node_after_upstream_ones() method, the connected
        nodes downstream will receive the arguments as well, even
        though they won't be executed. Rather than set complex checks
        to prevent such nodes to receive the arguments it is simpler
        to just clear everything anyway.

        The cleared data doesn't affect viewer nodes as well, because
        the outputs sent away as arguments to other nodes is also
        referenced in the viewer node anyway, so it is not lost when
        the arguments are cleared.
        """

        for node in self.nodes:

            if (
                not hasattr(node, 'argument_map')
                or node.data.get("commented_out", False)
                or node.data.get('mode') == 'callable'
            ):
                continue

            ### clear the argument map
            node.argument_map.clear()

            ### also insert empty dicts for subparameters if node allows
            ### them

            if hasattr(node, 'var_kind_map'):

                for param_name in node.var_kind_map:
                    node.argument_map[param_name] = {}
