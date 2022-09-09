"""Presets for various purposes."""

### standard library import
from collections.abc import Iterator

### local import
from ..ourstdlibs.dictutils import flatten_keys


## parameter annotation preset map
## (note that its keys are flattened in the next step)

PARAM_ANNOTATION_PRESET_MAP = {
    ("python_literal",): {
        "widget_name": "literal_entry",
    },
    ("python_multiline_literal",): {
        "widget_name": "literal_display",
    },
    ("python_literal_string",): {
        "widget_name": "string_entry",
        "widget_kwargs": {
            "validation_command": "literal_eval",
        },
        "type": str,
    },
    ("python_literal_text_string",): {
        "widget_name": "text_display",
        "widget_kwargs": {
            "validation_command": "literal_eval",
            "syntax_highlighting": "python",
            "font_path": "mono_bold",
        },
        "type": str,
    },
    ("non_negative_int", "non_negative_integer", "natural_number",): {
        "widget_name": "int_float_entry",
        "widget_kwargs": {
            "min_value": 0,
        },
        "type": int,
    },
    (
        "non_negative_int_or_none",
        "non_negative_integer_or_none",
        "natural_number_or_none",
    ): {
        "widget_name": "int_float_entry",
        "widget_kwargs": {"min_value": 0, "allow_none": True},
        "type": (int, None),
    },
    ("positive_int", "positive_integer",): {
        "widget_name": "int_float_entry",
        "widget_kwargs": {
            "min_value": 1,
        },
        "type": int,
    },
    ("positive_int_or_none", "positive_integer_or_none",): {
        "widget_name": "int_float_entry",
        "widget_kwargs": {"min_value": 1, "allow_none": True},
        "type": (int, None),
    },
    ("path", "file", "filepath", "directory", "dirpath",): {
        "widget_name": "path_preview",
        "type": str,
    },
    ("text_file_path", "text_filepath", "text_path",): {
        "widget_name": "text_preview",
        "type": str,
    },
    ("image_file_path", "image_filepath", "image_path",): {
        "widget_name": "image_preview",
        "type": str,
    },
    ("font_file_path", "font_filepath", "font_path",): {
        "widget_name": "font_preview",
        "type": str,
    },
    ("audio_file_path", "audio_filepath", "audio_path",): {
        "widget_name": "audio_preview",
        "type": str,
    },
    ("video_file_path", "video_filepath", "video_path",): {
        "widget_name": "video_preview",
        "type": str,
    },
    ("text", "text_string",): {
        "widget_name": "text_display",
        "type": str,
    },
}

flatten_keys(PARAM_ANNOTATION_PRESET_MAP)


## output annotation preset map
## (note that its keys are flattened in the next step)

OUTPUT_ANNOTATION_PRESET_MAP = {
    ("iterator",): [{"name": "iterator", "type": Iterator}],
    (
        "tuple",
        "a_tuple",
    ): [{"name": "a_tuple", "type": tuple}],
}
flatten_keys(OUTPUT_ANNOTATION_PRESET_MAP)


## widget default data map

WIDGET_DATA_PRESET_MAP = {
    "string": {
        "widget_name": "string_entry",
        "widget_kwargs": {"value": ""},
    },
    "integer": {
        "widget_name": "int_float_entry",
        "widget_kwargs": {"value": 0},
    },
    "float": {
        "widget_name": "int_float_entry",
        "widget_kwargs": {
            "value": 0.0,
            "numeric_classes_hint": "float",
        },
    },
    "boolean": {
        "widget_name": "check_button",
        "widget_kwargs": {"value": False},
    },
    "int_and_float_and_none": {
        "widget_name": "int_float_entry",
        "widget_kwargs": {
            "value": 0,
            "numeric_classes_hint": "int_float",
            "allow_none": True,
        },
    },
    "int_and_float": {
        "widget_name": "int_float_entry",
        "widget_kwargs": {
            "value": 0,
            "numeric_classes_hint": "int_float",
        },
    },
    "int_and_none": {
        "widget_name": "int_float_entry",
        "widget_kwargs": {
            "value": 0,
            "allow_none": True,
        },
    },
    "float_and_none": {
        "widget_name": "int_float_entry",
        "widget_kwargs": {
            "value": 0.0,
            "numeric_classes_hint": "float",
            "allow_none": True,
        },
    },
}

WIDGET_PRESET_MENU_LABEL_MAP = {
    "string": "String",
    "integer": "Integer",
    "float": "Float",
    "boolean": "Boolean",
    "int_and_float_and_none": "Integer/float/none",
    "int_and_float": "Integer/float",
    "int_and_none": "Integer/none",
    "float_and_none": "Float/none",
}
