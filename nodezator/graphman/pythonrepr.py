"""Function for extending the graph manager."""

### standard library imports
from textwrap import indent, wrap


### local imports

from ..config import APP_REFS

from ..appinfo import NODE_SCRIPT_NAME

from ..classes2d.collections import List2D

from ..rectsman.utils import get_minimum_distance_function

from .utils import yield_subgraphs

from ..widget.defaultholder import DefaultHolder


### constants

NODE_SCRIPT_MODULE_NAME = NODE_SCRIPT_NAME[:-3]

COMMENT_WRAPPING_WIDTH = 0

NODE_CLUSTERING_INFLATION = (300, 300)

MAXIMUM_NODE_TEXT_BLOCK_DISTANCE = 50

DEFAULT_DOCSTRING = '"""Execute script version of Python visual graph."""'


class WaitingParentException(Exception):
    pass


### set to store snippet nodes whose source will be included in
### the Python representation of the graph
###
### this won't necessarily store the ids of all snippet nodes in
### the graph
SNIPPET_NODES = set()

### set to store general viewer nodes temporarily
GENVIEWER_NODES = set()


### main function

def python_repr(self):
    """Return python representation of graph."""

    ### if there are proxy nodes that don't have a parent (orphan)
    ### nor a widget (empty), cancel the operation altogether with
    ### an exception

    orphan_empty_proxies = [

        ## item
        node

        ## source
        for node in self.nodes

        ## filtering

        if (

            ## first condition
            hasattr(node, 'proxy_socket')

            ## second condition

            and (
                (not hasattr(node.proxy_socket, "parent"))
                and (not hasattr(node, "widget"))
            )

        )
    ]

    if orphan_empty_proxies:

        ids = [node.id for node in orphan_empty_proxies]

        raise RuntimeError(
             "There are orphan redirect nodes/empty data nodes in the graph"
             " which probably isn't desired, since they accomplish nothing."
            f" Here's a list with their ids: {ids}"
        )

    ### clear temporary collections

    SNIPPET_NODES.clear()
    GENVIEWER_NODES.clear()

    ### create list of standard library imports

    ## gather from user-defined and stlib nodes

    from_user_defined_and_stlib_nodes = {

        ### item
        node.stlib_import_text

        ### source
        for node in self.nodes

        ### filtering
        if hasattr(node, "stlib_import_text")

    }

    ## gather from encapsulations usage

    from_encapsulations_stlib_usage = set(

        ##
        sum(

            (
                ### item
                node.stlib_import_texts

                ### source
                for node in self.nodes

                ### filtering

                if hasattr(node, "stlib_import_texts")
                if (
                    not hasattr(node, 'substitution_callable')
                    or node.data['mode'] == 'callable'
                )
            ),
            [],
        )

    )

    ## gather from encapsulations annotations

    from_encapsulations_stlib_annotations = set(

        ##
        sum(

            (
                ### item
                node.stlib_annotation_import_texts

                ### source
                for node in self.nodes

                ### filtering

                if hasattr(node, "stlib_annotation_import_texts")
                if (
                    not hasattr(node, 'substitution_callable')
                    or node.data['mode'] == 'callable'
                )
            ),
            [],
        )

    )

    ##
    stlib_imports = sorted(
        from_user_defined_and_stlib_nodes 
        .union(from_encapsulations_stlib_usage)
        .union(from_encapsulations_stlib_annotations)
    )

    ### create list of third-party imports
    ###
    ### also, while iterating over general viewer nodes,
    ### gather references to them in a special collection
    ### for future usage

    ## gather from general viewer nodes (if any)

    from_genviewer_nodes = set()

    for node in self.nodes:

        if 'genviewer_id' not in node.data:
            continue

        GENVIEWER_NODES.add(node)

        if not hasattr(node, 'thirdlib_import_texts'):
            continue

        from_genviewer_nodes.update(node.thirdlib_import_texts)

    ## gather from other nodes (if any)

    # from user-defined and thirdlib nodes
    from_user_defined_and_thirdlib_nodes = {

      ### item
      node.third_party_import_text
      ### source
      for node in self.nodes
      ### filtering
      if hasattr(node, "third_party_import_text")

    }

    # from encapsulation usage

    from_encapsulations_third_usage = set(

        ##
        sum(

            (
                ### item
                node.third_party_import_texts
                ### source
                for node in self.nodes
                ### filtering
                if hasattr(node, "third_party_import_texts")
                if (
                    not hasattr(node, 'substitution_callable')
                    or node.data['mode'] == 'callable'
                )
            ),
            [],

        )

    )

    # from encapsulation annotations

    from_encapsulations_third_annotations = set(

        ##
        sum(

            (
                ### item
                node.third_party_annotation_import_texts
                ### source
                for node in self.nodes
                ### filtering
                if hasattr(node, "third_party_annotation_import_texts")
                if (
                    not hasattr(node, 'substitution_callable')
                    or node.data['mode'] == 'callable'
                )
            ),
            [],

        )

    )

    ## create sorted list from their union

    third_party_imports = sorted(
        from_genviewer_nodes
        .union(from_user_defined_and_thirdlib_nodes)
        .union(from_encapsulations_third_usage)
        .union(from_encapsulations_third_annotations)
    )

    ### store a flag indicating whether there are pygame
    ### imports

    at_least_one_pygame_import = any(
        'from pygame' in import_text
        for import_text in third_party_imports
    )

    ### create list of import statements for user-defined
    ### nodes

    node_callable_imports = sorted(

        ## a set: so we end up without duplicates

        set(

            # item: a "from ... import ..." statement

            (
                "from "
                + ".".join(
                    node.data["script_id"]
                    + (NODE_SCRIPT_MODULE_NAME,)
                )
                + " import "
                + node.main_callable.__name__
            )

            # source
            for node in self.nodes

            # filtering

            if (
                "script_id" in node.data
                and not hasattr(node, "substitution_callable")
                and not hasattr(node, "stlib_import_text")
                and not hasattr(node, "third_party_import_text")
            )
        )

    )

    # XXX: the 'substitution_callable' check a few lines above
    # probably isn't needed, since only some app-defined nodes are
    # supposed to use substitution callables; ponder, review and decide
    # what to do about this when convenient; there is at least another
    # check like this in this module that need reviewing as well;

    ### def statement

    func_name = "".join(

        ## item (a character)
        char

        ## source
        for char in APP_REFS.source_path.stem

        ## filtering
        if char.isalnum() or char == "_"

    )

    if func_name[0].isdigit() or not func_name:
        func_name = "_" + func_name

    def_statement = f"def {func_name}():"

    ### text blocks

    text_blocks = list(self.text_blocks)

    block_map = {id(block.rect): block for block in text_blocks}

    block_rects = [block.rect for block in text_blocks]

    ## docstring

    docstring = DEFAULT_DOCSTRING

    if text_blocks:

        result = self.origin_rect.collidelist(block_rects)

        if result != -1:

            colliding_text_block = block_map[id(block_rects.pop(result))]

            text = colliding_text_block.data["text"]

            docstring = (
                '"""' + text + ('\n"""' if len(text.splitlines()) > 1 else '"""')
            )

            ##
            text_blocks.remove(colliding_text_block)

    ##
    docstring = indent(
        docstring,
        " " * 4,
    )

    ### create text from objects in the graph forming
    ### its body, that is, calls and snippets from nodes,
    ### comments from nodes and text blocks

    ##
    graph_function_body = ""

    ##

    if self.nodes:

        node_clusters = [
            List2D(cluster)
            for cluster in self.nodes.get_clusters(NODE_CLUSTERING_INFLATION)
        ]

        set_text_block_refs(
            self.nodes,
            node_clusters,
            text_blocks,
        )


    ## for each subgraph, write each node as a call or reference to
    ## a callable object with proper indentation

    for subgraph in yield_subgraphs(self.nodes):

        ## filter out redirect nodes and nodes in callable mode

        subgraph = [

            ## item
            node

            ## source
            for node in subgraph

            ## filtering

            # nodes which are NOT redirect nodes

            if not (
                hasattr(node, "proxy_socket")
                and hasattr(node.proxy_socket, "parent")
            )

            # nodes which are NOT in callable mode
            if node.data.get('mode', 'expanded_signature') != 'callable'
        ]

        ##
        graph_function_body += "\n" * 2

        ##

        nodes_to_visit = set(subgraph)
        visited_nodes = set()

        subgraph_calls_text = ""

        while nodes_to_visit:

            for node in nodes_to_visit:

                try:
                    node_source = node_to_python_source(
                        node,
                        nodes_to_visit,
                        visited_nodes,
                        node_clusters,
                    )

                except WaitingParentException:
                    pass

                else:

                    subgraph_calls_text += node_source
                    visited_nodes.add(node)

            nodes_to_visit -= visited_nodes

        graph_function_body += indent(
            subgraph_calls_text,
            " " * 4,
        )

    ###

    if (not self.nodes) and text_blocks:

        get_lowest_dist_to_origin = get_minimum_distance_function(self.origin_rect)
        min_distance_to_origin = lambda block: get_lowest_dist_to_origin(block.rect)

        for text_block in sorted(text_blocks, key=min_distance_to_origin):

            ##
            graph_function_body += "\n" * 2

            ##

            lines = (
                wrap(
                    text_block.data["text"],
                    width=COMMENT_WRAPPING_WIDTH,
                )
                if COMMENT_WRAPPING_WIDTH
                else text_block.data["text"].splitlines()
            )

            # add each line with a preceeding prefix
            # and succeeding '\n' (we didn't manage
            # to do this with solutions using
            # str.join/textwrap.indent, but we
            # achieved what we wanted)

            for line_text in lines:

                graph_function_body += "### " + line_text + "\n"

        ##

        graph_function_body = indent(
            graph_function_body,
            " " * 4,
        )

    ### gather source of snippets used
    ###
    ### also clear the collection used to keep track
    ### of them

    for node in self.nodes:

        if (
            'capsule_id' not in node.data
            or hasattr(node, 'substitution_callable')
        ):
            continue

        SNIPPET_NODES.add(node)

    source_of_snippets = (
        gather_snippets_source()
        if SNIPPET_NODES
        else ''
    )

    SNIPPET_NODES.clear()

    ### gather source of general viewer nodes used,
    ### regardless of the mode, if any;
    ###
    ### also clear the collection used to keep track
    ### of them

    source_of_general_viewer_nodes = (
        gather_genviewer_source()
        if GENVIEWER_NODES
        else ''
    )

    GENVIEWER_NODES.clear()

    ## now concatenate the python text and return it

    return (
        "\n"
        + (
            (
                "### standard library imports"
                + ("\n" * 2)
                + "\n".join(stlib_imports)
                + ("\n" * 3)
            )
            if stlib_imports
            else ""
        )
        + (
            (
                "### third-party imports"
                + ("\n" * 2)
                + "\n".join(third_party_imports)
                + ("\n" * 3)
            )
            if third_party_imports
            else ""
        )
        + (
            "### local imports (node callables)"
            + ("\n" * 2)
            + "\n".join(node_callable_imports)
            + ("\n" * 3)
            if node_callable_imports
            else ""
        )
        + "\n"
        + "### main function"
        + "\n"
        + "\n"
        + def_statement
        + "\n"
        + docstring
        + graph_function_body
        + "\n\n"
        + (
            (
                "### encapsulations (utility functions)"
                + "\n\n" + source_of_snippets + "\n\n"
            )
            if source_of_snippets
            else ''
        )
        + (
            (
                "### general viewer node scripts"
                + "\n\n"
                + source_of_general_viewer_nodes + "\n\n"
            )
            if source_of_general_viewer_nodes 
            else ''
        )
        + (
            (
            "### since your graph uses pygame imports, in case you intend to execute this"
            + "\n### script *outside* Nodezator, make sure pygame-ce/its relevant modules are"
            + "\n### initialized and the display mode is set (depending on the imports used)"
            + "\n\n"
            )
            if at_least_one_pygame_import
            else ''
        )
        + "if __name__ == '__main__':\n"
        + f"    {func_name}()\n\n"
    )


