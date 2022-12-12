"""Form for changing node packs on existing file."""

### standard library imports

from pathlib import Path

from functools import partial, partialmethod


### third-party imports

from pygame import (
    QUIT,
    MOUSEBUTTONDOWN,
    MOUSEBUTTONUP,
    KEYUP,
    KEYDOWN,
    K_UP,
    K_DOWN,
    K_ESCAPE,
    K_RETURN,
    K_KP_ENTER,
)

from pygame.event import get as get_events

from pygame.display import update

from pygame.math import Vector2


### local imports

from ...config import APP_REFS

from ...translation import TRANSLATION_HOLDER as t

from ...pygameconstants import (
    SCREEN_RECT,
    FPS,
    maintain_fps,
    blit_on_screen,
)

from ...appinfo import NATIVE_FILE_EXTENSION

from ...dialog import create_and_show_dialog

from ...fileman.main import select_paths

from ...ourstdlibs.collections.general import CallList

from ...ourstdlibs.behaviour import empty_function, get_oblivious_callable

from ...ourstdlibs.pyl import load_pyl, save_pyl

from ...our3rdlibs.button import Button

from ...our3rdlibs.behaviour import (
    watch_window_size,
    indicate_unsaved,
    set_status_message,
)

from ...classes2d.single import Object2D
from ...classes2d.collections import List2D

from ...fontsman.constants import (
    ENC_SANS_BOLD_FONT_HEIGHT,
    ENC_SANS_BOLD_FONT_PATH,
)

from ...textman.render import render_text
from ...textman.label.main import Label

from ...surfsman.cache import (
    UNHIGHLIGHT_SURF_MAP,
    cache_screen_state,
    draw_cached_screen_state,
)

from ...surfsman.icon import render_layered_icon

from ...surfsman.draw import draw_border, draw_depth_finish
from ...surfsman.render import render_rect

from ...loopman.exception import (
    QuitAppException,
    SwitchLoopException,
)

from ...colorsman.colors import (
    BLACK,
    CONTRAST_LAYER_COLOR,
    WINDOW_FG,
    WINDOW_BG,
    BUTTON_FG,
    BUTTON_BG,
)

from ...graphman.nodepacksissues import (
    get_formatted_local_node_packs,
    get_formatted_installed_node_packs,
    check_local_node_packs,
    check_installed_node_packs,
)

from ...graphman.scriptloading import load_scripts

from ...graphman.exception import NODE_PACK_ERRORS

from ...knownpacks import get_known_node_packs


## widgets

from ...widget.optionmenu.main import OptionMenu

from ...widget.stringentry import StringEntry


### constants

TEXT_SETTINGS = {
    "font_height": ENC_SANS_BOLD_FONT_HEIGHT,
    "font_path": ENC_SANS_BOLD_FONT_PATH,
    "padding": 5,
    "foreground_color": WINDOW_FG,
    "background_color": WINDOW_BG,
}

BUTTON_SETTINGS = {
    "font_height": ENC_SANS_BOLD_FONT_HEIGHT,
    "font_path": ENC_SANS_BOLD_FONT_PATH,
    "padding": 5,
    "depth_finish_thickness": 1,
    "foreground_color": BUTTON_FG,
    "background_color": BUTTON_BG,
}

FILE_MANAGER_CAPTION = (t.editing.change_node_packs_form.file_manager_caption).format(
    NATIVE_FILE_EXTENSION
)

FORM_CAPTION = (t.editing.change_node_packs_form.form_caption).format(
    NATIVE_FILE_EXTENSION
)


OPTION_MENU_DEFAULT_STRING = "Pick a known node pack"


### class definition


