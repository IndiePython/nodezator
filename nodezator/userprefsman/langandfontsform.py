"""Form for lang and font preferences editing."""

### standard library imports

from functools import partialmethod

from itertools import chain


### third-party imports

from pygame.locals import (
    QUIT,
    MOUSEBUTTONDOWN,
    MOUSEBUTTONUP,
    KEYUP,
    K_ESCAPE,
    K_RETURN,
    K_KP_ENTER,
)


### local imports

from ..pygamesetup import SERVICES_NS, SCREEN_RECT, blit_on_screen

from ..config import APP_REFS, DEFAULT_USER_PREFS, USER_PREFS

from ..translatedtext import TRANSLATIONS

from .main import CONFIG_FILEPATH

from .validation import (
    AVAILABLE_LOCALES,
    GENERAL_FONT_HEIGHT_RANGE,
    MONO_FONT_HEIGHT_RANGE,
    FONT_KIND_OPTIONS,
    validate_prefs_data,
)

from ..dialog import create_and_show_dialog

from ..ourstdlibs.pyl import save_pyl

from ..ourstdlibs.behaviour import (
    empty_function,
    get_oblivious_callable,
)

from ..our3rdlibs.button import Button

from ..our3rdlibs.behaviour import set_status_message

from ..classes2d.single import Object2D
from ..classes2d.collections import List2D

from ..textman.render import render_text

from ..surfsman.cache import UNHIGHLIGHT_SURF_MAP

from ..surfsman.draw import draw_border, draw_depth_finish

from ..surfsman.render import render_rect

from ..loopman.main import LoopHolder

from ..widget.intfloatentry.main import IntFloatEntry

from ..widget.optionmenu.main import OptionMenu

from ..widget.pathpreview.font import FontPreview

from ..widget.systemfontsoptionmenu import SystemFontsOptionMenu

from ..widget.defaultholder import DefaultHolder


from ..colorsman.colors import (
    CONTRAST_LAYER_COLOR,
    BUTTON_FG,
    BUTTON_BG,
    WINDOW_FG,
    WINDOW_BG,
)



### translations

t = TRANSLATIONS.language_and_fonts_form
general_t = TRANSLATIONS.general

### constants

TEXT_SETTINGS = {
    'font_height': APP_REFS.general_font_height,
    'font_key': APP_REFS.general_font_key,
    'padding': 5,
    'foreground_color': WINDOW_FG,
    'background_color': WINDOW_BG,
}

BUTTON_SETTINGS = {
    'font_height': APP_REFS.general_font_height,
    'font_key': APP_REFS.general_font_key,
    'padding': 5,
    'depth_finish_thickness': 1,
    'foreground_color': BUTTON_FG,
    'background_color': BUTTON_BG,
}


