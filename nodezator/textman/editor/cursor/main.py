"""Facility for text cursor definition."""

### standard library import
from string import digits


### third-party import
from pygame import Rect


### local imports

from ....surfsman.cache import EMPTY_SURF

from ....userprefsman.main import USER_PREFS

from ....classes2d.collections import List2D

from ....fontsman.constants import FIRA_MONO_BOLD_FONT_PATH

from ...render import render_text

from ..constants import NUMBER_OF_VISIBLE_LINES

from ..line import Line

from .op import GeneralOperations

from .navigation import Navigation
from .syntaxhigh import SyntaxHighlighting

from .modes.normal import NormalMode
from .modes.insert import InsertMode

from ..constants import EDITING_AREA_RECT


### XXX the next time you make a general refactoring of
### this class, separate the modes in a similar way in
### which you separate the window manager states (the
### 'winman' subpackage);
###
### for instance, instead of having multipurpose methods
### like 'navigate', have multiple versions of navigate,
### one for each mode, thus eliminating "if blocks", which
### would only pile up as we implement future new modes;


class Cursor(
    ## general operations
    GeneralOperations,
    Navigation,
    SyntaxHighlighting,
    ## mode related operations
    NormalMode,
    InsertMode,
):
    """Vim-like text cursor.

    Contains controls and behaviour to support operations
    similar to ones present in the Vim editor software.

    For now, only a small subset of such operations is
    implemented.
    """

    ### class attributes

    ## create and store a map to hold surfaces of digits;
    ##
    ## the digit surfaces that we'll add later will be used
    ## to draw the line number beside each visible line;
    ##
    ## note that, despite the name, the digit surf map is
    ## created with a space character in it, which is
    ## mapped to an empty surface; such character is needed
    ## cause we right-justify the line number strings with
    ## space characters when blitting them
    DIGIT_SURF_MAP = {" ": EMPTY_SURF}

    ## also create a class attribute which, once updated,
    ## will represent the width of the digit surfaces;
    ## the digit surfaces will all be created with a
    ## monospaced font, so they'll all have the same width;
    DIGIT_SURF_WIDTH = 0

    ### methods

    def __init__(self, text_editor, text, font_path, syntax_highlighting):
        """Store variables and perform setups.

        Parameters
        ==========
        text_editor (texteditor.main.TextEditor instance)
            object responsible for the loop which
            updates this cursor instance state and the
            states of other related objects from other
            classes.
        text (string)
            text being edited.
        font_path (string)
            indicates the font style to be used when
            editing the contents.
        syntax_highlighting (string)
            represents the name of a syntax used to
            highlight the text (for instance, 'python');
            if an empty string or the name of an
            unsupported syntax is given, syntax highlighting
            is disabled;
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
            the behaviours to enable/disable/manage such
            feature are all set inside the method
            self.set_syntax_highlighting(), called in this
            __init__() method;
            Line.set_normal_render_settings() also
            contributes for rendering normal text,
            regardless of whether such text is highlighted
            or not, also depending on the value of this
            parameter;
        """
        ### store text editor reference
        self.te = text_editor

        ### make syntax_highlighting string lowercase
        ### so users don't need to worry about
        ### capitalization when providing the value
        syntax_highlighting = syntax_highlighting.lower()

        ### set normal render settings based on the
        ### font style and syntax highlighting used

        Line.set_normal_render_settings(font_path, syntax_highlighting)

        ### store the attribute char_height of the Line
        ### class locally
        char_height = Line.char_height

        ### create a rect for the cursor

        ## define an arbitrary width for the rect (we
        ## use a third of the char_height since it looks
        ## good, but this is arbitrary; the cursor assumes
        ## the width of characters under it, so it's width
        ## changes multiple times over the editing session)
        arbitrary_width = char_height // 3

        ## instantiate and store rect

        self.rect = Rect(EDITING_AREA_RECT.topleft, (arbitrary_width, char_height))

        ### create list containing custom objects
        ### representing the lines of text

        self.lines = (
            ## if text is not empty, create a Line object
            ## for the text in each line
            [Line(line_text) for line_text in text.splitlines()]
            if text
            ## otherwise just create a list with a single
            ## empty line
            else [Line("")]
        )

        ### create collections/structures to manage
        ### visible lines

        ## create a special list subclass to hold visible
        ## lines

        self.visible_lines = List2D(self.lines[:NUMBER_OF_VISIBLE_LINES])

        ## define and store fixed y values for the visible
        ## lines

        y = EDITING_AREA_RECT.y

        self.y_values = [y + (char_height * i) for i in range(NUMBER_OF_VISIBLE_LINES)]

        ## define the index of the line among self.lines
        ## which is the first visible line
        self.top_visible_line_index = 0

        ## position each of the visible lines, aligning them
        ## all horizontally with the editing area while at
        ## the same time aligning them vertically with each
        ## of the stored y values for the visible lines

        x = EDITING_AREA_RECT.x

        for y, line in zip(self.y_values, self.visible_lines):
            line.rect.topleft = x, y

        ### additional setups

        ## define controls for rows and columns
        self.visible_row = self.row = self.col = 0

        ## set normal mode behaviour as the handle_input
        ## behaviour
        self.handle_input = self.normal_mode_handling

        ## set syntax highlighting; this may enable or
        ## disable syntax highlighting, depending on the
        ## given arguments
        self.set_syntax_highlighting(font_path, syntax_highlighting)

        ## create and store surfaces to show line number
        self.create_line_number_surfaces()

        ## store maximum number of characters needed
        ## to display the highest line number

        n_of_lines = len(self.lines)
        self.max_char_needed = len(str(n_of_lines))

        ## adjust values of editing area's width and its
        ## left coordinate
        self.adjust_editing_area_left_and_width()

        ## use the reposition method just for the
        ## side-effect of making the cursor assume the size
        ## of the character under it (if there is such
        ## character)
        self.reposition()

        ## if text editor behavior is the default one,
        ## cause the text editor to behave like a simple
        ## textarea-like text editor, instead of using the
        ## vim keybindings;

        if USER_PREFS["TEXT_EDITOR_BEHAVIOR"] == "default":

            ## start the insert text mode
            self.insert_before()

            ## erase statusbar message by setting value to
            ## an empty string
            self.te.statusbar.set("")

    def create_line_number_surfaces(self):
        """Create and store surfaces to show line number."""
        ### iterate over the digits, creating key-value
        ### pairs of each digit and its corresponding
        ### surface;
        ###
        ### each pair is them fed to the update method of
        ### the existing digits surf map

        self.DIGIT_SURF_MAP.update(
            ## key-value pair
            (
                ## the digit (a string)
                digit,
                ## its surface
                render_text(
                    digit,
                    font_height=Line.char_height,
                    font_path=FIRA_MONO_BOLD_FONT_PATH,
                    foreground_color=self.lineno_fg,
                    background_color=self.lineno_bg,
                ),
            )
            ## use each digit
            for digit in digits
        )

        ### also store the width of an arbitrary digit
        ### (here we use zero) in the DIGIT_SURF_WIDTH
        ### class attribute, which we use when blitting
        ### the digit surfaces beside each visible line
        ### in the text editing area;

        self.__class__.DIGIT_SURF_WIDTH = self.DIGIT_SURF_MAP["0"].get_width()
