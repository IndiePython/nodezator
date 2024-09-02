"""Window manager event handling for 'loaded_file' state."""

### standard library import
from itertools import chain


### third-party imports

from pygame.locals import (
    QUIT,
    KEYDOWN,
    KEYUP,
    KMOD_CTRL,
    KMOD_SHIFT,
    K_b,
    K_g,
    K_u,
    K_r,
    K_DELETE,
    K_F1,
    K_F5,
    K_F8,
    K_F12,
    K_KP0,
    K_HOME,
    K_w,
    K_q,
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
    MOUSEWHEEL,
)


### local imports

from ...pygamesetup import SERVICES_NS

from ...config import APP_REFS

from ...loopman.exception import (
    QuitAppException,
    CloseFileException,
    ContinueLoopException,
    SwitchLoopException,
)

from ...htsl.main import open_htsl_link



class LoadedFileState:
    """Methods related to 'loaded_file' state."""

    def loaded_file_event_handling(self):
        """Get and respond to events."""
        for event in SERVICES_NS.get_events():

            ### QUIT

            if event.type == QUIT:
                raise QuitAppException

            ### MOUSEWHEEL

            elif event.type == MOUSEWHEEL:

                x, y = event.x*50, event.y*50
                mod = SERVICES_NS.get_pressed_mod_keys()

                if  mod & KMOD_SHIFT:
                    x, y = y, x

                APP_REFS.ea.scroll(x, y)

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

                if event.key == K_q and event.mod & KMOD_CTRL:
                    raise QuitAppException

                # close file

                elif event.key == K_w and event.mod & KMOD_CTRL:

                    if hasattr(APP_REFS, 'source_path'):
                        raise CloseFileException

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

                    if event.mod & KMOD_SHIFT:
                        APP_REFS.ea.view_as_python()

                    else:
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

                    open_htsl_link("nodezator://help.nodezator.pysite")

                ## reload file
                elif event.key == K_F5:
                    self.reload()

                ## trigger system testing session

                elif (
                    event.key == K_F8
                    and event.mod & KMOD_SHIFT
                ):

                    if event.mod & KMOD_CTRL:
                        APP_REFS.ea.run_all_cases_at_max_speed()

                    else:
                        APP_REFS.ea.rerun_previous_test_session()

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

                ## prepare and present bird's eye view

                elif event.key == K_b:
                    APP_REFS.ea.prepare_and_present_birdseye_view()

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

                ## different actions using the J key

                elif event.key == K_j:

                    if event.mod & KMOD_SHIFT:

                        ## display the text of the user log

                        if event.mod & KMOD_CTRL:
                            APP_REFS.ea.show_user_log_contents()

                        ## present form to jump to node by id

                        else:
                            APP_REFS.ea.present_jump_to_node_form()

                    ## show contents of custom standard output stream

                    elif event.mod & KMOD_CTRL:
                        APP_REFS.ea.show_custom_stdout_contents()

                ## selection related

                elif event.key == K_a and event.mod & KMOD_CTRL:

                    if event.mod & KMOD_SHIFT:
                        APP_REFS.ea.deselect_all()

                    else:
                        APP_REFS.ea.select_all()

                ## canvas context menu

                elif event.key == K_MENU:

                    mouse_pos = SERVICES_NS.get_mouse_pos()

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

    def loaded_file_keyboard_input_handling(self):
        """Handle keyboard specific input."""
        ### get input state maps

        key_input, modif_bitmask = (
            SERVICES_NS.get_pressed_keys(), SERVICES_NS.get_pressed_mod_keys()
        )

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

        x_direction = y_direction = 0

        ## horizontal

        if left and not right:
            x_direction = 1

        elif right and not left:
            x_direction = -1

        ## vertical

        if up and not down:
            y_direction = 1

        elif down and not up:
            y_direction = -1

        ## scroll

        if x_direction or y_direction:
            APP_REFS.ea.scroll_on_direction(x_direction, y_direction)

    def loaded_file_on_mouse_click(self, event):
        """Act on mouse left button pressing.

        Act based on mouse position.
        """
        ### retrieve the mouse position
        mouse_pos = event.pos

        ### check objects on screen for collision

        gm = APP_REFS.gm

        for obj in chain(
            self.switches,
            gm.text_blocks.get_on_screen(),
            gm.nodes.get_on_screen(),
            gm.preview_toolbars.get_on_screen(),
            gm.preview_panels.get_on_screen(),
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
            pygame.event.Event object of type pygame.MOUSEMOTION
            or similar object.

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
        ### them was...
        ###
        ### - hovered by the mouse in this mouse motion event;
        ### - target of a previous mouse click event.
        ###
        ### if we find such object, we'll start moving it after
        ### we exit the for-loop
        ###
        ### for more information about the 'mouse_click_target' attribute
        ### of nodes and text blocks, used here, check the docstring of
        ### this method

        ## first, a few admin tasks

        # grab and populate a list of nodes that are on the screen

        nodes_on_screen = APP_REFS.gm.nodes_on_screen
        nodes_on_screen.extend(APP_REFS.gm.nodes.get_on_screen())

        # create a variable to hold the object if we find it
        obj_to_move = None

        ## now look for the object

        for obj in chain(
            nodes_on_screen,
            APP_REFS.gm.text_blocks.get_on_screen(),
        ):

            if (
                obj.rect.collidepoint(mouse_pos)
                and obj.mouse_click_target
            ):
                obj_to_move = obj
                break

        ### if we found such obj, start moving it after performing
        ### a few admin tasks

        if obj_to_move:

            # clean the collection of nodes on screen
            nodes_on_screen.clear()

            ## set the flag to False
            obj.mouse_click_target = False

            ## move object considering it is an target of a
            ## click and drag action
            APP_REFS.ea.move_from_click_and_drag(obj)

        ### if we reach this point in the method we know that objects
        ### weren't hovered in the "for loop" above because
        ### APP_REFS.ea.move_from_click_and_drag, among other things,
        ### also calls a method that raises an exception, causing the
        ### execution flow to leave this method when executed

        ### if neither the menu nor any object is hovered by the mouse,
        ### but the mouse was clicked before, it means we are dragging
        ### the mouse;
        ###
        ### depending on the state of modifier keys, this means the user
        ### wants to either:
        ###
        ### - cut segments between sockets
        ### - or begin defining a new segment between sockets
        ### - or perform a box selection

        if self.clicked_mouse:

            ## set the clicked_mouse flag to False,
            ## since we use it only to determine when
            ## we are dragging the mouse
            self.clicked_mouse = False

            ## obtain a bitmask which you'll use to check
            ## the state of modifier keys along the method
            bitmask = SERVICES_NS.get_pressed_mod_keys()

            ## if shift is pressed, exit method earlier, by returning,
            ## since there's nothing to be done in this scenario
            if bitmask & KMOD_SHIFT: return

            ## if ctrl is pressed, the user wants to cut segments between
            ## nodes

            if bitmask & KMOD_CTRL:
                APP_REFS.gm.trigger_segments_severance(mouse_pos)

            ## otherwise we must perform additional checks to determine
            ## what the user wants to do

            else:

                # if the periphery of a node collided with the mouse and
                # there was a socket close enough, we assume the user may
                # want to start defining a segment from the that socket
                #
                # if this is indeed the case, an exception will be raised on
                # purpose and the method will finish executing here
                APP_REFS.gm.start_defining_segment_if_close_to_socket(mouse_pos)

                # otherwise, we just assume the user wants to perform a box
                # selection
                APP_REFS.ea.start_box_selection()

        ### if the mouse wasn't clicked before, all that's left is to
        ### clear the collection of nodes on screen

        else:
            nodes_on_screen.clear()

    def loaded_file_on_mouse_release(self, event):
        """Act on mouse left button release.

        Act based on mouse position.

        event
            pygame.event.Event object of type pygame.MOUSEBUTTONUP
            or similar object.
        """
        ### store the mouse position when released
        mouse_pos = event.pos

        ### set the "clicked_mouse" flag off
        self.clicked_mouse = False

        ### check different groups of objects for collision

        gm = APP_REFS.gm

        for obj in chain(
            self.switches,
            gm.text_blocks.get_on_screen(),
            gm.nodes.get_on_screen(),
            gm.preview_toolbars.get_on_screen(),
            gm.preview_panels.get_on_screen(),
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

        SERVICES_NS.update_screen()
