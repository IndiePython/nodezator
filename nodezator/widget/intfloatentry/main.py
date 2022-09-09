"""Facility for single line updateable text object."""

### standard library import
from xml.etree.ElementTree import Element


### third-party imports

from pygame import Rect

from pygame.draw import aalines as draw_aalines

from pygame.transform import flip as flip_surface

from pygame.math import Vector2


### local imports

from ...surfsman.render import render_rect

from ...fontsman.constants import (
    ENC_SANS_BOLD_FONT_HEIGHT,
    ENC_SANS_BOLD_FONT_PATH,
)

from ...ourstdlibs.behaviour import (
    empty_function,
    return_untouched,
)

from ...ourstdlibs.color.creation import get_contrasting_bw

from ...colorsman.colors import (
    INT_FLOAT_ENTRY_FG,
    INT_FLOAT_ENTRY_BG,
)

from ...textman.cache import TEXT_SURFS_DB

## class for composition
from ...textman.entryedition.cursor import EntryCursor

## class extensions

from .op import IntFloatOperations
from .modes import IntFloatModes


### utility function


def ensure_int_float(value):
    """Return value if type(value) is int or float.

    Otherwise raises TypeError.

    Parameters
    **********
        value (any Python obj)
    """
    if type(value) not in (int, float):

        msg = "Value must be {!r} or {!r}.".format(int, float)

        raise TypeError(msg)

    return value


### constants

ALLOWED_NUM_CLASSES = {
    "int": (int,),
    "float": (float,),
    "int_float": (float, int),
}

NUM_TYPE_ENSURING_OPERATIONS = {
    (int,): round,
    (float,): float,
    (float, int): ensure_int_float,
}


### class definition


