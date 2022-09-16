"""Facility to mediate between window and graph manager."""

### local imports

from ..config import APP_REFS

from ..ourstdlibs.meta import initialize_bases

## class extensions

from .gridlogic import GridHandling
from .objinsert import ObjectInsertionRemoval
from .selection import SelectionHandling
from .reposition import Repositioning
from .export.main import Exporting
from .data import DataHandling

## more operations

from .categorycolors import (
    rebuild_category_color_form,
    change_category_colors,
)

## classes for composition

from .nodepacksforms.selection import (
    present_change_node_packs_form,
)

from .nodepacksforms.renaming import (
    present_rename_node_packs_form,
)

from .widgetpopups.creation import (
    WidgetCreationPopupMenu,
)

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
    Exporting,
    DataHandling,
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

        ### store calls to present forms
        self.present_rename_node_packs_form = present_rename_node_packs_form
        self.present_change_node_packs_form = present_change_node_packs_form

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
