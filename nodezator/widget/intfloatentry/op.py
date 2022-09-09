"""Extension for the IntFloatEntry with general operations."""

### standard library imports

from functools import partial

from math import nan


### third-party imports

from pygame.math import Vector2

from pygame.draw import rect as draw_rect


### local imports

from ...classes2d.single import Object2D

from ...loopman.exception import SwitchLoopException

from ...ourstdlibs.behaviour import (
    empty_function,
    return_untouched,
)

from .numeval import numeric_evaluation


INFS_AND_NANS = (
    float("-inf"),
    float("inf"),
    float("nan"),
    nan,
)

RANGE_ERROR_FORMATTER = ("{} argument must be of one of the following types: {}").format


class IntFloatOperations(Object2D):
    """General operations for the IntFloatEntry."""

    def get(self):
        """Return value of widget."""
        return self.value

    def set(self, value, custom_command=True):
        """Set obj text.

        Parameters
        ==========
        value (int, float or None, depends on valid types)
            value to be held by the widget.
        custom_command (boolean)
            indicates whether to execute self.command if the
            value is actually changed.
        """
        ### return if value isn't of allowed type

        ## try validating type
        try:
            self.validate_type(value)

        ## if a type/value error is raised, report it
        ## by printing, then exit this method by
        ## returning

        except (TypeError, ValueError) as err:

            ### TODO probably display error in statusbar
            ### or user logger, instead of printing
            print("From intfloat widget:", err)
            return

        ### override the value by evaluating its string;
        ###
        ### this will cause the value to be clamped in case
        ### its value isn't allowed yet
        value = self.evaluate_string(str(value))

        ### return if value is already set
        if value == self.value:
            return

        ### otherwise store the value
        self.value = value

        ### then set value as the contents of the line
        ### (convert to string first)
        self.cursor.set(str(value))

        ### also update the image
        self.update_image()

        ### also, if requested, execute custom command
        if custom_command:
            self.command()

    def update_image(self):
        """Update image surface attribute."""
        ### reference image locally
        image = self.image

        ### clean image using the background
        image.blit(self.background, (0, 0))

        ### execute a special routine to update the
        ### image surface,
        self.range_like_image_update_operation()

        ### blit character objects from line on the image

        ## reposition line

        self.cursor.line.rect.topleft = self.rect.move(self.sla_right, 0).topleft

        ## create an offset from rect's topleft inverse
        offset = -Vector2(self.rect.topleft)

        ## blit arrows

        y = self.arrow_y_offset

        image.blit(self.dla_surf, (0, y))
        image.blit(self.sla_surf, (self.dla_right, y))

        image.blit(self.sra_surf, (self.sra_left, y))
        image.blit(self.dra_surf, (self.dra_left, y))

        ## iterate over character objects colliding with
        ## self.rect, blitting then on the image using
        ## offset copies of their rects

        for obj in self.cursor.line.get_colliding(self.rect):
            image.blit(obj.image, obj.rect.move(offset))

    def update_image_like_range(self):
        """"""
        if self.value is None:
            return

        value = self.evaluate_string(self.cursor.get())

        try:
            factor = value / self.difference
        except ZeroDivisionError:
            factor = 1

        rect = self.rect.copy()
        rect.w *= factor

        rect.topleft = (0, 0)

        draw_rect(
            self.image,
            (30, 130, 70),
            rect,
        )

    def on_mouse_click(self, event):
        """Perform operations depending on click position.

        This method is aliased as "on_mouse_click" to
        comply with the mouse interaction protocol.

        Parameters
        ==========
        event
            (pygame.event.Event of pygame.MOUSEBUTTONDOWN
            type) we use it to retrieve and use the
            mouse position.
        """
        ### store special position for future reference
        ### if needed
        self.reference_pos = self.get_reference_pos()

        ### set movement watch out routine to an empty
        ### function
        self.movement_watch_out_routine = empty_function

        ## if value is None, incrementing or decrementing
        ## it makes no sense (which is what happens in the
        ## mouse edition mode), so instead, we enable the
        ## keyboard edition mode right away

        if self.value is None:
            self.enable_keyboard_edition_mode()

        ## otherwise, other tasks are performed

        else:

            ## if the area of one of the
            ## decrement/increment buttons is clicked,
            ## make the corresponding operation
            ## and exit this method by returning

            x = event.pos[0]
            delta_x = x - self.rect.x

            if delta_x < self.dla_right:

                self.set(self.value - self.normal_click_increment)

                return

            elif delta_x < self.sla_right:

                self.set(self.value - self.preciser_click_increment)

                return

            elif delta_x > self.dra_left:

                self.set(self.value + self.normal_click_increment)

                return

            elif delta_x > self.sra_left:

                self.set(self.value + self.preciser_click_increment)

                return

            ## otherwise, the user may want to use either
            ## the keyboard or the mouse edition mode, so
            ## we enable the standby mode, which
            ## automatically sets the next mode depending
            ## on the next action the user performs;
            ##
            ## before doing so, we backup the mouse
            ## position, since we might need it in case
            ## the user enters the mouse edition mode next
            ## (since we use such position when leaving
            ## the mouse edition mode)

            else:

                self.initial_mouse_pos = event.pos
                self.enable_standby_mode()

        ### reposition line and move cursor to end of text

        self.cursor.line.rect.topleft = self.rect.topleft
        self.cursor.go_to_end()

        ### give focus to self by raising a manager switch
        ### exception with a reference to this widget
        raise SwitchLoopException(self)

    def lose_focus(self):
        """Focus loop holder."""
        ### restore default behaviours for update and
        ### drawing operations

        self.draw = super().draw
        self.update = empty_function

        ### switch to the stored loop holder (if
        ### None, the default loop holder used is
        ### the WindowManager instance from the module
        ### winman.main)
        raise SwitchLoopException(self.loop_holder)

    def resume_editing(self):
        """Resume editing the contents.

        If the temporary value is equal to the actual
        value store, we just get out of the widget
        (lose focus).

        Otherwise, we check whether the temporary value
        is valid. If not, we restore the original value.
        If it is, we perform tasks to store it.
        """
        ### retrieve the line contents
        line_contents = self.cursor.get()

        ### try evaluating the string and validating
        ### its type

        try:

            value = self.evaluate_string(line_contents)
            self.validate_type(value)

        ### if line contents are not valid, print the error,
        ### roll string back to current value and update
        ### self.image

        except Exception as err:

            # TODO we could display the error in the
            # statusbar or the user logger, instead of
            # printing;
            print("From intfloat widget:", err)

            self.cursor.set(str(self.value))
            self.update_image()

        ### if otherwise the evaluation and validation
        ### succeed, it means the contents are valid,
        ### so we set the value if it is not already set

        else:

            ## update the line contents
            self.cursor.set(str(value))

            ## if the value is different from the actual
            ## one, set it, update the image and execute
            ## the custom command

            if value != self.value:

                self.set(value)

                self.update_image()

                self.command()

            ## otherwise just update the image
            else:
                self.update_image()

        ### finally we lose focus
        self.lose_focus()

    def validate_type(self, value):
        """Raise TypeError if type of value isn't allowed."""
        ### if value isn't of specified type...

        if type(value) not in self.num_classes:

            msg = ("'value' must be of one of the following" " types: {}").format(
                self.num_classes
            )

            ## if None is allowed...

            if self.allow_none:

                # if despite being allowed, the value is
                # not None, raise an error

                if value is not None:
                    raise TypeError(msg + " or 'NoneType'")

            ## otherwise, since the value isn't of the
            ## specified type and None is not allowed
            else:
                raise TypeError(msg)

        if value in INFS_AND_NANS:
            raise ValueError("Can't use inf/-inf/nan")

    def evaluate_string(self, string):
        """Return value represented by string.

        If allowed, the string might represent None, in
        which case we just return None.

        Otherwise, the string represents a numerical value
        or expression, in which case we also perform extra
        operations to enforce a numerical type and to clamp
        the value to allowed intervals when applicable.

        Parameters
        ==========

        string (string)
            string to be evaluated; it can be...

            1) 'None' (only if None is allowed; see the
               docstring of the __init__ method of the
               IntFloatEntry class about this);

            2) a string representing a numerical value
               (an integer or float);

            3) a string representing a numerical expression
               in Python (for instance '2 + 2', '5 ** 2',
               or even 'randint(10, 20)', etc.)

            4) any other string is considered invalid and
               will raise errors (for instance, an empty
               string or a string representing a numerical
               value with wrong syntax or numerical
               expression with wrong syntax);

               the error raised won't be caught, since this
               method is used in safe contexts (either with
               try/except clauses or with strings known to
               have correct syntax).
        """
        ### if string is empty, raise ValueError indicating
        ### problem

        if not string:

            raise ValueError("there is nothing typed in the entry")

        ### if None is allowed and the string represents it,
        ### return None
        if self.allow_none and string == "None":
            return None

        ### otherwise perform a custom evaluation of the
        ### string
        value = numeric_evaluation(string)

        ### and process it into the final value by passing
        ### it through several relevant operations

        for operation in (
            ## restrain to the allowed numeric type(s); check
            ## the docstring of the __init__ method of the
            ## IntFloatEntry class
            self.ensure_num_type,
            ## clamp to the allowed interval (when applicable)
            self.clamp_min,
            self.clamp_max,
        ):
            value = operation(value)

        ### finally return the value
        return value

    def set_range(
        self,
        min_value,
        max_value,
        update_image=True,
    ):
        """"""
        value = self.value

        ### process range constraining arguments

        range_is_constrained = min_value is not None and max_value is not None

        ## make extra checks/assignments depending on
        ## whether or not the range is constrained

        if range_is_constrained:

            ## ensure the maximum value is greater than or
            ## at least equal to the minimum value

            if not (max_value >= min_value):

                raise ValueError(
                    "arguments must follow rule:" " max_value >= min_value."
                )

            ## store difference between maximum and
            ## minimum values
            self.difference = max_value - min_value

        ## define extra operation to update the widget's
        ## surface, depending on whether the widget's
        ## range is constrained or not

        self.range_like_image_update_operation = (
            self.update_image_like_range if range_is_constrained else empty_function
        )

        ## define minimum and maximum value clamping
        ## operations, according to whether the
        ## corresponding arguments are None or not;
        ##
        ## we also check whether the 'min_value' and
        ## 'max_value' arguments, when numeric, are of an
        ## allowed type;
        ##
        ## we also check whether the value is within the
        ## interval defined by the 'min_value'/'max_value'
        ## arguments, if applicable (that is, if the value
        ## is numeric, check whether it complies with
        ## the 'min_value'/'max_value' arguments which
        ## are numeric too;

        # if min_value is not None, that is, if it is
        # numeric, check wheter it is of an allowed type
        # and perform additional setups

        if min_value is not None:

            ## if given minimum value is not one of the
            ## allowed numeric values, a ValueError must
            ## be raised to indicate this forbidden scenario

            if type(min_value) not in self.num_classes:

                raise ValueError(RANGE_ERROR_FORMATTER("min_value", self.num_classes))

            ## otherwise, we store a partial of the max
            ## function with the minimum value as the
            ## clamping operation;
            ##
            ## note: remember that to clamp to a
            ## minimum value, we should use max since
            ## we want min_value to have preference
            ## over values below it; it's how a
            ## minimum value is supposed to work;
            ##
            ## we also check whether the value, if numeric,
            ## complies with the defined boundary

            else:

                ## store clamping operation
                self.clamp_min = partial(max, min_value)

                ## if the value is numeric, but it is
                ## below the minimum value allowed,
                ## raise an error explaining the problem

                if value is not None and value < min_value:

                    msg = (
                        (
                            "value must be None or "
                            if self.allow_none
                            else "value must be "
                        )
                        + ">= "
                        + str(min_value)
                    )

                    raise ValueError(msg)

        # if min_value is None, though, it means no minimum
        # value clamping must take place, so we set a
        # dummy clamping operation, one which returns the
        # value as-is, without changing it
        else:
            self.clamp_min = return_untouched

        # if max_value is not None, that is, if it is
        # numeric, check wheter it is of an allowed type
        # and perform additional setups

        if max_value is not None:

            ## if given maximum value is not one of the
            ## allowed numeric values, a ValueError must
            ## be raised to indicate this forbidden scenario

            if type(max_value) not in self.num_classes:

                raise ValueError(RANGE_ERROR_FORMATTER("max_value", self.num_classes))

            ## otherwise, we store a partial of the min
            ## function with the maximum value as the
            ## clamping operation;
            ##
            ## note: remember that to clamp to a
            ## maximum value, we should use min since
            ## we want max_value to have preference
            ## over values above it; it's how a
            ## maximum value is supposed to work;
            ##
            ## we also check whether the value, if numeric,
            ## complies with the defined boundary

            else:

                ## store clamping operation
                self.clamp_max = partial(min, max_value)

                ## if the value is numeric, but it is
                ## above the maximum value allowed,
                ## raise an error explaining the problem

                if value is not None and value > max_value:

                    msg = (
                        (
                            "value must be None or "
                            if self.allow_none
                            else "value must be "
                        )
                        + "<= "
                        + str(max_value)
                    )

                    raise ValueError(msg)

        # if max_value is None, though, it means no maximum
        # value clamping must take place, so we set a
        # dummy clamping operation, one which returns the
        # value as-is, without changing it
        else:
            self.clamp_max = return_untouched

        ### if requested, update the image
        if update_image:
            self.update_image()
