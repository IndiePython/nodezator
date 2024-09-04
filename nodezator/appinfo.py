"""General info for the app, including versioning."""

### standard library import
from collections import namedtuple


### application version;
###
### the release level can be...
###
### 'beta' : changes are being implemented or were
###          just implemented, but not enough tests
###          were performed yet;
###
### 'release_candidate' : can be released, should not
###                       be used in production, though;
###
### 'stable' : can be used in production; bugs,
###            if existent, are considered tolerable;

AppVersion = namedtuple("AppVersion", "major minor micro release_level")

APP_VERSION = AppVersion(1, 5, 1, "release_candidate")


### titles for the application

TITLE = "Nodezator"

## used to name directories related to the app, like
## the config and log folders; it is important in
## case the title ever uses a name with characters not
## supported by any major operating system;
APP_DIR_NAME = "nodezator"

ORG_DIR_NAME = 'IndiePython' # org name for pygame.system.get_pref_path

ABBREVIATED_TITLE = "NDZ"


## custom title formats;


FULL_TITLE = "{} {} ({})".format(
    TITLE, ".".join(str(i) for i in APP_VERSION[:3]), APP_VERSION[3]
)

NO_RELEASE_LEVEL_FULL_TITLE = "{} {}".format(
    TITLE,
    ".".join(str(i) for i in APP_VERSION[:3]),
)

### other

WEBSITE_NAME = "nodezator.com"
WEBSITE_URL = "https://nodezator.com"

### file extension used for native files;
###
### the '.' character must be part of the extension,
### because we also use the NATIVE_FILE_EXTENSION with
### pathlib.Path.with_suffix, which raises an error
### if '.' isn't present
NATIVE_FILE_EXTENSION = ".ndz"


### node script constants

NODE_SCRIPT_NAME = "__main__.py"

MAIN_CALLABLE_VAR_NAME = "main_callable"

VIEWER_NODE_RELATED_VAR_NAMES = (

    SIDEVIZ_AND_OUTPUT_BACKDOOR_VAR_NAME,
    LOOPVIZ_SIDEVIZ_AND_OUTPUT_BACKDOOR_VAR_NAME,

    SIDEVIZ_FROM_OUTPUT_VAR_NAME,
    LOOPVIZ_FROM_OUTPUT_VAR_NAME,

    CUSTOM_VIEWER_LOOP_VAR_NAME,

) = (

    "sideviz_and_output_backdoor",
    "loopviz_sideviz_and_output_backdoor",

    "get_sideviz_from_output",
    "get_loopviz_from_output",

    "enter_viewer_loop",

)

LOOP_INDICATIVE_VAR_NAMES = (
    LOOPVIZ_SIDEVIZ_AND_OUTPUT_BACKDOOR_VAR_NAME,
    LOOPVIZ_FROM_OUTPUT_VAR_NAME,
)

BACKDOOR_INDICATIVE_VAR_NAMES = (
    SIDEVIZ_AND_OUTPUT_BACKDOOR_VAR_NAME,
    LOOPVIZ_SIDEVIZ_AND_OUTPUT_BACKDOOR_VAR_NAME,
)

OUTPUT_INSPECTING_VAR_NAMES = (
    SIDEVIZ_FROM_OUTPUT_VAR_NAME,
    LOOPVIZ_FROM_OUTPUT_VAR_NAME,
)


NODE_DEF_VAR_NAMES = (

    MAIN_CALLABLE_VAR_NAME,
    "signature_callable",
    "substitution_callable",
    "call_format",
    "stlib_import_text",
    "third_party_import_text",
    *VIEWER_NODE_RELATED_VAR_NAMES,
)

### node packs constants
NODE_CATEGORY_METADATA_FILENAME = ".metadata.pyl"

### native file keys

NODES_KEY = "nodes"
PARENT_SOCKETS_KEY = "parent_sockets"
TEXT_BLOCKS_KEY = "text_blocks"