class NodePacksSelectionChangeForm(Object2D):
    """Form for changing node packs on any file."""

    def __init__(self):
        """Setup form objects."""
        ###
        self.node_pack_widget_list = List2D()

        ### build widgets
        self.build_form_widgets()

        ### build rect and surf for background

        self.rect = self.widgets.rect.inflate(10, 10)

        self.image = render_rect(*self.rect.size, WINDOW_BG)
        draw_border(self.image)

        ### store a semitransparent object

        self.rect_size_semitransp_obj = Object2D.from_surface(
            surface=render_rect(*self.rect.size, (*CONTRAST_LAYER_COLOR, 130)),
            coordinates_name="center",
            coordinates_value=SCREEN_RECT.center,
        )

        ### assign behaviour
        self.update = empty_function

        ### center form and also append the centering
        ### method as a window resize setup

        self.center_pack_selection_form()

        APP_REFS.window_resize_setups.append(self.center_pack_selection_form)

    def center_pack_selection_form(self):

        diff = Vector2(SCREEN_RECT.center) - self.rect.center

        self.rect.center = SCREEN_RECT.center

        self.widgets.rect.move_ip(diff)

        ###
        npwl = self.node_pack_widget_list

        if npwl:
            npwl.rect.move_ip(diff)

        ### if this form loop is running, ask for screen
        ### preparations to be made

        if hasattr(self, "running") and self.running:
            APP_REFS.draw_after_window_resize_setups = perform_screen_preparations

    def build_form_widgets(self):
        """Build widgets to hold the data for edition."""
        ### create list to hold widgets
        self.widgets = List2D()

        ### define an initial topleft
        topleft = (0, 0)

        ### instantiate a caption for the form

        caption_label = Object2D.from_surface(
            surface=(
                render_text(
                    text=FORM_CAPTION,
                    border_thickness=2,
                    border_color=(TEXT_SETTINGS["foreground_color"]),
                    **TEXT_SETTINGS,
                )
            ),
            coordinates_name="topleft",
            coordinates_value=topleft,
        )

        self.widgets.append(caption_label)

        ### update the topleft to a value a bit below
        ### the bottomleft corner of the widgets already
        ### in the versatile list
        topleft = self.widgets.rect.move(0, 20).bottomleft

        ### instantiate widgets to pick known node packs

        ## known node packs label

        known_node_packs_label = Object2D.from_surface(
            surface=(
                render_text(
                    text="Pick known node packs:",
                    **TEXT_SETTINGS,
                )
            ),
            coordinates_name="topleft",
            coordinates_value=topleft,
        )

        self.widgets.append(known_node_packs_label)

        ## known node packs option menu

        midleft = known_node_packs_label.rect.move(5, 0).midright

        self.node_packs_option_menu = OptionMenu(
            loop_holder=self,
            value=OPTION_MENU_DEFAULT_STRING,
            options=[OPTION_MENU_DEFAULT_STRING] + get_known_node_packs(),
            max_width=700,
            command=self.pick_chosen_node_pack,
            draw_on_window_resize=self.draw,
            coordinates_name="midleft",
            coordinates_value=midleft,
        )

        self.widgets.append(self.node_packs_option_menu)

        ### update the topleft to a value a bit below
        ### the bottomleft corner of the widgets already
        ### in the versatile list
        topleft = self.widgets.rect.move(0, 15).bottomleft

        ### instantiate widgets to add new local node packs

        ## add local node packs label

        add_local_node_packs_label = Object2D.from_surface(
            surface=(
                render_text(
                    text="Add local node pack(s):",
                    **TEXT_SETTINGS,
                )
            ),
            coordinates_name="topleft",
            coordinates_value=topleft,
        )

        self.widgets.append(add_local_node_packs_label)

        ## add local node packs button

        midleft = add_local_node_packs_label.rect.move(5, 0).midright

        add_local_node_packs_button = Object2D.from_surface(
            surface=(
                render_layered_icon(
                    chars=[chr(ordinal) for ordinal in (33, 34)],
                    dimension_name="height",
                    dimension_value=20,
                    colors=[BLACK, (30, 130, 70)],
                    background_width=27,
                    background_height=27,
                    background_color=(40, 40, 50),
                    depth_finish_thickness=1,
                )
            ),
            on_mouse_release=(get_oblivious_callable(self.add_local_node_packs)),
            coordinates_name="midleft",
            coordinates_value=midleft,
        )

        self.widgets.append(add_local_node_packs_button)

        ### update the topleft to a value a bit below
        ### the bottomleft corner of the widgets already
        ### in the versatile list
        topleft = self.widgets.rect.move(0, 15).bottomleft

        ### instantiate widgets to add new installed node packs

        ## add installed node packs label

        add_installed_node_packs_label = Object2D.from_surface(
            surface=(
                render_text(
                    text="Add installed node pack(s):",
                    **TEXT_SETTINGS,
                )
            ),
            coordinates_name="topleft",
            coordinates_value=topleft,
        )

        self.widgets.append(add_installed_node_packs_label)

        ## add installed node packs entry

        midleft = add_installed_node_packs_label.rect.move(5, 0).midright

        self.add_installed_node_packs_entry = StringEntry(
            loop_holder=self,
            value="",
            width=500,
            draw_on_window_resize=self.draw,
            coordinates_name="midleft",
            coordinates_value=midleft,
        )

        self.widgets.append(self.add_installed_node_packs_entry)

        ## add installed node packs button

        midleft = self.add_installed_node_packs_entry.rect.move(5, 0).midright

        add_installed_node_packs_button = Object2D.from_surface(
            surface=(
                render_layered_icon(
                    chars=[chr(78)],
                    dimension_name="height",
                    dimension_value=20,
                    colors=[(30, 210, 70)],
                    background_width=27,
                    background_height=27,
                    background_color=(40, 40, 50),
                    depth_finish_thickness=1,
                )
            ),
            on_mouse_release=(
                get_oblivious_callable(self.add_installed_node_packs_from_entry)
            ),
            coordinates_name="midleft",
            coordinates_value=midleft,
        )

        self.widgets.append(add_installed_node_packs_button)

        ### obtain a topleft from the widgets' bottomleft
        topleft = self.widgets.rect.move(0, 20).bottomleft

        ### instantiate panel to indicate pack list below it

        self.pack_list_panel = Object2D.from_surface(
            surface=render_rect(960, 240, (40, 40, 40)),
            on_mouse_release=self.click_remove_buttons,
            coordinates_name="topleft",
            coordinates_value=topleft,
        )

        self.panel_bg = self.pack_list_panel.image.copy()

        self.widgets.append(self.pack_list_panel)

        ### create and store behaviour for cancelling form
        ### edition (equivalent to setting the form data to
        ### None and setting the 'running' flag to False)

        self.cancel = CallList(
            (
                partial(setattr, self, "form_data", None),
                partial(setattr, self, "running", False),
            )
        )

        ### create, position and store form related buttons

        ## apply changes button

        self.apply_changes_button = Button.from_text(
            text="Apply changes",
            command=self.apply_changes,
            **BUTTON_SETTINGS,
        )

        draw_depth_finish(self.apply_changes_button.image)

        self.apply_changes_button.rect.topright = self.widgets.rect.move(
            0, 20
        ).bottomright

        ## cancel button

        self.cancel_button = Button.from_text(
            text=(t.editing.change_node_packs_form.cancel),
            command=self.cancel,
            **BUTTON_SETTINGS,
        )

        draw_depth_finish(self.cancel_button.image)

        self.cancel_button.rect.midright = self.apply_changes_button.rect.move(
            -5, 0
        ).midleft

        ## store
        self.widgets.extend((self.cancel_button, self.apply_changes_button))

    def pick_chosen_node_pack(self):

        op_menu = self.node_packs_option_menu

        value = op_menu.get()
        op_menu.set(OPTION_MENU_DEFAULT_STRING, False)

        kind, pack_ref = value.split(" : ")

        if kind == "local":
            node_pack = Path(pack_ref)
        else:
            node_pack = pack_ref

        ### add node pack
        self.add_node_packs(node_pack)

    def retrieve_current_node_packs(self):

        ### grab node packs

        all_packs = get_formatted_local_node_packs(
            APP_REFS.source_path
        ) + get_formatted_installed_node_packs(APP_REFS.source_path)

        ### clear the node pack widget list
        self.node_pack_widget_list.clear()

        ### list each node pack
        self.add_node_packs(all_packs)

    def add_local_node_packs(self):
        """"""
        ### select new paths;

        paths = select_paths(
            caption=("Select node to be added to file"),
        )

        if not paths:
            return

        self.add_node_packs(paths)

    def add_installed_node_packs_from_entry(self):

        entry = self.add_installed_node_packs_entry

        content = entry.get()
        entry.set("")

        new_installed_node_packs = [name.strip() for name in content.split(",")]

        self.add_node_packs(new_installed_node_packs)

    def add_node_packs(self, node_packs):

        ### make sure node_packs is a containter

        if not isinstance(node_packs, (list, tuple)):
            node_packs = [node_packs]

        ### reference the node pack widget list locally
        npwl = self.node_pack_widget_list

        ### store whether the list is empty
        is_empty = not npwl

        ###
        for node_pack in node_packs:

            item = List2D()

            remove_button = Object2D.from_surface(
                surface=(
                    render_layered_icon(
                        chars=[chr(66)],
                        dimension_name="height",
                        dimension_value=13,
                        colors=[(202, 0, 0)],
                        background_width=17,
                        background_height=17,
                        background_color=(40, 40, 50),
                        depth_finish_thickness=1,
                    )
                ),
                on_mouse_release=(
                    get_oblivious_callable(partial(self.remove_item, item))
                ),
            )

            prefix = "local" if isinstance(node_pack, Path) else "installed"

            label = Object2D.from_surface(
                surface=(
                    render_text(
                        text=f"{prefix} : {node_pack}",
                        **TEXT_SETTINGS,
                    )
                ),
                node_pack=node_pack,
            )

            ###

            item.append(remove_button)
            item.append(label)

            item.rect.snap_rects_ip(
                retrieve_pos_from="midright",
                assign_pos_to="midleft",
                offset_pos_by=(5, 0),
            )

            ### append the item
            npwl.append(item)

        npwl.rect.snap_rects_ip(
            retrieve_pos_from="bottomleft",
            assign_pos_to="topleft",
            offset_pos_by=(0, 5),
        )

        panel_rect = self.pack_list_panel.rect

        if is_empty and npwl:

            npwl.rect.topleft = panel_rect.move(5, 5).topleft

            if item.rect.bottom > panel_rect.bottom:
                y_diff = panel_rect.bottom - item.rect.bottom
                npwl.rect.move_ip(0, y_diff)

            elif item.rect.top < panel_rect.top:
                y_diff = panel_rect.top - item.rect.top
                npwl.rect.move_ip(0, y_diff)

    def remove_item(self, item):

        ### reference node pack widget list locally
        npwl = self.node_pack_widget_list

        ###

        for index, current_item in enumerate(npwl):

            if current_item is item:
                break

        npwl.pop(index)

        ###

        if npwl:

            npwl.rect.snap_rects_ip(
                retrieve_pos_from="bottomleft",
                assign_pos_to="topleft",
                offset_pos_by=(0, 5),
            )

            top = self.pack_list_panel.rect.move(0, 5).top
            npwl_top = npwl.rect.top

            if npwl_top > top:
                y_diff = top - npwl_top
                npwl.rect.move_ip(0, y_diff)

    def present_change_node_packs_form(self):
        """Allow user to change node packs on any file."""
        ### perform screen preparations
        perform_screen_preparations()

        ###
        self.retrieve_current_node_packs()

        ### update values on option menu

        self.node_packs_option_menu.reset_value_and_options(
            value=OPTION_MENU_DEFAULT_STRING,
            options=[OPTION_MENU_DEFAULT_STRING] + get_known_node_packs(),
            custom_command=False,
        )

        ### loop until running attribute is set to False

        self.running = True
        self.loop_holder = self

        while self.running:

            maintain_fps(FPS)

            watch_window_size()

            ### put the handle_input/update/draw method
            ### execution inside a try/except clause
            ### so that the SwitchLoopException
            ### thrown when focusing in and out of some
            ### widgets is caught; also, you don't
            ### need to caught the QuitAppException,
            ### since it is caught in the main loop

            try:

                self.loop_holder.handle_input()
                self.loop_holder.update()
                self.loop_holder.draw()

            except SwitchLoopException as err:

                ## use the loop holder in the err
                ## attribute of same name
                self.loop_holder = err.loop_holder

        ### draw a semitransparent object over the
        ### form, so it appears as if unhighlighted
        self.rect_size_semitransp_obj.draw()

    def handle_input(self):
        """Process events from event queue."""
        for event in get_events():

            if event.type == QUIT:
                raise QuitAppException

            elif event.type == KEYUP:

                if event.key == K_ESCAPE:
                    self.cancel()

                elif event.key in (K_RETURN, K_KP_ENTER):
                    self.apply_changes()

            elif event.type == KEYDOWN:

                if event.key == K_UP:
                    self.scroll_up()

                elif event.key == K_DOWN:
                    self.scroll_down()

            elif event.type == MOUSEBUTTONDOWN:

                if event.button == 1:

                    if self.rect.collidepoint(event.pos):
                        self.on_mouse_click(event)

            elif event.type == MOUSEBUTTONUP:

                if event.button == 1:

                    if self.rect.collidepoint(event.pos):
                        self.on_mouse_release(event)

                elif event.button == 4:
                    self.scroll_up()

                elif event.button == 5:
                    self.scroll_down()

    # XXX in the future, maybe a "Reset" button would be
    # nice

    def mouse_method_on_collision(self, method_name, event):
        """Invoke inner widget if it collides with mouse.

        Parameters
        ==========

        method_name (string)
            name of method to be called on the colliding
            widget.
        event (event object of MOUSEBUTTON[...] type)
            it is required in order to comply with
            mouse interaction protocol used; here we
            use it to retrieve the position of the
            mouse when the first button was released.

            Check pygame.event module documentation on
            pygame website for more info about this event
            object.
        """
        ### retrieve position from attribute in event obj
        mouse_pos = event.pos

        ### search for a colliding obj among the widgets

        for obj in self.widgets:

            if obj.rect.collidepoint(mouse_pos):
                colliding_obj = obj
                break

        else:
            return

        ### if you manage to find a colliding obj, execute
        ### the requested method on it, passing along the
        ### received event

        try:
            method = getattr(colliding_obj, method_name)
        except AttributeError:
            pass
        else:
            method(event)

    on_mouse_click = partialmethod(
        mouse_method_on_collision,
        "on_mouse_click",
    )

    on_mouse_release = partialmethod(
        mouse_method_on_collision,
        "on_mouse_release",
    )

    def click_remove_buttons(self, event):
        """Remove node pack from list if remove button was clicked.

        Parameters
        ==========
        event (pygame.event.Event of pygame.MOUSEBUTTONUP
               type)

            Check pygame.event module documentation on
            pygame website for more info about this event
            object.
        """
        mouse_pos = event.pos

        for remove_button, _ in self.node_pack_widget_list:

            if remove_button.rect.collidepoint(mouse_pos):

                remove_button.on_mouse_release(event)
                break

    def scroll(self, dy):

        npwl = self.node_pack_widget_list
        if not npwl:
            return

        npwl_rect = npwl.rect
        panel_rect = self.pack_list_panel.rect

        if npwl_rect.height <= panel_rect.height:
            return

        if dy > 0:

            if npwl_rect.top + dy > panel_rect.top:
                dy = panel_rect.top - npwl_rect.top

        elif dy < 0:

            if npwl_rect.bottom + dy < panel_rect.bottom:
                dy = panel_rect.bottom - npwl_rect.bottom

        npwl_rect.move_ip(0, dy)

    scroll_up = partialmethod(scroll, 30)
    scroll_down = partialmethod(scroll, -30)

    def apply_changes(self):
        """Treat data and, if valid, perform changes."""
        current_packs = set(
            get_formatted_local_node_packs(APP_REFS.source_path)
            + get_formatted_installed_node_packs(APP_REFS.source_path)
        )

        final_selection = {item[1].node_pack for item in self.node_pack_widget_list}

        if current_packs == final_selection:

            create_and_show_dialog(
                "There is no change to apply, the node packs selected"
                " already correspond to the current node pack selection."
            )

            return

        ### check existence of orphaned nodes

        existing_node_pack_names = {
            node.id: node.data["script_id"][0]
            for node in APP_REFS.gm.nodes
            if "script_id" in node.data
        }

        final_node_pack_names = {
            pack.name if isinstance(pack, Path) else pack for pack in final_selection
        }

        orphaned_nodes = {
            node_id: node_pack_name
            for node_id, node_pack_name in existing_node_pack_names.items()
            if node_pack_name not in final_node_pack_names
        }

        if orphaned_nodes:

            orphan_node_ids = tuple(orphaned_nodes)

            create_and_show_dialog(
                "Can't proceed with operation, because there are nodes"
                " in the node layout still using some of the packs to be"
                f" removed: the nodes of ids {orphan_node_ids}"
            )

            return

        ### separate node packs

        local_node_packs = [
            str(node_pack)
            for node_pack in final_selection
            if isinstance(node_pack, Path)
        ]

        installed_node_packs = [
            node_pack for node_pack in final_selection if isinstance(node_pack, str)
        ]

        ### try loading node packs

        try:
            load_scripts(local_node_packs, installed_node_packs)

        except Exception as err:

            create_and_show_dialog(f"Error message: {err}")

            return

        ###
        APP_REFS.data["node_packs"] = local_node_packs
        APP_REFS.data["installed_node_packs"] = installed_node_packs

        ###

        APP_REFS.data["node_packs"] = local_node_packs = [
            str(node_pack)
            for node_pack in final_selection
            if isinstance(node_pack, Path)
        ]

        APP_REFS.data["installed_node_packs"] = installed_node_packs = [
            node_pack for node_pack in final_selection if isinstance(node_pack, str)
        ]

        ### rebuild canvas popup menu
        APP_REFS.window_manager.create_canvas_popup_menu()

        ###
        indicate_unsaved()

        ###
        set_status_message("Changed selected node pack(s)")

        ### trigger exiting the form by setting special
        ### flag to False
        self.running = False

    def draw(self):
        """Draw itself and widgets.

        Extends Object2D.draw.
        """
        ### draw a cached copy of the screen over itself
        draw_cached_screen_state()

        ### draw form background (self.image)
        super().draw()

        ### draw clean panel and draw its items over it (if any)

        panel = self.pack_list_panel
        panel.image.blit(self.panel_bg, (0, 0))

        for pack_objs in self.node_pack_widget_list:

            for obj in pack_objs:
                obj.draw_relative(panel)

        draw_border(panel.image, (235, 235, 235))

        ### draw all widgets
        self.widgets.draw()

        ### update screen (pygame.display.update)
        update()


present_change_node_packs_form = (
    NodePacksSelectionChangeForm().present_change_node_packs_form
)


### utility function


def perform_screen_preparations():

    ### dim the screen
    blit_on_screen(UNHIGHLIGHT_SURF_MAP[SCREEN_RECT.size], (0, 0))

    ### update the copy of the screen as it is now
    cache_screen_state()
