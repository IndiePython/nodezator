"""Facility for widget to preview contents of path(s)."""

### standard library imports

from pathlib import Path

from xml.etree.ElementTree import Element

from functools import partial

from operator import attrgetter


### third-party import
from pygame.draw import rect as draw_rect


### local imports

from ...ourstdlibs.behaviour import empty_function

from ...fileman.main import select_paths

from ...classes2d.single import Object2D

from ...fontsman.constants import (
    ENC_SANS_BOLD_FONT_PATH,
    ENC_SANS_BOLD_FONT_HEIGHT,
)

from ...textman.render import render_text, fit_text

from ...surfsman.render import render_rect

from ...surfsman.draw import draw_depth_finish, blit_aligned

from ...colorsman.colors import PATHPREVIEW_BG

from ..intfloatentry.main import IntFloatEntry

from .constants import (
    ICON_SURF,
    BUTTON_SURFS,
    BUTTON_RECTS,
    BUTTON_HEIGHT,
    BUTTON_CALLABLE_NAMES,
    BUTTON_SVG_REPRS,
)


GET_TOPLEFT = attrgetter("rect.topleft")


class _BasePreview(Object2D):
    """Base class for path preview w/ common operations."""

    button_surfs, button_rects = BUTTON_SURFS, BUTTON_RECTS

    button_callable_names = BUTTON_CALLABLE_NAMES
    button_svg_reprs = BUTTON_SVG_REPRS

    height = 42

    def __init__(
        self,
        value=".",
        loop_holder=None,
        string_when_single=True,
        name="path_preview",
        width=155,
        draw_on_window_resize=empty_function,
        command=empty_function,
        coordinates_name="topleft",
        coordinates_value=(0, 0),
    ):
        """Store arguments and define button image.

        Parameters
        ==========

        value
        (string representing a path or tuple of strings
        representing pahts)
            initial value of the widget.
        string_when_single (bool)
            when more than one path is given, the value is
            always a tuple of strings, however, this
            parameter defines whether the value
            must be represented by a string when only
            a single path is given, rather than a tuple
            with a single string.
        name (string)
            an arbitrary name to help identify the widget.
        coordinates_name (string)
            represents attribute name of rect wherein
            to store the position information from the
            coordinates value parameter.
        coordinates_value (list/tuple/vector w/ 2 integers)
            represents the x and y coordinates of a
            position in 2d space.
        """
        ### store string_when_single argument
        self.string_when_single = string_when_single

        ### validate value received
        self.validate_value(value)

        ### store other arguments

        self.value = value
        self.name = name
        self.command = command
        self.width = width

        ### define control attribute for when there's
        ### more than one path listed
        self.path_index = 0

        ### entry to display/change index

        max_value = len(value) - 1 if not isinstance(value, str) else 0

        topleft = self.button_rects[1].move(1, 0).topright

        self.index_entry = IntFloatEntry(
            value=0,
            min_value=0,
            max_value=max_value,
            numeric_classes_hint="int",
            font_height=ICON_SURF.get_height() - 1,
            width=68,
            loop_holder=loop_holder,
            command=self.update_previewed_path_from_entry,
            draw_on_window_resize=draw_on_window_resize,
            position_reference_getter=(partial(GET_TOPLEFT, self)),
            coordinates_name="topleft",
            coordinates_value=topleft,
        )

        ### create surface for the widget

        self.image = render_rect(
            self.width,
            self.height,
            PATHPREVIEW_BG,
        )

        ### create rect from the image, then position it

        self.rect = self.image.get_rect()

        setattr(self.rect, coordinates_name, coordinates_value)

        ### update the image contents with the value
        self.update_image()

    def validate_value(self, value):
        """Check whether value is of allowed type."""
        value_type = type(value)

        ### if value is string, it doesn't validate if it is
        ### empty or if 'string_when_single' attribute is
        ### False

        if value_type is str:

            if not value:

                raise ValueError("if 'value' is of 'str' type, it" " must not be empty")

            elif not self.string_when_single:

                raise ValueError(
                    "if 'string_when_single' is"
                    " False, 'value' must always"
                    " be a tuple"
                )

        ### if it is a tuple , more conditions need to be
        ### checked

        elif value_type is tuple:

            ## it must not be empty

            if not len(value):

                raise ValueError(
                    "if 'value' is of 'tuple' type, it must" " not be empty"
                )

            ## all of its items must be non-empty strings

            if any(type(item) is not str or not item for item in value):
                raise TypeError(
                    "if 'value' is of 'tuple' type, its items"
                    " must all be non-empty strings"
                )

        ### if type isn't one of the allowed types, raise
        ### TypeError with suitable message

        else:

            raise TypeError("'value' must be of type 'str' or 'tuple'")

    def update_image(self):
        """Update widget image."""
        ###
        image = self.image

        ### clean image surface
        image.fill(PATHPREVIEW_BG)

        ###
        value = self.value

        ### create variable specifying whether the value
        ### is a string
        value_is_string = isinstance(value, str)

        ### create variable specifying whether there's more
        ### than one path

        multiple_paths = not value_is_string and len(value) > 1

        ### if there are multiple paths...

        if multiple_paths:

            ### define current path
            self.current_path = value[self.path_index]

        ### if there's just one path, though...

        else:

            ### define path

            self.current_path = value if value_is_string else value[0]

        ### blit all buttons

        for surf, rect in zip(self.button_surfs, self.button_rects):
            image.blit(surf, rect)

        ### blit path representation
        self.blit_path_representation()

        ### draw depth finish
        draw_depth_finish(image)

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
            self.path_index = 0

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
        ### obtain the relative mouse position by
        ### subtracting the rect's topleft from the
        ### mouse's absolute position

        rel_mouse_pos = [a - b for a, b in zip(event.pos, self.rect.topleft)]

        ### if the mouse relative position collides with
        ### the rect of one of the buttons, execute the
        ### operation with the respective name, then exit
        ### this method by returning

        for i, rect in enumerate(self.button_rects):

            if rect.collidepoint(rel_mouse_pos):

                getattr(self, self.button_callable_names[i])()
                return

        ### if index entry was target, ignore
        if self.collides_with_entry(event.pos):
            return

        ### otherwise, it means the user clicked outside
        ### the buttons's boundaries, so we execute the
        ### path previewing method
        self.preview_paths()

    def collides_with_entry(self, pos):
        """Return whether given pos collides with entry."""
        ### TODO review/refactor this "if block"

        if isinstance(self.value, str) or len(self.value) == 1:
            return False

        entry = self.index_entry

        entry.rect.topleft = self.button_rects[1].move(self.rect.topleft).topright

        entry.rect.x += 1

        return entry.rect.collidepoint(pos)

    def select_new_paths(self):
        """Select new path(s) from the file manager.

        If no path is returned, the widget isn't updated.
        """
        ### retrieve path(s) from file browser
        paths = select_paths(caption="Select path(s)")

        ### if no paths are selected, return
        if not paths:
            return

        ### finally set the new path(s)

        paths = tuple(str(path) for path in paths)

        if len(paths) == 1 and self.string_when_single:
            self.set(paths[0])

        else:
            self.set(paths)

    def update_previewed_path_from_entry(self):
        """"""
        self.path_index = self.index_entry.get()

        self.current_path = self.value[self.path_index]

        self.blit_path_representation()

    def blit_path_representation(self):
        """Blit string representing path."""
        rect = self.image.get_rect()
        rect.topleft = rect.move(1, -BUTTON_HEIGHT).bottomleft
        rect.height = BUTTON_HEIGHT - 2
        rect.move_ip(0, 1)

        draw_rect(self.image, PATHPREVIEW_BG, rect)

        ###

        blit_aligned(
            surface_to_blit=render_text(
                text=str(self.current_path),
                font_path=ENC_SANS_BOLD_FONT_PATH,
                font_height=ENC_SANS_BOLD_FONT_HEIGHT,
                padding=1,
                max_width=152,
                ommit_direction="left",
            ),
            target_surface=self.image,
            retrieve_pos_from="bottomright",
            assign_pos_to="bottomright",
            offset_pos_by=(-1, -1),
        )

        if isinstance(self.value, str) or len(self.value) == 1:
            return

        ### blit entry

        self.image.blit(
            self.index_entry.image, self.button_rects[1].move(1, 0).topright
        )

    def get_expected_type(self):

        classes = set((tuple,))

        if self.string_when_single:
            classes.add(str)

        return classes.pop() if len(classes) == 1 else tuple(classes)

    def svg_repr(self):

        g = Element("g", {"class": "path_preview"})

        ###
        g.append(super().svg_repr())
        ###

        value = self.value

        ### create variable specifying whether the value
        ### is a string
        value_is_string = isinstance(value, str)

        ### create variable specifying whether there's more
        ### than one path

        multiple_paths = not value_is_string and len(value) > 1

        ###
        x_offset, y_offset = self.rect.inflate(-2, -2).topleft

        ### append all buttons' svg representations

        for button_svg_repr, rect in zip(self.button_svg_reprs, self.button_rects):

            x, y = (a + b for a, b in zip((x_offset, y_offset), rect.topleft))

            first_directive = f"M{x} {y}"

            for path_directives, style in button_svg_repr:

                path_directives = first_directive + path_directives

                g.append(
                    Element(
                        "path",
                        {
                            "d": path_directives,
                            "style": style,
                        },
                    )
                )

        ### append svg path representation
        g.append(self.svg_path_repr())

        ###
        return g

    def svg_path_repr(self):
        """Return svg text representing path."""
        g = Element("g")

        (
            text_x_str,
            text_y_str,
        ) = map(str, self.rect.move(-2, -5).bottomright)

        text_element = Element(
            "text",
            {
                "x": text_x_str,
                "y": text_y_str,
                "text-anchor": "end",
            },
        )

        text_element.text = fit_text(
            text=str(self.current_path),
            font_path=ENC_SANS_BOLD_FONT_PATH,
            font_height=ENC_SANS_BOLD_FONT_HEIGHT,
            padding=1,
            max_width=143,
            ommit_direction="left",
        )

        g.append(text_element)

        if isinstance(self.value, str) or len(self.value) == 1:
            return g

        ### append entry svg representation

        entry = self.index_entry

        entry_topleft = entry.rect.topleft

        button_topright = self.button_rects[1].move(2, 1).topright

        x, y = (
            value + offset for value, offset in zip(button_topright, self.rect.topleft)
        )

        entry.rect.topleft = x, y

        g.append(self.index_entry.svg_repr())

        entry.rect.topleft = entry_topleft

        return g
