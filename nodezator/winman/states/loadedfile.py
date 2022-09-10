"""Window manager event handling for 'loaded_file' state."""

### standard library import
from itertools import chain


### third-party imports

from pygame import (
    QUIT,
    KEYDOWN,
    KEYUP,
    KMOD_CTRL,
    KMOD_SHIFT,
    K_g,
    K_u,
    K_r,
    K_DELETE,
    K_F1,
    K_F5,
    K_F12,
    K_KP0,
    K_HOME,
    K_w,
    K_a,
    K_s,
    K_d,
    K_n,
    K_o,
    K_i,
    K_e,
    K_p,
    K_t,
    K_3,
    K_j,
    K_UP,
    K_LEFT,
    K_DOWN,
    K_RIGHT,
    K_MENU,
    MOUSEMOTION,
    MOUSEBUTTONUP,
    MOUSEBUTTONDOWN,
)

from pygame.event import get as get_events

from pygame.key import (
    get_mods as get_mods_bitmask,
    get_pressed as get_pressed_keys,
)

from pygame.mouse import get_pos as get_mouse_pos

from pygame.display import update


### local imports

from ...config import APP_REFS

from ...our3rdlibs.keyconst import KEYPAD_TO_COORDINATE_MAP

from ...loopman.exception import (
    QuitAppException,
    ContinueLoopException,
    SwitchLoopException,
)

from ...htsl.main import open_htsl_link


