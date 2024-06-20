"""Facility for window manager class."""

### third-party imports

from pygame import Rect

from pygame.display import set_caption


### local imports

## general widgets and other tools

from ..config import APP_REFS

from ..userprefsman.main import USER_PREFS

from ..dialog import (
    create_and_show_dialog,
    show_dialog_from_key,
)

from ..pygamesetup import SCREEN_RECT, blit_on_screen, reset_caption

from ..appinfo import (
    FULL_TITLE,
    ABBREVIATED_TITLE,
    NATIVE_FILE_EXTENSION,
)

from ..ourstdlibs.path import get_custom_path_repr
from ..ourstdlibs.behaviour import empty_function

from ..ourstdlibs.collections.general import CallList

from ..ourstdlibs.pyl import save_pyl

from ..ourstdlibs.path import save_timestamped_backup

from ..our3rdlibs.userlogger import USER_LOGGER

from ..our3rdlibs.behaviour import set_status_message

from ..logman.main import get_new_logger

from ..fileman.main import select_paths

from ..recentfile import store_recent_file

from ..surfsman.cache import UNHIGHLIGHT_SURF_MAP

from ..surfsman.render import render_rect, render_separator

from ..classes2d.single import Object2D

from ..colorsman.colors import GRAPH_BG, WINDOW_BG, MENU_BG

from ..memoryman import free_up_memory

## widgets/tools for composition

# related to node editing

from ..editing.main import EditingAssistant
from ..graphman.main import GraphManager

from ..graphman.nodepacksissues import (
    get_formatted_local_node_packs,
    get_formatted_installed_node_packs,
    check_local_node_packs,
    check_installed_node_packs,
)

from ..graphman.exception import NODE_PACK_ERRORS

# splash screen
from ..splashscreen.main import SplashScreen


## window manager class/function extensions

from .states.nofile import NoFileState
from .states.loadedfile import LoadedFileState
from .states.segmentdef import SegmentDefinitionState
from .states.segmentsev import SegmentSeveranceState
from .states.movingobject import MovingObjectState
from .states.boxselection import BoxSelectionState
from .states.birdseyeview import BirdsEyeViewState

from .menu import MenuSetup
from .label import MonitorLabelSetup
from .switch import setup_switches

from .fileop import FileOperations



### create logger for module
logger = get_new_logger(__name__)


### constants

STATE_NAMES = (
    'no_file',
    'loaded_file',
    'moving_object',
    'segment_definition',
    'segment_severance',
    'box_selection',
    'birdseye_view',
)

BEHAVIOUR_NAMES = (
    'event_handling',
    'keyboard_input_handling',
    'update',
    'draw',
)


### class definition

