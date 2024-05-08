"""Facility with graph execution operation."""

### standard library imports

from time import time

from io import StringIO

from contextlib import redirect_stdout

from datetime import datetime

from os import linesep

from itertools import chain


### local imports

from ..config import APP_REFS

from ..appinfo import (
    BACKDOOR_INDICATIVE_VAR_NAMES,
    SIDEVIZ_FROM_OUTPUT_VAR_NAME,
    LOOPVIZ_FROM_OUTPUT_VAR_NAME,
)

from ..userprefsman.main import USER_PREFS

from ..logman.main import get_new_logger

from ..dialog import create_and_show_dialog

from ..ourstdlibs.timeutils import friendly_delta_from_secs

from ..our3rdlibs.userlogger import USER_LOGGER

from ..our3rdlibs.behaviour import set_status_message

from ..textman.viewer.main import view_text

from .exception import (
    LackOfInputError,
    NodeCallableError,
    UnexpectedOutputError,
    PositionalSubparameterUnpackingError,
    KeywordSubparameterUnpackingError,
    ProxyNodesLackingDataError,
)

from .utils import lay_arguments_and_execute, yield_upstream_nodes



### create logger for module
logger = get_new_logger(__name__)


### constants

AT_LEAST_ONE_TO_EXECUTE = (
    "In order to execute the graph, it must have"
    " at least one node."
)

ALL_WERE_COMMENTED_OUT = (
    "Can't execute graph because all nodes are"
    " commented out. We must have at least one"
    " node not commented out in order to execute"
    " the graph."
)

ONLY_GIVEN_WERE_COMMENTED_OUT = (
    "Can't execute given nodes because they are all"
    " commented out."
)


### main class

