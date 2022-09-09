"""Facility for widget related utilities."""

### standard library imports

from inspect import Parameter

from ast import literal_eval


### local imports

## widgets

from ...widget.stringentry import StringEntry

from ...widget.literalentry import LiteralEntry

from ...widget.intfloatentry.main import (
    ALLOWED_NUM_CLASSES,
    IntFloatEntry,
)

from ...widget.textdisplay import TextDisplay
from ...widget.literaldisplay import LiteralDisplay

from ...widget.checkbutton import CheckButton
from ...widget.colorbutton import ColorButton
from ...widget.sortingbutton import SortingButton
from ...widget.defaultholder import DefaultHolder

from ...widget.optionmenu.main import OptionMenu
from ...widget.optiontray.main import OptionTray

from ...widget.pathpreview.path import PathPreview
from ...widget.pathpreview.text import TextPreview
from ...widget.pathpreview.image import ImagePreview
from ...widget.pathpreview.audio import AudioPreview
from ...widget.pathpreview.video import VideoPreview
from ...widget.pathpreview.font import FontPreview


### XXX implement remaining widgets
###
### from our3rdlibs.range import Range
###
### from our3rdlibs.calenderclock import CalendarClock
### (CalendarClock has the functionality of all the
### date/time related widgets listed below (which weren't
### created, and will probably not be anymore, since the
### CalendarClock should be used isntead, once created) in
### this comment, including deltas; there is a design sketch
### on paper on 2020-02-14)
###
### from our3rdlibs.date      import IsoDate
### from our3rdlibs.time      import IsoTime
### from our3rdlibs.datetime  import IsoDateTime
### from our3rdlibs.timedelta import IsoTimeDelta


### constants for usage elsewhere


## define a widget class map

WIDGET_CLASS_MAP = {
    "string_entry": StringEntry,
    "literal_entry": LiteralEntry,
    "int_float_entry": IntFloatEntry,
    "check_button": CheckButton,
    "text_display": TextDisplay,
    "literal_display": LiteralDisplay,
    "color_button": ColorButton,
    "sorting_button": SortingButton,
    "default_holder": DefaultHolder,
    "option_menu": OptionMenu,
    "option_tray": OptionTray,
    "path_preview": PathPreview,
    "text_preview": TextPreview,
    "image_preview": ImagePreview,
    "audio_preview": AudioPreview,
    "video_preview": VideoPreview,
    "font_preview": FontPreview,
}


### main function


### TODO check whether type for widgets in the mini-language
### are all strictly json compatible (be as strict as
### possible; for instance, use lists, not tuples, since
### tuples are converted to lists anyway);