class WindowManager(

    ### state-related operations

    NoFileState,
    LoadedFileState,
    SegmentDefinitionState,
    SegmentSeveranceState,
    MovingObjectState,
    BoxSelectionState,
    BirdsEyeViewState,

    ### support operations

    MenuSetup,
    MonitorLabelSetup,
    FileOperations,

):
    """Instantiates widgets and other managers."""

    setup_switches = setup_switches

    def __init__(self):
        """Instantiate support objects and perform setups."""

        logger.info("Instantiating window manager.")

        ### store a reference to the window manager
        ### in the APP_REFS object
        APP_REFS.wm = self

        ### instantiate support objects to
        ### manage/assist different kinds of tasks;
        ###
        ### don't worry about storing references to
        ### them, since they reference themselves
        ### automatically in config.APP_REFS

        GraphManager()
        EditingAssistant()

        self.splash_screen = SplashScreen()

        ### instantiate label widgets
        self.instantiate_labels()

        ### organize state behaviours
        self.build_state_behaviour_map()

        ### attribute to keep track of current state
        self.state_name = ''

        ### set flag indicating whether the mouse is clicked
        self.clicked_mouse = False

        ### create background obj
        self.background = Object2D(rect=Rect(0, 0, 0, 0))

        ### create separator obj
        self.separator = Object2D(rect=Rect(0, 0, 0, 0))

        ### append window resize setup method
        APP_REFS.window_resize_setups.append(self.resize_setups)

    def resize_setups(self):

        self.create_background_surface()
        self.fix_menubar_size()
        self.create_separator_surface()
        self.reposition_labels()

    def prepare_for_new_session(self):
        """Instantiate and set up objects.

        Also takes additional measures to free memory and
        check whether there are issues with the nodes
        directory, in case a file is to be loaded.
        """
        ### first of all free up memory used by data/objects
        ### from a possible previous session, data/objects
        ### that may not be needed anymore
        free_up_memory()

        ### check if a valid filepath sits on 'source_path'
        ### attribute of the APP_REFS object (it means a
        ### file is loaded)
        try:
            APP_REFS.source_path

        ### if not, pick 'no_file' state name
        except AttributeError:
            state_name = "no_file"

        ### otherwise perform setups and add the update
        ### viz widgets to the methods to be executed when
        ### updating the window manager

        else:

            ### check if the local node packs provided in
            ### the file are appropriate, to prevent the
            ### application from crashing if such node
            ### packs don't exist or are somehow faulty

            original_local_node_packs = (
                get_formatted_local_node_packs(APP_REFS.source_path)
            )

            current_local_node_packs = original_local_node_packs.copy()

            local_node_packs_are_ok = True

            while True:

                try:
                    check_local_node_packs(current_local_node_packs)

                except NODE_PACK_ERRORS as err:

                    message = (
                        "One of the provided local node packs"
                        " presented the following issue:"
                        f" {err}; what would you like to do?"
                    )

                    buttons = (
                        ("Select replacement/new path", "select"),
                        ("Cancel loading file", None),
                    )

                    answer = create_and_show_dialog(
                        message,
                        buttons,
                        level_name="warning",
                    )

                    if answer == "select":

                        result = select_paths(
                            caption="Select replacement/new path for local node pack"
                        )

                        if result:

                            current_local_node_packs.remove(err.faulty_pack)

                            replacement = result[0]
                            current_local_node_packs.append(replacement)

                    else:

                        local_node_packs_are_ok = False
                        break

                else:
                    break

            if local_node_packs_are_ok:

                ### if by this point the original node
                ### packs listed have changed, then it is
                ### as if we changed the file, so we save
                ### its current contents before assigning
                ### the new node packs

                if set(current_local_node_packs) != set(original_local_node_packs):

                    APP_REFS.data["node_packs"] = [
                        str(path) for path in current_local_node_packs
                    ]

                    ## pass content from source to backup
                    ## files just like rotating contents
                    ## between log files in Python

                    save_timestamped_backup(
                        APP_REFS.source_path, USER_PREFS["NUMBER_OF_BACKUPS"]
                    )

                    ## save the data in the source,
                    ## since it now have different node
                    ## packs
                    save_pyl(APP_REFS.data, APP_REFS.source_path)

                    ## finally, copy the contents of the
                    ## source to the swap file

                    APP_REFS.swap_path.write_text(
                        APP_REFS.source_path.read_text(encoding="utf-8"),
                        encoding="utf-8",
                    )

            ### check if the "installed" node packs provided in
            ### the file are appropriate, to prevent the
            ### application from crashing if such node
            ### packs can't be found or are somehow faulty

            installed_node_packs = get_formatted_installed_node_packs(
                APP_REFS.source_path
            )

            try:
                check_installed_node_packs(installed_node_packs)
            except NODE_PACK_ERRORS as err:

                message = (
                    "One of the provided node packs"
                    " (the ones supposed to be installed)"
                    " presented the following issue:"
                    f" {err}; aborting loading file now"
                )

                create_and_show_dialog(message, level_name='error')

                installed_node_packs_are_ok = False

            else:
                installed_node_packs_are_ok = True

            if local_node_packs_are_ok and installed_node_packs_are_ok:

                ### try preparing graph manager for
                ### edition
                try:
                    APP_REFS.gm.prepare_for_new_session()

                ### if it fails, report the problem to
                ### user and pick the 'no_file' state name

                except Exception as err:

                    ## do this to signal other method not to
                    ## create extra dependencies
                    del APP_REFS.source_path

                    ## report problem to user

                    show_dialog_from_key("error_while_loading_node_packs_dialog")

                    ## also log it

                    msg = (
                        "Unexpected error(s) while trying to load node"
                        " packs for new session"
                    )

                    logger.exception(msg)

                    USER_LOGGER.error(f"{msg}\n\n{err}")

                    ###
                    state_name = "no_file"

                ### otherwise, perform additional setups
                ### and pick the 'loaded_file' state name

                else:

                    APP_REFS.ea.prepare_for_new_session()

                    if not APP_REFS.temp_filepaths_man.is_temp_path(
                        APP_REFS.source_path
                    ):
                        store_recent_file(APP_REFS.source_path)

                    self.build_app_widgets()

                    state_name = "loaded_file"

            ### otherwise, trigger cancellation of file
            ### loading and pick the 'no_file' state name

            else:

                show_dialog_from_key("cancelled_file_loading_dialog")

                self.clean_loaded_file_data()

                state_name = "no_file"

        ### set the state picked
        self.set_state(state_name)

        ### instantiate support widgets and set manager
        self.build_support_widgets()

        ### check again whether a valid filepath still sits on 'source_path'
        ### attribute of the APP_REFS object (it means a file is loaded)
        try:
            source_path = APP_REFS.source_path

        ### if not, reset caption to its initial state and build log message

        except AttributeError:

            reset_caption()
            log_message = "User started new session with no file loaded"

        ### otherwise, create the popup menu and build log message

        else:

            self.create_canvas_popup_menu()

            log_message = (
                f"User started new session with {source_path} loaded"
            )

        logger.info(log_message)
        USER_LOGGER.info(log_message)

    def build_state_behaviour_map(self):
        """Build map with behaviours for each state."""
        ### create and alias map
        stb_map = self.state_behaviour_map = {}

        ### create and alias a behaviour map for each
        ### state

        for state_name in STATE_NAMES:

            behaviour_map = stb_map[state_name] = {}

            ## for each behaviour name, gather the
            ## corresponding behaviour for the current
            ## state and assign it to the map using
            ## the behaviour name as a key

            for behaviour_name in BEHAVIOUR_NAMES:

                ## build the behaviour name for this
                ## state
                full_behaviour_name = "_".join((state_name, behaviour_name))

                ## retrieve and store the behaviour using
                ## the name you put together; if the
                ## behaviour doesn't exist, an empty
                ## function is used instead

                behaviour_map[behaviour_name] = getattr(
                    self, full_behaviour_name, empty_function
                )

    def set_state(self, state_name):
        """Assign behaviours according to given state.

        Parameters
        ==========
        state_name (string)
            name of state whose behaviours must be set.
        """
        ### get behaviours for given state
        behaviour_map = self.state_behaviour_map[state_name]

        ### assign behaviours to corresponding attributes

        for behaviour_name in BEHAVIOUR_NAMES:

            behaviour = behaviour_map[behaviour_name]
            setattr(self, behaviour_name, behaviour)

        ### gather the created attributes in a 'handle_input'
        ### attribute containing a callable which calls
        ### the gathered behaviours whenever called

        self.handle_input = CallList(
            (self.event_handling, self.keyboard_input_handling)
        )

        ### set state name attribute
        self.state_name = state_name

    def build_support_widgets(self):
        """Build widgets which support operations."""
        ### background surface
        self.create_background_surface()

        ### create the menubar
        self.create_menubar()

        ### instantiate hide/show switches

        try:
            APP_REFS.source_path
        except AttributeError:
            pass
        else:
            self.setup_switches()

        ### separator for aesthetics (placed below
        ### menubar)
        self.create_separator_surface()

    def create_background_surface(self):

        ### background surface

        try:
            APP_REFS.source_path
        except AttributeError:
            bg_color = WINDOW_BG
        else:
            bg_color = GRAPH_BG

        if (
            not hasattr(self.background, 'image')
            or SCREEN_RECT.size != self.background.image.get_size()
        ):

            self.background.image = render_rect(*SCREEN_RECT.size, bg_color)
            self.background.rect.size = self.background.image.get_size()

        else:
            self.background.image.fill(bg_color)

    def fix_menubar_size(self):

        _, height = self.menubar.image.get_size()

        width = SCREEN_RECT.width

        self.menubar.image = render_rect(width, height, MENU_BG)

        self.menubar.rect.width = width

        ##

    def create_separator_surface(self):

        separator = self.separator

        separator.image = render_separator(SCREEN_RECT.width)

        separator.rect.size = self.separator.image.get_size()

        separator.rect.topleft = self.menubar.rect.bottomleft

    def build_app_widgets(self):
        """Build graph management related widgets."""
        ### get a custom string representation for the file
        ### depending on whether it is a temporary file or not

        if APP_REFS.temp_filepaths_man.is_temp_path(
            APP_REFS.source_path
        ):
            path_str = f"untitled{NATIVE_FILE_EXTENSION}"

        else:
            path_str = get_custom_path_repr(APP_REFS.source_path)

        ### update caption to show the loaded path
        self.put_path_on_caption(path_str)

        ### also display loaded path on statusbar
        set_status_message("loaded {}".format(path_str))

    def put_path_on_caption(self, path_str):
        """Update caption with custom formated title.

        Parameters
        ==========
        path_str (string)
            string representing the loaded path.
        """
        full_caption = path_str + " - " + FULL_TITLE
        set_caption(full_caption, ABBREVIATED_TITLE)

    def exit(self):
        """Draw semitransparent surface over screen.

        The goal is to make the screen appear
        unhighlighted, so the next loop holder appears
        highlighted.
        """
        blit_on_screen(UNHIGHLIGHT_SURF_MAP[SCREEN_RECT.size], (0, 0))

    def __repr__(self):
        """Return unambiguous string representation."""
        return "WindowManager()"


perform_startup_preparations = WindowManager().perform_startup_preparations