class Execution:
    """Holds operations to assist in execution of the graph."""

    def __init__(self):

        ### create sets to hold references to specific subsets of the
        ### existing nodes
        ###
        ### also store recurrent methods in dedicated attributes for
        ### easier and quicker access

        for set_name in (
            'nodes_to_visit',
            'redirect_nodes',
            'data_nodes',
            'callable_mode_nodes',
            'nodes_to_sort',
        ):

            ### create set
            the_set = set()

            ### store it in attribute
            setattr(self, set_name, the_set)

            ### reference its methods as attributes as well

            for method_name, substr_to_replace in (
                ('clear', 'nodes'),
                ('add', 'node'),
            ):

                method = getattr(the_set, method_name)

                attr_name = (
                    method_name
                    + '_'
                    + set_name.replace('nodes', substr_to_replace)
                )

                setattr(self, attr_name, method)


        ### create list used to sort groups of nodes (generations) to
        ### be executed;
        ###
        ### also reference useful recurrent methods

        node_generations = self.node_generations = []

        self.clear_node_generations = node_generations.clear
        self.append_node_generation = node_generations.append

        ### create list of executed nodes
        self.executed_nodes = []

        ### create map to track node execution time
        self.node_exec_time_map = {}

    def execute_graph(self, requested_nodes=None):
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

            create_and_show_dialog(AT_LEAST_ONE_TO_EXECUTE, level_name='info')
            return

        ### define the nodes to be visited by filtering out the commented out
        ### ones

        ## reference and clear set to hold references of nodes to be visited

        nodes_to_visit = self.nodes_to_visit
        nodes_to_visit.clear()

        ## if the nodes requested for execution were not specified...

        if requested_nodes is None:

            ## consider all existing ones as requested
            requested_nodes = self.nodes

            ## reference message to show in case requested nodes are commented out
            commented_out_message = ALL_WERE_COMMENTED_OUT

        ## if the nodes to be visited were specified, reference message to show in
        ## case requested nodes are commented out

        else:
            commented_out_message = ONLY_GIVEN_WERE_COMMENTED_OUT

        ## filter out commented out nodes

        nodes_to_visit.update(
            node
            for node in requested_nodes
            if not node.data.get('commented_out', False)
        )

        ## if no nodes to visit remain, notify user via dialog and cancel
        ## operation by returning earlier

        if not nodes_to_visit:

            create_and_show_dialog(commented_out_message, level_name='info')
            return

        ### let's also split the nodes to visit into different categories
        ### by storing them in dedicated sets
        ###
        ### the nodes meant for sorting are also subject to additional
        ### setups and checks

        ## clear sets

        self.clear_redirect_nodes()
        self.clear_data_nodes()
        self.clear_callable_mode_nodes()
        self.clear_nodes_to_sort()

        ## reference their add() operations locally for quicker and easier
        ## access

        add_redirect_node = self.add_redirect_node
        add_data_node = self.add_data_node
        add_callable_mode_node = self.add_callable_mode_node
        add_node_to_sort = self.add_node_to_sort

        ## try iterating over nodes, adding them to specific sets and
        ## performing extra tasks as needed

        try:

            for node in nodes_to_visit:

                if not hasattr(node, 'main_callable'):

                    if 'source_name' in node.data:
                        add_redirect_node(node)

                    else:
                        add_data_node(node)

                elif node.data.get('mode') == 'callable':
                    add_callable_mode_node(node)

                else:

                    add_node_to_sort(node)

                    ## perform extra setups/checks needed to ensure the
                    ## node is able and ready to be executed after being
                    ## sorted

                    node.perform_execution_setup()
                    node.check_and_setup_parameters()

        ## if one of the nodes meant for sorting is lacking input(s),
        ## notify user via dialog and cancel operation by returning earlier

        except LackOfInputError as err:

            create_and_show_dialog(str(err), level_name='error')
            return

        ### perform checks and redirect data from the corresponding
        ### set of nodes

        try:
            _check_data_nodes_and_send_data(self.data_nodes)

        except ProxyNodesLackingDataError as err:

            create_and_show_dialog(str(err), level_name='error')
            return

        ### reference callables from the corresponding set of nodes
        _reference_callables(self.callable_mode_nodes)

        ### at this point, all the nodes, except the ones for sorting,
        ### were visited and dealt with already;
        ###
        ### now it is time to sort the remaining nodes so we can execute
        ### them
        self._sort_nodes()

        ### make preparations to execute the sorted nodes

        ## reference and clear list to store references of executed nodes

        executed_nodes = self.executed_nodes
        executed_nodes.clear()

        ## reference and clear map to store execution time
        ## of individual nodes

        node_exec_time_map = self.node_exec_time_map
        node_exec_time_map.clear()

        ## mark the beginning of the node layout execution
        layout_exec_start = time()


        ### we can finally start executing the sorted nodes;
        ###
        ### the nodes were sorted and divided in different groups
        ### called generations;
        ###
        ### iterate over the sorted nodes one by one, executing them and
        ### performing several other related tasks as needed, like sending
        ### output to the next nodes, etc.

        for node in chain.from_iterable(self.node_generations):

            ### try executing the node

            try:

                ## first, perform pre-execution setups
                node.perform_pre_execution_setups()

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

                _send_output_to_connected_nodes(
                    node,
                    output_to_send,
                )

                # perform its execution setup
                node.perform_execution_setup()

                # append node to list of executed ones
                executed_nodes.append(node)


            ### if an error is thrown, act according to its
            ### class

            except Exception as err:

                ## clear all stored arguments
                _clear_arguments(self.nodes)

                ## if the error is among the ones listed
                ## below, just notify the user via dialog,
                ## using the error converted to a string
                ## as the error message

                if isinstance(
                    err,
                    (
                        UnexpectedOutputError,
                        PositionalSubparameterUnpackingError,
                        KeywordSubparameterUnpackingError,
                    ),
                ):

                    create_and_show_dialog(str(err), level_name="error")

                ## any other kind of error is either within the node being
                ## executed or completely unexpected, so we take further
                ## measures

                else:


                    ## build a custom log message to be logged
                    ## depending on whether the error was caused
                    ## during call/execution of a node's callable
                    ## or not

                    if isinstance(err, NodeCallableError):

                        # grab the node wherein the
                        # error bubbled up
                        error_node = err.node

                        # grab the original error
                        original_error = err.__cause__

                        log_message = (
                            f"'{error_node.title_text}'() callable from node"
                            f" #{error_node.id} raised an error."
                        )


                    ## otherwise we just notify the user
                    ## with a custom error message

                    else:

                        log_message = (
                            "An unexpected error occurred during graph"
                            " execution."
                        )


                    ## log traceback

                    logger.exception(log_message)
                    USER_LOGGER.exception(log_message)

                    ## notify user via dialog

                    dialog_message = log_message + (
                        " Check the user log for more info (on"
                        " graph/canvas, press <Ctrl+Shift+j> or access"
                        " the \"Help > Show user log\" option on menubar)."
                    )

                    create_and_show_dialog(dialog_message, level_name='error')


                ## break out of the for-loop (stop iterating over sorted
                ## nodes for execution)
                break

        ### provided everything went ok, we didn't have to break out of the
        ### for-loop, which means we now enter this corresponding else clause

        else:

            ### clear all stored arguments on all nodes
            _clear_arguments(self.nodes)

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
                    node.signature_callable, 'dismiss_exec_time_tracking', False
                )
            )

            time_for_humans = friendly_delta_from_secs(tracked_nodes_total)

            set_status_message(f'Total execution time was {time_for_humans}')

    def _sort_nodes(self):
        """Sort nodes.

        Nodes are sorted so that the ones which depend on the input of other
        nodes appear after them.

        Uses a breadth-first topological sort algorithm, gathering nodes in
        different groups called generations.

        The first generation is formed by nodes that don't have incoming
        edges. Each subsequent generation is formed by nodes which expect
        inputs solely from the nodes on the previous generation(s) and so on.
        """
        ### clear list where generations will be stored in order
        self.clear_node_generations()

        ### reference objects locally for quicker and easier access

        ## operation to append a node generation
        append_node_generation = self.append_node_generation

        ## set of nodes to sort into generations
        nodes_to_sort = self.nodes_to_sort

        ### send ids of the nodes to their direct children, so the
        ### children can keep track of their indegree

        for node in nodes_to_sort:
            node.send_id_to_direct_children()

        ### while there's nodes to sort, keep creating and appending
        ### new node generations from the nodes with indegree == 0, always
        ### decrementing the indegree of their direct children

        while nodes_to_sort:

            ## create generation from nodes whose indegree == 0, that is,
            ## nodes with no incoming edges;
            ##
            ## however, the meaning of indegree == 0 was extended here to
            ## also mean nodes whose incoming edges come from nodes in
            ## previous generation(s)

            node_generation = [
                node
                for node in nodes_to_sort
                if len(node.input_source_ids) == 0
            ]

            ## now that we defined a new generation, append it to the
            ## dedicated list
            append_node_generation(node_generation)

            ## and remove them from the set of nodes to sort
            nodes_to_sort.difference_update(node_generation)

            ## create a set of ids from the nodes in this generation
            ## and use it to remove such ids from the remaining nodes
            ## to be sorted
            ##
            ## this is a way to signal the remaining nodes that the
            ## nodes with those ids are already stored in previous
            ## generation(s)

            ids_to_remove = {node.id for node in node_generation}

            for node in nodes_to_sort:
                node.remove_source_ids(ids_to_remove)

    def execute_with_custom_stdout(self):

        with StringIO() as custom_stdout:

            ###

            with redirect_stdout(custom_stdout):

                # XXX is calling between f-string '{}' characters allowed in
                # Python 3.7? check and fix if needed to keep compatibility
                # with that version
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



