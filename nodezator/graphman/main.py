"""Facility with class for graph management."""

### third-party import
from pygame import Rect


### local imports

from ..config import APP_REFS

from ..appinfo import (
    NODES_KEY,
    PARENT_SOCKETS_KEY,
    TEXT_BLOCKS_KEY,
)

from ..logman.main import get_new_logger

from ..ourstdlibs.meta import initialize_bases

from ..classes2d.single import Object2D

from ..classes2d.collections import (
    Iterable2D,
    List2D,
)

from .exception import (
    NodeScriptsError,
    MissingNodeScriptsError,
)

## function
from .scriptloading import load_scripts

## classes for composition

from .callablenode.main import CallableNode
from .builtinnode.main import BuiltinNode
from .stlibnode.main import StandardLibNode
from .capsulenode.main import CapsuleNode

from .operatornode.main import OperatorNode
from .proxynode.main import ProxyNode

from .textblock.main import TextBlock

## class extensions

from .editlogic import DataEdition

from .socketparenthood.main import SocketParenthood

from .execution import Execution

## function for memory freeing
from .callablenode.surfs import free_up_memory

## function for representing graph as python code
from .pythonrepr import python_repr


### create logger for module
logger = get_new_logger(__name__)


class GraphManager(
    DataEdition,
    SocketParenthood,
    Execution,
):
    """Manages native file json data presentation/edition.

    The data is retrieved from a json file, which is
    a json formatted text file complying to the native
    format.
    """

    python_repr = python_repr

    def __init__(self):
        """Reference itself in the node class."""
        ### reference itself on APP_REFS
        APP_REFS.gm = self

        ### create rect to mark origin of 2d space
        self.origin_rect = Rect(0, 0, 100, 100)

        ### initialize each base class which has its own
        ### init method
        initialize_bases(self)

    def prepare_for_new_session(self):
        """Create objects to help manage data."""
        ### reference data from APP_REFS locally
        data = APP_REFS.data

        ### retrieve the value in the NODES_KEY key
        ### from the native file data and store in an
        ### attribute
        self.nodes_data = data.setdefault(NODES_KEY, {})

        ### load scripts to use callables provided by
        ### them as specifications for nodes
        load_scripts(data["node_packs"], data["installed_node_packs"])

        ### instantiate nodes
        self.instantiate_nodes()

        ### retrieve the value in the PARENT_SOCKETS_KEY
        ### key from the native data and pass it to related
        ### method to perform needed setups

        parent_sockets_data = data.setdefault(PARENT_SOCKETS_KEY, [])

        self.setup_parent_sockets_data(parent_sockets_data)

        ### retrieve the value in the TEXT_BLOCKS_KEY key
        ### from the file data and store in an attribute

        self.text_blocks_data = data.setdefault(TEXT_BLOCKS_KEY, [])

        ### instantiate text blocks
        self.instantiate_text_blocks()

    def instantiate_nodes(self):
        """Instantiate node widgets.

        This is done so they can be used to execute the node
        layout.
        """
        ### create map to store node objects
        node_map = self.node_map = {}

        ### reference the callable map locally
        node_def_map = APP_REFS.node_def_map

        ### also create a list to hold missing node script
        ### ids, in case there's any
        missing_ids = []

        ### instantiate and store nodes in the map

        for node_data in self.nodes_data.values():

            if "script_id" in node_data:

                script_id = node_data["script_id"]

                ## try retrieving the node defining object
                ## from the corresponding map

                try:
                    node_def_obj = node_def_map[script_id]

                ## if a KeyError is raised, store the missing
                ## id and skip the processing of this item
                ## using the 'continue' statement; a custom
                ## error will be raised after exiting the
                ## loop to report the missing ids found

                except KeyError:

                    missing_ids.append(script_id)
                    continue

                ## if otherwise you retrieve the node
                ## defining object successfully,
                ## instantiate and store the node

                else:
                    node_map[node_data["id"]] = CallableNode(
                        node_def_obj,
                        node_data,
                    )

            elif "operation_id" in node_data:

                node_map[node_data["id"]] = OperatorNode(node_data)

            elif "builtin_id" in node_data:
                node_map[node_data["id"]] = BuiltinNode(node_data)

            elif "stlib_id" in node_data:
                node_map[node_data["id"]] = StandardLibNode(node_data)

            elif "capsule_id" in node_data:
                node_map[node_data["id"]] = CapsuleNode(node_data)

            else:
                node_map[node_data["id"]] = ProxyNode(node_data)

        ### TODO
        ### this should be dealt with in the GUI to help
        ### the user; we would probably present a custom
        ### message listing the missing scripts, telling
        ### the user how to solve the problem and
        ### probably offering the option to return to
        ### 'no file' state, etc.
        ###
        ### edit: at the present time, we automatically
        ### return to the 'no file' state

        ### if there are missing ids, report them by
        ### raising a custom error

        if missing_ids:
            raise MissingNodeScriptsError(missing_ids)

        ### create a special object from the __iter__
        ### method of the node map values() view;
        ###
        ### such special iterable provides extra control
        ### over the objects in the view; it also provides
        ### extra functionality, including blitting
        ### operations;

        self.nodes = Iterable2D(node_map.values().__iter__)

    def instantiate_text_blocks(self):
        """Instantiate text blocks."""
        ### create list to storing text block objects

        self.text_blocks = List2D(
            TextBlock(text_data) for text_data in self.text_blocks_data
        )

    def draw(self):
        """Draw node layout elements."""
        ### lines
        self.draw_lines()

        ### nodes
        self.nodes.call_draw_on_screen()

        ### text blocks
        self.text_blocks.call_draw_on_screen()

    def free_up_memory(self):
        """Clear accumulated data that won't be reused.

        Used just before loading a new file, so data
        accumulated from the edition of the previous file
        (in case there was one) isn't kept around now that
        another file is being loaded.

        The previous file edited might be the one being
        loaded (that is, the file is reloaded). However,
        even if it is the case, this measures should still
        save memory, since data/objects present in
        the past session may not be needed anymore in
        the new session.
        """
        ### free memory from node body surfaces
        free_up_memory()

        ### clear collections containing native file data,
        ### node instances and text block instances

        for attr_name in ("nodes_data", "text_blocks_data", "node_map", "text_blocks"):

            try:
                obj = getattr(self, attr_name)
            except AttributeError:
                pass
            else:
                obj.clear()
