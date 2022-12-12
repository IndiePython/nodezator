"""Form for changing node packs on existing file."""

### standard library imports

from pathlib import Path

from functools import partial, partialmethod

from collections import defaultdict


### third-party imports

from pygame import (
    QUIT,
    MOUSEBUTTONDOWN,
    MOUSEBUTTONUP,
    KEYUP,
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

from ...ourstdlibs.behaviour import empty_function

from ...ourstdlibs.pyl import load_pyl, save_pyl

from ...our3rdlibs.button import Button

from ...our3rdlibs.behaviour import watch_window_size

from ...classes2d.single import Object2D
from ...classes2d.collections import List2D

from ...fontsman.constants import (
    ENC_SANS_BOLD_FONT_HEIGHT,
    ENC_SANS_BOLD_FONT_PATH,
)

from ...textman.render import render_text
from ...textman.label.main import Label

from ...surfsman.cache import UNHIGHLIGHT_SURF_MAP

from ...surfsman.draw import draw_border, draw_depth_finish
from ...surfsman.render import render_rect

from ...loopman.exception import (
    QuitAppException,
    SwitchLoopException,
)

from ...graphman.exception import NODE_PACK_ERRORS

from ...colorsman.colors import (
    CONTRAST_LAYER_COLOR,
    WINDOW_FG,
    WINDOW_BG,
    BUTTON_FG,
    BUTTON_BG,
)


## widget
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

FILE_MANAGER_CAPTION = (t.editing.rename_node_packs_form.file_manager_caption).format(
    NATIVE_FILE_EXTENSION
)

FORM_CAPTION = (t.editing.rename_node_packs_form.form_caption).format(
    NATIVE_FILE_EXTENSION
)


### class definition


class NodePacksRenamingChangeForm(Object2D):
    """Form for changing node packs on another file."""

    def __init__(self):
        """Setup form objects."""
        ### build surf and rect for background

        self.image = render_rect(500, 305, WINDOW_BG)
        draw_border(self.image)

        self.rect = self.image.get_rect()

        ### store a semitransparent object

        self.rect_size_semitransp_obj = Object2D.from_surface(
            surface=render_rect(*self.rect.size, (*CONTRAST_LAYER_COLOR, 130)),
            coordinates_name="center",
            coordinates_value=SCREEN_RECT.center,
        )

        ###
        self.chosen_filepath = Path(".")

        ###
        self.subform_objects = List2D()

        ### build widgets
        self.build_form_widgets()

        ### assign behaviour
        self.update = empty_function

        ### center form and append centering method as
        ### a window resize setup

        self.center_pack_renaming_form()

        APP_REFS.window_resize_setups.append(self.center_pack_renaming_form)

    def center_pack_renaming_form(self):

        diff = Vector2(SCREEN_RECT.center) - self.rect.center

        self.rect.center = SCREEN_RECT.center

        self.widgets.rect.move_ip(diff)

    def build_form_widgets(self):
        """Build widgets to hold the data for edition."""
        ### create list to hold widgets
        self.widgets = List2D()

        ### define an initial topleft relative to the
        ### topleft corner of the form 'rect'
        topleft = self.rect.move(5, 5).topleft

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

        ### instantiate widgets for filepath

        ## filepath choose button

        self.choose_filepath_button = Object2D.from_surface(
            surface=render_text(
                text=(t.editing.rename_node_packs_form.choose_filepath),
                **BUTTON_SETTINGS,
            ),
            coordinates_name="topleft",
            coordinates_value=topleft,
        )

        self.choose_filepath_button.on_mouse_release = self.choose_filepath

        self.widgets.append(self.choose_filepath_button)

        ## chosen filepath label

        midleft = self.choose_filepath_button.rect.move(5, 0).midright

        self.chosen_filepath_label = Label(
            text=(t.editing.rename_node_packs_form.no_filepath_chosen),
            name="filepath",
            max_width=345,
            ellipsis_at_end=False,
            coordinates_name="midleft",
            coordinates_value=midleft,
            **TEXT_SETTINGS,
        )

        self.widgets.append(self.chosen_filepath_label)

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

        ## submit button

        self.submit_button = Button.from_text(
            text=(t.editing.rename_node_packs_form.submit),
            command=self.submit_form,
            **BUTTON_SETTINGS,
        )

        draw_depth_finish(self.submit_button.image)

        self.submit_button.rect.bottomright = self.rect.move(-10, -10).bottomright

        ## cancel button

        self.cancel_button = Button.from_text(
            text=(t.editing.rename_node_packs_form.cancel),
            command=self.cancel,
            **BUTTON_SETTINGS,
        )

        draw_depth_finish(self.cancel_button.image)

        self.cancel_button.rect.midright = self.submit_button.rect.move(-5, 0).midleft

        ## store

        self.widgets.extend((self.cancel_button, self.submit_button))

    def choose_filepath(self, event):
        """Pick new path and update label using it.

        Parameters
        ==========
        event (pygame.event.Event of pygame.MOUSEBUTTONDOWN
               type)
          although not used, it is required in order to
          comply with protocol used;

          Check pygame.event module documentation on
          pygame website for more info about this event
          object.
        """
        ### pick new path

        paths = select_paths(caption=FILE_MANAGER_CAPTION)

        ### if paths were given, a single one, should be
        ### used as the new filepath;
        ###
        ### update the label using the given value

        if paths:

            self.chosen_filepath = paths[0]

            self.chosen_filepath_label.set(str(self.chosen_filepath))

            self.build_renaming_subform()

    ### TODO build subform (two columns, where first has
    ### current names as labels and second has string
    ### entries wherein to type the new names)

    def build_renaming_subform(self):

        if not self.chosen_filepath.is_file():
            return

        elif not self.chosen_filepath.suffix == ".ndz":
            return

        try:
            data = self.data = load_pyl(self.chosen_filepath)

        except Exception as err:

            print(err)
            return

        else:

            node_packs = data.get("node_packs", [])

            if not node_packs:

                create_and_show_dialog(
                    "The file hasn't node packs linked for" " us to rename."
                )

                return

            node_packs = self.node_packs = (
                [Path(node_packs)]
                if isinstance(node_packs, str)
                else [Path(path) for path in node_packs]
            )

            node_packs_names = [path.name for path in node_packs]

            ###
            self.current_name_labels = List2D(
                Object2D.from_surface(
                    surface=(
                        render_text(
                            text=name,
                            **TEXT_SETTINGS,
                        )
                    ),
                    name=name,
                )
                for name in node_packs_names
            )

            self.new_name_entries = List2D(
                StringEntry(
                    value=f"new_name{index}",
                    loop_holder=self,
                    draw_on_window_resize=self.draw,
                )
                for index, _ in enumerate(node_packs_names)
            )

            self.current_name_labels.rect.snap_rects_ip(
                retrieve_pos_from="bottomright",
                assign_pos_to="topright",
                offset_pos_by=(0, 5),
            )

            for label, entry in zip(self.current_name_labels, self.new_name_entries):

                entry.rect.midleft = label.rect.move(5, 0).midright

            self.subform_objects.extend(
                self.current_name_labels + self.new_name_entries
            )

            self.subform_objects.rect.topleft = self.choose_filepath_button.rect.move(
                0, 5
            ).bottomleft

            self.widgets.extend(self.subform_objects)

            ###

            self.node_pack_name_to_ids = node_pack_name_to_ids = defaultdict(list)

            for node_id, node_data in data.get("nodes", {}).items():

                if "script_id" not in node_data:
                    continue

                node_pack_name = node_data["script_id"][0]

                (node_pack_name_to_ids[node_pack_name].append(node_id))

    def present_rename_node_packs_form(self):
        """Allow user to rename node packs on any file."""
        ### draw semi-transparent object so screen behind
        ### form appears as if unhighlighted

        blit_on_screen(UNHIGHLIGHT_SURF_MAP[SCREEN_RECT.size], (0, 0))

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
                    self.submit_form()

            elif event.type == MOUSEBUTTONDOWN:

                if event.button == 1:

                    if self.rect.collidepoint(event.pos):
                        self.on_mouse_click(event)

            elif event.type == MOUSEBUTTONUP:

                if event.button == 1:

                    if self.rect.collidepoint(event.pos):
                        self.on_mouse_release(event)

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

    def submit_form(self):
        """Treat data and, if valid, perform changes."""
        if not self.subform_objects:
            return

        for label, entry in zip(self.current_name_labels, self.new_name_entries):

            new_name = entry.get()

            if not new_name:
                return
            elif label.name == new_name:
                return

        nodes_data = self.data.get("nodes", {})
        new_node_packs = []

        for label, entry in zip(self.current_name_labels, self.new_name_entries):

            old_name = label.name
            new_name = entry.get()

            ###
            old_path = next(path for path in self.node_packs if path.name == old_name)

            new_path = old_path.parent / new_name
            new_node_packs.append(new_path)

            ###

            ids = self.node_pack_name_to_ids[old_name]

            for node_id in ids:

                node_data = nodes_data[node_id]

                _, categ_name, script_name = node_data["script_id"]

                node_data["script_id"] = (new_name, categ_name, script_name)

        self.data["node_packs"] = (
            str(new_node_packs[0])
            if len(new_node_packs) == 1
            else [str(path) for path in new_node_packs]
        )

        ###

        save_pyl(self.data, self.chosen_filepath)

        ###

        for obj in self.subform_objects:
            self.widgets.remove(obj)

        self.subform_objects.clear()

        ###

        ### trigger exiting the form by setting special
        ### flag to False
        self.running = False

    def draw(self):
        """Draw itself and widgets.

        Extends Object2D.draw.
        """
        ### draw self (background)
        super().draw()

        ### draw widgets
        self.widgets.draw()

        ### update screen (pygame.display.update)
        update()


present_rename_node_packs_form = (
    NodePacksRenamingChangeForm().present_rename_node_packs_form
)
