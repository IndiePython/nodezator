"""Facility for text editing."""

### standard library import
from functools import partial


### third-party imports

from pygame import Rect

from pygame.display import update

from pygame.draw import rect as draw_rect

from pygame.math import Vector2


### local imports

from ...config import APP_REFS

from ...pygameconstants import (
    SCREEN_RECT,
    maintain_fps,
    FPS,
    blit_on_screen,
)

from ...dialog import create_and_show_dialog

from ...ourstdlibs.collections.general import CallList

from ...our3rdlibs.behaviour import watch_window_size

from ...surfsman.cache import UNHIGHLIGHT_SURF_MAP

from ...classes2d.single import Object2D
from ...classes2d.collections import List2D

from ...surfsman.draw import draw_border
from ...surfsman.render import render_rect

from ...surfsman.icon import render_layered_icon

from ...colorsman.colors import (
    BLACK,
    WHITE,
    WINDOW_FG,
    WINDOW_BG,
    BUTTON_FG,
    BUTTON_BG,
    CONTRAST_LAYER_COLOR,
)

from ..render import render_text

from ...fontsman.constants import (
    ENC_SANS_BOLD_FONT_HEIGHT,
    ENC_SANS_BOLD_FONT_PATH,
    FIRA_MONO_BOLD_FONT_HEIGHT,
    FIRA_MONO_BOLD_FONT_PATH,
)

from ..label.main import Label

from .cursor.main import Cursor

from .constants import (
    TEXT_EDITOR_RECT,
    EDITING_AREA_RECT,
)


### XXX
### use the label at the bottom to show info just like vim
### does: info like where the cursor is, the percentage
### of the text you're navigating, etc. (it could also be
### used in the future as a prompt for a command mode)