### other utility functions


def set_text_block_refs(
    nodes,
    node_clusters,
    text_blocks,
):

    node_map = {id(node.rect): node for node in nodes}

    node_rects = [node.rect for node in nodes]

    cluster_map = {id(cluster.rect): cluster for cluster in node_clusters}

    cluster_rects = [cluster.rect for cluster in node_clusters]

    for text_block in text_blocks:

        get_lowest_dist = get_minimum_distance_function(text_block.rect)

        closest_obj = node_map[
            id(
                min(
                    node_rects,
                    key=get_lowest_dist,
                )
            )
        ]

        if get_lowest_dist(closest_obj.rect) > MAXIMUM_NODE_TEXT_BLOCK_DISTANCE:

            closest_obj = cluster_map[
                id(
                    min(
                        cluster_rects,
                        key=get_lowest_dist,
                    )
                )
            ]

        ## ignore redirect nodes and associated text
        ## blocks; text blocks close to redirect
        ## nodes are considered visual aids to help
        ## give context to the redirected data,
        ## rather than part of the graph function;

        if hasattr(closest_obj, "proxy_socket") and hasattr(
            closest_obj.proxy_socket, "parent"
        ):
            continue

        ##

        try:
            refs = closest_obj.text_block_refs
        except AttributeError:
            refs = closest_obj.text_block_refs = []

        refs.append(text_block)