class UserPreferencesLanguageAndFontsForm(Object2D, LoopHolder):
    """Form for editing user preferences for language and fonts."""

    def __init__(self):
        """Setup form objects."""
        ### build widgets
        self.build_form_widgets()

        ### assign rect and surf for background

        self.rect = self.widgets.rect.inflate(20, 20)
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

        ### center edition form and append centering
        ### method as a window resize setup

        self.center_preferences_form()

        APP_REFS.window_resize_setups.append(self.center_preferences_form)

    def center_preferences_form(self):
        self.rect.center = self.widgets.rect.center = SCREEN_RECT.center

    def build_form_widgets(self):
        """Build widgets to hold settings for edition."""
        ### create list to hold widgets
        widgets = self.widgets = List2D()

        ### instantiate a caption for the form

        caption_label = Object2D.from_surface(
            surface=(
                render_text(
                    text=t.caption,
                    border_thickness=2,
                    border_color=(TEXT_SETTINGS["foreground_color"]),
                    **TEXT_SETTINGS,
                )
            ),
        )

        widgets.append(caption_label)

        ### instantiate labels

        labels = List2D(


            Object2D.from_surface(
                render_text(text=f"{label_text}:", **TEXT_SETTINGS)
            )

            for label_text in (
                t.language,
                t.general_font_height,
                t.mono_font_height,
                t.general_font,
                t.mono_font,
            )
        )


        labels.rect.snap_rects_ip(
            retrieve_pos_from='bottomleft',
            assign_pos_to='topleft',
            offset_pos_by=(0, 5),
        )

        labels.rect.topleft = widgets.rect.move(0, 5).bottomleft

        widgets.extend(labels)

        ### create specific widgets to edit user preferences

        lang_option_menu = (

            OptionMenu(
                loop_holder=self,
                options=AVAILABLE_LOCALES,
                value=USER_PREFS['LOCALE'],
                draw_on_window_resize=self.draw,
                name='LOCALE',
            )

        )

        general_font_size_intfloat_entry = (

            IntFloatEntry(
                loop_holder=self,
                value=USER_PREFS['GENERAL_FONT_HEIGHT'],
                name='GENERAL_FONT_HEIGHT',
                width=90,
                min_value=min(GENERAL_FONT_HEIGHT_RANGE),
                max_value=max(GENERAL_FONT_HEIGHT_RANGE),
                numeric_classes_hint='int',
                allow_none=False,
                draw_on_window_resize=self.draw,
            )

        )

        mono_font_size_intfloat_entry = (

            IntFloatEntry(
                loop_holder=self,
                value=USER_PREFS['MONO_FONT_HEIGHT'],
                name='MONO_FONT_HEIGHT',
                min_value=min(MONO_FONT_HEIGHT_RANGE),
                max_value=max(MONO_FONT_HEIGHT_RANGE),
                width=90,
                numeric_classes_hint='int',
                allow_none=False,
                draw_on_window_resize=self.draw,
            )

        )

        general_font_kind_option_menu = self.gen_font_option = (

            OptionMenu(
                loop_holder=self,
                options=FONT_KIND_OPTIONS,
                value=USER_PREFS['GENERAL_FONT_KIND'],
                name='GENERAL_FONT_KIND',
                draw_on_window_resize=self.draw,
                command=self.switch_general_font_use_widget,
            )

        )

        mono_font_kind_option_menu = self.mono_font_option = (

            OptionMenu(
                loop_holder=self,
                options=FONT_KIND_OPTIONS,
                value=USER_PREFS['MONO_FONT_KIND'],
                name='MONO_FONT_KIND',
                draw_on_window_resize=self.draw,
                command=self.switch_mono_font_use_widget,
            )

        )

        self.prefs_widgets = prefs_widgets = (

            List2D(

                (
                    lang_option_menu,
                    general_font_size_intfloat_entry,
                    mono_font_size_intfloat_entry,
                    general_font_kind_option_menu,
                    mono_font_kind_option_menu,
                )

            )

        )

        right = max(label.rect.right for label in labels) + 5

        for pref_widget, label in zip(prefs_widgets, labels):
            pref_widget.rect.midleft = (right, label.rect.centery)

        widgets.extend(prefs_widgets)

        ###

        self.general_font_widget_map = general_font_widget_map = {}
        self.mono_font_widget_map = mono_font_widget_map = {}

        for font_kind, value_key, widget_map in (

            (
                USER_PREFS['GENERAL_FONT_KIND'],
                'GENERAL_FONT_TO_USE',
                general_font_widget_map,
            ),

            (
                USER_PREFS['MONO_FONT_KIND'],
                'MONO_FONT_TO_USE',
                mono_font_widget_map,
            ),
        ):

            user_value = USER_PREFS[value_key]

            ## font preview

            value = user_value if font_kind == 'font_file' else '.'

            fp = FontPreview(
                value=value,
                name=value_key,
                loop_holder=self,
                draw_on_window_resize=self.draw,
            )

            widget_map['font_file'] = fp

            ## system fonts option menu

            value = user_value if font_kind == 'system_font' else ''

            sfom = SystemFontsOptionMenu(
                value=value,
                name=value_key,
                loop_holder=self,
                string_when_single=True,
                draw_on_window_resize=self.draw,
            )

            widget_map['system_font'] = sfom

            ## default holder (when user chooses default font to be used)

            value = (

                "Encode Sans Semi-expanded Bold"
                if value_key == 'GENERAL_FONT_TO_USE'

                else "Fira Mono Bold"

            )

            dh = DefaultHolder(value=value, name=value_key, max_width=400)

            widget_map['default'] = dh



        ### calculate extra width and height used by "font_to_use" widgets

        widths, heights = zip(

            *(
                widget.rect.size

                for widget in chain(
                    general_font_widget_map.values(),
                    mono_font_widget_map.values(),
                )

            )

        )

        extra_width_required = max(widths)

        extra_height_used_by_single_widget = (
            max(heights) - general_font_kind_option_menu.rect.height
        )

        ### move last widget and label further down to make space for one of
        ### the extra widgets (from the maps we just created) that might be
        ### used

        prefs_widgets[-1].rect.y += extra_height_used_by_single_widget
        labels[-1].rect.y += extra_height_used_by_single_widget

        ### add and position "font_use" widgets beside their respective option
        ### menus

        self.switch_general_font_use_widget()
        self.switch_mono_font_use_widget()

        ### create, position and store form related buttons

        buttons = List2D(

            Button.from_text(
                text=text,
                command=command,
                **BUTTON_SETTINGS,
            )

            for text, command in (

                (
                    general_t.restore_default_settings,
                    self.restore_default_settings,
                ),
                (t.cancel, self.exit_loop),
                (t.save, self.save_form),

            )

        )

        for button in buttons:
            draw_depth_finish(button.image)

        buttons.rect.snap_rects_ip(
            retrieve_pos_from='midright',
            assign_pos_to='midleft',
            offset_pos_by=(8, 0),
        )

        buttons.rect.topright = (

            (

                # right
                widgets.rect.move(0, 5).right + extra_width_required,

                # top

                (
                    widgets.rect.move(0, 5).bottom
                    + extra_height_used_by_single_widget
                )

            )

        )


        ## store
        widgets.extend(buttons)

    def switch_font_use_widget(self, font_role):

        if font_role == 'general':

            widgets_to_remove = self.general_font_widget_map.values()

            widget_to_add = (

                self.general_font_widget_map[
                    self.gen_font_option.get()
                ]

            )

            topright = self.gen_font_option.rect.topright

        elif font_role == 'mono':

            widgets_to_remove = self.mono_font_widget_map.values()

            widget_to_add = (

                self.mono_font_widget_map[
                    self.mono_font_option.get()
                ]

            )

            topright = self.mono_font_option.rect.topright

        else:

            return RuntimeError(
                "This block should never execute, since the 'font_role'"
                " argument must be either 'general' or 'mono'."
            )

        widget_collections = (self.widgets, self.prefs_widgets)

        widgets = self.widgets

        for widget in widgets_to_remove:

            for collection in widget_collections:

                if widget in collection:
                    collection.remove(widget)

        widget_to_add.rect.topleft = topright
        widget_to_add.rect.move_ip(5, 0)

        for collection in widget_collections:
            collection.append(widget_to_add)


    switch_general_font_use_widget = (
        partialmethod(switch_font_use_widget, 'general')
    )

    switch_mono_font_use_widget = partialmethod(switch_font_use_widget, 'mono')

    def restore_default_settings(self):

        ## first change the option menus

        for widget in self.prefs_widgets:

            if isinstance(widget, OptionMenu):

                widget.set(
                    DEFAULT_USER_PREFS[widget.name]
                )

        ## then change the widgets which are not option menus, but also
        ## not default holders either (because as the name implies, they
        ## only ever hold default values, never needing to change)

        for widget in self.prefs_widgets:

            if not isinstance(widget, (OptionMenu, DefaultHolder)):

                widget.set(
                    DEFAULT_USER_PREFS[widget.name]
                )


    def edit_lang_and_fonts_settings(self):

        ### blit the screen-size semitransparent surf in the
        ### canvas to increase constrast
        blit_on_screen(UNHIGHLIGHT_SURF_MAP[SCREEN_RECT.size], (0, 0))

        ###
        self.loop()

        ### blit semitransparent surface over area occupied
        ### by self.rect so the form appears unhighlighted
        self.unhighlight()

    def handle_input(self):
        """Process events from event queue."""

        for event in SERVICES_NS.get_events():
            ### QUIT
            if event.type == QUIT:
                self.quit()

            ### KEYUP

            elif event.type == KEYUP:

                ## exit the preferences dialog by
                ## pressing "Esc"

                if event.key == K_ESCAPE:
                    self.exit_loop()

                ## confirm edition by pressing one of the "enter" keys

                elif event.key in (K_RETURN, K_KP_ENTER):
                    self.save_form()

            ### MOUSEBUTTONDOWN

            elif event.type == MOUSEBUTTONDOWN:

                if event.button == 1:

                    if self.rect.collidepoint(event.pos):
                        self.on_mouse_click(event)

            ### MOUSEBUTTONUP

            elif event.type == MOUSEBUTTONUP:

                if event.button == 1:

                    if self.rect.collidepoint(event.pos):
                        self.on_mouse_release(event)

                    ## cancel editing form if mouse left
                    ## button is released out of boundaries
                    else:
                        self.exit_loop()

    def mouse_method_on_collision(self, method_name, event):
        """Invoke inner widget if it collides with mouse.

        Parameters
        ==========

        method_name (string)
            name of method to be called on the colliding
            widget.
        event (event object of MOUSEBUTTON~ type)
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
                self.unhighlight()
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

    def save_form(self):
        """Save and set new preferences if copy with new values validates."""

        prefs_copy = USER_PREFS.copy()

        prefs_copy.update(

            (widget.name, widget.get())
            for widget in self.prefs_widgets

        )

        try:
            validate_prefs_data(prefs_copy)

        except Exception as err:

            message = f"Some error happened: {err}"
            create_and_show_dialog(message, level_name='error')

            return

        else:

            try:
                save_pyl(prefs_copy, CONFIG_FILEPATH)

            except Exception as err:

                message = f"Couldn't save config file: {err}"
                create_and_show_dialog(message, level_name='error')

                return

            else:
                USER_PREFS.update(prefs_copy)

        ### notify user via dialog and status message

        message = (
            "Language preferences changed. Most of these changes"
            " only take effect after restarting the app."
        )

        set_status_message(message)

        create_and_show_dialog(message, level_name='info')

        ### trigger exit of the loop
        self.exit_loop()

    def draw(self):
        """Draw itself and widgets.

        Extends Object2D.draw.
        """
        ### draw self (background)
        super().draw()

        ### draw widgets
        self.widgets.call_draw()

        ### update screen
        SERVICES_NS.update_screen()

    def unhighlight(self):
        """Draw semitransparent surface on self.rect area.

        Done to make form appear unhighlighted.
        """
        blit_on_screen(UNHIGHLIGHT_SURF_MAP[self.rect.size], self.rect)


edit_lang_and_fonts_settings = (
    UserPreferencesLanguageAndFontsForm()
    .edit_lang_and_fonts_settings
)