class LoadedFileState:
    """Methods related to 'loaded_file' state."""

    def loaded_file_event_handling(self):
        """Get and respond to events."""
        for event in get_events():

            ### QUIT
            if event.type == QUIT:
                raise QuitAppException

            ### MOUSEMOTION

            elif event.type == MOUSEMOTION:
                self.loaded_file_on_mouse_motion(event)

            ### MOUSEBUTTONDOWN

            elif event.type == MOUSEBUTTONDOWN:

                if event.button == 1:

                    ## trigger the mouse click method
                    self.loaded_file_on_mouse_click(event)

            ### MOUSEBUTTONUP

            elif event.type == MOUSEBUTTONUP:

                ## XXX if/elif blocks below could be better
                ## commented

                if event.button == 1:
                    self.loaded_file_on_mouse_release(event)

                elif event.button == 3:

                    (self.loaded_file_on_right_mouse_release(event))

            ### KEYDOWN

            elif event.type == KEYDOWN:

                ## Application related operations

                # quit
                if event.key == K_w and event.mod & KMOD_CTRL:
                    raise QuitAppException

                # create new file
                elif event.key == K_n and event.mod & KMOD_CTRL:
                    self.new()

                # open file
                elif event.key == K_o and event.mod & KMOD_CTRL:
                    self.open()

                ## Export node graph

                elif event.key == K_e and event.mod & KMOD_CTRL:
                    APP_REFS.ea.export_as_image()

                elif event.key == K_p and event.mod & KMOD_CTRL:
                    APP_REFS.ea.export_as_python()

                ## Duplicate selected nodes

                elif event.key == K_d and event.mod & KMOD_CTRL:
                    APP_REFS.ea.duplicate_selected()

                ## undo/redo changes

                # XXX not (re)implemented yet
                elif event.key == K_u:
                    pass  # APP_REFS.ea.undo()

                elif event.key == K_r and KMOD_CTRL & event.mod:
                    pass  # APP_REFS.ea.redo()

            ### KEYUP

            elif event.type == KEYUP:

                ## toggle grid
                if event.key == K_KP0:
                    APP_REFS.ea.toggle_grid()

                ## save file

                elif event.key == K_s and event.mod & KMOD_CTRL:

                    if event.mod & KMOD_SHIFT:
                        self.save_as()

                    else:
                        self.save()

                    raise ContinueLoopException

                ## show help text

                elif event.key == K_F1:

                    open_htsl_link("htap://help.nodezator.pysite")

                ## reload file
                elif event.key == K_F5:
                    self.reload()

                ## execute nodes

                elif event.key == K_F12:

                    if event.mod & KMOD_SHIFT:

                        (APP_REFS.gm.execute_with_custom_stdout())

                    else:
                        APP_REFS.gm.execute_graph()

                ## scroll back to origin

                elif event.key == K_HOME:
                    APP_REFS.ea.scroll_to_origin()

                ## positioning related

                elif event.key == K_g:
                    APP_REFS.ea.start_moving()

                ## deleting nodes
                elif event.key == K_DELETE:
                    APP_REFS.ea.remove_selected()

                ## active node's info

                elif event.key == K_i:

                    if event.mod & KMOD_SHIFT:
                        APP_REFS.ea.view_callable_info()

                    else:
                        APP_REFS.ea.view_node_script()

                ## edit text of selected text block or
                ## label of data node

                elif event.key == K_t:
                    APP_REFS.ea.edit_text_of_selected()

                ## comment out/uncomment nodes
                ## (same as typing '#')

                elif event.key == K_3 and event.mod & KMOD_SHIFT:

                    (APP_REFS.ea.comment_uncomment_selected_nodes())

                ## display the text of the user log

                elif event.key == K_j and event.mod & KMOD_CTRL:

                    if event.mod & KMOD_SHIFT:

                        (APP_REFS.ea.show_user_log_contents())

                    else:

                        (APP_REFS.ea.show_custom_stdout_contents())

                ## selection related

                elif event.key == K_a and event.mod & KMOD_CTRL:

                    if event.mod & KMOD_SHIFT:
                        APP_REFS.ea.deselect_all()

                    else:
                        APP_REFS.ea.select_all()

                ## canvas context menu

                elif event.key == K_MENU:

                    mouse_pos = get_mouse_pos()

                    ### mark the mouse position for the
                    ### editing assistant, that is, the
                    ### position from where the popup
                    ### spawned;
                    ###
                    ### this position is used in case the
                    ### user performs a command to add an
                    ### object to the canvas, as the
                    ### position of the object (we have
                    ### been using it as the midtop
                    ### coordinate of new objects)
                    APP_REFS.ea.popup_spawn_pos = mouse_pos

                    ### then give focus to the popup menu

                    (self.canvas_popup_menu.focus_if_within_boundaries(mouse_pos))

                ## jump to corner feature

                elif event.key in KEYPAD_TO_COORDINATE_MAP and event.mod & KMOD_SHIFT:

                    corner = KEYPAD_TO_COORDINATE_MAP[event.key]
                    APP_REFS.ea.jump_to_corner(corner)

    def loaded_file_keyboard_input_handling(self):
        """Handle keyboard specific input."""
        ### get input state maps
        key_input, modif_bitmask = get_pressed_keys(), get_mods_bitmask()

        ### check whether the control key is pressed
        ctrl = modif_bitmask & KMOD_CTRL

        ### if the control key is pressed we give up
        ### scrolling altogether by returning earlier;
        ###
        ### we do so because we assume the control key
        ### is pressed because the user is attempting
        ### to use one of the scroll keys for other
        ### purpose other than scrolling;
        ###
        ### for instance, the "s" and "d" keys, can be used
        ### together with the control (ctrl) key to save
        ### the file and duplicate selected nodes,
        ### respectively
        if ctrl:
            return

        ### state of keys related to scrolling

        up = key_input[K_w] or key_input[K_UP]
        left = key_input[K_a] or key_input[K_LEFT]
        down = key_input[K_s] or key_input[K_DOWN]
        right = key_input[K_d] or key_input[K_RIGHT]

        ### perform scrolling or not, according to state
        ### of keys

        ## vertical scrolling

        if up and not down:
            APP_REFS.ea.scroll_up()

        elif down and not up:
            APP_REFS.ea.scroll_down()

        ## horizontal scrolling

        if left and not right:
            APP_REFS.ea.scroll_left()

        elif right and not left:
            APP_REFS.ea.scroll_right()

    def loaded_file_on_mouse_click(self, event):
        """Act on mouse left button pressing.

        Act based on mouse position.
        """
        ### retrieve the mouse position
        mouse_pos = event.pos

        ### check objects on screen for collision

        for obj in chain(
            self.switches,
            APP_REFS.gm.text_blocks.get_on_screen(),
            APP_REFS.gm.nodes.get_on_screen(),
        ):

            if obj.rect.collidepoint(mouse_pos):

                try:
                    method = obj.on_mouse_click
                except AttributeError:
                    pass
                else:
                    method(event)

                break

        ### otherwise, if no collision is detected with
        ### any node, just set the "clicked_mouse" flag on
        else:
            self.clicked_mouse = True

    def loaded_file_on_mouse_motion(self, event):
        """Act based on mouse motion event.

        Parameters
        ==========
        event
            pygame.event.Event object of type
            pygame.MOUSEMOTION.

        About the 'mouse_click_target' attribute
        ========================================

        Since we don't keep track of when the mouse
        leaves the boundaries of nodes or text blocks,
        in some rare cases the user might click one of
        these objects and immediately move the cursor
        away from the obj, making it so this attribute
        is left set to True, instead of being set to
        False and triggering the movement of objects.

        The only effect this will have is that the next
        time the user hover that object the movement
        will be triggered, but this is really rare
        behaviour and otherwise not considered
        bothersome enough to justify redesigning the
        app to track when the cursor exits the boundaries
        of such objects.
        """
        ### retrieve the mouse position
        mouse_pos = event.pos

        ### if the menu is hovered, we use it as the
        ### new loop holder in the application loop,
        ### by raising a special method, after we set
        ### the clicked_mouse flag to False, as an admin
        ### task

        if self.menubar.get_hovered_menu(mouse_pos):

            self.clicked_mouse = False

            raise SwitchLoopException(self.menubar)

        ### iterate over objects to check whether any of
        ### them was hovered by the mouse in this mouse
        ### motion event;

        for obj in chain(
            APP_REFS.gm.text_blocks.get_on_screen(), APP_REFS.gm.nodes.get_on_screen()
        ):

            if obj.rect.collidepoint(mouse_pos):

                ## if a hovered object was the target
                ## of a click action before, deselect all
                ## objects, select this one and trigger
                ## its movement;
                ##
                ## for more information about the
                ## 'mouse_click_target' attribute of nodes
                ## and text blocks we use below, check the
                ## docstring of this method

                if obj.mouse_click_target:

                    ## set the flag to False
                    obj.mouse_click_target = False

                    ## move object considering it is
                    ## an target of a click and drag
                    ## action
                    APP_REFS.ea.move_from_click_and_drag(obj)

        ### if we reach this point in the method we know
        ### that objects weren't hovered in the "for loop"
        ### above because APP_REFS.ea.start_moving, among
        ### other things, raises an exception which causes
        ### the execution flow to leave this method when
        ### executed

        ### if neither the menu nor any object is hovered by
        ### the mouse, but the mouse was clicked before, it
        ### means we are dragging the mouse, which means the
        ### user wants to either cut segments or perform a
        ### box selection, depending on the modifier keys
        ### pressed or not

        if self.clicked_mouse:

            ## set the clicked_mouse flag to False,
            ## since we use it only to determine when
            ## we are dragging the mouse (if it is on
            ## when executing this mouse motion method)
            self.clicked_mouse = False

            ## obtain a bitmask which you'll use to check
            ## the state of modifier keys along the method
            bitmask = get_mods_bitmask()

            ## store the state of the ctrl key
            ctrl_pressed = bitmask & KMOD_CTRL

            ## store the state of the shift key
            shift_pressed = bitmask & KMOD_SHIFT

            ## now define which is the case depending on
            ## the modifier keys pressed or not pressed

            # user wants to cut segments between nodes

            if ctrl_pressed and not shift_pressed:

                (APP_REFS.gm.trigger_segments_severance(mouse_pos))

            # user wants to perform box selection
            else:
                APP_REFS.ea.start_box_selection()

    def loaded_file_on_mouse_release(self, event):
        """Act on mouse left button release.

        Act based on mouse position.

        event
            pygame.event.Event object of type
            pygame.MOUSEBUTTONUP.
        """
        ### store the mouse position when released
        mouse_pos = event.pos

        ### set the "clicked_mouse" flag off
        self.clicked_mouse = False

        ### check different groups of objects for collision

        for obj in chain(
            self.switches,
            APP_REFS.gm.text_blocks.get_on_screen(),
            APP_REFS.gm.nodes.get_on_screen(),
        ):

            if obj.rect.collidepoint(mouse_pos):

                obj.on_mouse_release(event)
                break

        ### getting to this "else clause" means none of the
        ### objects above collided;
        ###
        ### that is, the user either clicked the menubar,
        ### or the canvas in an empty area

        else:

            ### if the menu is hovered, we use it as the
            ### new loop holder in the application loop,
            ### by raising a special method, after we set
            ### the clicked_mouse flag to False, as an admin
            ### task

            if self.menubar.get_hovered_menu(mouse_pos):

                self.clicked_mouse = False

                raise SwitchLoopException(self.menubar)

            ## otherwise the user clicked the canvas, in
            ## which case we assume the user wants to
            ## deselect all objects (in case there are
            ## selected objects)
            else:
                APP_REFS.ea.deselect_all()

    def loaded_file_on_right_mouse_release(self, event):
        """Act on mouse right button release.

        Act based on mouse position.
        """
        ### retrieve mouse position
        mouse_pos = event.pos

        ### check nodes for collision, executing its
        ### respective method if so and returning

        for obj in chain(
            APP_REFS.gm.nodes.get_on_screen(),
            APP_REFS.gm.text_blocks.get_on_screen(),
        ):

            if obj.rect.collidepoint(mouse_pos):

                obj.on_right_mouse_release(event)
                break

        ### otherwise, it means the user right-clicked an
        ### empty area in the canvas; in such case, we assume
        ### the user means to invoke to popup menu, so we
        ### take measures to make it happen

        else:

            ### mark the mouse position for the editing
            ### assistant, that is, the position from
            ### where the popup spawned;
            ###
            ### this position is used in case the user
            ### performs a command to add an object to
            ### the canvas, as the position of the object
            ### (we have been using it as the midtop
            ### coordinate of new objects)
            APP_REFS.ea.popup_spawn_pos = event.pos

            ### then give focus to the popup menu

            (self.canvas_popup_menu.focus_if_within_boundaries(event.pos))

    ### update

    def loaded_file_update(self):
        """Update method for the 'loaded_file' state."""
        for item in self.labels_update_methods:
            item()
        for item in self.switches_update_methods:
            item()

    ### draw

    def loaded_file_draw(self):
        """Draw method for the 'loaded_file' state."""
        self.background.draw()

        APP_REFS.ea.grid_drawing_behaviour()
        APP_REFS.ea.draw_selected()
        APP_REFS.gm.draw()

        for item in self.labels_drawing_methods:
            item()
        for item in self.switches_drawing_methods:
            item()

        self.separator.draw()
        self.menubar.draw_top_items()

        update()  # pygame.display.update