def node_to_python_source(
    node,
    nodes_to_visit,
    visited_nodes,
    node_clusters,
):

    for cluster in node_clusters:

        if node in cluster:
            break

    else:
        raise RuntimeError("this else statement should never be" " reached")

    ###

    if (
        "script_id" in node.data
        or "stlib_id" in node.data
        or "builtin_id" in node.data
        or "genviewer_id" in node.data
        or "capsule_id" in node.data
        or "thirdlib_id" in node.data
    ) and not hasattr(node, "substitution_callable"):
        node_text_yielding_function = callable_node_to_call_text

    elif hasattr(node, "widget"):
        node_text_yielding_function = data_node_to_variable_assignment

    elif "operation_id" in node.data:
        node_text_yielding_function = operator_node_to_call_text

    else:
        node_text_yielding_function = node_to_code_snippet

    return node_text_yielding_function(
        node,
        cluster,
        nodes_to_visit,
        visited_nodes,
        node_clusters,
    )


def callable_node_to_call_text(
    node,
    cluster,
    nodes_to_visit,
    visited_nodes,
    node_clusters,
):

    call_text = node.title_text + "("

    insocket_flmap = node.input_socket_live_flmap
    widget_flmap = node.widget_live_flmap
    keyword_lmap = node.subparam_keyword_entry_live_map

    for param_name in node.signature_obj.parameters.keys():

        ### start by assigning a default value to the
        ### argument, which is the name of the parameter
        ### itself
        argument = param_name

        ### check whether parameter name is of variable
        ### kind, storing which kind, if it is the case
        try:
            kind = node.var_kind_map[param_name]

        ### if it isn't of variable kind...

        except KeyError:

            ### define a condition where the argument
            ### must be ommited, defaulting to False
            ommit_argument = False

            ### we check whether the parameter depends on
            ### different incomming data

            insocket = insocket_flmap[param_name]

            ### if it does...

            if hasattr(insocket, "parent"):

                ### first of all retrieve references to the parent socket
                ### and parent node

                parent = insocket.parent
                parent_node = parent.node

                ### ensure the parent node is not a redirect node

                while True:

                    if hasattr(parent_node, "proxy_socket") and hasattr(
                        parent_node.proxy_socket, "parent"
                    ):

                        parent = parent_node.proxy_socket.parent

                        parent_node = parent.node

                        continue

                    break

                ### now that we are sure we have a proper parent node,
                ### check whether it is in callable mode;
                ###
                ### it it is...

                if parent_node.data.get('mode', 'expanded_signature') == 'callable':

                    ### if we have an operator node, the incoming data is a lambda
                    ### representing the node
                    if 'operation_id' in parent_node.data:
                        argument = '(' + parent_node.get_lambda_source() + ')'

                    ### otherwise, it is a reference to the nodes callable

                    else:

                        argument = parent_node.title_text

                        ## additionally, if the node is a snippet node,
                        ## store a reference in a special collection

                        if 'capsule_id' in parent_node.data:
                            SNIPPET_NODES.add(parent_node)

                ### otherwise...

                else:

                    if parent_node not in visited_nodes:
                        raise WaitingParentException

                    argument = "_" + "_".join(
                        map(
                            str,
                            parent.get_id(),
                        )
                    )

            ### otherwise check whether there's an embedded
            ### widget with data for the parameter

            else:

                try:
                    widget = widget_flmap[param_name]

                ### if there's not, just pass
                except KeyError:
                    pass

                ### if it has...
                else:

                    ## if the argument is a default holder,
                    ## than it means the argument was
                    ## not edited, it might even not be
                    ## a python literal, so we make it
                    ## so it is ommited by assigning True
                    ## to the corresponding flag
                    if type(widget) is DefaultHolder:
                        ommit_argument = True

                    ## otherwise we use repr() of the value
                    ## it holds as the argument
                    else:
                        argument = repr(widget.get())

            ## if upon reaching this spot it is decided
            ## that the argument must not be ommited...

            if not ommit_argument:

                ## if parameter is of kind keyword-only,
                ## make it so the argument is passed with
                ## the parameter name

                if int(node.signature_obj.parameters[param_name].kind) == 3:

                    argument = f"{param_name}={argument}"

                ## concatenate the argument text to the
                ## call text
                call_text += argument + ", "

        ### if it is of variable kind...

        else:

            subparam_socket_map = insocket_flmap[param_name]

            unpacked_subparams = node.data["subparam_unpacking_map"][param_name]

            call_text += "*(" if kind == "var_pos" else "**{"

            for subparam_index in sorted(subparam_socket_map.keys()):

                insocket = subparam_socket_map[subparam_index]

                ### we check whether the subparameter
                ### depends on other sources of data

                if hasattr(insocket, "parent"):

                    ### first of all retrieve references to the parent socket
                    ### and parent node

                    parent = insocket.parent
                    parent_node = parent.node

                    ### ensure the parent node is not a redirect node

                    while True:

                        if hasattr(parent_node, "proxy_socket") and hasattr(
                            parent_node.proxy_socket, "parent"
                        ):

                            parent = parent_node.proxy_socket.parent

                            parent_node = parent.node

                            continue

                        break

                    ### now that we are sure we have a proper parent node,
                    ### check whether it is in callable mode;
                    ###
                    ### it it is...

                    if parent_node.data.get('mode', 'expanded_signature') == 'callable':

                        ### if we have an operator node, the incoming data is a lambda
                        ### representing the node
                        if 'operation_id' in parent_node.data:
                            subargument = '(' + parent_node.get_lambda_source() + ')'

                        ### otherwise, it is a reference to the nodes callable

                        else:

                            subargument = parent_node.title_text

                            ## additionally, if the node is a snippet node,
                            ## store a reference in a special collection

                            if 'capsule_id' in parent_node.data:
                                SNIPPET_NODES.add(parent_node)

                    ### otherwise...

                    else:

                        if parent_node not in visited_nodes:
                            raise WaitingParentException

                        subargument = "_" + "_".join(map(str, parent.get_id()))

                ## a widget

                else:

                    widget = widget_flmap[param_name][subparam_index]

                    subargument = repr(widget.get())

                if kind == "var_pos":

                    if subparam_index in unpacked_subparams:
                        subargument = f"*{subargument}"

                elif kind == "var_key":

                    if subparam_index in unpacked_subparams:
                        subargument = f"**{subargument}"

                    else:

                        keyword = keyword_lmap[subparam_index].get()

                        subargument = f"{repr(keyword)}: {subargument}"

                call_text += subargument + ", "

            call_text += "), " if kind == "var_pos" else "}, "

    ###

    call_text += ")"

    ###

    comment_prefix = "# " if node.data.get("commented_out", False) else ""

    output_sockets = node.output_socket_live_map.values()

    if len(output_sockets) > 1:

        dict_name = f"_temp_dict_{node.id}"

        max_char_no = (
            max(len(socket.output_name) for socket in output_sockets)
            + len(str(node.id))
            + 2  # initial '_' plus '_' between node id and
            # output_name
        )

        max_char_no = max(max_char_no, len(dict_name))

        call_text = (
            comment_prefix
            + dict_name.ljust(max_char_no, " ")
            + " = "
            + call_text
            + "\n"
        )

        for socket in output_sockets:

            call_text += (
                comment_prefix
                + ("_" + "_".join(map(str, socket.get_id()))).ljust(max_char_no, " ")
                + " = "
                + f"{dict_name}[{repr(socket.output_name)}]"
                + "\n"
            )

    else:

        call_text = (
            comment_prefix
            + "_"
            + "_".join(
                map(
                    str,
                    next(iter(output_sockets)).get_id(),
                )
            )
            + " = "
            + call_text
        )

    ###
    comments_text = ""

    for prefix, obj in (
        ("### ", cluster),
        ("## ", node),
    ):

        try:
            refs = obj.text_block_refs

        except AttributeError:
            pass

        else:

            del obj.text_block_refs

            comments_text += "\n"

            for text_block in refs:

                lines = (
                    wrap(
                        text_block.data["text"],
                        width=COMMENT_WRAPPING_WIDTH,
                    )
                    if COMMENT_WRAPPING_WIDTH
                    else text_block.data["text"].splitlines()
                )

                # yield each line with a preceeding prefix
                # and succeeding '\n' (we didn't manage
                # to do this with solutions using
                # str.join/textwrap.indent, but we
                # achieved what we wanted)

                for line_text in lines:

                    comments_text += prefix + line_text + "\n"

                comments_text += "\n"

            if obj is cluster:
                comments_text += "\n"

    ###
    node_text = comments_text + call_text

    ##

    node_text += (
        ## if a node comment was joined, we join 02
        ## line separators, in order to isolate the
        ## call text further from the next line
        "\n" * 2
        if comments_text
        ## otherwise a simple '\n' is enough
        else "\n"
    )

    return node_text


