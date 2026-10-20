
### local import
from ...config import APP_REFS


## use only a percentage of font height (seems to yield
## better results)

percentage = .85

gfh = round(APP_REFS.general_font_height * percentage)
mfh = round(APP_REFS.mono_font_height * percentage)

angle_brackets_percentage = (
    .4
    if APP_REFS.general_font_height > 30
    else .7
)

angle_brackets_fh = (
    round(
        APP_REFS.general_font_height
        * angle_brackets_percentage
    )
)


WIDGET_CSS = f"""

g.default_holder > rect {{
  fill: rgb(200, 200, 200);
  stroke:black;
  stroke-width:1px;
}}

g.default_holder > text {{
  font: bold {gfh}px sans-serif;
  fill: rgb(35, 35, 35);
}}

g.string_entry > text {{
  font: bold {gfh}px sans-serif;
  fill: rgb(35, 35, 35);
}}

g.string_entry > rect {{
  fill: rgb(255, 255, 255);
}}

g.literal_entry > text {{
  font: bold {mfh}px monospace;
  fill: rgb(255, 212, 59);
}}

g.literal_entry > rect {{
  fill: rgb(48, 105, 152);
}}

g.int_float_entry > text {{
  font: bold {gfh}px sans-serif;
  fill: rgb(238, 238, 238);
}}

g.int_float_entry > text.angle_brackets {{
  font: bold {angle_brackets_fh}px sans-serif;
  fill: rgb(238, 238, 238);
}}

g.int_float_entry > rect.bg {{
  fill: rgb(47, 47, 60);
}}

g.int_float_entry > rect.range_bg {{
  fill: rgb(30, 130, 70);
}}

g.check_button > rect {{
  fill: white;
  stroke: black;
  stroke-width: 2px;
}}

g.check_button > polyline {{
  fill:none;
  stroke:black;
  stroke-width:3px;
}}

g.option_menu > rect {{
  fill: rgb(47, 47, 60);
}}

g.option_menu > path {{
  fill: rgb(238, 238, 238);
}}

g.option_menu > text {{
  font: bold {gfh}px sans-serif;
  fill: rgb(238, 238, 238);
}}



g.option_tray > rect.not_selected_bg {{
  fill: rgb(47, 47, 60);
  stroke: white;
  stroke-width: 1px;
}}

g.option_tray > rect.selected_bg {{
  fill: rgb(30, 130, 70);
  stroke: white;
  stroke-width:1px;
}}

g.option_tray > text {{
  font: bold {gfh}px sans-serif;
  fill: rgb(238, 238, 238);
}}



g.color_button > path.color_unit_checker_bg {{
  fill:url(#checker_pattern);
}}

g.color_button > path.color_unit {{
  stroke: black;
  stroke-width: 2px;
}}





g.path_preview > rect {{
  fill:grey;
  stroke: silver;
  stroke-width:1px;
}}



g.text_display > rect {{
  fill:grey;
  stroke: silver;
  stroke-width:1px;
}}

g.literal_display > rect {{
  fill: rgb(48, 105, 152);
  stroke: silver;
  stroke-width:1px;
}}


g.sorting_button > rect {{
  fill:white;
}}

g.sorting_button > text {{
  font: bold {gfh}px sans-serif;
  fill: black;
}}

.thumb_bg {{
  fill: rgb(40, 40, 90);
}}
"""
