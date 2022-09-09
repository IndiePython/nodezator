"""Facility for widget setup loop holder."""

### local imports

from itertools import chain
from functools import partial, partialmethod


### third-party imports

from pygame import (
    QUIT,
    KEYUP,
    K_ESCAPE,
    K_RETURN,
    K_KP_ENTER,
    MOUSEBUTTONDOWN,
    MOUSEBUTTONUP,
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
)

from ...our3rdlibs.behaviour import watch_window_size

from ...our3rdlibs.button import Button

from ...classes2d.single import Object2D

from ...textman.render import render_text

from ...surfsman.draw import draw_border
from ...surfsman.render import render_rect

from ...widget.optionmenu.main import OptionMenu

from ...loopman.exception import (
    QuitAppException,
    SwitchLoopException,
)

from ...fontsman.constants import ENC_SANS_BOLD_FONT_HEIGHT

from ...graphman.widget.utils import WIDGET_CLASS_MAP

from ...colorsman.colors import (
    BUTTON_FG,
    BUTTON_BG,
    WINDOW_FG,
    WINDOW_BG,
    CONTRAST_LAYER_COLOR,
)

from ...dialog import create_and_show_dialog

## class extension
from .subforms import SubformCreation


### constants

## font height
FONT_HEIGHT = ENC_SANS_BOLD_FONT_HEIGHT

## availabel widgets

# use the keys from the widget class map, removing some
# of them

AVAILABLE_WIDGETS = list(WIDGET_CLASS_MAP.keys())

for key in ("default_holder", "option_menu", "option_tray", "sorting_button"):
    AVAILABLE_WIDGETS.remove(key)

# also add some new ones, which actually are variations
# of some of the keys we just removed

AVAILABLE_WIDGETS.extend(
    (
        "option_menu_with_strings",
        "option_menu_with_intfloats",
        "option_tray_with_strings",
        "option_tray_with_intfloats",
        "sorting_button_with_strings",
        "sorting_button_with_intfloats",
    )
)

# also sort the list
AVAILABLE_WIDGETS.sort()


### class definition


### XXX
### you must decide what to do about the list widget
### increasing its height; should the widget picker
### contents be scrollable? ponder


