"""Facility with operations for system testing case 0000."""

### local imports

from .....config import APP_REFS

from .....graphman.textblock import TextBlock
from .....graphman.proxynode.main import ProxyNode
from .....graphman.builtinnode.main import BuiltinNode
from .....graphman.stlibnode.main import StandardLibNode
from .....graphman.thirdlibnode.main import ThirdLibNode
from .....graphman.capsulenode.main import CapsuleNode
from .....graphman.genviewernode.main import GeneralViewerNode

from .....graphman.operatornode.main import OperatorNode



def perform_assertions(result_map):
    """Confirm instantiation of default objects.

    Parameters
    ==========
    result_map (dict)
        Used to store test results.
    """
    ### confirm a single text box exists

    ## grab the text blocks
    text_blocks = APP_REFS.gm.text_blocks

    ## exactly one object in APP_REFS.gm.text_blocks

    result_map[
        "There's only one object in APP_REFS.gm.text_blocks"
    ] = len(text_blocks) == 1


    ## that object is a TextBlock instance

    result_map[
        "Single object in APP_REFS.gm.text_blocks is TextBlock instance"
    ] = isinstance(text_blocks[0], TextBlock)


    ### confirm these kind of nodes exist, one of each kind only
    ###
    ### - a redirect node
    ### - a data node
    ### - an operation node
    ### - a built-in node
    ### - a standard library node
    ### - a general viewer node
    ### - a pygame-ce node
    ### - a snippet node

    ## grab the nodes iterable
    nodes = APP_REFS.gm.nodes

    ## the "nodes" iterable must contain exactly 8 nodes

    result_map[
        "There must be exactly 8 items in the nodes iterable"
    ] = len(nodes) == 8

    ## there must be only one redirect node among the existing ones

    result_map[
        "There must be only one redirect node among the existing ones"
    ] = sum(

        1
        for node in nodes
        if (
            isinstance(node, ProxyNode)
            and not hasattr(node, 'widget')
        )

    ) == 1

    ## there must be only one data node among the existing ones

    result_map[
        "There must be only one data node among the existing ones"
    ] = sum(

        1
        for node in nodes
        if (
            isinstance(node, ProxyNode)
            and hasattr(node, 'widget')
            and not hasattr(node.proxy_socket, 'parent')
        )

    ) == 1

    ###
    ...
