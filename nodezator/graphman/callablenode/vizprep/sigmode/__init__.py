"""Class extension for preparation of visual objects."""

### local imports

from .....ourstdlibs.collections.fldict.main import FlatListDict

from .....classes2d.single import Object2D

from .....rectsman.main import RectsManager

from ....socket.surfs import type_to_codename


## classes for composition

from ....socket.output import OutputSocket

from .....rectsman.main import RectsManager


## functions for injection

from .param import create_parameter_objs

from .varparam import create_var_parameter_objs



class SignatureModeVisualPreparations():
    """Manages creation and setup of node visuals for signature mode."""

    ### extend class by injecting functions

    create_parameter_objs = create_parameter_objs
    create_var_parameter_objs = create_var_parameter_objs

    ### define remaining methods

    def create_exp_mode_visual_elements(self):
        """Create visual elements for node's expanded signature mode."""
        ### create input related widgets
        self.create_input_related_objects()

        ### create output sockets
        self.create_output_sockets()

        ### reposition all objects within the node (also
        ### sets height of self.rect)
        self.reposition_expanded_elements()

        ### also create and store a rects manager to
        ### control all the rects in the node

        ## create a list containing the rects to be managed
        ## and get its __iter__ method to use as a callable
        ## which returns the rects to be managed by the
        ## rects manager instance

        all_rects = [
            self.rect,
            self.top_rectsman,
            self.sigmode_toggle_button.rect,
            self.title_text_obj.rect,
            self.body.rect,
            self.id_text_obj.rect,
            self.output_rectsman,
            self.bottom_rectsman,
        ]

        get_all_rects = all_rects.__iter__

        ## if there are parameters, add the input rectsman to the list

        if self.signature_obj.parameters.values():
            all_rects.append(self.input_rectsman)

        ## use the callable to instantiate the rects
        ## manager and then store it
        self.exp_rectsman = RectsManager(get_all_rects)

    def create_col_mode_visual_elements(self):
        """Create visual elements for node's expanded signature mode."""

        ### create and store a rects manager to control all the rects in
        ### the node

        ## create a list containing the minimum rects to be managed
        ## and get its __iter__ method to use as a callable
        ## which returns the rects to be managed by the
        ## rects manager instance

        all_rects = [
            self.rect,
            self.top_rectsman,
            self.sigmode_toggle_button.rect,
            self.title_text_obj.rect,
            self.body.rect,
            self.id_text_obj.rect,
            self.bottom_rectsman,
        ]

        get_all_rects = all_rects.__iter__

        ## use the callable to instantiate the rects
        ## manager and then store it
        self.col_rectsman = RectsManager(get_all_rects)

        ### store a copy of the list to represent rects whose
        ### objects are never collapsed
        self.not_collapsible_rects = all_rects.copy()

        ### create lists to hold visible input and output sockets

        self.visible_input_sockets = []
        self.visible_output_sockets = []

        ### create a list to hold rects of visible unpacking icons
        self.visible_unpacking_icon_rects = []

        ### create lists to temporarily hold references to disconnected
        ### input sockets

        self.disconnected_param_input_sockets = []
        self.disconnected_subparam_input_sockets = []

    def create_input_related_objects(self):
        """Create objects representing the node' inputs."""
        ### create maps to hold button instances
        ### for subparameters and for placeholder sockets

        self.widget_remove_button_flmap = FlatListDict()
        self.placeholder_add_button_map = {}

        self.subparam_up_button_flmap = FlatListDict()
        self.subparam_down_button_flmap = FlatListDict()

        ### instantiate a special input socket map to hold
        ### input socket instances
        self.input_socket_live_flmap = FlatListDict()

        ### instantiate a placeholder socket map to hold
        ### placeholder socket instances
        self.placeholder_socket_live_map = {}

        ### instantiate a dict to hold widget instances
        self.widget_live_flmap = FlatListDict()

        ### instantiate a dict to hold objects indicating
        ### that a subparameter must be unpacked when
        ### the node is executed
        self.subparam_unpacking_icon_flmap = FlatListDict()

        ### instantiate a subparam keyword live map to
        ### hold entry widget instances representing
        ### keywords for subparameters of a
        ### keyword-variable parameter
        self.subparam_keyword_entry_live_map = {}

        ### regarding some of the maps created earlier, also store
        ### their 'flat_values' attribute or '.values()'
        ### view in dedicated attributes for easier access
        ### to their values

        self.subparam_up_buttons = self.subparam_up_button_flmap.flat_values

        self.subparam_down_buttons = self.subparam_down_button_flmap.flat_values

        self.placeholder_sockets = self.placeholder_socket_live_map.values()

        self.placeholder_add_buttons = self.placeholder_add_button_map.values()

        self.live_widgets = self.widget_live_flmap.flat_values

        self.widget_remove_buttons = self.widget_remove_button_flmap.flat_values

        self.unpacking_icons = self.subparam_unpacking_icon_flmap.flat_values

        self.live_keyword_entries = self.subparam_keyword_entry_live_map.values()

        ### create and store a map to hold rects manager
        ### instances for each group of objects related to
        ### a specific parameter
        param_rectsman_map = self.param_rectsman_map = {}

        ### create and store a map to hold rects manager
        ### instances for each group of objects related to
        ### a specific subparameter
        self.subparam_rectsman_map = {}

        ### create a list to hold instances of visible widgets (widgets are
        ### visible when there are no connections to the corresponding
        ### input socket)
        self.visible_widgets = []

        ### create a list to hold instances of remove widget buttons
        self.visible_remove_widget_buttons = []

        ### iterate over each parameter, instantiating its
        ### related widgets

        parameters = self.signature_obj.parameters.values()

        for param_obj in parameters:

            ## manage socket(s) and widget(s) creation
            ## for parameter depending on whether the
            ## parameter is of variable kind or not

            if param_obj.name in self.var_kind_map:
                self.create_var_parameter_objs(param_obj)

            else:
                self.create_parameter_objs(param_obj)

            ## also create a parameter rectsman to manage rects
            ## in the parameter
            param_rectsman_map[param_obj.name] = RectsManager([].__iter__)

        ### execute the update method on the maps created,
        ### so the list in their flat_values attribute is
        ### updated

        self.input_socket_live_flmap.update()
        self.widget_live_flmap.update()

        ### if there are indeed parameters, create a rects
        ### manager instance to control the position of all
        ### the input related objects

        if parameters:

            get_param_rectsmans = [
                item for item in self.param_rectsman_map.values()
            ].__iter__

            self.input_rectsman = RectsManager(get_param_rectsmans)

        ### update values in flat list dict instances
        ### related to subparameters

        self.widget_remove_button_flmap.update()

        self.subparam_up_button_flmap.update()
        self.subparam_down_button_flmap.update()

    def create_output_sockets(self):
        """Instantiate and store output sockets."""
        ### create a new dictionary holding output socket
        ### instances mapped to the name of the output
        ### they represent (also reference it locally);
        ###
        ### here we use key-value pairs from the ordered
        ### output map, which is an ordered dict where
        ### each key is the name of the output and the
        ### value is the expected type of the output to be
        ### sent;
        ###
        ### the value is called "expected type" because
        ### the type isn't enforced, it only serves to
        ### indicate which type to expected, just like
        ### regular type hints in Python, but in this
        ### case for return values instead of parameters

        self.output_socket_live_map = {
            output_name: OutputSocket(
                node=self,
                output_name=output_name,
                type_codename=(type_to_codename(expected_type)),
            )
            for output_name, expected_type in self.ordered_output_type_map.items()
        }

        ### gather the rects of the output sockets in a list
        ### in order to use its __iter__ method to create a
        ### rects manager instance which you'll use to
        ### control the rects (and thus the position of the
        ### sockets

        ## reference output sock live map locally
        osl_map = self.output_socket_live_map

        ## create mentioned list

        rect_list = [
            osl_map[output_name].rect
            for output_name in self.ordered_output_type_map.keys()
        ]

        ## finally, instantiate and store the rects
        ## manager
        self.output_rectsman = RectsManager(rect_list.__iter__)
