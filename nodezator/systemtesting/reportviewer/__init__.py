"""Form for setting and triggering system testing session."""

### standard library imports

from functools import partialmethod

from xml.etree.ElementTree import XML, tostring as element_to_string

### third-party imports

from pygame import Rect

from pygame.math import Vector2

from pygame.image import save as save_surface


### local imports

from ...config import APP_REFS

from ...dialog import create_and_show_dialog

from ...pygamesetup import SCREEN_RECT

from ...ourstdlibs.behaviour import empty_function

from ...ourstdlibs.pyl import save_pyl

from ...our3rdlibs.button import Button

from ...classes2d.single import Object2D
from ...classes2d.collections import List2D

from ...textman.render import render_text

from ...svgutils import get_rect_svg_text

from ...rectsman.main import RectsManager

from ...surfsman.draw import draw_depth_finish
from ...surfsman.render import (
    render_rect,
    render_surface_from_svg_text,
    combine_surfaces,
    unite_surfaces,
)

from ...fileman.main import select_paths

from .constants import (
    REPORT_BG,
    BUTTON_SETTINGS,
    HTML_TEMPLATE,
)

## classes for extension

from .op import ReportViewerOperations
from .factoryfuncs import ReportViewerFactoryFuncs
from .constants import RESULT_COLOR_MAP, LEGEND_ORDER, TITLE_MAP



### local constants

## legend rects and rects manager

def _get_legend_rects_and_rectsman():

    rects = []

    topleft = (0, 0)

    for _ in range(3):

        color_rect = Rect(0, 0, 16, 16)
        text_rect = Rect(0, 0, 100, 21)

        color_rect.topleft = topleft
        text_rect.midleft = color_rect.move(10, 0).midright

        rects.extend((color_rect, text_rect))

        topleft = color_rect.move(0, 10).bottomleft

    rect_pairs = [
        (rects[index], rects[index+1])
        for index in (0, 2, 4)
    ]

    return rect_pairs, RectsManager(rects.__iter__)

LEGEND_RECT_PAIRS, LEGEND_RECTSMAN = _get_legend_rects_and_rectsman()


## utility

FORMAT_CAPTION = (
    "Pick location wherein to save exported {} file"
).format



### class definition

