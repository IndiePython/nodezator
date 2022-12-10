"""Facility for (usually single line) text object.

Check docstring of entry class defined in this module
to know more.
"""

### standard library import
from xml.etree.ElementTree import Element


### third-party imports

from pygame import (
    ## event types
    QUIT,
    KEYUP,
    KEYDOWN,
    MOUSEBUTTONUP,
    ## keys
    K_BACKSPACE,
    K_DELETE,
    KMOD_CTRL,
    K_LEFT,
    K_RIGHT,
    K_HOME,
    K_END,
    K_ESCAPE,
    K_RETURN,
    K_KP_ENTER,
    K_t,
    ## rect class
    Rect,
)

from pygame.display import update

from pygame.event import get as get_events

from pygame.math import Vector2


### local imports

from ..pygameconstants import WINDOW_RESIZE_EVENT_TYPE

from ..ourstdlibs.behaviour import (
    empty_function,
    return_untouched,
)

from ..ourstdlibs.stringutils import VALIDATION_COMMAND_MAP

from ..ourstdlibs.color.creation import get_contrasting_bw

from ..classes2d.single import Object2D

from ..surfsman.render import render_rect

from ..fontsman.constants import (
    ENC_SANS_BOLD_FONT_HEIGHT,
    ENC_SANS_BOLD_FONT_PATH,
)

from ..textman.editor.main import edit_text

from ..loopman.exception import (
    QuitAppException,
    SwitchLoopException,
)

from ..colorsman.colors import (
    STRING_ENTRY_FG,
    STRING_ENTRY_BG,
)

from ..textman.entryedition.cursor import EntryCursor