### support functions

def _check_data_nodes_and_send_data(data_nodes):

    nodes_lacking_data = {
        node
        for node in data_nodes
        if not hasattr(node, 'widget')
    }

    if nodes_lacking_data:
        raise ProxyNodesLackingDataError(nodes_lacking_data)

    for node in data_nodes:

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

def _reference_callables(callable_mode_nodes):
    """For each given node, send callable reference through edges, if any."""

    for node in callable_mode_nodes:

        try:
            children = node.callable_output_socket.children
        except AttributeError:
            pass
        else:

            callable_reference = node.main_callable

            for child in children:
                child.receive_input(callable_reference)

def _send_output_to_connected_nodes(node, output):
    """Send output to nodes connected to the given one.

    If the given one has connections to other nodes.

    Parameters
    ==========

    node (graphman.callablenode.main.CallableNode or subclass)
        node from which the output was produced.
    output (any Python value)
        output produced by the given node.
    """
    ### retrieve iterable with all output sockets from the given node
    ###
    ### note that whenever traversing the graph, we usually only worry
    ### about the 'output_sockets' collections, but here we check the
    ### existence of the live map as well;
    ###
    ### the reason for that is that here we need to know the number of
    ### existing output sockets rather than the number of output sockets
    ### with connections; when traversing we only care about the connected
    ### ones, but here we need to know the exact number because if it
    ### is higher than 1 it means the expected output is a mapping containing
    ### each output; that is why only here we worry about the output
    ### socket live map, which is present in all callable nodes and their
    ### subclasses, except the operator nodes, since they only ever
    ### have a single output socket in signature mode

    if hasattr(node, 'output_socket_live_map'):
        output_sockets = node.output_socket_live_map.values()

    else:
        output_sockets = node.output_sockets

    ### now that we retrieved the appropriate collection of references
    ### to the existing output sockets, we can properly obtain its length,
    ### that is, the quantity of output sockets, and treat the output
    ### according to that quantity

    ## if there's more than one socket, then the output received is expected
    ## to be a mapping;
    ##
    ## each output socket has an output name that serves as a key to retrieve
    ## a value from this mapping that must be sent via that output socket
    ## (if that socket has children)

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
                        socket.output_name
                        for socket in output_sockets
                    )

                    ## pass relevant data to the
                    ## exception constructor and
                    ## raise it from the original
                    ## exception

                    raise UnexpectedOutputError(
                        node, expected_outputs
                    ) from err

                ## send value to each child

                else:

                    for child in children:
                        child.receive_input(value_to_be_sent)

    ### otherwise, if we have only one output socket, the output received
    ### is itself the value to be sent to the output socket children, if it
    ### has children

    else:

        for socket in output_sockets:

            try:
                children = socket.children

            except AttributeError:
                pass

            else:

                for child in children:
                    child.receive_input(output)

def _clear_arguments(nodes):
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
    for node in nodes:

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

