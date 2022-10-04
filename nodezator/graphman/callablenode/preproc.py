"""Facility for callable preprocessing."""

### standard library imports

from collections import OrderedDict

from copy import deepcopy

from inspect import Parameter


### local imports

from ...config import APP_REFS

from ..presets import (
    PARAM_ANNOTATION_PRESET_MAP,
    OUTPUT_ANNOTATION_PRESET_MAP,
)

from ..widget.utils import get_widget_metadata

from ..validation.main import (
    check_return_annotation_mini_lang,
)


class Preprocessing:
    """Preprocessing methods for the node class."""

    ### create a set to reference callables which were
    ### already preprocessed
    preprocessed_callables = set()

    ### create a map to store variable parameter
    ### information for each callable
    callables_var_kind = {}

    ### create a map to store parameter defaults
    ### information for each callable
    callables_defaults = {}

    ### create a map to store parameter types information
    ### for each callable
    callables_types = {}

    ### create a map to store widget customization
    ### information for non-variable parameters in each
    ### callable
    callables_widgets = {}

    ### create a map to store output name/output type pairs
    ### of data in the order they appear on the node
    callables_ordered_output_types = {}

    def inspect_callable_object(self, signature_callable):
        """Inspect callable object, storing resulting data.

        signature_callable (callable obj)
            callable used in the node.

        Works by checking the callable and its metadata
        creating new class attributes to hold the resulting
        data for easier access across other node instances
        as well.
        """
        ## reference class locally, since it is accessed
        ## multiple times
        cls = self.__class__

        ## initialize needed objects before iterating
        ## over parameters

        # create a map to store names of parameters of
        # variable kind; the map associates such names
        # to a string indicating the specific variable
        # kind (positional or keyword)
        var_kind_map = {}

        # create a map to store names of parameters
        # to which default values were assigned;
        # the map associates such names to the default
        # values
        default_map = {}

        # create a map to store types of parameters;
        # the map associates parameter names to their
        # respective types
        type_map = {}

        # create a map to store names of parameters
        # for which widget metadata (customizations)
        # were defined;
        # the map associates such names to the widget
        # customization data
        widget_meta = {}

        ## obtain the signature object
        signature_obj = self.get_signature()

        ## alias the parameter objects in the signature
        ## object 'parameters' ordered dict
        parameters = signature_obj.parameters.values()

        ## iterate over each parameter of the callable,
        ## performing specific setups

        for param_obj in parameters:

            ## retrieve data from the parameter obj

            param_name = param_obj.name
            default = param_obj.default
            annotation = param_obj.annotation
            kind = param_obj.kind

            ## take specific measures according to
            ## whether or not the parameter is of
            ## variable kind and the specific variable
            ## kind if so

            # assign "var_pos" to var_kind_map if
            # parameter is of positional variable kind

            if kind is param_obj.VAR_POSITIONAL:
                var_kind_map[param_name] = "var_pos"

            # assign "var_key" to var_kind_map if
            # parameter is of keyword variable kind

            elif kind is param_obj.VAR_KEYWORD:
                var_kind_map[param_name] = "var_key"

            ## check whether the annotation is actually
            ## a key to access a parameter annotation
            ## preset

            # if it is, use the preset as the annotation
            # itself
            try:
                annotation = PARAM_ANNOTATION_PRESET_MAP[annotation]

            # if not just ignore
            except (TypeError, KeyError):
                pass

            # also deepcopy the annotation, so the preset
            # isn't shared among other parameters
            else:
                annotation = deepcopy(annotation)

            ## check whether the annotation is a dict providing
            ## a 'type' key, in which case, the value in the 'type'
            ## key must be considered the actual type to be used
            if isinstance(annotation, dict) and "type" in annotation:
                type_ = annotation["type"]

            ## otherwise, consider the annotation itself as the type
            else:
                type_ = annotation

            ## regardless of the origin of the type_
            ## variable obtained, store it in the
            ## type_map
            type_map[param_name] = type_

            ## if a default value is valid (one which
            ## is not a sentinel value)...

            if default is not Parameter.empty:

                ## store it in the default map
                default_map[param_name] = default

                ## use the default value along with the
                ## annotation to define a widget;
                ## this way the user can edit the value
                ## in the editor whenever desired, or
                ## at least be able to see it;

                ## process the gathered data to produce
                ## suitable data to instantiate a
                ## widget

                widget_meta[param_name] = get_widget_metadata(annotation, default)

        ## store the var_kind_map in a map from a class
        ## attribute, so other instances can access it
        cls.callables_var_kind[signature_callable] = var_kind_map

        ## store the default_map in a map from a class
        ## attribute, so other instances can access it
        cls.callables_defaults[signature_callable] = default_map

        ## store the type_map in a map from a class
        ## attribute, so other instances can access it
        cls.callables_types[signature_callable] = type_map

        ## store the widget_meta in a map from a class
        ## attribute, so other instances can access it
        cls.callables_widgets[signature_callable] = widget_meta

        ## process the output metadata of the
        ## callable (if any) using the signature
        ## return annotation

        # create a map to store types of outputs
        # by order of appearance on the node (as
        # define by the user or default setting);
        # the map associates output names to their
        # respective types; also alias it to a
        # variable of low character count for better
        # code layout;
        #
        # oot_map means ordered output type map
        oot_map = OrderedDict()

        # retrieve the return annotation
        return_annotation = signature_obj.return_annotation

        ## check whether the return annotation is actually
        ## a key to access an output annotation preset

        # if it is, use the preset as the annotation
        # itself
        try:
            return_annotation = OUTPUT_ANNOTATION_PRESET_MAP[return_annotation]

        # if not just ignore
        except (TypeError, KeyError):
            pass

        # check whether the annotation adopts a
        # specific mini language
        try:
            check_return_annotation_mini_lang(return_annotation)

        # if type or value errors are raised, then it
        # means no mini language is adopted, so we just
        # store the return annotation in a key
        # named 'output'
        except (ValueError, TypeError):
            oot_map["output"] = return_annotation

        # otherwise, we can treat the return annotation
        # as extra metadata provided by the user about
        # the callable outputs

        else:

            ### rename the return_annotation to a more
            ### meaningful variable name; each of this
            ### list's items is a dictionary with
            ### metadata for an output;
            outputs_metadata = return_annotation

            ### populate the ordered output with the
            ### names (as keys) and types (as values)
            ### in the provided order

            for output_data in outputs_metadata:

                ## retrieve name
                name = output_data["name"]

                ## store type using name as key and
                ## Parameter.empty as default value in
                ## case the type wasn't specified

                oot_map[name] = output_data.get("type", Parameter.empty)

        ## store the ordered output type map in another
        ## map from a class attribute, so other
        ## instances can access it

        (cls.callables_ordered_output_types[signature_callable]) = oot_map

        ## since we finished preprocessing the callable
        ## object, we can store a reference to it in
        ## the preprocessed_callables set so it isn't
        ## processed again
        cls.preprocessed_callables.add(signature_callable)

    def reference_related_maps(self, signature_callable):
        """Reference maps from class attributes in instance.

        The maps are related to the callable obj of the
        node instance and are referenced for easier access.
        """
        ### reference class locally, since it is accessed
        ### multiple times
        cls = self.__class__

        ## var_kind_map
        self.var_kind_map = cls.callables_var_kind[signature_callable]

        ## default_map
        self.default_map = cls.callables_defaults[signature_callable]

        ## type_map
        self.type_map = cls.callables_types[signature_callable]

        ## widget meta
        self.widget_meta = cls.callables_widgets[signature_callable]

        ## signature obj
        self.signature_obj = self.get_signature()

        ## ordered_output_type_map

        self.ordered_output_type_map = cls.callables_ordered_output_types[
            signature_callable
        ]

    def set_data_defaults(self):
        """Set default values for missing node data.

        Works by using the dict.setdefault method to check
        the existence of specific fields, providing default
        values so they can be inserted on the spot in case
        the value checked is missing.
        """
        ### define a tuple containing pairs of field name
        ### plus default value to be provided to the
        ### dict.setdefault method

        field_default_pairs = (
            ## the 'param_widget_value_map' field maps
            ## strings representing each parameter's
            ## widget to its respective value as defined
            ## by the user in the last editing session
            ("param_widget_value_map", {}),
            ## map listing existing subparams; subparams are
            ## informal parameters (those created to fill
            ## variable parameters, *args and **kwargs);
            ## this map uses the name of each variable
            ## parameter in the callable (if it has) as
            ## a key; the key points to a list containing
            ## indices for subparameters created (if they
            ## exist);
            ("subparam_map", {}),
            ## the 'subparam_widget_map' field maps strings
            ## representing variable-kind parameters to data
            ## describing an embedded widget for each of
            ## their subparameters which have one;
            ## this is only used when editing the node layout
            ## in the visual editor
            ("subparam_widget_map", {}),
            ## the 'subparam_keyword_map' field maps strings
            ## representing the name of subparameters
            ## of a keyword-variable parameter to strings
            ## representing their respective keyword
            ("subparam_keyword_map", {}),
            ## the 'subparam_unpacking_map' field maps
            ## strings representing variable-kind parameters
            ## to a list of indices representing the
            ## subparametes which are unpacked when the
            ## graph is executed
            ("subparam_unpacking_map", {}),
        )

        ### iterate over pairs, passing them to the node
        ### data 'setdefault' method

        for field_name, default in field_default_pairs:
            self.data.setdefault(field_name, default)

    ### though part of the methods above, the methods
    ### below are isolated so they can be overridden
    ### by subclasses

    def get_signature(self):

        return APP_REFS.signature_map[self.signature_callable]
