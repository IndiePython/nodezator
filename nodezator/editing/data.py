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

from config import APP_REFS

from translation import TRANSLATION_HOLDER as t

from dialog import create_and_show_dialog

from our3rdlibs.userlogger import USER_LOGGER

from ourstdlibs.exceptionutils import bool_func_from_raiser

from our3rdlibs.behaviour import (
                            indicate_unsaved,
                            set_status_message,
                          )

from fontsman.constants import FIRA_MONO_BOLD_FONT_PATH

from textman.viewer.main import view_text

from textman.editor.main import edit_text

from fileman.main import select_path

from graphman.utils import yield_subgraphs

from graphman.callablenode.main import CallableNode
from graphman.proxynode.main    import ProxyNode
from graphman.textblock.main    import TextBlock

from graphman.textblock.check import (
                                check_text_block_text,
                              )

from graphman.nodepacksissues import (
                         get_formatted_current_node_packs,
                         check_node_packs,
                       )

from graphman.exception import NODE_PACK_ERRORS

from graphman.scriptloading import load_scripts


### map associating node "commented_out" states to
### corresponding actions performed

ACTION_DESCRIPTION_MAP = {
  True  : "commented out",
  False : "uncommented"
}


### utility functions

def retrieve_callable_info(callable_obj):
    """Return callable source or its docstring.

    Parameters
    ==========

    callable_obj (any inspectable Python callable)
    """
    ### try retrieving the source code for the callable
    ### as the text containing info about the callable
    try: text = getsource(callable_obj)
      
    ### if it is not possible (for instance, the built-in
    ### function 'pow' can't have its source retrieved,
    ### even though it works with inspect.signature),
    ### just used the docstring or a placeholder text,
    ### if the docstring is None

    except (OSError, TypeError):
        
        text = getdoc(callable_obj)
          
        if text is None:
            text = t.editing.data.no_source_available

    ### finally return the text retrieved/used
    return text


## boolean function to check whether text of text block
## is valid

is_text_block_text_valid = (

  bool_func_from_raiser(

    raiser_func            = check_text_block_text,
    reporting_func         = create_and_show_dialog,
    include_exception_name = False,

  )

)

### main class definition

