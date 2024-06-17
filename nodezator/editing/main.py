"""Facility to mediate between window and graph manager."""

### local imports

from ..config import APP_REFS

from ..ourstdlibs.meta import initialize_bases

## class extensions

from .gridlogic import GridHandling
from .objinsert import ObjectInsertionRemoval
from .selection import SelectionHandling
from .reposition import Repositioning
from .data import DataHandling
from .birdseyeview import BirdsEyeViewHandling

## more operations

from .imageexport.main import export_as_image
from .imageexport.form import reset_image_filename

from .pythonexporting import export_as_python, view_as_python

from .categorycolors import (
    rebuild_category_color_form,
    change_category_colors,
)

from .nodepacksforms.selection import present_change_node_packs_form

from .nodepacksforms.renaming import present_rename_node_packs_form

from .jumptonode import present_jump_to_node_form


from .playback.record import set_session_recording
from .playback.play import set_session_playing
from .playback.demonstrate import set_demonstration_session
from .playback.systemtesting import (
    set_system_testing_session,
    rerun_previous_test_session,
    run_all_cases_at_max_speed,
)

## classes for composition

from .widgetpopups.creation import WidgetCreationPopupMenu

from .objpopups.callablenode import CallableNodePopupMenu

from .objpopups.proxynode import ProxyNodePopupMenu

from .objpopups.operatornode import OperatorNodePopupMenu

from .objpopups.textblock import TextBlockPopupMenu

from .socketpopups.input import InputSocketPopupMenu

from .socketpopups.proxy import ProxySocketPopupMenu

from .socketpopups.output import OutputSocketPopupMenu



class EditingAssistant(
    GridHandling,
    ObjectInsertionRemoval,
    SelectionHandling,
    Repositioning,
    DataHandling,
    BirdsEyeViewHandling,
):
    """Assist objects operations like selection/positioning.

    This class was specifically designed so that its
    instance assists the graph manager by handling
    operations which are not inherently related to node
    management, but rather with management of visual
    components.

    In other words, this class was intended to do or
    trigger the majority of the frontend work while the
    graph manager handles the backend.
    """

    def __init__(self):
        """Store references."""
        ### reference itself on APP_REFS
        APP_REFS.ea = self

        ### store reference to callables to allow category
        ### color picking

        self.change_category_colors = change_category_colors

        self.rebuild_category_color_form = rebuild_category_color_form

        ### store calls to exporting forms

        self.export_as_image = export_as_image
        self.export_as_python = export_as_python
        self.view_as_python = view_as_python

        ### store calls to present forms

        self.present_rename_node_packs_form = present_rename_node_packs_form
        self.present_change_node_packs_form = present_change_node_packs_form

        self.present_jump_to_node_form = present_jump_to_node_form

        self.set_session_recording = set_session_recording
        self.set_session_playing = set_session_playing
        self.set_demonstration_session = set_demonstration_session
        self.set_system_testing_session = set_system_testing_session

        ### store extra call related to system testing

        self.rerun_previous_test_session = rerun_previous_test_session
        self.run_all_cases_at_max_speed = run_all_cases_at_max_speed

        ### create and store popup menus

        ## widget-related

        self.widget_creation_popup_menu = WidgetCreationPopupMenu()

        ## objects

        self.callable_node_popup_menu = CallableNodePopupMenu()

        self.proxy_node_popup_menu = ProxyNodePopupMenu()

        self.operator_node_popup_menu = OperatorNodePopupMenu()

        self.text_block_popup_menu = TextBlockPopupMenu()

        ## sockets

        self.input_socket_popup_menu = InputSocketPopupMenu()

        self.proxy_socket_popup_menu = ProxySocketPopupMenu()

        self.output_socket_popup_menu = OutputSocketPopupMenu()

    def prepare_for_new_session(self):
        """Execute setups to assist in editing."""
        ### execute __init__ method of base classes;
        ###
        ### that is, of the base classes which have a custom
        ### __init__ method
        initialize_bases(self)

        ### rebuild category color picking form
        self.rebuild_category_color_form()

        ### reset default filename for image to be exported
        ### in the image exporting form
        reset_image_filename()