class ReportViewer(
    ReportViewerOperations,
    ReportViewerFactoryFuncs,
):
    """Displays a system testing report."""

    def __init__(self):
        """Setup objects."""
        ### build surf and rect for background

        self.image = render_rect(970, 650, REPORT_BG)
        self.rect = self.image.get_rect()

        ### store copy for cleaning the image
        self.clean_bg = self.image.copy()

        ### store slightly smaller area for scrolling/safe display
        self.scroll_area = self.rect.inflate(-60, -80)

        ### assign behaviours

        ## update
        self.update = empty_function

        ### special collection to store widgets
        self.widgets = List2D()

        ### build button widgets
        self.create_buttons()

        ### create placeholder attributes

        ## to hold next loop holder
        self.loop_holder = None

        ## to hold report data
        self.report_data = None

        ### center form and also append centering method
        ### as a window resize setup

        self.center_session_recording_form()

        APP_REFS.window_resize_setups.append(
            self.center_session_recording_form
        )

    def center_session_recording_form(self):

        diff = Vector2(SCREEN_RECT.center) - self.rect.center

        ## center rect and scroll area on screen
        self.rect.center = self.scroll_area.center = SCREEN_RECT.center

        ##
        self.widgets.rect.move_ip(diff)

    def create_buttons(self):
        """Build buttons to use/reuse in reports."""
        ### create report related buttons

        self.buttons = (

            List2D(

                Button.from_text(
                    text=text,
                    command=operation,
                    **BUTTON_SETTINGS,
                )

                for text, operation in (
                    ("Export as .html", self.export_html),
                    ("Export as .pyl", self.export_pyl),
                    ("Export as .png", self.export_png),
                    ("Exit report", self.exit),
                )

            )

        )

        ## apply depth finish

        for button in self.buttons:
            draw_depth_finish(button.image)

        ## align and position buttons

        self.buttons.rect.snap_rects_ip(
            retrieve_pos_from='midright',
            assign_pos_to='midleft',
            offset_pos_by=(10, 0),
        )

        self.buttons.rect.bottomright = self.rect.move(-10, -10).bottomright

        ## store as widgets
        self.widgets.extend(self.buttons)

    def export(self, extension):
        """Export report as extension."""

        ### retrieve path

        paths = (

            select_paths(

                caption=FORMAT_CAPTION(extension),

                path_name=(
                    'test_report_'
                    + self.session_start_timestamp
                    + extension
                )

            )

        )

        ### if path(s) were given, use the first one

        if paths:

            filepath = paths[0]

            if filepath.suffix.lower() != extension:

                answer = create_and_show_dialog(

                    f"Extension must be {extension}. Want us to fix it for you?",

                    (
                        ("Yes", True),
                        ("No, cancel operation", False),
                    )

                )

                if answer:
                    filepath = filepath.with_suffix(extension)

                else:
                    return


            if extension == '.pyl':
                self.save_pyl(filepath)
            elif extension == '.png':
                self.save_png(filepath)
            elif extension == '.html':
                self.save_html(filepath)
            else:
                raise RuntimeError("Logic shouldn't allow this block to be executed.")

    export_pyl = partialmethod(export, extension='.pyl')
    export_png = partialmethod(export, extension='.png')
    export_html = partialmethod(export, extension='.html')

    def save_pyl(self, filepath):

        try:
            save_pyl(self.report_data, filepath)

        except Exception as err:

            error_msg = str(err)[:200]
            create_and_show_dialog(error_msg, level_name='error')

    def save_png(self, filepath):

        widgets = self.widgets
        rects_manager = widgets.rect

        topleft = rects_manager.topleft

        rects_manager.topleft = (0, 0)

        union_surf = (

            unite_surfaces(

                surface_rect_pairs=(
                    (obj.image, obj.rect)
                    for obj in widgets
                ),

                padding=10,
                background_color=REPORT_BG,

            )

        )

        rects_manager.topleft = topleft

        try:
            save_surface(union_surf, str(filepath))

        except Exception as err:

            error_msg = str(err)[:200]
            create_and_show_dialog(error_msg, level_name='error')

    def save_html(self, filepath):

        html_text = (

            HTML_TEMPLATE.substitute(
                title_text=self.caption_text,
                pie_and_legend_svg=(
                    self._get_pie_svg_with_legend(self.pie_svg_text)
                ),
                rest_of_body_content=self.html_content,
            )

        )

        try:
            filepath.write_text(html_text, encoding='utf-8')

        except Exception as err:

            error_msg = str(err)[:200]
            create_and_show_dialog(error_msg, level_name='error')

    def _get_pie_svg_with_legend(self, pie_svg_text):
        """Return SVG text changed so it includes a legend."""
        ### create root element
        pie_svg_tag = XML(pie_svg_text)

        ### remove first rect, since it is used as background, and the html
        ### presention doesn't need one
        rect_to_remove = pie_svg_tag.find('rect')
        pie_svg_tag.remove(rect_to_remove)

        ### create a rect representing the pie

        pie_rect = (

            Rect(
                0,
                0,
                int(pie_svg_tag.get('width')),
                int(pie_svg_tag.get('height')),
            )

        )

        ### position legend relatively and unite it with te pie rect instance

        LEGEND_RECTSMAN.midleft = pie_rect.move(10, 0).midright
        pie_rect.union_ip(LEGEND_RECTSMAN)

        ### update dimensions of pie svg tag with pie rect

        for dimension in ('width', 'height'):
            pie_svg_tag.set(dimension, str(getattr(pie_rect, dimension)))

        pie_svg_tag.set('viewBox', f'0 0 {pie_rect.width} {pie_rect.height}')

        ### create and add legend shapes/text

        for index, key in enumerate(LEGEND_ORDER):

            color_rect, text_rect = LEGEND_RECT_PAIRS[index]

            ## get rect tag

            color = RESULT_COLOR_MAP[key]

            ###
            rect_tag = XML(
                get_rect_svg_text(
                    0, 0, 16, 16,
                    fill_color=color,
                    outline_color='black',
                    outline_width=2,
                )
            ).find('rect')

            ## set x and y

            for char in 'xy':
                rect_tag.set(char, str(getattr(color_rect, char)))

            ## append it to pie svg
            pie_svg_tag.append(rect_tag)

            ## create text tag

            title = TITLE_MAP[key]

            x, y = text_rect.bottomleft

            pie_svg_tag.append(
                XML(f'<text x="{x}" y="{y}">{title}</text>')
            )

        ### return pie svg from updated tag
        return (
            element_to_string(
                pie_svg_tag,
                encoding='unicode',
            )
        ).replace('<svg', '<svg xmlns="http://www.w3.org/2000/svg"')

## create instance of report viewer
report_viewer = ReportViewer()
