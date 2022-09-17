"""Facility for data edition/presentation.

Other modules from the "editing" subpackage deal with
data as well, but this one is rather dedicated to direct
edition of data, rather than data edition that is an effect
of custom actions (like deleting a node, for instance).

However, it also contains operations that didn't fit other
modules, so in the end, the functionality here is pretty
varied, though it still handles data, in one way or another.

Here we do things like presenting forms for the user to
edit different kinds of data in the file directly.
"""

### standard library imports

from inspect import getsource, getdoc

from functools import partialmethod

from os import linesep


### local imports

from ..config import APP_REFS

from ..pygameconstants import SCREEN_RECT

from ..logman.main import get_new_logger

from ..translation import TRANSLATION_HOLDER as t

from ..dialog import create_and_show_dialog

from ..our3rdlibs.userlogger import USER_LOGGER

from ..ourstdlibs.exceptionutils import bool_func_from_raiser

from ..our3rdlibs.behaviour import (
    indicate_unsaved,
    set_status_message,
)

from ..fontsman.constants import FIRA_MONO_BOLD_FONT_PATH

from ..textman.viewer.main import view_text

from ..textman.editor.main import edit_text

from ..widget.stringentry import StringEntry

from ..graphman.utils import yield_subgraphs

from ..graphman.callablenode.main import CallableNode
from ..graphman.proxynode.main import ProxyNode
from ..graphman.textblock.main import TextBlock

from ..graphman.textblock.check import (
    check_text_block_text,
)


### create logger for module
logger = get_new_logger(__name__)


### map associating node "commented_out" states to
### corresponding actions performed

ACTION_DESCRIPTION_MAP = {True: "commented out", False: "uncommented"}


### utility functions


def retrieve_callable_info(callable_obj):
    """Return 2-tuple.

    The first value is the callable source or its
    docstring.

    The second value is a boolean which is True if
    the source was retrieve and false otherwise.

    Parameters
    ==========

    callable_obj (any inspectable Python callable)
    """
    ### try retrieving the source code for the callable
    ### as the text containing info about the callable
    try:
        text = getsource(callable_obj)

    ### if it is not possible (for instance, the built-in
    ### function 'pow' can't have its source retrieved,
    ### even though it works with inspect.signature),
    ### just use the docstring or a placeholder text,
    ### if the docstring is None

    except (OSError, TypeError):

        managed_to_get_source = False

        text = getdoc(callable_obj)

        if text is None:
            text = t.editing.data.no_source_available

    ### if it is, set flag to True
    else:
        managed_to_get_source = True

    ### finally return the text retrieved/used and
    ### the flag
    return text, managed_to_get_source


## boolean function to check whether text of text block
## is valid

is_text_block_text_valid = bool_func_from_raiser(
    raiser_func=check_text_block_text,
    reporting_func=create_and_show_dialog,
    include_exception_name=False,
)


### main class definition