class TextEditor(Object2D):
    """Manages text edition session.

    This class is instantiated only once and its
    edit_text() method is referenced in this module
    so it can be imported wherever needed in the
    entire package (check the last line in this module).
    """

    def __init__(self):
        """Setup rect and image and build structure."""
        ### store rect and build image from it

        self.rect = TEXT_EDITOR_RECT

        self.image = render_rect(*self.rect.size, WINDOW_BG)

        ### draw black border around self.image
        draw_border(self.image, color=BLACK, thickness=1)

        ### create widgets which compose the text editor
        self.create_widgets()

        ### center text editor and append centering method
        ### as window resize setup

        self.center_text_editor()

        APP_REFS.window_resize_setups.append(self.center_text_editor)

    def center_text_editor(self):

        diff = Vector2(SCREEN_RECT.center) - self.rect.center

        self.rect.center = SCREEN_RECT.center

        EDITING_AREA_RECT.move_ip(diff)

        self.line_number_x = self.rect.left + 20

        ## reference each button so we can position them
        ok_button, cancel_button = self.buttons

        ok_button.rect.bottomright = self.rect.move(-10, -10).bottomright

        cancel_button.rect.bottomright = ok_button.rect.move(-10, 0).bottomleft

        ##
        self.statusbar.rect.bottomleft = self.rect.move(10, -10).bottomleft

        ##

        if hasattr(self, "cursor"):

            self.cursor.rect.move_ip(diff)

            if self.cursor.visible_lines:
                self.cursor.visible_lines.rect.move_ip(diff)

    def create_widgets(self):
        """Create widgets used in operations."""
        ### store semitransparent object the size of
        ### self.rect

        self.rect_size_semitransp_obj = Object2D.from_surface(
            surface=render_rect(
                ## size and color of rect
                *self.rect.size,
                (*CONTRAST_LAYER_COLOR, 130),
            ),
            ## position info
            coordinates_name="center",
            coordinates_value=self.rect.center,
        )

        ### create buttons

        ## create special list to store buttons
        self.buttons = List2D()

        ## instantiate and store buttons

        for text in ("Ok", "Cancel"):

            # instantiate

            button = Object2D.from_surface(
                render_text(
                    text,
                    ## text settings
                    font_height=ENC_SANS_BOLD_FONT_HEIGHT,
                    padding=5,
                    foreground_color=BUTTON_FG,
                    background_color=BUTTON_BG,
                    depth_finish_thickness=1,
                )
            )

            # store
            self.buttons.append(button)

        ## reference each button so we can set their
        ## behaviour
        ok_button, cancel_button = self.buttons

        ## set ok_button behaviour
        ok_button.invoke = self.confirm

        ## set cancel_button behaviour

        cancel_button.invoke = CallList(
            [
                partial(setattr, self, "text", None),
                partial(setattr, self, "running", False),
            ]
        )

        ### blit icon and title text on background

        ## icons

        text_icon = render_layered_icon(
            chars=[chr(ordinal) for ordinal in (37, 36)],
            dimension_name="height",
            dimension_value=26,
            colors=[BLACK, WHITE],
        )

        self.image.blit(text_icon, (10, 10))

        pencil_icon = render_layered_icon(
            chars=[chr(ordinal) for ordinal in range(115, 119)],
            dimension_name="height",
            dimension_value=21,
            colors=[BLACK, (255, 225, 140), (255, 255, 0), (255, 170, 170)],
        )

        self.image.blit(pencil_icon, (20, 20))

        ## title

        midleft = (40, 22)

        title_obj = Object2D.from_surface(
            surface=(
                render_text(
                    "Text editor",
                    ## text settings
                    font_height=ENC_SANS_BOLD_FONT_HEIGHT,
                    foreground_color=WINDOW_FG,
                    padding=5,
                )
            ),
            ## position info
            coordinates_name="midleft",
            coordinates_value=midleft,
        )

        title_obj.draw_on_surf(self.image)

        ### create a label object to use as a statusbar,
        ### displaying extra info about user' actions

        self.statusbar = Label(
            "Welcome to the text editor",
            ## text settings
            font_height=FIRA_MONO_BOLD_FONT_HEIGHT,
            font_path=FIRA_MONO_BOLD_FONT_PATH,
            foreground_color=WINDOW_FG,
            background_color=WINDOW_BG,
        )

    def clean_editing_area(self):
        """Blit bg color over editing area to clean it."""
        ### reference topleft coordinates of text editor
        x, y = self.rect.topleft

        ### obtain a rect which covers the editing area
        ### plus the lineno area

        area_to_clean = Rect(
            ## left is the same as the text editor's, but
            ## one pixel to the right
            TEXT_EDITOR_RECT.left + 1,
            ## top is same as editing area's, but one pixel
            ## higher
            EDITING_AREA_RECT.top - 1,
            ## the width is the same as the text editor's,
            ## but 2 pixels shorter
            TEXT_EDITOR_RECT.width - 2,
            ## height is same as editing area's, but 2 pixels
            ## higher
            EDITING_AREA_RECT.height + 2,
            ## we move the resulting rect by the opposite of
            ## the topleft of the self.rect.topleft (the
            ## text editor rect), which makes it so the
            ## rect position represents its position relative
            ## to the text editor rect, rather than relative
            ## to the screen)
        ).move(-x, -y)

        ### now finally use the rect to blit the background
        ### color over the blitting area in order to clean it

        draw_rect(self.image, WINDOW_BG, area_to_clean)

    def paint_editing_and_lineno_areas(self, area_bg_color, lineno_bg_color):
        """Draw editing area on self.image.

        Parameters
        ==========
        area_bg_color (3-tuple/list or pygame.color.Color)
            represent the rgb values of the color used
            to fill the editing area.
        lineno_bg_color (3-tuple/list or pygame.color.Color)
            represent the rgb values of the color used
            to fill the area surrounding the line numbers.
        """
        ### paint editing area

        ## reference topleft coordinates of text editor
        x, y = self.rect.topleft

        ## blit editing area on the self.image

        # obtain rect equal to editing area, but positioned
        # relative to the origin of the text editor surface
        offset_editing_area = EDITING_AREA_RECT.move(-x, -y)

        # now add just a bit of padding to the left of
        # this area by changing the left coordinates and
        # width

        offset_editing_area.left += -5
        offset_editing_area.width += 5

        # fill the area with the color for the background
        # of the text editing area

        draw_rect(self.image, area_bg_color, offset_editing_area)

        ## draw an outline for the editing area as well

        # define outline rect
        editing_outline = offset_editing_area.inflate(2, 2)

        # draw it
        draw_rect(self.image, BLACK, editing_outline, 1)

        ### paint lineno area

        ## define lineno area

        lineno_area = (
            ## left is 10 pixels to the left of the text
            ## editor
            10,
            ## top is the same as the top from the outline of
            ## the editing area
            editing_outline.top,
            ## our width goes from the left of text editor
            ## rect, which is zero, to the left of the outline
            ## for the editing area, but since we added 10
            ## to our left as can be seen above, we subtract
            ## 10 here to compensate
            editing_outline.left - 10,
            ## height is the same as the height from the
            ## outline of the editing area
            editing_outline.height,
        )

        ## fill line number area
        draw_rect(self.image, lineno_bg_color, lineno_area)

        ## outline line number area
        draw_rect(self.image, BLACK, lineno_area, 1)

    def edit_text(
        self,
        text="",
        font_path=ENC_SANS_BOLD_FONT_PATH,
        validation_command=None,
        syntax_highlighting="",
    ):
        """Edit given text.

        Parameters
        ==========

        text (string)
            text to be edited.
        font_path (string)
            indicates the font style to be used when
            editing the contents; defaults to
            ENC_SANS_BOLD_FONT_PATH, which uses the normal
            font of the app. You can use
            FIRA_MONO_BOLD_FONT_PATH, to edit text
            representing code using a monospace font.
        validation_command (None or callable)
            if it is None, the instance is set up so that
            no validation is done;

            if it is a callable, it must accept a single
            argument and its return value is used to
            determined whether validation passed (when the
            return value is truthy) or not (when it is not
            truthy).
        syntax_highlighting (string)
            represents the name of a syntax used to
            highlight the text (for instance, 'python');
            if an empty string, which is the default value,
            or the name of an unsupported syntax is given,
            syntax highlighting is disabled;
            if, otherwise, the argument indicates a
            supported syntax, syntax highlighting is
            enabled and we use it to highlight the text
            when rendering it;
            even when the syntax highlight is enabled,
            though, the highlighting may fail, for instance,
            if there's a syntax error in the text; in such
            case, the text is rendered with no highlighting
            at all, but highlighting goes back to normal
            once the syntax error is solved;
            none of this is performed/managed here, though,
            but instead in the Cursor instance, to which we
            pass this argument.
        """
        ### blit a screen-size semitransparent surface in
        ### the canvas to increase constrast

        blit_on_screen(UNHIGHLIGHT_SURF_MAP[SCREEN_RECT.size], (0, 0))

        ### instantiate and store cursor in its own attribute,
        ### also referencing it locally (the text is stored
        ### and handled in the cursor instance)

        cursor = self.cursor = Cursor(
            text_editor=self,
            text=text,
            font_path=font_path,
            syntax_highlighting=syntax_highlighting,
        )

        ### set text attribute to None
        self.text = None

        ### process validation command
        self.validation_command = validation_command

        ### loop until running attribute is set to False

        self.running = True

        while self.running:

            maintain_fps(FPS)

            watch_window_size()

            ### perform the GUD operations;
            ###
            ### note that, rather than using a single
            ### loop holder, both the cursor and text editor
            ### provide GUD operations together

            ## execute handle_input() and update() operations
            ## from the cursor object

            cursor.handle_input()
            cursor.update()

            ## execute drawing operation from the text editor
            self.draw()

        ### blit the self.rect-size semitransparent obj
        ### over the screen to leave the self.rect
        ### temporarily darkened in case it keeps showing
        ### even after leaving this text editor (in some
        ### cases the loop holder which called this
        ### method might not care to update the area of the
        ### screen previously occupied by this color picker,
        ### making it so it keeps appearing as if it was
        ### still active on the screen)
        self.rect_size_semitransp_obj.draw()

        ### since we won't need the objects forming
        ### the text anymore, we clear all text-related
        ### objects in the cursor, to free memory
        cursor.free_up_memory()

        ### return text attribute
        return self.text

    @property
    def validation_command(self):
        """Return stored validation command."""
        return self._validation_command

    @validation_command.setter
    def validation_command(self, validation_command):
        """Setup validation according to received argument.

        Parameters
        ==========
        validation_command (None  or callable)
            check __init__ method's docstring for more
            info.
        """
        ### if validation_command is None, validation
        ### always passes, no matter what value is set

        if validation_command is None:
            command = lambda value: True

        ### if it is a callable, it is used.

        elif callable(validation_command):
            command = validation_command

        ### otherwise, it isn't a legal value, so raise
        ### an error

        else:

            raise ValueError("'validation_command' argument isn't" " an allowed value.")

        ### finally, check whether the text received
        ### is valid and store the command on the
        ### appropriate attribute

        ## retrieve text
        text = self.cursor.get_text()

        ## check text

        # try validating
        try:
            result = command(text)

        # if an exception occurred while validating,
        # catch the exception and raise a new exception
        # from it, explaining the context of such
        # error

        except Exception as err:

            raise RuntimeError(
                "An exception was raised while using the"
                " specified validation command on the"
                " provided text"
            ) from err

        # if validation works and result is false,
        # raise a value error

        else:

            if not result:

                raise ValueError(
                    "the 'validation_command' received"
                    " doesn't validate the 'text' received."
                )

        ## finally, let's store the validation command
        self._validation_command = command

    def draw(self):
        """Process events, draw widgets and update screen."""
        ### draw self.image (background)
        super().draw()

        ### draw lines which appear on editing area and
        ### the cursor
        self.cursor.draw_visible_lines_and_self()

        ### draw buttons
        self.buttons.draw()

        ### draw statusbar
        self.statusbar.draw()

        ### update screen (pygame.display.update)
        update()

    def mouse_release_action(self, mouse_pos):
        """Invoke colliding button, if any.

        Parameters
        ==========
        mouse_pos (2-tuple of integers)
            represents mouse position on x and y axes,
            respectively.
        """
        ### check if click was meant to invoke a button

        for button in self.buttons:

            if button.rect.collidepoint(mouse_pos):

                button.invoke()
                break

    def confirm(self):
        """Assign content to data if valid and finish editing.

        Triggered when users press the 'confirm' button
        to signal they finished editing the data.
        """
        ### retrieve text from cursor
        text = self.cursor.get_text()

        ### try validating text
        try:
            text_validates = self.validation_command(text)

        ### if text doesn't validate, user is notified

        except Exception as err:

            create_and_show_dialog(
                (
                    "Can't confirm edition cause text"
                    " doesn't validate. Here's the error"
                    f" message >> {err.__class__.__name__}:"
                    f" {err}"
                ),
                level_name="error",
            )

        ### otherwise...

        else:

            ### if the text validates it is assigned to the text
            ### attribute and we trigger the end of the looping by
            ### setting the running flag to False

            if text_validates:

                self.text = text
                self.running = False

            ### otherwise we notify the user

            else:

                create_and_show_dialog(
                    "Text doesn't validate.",
                    level_name="info",
                )


edit_text = TextEditor().edit_text
