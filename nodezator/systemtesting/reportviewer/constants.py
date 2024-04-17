
### standard library import
from string import Template


### local imports

from ...fontsman.constants import (
    ENC_SANS_BOLD_FONT_HEIGHT,
    ENC_SANS_BOLD_FONT_PATH,
    FIRA_MONO_BOLD_FONT_HEIGHT,
    FIRA_MONO_BOLD_FONT_PATH,
)

from ...colorsman.colors import (
    BUTTON_FG,
    BUTTON_BG,
)



REPORT_BG = (235, 235, 250)
REPORT_FG = (28, 28, 28)

RESULT_COLOR_MAP = {
    'passed': (30, 160, 70),
    'failed': (205, 0, 0),
    'error': (255, 140, 0),
}

LEGEND_ORDER = (
    'passed',
    'failed',
    'error',
)

TITLE_MAP = {
    'passed': 'Passed',
    'failed': 'Failed',
    'error': 'Error',
}

CSS_CLASS_NAME_MAP = {
    'passed': 'success-text',
    'failed': 'failure-text',
    'error': 'error-text',
}

PIE_FILL_RADIUS = 150
PIE_INNER_OUTLINE_WIDTH = 2
PIE_OUTER_OUTLINE_WIDTH = 2

TEXT_SETTINGS = {
    "font_height": ENC_SANS_BOLD_FONT_HEIGHT,
    "font_path": ENC_SANS_BOLD_FONT_PATH,
    "padding": 2,
    "foreground_color": REPORT_FG,
    "background_color": REPORT_BG,
}

MONO_TEXT_SETTINGS = {
    "font_height": FIRA_MONO_BOLD_FONT_HEIGHT,
    "font_path": FIRA_MONO_BOLD_FONT_PATH,
    "padding": 2,
    "foreground_color": REPORT_FG,
    "background_color": REPORT_BG,
}

BUTTON_SETTINGS = {
    "font_height": ENC_SANS_BOLD_FONT_HEIGHT,
    "font_path": ENC_SANS_BOLD_FONT_PATH,
    "padding": 5,
    "foreground_color": BUTTON_FG,
    "background_color": BUTTON_BG,
}


_INTERMEDIARY_HTML_TEMPLATE = Template("""
<!DOCTYPE html>
<html>

<head>
    <title>$title_text</title>

    <style>

body {
    color: rgb$foreground_color;
    background-color: rgb$background_color;
    font-family: Arial, Verdana, sans-serif;
    font-size: 1em;
    padding:0px 40px;
}

td {padding: 2px;}

a {text-decoration:none; padding: 2px; border:1px solid black;}

ul {
    list-style-type: none;
    margin:0;
    padding:0;
}

ul.extra-li-margin > li {
    margin:8px 0px;
}

div.block-link {
    margin:30px 0px;
}

div.block-link > a {
    padding:6px;
}

.monospaced_text {
    font-family: "Courier New", "Lucida Console", monospace;
}

.slightly-bigger-text {
    font-size: 1.5em;
    font-weight: bold;
}

.text-right {
    text-align: right;
}

.text-top {
    vertical-align: top;
}

.success-text
{
    color: rgb$success_color;
    font-weight: bold;
}

.failure-text
{
    color: rgb$failure_color;
    font-weight: bold;
}

.error-text
{
    color: rgb$error_color;
    font-weight: bold;
}
    </style>

</head>

<body>

<h1>$title_text</h1>

$pie_and_legend_svg

$rest_of_body_content

</body>
</html>
""".strip()
)

HTML_TEMPLATE = Template(
    _INTERMEDIARY_HTML_TEMPLATE
    .safe_substitute(
        foreground_color=str(REPORT_FG),
        background_color=str(REPORT_BG),
        success_color=str(RESULT_COLOR_MAP['passed']),
        failure_color=str(RESULT_COLOR_MAP['failed']),
        error_color=str(RESULT_COLOR_MAP['error']),
    )
)