class DataHandling:
    """Data handling operations."""

    def __init__(self):

        self.title_entry = StringEntry(
            value="output",
            command=self.update_data_node_title,
            validation_command="isidentifier",
        )

    def info_from_active_selection(self, source_name):
        """Display info about active selection node.

        Parameters
        ==========
        source_name (string)
            name indicating the kind of source to be
            shown; can be 'node_script' or 'callable_info'.
        """

        ### if there's no active selection, notify user
        ### and return earlier

        if not self.active_obj:

            create_and_show_dialog(
                "A node must be selected for the source" " info to be displayed."
            )

            return

        ### likewise, if an object uncompatible with the
        ### feature is selected, notify user and return
        ### earlier

        elif type(self.active_obj) in (
            TextBlock,
            ProxyNode,
        ):

            create_and_show_dialog(
                "The source/info viewing feature does not"
                " apply to text blocks, data nodes or"
                " redirect nodes"
            )

            return

        self.view_info(self.active_obj, source_name)

    view_node_script = partialmethod(info_from_active_selection, "node_script")

    view_callable_info = partialmethod(info_from_active_selection, "callable_info")

    def view_info(self, obj, source_name="node_script"):
        """Retrieve and present obj's source/info."""

        if type(obj) == CallableNode:

            if source_name == "node_script":

                ## retrieve the source of the script from
                ## which the node's callable was retrieved

                text = (
                    # from the APP_REFS obj...
                    APP_REFS
                    # retrieve a map containing pathlib.Path
                    # objects pointing to node scripts
                    .script_path_map
                    # use the script id of the node to
                    # retrieve the pathlib.Path instance
                    # which points to the node's script
                    [obj.data["script_id"]]
                    # and grab its contents
                    .read_text()
                )

                show_line_number = True

            elif source_name == "callable_info":

                ## retrieve information about the node's
                ## main callable

                text, managed_to_get_source = retrieve_callable_info(obj.main_callable)

                show_line_number = managed_to_get_source

        else:

            show_line_number = False
            text = obj.get_source_info()

        ### then display the text

        view_text(
            text,
            syntax_highlighting="python",
            show_line_number=show_line_number,
        )

    def edit_text_of_selected(self):

        ### reference active obj locally
        obj = self.active_obj

        ### retrieve its type
        type_ = type(self.active_obj)

        ### if it is a text block or data node trigger
        ### edition of its text

        if type_ is TextBlock:
            self.edit_text_block_text(obj)

        elif type_ is ProxyNode and not hasattr(obj.proxy_socket, "parent"):
            self.edit_data_node_title(obj)

        ### if the active obj is not a text block or data
        ### node, notify situation to user

        else:

            create_and_show_dialog(
                "The active selection must be a text block"
                " or data node for its text to be edited."
            )

    def edit_text_block_text(self, text_block):
        """Edit text block text on text editor."""
        ### retrieve its text
        text = text_block.data["text"]

        ### edit the text

        edited_text = edit_text(
            text=text,
            font_path=FIRA_MONO_BOLD_FONT_PATH,
            syntax_highlighting="comment",
            validation_command=is_text_block_text_valid,
        )

        ### if the edited text is None, it means the user
        ### cancelled editing the text, so we just indicate
        ### such in the status bar

        if edited_text is None:

            set_status_message("Cancelled editing text of text block.")

        ### if the edited text is equal to the original
        ### one, we do nothing besides indicating such
        ### in the status bar

        elif edited_text == text:

            set_status_message(
                "Text of text block wasn't updated, since" " text didn't change"
            )

        else:

            ## insert the new text
            text_block.data["text"] = edited_text

            ## indicate the change in the data
            indicate_unsaved()

            ## indicate finished action in status bar

            set_status_message("Text of text block was edited.")

            ## rebuild the surface of the text block
            text_block.rebuild_surf()

    def edit_data_node_title(self, data_node):

        entry = self.title_entry

        entry.set(data_node.title, False)

        entry.rect.midtop = data_node.rect.move(0, 5).midtop

        entry.rect.clamp_ip(SCREEN_RECT)

        APP_REFS.window_manager.draw()

        entry.data_node = data_node

        entry.get_focus()

    def update_data_node_title(self):

        entry = self.title_entry
        new_title = entry.get()
        entry.data_node.update_title(new_title)

    def comment_uncomment_selected_nodes(self):
        """Toggle commented out state of selected nodes.

        Nodes attached to the selected ones are also
        affected.
        """
        ### retrieve all selected node instances

        selected_nodes = [
            obj for obj in self.selected_objs if not isinstance(obj, TextBlock)
        ]

        ### if there are no selected node instances,
        ### notify user and return earlier, since there's
        ### nothing to be done in this case

        if not selected_nodes:

            create_and_show_dialog(
                "In order to comment/uncomment selected"
                " nodes at least one must be selected"
            )

        ### otherwise, delegate the
        ### commenting/uncommenting to another
        ### method
        else:
            self.comment_uncomment_nodes(selected_nodes)

    def comment_uncomment_nodes(self, nodes):
        """Toggle commenting state in each subgraph.

        Also, keeps track of the toggled states so that
        actions performed are properly reported.
        """

        toggled_states = set()

        for subgraph in yield_subgraphs(nodes):

            ### sample the state of the nodes from one of
            ### them; it can be any node, we use the first
            ### one

            current_state = subgraph[0].data.get("commented_out", False)

            ### toggle the state
            toggled_state = not current_state

            ### store the toggled state
            toggled_states.add(toggled_state)

            ### apply the toggled state to all nodes in the
            ### subgraph

            for node in subgraph:

                node.data["commented_out"] = toggled_state
                node.perform_commenting_uncommenting_setups()

        ### indicate the change in the data
        indicate_unsaved()

        ### indicate finished action in status bar

        ## build string specifying actions performed,
        ## according to toggled states applied
        ##
        ## note that we sort the order of the states, so
        ## that the items, when more than one, always
        ## appear in the same order

        actions = "/".join(
            ACTION_DESCRIPTION_MAP[toggled_state]
            for toggled_state in sorted(toggled_states)
        )

        ## build a message with the actions
        message = "Nodes were {}.".format(actions)

        ## finally display the message in the status bar
        set_status_message(message)

    def show_user_log_contents(self):

        view_text(
            USER_LOGGER.contents,
            syntax_highlighting="user_log",
            header_text="User log",
            index_to_jump_to=-1,
        )

    def show_custom_stdout_contents(self):

        view_text(
            text=linesep.join(APP_REFS.custom_stdout_lines),
            header_text="Text from custom stdout",
            general_text_settings="custom_stdout",
            index_to_jump_to=-1,
        )