def operator_node_to_call_text(
    node,
    cluster,
    nodes_to_visit,
    visited_nodes,
    node_clusters,
):

    substitution_map = {}

    for insocket in node.input_sockets:

        argument = param_name = insocket.parameter_name

        ### if parameter depends on the output of another
        ### node, we yield content from that
        ### node first and use its output as the
        ### argument

        if hasattr(insocket, "parent"):

            ### first of all retrieve references to the parent socket
            ### and parent node

            parent = insocket.parent
            parent_node = parent.node

            ### ensure the parent node is not a redirect node

            while True:

                if hasattr(parent_node, "proxy_socket") and hasattr(
                    parent_node.proxy_socket, "parent"
                ):

                    parent = parent_node.proxy_socket.parent

                    parent_node = parent.node

                    continue

                break

            ### now that we are sure we have a proper parent node,
            ### check whether it is in callable mode;
            ###
            ### it it is...

            if parent_node.data.get('mode', 'expanded_signature') == 'callable':

                ### if we have an operator node, the incoming data is a lambda
                ### representing the node
                if 'operation_id' in parent_node.data:
                    argument = '(' + parent_node.get_lambda_source() + ')'

                ### otherwise, it is a reference to the nodes callable

                else:

                    argument = parent_node.title_text

                    ## additionally, if the node is a snippet node,
                    ## store a reference in a special collection

                    if 'capsule_id' in parent_node.data:
                        SNIPPET_NODES.add(parent_node)

            ### otherwise...
            else:

                if parent_node not in visited_nodes:
                    raise WaitingParentException

                argument = "_" + "_".join(
                    map(
                        str,
                        parent.get_id(),
                    )
                )

        substitution_map[param_name] = argument

    ###

    ###

    output_socket = node.output_sockets[0]

    output_text = "_" + "_".join(
        map(
            str,
            output_socket.get_id(),
        )
    )

    substitution_map[output_socket.output_name] = output_text

    ###
    comments_text = ""

    for prefix, obj in (
        ("### ", cluster),
        ("## ", node),
    ):

        try:
            refs = obj.text_block_refs

        except AttributeError:
            pass

        else:

            del obj.text_block_refs

            comments_text += "\n"

            for text_block in refs:

                lines = (
                    wrap(
                        text_block.data["text"],
                        width=COMMENT_WRAPPING_WIDTH,
                    )
                    if COMMENT_WRAPPING_WIDTH
                    else text_block.data["text"].splitlines()
                )

                # yield each line with a preceeding prefix
                # and succeeding '\n' (we didn't manage
                # to do this with solutions using
                # str.join/textwrap.indent, but we
                # achieved what we wanted)

                for line_text in lines:

                    comments_text += prefix + line_text + "\n"

                comments_text += "\n"

            if obj is cluster:
                comments_text += "\n"

    ###
    node_text = node.substitution_callable(substitution_map)

    if node.data.get("commented_out", False):

        node_text = "\n".join("# " + line for line in node_text.splitlines())

    ###
    node_text = comments_text + node_text
    ###

    node_text += (
        ## if a node comment was joined, we join 02
        ## line separators, in order to isolate the
        ## call text further from the next line
        "\n" * 2
        if comments_text
        ## otherwise a simple '\n' is enough
        else "\n"
    )

    ###
    return node_text


