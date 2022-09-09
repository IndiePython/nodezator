"""Facility for object insertion/removal handling."""

### standard-library imports

from copy import deepcopy

from itertools import chain, count


### local imports

from ..config import APP_REFS

from ..dialog import create_and_show_dialog

from ..appinfo import NODES_KEY

from ..translation import TRANSLATION_HOLDER as t

from ..logman.main import get_new_logger

from ..our3rdlibs.userlogger import USER_LOGGER

from ..our3rdlibs.behaviour import (
    indicate_unsaved,
    saved_or_unsaved_state_kept,
)

from ..graphman.callablenode.main import CallableNode
from ..graphman.operatornode.main import OperatorNode
from ..graphman.builtinnode.main import BuiltinNode
from ..graphman.stlibnode.main import StandardLibNode
from ..graphman.capsulenode.main import CapsuleNode
from ..graphman.proxynode.main import ProxyNode
from ..graphman.textblock.main import TextBlock

from .widgetpicker.main import pick_widget


### create logger for module
logger = get_new_logger(__name__)


class ObjectInsertionRemoval:
    """Contains object insertion and removal methods.

    The objects are:
      - graphman.proxynode.main.ProxyNode instances; or
      - graphman.callablenode.main.CallableNode instances; or
      - graphman.textblock.main.TextBlock instances;
    """

    def __init__(self):
        """Set specific flag for movement from duplication.

        That is, a flag to indicate when the state of
        moving the objects was triggered by a duplication
        operation.

        When this flag is on, cancelling the moving
        operation will cause the selected objects to
        be deleted.
        """
        ### set flag to specify when the moving operation
        ### was triggered by a duplication operation
        self.moving_from_duplication = False

    def pick_widget_for_proxy_node(self):

        ### retrieve widget kwargs
        widget_data = pick_widget()

        ### if widget data is None, cancel the operation
        ### by returning earlier
        if widget_data is None:
            return

        ### otherwise insert new raw data node by passing
        ### widget data as node hint

        self.insert_node(
            node_hint=widget_data,
        )

    def insert_node(
        self,
        node_hint,
        absolute_midtop=None,
        commented_out_state=False,
    ):
        """Trigger node insertion on graph manager.

        Parameters
        ==========

        node_hint

            dict instance
            or graphman.callablenode.main.CallableNode
            or graphman.proxynode.main.ProxyNode
            or None


            if it is a dict, it can be a callable node or
            a proxy node; if it is None we instantiate
            a proxy node without additional data

            if it is a node instance, then naturally no
            instantiation is needed, we just reinsert it
            in the node layout.

        absolute_midtop (2-tuple or None)
            if not None, it is used as the relative midtop
            position of the node being inserted. This
            parameter is relevant only if the node hint
            isn't a node instance.

        commented_out_state (bool)
            the "commented out" state of the node. This
            parameter is relevant only if the node hint
            isn't a node instance.
        """
        ### assess which kind of argument was received in
        ### the node_hint parameter

        ## if we have a node instance, we just insert it

        if isinstance(
            node_hint,
            (CallableNode, OperatorNode, ProxyNode),
        ):

            APP_REFS.gm.insert_node(node=node_hint)

        ### otherwise...

        else:

            ## get new id for the node
            new_id = get_new_node_id()

            ## get absolute midtop coordinates
            ## according to whether it was provided
            ## via argument or not

            absolute_midtop = (
                absolute_midtop if absolute_midtop is not None else self.popup_spawn_pos
            )

            ## the relative midtop is obtained by
            ## taking into account the effect of the
            ## scrolling

            relative_midtop = tuple(absolute_midtop - self.scrolling_amount)

            ## if we have a string, we create an operator
            ## node

            if isinstance(node_hint, str):

                ## gather data in a dict which will be fed
                ## to the node constructor

                node_data = {
                    "id": new_id,
                    "midtop": relative_midtop,
                    "commented_out": commented_out_state,
                }

                for cls, key in (
                    (OperatorNode, "operation_id"),
                    (BuiltinNode, "builtin_id"),
                    (StandardLibNode, "stlib_id"),
                    (CapsuleNode, "capsule_id"),
                ):

                    if node_hint in cls.available_ids:

                        node_data[key] = node_hint

                        ## create the node, adding its
                        ## data to the file

                        APP_REFS.gm.create_node(
                            cls,
                            data=node_data,
                            midtop=absolute_midtop,
                        )

            ## if we have a dict...

            elif isinstance(node_hint, dict):

                if "signature_callable" in node_hint:

                    ## gather data in a dict which will be
                    ## fed to the node constructor

                    node_data = {
                        "id": new_id,
                        "midtop": relative_midtop,
                        "commented_out": commented_out_state,
                    }

                    ## try creating the node, adding its data to
                    ## the file

                    try:
                        APP_REFS.gm.create_callable_node(
                            node_defining_object=(node_hint),
                            data=node_data,
                            midtop=(absolute_midtop),
                        )

                    except Exception as err:

                        ## log traceback in regular
                        ## log and and user log

                        msg = (
                            "An unexpected error ocurred"
                            " while trying to instantiate"
                            " the node."
                        )

                        logger.exception(msg)
                        USER_LOGGER.exception(msg)

                        ## notify user via dialog

                        create_and_show_dialog(
                            (
                                "An error ocurred while"
                                " trying to instantiate"
                                " the node. Check the user"
                                " log for details"
                                " (click <Ctrl+Shift+J> after"
                                " leaving this dialog)."
                            ),
                            level_name="error",
                        )

                        ## leave the method
                        return

                else:

                    widget_data = deepcopy(node_hint)

                    ## gather data in a dict which will be
                    ## fed to the node constructor

                    node_data = {
                        "id": new_id,
                        "midtop": relative_midtop,
                        "commented_out": commented_out_state,
                        "widget_data": widget_data,
                    }

                    ## create the node, adding its data to the
                    ## file

                    APP_REFS.gm.create_proxy_node(
                        data=node_data,
                        midtop=absolute_midtop,
                    )

            ## if node_hint argument is none, we also
            ## create a proxy node
            elif node_hint is None:

                ## gather data in a dict which will be fed to
                ## the node constructor

                node_data = {
                    "id": new_id,
                    "midtop": relative_midtop,
                    "commented_out": commented_out_state,
                }

                ## create the node, adding its data to the
                ## file

                APP_REFS.gm.create_proxy_node(
                    data=node_data,
                    midtop=absolute_midtop,
                )

        ### indicate the data was changed
        indicate_unsaved()

    def insert_text_block(
        self,
        text_block_hint=(t.editing.objinsert.new_text_block),
        absolute_midtop=None,
    ):
        """Trigger text block insertion on graph manager.

        text_block_hint (
        graphman.textblock.main.TextBlock instance or string)

            if it is a string then we just insert a new
            text block using the given string and its text.

            if it is a TextBlock instance, then naturally
            no instantiation is needed, we just reinsert it.

        absolute_midtop (2-tuple or None)
            if not None, it is used as the relative midtop
            position of the text block being inserted.
        """
        ### assess whether the text_block_hint argument is
        ### a string or not, storing the result
        text_block_hint_is_str = isinstance(text_block_hint, str)

        ### if text_block_hint argument is a string
        ### gather spatial data and pass it to the
        ### graph manager so it can instantiate a new
        ### text block

        if text_block_hint_is_str:

            ## get absolute midtop coordinates according to
            ## whether it was provided via argument or not

            absolute_midtop = (
                absolute_midtop if absolute_midtop is not None else self.popup_spawn_pos
            )

            ## the relative midtop is obtained by taking
            ## into account the effect of the scrolling
            relative_midtop = tuple(absolute_midtop - self.scrolling_amount)

            ## gather id and spatial data in a dict which
            ## will be fed to the text block constructor

            text = text_block_hint

            text_block_data = {"text": text, "midtop": relative_midtop}

            ## create text block, adding its data file to
            ## the file

            APP_REFS.gm.create_text_block(
                text_block_data=text_block_data,
                text_block_absolute_midtop=absolute_midtop,
            )

        ### otherwise, we know it is a text block instance,
        ### so we instead just insert it
        else:
            APP_REFS.gm.insert_text_block(text_block=text_block_hint)

        ### indicate the data was changed
        indicate_unsaved()

    def duplicate_selected(self):
        """Duplicate selected objects."""
        ### return earlier if there's no selected objects,
        ### since the duplication must be performed on them
        if not self.selected_objs:
            return

        ### perform duplication and related admin tasks

        ## copy references to existing objects before the
        ## duplication

        # nodes
        pre_existing_nodes = list(APP_REFS.gm.nodes)

        # text blocks
        pre_existing_text_blocks = list(APP_REFS.gm.text_blocks)

        ## for each selected obj, create another of the
        ## same kind instantiated at almost the same spot,
        ## with just a bit of offset to make it more
        ## evident there's a new object on top of the
        ## original one

        with saved_or_unsaved_state_kept():

            for obj in self.selected_objs:

                if type(obj) is CallableNode:

                    self.insert_node(
                        node_hint=obj.node_defining_object,
                        absolute_midtop=(obj.rectsman.move(20, -20).midtop),
                        commented_out_state=(obj.data.get("commented_out", False)),
                    )

                elif isinstance(obj, ProxyNode):

                    self.insert_node(
                        node_hint=(obj.data.get("widget_data", None)),
                        absolute_midtop=(obj.rectsman.move(20, -20).midtop),
                        commented_out_state=(obj.data.get("commented_out", False)),
                    )

                elif isinstance(obj, TextBlock):

                    self.insert_text_block(
                        text_block_hint=obj.data["text"],
                        absolute_midtop=(obj.rect.move(20, -20).midtop),
                    )

                else:

                    for cls, key in (
                        (OperatorNode, "operation_id"),
                        (BuiltinNode, "builtin_id"),
                        (StandardLibNode, "stlib_id"),
                        (CapsuleNode, "capsule_id"),
                    ):

                        if type(obj) is cls:

                            self.insert_node(
                                node_hint=obj.data[key],
                                absolute_midtop=(obj.rectsman.move(20, -20).midtop),
                                commented_out_state=(
                                    obj.data.get("commented_out", False)
                                ),
                            )

                            break

        ### gather references for all newly created objects

        new_objects = chain(
            ## nodes
            (node for node in APP_REFS.gm.nodes if node not in pre_existing_nodes),
            ## text blocks
            (
                block
                for block in APP_REFS.gm.text_blocks
                if block not in pre_existing_text_blocks
            ),
        )

        ### deselect current selection
        self.selected_objs.clear()

        ### select duplicated objects

        self.selected_objs.extend(new_objects)
        self.active_obj = self.selected_objs[0]

        ### set moving_from_duplication flag on
        self.moving_from_duplication = True

        ### put window manager in state to move objects
        self.start_moving()

    def remove_selected(self):
        """Remove selected objects."""
        ### return earlier if there's no selected objects,
        ### since this deletion is applied on them
        if not self.selected_objs:
            return

        ### otherwise remove each selected object according
        ### to its class

        for obj in self.selected_objs:

            if isinstance(obj, TextBlock):
                self.remove_text_block(obj)

            else:
                self.remove_node(obj)

        ### clear selection
        self.deselect_all()

        ### indicate changes made in the data
        indicate_unsaved()

    def remove_node(self, node):
        """Remove given node.

        node (graphman.callablenode.CallableNode instance
              or graphman.proxynode.ProxyNode instance)
        """
        ### remove node instance from the node map and
        ### node data
        APP_REFS.gm.remove_node(node)

    def remove_text_block(
        self,
        text_block,
    ):
        """Remove given text block.

        text_block (graphman.textblock.main.TextBlock obj)
        """
        ### remove text block instance from the text block
        ### list and text block data
        APP_REFS.gm.remove_text_block(text_block)


### utility function


def get_new_node_id():
    """Return a new unused id for the nodes."""
    ### retrieve existing node ids
    existing_ids = APP_REFS.data[NODES_KEY].keys()

    ### get a callable to generate integers from 0 to
    ### infinite
    get_new_id = count().__iter__().__next__

    ### keep generating a new id while until it cannot
    ### be found among the existing ones

    while True:

        new_id = get_new_id()
        if new_id not in existing_ids:
            break

    ### finally return the new unused id
    return new_id
