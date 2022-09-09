"""Node management utilities"""


### function to perform call with custom syntaxes
### according to their parameters (or lack thereof)

# obtain a string formatter callable which simulates
# a call
format_as_call = "callable_obj({})".format

## main function


def lay_arguments_and_execute(callable_obj, argument_map, signature_obj):
    """Lay arguments, execute callable and return result.

    Works by building a string representing a call to the
    received callable with all its arguments laid out
    properly according to the kind of the corresponding
    parameters.

    Such string is then, executed with the builtin function
    eval() and its return value is returned from this
    function.

    Such kinds of parameters refer to whether a parameter
    is positional-only, keyword-only, both positional
    and keyword compatible, etc., for instance. They are
    listed in the following attributes of the standard
    library inspect module:

    '_POSITIONAL_ONLY',
    '_POSITIONAL_OR_KEYWORD',
    '_KEYWORD_ONLY',
    '_VAR_POSITIONAL'
    '_VAR_KEYWORD'.

    If a parameter is of kind inspect._KEYWORD_ONLY, for
    instance, the string will be built so that its
    argument is passed as a keyword in the call.

    Note that instead of obtaining the signature from
    the callable itself we chose to receive it as an
    argument. This is so because we speed up the function
    by eliminating the step of obtaining the signature and
    this also enable us to use a different signature for
    the given callable, as long as it is compatible with
    the callable.


    Parameters
    ==========

    callable_obj (callable)
        callable to be executed.

    argument_map  (dict)
        has values for the parameters, to use in the call.

    signature_obj (obj returned from inspect.signature())
        object returned from passing the callable object
        to the inspect.signature() function; it is used
        to obtain information about the parameters (or lack
        thereof) of the callable.


    Doctests
    ========

    >>> from inspect import signature
    >>> from pprint  import pprint

    >>> def hello(a, *b, c, **d):
    ...     return a, b, c, d
    >>> sig = signature(hello)

    >>> kwargs = {
    ...   'a': 11,
    ...   'b': ['hello', 'world'],
    ...   'c': 'the letter c',
    ...   'd': {
    ...     'food': 'pie'
    ...   }
    ... }
    >>> values = lay_arguments_and_execute(
    ... hello, kwargs, sig)
    >>> for arg_name, arg_value in zip("abcd", values):
    ...     print(arg_name, ":", arg_value)
    a : 11
    b : ('hello', 'world')
    c : the letter c
    d : {'food': 'pie'}

    >>> # if we didn't use the lay_arguments_and_execute
    >>> # function, that is, just passed the arguments
    >>> # like this: hello(**kwargs), it wouldn't assign
    >>> # the values properly. For instance, the 'b'
    >>> # argument would be empty, its value would be
    >>> # assigned to the 'd' parameter instead, along with
    >>> # the original value of 'd':

    >>> values = hello(**kwargs)
    >>> values[1] # value of 'b'
    ()
    >>> d = values[3] # value of 'd'
    >>> d == {'b': ['hello', 'world'], 'd': {'food': 'pie'}}
    True

    >>> # also, depending on the signature of the function
    >>> # using 'function(**kwargs)' would even raise an
    >>> # error if the function had any parameter of
    >>> # inspect._POSITIONAL_ONLY kind:

    >>> pow_kwargs = {'x': 4, 'y': 2}
    >>> pow(**kwargs)
    Traceback (most recent call last):
    ...
    TypeError: pow() takes no keyword arguments

    >>> # however, we can overcome such problem by using
    >>> # our lay_arguments_and_execute function:

    >>> pow_sig = signature(pow)
    >>> lay_arguments_and_execute(pow, pow_kwargs, pow_sig)
    16

    >>> # it also works when the function has no parameters
    >>> # at all
    >>> def no_param(): return 'this'
    >>> no_param_sig = signature(no_param)
    >>> lay_arguments_and_execute(no_param, {}, no_param_sig)
    'this'

    """
    ### start a string to be built representing the
    ### laid out arguments
    layout_string = ""

    ### iterate over each parameter filling the layout
    ### string with more content representing each argument
    ### being properly laid out in it according to the
    ### kind of its corresponding parameter

    for param_name, param_obj in signature_obj.parameters.items():

        ## if the argument for the parameter wasn't provided,
        ## that is, isn't present on the argument map, skip
        ## this iteration by using the 'continue' statement
        if param_name not in argument_map:
            continue

        ## create a base text from the parameter name,
        ## representing the retrieval of the value for
        ## the parameter from the argument map
        param_value_retrieval = f"argument_map['{param_name}'],"

        ## alter the value retrieval text according to the
        ## kind of the parameter

        # parameters before '*'

        if param_obj.kind in (
            param_obj.POSITIONAL_ONLY,
            param_obj.POSITIONAL_OR_KEYWORD,
        ):
            layout_string += param_value_retrieval

        # a parameter with a single star: *args

        elif param_obj.kind == param_obj.VAR_POSITIONAL:
            layout_string += "*" + param_value_retrieval

        # parameters after either bare '*' or '*args'

        elif param_obj.kind == param_obj.KEYWORD_ONLY:

            layout_string += param_name + "=" + param_value_retrieval

        # a parameter with double stars: **kwargs

        elif param_obj.kind == param_obj.VAR_KEYWORD:
            layout_string += "**" + param_value_retrieval

    ### now format the layout string as a proper call
    ### and, since the string is now complete and
    ### represents a valid call using variables present
    ### in this function's name space, perform the call
    ### using eval(), returning the call's return value
    return eval(f"callable_obj({layout_string})")