def node_to_code_snippet(
    node,
    cluster,
    nodes_to_visit,
    visited_nodes,
    node_clusters,
):

    substitution_map = {}

    insocket_flmap = node.input_socket_live_flmap
    widget_flmap = node.widget_live_flmap
    keyword_lmap = node.subparam_keyword_entry_live_map

    for param_name in node.signature_obj.parameters.keys():

        argument = param_name

        ### check whether parameter name is of variable
        ### kind, storing which kind, if it is the case
        try:
            kind = node.var_kind_map[param_name]

        ### if it isn't of variable kind...

        except KeyError:

            ### we check whether the parameter depends on
            ### different incomming data

            insocket = insocket_flmap[param_name]

            ### if it depends on the output of another
            ### node, we yield content from that
            ### node first and use its output as the
            ### argument

            if hasattr(insocket, "parent"):

                ### first of all retrieve references to the parent socket
                ### and parent node

                parent = insocket.parent
                parent_node = parent.node

                ### ensure the parent node is not a redirect node

                while True:

                    if hasattr(parent_node, "proxy_socket") and hasattr(
                        parent_node.proxy_socket, "parent"
                    ):

                        parent = parent_node.proxy_socket.parent

                        parent_node = parent.node

                        continue

                    break

                ### now that we are sure we have a proper parent node,
                ### check whether it is in callable mode;
                ###
                ### it it is...

                if parent_node.data.get('mode', 'expanded_signature') == 'callable':

                    ### if we have an operator node, the incoming data is a lambda
                    ### representing the node
                    if 'operation_id' in parent_node.data:
                        argument = '(' + parent_node.get_lambda_source() + ')'

                    ### otherwise, it is a reference to the nodes callable

                    else:

                        argument = parent_node.title_text

                        ## additionally, if the node is a snippet node,
                        ## store a reference in a special collection

                        if 'capsule_id' in parent_node.data:
                            SNIPPET_NODES.add(parent_node)

                ### otherwise...

                else:

                    if parent_node not in visited_nodes:
                        raise WaitingParentException

                    argument = "_" + "_".join(
                        map(
                            str,
                            parent.get_id(),
                        )
                    )

            ### otherwise check whether there's an embedded
            ### widget with data for the parameter

            else:

                try:
                    widget = widget_flmap[param_name]

                ### if there's not, just pass
                except KeyError:
                    pass

                ### if it has...
                else:

                    ## otherwise we use repr() of the
                    ## it holds as the argument
                    argument = repr(widget.get())

            substitution_map[param_name] = argument

        ### if it is of variable kind...

        else:

            subparam_socket_map = insocket_flmap[param_name]

            argument = "(" if kind == "var_pos" else "{"

            for subparam_index in sorted(subparam_socket_map.keys()):

                insocket = subparam_socket_map[subparam_index]

                ### we check whether the subparameter
                ### depends on other sources of data

                if hasattr(insocket, "parent"):

                    ### first of all retrieve references to the parent socket
                    ### and parent node

                    parent = insocket.parent
                    parent_node = parent.node

                    ### ensure the parent node is not a redirect node

                    while True:

                        if hasattr(parent_node, "proxy_socket") and hasattr(
                            parent_node.proxy_socket, "parent"
                        ):

                            parent = parent_node.proxy_socket.parent

                            parent_node = parent.node

                            continue

                        break

                    ### now that we are sure we have a proper parent node,
                    ### check whether it is in callable mode;
                    ###
                    ### it it is...

                    if parent_node.data.get('mode', 'expanded_signature') == 'callable':

                        ### if we have an operator node, the incoming data is a lambda
                        ### representing the node
                        if 'operation_id' in parent_node.data:
                            subargument = '(' + parent_node.get_lambda_source() + ')'

                        ### otherwise, it is a reference to the nodes callable

                        else:

                            subargument = parent_node.title_text

                            ## additionally, if the node is a snippet node,
                            ## store a reference in a special collection

                            if 'capsule_id' in parent_node.data:
                                SNIPPET_NODES.add(parent_node)

                    ### otherwise...

                    else:

                        if parent_node not in visited_nodes:
                            raise WaitingParentException

                        subargument = "_" + "_".join(map(str, parent.get_id()))

                ## a widget

                else:

                    widget = widget_flmap[param_name][subparam_index]

                    subargument = repr(widget.get())

                if kind == "var_key":

                    if subparam_index in keyword_lmap:

                        keyword = keyword_lmap[subparam_index].get()

                        subargument = f"{repr(keyword)}: {subargument}"

                    else:
                        subargument = f"**{subargument}"

                else:

                    if subparam_index in (
                        node.data["subparam_unpacking_map"][param_name]
                    ):
                        subargument = f"*{subargument}"

                argument += subargument + ", "

            argument += ")" if kind == "var_pos" else "}"

            substitution_map[param_name] = argument

    ###

    ###
    output_sockets = node.output_socket_live_map.values()

    for socket in output_sockets:

        output_text = "_" + "_".join(
            map(
                str,
                socket.get_id(),
            )
        )

        substitution_map[socket.output_name] = output_text

    ###
    comments_text = ""

    for prefix, obj in (
        ("### ", cluster),
        ("## ", node),
    ):

        try:
            refs = obj.text_block_refs

        except AttributeError:
            pass

        else:

            del obj.text_block_refs

            comments_text += "\n"

            for text_block in refs:

                lines = (
                    wrap(
                        text_block.data["text"],
                        width=COMMENT_WRAPPING_WIDTH,
                    )
                    if COMMENT_WRAPPING_WIDTH
                    else text_block.data["text"].splitlines()
                )

                # join each line with a preceeding prefix
                # and succeeding '\n' (we didn't manage
                # to do this with solutions using
                # str.join/textwrap.indent, but we
                # achieved what we wanted)

                for line_text in lines:

                    comments_text += prefix + line_text + "\n"

                comments_text += "\n"

            if obj is cluster:
                comments_text += "\n"

    ###

    node_text = node.substitution_callable(substitution_map)

    if node.data.get("commented_out", False):

        node_text = "\n".join("# " + line for line in node_text.splitlines())

    node_text = comments_text + node_text

    node_text += (
        ## if a node comment was yielded, we join 02
        ## line separators, in order to isolate the
        ## call text further from the next line
        "\n" * 2
        if comments_text
        ## otherwise a simple '\n' is enough
        else "\n"
    )

    return node_text