class IntFloatEntry(IntFloatOperations, IntFloatModes):
    """Specialized entry class for integer/float input.

    May also accept None.
    """

    def __init__(
        self,
        value=None,
        loop_holder=None,
        numeric_classes_hint="int",
        min_value=None,
        max_value=None,
        normal_drag_increment=None,
        preciser_drag_increment=None,
        normal_click_increment=None,
        preciser_click_increment=None,
        allow_none=False,
        name="int_float_entry",
        command=empty_function,
        update_behind=empty_function,
        draw_behind=empty_function,
        draw_on_window_resize=empty_function,
        position_reference_getter=None,
        width=155,
        font_height=ENC_SANS_BOLD_FONT_HEIGHT,
        font_path=ENC_SANS_BOLD_FONT_PATH,
        foreground_color=INT_FLOAT_ENTRY_FG,
        background_color=INT_FLOAT_ENTRY_BG,
        coordinates_name="topleft",
        coordinates_value=(0, 0),
    ):
        """Perform setups and assign data for reuse.

        Parameters
        ==========

        value (int, float or None)
            initial value of the widget; if None, the
            'allow_none' argument is automatically set
            to True.
        loop_holder (class w/ specific operations or None)
            obj with get_iput-update-draw operations; None
            can also be passed, in which case it means
            the loop holder will be the WindowManager
            class from the module winman.main.
        numeric_classes_hint
            (string, either "int", "float" or "int_float")
            indicates the allowed numeric class(es) to which
            the values will be constrained.
        min_value, max_value (int, float or None)
            if not None, it must be a number used to clamp
            the value of the widget to the minimum/maximum
            value specified, whenever the value is edited;
            such number must be of an allowed type, as
            defined by the 'numeric_classes_hint' argument;
            if None is used, no clamping to minimum/maximum
            value is ever performed.
        normal_drag_increment, preciser_drag_increment
            (int, float or None)
            these arguments are used to assist in the
            mouse edition mode, a mode where the user
            can edit the value by clicking the widget and,
            without releasing the button, dragging the
            mouse horizontally;
            if None, numeric values will be picked
            automatically;
            otherwise, they must be numbers of an allowed
            type, as defined by the 'numeric_classes_hint'
            argument; the normal_drag_increment is the normal
            value incremented/decremented when dragging
            the mouse; the preciser_drag_increment has the same
            purpose, but is used only when holding the
            shift key while dragging the mouse;
            as the name implies, the preciser increment is
            meant to be a value lower than the normal
            increment, but you can use a value which is
            equal, if you don't want to bother with
            preciser incrementation/decrementation.
        allow_none (boolean)
            if True, None can be used as a valid value
            in the widget; if the 'value' argument is
            None, this argument will be set to True
            automatically, even if the original value
            received was False.
        name (string)
            an arbitrary name to help identify the widget;
            it is assigned to the self.name attribute of
            this widget.
        command (callable)
            callable to be executed whenever the value
            changes (except when changing the value with
            self.set and setting its 'custom_command'
            parameter to False).
        update_behind (callable)
            to be called every loop. Can be used to update
            the states of other widgets outside entry
            (useful when the objects outside the entry
            change their appearance over time or in
            response to the contents of this entry while
            you type)
        draw_behind (callable)
            to be called every loop. Can be used to draw
            other widgets outside entry (useful when the
            objects outside the entry change their
            appearance over time or in response to the
            contents of this entry while you type).
        width (integer)
            width of the widget.
        font_height (integer)
            desired font height in pixels.
        font_path (string, defaults to ENC_SANS_BOLD_FONT_PATH)
            represents font style. Check local
            font.py module for available styles. In doubt,
            use ENC_SANS_BOLD_FONT_PATH for default font.
        foreground_color, background_color
            (tuple or list of r, g, b values which are
            integers ranging from 0 to 255)
            For the background color, an optional fourth
            value can be passed, which is an integer in
            the same range as the others, representing
            the image opacity (0 for full transparency
            and 255 for full opacity).
        coordinates_name (string)
            represents attribute name of rect wherein
            to store the position information from the
            coordinates value parameter.
        coordinates_value (2-tuple of integers)
            represents a position in 2d space; the values
            of x and y axes, respectively; it is assigned
            to the rect in the self.rect attribute of this
            widget, in the attribute represented by the
            'coordinates_name' argument.
        """
        ### store the allowed numeric types according to
        ### the numeric_classes_hint argument received

        # try retrieving the classes
        try:
            self.num_classes = ALLOWED_NUM_CLASSES[numeric_classes_hint]

        # if not present, then raise an error explaining
        # the issue
        except KeyError as err:

            raise ValueError(
                "'numeric_classes_hint' argument must be a"
                " string of value 'int', 'float' or"
                " 'int_float'"
            ) from err

        ### store a callable to constrain numeric values to
        ### the allowed numeric types (this callable is used
        ### only when the value is not None)

        self.ensure_num_type = NUM_TYPE_ENSURING_OPERATIONS[self.num_classes]

        ### process the normal and precision drag increment
        ### arguments (they contain the amount to be added
        ### to the widget value depending on direction and
        ### amount of pixels travelled by the mouse cursor
        ### horizontally when the value incrementation/
        ### decrementation by mouse dragging is active)

        ## provide default values for arguments if not
        ## provided

        if normal_drag_increment is None:
            normal_drag_increment = self.ensure_num_type(10)

        if preciser_drag_increment is None:
            preciser_drag_increment = self.ensure_num_type(1)

        ## check the arguments typing

        msg = (
            "{} must be of type hinted by the"
            " 'numeric_classes_hint' argument, which is"
            " one of the following: {}"
        )

        if type(normal_drag_increment) not in self.num_classes:

            raise TypeError(msg.format("normal_drag_increment", self.num_classes))

        if type(preciser_drag_increment) not in self.num_classes:

            raise TypeError(msg.format("preciser_drag_increment", self.num_classes))

        ## to guarantee the proper functioning of the
        ## feature, the arguments must always be positive

        msg = "{} must be positive."

        if normal_drag_increment < 0:

            raise ValueError(msg.format("normal_drag_increment"))

        if preciser_drag_increment < 0:

            raise ValueError(msg.format("preciser_drag_increment"))

        ## as an usability measure to guarantee the feature
        ## always works as intended, we decided to enforce
        ## the following rule: the normal drag increment
        ## must always be greater than or equal to the
        ## preciser increment

        if normal_drag_increment < preciser_drag_increment:

            msg = "normal_drag_increment must be" " >= preciser_drag_increment."
            raise ValueError(msg)

        ## finally store them

        self.normal_drag_increment = normal_drag_increment
        self.preciser_drag_increment = preciser_drag_increment

        ### process the normal and precision click
        ### increment arguments (they contain the amount to
        ### be added to the widget value depending on the
        ### arrow button clicked)

        ## provide default values for arguments if not
        ## provided

        if normal_click_increment is None:

            normal_click_increment = self.ensure_num_type(10)

        if preciser_click_increment is None:

            preciser_click_increment = self.ensure_num_type(1)

        ## check the arguments typing

        msg = (
            "{} must be of type hinted by the"
            " 'numeric_classes_hint' argument, which is"
            " one of the following: {}"
        )

        if type(normal_click_increment) not in self.num_classes:

            raise TypeError(msg.format("normal_click_increment", self.num_classes))

        if type(preciser_click_increment) not in self.num_classes:

            raise TypeError(msg.format("preciser_click_increment", self.num_classes))

        ## to guarantee the proper functioning of the
        ## feature, the arguments must always be positive

        msg = "{} must be positive."

        if normal_click_increment < 0:

            raise ValueError(msg.format("normal_click_increment"))

        if preciser_click_increment < 0:

            raise ValueError(msg.format("preciser_click_increment"))

        ## as an usability measure to guarantee the feature
        ## always works as intended, we decided to enforce
        ## the following rule: the normal_click_increment
        ## must always be greater than or equal to the
        ## preciser increment

        if normal_click_increment < preciser_click_increment:

            msg = "normal_click_increment must be" " >= preciser_click_increment."
            raise ValueError(msg)

        ## finally store them

        self.normal_click_increment = normal_click_increment
        self.preciser_click_increment = preciser_click_increment

        ### set the allow_none flag based on the
        ### "allow_none" argument and the "value" argument

        ## set allow_none attribute to the value in the
        ## argument
        self.allow_none = allow_none

        ## however, if the "value" argument is None,
        ## the flag is set to True regardless of the
        ## argument
        if value is None:
            self.allow_none = True

        ### check whether value is of allowed type, raising
        ### error if it is not
        self.validate_type(value)

        ### store value
        self.value = value

        ### process range constraining arguments
        self.set_range(min_value, max_value, False)

        ### convert the colors passed into tuples for
        ### simplicity (since colors can appear in other
        ### classes like pygame.Color and builtin lists too)

        background_color = tuple(background_color)
        foreground_color = tuple(foreground_color)

        ### store some of the arguments in their own
        ### attributes

        self.name = name
        self.command = command
        self.loop_holder = loop_holder
        self.background_color = background_color

        ### create and position a rect for this entry

        self.rect = Rect(0, 0, width, font_height)

        setattr(
            self.rect,
            coordinates_name,
            coordinates_value,
        )

        ### create a background surface for the widget

        self.background = render_rect(width, font_height, background_color)

        ### also store a copy of it as the image
        ### representing this widget
        self.image = self.background.copy()

        ### gather the remaining text rendering settings
        ### in a dictionary inside its own attribute

        render_settings = {
            "font_height": font_height,
            "font_path": font_path,
            "foreground_color": foreground_color,
        }

        ### instantiate the entry cursor class, which
        ### will hold the value of the entry as an string

        self.cursor = EntryCursor(
            str(value),
            render_settings,
            self,
            get_contrasting_bw(background_color),
        )

        ### also create and store objects/values to help
        ### manage button decrementation/incrementation

        arrow_height = 17

        arrow_rect = Rect(0, 0, 10, arrow_height)

        drawing_points = (
            arrow_rect.move(2, 4).midtop,
            arrow_rect.move(-2, 0).center,
            arrow_rect.move(2, -5).midbottom,
        )

        arrow_surfs = []

        for flip_x, arrows in (
            (False, 2),
            (False, 1),
            (True, 1),
            (True, 2),
        ):

            arrow_surf = render_rect(10, arrow_height, (0, 0, 0, 0))

            if arrows == 1:

                for offset in (
                    (-1, 0),
                    (0, 0),
                ):

                    draw_aalines(
                        arrow_surf,
                        foreground_color,
                        False,
                        tuple(point + Vector2(offset) for point in drawing_points),
                    )

            else:

                for offset in (
                    (-3, 0),
                    (-2, 0),
                    (1, 0),
                    (2, 0),
                ):

                    draw_aalines(
                        arrow_surf,
                        foreground_color,
                        False,
                        tuple(point + Vector2(offset) for point in drawing_points),
                    )

            if flip_x:

                arrow_surf = flip_surface(arrow_surf, True, False)

            arrow_surfs.append(arrow_surf)

        ###

        (
            self.dla_surf,
            self.sla_surf,
            self.sra_surf,
            self.dra_surf,
        ) = arrow_surfs

        self.dla_right = self.dla_surf.get_width()

        self.sla_right = self.dla_right + self.sla_surf.get_width()

        self.dra_left = width - self.dra_surf.get_width()

        self.sra_left = self.dra_left - self.sra_surf.get_width()

        self.arrow_y_offset = (font_height - arrow_height) // 2

        ### update the surface of the widget
        self.update_image()

        ### store behaviours

        self.update_behind = update_behind
        self.draw_behind = draw_behind

        self.draw_on_window_resize = draw_on_window_resize

        ### check existence of position reference getter and
        ### store it if it exists

        self.get_reference_pos = (
            position_reference_getter
            if position_reference_getter is not None
            else self.get_topleft
        )

        ### define behaviours

        self.draw = super().draw
        self.update = empty_function

        ### special routine
        self.movement_watch_out_routine = empty_function

    def get_expected_type(self):

        classes = self.num_classes + ((type(None),) if self.allow_none else ())

        return classes[0] if len(classes) == 1 else classes

    def get_topleft(self):
        return self.rect.topleft

    def svg_repr(self):
        """Return svg group element representing widget.

        Overrides Object2D.svg_repr().
        """
        line = self.cursor.line
        line.rect.topleft = self.rect.topleft

        text = "<< <" + "".join(
            obj.text for obj in self.cursor.line.get_colliding(self.rect)
        )

        rect = self.rect.copy()
        x_str, y_str, width_str, height_str = map(str, rect)

        ###

        group = Element("g", {"class": "int_float_entry"})

        group.append(
            Element(
                "rect",
                {
                    "x": x_str,
                    "y": y_str,
                    "width": width_str,
                    "height": height_str,
                    "class": "bg",
                },
            )
        )

        ##

        if (
            self.clamp_min is not return_untouched
            and self.clamp_max is not return_untouched
            and self.value is not None
        ):

            try:
                factor = self.value / self.difference
            except ZeroDivisionError:
                factor = 1

            range_rect = self.rect.copy()
            range_rect.w *= factor

            x_str, y_str, width_str, height_str = map(str, range_rect)

            group.append(
                Element(
                    "rect",
                    {
                        "x": x_str,
                        "y": y_str,
                        "width": width_str,
                        "height": height_str,
                        "class": "range_bg",
                    },
                )
            )

        ##

        (
            text_x_str,
            text_y_str,
        ) = map(str, rect.move(0, -3).bottomleft)

        text_element1 = Element(
            "text",
            {
                "x": text_x_str,
                "y": text_y_str,
                "text-anchor": "start",
            },
        )

        text_element1.text = text

        group.append(text_element1)

        ##

        (
            text_x_str,
            text_y_str,
        ) = map(str, rect.move(0, -3).bottomright)

        text_element2 = Element(
            "text",
            {
                "x": text_x_str,
                "y": text_y_str,
                "text-anchor": "end",
            },
        )

        text_element2.text = "> >>"
        group.append(text_element2)

        ##

        return group
