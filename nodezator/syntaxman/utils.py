"""Syntax-related utilities."""

### local imports

from ..config import SYNTAX_THEMES_DIR

from ..ourstdlibs.pyl import load_pyl

from ..ourstdlibs.dictutils import settings_to_hashable_repr


## syntax mapping functions

from .syntaxes.python.main import get_python_syntax_map

from .syntaxes.comment import get_comment_syntax_map

from .syntaxes.userlog import get_user_log_syntax_map


### constants

## map associating a syntax name to "raw" theme data;
##
## the theme data is stored the way it was loaded, without
## any further processing and thus not ready for usage yet
## (which is why we call it "raw")

RAW_THEMES_MAP = {
    # key is the syntax name
    syntax_name:
    # value is the json contents (a dict) loaded from the
    # path resulting of joining the themes dir with the
    # syntax name and the filename
    load_pyl(str(SYNTAX_THEMES_DIR / syntax_name / filename))
    # data source
    for syntax_name, filename in (
        ## pairs associating a syntax name to the name of the
        ## json file from where to load the theme data (change
        ## name of file here to switch to different themes for
        ## each syntax)
        ("python", "sprinkled_dark.pyl"),
        ("comment", "fresh_eucalyptus_dark.pyl"),
        ("user_log", "message_temperature_dark.pyl"),
    )
}

## dict view containing keywords for available syntaxes
AVAILABLE_SYNTAXES = RAW_THEMES_MAP.keys()

## map to store ready theme data;
##
## associates a syntax name and default text settings
## to data for a theme ready for use;
##
## it is populated on demand by the get_ready_theme()
## function
READY_THEMES_MAP = {}


## map of syntax mapping functions

SYNTAX_TO_MAPPING_FUNCTION = {
    "python": get_python_syntax_map,
    "comment": get_comment_syntax_map,
    "user_log": get_user_log_syntax_map,
}


### functions

## function to return ready theme, meant to be imported
## wherever needed in the app


def get_ready_theme(syntax_name, default_text_settings):
    """Return theme ready for usage.

    Works by retrieving a ready theme from a map and
    returning it. If the theme doesn't exist, its creation
    is delegated to create_ready_theme() and the new theme
    is stored back in the map before being returned at the
    end.

    Parameters
    ==========
    syntax_name (string)
        represents the syntax for which the theme data
        is used.
    default_text_settings (dict)
        text settings used as defaults for values not
        specified in the highlighting settings.
    """
    ### convert the text settings (a dict) to a custom
    ### tuple representing them, so the data is now hashable
    settings_tuple = settings_to_hashable_repr(default_text_settings)

    ### create a custom key by combining the syntax name
    ### with the tuple we just create in a single tuple
    key = (syntax_name, settings_tuple)

    ### try retrieving a ready theme from the ready theme
    ### maps with the key we just created
    try:
        ready_theme = READY_THEMES_MAP[key]

    ### if the key doesn't exist, create a ready theme
    ### for it using the received arguments

    except KeyError:

        ready_theme = READY_THEMES_MAP[key] = create_ready_theme(
            syntax_name, default_text_settings
        )

    ### finally return the ready theme
    return ready_theme


## support function for the get_ready_theme() function
## above


def create_ready_theme(syntax_name, default_text_settings):
    """Create and return a theme by merging text settings.

    That is, we merge general settings with the highlighting
    settings for the syntax to be used (such highlight
    settings are several text settings for different
    kinds of words/text in a specific syntax).

    For instance, in the Python syntax, the highlight
    settings include settings for several kinds of text
    like keywords, built-in functions, etc. Each of these
    groups have specific settings assigned to them in the
    json file for the theme.

    But instead of starting from such specific settings,
    each kind of text starts with the general settings and
    only them we override such settings with the specific
    settings for that group.

    Before using the specific settings, we also assign the
    background color from the theme to the general settings.

    Why not just use the specific settings, then? Because
    the general settings as well as the background color
    represent default values for specific settings that may
    not be present in the specific settings, thus serving as
    a base.

    This is specially important for settings not defined
    on the theme, like font height, which is something
    that usually depends on where the text will be used
    which is why it is not defined on the theme.

    Parameters
    ==========
    syntax_name (string)
        represents the syntax for which the highlighting
        settings will be retrieved.
    default_text_settings (dict)
        text settings to use as defaults for values not
        specified in the highlighting settings.
    """
    ### retrieve the raw theme
    raw_theme = RAW_THEMES_MAP[syntax_name]

    ### retrieve the text settings and background
    ### color from the raw theme

    theme_text_settings = raw_theme["text_settings"]
    background_color = raw_theme["background_color"]

    ### create a new merged settings map by merging
    ### the different text and background settings;
    ### settings with lower priority are merged first,
    ### so those with higher priority can override
    ### them as they are merged into the dict

    merged_settings_map = {
        ## this new dict map each kind of highlighted
        ## text to a dict
        kind_of_text: dict(
            ## the dict is built with the following items:
            ##
            ## 1) the items from the general text settings;
            ## 2) the background color defined for the theme;
            ## 3) the items from the specific settings;
            (
                *default_text_settings.items(),
                ("background_color", background_color),
                *specific_settings.items(),
            )
        )
        ## we grab the kind_of_text (a string) and highlight
        ## settings (a dict) from the theme text settings map
        for kind_of_text, specific_settings in theme_text_settings.items()
    }

    ### now return a new dict with the background of the
    ### raw theme and the new merged settings as the
    ### 'text_settings';
    ###
    ### this dict represents the theme ready for usage

    return {"background_color": background_color, "text_settings": merged_settings_map}