class StringEntry(Object2D):
    """Entry widget to hold (usually) a single line of text.

    This widget was initially design to hold a single line
    of text. However, in our efforts to make data handling
    as close as possible to how Python works we thought
    that in some cases where single line strings are used,
    it might also be that, however rare, users want to use
    multi-line text instead. This is why, though designed
    for single-line editing, this widget also allows
    multi-line editing by pressing Ctrl-T.

    For instance, check this function call:

        function(**{key: value})

    Where 'key' must always be a string, but can be any
    string, including an empty one and also a multi-line
    one (one with one or more line separator characters).

    We don't know why Python allows this and we don't
    think this is bad design either, but since keys
    from dicts used in such way can indeed be multi-line
    strings as well, and we use entry widgets to
    represent such keys, it was only natural, given
    our desire to be as close as possible to Python
    design, that we also allow multi-line editing in
    the entry widget so that the user can add such text
    in that keys (and anywhere else) if so desired.

    Furthermore, Python doesn't make distinction between
    empty, single-line or multi-line strings, they are
    all the same type. We think this is an even stronger
    argument for allowing text editing of all kinds
    whenever strings are concerned.

    This is why we plan to merge the textbutton widget
    with this one, so that text editing of all kinds
    is encompassed in a single widget.
    """

    def __init__(
        self,
        value="",
        loop_holder=None,
        font_height=ENC_SANS_BOLD_FONT_HEIGHT,
        font_path=ENC_SANS_BOLD_FONT_PATH,
        width=155,
        name="string_entry",
        command=empty_function,
        validation_command=None,
        formatting_command=return_untouched,
        update_behind=empty_function,
        draw_behind=empty_function,
        draw_on_window_resize=empty_function,
        coordinates_name="topleft",
        coordinates_value=(0, 0),
        foreground_color=STRING_ENTRY_FG,
        background_color=STRING_ENTRY_BG,
    ):
        """Perform setups and assign data for reuse.

        Parameters
        ==========
        loop_holder (class w/ specific operations or None)
            obj with handle_input-update-draw operations; None
            can also be passed, in which case it means
            the loop holder will be the WindowManager
            class from the module winman.main.
        value (string)
            initial value of the widget.
        font_height (integer)
            desired font height in pixels.
        font_path (string, defaults to "default")
            represents font style. Check local
            font.py module for available styles. In doubt
            use 'default' for default font.
        width (integer)
            width of the widget.
        name (string)
            an arbitrary name to help identify the widget.
        command (callable)
            callable to be executed whenever the value
            changes at the end of an editing session.
        validation_command (None, string or callable)
            if it is None, the instance is set up so that
            no validation is done.

            If it is a string, it must be a key in a
            preset map used to grab a valid command, for
            instance, the name of a built-in "str" method
            to use as the validation command.

            If it is a callable, it must accept a single
            argument and its return value is used to
            determine whether validation passed (when the
            return value is truthy value) or not (when it
            is not truthy).
        formatting_command (callable)
            It must accept a single argument, which is the
            string displayed in the widget, and its return
            value replaces such string in the final value
            of the widget.

            This callable will be used whenever the value
            in the widget is set with self.set.
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
        coordinates_name (string)
            represents attribute name of rect wherein
            to store the position information from the
            coordinates value parameter.
        coordinates_value (2-tuple of integers)
            represents a position in 2d space; the values of
            x and y axes, respectively.
        foreground_color, background_color
            (tuple/list/pygame.color.Color instance)
            A tuple or list of r, g, b values which are
            integers ranging from 0 to 255. For the
            background color, an optional fourth value
            can be passed, which is an integer in the
            same range as the others, representing the
            image opacity (0 for full transparency and
            255 for full opacity).
        """
        ### ensure value argument received is a string

        if type(value) is not str:

            raise TypeError("'value' received must be of 'str' type")

        ### convert the colors passed into tuples for
        ### simplicity (since colors can be given as
        ### instances from other classes like
        ### pygame.Color and builtin lists too)

        background_color = tuple(background_color)
        foreground_color = tuple(foreground_color)

        ### store some of the arguments in their own
        ### attributes

        self.name = name
        self.value = value
        self.command = command
        self.loop_holder = loop_holder
        self.formatting_command = formatting_command

        ### store the validation command (this is a
        ### property with setter implementation which
        ### process the given command and also validates
        ### self.value)
        self.validation_command = validation_command

        ### create and position a rect for this entry

        self.rect = Rect(0, 0, width, font_height)

        setattr(self.rect, coordinates_name, coordinates_value)

        ### create a background surface for the widget

        self.background = render_rect(width, font_height, background_color)

        ### also store a copy of it as the image
        ### representing this widget
        self.image = self.background.copy()

        ### gather the text rendering settings in a
        ### dictionary

        render_settings = {
            "font_height": font_height,
            "font_path": font_path,
            "foreground_color": foreground_color,
            "background_color": background_color,
        }

        ### instantiate the entry cursor class, which is
        ### responsible for holding and managing the text
        ### of the entry during edition (while the actual
        ### value keeps stored in the 'value' attribute,
        ### until the edition in the entry is confirmed
        ### or the value is set with self.set())

        self.cursor = EntryCursor(
            value,
            render_settings,
            self,
            get_contrasting_bw(background_color),
        )

        ### update the surface of the widget
        self.update_image()

        ### store behaviours

        self.update_behind = update_behind
        self.draw_behind = draw_behind

        self.draw_on_window_resize = draw_on_window_resize

        ### define behaviours

        self.draw = super().draw
        self.update = empty_function
        self.handle_input = self.handle_events

    @property
    def validation_command(self):
        return self._validation_command

    @validation_command.setter
    def validation_command(self, validation_command):
        """Setup validation according to received argument.

        Parameters
        ==========
        validation_command (None, string or callable)
            check __init__ method's docstring for more
            info.
        """
        ### check whether the value received is present
        ### in the validation command map

        try:
            command = VALIDATION_COMMAND_MAP[validation_command]

        ### if it is absent, though...

        except KeyError:

            ## use the value as the command itself, if
            ## it is callable

            if callable(validation_command):
                command = validation_command

            ## otherwise, it means no valid validation
            ## command was given

            else:

                msg = (
                    "'validation_command' received invalid"
                    " input: {} (it must be a valid string"
                    " or callable)"
                ).format(repr(validation_command))

                raise ValueError(msg)

        ### check whether the value received is valid

        ## try validating
        try:
            value = command(self.value)

        ## if an exception occurred while validating,
        ## catch the exception and raise a new exception
        ## from it, explaining the context of such
        ## error

        except Exception as err:

            raise RuntimeError(
                "An exception was raised while using the"
                " specified validation command on the"
                " provided value"
            ) from err

        ## if validation works, but the result is false,
        ## raise a value error

        else:

            if not value:

                raise ValueError(
                    "the 'validation_command' received"
                    " doesn't validate the 'value' received."
                )

        ### finally, let's store the validation command
        self._validation_command = command

    def get(self):
        """Return text content of widget."""
        return self.value

    def set(self, value, custom_command=True):
        """Set obj value.

        value (string)
            value to be used as label text.
        """
        ### ensure value argument received is a string

        if type(value) is not str:

            ## report problem
            print("'value' received must be of 'str' type")

            ## exit method by returning early
            return

        ### return earlier if value is already set or
        ### doesn't validate

        if value == self.value or not self.validation_command(value):
            return

        ### otherwise set the value

        ## format the value
        formatted_value = self.formatting_command(value)

        ## store the formatted value in the 'value' attribute
        self.value = formatted_value

        ## set formatted value as the entry text
        self.cursor.set(formatted_value)

        ## update the image
        self.update_image()

        ### also, if requested, execute the custom command
        if custom_command:
            self.command()

    def update_image(self):
        """Update image surface attribute."""
        ### reference objects locally

        image = self.image
        line = self.cursor.line
        topleft = self.rect.topleft

        ### clean image using the background
        image.blit(self.background, (0, 0))

        ### blit character objects from line on the image

        ## align line's topleft with self.rect.topleft
        line.rect.topleft = topleft

        ## store the inverse of self.rect.topleft as an
        ## offset
        offset = -Vector2(topleft)

        ## iterate over character objects colliding with
        ## self.rect, blitting then on the image using
        ## offset copies of their rects

        for obj in line.get_colliding(self.rect):
            image.blit(obj.image, obj.rect.move(offset))

    def handle_events(self):
        """Iterate over event queue processing events."""
        for event in get_events():

            if event.type == QUIT:
                raise QuitAppException

            elif event.type == KEYUP:

                ### exiting the widget by either pressing
                ### escape or enter/numpad enter resumes
                ### the edition

                if event.key in (K_ESCAPE, K_RETURN, K_KP_ENTER):
                    self.resume_editing()

            elif event.type == KEYDOWN:

                ### ignore keys below

                if event.key in (K_ESCAPE, K_RETURN, K_KP_ENTER):
                    pass

                ### move cursor

                elif event.key == K_LEFT:
                    self.cursor.go_left()

                elif event.key == K_RIGHT:
                    self.cursor.go_right()

                ### snap cursor to different edges of
                ### line

                elif event.key == K_HOME:
                    self.cursor.go_to_beginning()

                elif event.key == K_END:
                    self.cursor.go_to_end()

                ### remove characters

                elif event.key == K_BACKSPACE:

                    if event.mod & KMOD_CTRL:
                        self.cursor.delete_previous_word()

                    else:
                        self.cursor.delete_previous()

                elif event.key == K_DELETE:
                    self.cursor.delete_under()

                ### responses to keydown events when the
                ### control key is pressed

                elif event.mod & KMOD_CTRL:

                    ### edit entry text in text editor

                    if event.key == K_t:
                        self.edit_on_text_editor()

                    ### in all other scenarios, the event
                    ### must be ignored, since the
                    ### combination of ctrl key and other
                    ### keys doesn't produce characters
                    ### of our interest (only strings like
                    ### '\x08', etc.)
                    else:
                        pass

                ### if the keydown event has a non-empty
                ### string as its unicode attribute, add
                ### such string as text (character)

                elif event.unicode:
                    self.cursor.add_text(event.unicode)

            ### releasing either the left or right button
            ### of the mouse out of the widget boundaries
            ### resumes the edition

            elif event.type == MOUSEBUTTONUP:

                if event.button in (1, 3):

                    if not self.rect.collidepoint(event.pos):
                        self.resume_editing()

            ### if window is resized, set handle_input
            ### to a new callable that keeps handling
            ### events and at the same time watches out
            ### for movement of the widget

            elif event.type == WINDOW_RESIZE_EVENT_TYPE:

                self.handle_input = self.watch_out_for_movement

    def watch_out_for_movement(self):

        if self.rect.topleft != self.last_topleft:

            diff = Vector2(self.rect.topleft) - self.last_topleft

            self.last_topleft = self.rect.topleft

            self.cursor.rect.move_ip(diff)
            self.cursor.line.rect.move_ip(diff)

            ##
            self.handle_input = self.handle_events

            ##
            self.draw_on_window_resize()
            self.draw_focused()

        self.handle_events()

    def update_focused(self):
        """Update widget state."""
        self.update_behind()
        self.cursor.update()

    def draw_focused(self):
        """Draw objects.

        Extends Object2D.draw.
        """
        ### draw objecs behind entry
        self.draw_behind()

        ### clean image
        self.image.blit(self.background, (0, 0))

        ### draw cursor and characters
        self.cursor.draw()

        ### blit self.image on screen
        super().draw()

        ### finally update the screen (pygame.display.update)
        update()

    def on_mouse_click(self, event):
        """Delegate focus-related setups to get_focus().

        This method is called "on_mouse_click" to
        comply with the mouse interaction protocol.

        Parameters
        ==========
        event
            (pygame.event.Event of pygame.MOUSEBUTTONDOWN
            type)

            although the argument is not used, it is
            required in order to comply with protocol
            used; when needed it can be used to retrieve
            the position of the mouse click, for instance.

            Check pygame.event module documentation on
            pygame website for more info about this event
            object.
        """
        self.get_focus()

    def get_focus(self):
        """Perform setups and get focus to itself.

        "Getting focus" means assuming control of the
        application loop.
        """
        ### assign behaviours

        self.update = self.update_focused
        self.draw = self.draw_focused
        self.handle_input = self.handle_events

        ### align line topleft with self.rect.topleft and
        ### move cursor to the end of the contents

        self.cursor.line.rect.topleft = self.rect.topleft
        self.cursor.go_to_end()

        ### store topleft left position for later
        ### reference if needed
        self.last_topleft = self.rect.topleft

        ### give focus to self by raising a manager switch
        ### exception with a reference to this widget
        raise SwitchLoopException(self)

    def lose_focus(self):
        """Focus loop holder.

        That is, restore control of the application loop
        back to the loop holder.
        """
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

        If the contents in the entry are equal to the actual
        value stored, we just get out of the widget (lose
        focus).

        Otherwise, we check whether such contents are valid.
        If not, we restore the original value. If it is,
        we perform tasks to store it.
        """
        ### retrieve the entry text
        entry_text = self.cursor.get()

        ### if contents are equal to value, just update
        ### the image (so that it doesn't contain
        ### the outline of the cursor in it)

        if entry_text == self.value:
            self.update_image()

        ### if the contents changed, though, we must check
        ### if it is valid and perform extra setups
        ### depending on that

        else:

            ## if contents are valid, store the contents
            ## as the value of the widget, update the image,
            ## then execute the custom command

            if self.validation_command(entry_text):

                # format contents
                formatted_value = self.formatting_command(entry_text)

                # set formatted value as entry text
                self.cursor.set(formatted_value)

                # set formatted value as value
                self.value = formatted_value

                # update the image (it is important to do
                # this before executing the command, since
                # the command is given by the user and we
                # never know which effect it may have)
                self.update_image()

                # execute the custom command
                self.command()

            ## otherwise set the entry text to the
            ## current value and update the image

            else:

                # since text on cursor is different from
                # self.value, set self.value as its text
                self.cursor.set(self.value)

                # udpate image
                self.update_image()

        ### finally we lose focus
        self.lose_focus()

    def edit_on_text_editor(self):
        """Edit the entry text in the text editor."""
        ### retrieve the text in the entry
        entry_text = self.cursor.get()

        ### edit it on text editor
        text = edit_text(entry_text)

        ### if there is an edited text (if it is not None,
        ### it means the user confirmed the edition in the
        ### text editor) and it is different from the entry
        ### text originally used, set such text as the text
        ### of the entry

        if text is not None and text != entry_text:
            self.cursor.set(text)

        ### regardless of whether the new text was set as
        ### the entry text or not, we resume the entry's
        ### editing session
        self.resume_editing()

    def get_expected_type(self):
        return str

    def svg_repr(self):
        """Return svg group element representing widget.

        Overrides Object2D.svg_repr().
        """
        line = self.cursor.line
        line.rect.topleft = self.rect.topleft

        text = "".join(obj.text for obj in line.get_colliding(self.rect))

        rect = self.rect

        x_str, y_str, width_str, height_str = map(str, rect)

        ###

        group = Element("g", {"class": "string_entry"})

        group.append(
            Element(
                "rect",
                {
                    "x": x_str,
                    "y": y_str,
                    "width": width_str,
                    "height": height_str,
                },
            )
        )

        (
            text_x_str,
            text_y_str,
        ) = map(str, rect.move(0, -3).bottomleft)

        text_element = Element(
            "text",
            {
                "x": text_x_str,
                "y": text_y_str,
                "text-anchor": "start",
            },
        )

        text_element.text = text

        group.append(text_element)

        return group
