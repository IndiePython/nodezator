"""Facility for system font option menu widget."""

### standard library imports

from string import (
    ascii_uppercase,
    ascii_lowercase,
    digits,
    punctuation,
)

from functools import partial

from operator import attrgetter


### third-party imports

from pygame import Surface, error as PygameError

from pygame.draw import rect as draw_rect


### local imports

from ..config import APP_REFS

from ..dialog import create_and_show_dialog

from ..ourstdlibs.behaviour import empty_function

from ..our3rdlibs.behaviour import set_status_message

from ..classes2d.single import Object2D

from ..surfsman.render import render_rect

from ..surfsman.cache import NOT_FOUND_SURF_MAP

from ..surfsman.draw import blit_aligned, draw_depth_finish

from ..fontsman.viewer import view_fonts

from ..fontsman.preview.cache import (
    FONT_PREVIEWS_DB,
    update_cache_for_font_preview,
)

from ..fontsman.systemfontspicker import pick_system_fonts

from ..fontsman.constants import FIRA_MONO_BOLD_FONT_PATH

from ..textman.render import render_text

from .intfloatentry.main import IntFloatEntry



BUTTON = (

    Object2D.from_surface(
        render_text(
            text='SYSFONT',
            font_height=18,
            font_key=FIRA_MONO_BOLD_FONT_PATH,
            foreground_color=(0, 205, 0),
            background_color=(0, 0, 145),
        ),
    )

)




PREVIEW_CHARS = (
    digits
    + "".join(
        sorted(ascii_uppercase + ascii_lowercase, key=str.lower)[
            : 2 * 9
        ]  # only first 9 pairs
    )
    + punctuation
)


GET_TOPLEFT = attrgetter('rect.topleft')


