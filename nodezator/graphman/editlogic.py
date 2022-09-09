"""Facility for node layout edition logic."""

### standard library import
from functools import partialmethod


### local imports

from ..ourstdlibs.behaviour import remove_by_identity


## classes for composition

from .callablenode.main import CallableNode
from .proxynode.main import ProxyNode

from .textblock.main import TextBlock


class DataEdition:
    """Contains methods for node layout edition."""

    def create_node(self, node_class, *args, **kwargs):
        """Instantiate and insert node."""
        ### instantiate
        node = node_class(*args, **kwargs)

        ### insert node into the node map using its id
        self.node_map[node.id] = node

        ### insert the node data into the nodes_data map
        ### using its id
        self.nodes_data[node.id] = node.data

    create_callable_node = partialmethod(create_node, CallableNode)

    create_proxy_node = partialmethod(create_node, ProxyNode)

    def insert_node(self, node):
        """Insert node into node map and node's data."""
        ### XXX to be implemented along with the undo/redo
        ### feature

    def remove_node(self, node):
        """Remove node instance from node layout.

        node (
          instance
          of graphman.callablenode.main.CallableNode
          or graphman.proxynode.main.ProxyNode
          or graphman.proxynode.main.ProxyNode
        )
        """
        ### sever node connections
        self.sever_all_connections(node)

        ### remove node from the node map and nodes_data
        ### map using its id
        self.node_map.pop(node.id)

        ### remove the node data from the nodes_data map
        ### using its id
        self.nodes_data.pop(node.id)

    def create_text_block(
        self,
        text_block_data,
        text_block_absolute_midtop,
    ):
        """Instantiate, build visuals and insert new node.

        text_block_data (dict)
            instance data for text block.
        text_block_absolute_midtop (2-tuple of integers)
            represents the midtop position of the node on
            the screen.
        """
        ### instantiate text block

        text_block = TextBlock(text_block_data, text_block_absolute_midtop)

        ### insert it in the data
        self.insert_text_block(text_block)

    def insert_text_block(self, text_block):
        """Insert text block into node layout.

        text_block (graphman.textblock.main.TextBlock obj)
        """
        ### append text block into the text blocks' list
        self.text_blocks.append(text_block)

        ### append the text block data into the
        ### text blocks data list
        self.text_blocks_data.append(text_block.data)

    def remove_text_block(self, text_block):
        """Remove text block instance from node layout.

        text_block (graphman.textblock.main.TextBlock obj)
        """
        ### remove text block from the text block list
        remove_by_identity(text_block, self.text_blocks)

        ### remove the text block data from the text
        ### block data list

        remove_by_identity(text_block.data, self.text_blocks_data)