def get_widget_metadata(annotation, default):
    """Return dict w/ instructions for widget instantiation.

    In this function we inspect the annotation and default
    value of a parameter to determine which widget should
    we use to hold and/or change such value in the node
    for that parameter.

    Sometimes, such data provided in the parameter is not
    enough per se to determine the usage of a specific
    widget. Even when this is the case, we defined some
    extra value/annotation combinations that can be
    considered syntax sugar to define a particular widget.

    Even if we cannot define any particular widget in the
    end, we still return a dict with instructions to
    define a "default holder" widget, which is a general
    widget whose sole purpose is holding a string
    representation of the default value.

    Parameters
    ==========
    annotation (any python object)
        represents data to help define a widget.
    default (any python object, except inspect._empty)
        type provided by the user for the given default
        value
    """
    ######## retrieve/inspect data ########

    ### define an empty widget name
    widget_name = ""

    ### if the annotation is a dict instance,
    ### has a non-empty 'widget_name' field
    ### though, treat such dict instance as
    ### extra metadata provided by the user

    if isinstance(annotation, dict) and annotation.get("widget_name"):

        ## alias the annotation as metadata
        metadata = annotation

        ## store the widget name
        widget_name = metadata["widget_name"]

        ## retrieve a widget_kwargs dict from the
        ## metadata, creating it if it doesn't exists
        widget_kwargs = metadata.setdefault("widget_kwargs", {})

        ## store the default value in the widget
        ## kwargs 'value' field
        widget_kwargs["value"] = default

        ## if the metadata specifies a 'type', use it
        ## as the new annotation

        try:
            annotation = metadata["type"]
        except KeyError:
            pass

    ### if no specific metadata for a widget was provided,
    ### define a widget kwargs dict with the default added
    ### to it in the 'value' field
    else:
        widget_kwargs = {"value": default}

    ### from this point on, we must consider the annotation
    ### as the type for the input
    type_ = annotation

    ######## adjust and return widget data ########

    ### if a widget name was provided it means the user
    ### also provided the needed data for instantiating
    ### the widget, so we return the instructions to
    ### define such widget, but only after checking
    ### if the widget in question is an int float entry,
    ### in which case extra processing is needed before
    ### doing so

    if widget_name:

        ## handle int float entry specific requirements
        ## if widget name matches;
        ##
        ## here we purposefully don't catch possible
        ## errors raised by the function used, since they
        ## mean the data isn't suitable for defining the
        ## widget in question

        if widget_name == "int_float_entry":

            process_int_float_entry_data(widget_kwargs, type_)

        elif widget_name == "color_button":

            if type_ is tuple:
                widget_kwargs["color_format"] = "rgb_tuple"

            elif type_ is str:
                widget_kwargs["color_format"] = "hex_string"

            else:

                raise TypeError("type for color buttons must be" "either tuple or str")

        ## regardless of whether widget_name is equal to
        ## 'int_float_entry' or not, return dict with
        ## instructions to instantiate the widget named
        ## in widget_name with the given keyword arguments

        return {"widget_name": widget_name, "widget_kwargs": widget_kwargs}

    ### if a widget name wasn't specified, though, use the
    ### type_ and value (widget_kwargs['value']) to
    ### determine whether instructions for a widget can be
    ### put together

    else:

        ## retrieve the value
        value = widget_kwargs["value"]

        ## if the value isn't a python literal, a default
        ## holder widget must be used

        try:
            literal_eval(repr(value))

        except Exception:

            return {"widget_name": "default_holder", "widget_kwargs": widget_kwargs}

        ## if the type information is in reality
        ## a sentinel value meaning there's no actual
        ## type data used, a default holder widget must
        ## be used as well

        if type_ is Parameter.empty:

            return {"widget_name": "default_holder", "widget_kwargs": widget_kwargs}

        ## if type is str and value is an instance
        ## of it use a string entry widget

        elif type_ is str and isinstance(value, str):

            return {"widget_name": "string_entry", "widget_kwargs": widget_kwargs}

        ## if type is boolean and value is an instance
        ## of it use a check button widget

        elif type_ is bool and isinstance(value, bool):

            return {"widget_name": "check_button", "widget_kwargs": widget_kwargs}

        ### perform extra checks;
        ###
        ### if we got to this point, without returning
        ### we try going through additional more complex
        ### checks to determine if an widget can be
        ### defined by the value (in the kwargs) and type;
        ###
        ### we do so by iterating over special functions
        ### and associated widget names checking whether
        ### the widget in question can be defined by
        ### the available data

        for processing_operation, widget_name in (
            (process_none_or_boolean_option_tray, "option_tray"),
            (process_int_float_entry_data, "int_float_entry"),
        ):

            ## check whether value (in kwargs) and type
            ## can be used to define specific widget
            try:
                processing_operation(widget_kwargs, type_)

            ## if not, then just pass
            except (TypeError, ValueError):
                pass

            ## otherwise, we return data specifying the
            ## widget in question

            else:

                return {"widget_name": widget_name, "widget_kwargs": widget_kwargs}

        ### if we get to this point without ever returning
        ### then it means there is no way to define other
        ### widget, so we just return data to define the
        ### default holder widget

        return {"widget_name": "default_holder", "widget_kwargs": widget_kwargs}


### TODO the utility functions below will perhaps be
### relocated to where the widgets are defined, since
### they are more closely related to them; ponder when
### reviewing the mini-language associated with the
### definition of all the widgets;

### utility functions for local usage and related constants


## int float entry

ALLOWED_INT_FLOAT_TYPES = int, float, type(None), None
ALLOWED_CLASS_NAMES = tuple(ALLOWED_NUM_CLASSES.keys())


def process_int_float_entry_data(widget_kwargs, type_):
    """Check/define data on intfloat entry.

    Parameters
    ==========
    widget_kwargs (dict)
        keyword arguments to define an intfloat entry
        widget.
    type_ (any Python value)
        value used as type information to help define
        the value for the 'numeric_classes_hint' string.
    """
    ### if a 'numeric_classes_hint' field is not present
    ### in the widget keyword arguments, create one for it
    ### using the type information (the class info
    ### also specifies a type(None) class, we also set
    ### the 'allow_none' field to True

    if "numeric_classes_hint" not in widget_kwargs:

        ## create an 'raise_error' flag set to False
        raise_error = False

        ## retrieve a value for the string depending on
        ## the type information (set the flag to raise
        ## an error ahead if type information not allowed
        ## is found)

        # if the type_ info is a tuple or list...

        if isinstance(type_, (tuple, list)):

            # if the tuple/list is empty, raise an error
            if not type_:
                raise_error = True

            # if any type contained in the tuple or list
            # is not allowed, set the raise_error flag on

            elif any(item not in ALLOWED_INT_FLOAT_TYPES for item in type_):
                raise_error = True

            # otherwise you can inspect the items to
            # come up with a class name, and maybe a
            # allow_none field too

            else:

                # define the class name according to the
                # numeric types present in types

                if int in type_ and float in type_:
                    numeric_classes_hint = "int_float"

                elif int in type_:
                    numeric_classes_hint = "int"
                elif float in type_:
                    numeric_classes_hint = "float"

                else:
                    raise_error = True

                # if None or NoneType is present, set the
                # 'allow_none' field to True (regardless
                # of whether it already exists or not)

                if None in type_ or type(None) in type_:
                    widget_kwargs["allow_none"] = True

        # if the type_ info is builtin int or builtin
        # float, assign the respective names to the
        # numeric_classes_hint string

        elif type_ == int:
            numeric_classes_hint = "int"
        elif type_ == float:
            numeric_classes_hint = "float"

        # otherwise we have a type not allowed, so set the
        # raise_error flag on
        else:
            raise_error = True

        ## if the raise error flag is set, do as it says:
        ## raise an error to report the error

        if raise_error:

            raise TypeError("type information for int float entry" " isn't legal")

        ## otherwise it means we achieved a legal
        ## numeric_classes_hint, so store it
        else:
            widget_kwargs["numeric_classes_hint"] = numeric_classes_hint

    ### if a numeric_classes_hint field is present though,
    ### check whether it's value is allowed

    else:

        if widget_kwargs["numeric_classes_hint"] not in ALLOWED_CLASS_NAMES:

            msg = (
                "'numeric_classes_hint' value for int float"
                " entry isn't legal, must be one of {}"
            ).format(ALLOWED_CLASS_NAMES)

            raise ValueError(msg)

    ### if value in the 'value' field of the widget_kwargs
    ### is None, set allow none to True

    if widget_kwargs["value"] is None:
        widget_kwargs["allow_none"] = True

    ### finally, check whether the value complies with
    ### the expected type
    check_int_float_entry_value_type_compliance(widget_kwargs)