class WidgetPicker(Object2D, SubformCreation):
    """Form to define new widget and its settings."""

    def __init__(self):
        """Build widget structure for the form."""
        ### build surf and rect for background

        self.image = render_rect(360, 540, WINDOW_BG)
        draw_border(self.image)

        self.rect = self.image.get_rect()

        ### create and store caption

        self.caption = Object2D.from_surface(
            surface=(
                render_text(
                    text=(t.graph_manager.widget_picker.caption),
                    font_height=17,
                    padding=5,
                    foreground_color=WINDOW_FG,
                    border_thickness=2,
                    border_color=WINDOW_FG,
                )
            ),
            coordinates_name="topleft",
            coordinates_value=(self.rect.move(10, 10).topleft),
        )

        ### build option menu
        self.build_option_menu()

        ### build widget subforms
        self.build_widget_subforms()

        ### assign behaviour for exiting the form
        ### (equivalent to setting the running flag to
        ### False, which triggers the exiting of the
        ### loop)
        self.exit_form = partial(setattr, self, "running", False)

        ### create and store form related buttons

        self.cancel_button = Button.from_text(
            text=(t.graph_manager.widget_picker.cancel),
            padding=5,
            foreground_color=BUTTON_FG,
            background_color=BUTTON_BG,
            depth_finish_thickness=1,
            command=self.exit_form,
        )

        self.submit_button = Button.from_text(
            text=(t.graph_manager.widget_picker.submit),
            padding=5,
            foreground_color=BUTTON_FG,
            background_color=BUTTON_BG,
            depth_finish_thickness=1,
            command=self.submit_data,
        )

        ### assign subform according to current
        ### kind of widget selected
        self.update_widget_subform()

        ### center widget picker form and append centering
        ### method as a window resize setup

        self.center_widget_picker_form()

        APP_REFS.window_resize_setups.append(self.center_widget_picker_form)

    def center_widget_picker_form(self):

        diff = Vector2(SCREEN_RECT.center) - self.rect.center

        self.rect.center = SCREEN_RECT.center

        self.caption.rect.move_ip(diff)
        self.widget_kind_options.rect.move_ip(diff)

        self.cancel_button.rect.move_ip(diff)
        self.submit_button.rect.move_ip(diff)

        for subform in self.subform_map.values():
            subform.rect.move_ip(diff)

        ### store a semitransparent object the size of
        ### the screen

        self.semitransp_obj = Object2D.from_surface(
            render_rect(*SCREEN_RECT.size, (*CONTRAST_LAYER_COLOR, 130))
        )

    def build_option_menu(self):
        """Build option menu to pick the kind of widget."""
        ### define arguments for option menu instantiation

        ## a (default) value
        value = "string_entry"

        ## position related arguments

        coordinates_name = "topleft"
        coordinates_value = self.caption.rect.move(0, 10).bottomleft

        ## command
        command = self.update_widget_subform

        ### instantiate option menu

        self.widget_kind_options = OptionMenu(
            loop_holder=self,
            value=value,
            options=AVAILABLE_WIDGETS,
            max_width=230,
            font_height=FONT_HEIGHT,
            draw_on_window_resize=self.draw,
            coordinates_name=coordinates_name,
            coordinates_value=coordinates_value,
            command=command,
        )

    def build_widget_subforms(self):
        """Build subform with specific widget settings."""
        ### create and store map to hold each subform
        self.subform_map = {}

        ### create subforms for each option of widget

        self.create_string_entry_subform()
        self.create_literal_entry_subform()
        self.create_int_float_entry_subform()
        self.create_checkbutton_subform()
        self.create_colorbutton_subform()

        self.create_sorting_button_subform_with_strings()
        self.create_sorting_button_subform_with_intfloats()

        self.create_text_display_subform()
        self.create_literal_display_subform()

        self.create_pathpreview_subform()
        self.create_textpreview_subform()
        self.create_imagepreview_subform()
        self.create_fontpreview_subform()
        self.create_audiopreview_subform()
        self.create_videopreview_display_subform()

        self.create_option_menu_subform_with_strings()
        self.create_option_menu_subform_with_intfloats()
        self.create_option_tray_subform_with_strings()
        self.create_option_tray_subform_with_intfloats()

    def update_widget_subform(self):
        """Change the subform according to widget kind."""
        ### retrieve value from widget kind option menu
        value = self.widget_kind_options.get()

        ### use the value as key to retrieve the subform to
        ### be used for the widget_subform attribute
        self.widget_subform = self.subform_map[value]

        ### reposition form elements
        self.reposition_form_elements()

    def reposition_form_elements(self):
        """Position form buttons below widget subform."""
        ### align subform below widget kind option menu
        self.widget_subform.rect.topleft = self.widget_kind_options.rect.move(
            0, 10
        ).bottomleft

        ### align cancel button left with the self.rect
        ### left, with a little offset
        self.cancel_button.rect.left = self.rect.move(5, 0).left

        ### align cancel button top with the widget subform
        ### bottom, then offset it a little

        self.cancel_button.rect.top = self.widget_subform.rect.bottom
        self.cancel_button.rect.y += 10

        ### then align the submit button topleft with the
        ### cancel button topright just a little bit more
        ### to the right
        self.submit_button.rect.topleft = self.cancel_button.rect.move(10, 0).topright

    def pick_widget(self):
        """Display form; return widget instantiation data."""
        self.widget_data = None

        self.semitransp_obj.draw()

        ### loop until running attribute is set to False

        self.running = True

        ## TODO it seems the loop holder doesn't need
        ## to be referenced in an attribute here, but can
        ## be in a local variable, so make the change;
        self.loop_holder = self

        while self.running:

            maintain_fps(FPS)

            watch_window_size()

            ### put the handle_input/update/draw method
            ### execution inside a try/except clause
            ### so that the SwitchLoopException
            ### thrown when focusing in and out of some
            ### widgets is caught; also, you don't
            ### need to catch the QuitAppException,
            ### since it is caught in the main loop

            try:

                self.loop_holder.handle_input()
                self.loop_holder.update()
                self.loop_holder.draw()

            except SwitchLoopException as err:

                ## use the loop holder in the err
                ## attribute of same name
                self.loop_holder = err.loop_holder

        return self.widget_data

    def handle_input(self):
        """Process events from event queue."""
        for event in get_events():

            if event.type == QUIT:
                raise QuitAppException

            elif event.type == KEYUP:

                if event.key == K_ESCAPE:
                    self.exit_form()

                elif event.key in (K_RETURN, K_KP_ENTER):
                    self.submit_data()

            elif event.type == MOUSEBUTTONDOWN:

                if event.button == 1:

                    if self.rect.collidepoint(event.pos):
                        self.on_mouse_click(event)

            elif event.type == MOUSEBUTTONUP:

                if event.button == 1:

                    if self.rect.collidepoint(event.pos):
                        self.on_mouse_release(event)

    # XXX in the future a "Reset" button would be nice

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

        ### chain all widgets together

        other_widgets = (
            self.widget_kind_options,
            self.cancel_button,
            self.submit_button,
        )

        objs = chain(self.widget_subform, other_widgets)

        for obj in objs:

            if obj.rect.collidepoint(mouse_pos):

                colliding_obj = obj
                break

        else:
            colliding_obj = None

        if colliding_obj:

            try:
                method = getattr(colliding_obj, method_name)

            except AttributeError:
                pass
            else:
                method(event)

    on_mouse_click = partialmethod(mouse_method_on_collision, "on_mouse_click")

    on_mouse_release = partialmethod(mouse_method_on_collision, "on_mouse_release")

    def submit_data(self):
        """Submit form data.

        Works by retrieving the data from the widgets,
        assigning it to a dictionary, store it in the
        "widget_data" attribute and exit the form by
        setting the running flag to False.
        """
        ### create dictionary
        widget_data = {}

        ### retrieve the widget name
        widget_name = self.widget_kind_options.get()

        ### admin task: if widget name starts with
        ### 'option_menu', 'option_tray' or
        ### 'sorting_button', change the name to
        ### only contain that substring

        for substring in (
            "option_menu",
            "option_tray",
            "sorting_button",
        ):

            if widget_name.startswith(substring):

                widget_name = substring
                break

        ### store the widget name in the widget data
        widget_data["widget_name"] = widget_name

        ### create a new dictionary and store in the
        ### "kwargs" key and also in a local variable
        kwargs = widget_data["widget_kwargs"] = {}

        ### populate the widget_kwargs dictionary with data
        ### from each widget in the subform which have
        ### the needed data

        for widget in self.widget_subform:

            ## check whether needed method/attribute
            ## are present
            try:
                widget.get, widget.name

            ## if not, just pass (it is probably just
            ## a widget to display information for the
            ## user, like a label)
            except AttributeError:
                pass

            ## otherwise, use the tested method/attribute
            ## to fill the widget_kwargs dict
            else:
                kwargs[widget.name] = widget.get()

        ### if values received are ok, store the
        ### widget_data dict in an attribute and exit the
        ### form

        if self.is_widget_data_ok(widget_data):

            self.widget_data = widget_data
            self.exit_form()

    def is_widget_data_ok(self, widget_data):
        """Return True if widget data won't cause errors.

        Works by checking whether instantiating a widget
        using the data provided will raise an error or
        not and returning True if no exception is raised.
        """
        ### retrieve widget class using the widget
        ### name from the parameter widget metadata

        widget_name = widget_data["widget_name"]
        widget_cls = WIDGET_CLASS_MAP[widget_name]

        ### retrieve the keyword arguments
        kwargs = widget_data["widget_kwargs"]

        ### try instantiating the widget
        try:
            widget = widget_cls(**kwargs)

        ### if the instantiation fails, inform the user of
        ### such error using a dialogue

        except Exception as err:

            msg = (
                "It seems the values provided for the widget"
                " aren't valid. If you wish to proceed,"
                " please, fix the values. A '{}' exception"
                " with the following message was issued: {}"
            ).format(type(err).__name__, str(err))

            create_and_show_dialog(msg)

        ### otherwise return True
        else:
            return True

    def update(self):
        """Empty method.

        It exists so that this object is considered a
        loop holder (that is, it must have handle_input,
        update, and draw methods).
        """

    def draw(self):
        """Draw itself and widgets.

        Extends Object2D.draw.
        """
        super().draw()

        self.caption.draw()

        self.widget_kind_options.draw()

        for obj in self.widget_subform:
            obj.draw()

        self.cancel_button.draw()
        self.submit_button.draw()

        update()  # pygame.display.update


pick_widget = WidgetPicker().pick_widget