def data_node_to_variable_assignment(
    node,
    cluster,
    nodes_to_visit,
    visited_nodes,
    node_clusters,
):

    output_socket = node.output_socket
    widget = node.widget

    var_def_text = (
        "_"
        + "_".join(
            map(
                str,
                output_socket.get_id(),
            )
        )
        + " = "
        + repr(widget.get())
    )

    ###
    comments_text = ""

    for prefix, obj in (
        ("### ", cluster),
        ("## ", node),
    ):

        try:
            refs = obj.text_block_refs

        except AttributeError:
            pass

        else:

            del obj.text_block_refs

            comments_text += "\n"

            for text_block in refs:

                lines = (
                    wrap(
                        text_block.data["text"],
                        width=COMMENT_WRAPPING_WIDTH,
                    )
                    if COMMENT_WRAPPING_WIDTH
                    else text_block.data["text"].splitlines()
                )

                # yield each line with a preceeding prefix
                # and succeeding '\n' (we didn't manage
                # to do this with solutions using
                # str.join/textwrap.indent, but we
                # achieved what we wanted)

                for line_text in lines:

                    comments_text += prefix + line_text + "\n"

                comments_text += "\n"

            if obj is cluster:
                comments_text += "\n"

    ###

    if node.data.get("commented_out", False):
        var_def_text = "# " + var_def_text

    ###

    node_text = comments_text + var_def_text
    ###

    node_text += (
        ## if a node comment was yielded, we join 02
        ## line separators, in order to isolate the
        ## definition text further from the next line
        "\n" * 2
        if comments_text
        ## otherwise a simple '\n' is enough
        else "\n"
    )

    return node_text


def gather_snippets_source():

    node_map = {
        node.data['capsule_id']: node
        for node in SNIPPET_NODES
    }

    source = '\n\n'.join(
        node_map[id_str].get_source_to_export()
        for id_str in sorted(node_map)
    )

    return source

def gather_genviewer_source():

    node_map = {
        node.data['genviewer_id']: node
        for node in GENVIEWER_NODES
    }

    source = '\n\n'.join(
        node_map[id_str].get_source_to_export()
        for id_str in sorted(node_map)
    )

    return source
