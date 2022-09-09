"""Facility for node class definition."""

### local imports

from ...config import APP_REFS

## class extensions

from .preproc import Preprocessing

from .vizprep.main import VisualRelatedPreparations

from .vizop.main import VisualRelatedOperations

from .subparam.main import SubparameterHandling

from .execution import Execution

from .export import Exporting


class CallableNode(
    Preprocessing,
    VisualRelatedPreparations,
    VisualRelatedOperations,
    SubparameterHandling,
    Execution,
    Exporting,
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
        self.reference_related_maps(signature_callable)

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

        ### create visuals of the node
        self.create_visual_elements()

        ### initialize execution-related objects
        self.create_execution_support_objects()