class DataHandling:
    """Data handling operations."""

    def view_code(self, source_name):
        """Display source of active node's script.

        Parameters
        ==========
        source_name (string)
            name indicating the kind of source to be
            shown; can be 'node_script' or 'callable_source'.
        """
        ### if the active obj is not a node, notify situation
        ### to user via dialog and return earlier

        if not isinstance(self.active_obj, CallableNode):

            create_and_show_dialog(
              "A node must be the active selection"
              " for its code to be displayed"
            )

            return

        ### otherwise, retrieve the code requested as text

        if source_name == 'node_script':

            ## retrieve the source of the script from which
            ## the node's callable was retrieved

            text = (

              # from the APP_REFS obj...
              APP_REFS

              # retrieve a map containing pathlib.Path
              # objects pointing to node scripts
              .script_path_map

              # use the id of the node's defining object
              # to retrieve the pathlib.Path instance
              # which points to the node's script

              [

                APP_REFS.id_map[
                           self
                           .active_obj
                           .signature_callable
                         ]
              ]

              # and grab its contents
              .read_text()

            )

        elif source_name == 'callable_source':

            ## retrieve information about the node's
            ## callable

            text = retrieve_callable_info(
                     self.active_obj.signature_callable
                   )

        ### then display the text

        view_text(
          text,
          syntax_highlighting='python',
          show_line_number=True,
        )

    view_node_script = partialmethod(
                         view_code, 'node_script'
                       )

    view_callable_source = partialmethod(
                             view_code, 'callable_source'
                           )

    def edit_text_of_selected(self):

        ### if the active obj is not a text block, notify
        ### situation to user and return earlier

        type_ = type(self.active_obj)

        if type_ is TextBlock:
            self.edit_text_block_text()

        #elif type_ is ProxyNode:
        #    self.edit_proxy_node_label()

        else:

            create_and_show_dialog(
              "The text block must be the active"
              " selection if you want to edit its text."
            )

    def edit_text_block_text(self):
        """Edit text block text on text editor."""

        ### otherwise, edit the text block's text in the
        ### text editor

        ## reference text block locally
        block = self.active_obj

        ## retrieve its text
        text = block.data['text']

        ### edit the text

        edited_text = \
            edit_text(
              text=text,
              font_path=FIRA_MONO_BOLD_FONT_PATH,
              syntax_highlighting='comment',
              validation_command=is_text_block_text_valid
            )

        ### if the edited text is None, it means the user
        ### cancelled editing the text, so we just indicate
        ### such in the status bar

        if edited_text is None:

            set_status_message(
              "Cancelled editing text of text block."
            )

        ### if the edited text is equal to the original
        ### one, we do nothing besides indicating such
        ### in the status bar

        elif edited_text == text:

            set_status_message(
              "Text of text block wasn't updated, since"
              " text didn't change"
            )

        else:

            ## insert the new text
            block.data['text'] = edited_text

            ## indicate the change in the data
            indicate_unsaved()

            ## indicate finished action in status bar

            set_status_message(
              "Text of text block was edited."
            )

            ## rebuild the surface of the text block
            block.rebuild_surf()

    def edit_proxy_label(self):
        """Edit proxy node label on form."""
        ### reference node locally
        node = self.active_obj

        ### retrieve label's text
        text = node.data['label_text']

        ### TODO implement form to be used in the block
        ### below

        ### edit the text
        ...

        ### if the edited text is None, it means the user
        ### cancelled editing the text, so we just indicate
        ### such in the status bar

        if edited_text is None:

            set_status_message(
              "Cancelled editing text of"
              " raw data node's label."
            )

        ### if the edited text is equal to the original
        ### one, we do nothing besides indicating such
        ### in the status bar

        elif edited_text == text:

            set_status_message(
              "Text of raw data node's label wasn't"
              " updated, since text didn't change"
            )

        else:

            ## insert the new text
            node.data['label_text'] = edited_text

            ## indicate the change in the data
            indicate_unsaved()

            ## indicate finished action in status bar

            set_status_message(
              "Text of text block was edited."
            )

            ## update the node's label surface
            node.update_label_surface()

    def comment_uncomment_nodes(self):
        """Toggle commented out state of selected nodes.

        Nodes attached to the selected ones are also
        affected.
        """
        ### retrieve all selected node instances

        selected_nodes = [
          obj
          for obj in self.selected_objs
          if not isinstance(obj, TextBlock)
        ]

        ### if there are no selected node instances,
        ### notify user and return earlier, since there's
        ### nothing to be done in this case

        if not selected_nodes:

            create_and_show_dialog(
              "You need first to select node(s) in order"
              " to be able to comment/uncomment them"
            )

            return

        ### otherwise, iterate over each subgraph,
        ### commenting out/uncommenting the nodes,
        ### depending on their initial state
        ###
        ### also, keep track of the toggled states so
        ### that you know which actions you performed,
        ### in order to notify the user properly

        toggled_states = set()

        for subgraph in yield_subgraphs(selected_nodes):
            
            ### sample the state of the nodes from one of
            ### them; it can be any node, we use the first
            ### one

            current_state = \
            subgraph[0].data.get('commented_out', False)

            ### toggle the state
            toggled_state = not current_state

            ### store the toggled state
            toggled_states.add(toggled_state)

            ### apply the toggled state to all nodes in the
            ### subgraph

            for node in subgraph:

                node.data['commented_out'] = toggled_state
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

                        for toggled_state
                        in sorted(toggled_states)

                      )

        ## build a message with the actions
        message = "Nodes were {}.".format(actions)

        ## finally display the message in the status bar
        set_status_message(message)


    ### TODO refactor

    def select_node_packs(self):
        """"""

        ### select new paths;

        paths = select_path(
                  caption=(
                    "Select node paths for current file"
                  ),
                )

        if not paths: return

        ### check them

        try: check_node_packs(paths)

        except NODE_PACK_ERRORS as err:

            create_and_show_dialog(
               "One or more node packs selected presented"
              f" errors. Here's the error message: {err}"
            )

            return

        ### grab current node pack selection;
        current = get_formatted_current_node_packs()

        if set(current) == set(paths):
            return

        removed = {
          item
          for item in current
          if item not in paths
        }

        ### if there are removed node packs, check whether
        ### there are instantiated nodes from them

        if removed:
            
            removed_names = {path.name for path in removed}

            orphaned_nodes_ids = []
            not_removable_packs = set()

            for node in APP_REFS.gm.nodes:
                
                if 'script_id' not in node.data:
                    continue

                node_pack_name = node.data['script_id'][0]

                if node_pack_name in removed_names:

                    not_removable_packs.add(node_pack_name)
                    orphaned_nodes_ids.append(node.id)

            if orphaned_nodes_ids:

                message = (
                   "before removing packs named"
                  f" {not_removable_packs}, you must"
                   "remove the nodes of ids"
                  f" {orphaned_nodes_ids}, which belong"
                   " to those node packs"
                )

                create_and_show_dialog(message)
                return

        ### update node packs

        value = (

          str(paths[0])
          if len(paths) == 1

          else [str(path) for path in paths]

        )

        APP_REFS.data['node_packs'] = value

        ### load scripts to use callables provided by
        ### them as specifications for nodes
        load_scripts(APP_REFS.data['node_packs'])

        # rebuild popup menu;
        APP_REFS.window_manager.create_canvas_popup_menu()

        # rebuild change category colors form
        self.rebuild_category_color_form()

        ## indicate the change in the data
        indicate_unsaved()

        ## indicate finished action in status bar

        set_status_message(
          "Node packs for current file were changed."
        )

    def unlink_all_node_packs_from_file(self):
        """"""
        node_packs = APP_REFS.data.get('node_packs')

        if not node_packs:

            create_and_show_dialog(
              "Don't need to unlink node packs cause"
              " the file doesn't have any."
            )

            return

        answer = create_and_show_dialog(
                   "Are you sure you want to unlink"
                   " all node packs from file"
                 )

        ### grab current node pack selection;
        current = get_formatted_current_node_packs()

        ### check whether there are instantiated nodes
        ### from them

        removed_names = {path.name for path in current}

        orphaned_nodes_ids = []
        not_removable_packs = set()

        for node in APP_REFS.gm.nodes:
            
            if 'script_id' not in node.data:
                continue

            node_pack_name = node.data['script_id'][0]

            not_removable_packs.add(node_pack_name)
            orphaned_nodes_ids.append(node.id)

        if orphaned_nodes_ids:

            message = (
               "before removing packs named"
              f" {not_removable_packs}, you must"
               "remove the nodes of ids"
              f" {orphaned_nodes_ids}, which belong"
               " to those node packs"
            )

            create_and_show_dialog(message)
            return

        del APP_REFS.data['node_packs']
        APP_REFS.window_manager.create_canvas_popup_menu()

        ## indicate the change in the data
        indicate_unsaved()

        ## indicate finished action in status bar

        set_status_message(
          "Node packs were removed from current file."
        )

    def show_user_log_contents(self):

        view_text(
          USER_LOGGER.contents,
          syntax_highlighting='user_log',
          header_text = "User log",
          index_to_jump_to=-1,
        )

    def show_custom_stdout_contents(self):

        view_text(
          text=linesep.join(APP_REFS.custom_stdout_lines),
          header_text = "Text from custom stdout",
          general_text_settings = 'custom_stdout',
          index_to_jump_to=-1,
        )