def check_int_float_entry_value_type_compliance(int_float_kwargs):
    """Check whether the value complies with type.

    Parameters
    ==========
    int_float_kwargs (dict)
        contains keyword arguments to instantiate
        int float entry widget.
    """
    ### retrieve relevant values

    value = int_float_kwargs["value"]
    numeric_classes_hint = int_float_kwargs["numeric_classes_hint"]
    allow_none = int_float_kwargs.get("allow_none", False)

    ### gather allowed classes

    ## retrieve allowed numeric classes
    allowed_classes = ALLOWED_NUM_CLASSES[numeric_classes_hint]

    ## add NoneType if allowed
    if allow_none:
        allowed_classes = allowed_classes + (type(None),)

    ## check type

    if not isinstance(value, allowed_classes):

        msg = (
            "'value' provided ({}) for int float entry isn't"
            " compatible with allowed types you requested: {}"
        ).format(value, allowed_classes)

        raise TypeError(msg)


## option tray widget with False/None/True values


def process_none_or_boolean_option_tray(widget_kwargs, type_):
    """Check whether given args can define option tray.

    Also performs additional changes in the widget kwargs
    received if the check does confirm the arguments can
    be used to infer what is missing.

    That is, we check whether the default value and type
    associated with a parameter are compliant with what is
    expected to define an option tray widget with
    False/None/True as its options.

    If get to the end of this function without raising any
    exceptions, it means the data received is approved
    for defining such widget, so we add what is missing,
    so the keyword arguments are ready to instantiate the
    widget when needed.

    Parameters
    ==========
    widget_kwargs (dict)
        a dict whose sole item is the 'value' key
        pointing to any object.
    type_ (any Python value)
        the type associated with the parameter.
    """
    ### retrieve the value
    value = widget_kwargs["value"]

    ### if type is bool and value is None raise no error,
    ### we do nothing, since this is an allowed scenario
    if type_ is bool and value is None:
        pass

    ### otherwise, we keep performing extra checks, this
    ### time for forbidden scenarios, assuming type_ is an
    ### iterable (if it is not, the TypeError raised by
    ### len() is purposefully not caught, meaning the check
    ### failed; it might be better to catch the exception
    ### and raise another one with a better explanation,
    ### though)

    elif len(type_) != 2:

        raise TypeError(
            "if type is an iterable, it must have only 02"
            " items, regardless of the order, for"
            " 'False/None/True' option tray to be defined"
        )

    elif bool not in type_:

        raise TypeError(
            "bool must be in 'type_' iterable for"
            " 'False/None/True' option tray to be defined"
        )

    elif None not in type_ and type(None) not in type_:

        raise TypeError(
            "either None or NoneType must be in 'type_'"
            " iterable for 'False/None/True' option tray"
            " to be defined"
        )

        ## note: since we avoided the previous
        ## "if/elif blocks" we can be sure that type_ has
        ## 02 items and bool is one of them; in addition
        ## to this, if we avoid this "elif block" as well,
        ## we can be sure that the other element is either
        ## None or type(None); in other words, both None
        ## and type(None) cannot appear at the same time
        ## in type_

    elif not isinstance(widget_kwargs["value"], (type(None), bool)):

        raise ValueError(
            "'value' must be either None, True or False"
            " for 'False/None/True' option tray to be"
            " defined"
        )

    ### getting to this point in the function means
    ### the data can be used to define the False/None/True
    ### option tray, but it isn't complete yet, so we
    ### increment the widget kwargs with what it is
    ### lacking: the 'options' argument
    widget_kwargs["options"] = [False, None, True]
