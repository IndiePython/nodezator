
### local imports

from config import APP_REFS

from pygameconstants import SCREEN_RECT

from widget.stringentry import StringEntry

from menu.main import MenuManager

from editing.popups.constants import GeneralPopupCommands



class ProxyNodePopupMenu(GeneralPopupCommands):

    def __init__(self):

        super().__init__()

        self.entry = (

          StringEntry(
            value = 'output',
            command = self.update_data_node_title,
            validation_command = 'isidentifier',
          )

        )

        ###

        self.redirect_node_only_popup = (

          MenuManager(

            self.GENERAL_SINGLE_COMMANDS,

            is_menubar  = False,
            use_outline = True,
            keep_focus_when_unhovered=True,

          )

        )

        ###

        data_node_menu_list = (
          self.GENERAL_SINGLE_COMMANDS.copy()
        )

        data_node_menu_list.insert(

          0,

          {
            'label'   : "Edit title",
            'icon'    : 'pencil',
            'command' : self.edit_node_title,
          },

        )

        self.data_node_only_popup = (

          MenuManager(

            data_node_menu_list,

            is_menubar  = False,
            use_outline = True,
            keep_focus_when_unhovered=True,

          )

        )

        ###


        self.redirect_node_and_selected_popup = (

          MenuManager(

            (
                 self.GENERAL_COLLECTIVE_COMMANDS
               + self.GENERAL_SINGLE_COMMANDS
            ),

            is_menubar  = False,
            use_outline = True,
            keep_focus_when_unhovered=True,

          )

        )

        ###

        data_node_menu_list.extend(
          self.GENERAL_COLLECTIVE_COMMANDS
        )

        self.data_node_and_selected_popup = (

          MenuManager(

            data_node_menu_list,

            is_menubar  = False,
            use_outline = True,
            keep_focus_when_unhovered=True,

          )

        )

    def show(self, proxy_node, mouse_pos):

        self.obj_under_mouse = proxy_node

        if proxy_node in APP_REFS.ea.selected_objs:

            if hasattr(proxy_node.proxy_socket, 'parent'):

                (
                  self
                  .redirect_node_and_selected_popup
                  .focus_if_within_boundaries(mouse_pos) 
                )

            else:

                (
                  self
                  .data_node_and_selected_popup
                  .focus_if_within_boundaries(mouse_pos) 
                )

        else:

            if hasattr(proxy_node.proxy_socket, 'parent'):

                (
                  self
                  .redirect_node_only_popup
                  .focus_if_within_boundaries(mouse_pos) 
                )

            else:

                (
                  self
                  .data_node_only_popup
                  .focus_if_within_boundaries(mouse_pos) 
                )

    def edit_node_title(self):

        entry = self.entry

        entry.set(
          self.obj_under_mouse.title, False
        )

        entry.rect.midtop = (
          self.obj_under_mouse.rect.move(0, 5).midtop
        )

        entry.rect.clamp_ip(SCREEN_RECT)

        APP_REFS.window_manager.draw()

        self.entry.get_focus()

    def update_data_node_title(self):

        new_title = self.entry.get()
        self.obj_under_mouse.update_title(new_title)