### generator function to yield nodes in a subgraph and
### all subgraphs in the file


def yield_subgraph_nodes(node, visited_nodes=None):
    """Yield all nodes in subgraph.

    Works by recursively yielding nodes connected with
    the given one until all connected nodes are yielded.

    Parameters
    ==========
    node (graphman.callablenode.CallableNode instance)
        a node from the subgraph; start from it, we yield
        all nodes in the subgraph.
    visited_nodes (built-in class 'set' instance)
        set used to keep track of nodes already visited,
        so we avoid revisiting them.
    """
    ### create a "visited nodes" set if it doesn't exist
    ### already
    if visited_nodes is None:
        visited_nodes = set()

    ### since we are visiting the given node, mark it
    ### as visited by adding it to the corresponding set
    visited_nodes.add(node)

    ### let's start the visit by yielding the node
    yield node

    ### now let's visit each upstream node recursively,
    ### that is, the ones we didn't visit yet

    for input_socket in node.input_sockets:

        ## try retrieving the value of the socket's
        ## 'parent' attribute, which, if exists,
        ## should contain a reference to an output
        ## socket which is the parent of the socket
        ## (the output socket is from another node)
        try:
            parent_output_socket = input_socket.parent

        ## if such attribute doesn't exits, just pass
        except AttributeError:
            pass

        ## otherwise, reference the node of such
        ## parent socket and visit it if not visited
        ## already, by passing it to this same
        ## function and yielding from it
        ##
        ## you must also pass along the set of visited
        ## nodes, so that the function knows whether
        ## a node has already been visited or not

        else:

            parent_node = parent_output_socket.node

            if parent_node not in visited_nodes:

                yield from yield_subgraph_nodes(parent_node, visited_nodes)

    ### now let's visit each downstream node recursively,
    ### that is, the ones we didn't visit yet

    for output_socket in node.output_sockets:

        ## try retrieving the value of the socket's
        ## 'children' attribute, which, if exists, should
        ## contain a reference to a list which contains
        ## references to input sockets considered
        ## children of this socket (the input sockets are
        ## from other nodes)
        try:
            children = output_socket.children

        ## if such attribute doesn't exits, just pass
        except AttributeError:
            pass

        ## otherwise, iterate over each input socket
        ## reference, referencing its node and visiting
        ## such node, if not visited already, by passing
        ## it to this same function and yielding from it
        ##
        ## you must also pass along the set of visited
        ## nodes, so that the function knows whether a
        ## node has already been visited or not

        else:

            for child_input_socket in children:

                child_node = child_input_socket.node

                if child_node not in visited_nodes:

                    yield from yield_subgraph_nodes(
                        child_node,
                        visited_nodes,
                    )


def yield_subgraphs(nodes):
    """Yield node lists representing subgraphs of given nodes.

    Subgraphs are not yielded twice, so if a node
    in the given list was already referenced in another
    previously yielded subgraph, it is ignored (we actually
    remove it from the set of nodes to check).

    Parameters
    ==========

    nodes (iterable w/
    graphman.callablenode.CallableNode instances)
        nodes whose subgraphs will be yielded, one by one,
        in no particular order, since we use this iterable
        to obtain a set with which we work;

        by subgraph we mean a list containing all the nodes
        forming that particular subgraph.
    """
    ### obtain a set from the given nodes, considering them
    ### as nodes to check
    nodes_to_check = set(nodes)

    ### execute this loop while there's still nodes to
    ### be checked

    while nodes_to_check:

        ## pop and reference a node from the set
        node = nodes_to_check.pop()

        ## list all the nodes from that node's subgraph,
        ## including that node itself
        subgraph = list(yield_subgraph_nodes(node))

        ## yield such list
        yield subgraph

        ## now remove from our set all the nodes from
        ## the subgraph which may be present there
        ##
        ## this way we prevent the same subgraph to be
        ## yielded twice, as no node in this subgraph
        ## will be checked again, since we are removing
        ## them from the set of nodes to be checked
        nodes_to_check.difference_update(subgraph)
