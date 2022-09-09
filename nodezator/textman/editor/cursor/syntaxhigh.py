"""Syntax highlighting setups and operations."""

### third-party import
from pygame.time import get_ticks as get_pygame_msecs


### local imports

from ....ourstdlibs.behaviour import empty_function

from ....ourstdlibs.color.creation import get_contrasting_bw

from ....syntaxman.exception import SyntaxMappingError

from ....syntaxman.utils import (
    AVAILABLE_SYNTAXES,
    SYNTAX_TO_MAPPING_FUNCTION,
    get_ready_theme,
)

from ....fontsman.constants import FIRA_MONO_BOLD_FONT_PATH

from ..constants import (
    SANS_FONT_SETTINGS,
    MONO_FONT_SETTINGS,
)


### number of milliseconds to wait after last text edition
### before mapping syntax highlighting (and applying it to
### visible lines)
MSECS_TO_UPDATE_SYNTAX = 500


### class definition


class SyntaxHighlighting:
    """Operations/setups for syntax highlighting support."""

    def set_syntax_highlighting(self, font_path, syntax_highlighting):
        """Perform syntax highlighting setups.

        Depends on the requested syntax highlighting,
        which might also be an empty string, meaning
        syntax highlighting must be disabled.

        Requesting the highlighting of a syntax which is
        not available has the same effect as passing an
        empty string.

        If syntax highlighting is enabled, we also attempt
        to highlight the text at this step. Check the
        update_syntax_highlight_data() and
        syntax_highlight_visible_lines() methods to see
        how this happens.

        Parameters
        ==========

        font_path (string)
            indicates the font style to be used when
            editing the contents; defaults to ENC_SANS_BOLD_FONT_PATH,
            which uses the normal font of the app; you can
            use FIRA_MONO_BOLD_FONT_PATH, to edit text in monospace font
            (to edit code for instance).
        syntax_highlighting (string)
            represents the name of a syntax used to
            highlight the text (for instance, 'python');
            if an empty string, or the name of an
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
            once the syntax problem is solved;
        """
        ### set syntax highlighting behaviour depending on
        ### requested syntax highlighting

        ### if a valid syntax is requested...

        if syntax_highlighting in AVAILABLE_SYNTAXES:

            ## define the default settings depending on the
            ## font style

            default_text_settings = (
                MONO_FONT_SETTINGS
                if font_path == FIRA_MONO_BOLD_FONT_PATH
                else SANS_FONT_SETTINGS
            )

            ## store a theme map ready for usage with the
            ## syntax name and default settings

            self.theme_map = get_ready_theme(syntax_highlighting, default_text_settings)

            ## store specific syntax mapping behaviour
            self.get_syntax_map = SYNTAX_TO_MAPPING_FUNCTION[syntax_highlighting]

            ## set routines so syntax highlighting is
            ## enabled

            self.syntax_highlighting_routine = self.check_syntax_highlighting

            self.edition_routine = self.mark_edition_time

            self.visible_lines_routine = self.syntax_highlight_visible_lines

            ### create a control variable to keep track of
            ### the time when the text was last edited
            self.last_edition_msecs = 0

            ### map and apply the syntax highlighting in the
            ### text

            self.update_syntax_highlight_data()
            self.syntax_highlight_visible_lines()

            ### define foreground and background colors for
            ### the line numbers

            ## define text settings for the line numbers

            # reference the theme text settings locally
            theme_text_settings = self.theme_map["text_settings"]

            # if the line number settings from the theme
            # are available, use them
            try:
                lineno_settings = theme_text_settings["line_number"]

            # otherwise use the settings for normal text of
            # the theme for the line number settings

            except KeyError:

                lineno_settings = theme_text_settings["normal"]

            ## store the colors

            self.lineno_fg = lineno_settings["foreground_color"]

            self.lineno_bg = lineno_settings["background_color"]

            ### define the background color for the text
            self.background_color = self.theme_map["background_color"]

        ### otherwise, no syntax highlighting is applied,
        ### but other setups are needed

        else:

            ### we set routines so that no syntax
            ### highlighting is ever performed

            self.syntax_highlighting_routine = (
                self.edition_routine
            ) = self.visible_lines_routine = empty_function

            ### we define line number settings from the
            ### default text settings for monospaced text

            self.lineno_fg = MONO_FONT_SETTINGS["foreground_color"]

            self.lineno_bg = MONO_FONT_SETTINGS["background_color"]

            ### and also define the background color for
            ### the editing area

            self.background_color = (
                MONO_FONT_SETTINGS
                if font_path == FIRA_MONO_BOLD_FONT_PATH
                else SANS_FONT_SETTINGS
            )["background_color"]

        ### finally, define either black or white as the
        ### color for the cursor, whichever contrasts more
        ### with the current background color used
        self.cursor_color = get_contrasting_bw(self.background_color)

    def check_syntax_highlighting(self):
        """Trigger syntax highlighting update, if suitable."""
        ### if the last time when an edition was performed
        ### isn't stored (it is set to 0), it indicates
        ### that no changes were performed, so there is no
        ### point in updating the syntax highlighting data;
        ### therefore, we cancel the operation by returning
        if not self.last_edition_msecs:
            return

        ### otherwise, there were changes, so we check
        ### wether the pre-defined delay between the last
        ### change and the present time has elapsed;
        ###
        ### if such time already elapsed, we reset the
        ### last_edition_msecs to 0, then update the syntax
        ### highlighting and apply it in the visible lines

        if get_pygame_msecs() - self.last_edition_msecs > MSECS_TO_UPDATE_SYNTAX:

            self.last_edition_msecs = 0

            self.update_syntax_highlight_data()
            self.syntax_highlight_visible_lines()

    def mark_edition_time(self):
        """Mark current time as the last edition time."""
        ### mark current time, which represents the time
        ### at which the most recent change was made in the
        ### text
        self.last_edition_msecs = get_pygame_msecs()

    def update_syntax_highlight_data(self):
        """Map and store syntax highlight data for text."""
        ### try mapping the syntax, generating data to help
        ### identify different parts of the text
        try:
            self.highlight_data = self.get_syntax_map(self.get_text())

        ### if the syntax mapping fails, for instance, due
        ### to a syntax error, create data that maps all
        ### contents as if they were normal text;
        ###
        ### this serves as an indicator for the user that
        ### the text has a syntax error;
        ###
        ### additionally, this error might also be caused by
        ### a bug in the syntax mapping function, so if
        ### the error occurs with text known to have no
        ### syntax errors, the mapping function should be
        ### checked;

        except SyntaxMappingError:

            self.highlight_data = {
                ## store a dict item where the line index is
                ## the key and another dict is the value
                line_index: {
                    ## in this dict, an interval representing
                    ## the indices of all items of the line
                    ## (character objects) is used as the
                    ## key, while the 'normal' string is used
                    ## as value, indicating that all content
                    ## must be considered normal text
                    (0, len(line)): "normal"
                }
                ## for each line_index and respective line
                for line_index, line in enumerate(self.lines)
                ## but only if the line isn't empty
                if line
            }

    def syntax_highlight_visible_lines(self):
        """Apply syntax highlighting to visible lines."""
        ### if the last_edition_msecs isn't 0, it means
        ### there are changes yet to be taken into account,
        ### that is, the syntax highlighting data is
        ### outdated;
        ###
        ### in such case,  we abort the execution of
        ### the rest of this method by returning earlier
        if self.last_edition_msecs:
            return

        ### otherwise we go on and apply the syntax
        ### highlighting to the visible lines

        ## reference the theme text settings and
        ## highlight data locally, for quicker and easier
        ## access

        theme_text_settings = self.theme_map["text_settings"]
        highlight_data = self.highlight_data

        ## iterate over the visible lines and their indices,
        ## highlighting their text according to the
        ## highlighting data present

        for line_index, line in enumerate(
            self.visible_lines, start=self.top_visible_line_index
        ):

            ## try popping out the interval data from the
            ## highlight data dict with the line index

            try:
                interval_data = highlight_data.pop(line_index)

            ## if there is no such data, skip iteration
            ## of this item
            except KeyError:
                continue

            ## otherwise, we take needed measures so the
            ## interval data is used to highlight the
            ## text of the line

            # iterate over the interval data, which consists
            # of interval/category name pairs, with the
            # intervals further decomposed into their
            # start and ending indices

            for (
                (including_start, excluding_end),
                category_name,
            ) in interval_data.items():

                # retrieve the text settings for the
                # category
                category_text_settings = theme_text_settings[category_name]

                # each index in the interval represents
                # the index of a character object;
                #
                # iterate over such indices, applying the
                # text settings corresponding to the syntax
                # category to the character in each index

                for char_index in range(including_start, excluding_end):

                    line[char_index].change_text_settings(category_text_settings)