class SystemFontsOptionMenu(Object2D):
    """Helps users pick system fonts and display them."""

    def __init__(
        self,
        value='',
        loop_holder=None,
        string_when_single=True,
        name='system_font_option_menu',
        width=155,
        draw_on_window_resize=empty_function,
        command=empty_function,
        coordinates_name='topleft',
        coordinates_value=(0, 0),
    ):

        ### store string_when_single argument
        self.string_when_single = string_when_single

        ### ensure value argument received is valid
        self.validate_value(value)

        ### store more of the arguments in their own
        ### attributes

        self.name = name
        self.value = value
        self.command = command
        self.loop_holder = loop_holder

        ### define control attribute for when there's more than one name listed
        self.name_index = 0

        ### entry to dipslay/change index

        max_value = len(value) - 1 if not isinstance(value, str) else 0

        topleft = BUTTON.rect.move(1, 0).topright

        self.index_entry = IntFloatEntry(
            value=0,
            min_value=0,
            max_value=max_value,
            numeric_classes_hint='int',
            font_height=BUTTON.rect.height,
            width=68,
            loop_holder=loop_holder,
            command=self.update_previewed_font_from_entry,
            draw_on_window_resize=draw_on_window_resize,
            position_reference_getter=(partial(GET_TOPLEFT, self)),
            coordinates_name='topleft',
            coordinates_value=topleft,
        )

        ### create image and rect, then position rect

        self.image = Surface((width, 170)).convert()
        self.image.fill('grey')
        self.rect = self.image.get_rect()

        setattr(
            self.rect,
            coordinates_name,
            coordinates_value,
        )

        ###
        self.update_image()

    def validate_value(self, value):
        """Check whether type is of allowed type."""
        value_type = type(value)

        ### if value is a string, it can be any value, so we don't need
        ### to do anything else

        if value_type is str:
            pass

        ### if value is a tuple, though, more conditions need to be checked

        elif value_type is tuple:

            ## it must not be empty

            if not value:
                raise ValueError("if 'value' is a tuple, it must not be empty")

            ## all of its items must be strings

            elif any(

                not isinstance(item, str)
                for item in value

            ):

                raise TypeError(
                    "if 'value' is a tuple, all of its items must be strings"
                )

            ## if 'string_when_single' flag is on, it cannot have a single value
            ## (otherwise it should be a string instead)

            elif self.string_when_single and len(value) == 1:

                raise TypeError(
                    "with 'string_when_single' enabled, when the value"
                    " contains a single font name, it must be a string,"
                    " not a tuple"
                )

        ### if type isn't one of the allowed types, raise
        ### TypeError with suitable message

        else:
            raise TypeError("'value' must be a string or tuple of strings")

    def update_image(self):
        """Update widget image."""
        ###
        image = self.image

        ### clean image surface
        image.fill('grey')

        ###
        value = self.value

        ### create variable specifying whether the value
        ### is a string
        value_is_string = isinstance(value, str)

        ### create variable specifying whether there's more than one font name
        multiple_names = not value_is_string and len(value) > 1

        ### if there are multiple font names...

        if multiple_names:

            ### define current font name
            self.current_font_name = value[self.name_index]

        ### if there's just one font name, though...

        else:

            ### define font name
            self.current_font_name = value if value_is_string else value[0]

        ### blit all buttons
        image.blit(BUTTON.image, (2, 2))

        ### blit font representation
        self.blit_value_representation()

        ### draw depth finish
        draw_depth_finish(image)

    def update_previewed_font_from_entry(self):
        """"""
        self.name_index = self.index_entry.get()

        self.current_font_name = self.value[self.name_index]

        self.blit_value_representation()

    def blit_value_representation(self):
        """Blit representation of current font."""

        image = self.image

        button_height = BUTTON.rect.height

        rect = (
            1,
            button_height + 2,
            self.rect.width - 2,
            self.rect.height - ((button_height * 2) + 2),
        )

        draw_rect(image, 'grey', rect)

        ###

        if self.current_font_name == '':
            preview_surf = NOT_FOUND_SURF_MAP[(rect[2], rect[3])]

        else:

            preview_surf = FONT_PREVIEWS_DB[self.current_font_name][
                {
                    'font_size': 20,
                    'chars': PREVIEW_CHARS,
                    'width': rect[2],
                    'height': rect[3],
                    'not_found_width': rect[2],
                    'not_found_height': rect[3],
                }
            ]

        image.blit(preview_surf, rect)

        ### blit rest of elements

        rect = image.get_rect()
        rect.topleft = rect.move(1, -button_height).bottomleft
        rect.height = button_height - 2
        rect.move_ip(0, 1)

        draw_rect(image, 'grey', rect)

        ###

        blit_aligned(

            surface_to_blit=(

                render_text(
                    text=str(self.current_font_name),
                    font_height=APP_REFS.general_font_height,
                    font_key=APP_REFS.general_font_key,
                    padding=1,
                    max_width=152,
                    ommit_direction='left',
                )

            ),

            target_surface=image,
            retrieve_pos_from='bottomright',
            assign_pos_to='bottomright',
            offset_pos_by=(-1, 0),
        )

        if isinstance(self.value, str) or len(self.value) == 1:
            return

        ### blit entry

        blit_aligned(

            surface_to_blit=self.index_entry.image,
            target_surface=image,
            retrieve_pos_from='topleft',
            assign_pos_to='topleft',
            offset_pos_by=(BUTTON.rect.width + 4, 2),

        )

    def preview_fonts(self):
        """Preview font(s) from system."""

        try:
            view_fonts(self.value)

        except FileNotFoundError:
            error_msg = "System font wasn't found."

        except PygameError:
            error_msg = "Couldn't load font file"

        except Exception as err:
            error_msg = str(err)

        else:
            error_msg = ''

        if error_msg:

            create_and_show_dialog(
                message=error_msg,
                level_name='error',
            )

            set_status_message(error_msg)

    def get(self):
        """Return the widget value."""
        return self.value

    def set(
        self,
        value,
        custom_command=True,
        update_image=True,
    ):
        """Set the value of the widget.

        value (string or tuple of strings representing paths)
            new value for widget.
        custom_command (boolean)
            indicates whether the custom command stored
            upon instantiation should be called after
            updating the value.
        update_image (boolean)
            indicates whether the update_image method
            should be called after updating the value.
        """
        ### validate value received
        try:
            self.validate_value(value)

        ### if it doesn't validate, report error and exit
        ### method by returning

        except (TypeError, ValueError) as err:

            print(err)
            return

        ### changes are only performed if the new value is
        ### indeed different from the current one

        if self.value != value:

            ### store new value
            self.value = value

            ### reset index
            self.name_index = 0

            ### reset index value and max value

            entry = self.index_entry

            entry.set(0, False)

            max_value = 0 if isinstance(value, str) else len(value) - 1

            entry.set_range(0, max_value)

            ### if requested, execute the custom command

            if custom_command:
                self.command()

            ### if requested, update the widget image

            if update_image:
                self.update_image()

    def on_mouse_click(self, event):
        """Reposition and give focus to entry."""
        if self.collides_with_entry(event.pos):
            self.index_entry.on_mouse_click(event)

    def on_mouse_release(self, event):
        """Act according to mouse release position.

        Parameters
        ==========
        event
            (pygame.event.Event of pygame.MOUSEBUTTONUP type)

            It is required in order to comply with
            protocol used. We retrieve the mouse position
            from its "pos" attribute.

            Check pygame.event module documentation on
            pygame website for more info about this event
            object.
        """

        pos = event.pos

        rect = BUTTON.rect
        rect.topleft = self.rect.move(2, 2).topleft

        if self.collides_with_entry(pos):
            pass

        elif rect.collidepoint(pos):

            font_names = (

                (self.value,)
                if isinstance(self.value, str)

                else self.value

            )

            new_font_names = pick_system_fonts(font_names)

            if new_font_names is not None:

                new_value = (
                    new_font_names[0]
                    if len(new_font_names) == 1 and self.string_when_single
                    else new_font_names
                )

                self.set(new_value)
            
        else:
            self.preview_fonts()

    def collides_with_entry(self, pos):
        """Return whether given pos collides with entry."""
        ### TODO review/refactor this "if block"

        if isinstance(self.value, str) or len(self.value) == 1:
            return False

        entry_rect = self.index_entry.rect

        entry_rect.topleft = (
            self.rect.move(BUTTON.rect.width+2, 0).topleft
        )

        return entry_rect.collidepoint(pos)
