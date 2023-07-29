"""Strucuture for general popup to grab widgets."""

from .utils import get_widget_metadata


WIDGET_POPUP_STRUCTURE = [

    [
        "String",

        {

            "annotation": str,
            "value": "string",

        },

    ],

    [
        "String(s) representing path(s)",

        [


            [

                "General",

                {
                    "annotation": {
                        "widget_name": "path_preview",
                        "type": str,
                    },
                    "value": '.',
                },

            ],

            [

                "Text",

                {
                    "annotation": {
                        "widget_name": "text_preview",
                        "type": str,
                    },
                    "value": '.',
                },

            ],

            [

                "Image",

                {
                    "annotation": {
                        "widget_name": "image_preview",
                        "type": str,
                    },
                    "value": '.',
                },

            ],

            [

                "Font",

                {
                    "annotation": {
                        "widget_name": "font_preview",
                        "type": str,
                    },
                    "value": '.',
                },

            ],

            [

                "Audio",

                {
                    "annotation": {
                        "widget_name": "audio_preview",
                        "type": str,
                    },
                    "value": '.',
                },

            ],

            [

                "Video",

                {
                    "annotation": {
                        "widget_name": "video_preview",
                        "type": str,
                    },
                    "value": '.',
                },

            ],


        ],

    ],

    [

        "More string variations",

        [


            [
                "Multiline",

                {

                    "annotation": {"widget_name": "text_display"},
                    "value": "string\nin multiple\nlines",

                },

            ],

            [
                "Python source",

                {
                    "annotation": {
                        "widget_name": "text_display",
                        "widget_kwargs": {
                            "syntax_highlighting": "python",
                            "font_path": "mono_bold",
                        },
                    },
                    "value": '"""Python source"""',
                }
            ]

        ]

    ],

    [

        "Boolean",

        {
            "annotation": bool,
            "value": False,
        },

    ],

    [
        "Integer",

        {
            "annotation": int,
            "value": 0,
        },

    ],

    [

        "Float",

        {
            "annotation": float,
            "value": 0.0,
        },

    ],

    [
        "More integer/float variations",

        [


            [

                "Integer/float/none",

                {
                    "annotation": (int, float, type(None)),
                    "value": 0,
                },

            ],

            [

                "Integer/float",

                {
                    "annotation": (int, float),
                    "value": 0,
                },
            ],

            [

                "Integer/none",

                {
                    "annotation": (int, type(None)),
                    "value": 0,
                },

            ],

            [

                "Float/none",

                {
                    "annotation": (float, type(None)),
                    "value": 0.0,
                }
            ],

        ],

    ],

    [
        "Python literal",

        [


            [

                "Single line",

                {
                    "annotation": {
                        "widget_name": "literal_entry",
                    },
                    "value": None,
                },

            ],

            [

                "Multiline",

                {
                    "annotation": {
                        "widget_name": "literal_display",
                    },
                    "value": None,
                },
            ],

        ],

    ],

    [
        "Color(s)",

        [

            [

                "RGB(A) tuple(s) (e.g.: (255, 0, 0))",

                {
                    "annotation": {
                        "widget_name": "color_button",
                        "type": tuple,
                    },
                    "value": (255, 0, 0),
                },

            ],

            [

                "Hex string(s) (e.g.: '#ff0000')",

                {
                    "annotation": {
                        "widget_name": "color_button",
                        "type": str,
                    },
                    "value": '#ff0000',
                },

            ],

        ],

    ]

]


for pair in WIDGET_POPUP_STRUCTURE:

    text, data = pair

    if isinstance(data, dict):
        pair[1] = get_widget_metadata(data['annotation'], data['value'])

    else:

        for subpair in data:

            subdata = subpair[1]

            subpair[1] = get_widget_metadata(subdata['annotation'], subdata['value'])
