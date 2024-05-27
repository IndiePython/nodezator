"""Facility for node class definition."""

### local imports

from ...config import APP_REFS

from ...ourstdlibs.behaviour import empty_function
from ...our3rdlibs.behaviour import indicate_unsaved


## class extensions

from .preproc import Preprocessing

from .vizprep.main import VisualPreparations

from .vizop.main import VisualOperations

from .subparam.main import SubparameterHandling

from .segment import SegmentOperations

from .execution import Execution

from .export import Exporting

from .outputviz import OutputVisualization


##
from .surfs import SIGMODE_TOGGLE_BUTTON_MAP



EMPTY_TUPLE = ()


class CallableNode(
    Preprocessing,
    VisualPreparations,
    VisualOperations,
    SubparameterHandling,
    SegmentOperations,
    Execution,
    Exporting,
    OutputVisualization,
):
    """Stores and manages a callable state.

    This object is used to manage gathering, storage and
    processing of data by its underlying callable and its
    related metadata. Such callable is provided upon
    instantiation.

    Additional instance state is provided as an argument
    called "data", also received upon instantiation.
    """

    ### XXX ponder: instead of making a method like this
    ### one which goes out of its way to meet requirements
    ### of two different use cases, it would most likely
    ### be more pythonic/elegant to create a second
    ### constructor using a class method; it would be
    ### simpler/easier to maintain too; edit: I'm not
    ### sure this applies anymore, I must review
    ### the sections of code using this piece of code,
    ### which are the graph manager when first
    ### instantiating the callable nodes and the editing
    ### assistant, when creating nodes in response to
    ### input from the user

    def __init__(
        self,
        node_defining_object,
        data,
        midtop=None,
    ):
        """Setup attributes for storage and control.

        Parameters
        ==========

        node_defining_object (dict)
            contains callable(s) which the node will
            represent.
        data (dict)
            data representing this node instance.
        midtop (2-tuple of integers; or None)
            represents the absolute midtop position of
            the node on screen. If no midtop is received
            (the default None is used), then the midtop
            information is retrieved from the node data.
        """
        ### store the node defining object and the
        ### callables it contains;
        ###
        ### note that the signature callable is also
        ### referenced locally for easier and quick access

        self.node_defining_object = node_defining_object

        main_callable = self.main_callable = node_defining_object["main_callable"]

        signature_callable = self.signature_callable = node_defining_object[
            "signature_callable"
        ]

        ##

        try:
            substitution_callable = node_defining_object["substitution_callable"]

        except KeyError:
            pass

        else:
            self.substitution_callable = substitution_callable

        ### unless a call format text is given, set
        ### the main callable name as the text for the
        ### nodes title

        try:
            call_format = node_defining_object["call_format"]

        except KeyError:
            self.title_text = main_callable.__name__

        else:
            self.title_text = call_format

        ### store import statements from node defining
        ### object, if present

        for key in (
            "stlib_import_text",
            "third_party_import_text",
        ):

            try:
                text = node_defining_object[key]
            except KeyError:
                pass
            else:
                setattr(self, key, text)

        ### perform inspections/setups related to the
        ### signature callable and its metadata as needed

        ## the inspection is performed only once for each
        ## different signature callable. Thus, if another
        ## node instance is created with the same
        ## signature callable, it will use the already
        ## created data, shared through class attributes

        if signature_callable not in self.__class__.preprocessed_callables:
            self.inspect_callable_object(signature_callable)

        ### reference maps from class attributes in
        ### instance; maps are related to the signature
        ### callable and are shared accross all node
        ### instances which such signature callable obj
        self.reference_related_data(signature_callable)

        ### store the instance data argument in its own
        ### attribute and check whether there's data needed
        ### to be set in the instance data

        self.data = data
        self.set_data_defaults()

        ### store script id on node's data
        data["script_id"] = node_defining_object["script_id"]

        ### store the id in its own attribute for easy
        ### access
        self.id = self.data["id"]

        ### store the midtop position

        self.midtop = midtop if midtop is not None else self.data["midtop"]

        ### create control to indicate when the node was
        ### subject to mouse click
        self.mouse_click_target = False

        ### create visuals for node
        self.create_visual_elements()

        ### perform additional setups, if functions from one of the
        ### viewer node protocols are available
        self.check_preview_objects()

        ### set mode

        self.set_mode(
            self.data.get('mode', 'expanded_signature'),
            indicate_changes=False,
            first_setup=True
        )

        ### initialize execution-related objects
        self.create_execution_support_objects()

    def set_mode(self, mode_name, indicate_changes=True, first_setup=False):

        current_mode_name = self.data.get('mode', 'expanded_signature')

        ### if this is not the first mode setup and the requested and
        ### current mode are the same, prevent the method to execute by
        ### exiting

        if not first_setup and mode_name == current_mode_name:
            return

        ### set mode

        if mode_name == 'expanded_signature':

            if current_mode_name == 'callable':
                APP_REFS.gm.sever_all_connections(self)

            self.adjust_sigmode_toggle_button(mode_name)

            self.reposition_elements = self.reposition_expanded_elements
            self.create_body_surface = self.get_expanded_body_surface

            self.input_sockets = self.input_socket_live_flmap.flat_values
            self.output_sockets = self.output_socket_live_map.values()

            self.yield_mouse_aware_objects = self.yield_mouse_aware_objects_in_expmode
            self.yield_visible_objects = self.yield_visible_objects_in_expmode
            self.yield_visible_sockets = self.yield_visible_sockets_in_expmode

            self.rectsman = self.exp_rectsman

            self.draw_on_surf = self.expanded_draw_on_surf
            self.mode_dependent_elements_svg_repr = self.expanded_elements_svg_repr

        elif mode_name == 'collapsed_signature':

            if current_mode_name == 'callable':
                APP_REFS.gm.sever_all_connections(self)

            self.adjust_sigmode_toggle_button(mode_name)

            self.reposition_elements = self.reposition_collapsed_elements
            self.create_body_surface = self.get_collapsed_body_surface

            self.input_sockets = self.visible_input_sockets
            self.output_sockets = self.visible_output_sockets

            self.yield_mouse_aware_objects = self.yield_mouse_aware_objects_in_colmode
            self.yield_visible_objects = self.yield_visible_objects_in_colmode
            self.yield_visible_sockets = self.yield_visible_sockets_in_colmode

            self.rectsman = self.col_rectsman

            self.draw_on_surf = self.collapsed_draw_on_surf
            self.mode_dependent_elements_svg_repr = self.collapsed_elements_svg_repr

        elif mode_name == 'callable':

            if current_mode_name in {'expanded_signature', 'collapsed_signature'}:
                APP_REFS.gm.sever_all_connections(self)

            self.create_body_surface = self.get_callable_body_surface
            self.reposition_elements = self.reposition_callable_elements

            self.input_sockets = EMPTY_TUPLE
            self.output_sockets = self.callable_output_sockets

            self.yield_mouse_aware_objects = self.yield_mouse_aware_objects_in_calmode
            self.yield_visible_objects = self.yield_visible_objects_in_calmode
            self.yield_visible_sockets = self.yield_visible_sockets_in_calmode

            self.rectsman = self.cal_rectsman

            self.draw_on_surf = self.callable_draw_on_surf
            self.mode_dependent_elements_svg_repr = self.callable_elements_svg_repr

        ###
        self.data['mode'] = mode_name

        ###
        self.reposition_elements()
        self.setup_body()
        ###

        self.perform_mode_related_viewer_setups(
            mode_name,
            current_mode_name,
            first_setup
        )

        ### if requested, indicate that changes were made and that
        ### the birdseye view state of window manager must have its
        ### objects updated next time it is set

        if indicate_changes:

            indicate_unsaved()
            APP_REFS.ea.must_update_birdseye_view_objects = True

    def adjust_sigmode_toggle_button(self, mode_name):

        button = self.sigmode_toggle_button
        button.rect.topleft = self.top_rectsman.move(2, 0).bottomleft

        if mode_name == 'expanded_signature':
            surf_index = 0
        elif mode_name == 'collapsed_signature':
            surf_index = 1

        button.image = SIGMODE_TOGGLE_BUTTON_MAP[self.category_color][surf_index]

    def perform_mode_related_viewer_setups(
        self,
        mode_name,
        previous_mode_name,
        first_setup,
    ):

        ###

        if not hasattr(self, 'preview_panel'):
            return

        ###

        self.anchor_viewer_objects = (

            ##
            empty_function
            if mode_name == 'callable'

            ##
            else self.anchor_viewer_objects_to_node

        )

        ###

        if mode_name == 'expanded_signature':
            self.get_anchor_pos = self.get_anchor_below_output

        elif mode_name == 'collapsed_signature':
            self.get_anchor_pos = self.get_anchor_below_visible_output

        ###

        if mode_name == 'callable':

            if not first_setup:
                self.hide_preview_objects()

        else:

            self.anchor_viewer_objects()

            if first_setup or (previous_mode_name == 'callable'):
                self.show_preview_objects()

    def show_popup_menu(self, pos):
        APP_REFS.ea.callable_node_popup_menu.show(self, pos)

