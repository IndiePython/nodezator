"""Facility with operations for system testing case 0000."""

### standard library imports

from zipfile import ZipFile

from ast import literal_eval


### local imports

from ...config import APP_REFS, SYSTEM_TESTING_DATA_DIR

from ...graphman.textblock.main import TextBlock
from ...graphman.proxynode.main import ProxyNode
from ...graphman.operatornode.main import OperatorNode
from ...graphman.builtinnode.main import BuiltinNode
from ...graphman.stlibnode.main import StandardLibNode
from ...graphman.genviewernode.main import GeneralViewerNode
from ...graphman.thirdlibnode.main import ThirdLibNode
from ...graphman.capsulenode.main import CapsuleNode



FRAME_ASSERTION_MAP = {}


def perform_setup(data):
    """Load and reference input data."""

    with ZipFile(
        str(SYSTEM_TESTING_DATA_DIR / 'test_cases' / 'stc0000.zip'),
        mode='r',
    ) as archive:

        with archive.open('input_data.pyl', mode='r') as input_data_file:

            data.input_data = (
                literal_eval(input_data_file.read().decode(encoding='utf-8'))
            )

def ensure_collections_are_empty(append_assertion_data):
    """Ensure collections have no items.

    Parameters
    ==========
    append_assertion_data (callable)
        Used to store the results of assertions.
    """
    ### confirm no text box exists

    ## grab the text blocks
    text_blocks = APP_REFS.gm.text_blocks

    ## 01 item in APP_REFS.gm.text_blocks

    append_assertion_data(

        (
            "There must be no object in APP_REFS.gm.text_blocks",
            len(text_blocks) == 0,
        )

    )

    ### confirm no nodes exist

    ## grab the nodes iterable
    nodes = APP_REFS.gm.nodes

    ## the "nodes" iterable must contain no items

    append_assertion_data(

        (
            "There must be no items in APP_REFS.gm.nodes",
            len(nodes) == 0,
        )

    )

FRAME_ASSERTION_MAP[51] = ensure_collections_are_empty


def perform_final_assertions(append_assertion_data):
    """Confirm instantiation of default objects.

    Parameters
    ==========
    append_assertion_data (dict)
        Used to store test results.
    """
    ### confirm a single text box exists

    ## grab the text blocks
    text_blocks = APP_REFS.gm.text_blocks

    ## exactly one object in APP_REFS.gm.text_blocks

    append_assertion_data(

        (
            "There's only one object in APP_REFS.gm.text_blocks",
            len(text_blocks) == 1,
        )

    )


    ## that object is a TextBlock instance

    append_assertion_data(
        (
            "Single object in APP_REFS.gm.text_blocks is TextBlock instance",
            isinstance(text_blocks[0], TextBlock),
        )
    )


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

    append_assertion_data(
        (
            "There must be exactly 8 items in the nodes iterable",
            len(nodes) == 8,
        )
    )

    ## there must be only one node of each kind

    for kind_name, check_functions in (

        (

            "redirect node",

            (
                lambda node: isinstance(node, ProxyNode),
                lambda node: not hasattr(node, 'widget'),
            ),

        ),

        (

            "data node",

            (
                lambda node: isinstance(node, ProxyNode),
                lambda node: hasattr(node, 'widget'),
                lambda node: not hasattr(node.proxy_socket, 'parent'),
            ),

        ),

        (

            "operation node",

            (
                lambda node: isinstance(node, OperatorNode),
            ),

        ),

        (

            "built-in node",

            (
                lambda node: isinstance(node, BuiltinNode),
            ),

        ),

        (

            "standard library node",

            (
                lambda node: isinstance(node, StandardLibNode),
            ),

        ),

        (

            "general viewer node",

            (
                lambda node: isinstance(node, GeneralViewerNode),
            ),

        ),

        (

            "pygame-ce node",

            (
                lambda node: isinstance(node, ThirdLibNode),
            ),

        ),

        (

            "snippet node",

            (
                lambda node: isinstance(node, CapsuleNode),
            ),

        ),

    ):

        append_assertion_data(

            (

                f"There must be only one {kind_name} among the existing ones",

                sum(

                    1
                    for node in nodes
                    if all(check_func(node) for check_func in check_functions)

                ) == 1,

            )

        )
