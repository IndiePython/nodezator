
### standard library imports

from collections import Counter

from datetime import datetime

from functools import partial


### local imports

from ...config import APP_REFS

from ...ourstdlibs.datetimeutils import DATETIME_STR_FORMAT_CODE

from ...our3rdlibs.button import Button

from ...svgutils import (
    get_pie_chart_svg_text,
    get_rect_svg_text,
    get_circle_svg_text_from_radius,
)

from ...textman.render import render_text

from ...classes2d.single import Object2D
from ...classes2d.collections import List2D

from ...surfsman.render import (
    render_surface_from_svg_text,
    render_separator,
    combine_surfaces,
    unite_surfaces,
)

from ...surfsman.draw import draw_border

from ...surfsman.icon import render_layered_icon

from ..constants import ID_FORMAT_SPEC, TEST_ID_TO_TITLE

from .constants import (

    REPORT_BG, REPORT_FG,
    RESULT_COLOR_MAP,
    TITLE_MAP,
    LEGEND_ORDER,
    CSS_CLASS_NAME_MAP,
    PIE_FILL_RADIUS,
    PIE_INNER_OUTLINE_WIDTH,
    PIE_OUTER_OUTLINE_WIDTH,

    TEXT_SETTINGS, MONO_TEXT_SETTINGS,

)



### local constants

PIE_COLOR_MAP = RESULT_COLOR_MAP 

TEXT_SETTINGS_FOR_OVERALL_RESULT = {

    result : {
        **TEXT_SETTINGS,
        'foreground_color': color,
        'font_height': 40,
    }

    for result, color in RESULT_COLOR_MAP.items()
}

TEXT_SETTINGS_FOR_CASE_RESULT = {

    result : {
        **TEXT_SETTINGS,
        'foreground_color': color,
    }

    for result, color in RESULT_COLOR_MAP.items()
}


RESULTS = []
RESULTS_COUNTER = Counter()

PASSED_SURF = render_layered_icon(
    chars=[chr(124)],
    dimension_name="height",
    dimension_value=14,
    padding=0,
    colors=[RESULT_COLOR_MAP['passed']],
    background_width=20,
    background_height=20,
    background_color=REPORT_BG,
)

FAILED_SURF = render_layered_icon(
    chars=[chr(126)],
    dimension_name="height",
    dimension_value=14,
    padding=0,
    colors=[RESULT_COLOR_MAP['failed']],
    background_width=20,
    background_height=20,
    background_color=REPORT_BG,
)

ERROR_SURF = render_layered_icon(
    chars=[chr(67), chr(68)],
    dimension_name="height",
    dimension_value=18,
    padding=0,
    colors=[(0, 0, 0), RESULT_COLOR_MAP['error']],
    background_width=20,
    background_height=20,
    background_color=REPORT_BG,
)

SEPARATOR_SURF = (
    render_separator(
        600,
        is_horizontal=True,
        padding=2,
        thickness=2,
        background_color=REPORT_BG,
        foreground_color=REPORT_FG,
        highlight_color=(235, 235, 235),
    )
)


ASSERTION_RESULT_TO_SURF = {
    False : FAILED_SURF,
    True : PASSED_SURF,
}

CASE_RESULT_TO_SURF = {
    'passed' : PASSED_SURF,
    'failed' : FAILED_SURF,
    'error': ERROR_SURF,
}

BACK_TO_CASE_LIST_SURF = (

    combine_surfaces(

        (

            ## arrow up with circle outline

            combine_surfaces(

                (

                    ## circle outline

                    render_surface_from_svg_text(

                        get_circle_svg_text_from_radius(
                            12,
                            fill_color=None,
                            outline_color='black',
                            outline_width=2,
                        )

                    ),

                    ## arrow up

                    render_layered_icon(
                        chars=[chr(ordinal) for ordinal in (50, 51)],
                        dimension_name="height",
                        dimension_value=15,
                        colors=[
                            (0, 0, 0),
                            (0, 0, 0),
                        ],
                    ),
                ),
                retrieve_pos_from='center',
                assign_pos_to='center',
                offset_pos_by=(0, -1),
                background_color=REPORT_BG,
            ),

            ## text

            render_text(
                "Back to case list",
                **TEXT_SETTINGS,
            )

        ),
        retrieve_pos_from='midright',
        assign_pos_to='midleft',
        offset_pos_by=(2, 0),
        padding=4,
        background_color=REPORT_BG,

    )

)

draw_border(BACK_TO_CASE_LIST_SURF)

EMOJI_MAP = {
  'passed': '✅',
  'failed':'❌',
  'error': '✴️',
}

##

def _get_pie_legend():

    objs = List2D()

    topleft = (0, 0)

    for key in LEGEND_ORDER:

        title = TITLE_MAP[key]

        color = PIE_COLOR_MAP[key]

        objs.append(

            Object2D.from_surface(

                render_surface_from_svg_text(

                    get_rect_svg_text(
                        0, 0, 16, 16,
                        fill_color=color,
                        outline_color='black',
                        outline_width=4,
                    )

                ).convert(),
                coordinates_name='topleft',
                coordinates_value=topleft,

            )

        )

        ###

        midleft = objs[-1].rect.move(5, 0).midright

        objs.append(

            Object2D.from_surface(

                render_text(
                    text=title,
                    **TEXT_SETTINGS,
                ),
                coordinates_name='midleft',
                coordinates_value=midleft,

            )

        )

        topleft = objs.rect.move(0, 10).bottomleft

    objs.rect.topleft = (0, 0)

    return unite_surfaces((obj.image, obj.rect) for obj in objs)

PIE_LEGEND = _get_pie_legend()



class ReportViewerFactoryFuncs:

    def prepare_report(self, report_data):
        """Create visuals showing report results."""

        ### store report data
        self.report_data = report_data

        ### reference widgets locally
        widgets = self.widgets

        ### clear widgets
        widgets.clear()

        ### store session start timestamp in special format

        self.session_start_timestamp = ''.join(

            char if char.isdigit() else '_'

            for char in report_data['start_time'][:19]

        )

        ### create, position and store caption

        caption_text = self.caption_text = (
            "System testing report:"
            + ' '
            + report_data['start_time'][:19]
            + ' '
            + report_data['utc_offset']
        )

        self.caption_label = Object2D.from_surface(
            surface=(
                render_text(
                    text=caption_text,
                    **{**TEXT_SETTINGS, 'font_height': 34},
                )
            ),
            coordinates_name="topleft",
            coordinates_value=self.scroll_area.topleft,
        )

        self.caption_label.rect.topleft = self.scroll_area.topleft
        widgets.append(self.caption_label)

        ### create report-related visuals

        ## create pie chart

        # update results

        RESULTS.clear()
        RESULTS_COUNTER.clear()

        RESULTS.extend(
            stats['result']
            for stats in report_data['test_cases_stats'].values()
        )

        RESULTS_COUNTER.update(RESULTS)

        # generate svg text

        self.pie_svg_text = pie_svg_text = (
            get_pie_chart_svg_text(
                value_map=RESULTS_COUNTER,
                color_map=PIE_COLOR_MAP,
                fill_radius=PIE_FILL_RADIUS,
                outer_outline_color='black',
                outer_outline_width=PIE_OUTER_OUTLINE_WIDTH,
                inner_outline_color='black',
                inner_outline_width=PIE_INNER_OUTLINE_WIDTH,
                background_color=REPORT_BG,
            )
        )

        # create pie chart surface

        pie_surf = render_surface_from_svg_text(pie_svg_text).convert()

        final_pie_surf = (
            combine_surfaces(
                (pie_surf, PIE_LEGEND),
                retrieve_pos_from='midright',
                assign_pos_to='midleft',
                offset_pos_by=(20, 0),
                background_color=REPORT_BG,
            )
        )

        ##

        topleft = widgets.rect.move(0, 20).bottomleft

        pie = Object2D.from_surface(
            surface=final_pie_surf,
            coordinates_name='topleft',
            coordinates_value=topleft,
        )

        # append to widgets
        widgets.append(pie)

        ##
        self.html_content = ''
        ##

        overall_obj = self.get_overall_stats_object()

        overall_obj.rect.topleft = pie.rect.move(0, 10).bottomleft

        widgets.append(overall_obj)

        ##

        self.html_content += "<hr />\n\n"
        separator = Object2D.from_surface(SEPARATOR_SURF)

        separator.rect.top = widgets.rect.bottom + 20
        separator.rect.centerx = self.rect.centerx
        widgets.append(separator)

        ##
        section_text = "Case list"

        self.html_content += f'<h2 id="case-list">{section_text}</h2>\n\n'

        case_list_caption = self.case_list_caption = Object2D.from_surface(

            surface=(
                render_text(
                    text=section_text,
                    **{**TEXT_SETTINGS, 'font_height': 28},
                )
            )

        )

        case_list_caption.rect.topleft = widgets.rect.move(0, 20).bottomleft

        widgets.append(case_list_caption)

        ##

        case_buttons = self.case_buttons = self.get_case_buttons()

        case_buttons.rect.topleft = widgets.rect.move(0, 10).bottomleft

        widgets.extend(case_buttons)

        ##
        requested_cases = report_data['requested_cases']
        cases_stats = report_data['test_cases_stats']

        self.html_content += '<ul class="extra-li-margin">\n\n'

        for case_id in sorted(

            ## items
            requested_cases,

            ## - problematics first (error, failed, then passed)
            ## - then by id
            key=(lambda item: (cases_stats[item]['result'], item)),

        ):

            case_html_id = 'stc' + format(case_id, ID_FORMAT_SPEC)
            case_result = cases_stats[case_id]['result']
            class_name = CSS_CLASS_NAME_MAP[case_result]
            emoji_char = EMOJI_MAP[case_result]

            text=(
                'STC '
                + format(case_id, ID_FORMAT_SPEC)
                + " - "
                + TEST_ID_TO_TITLE[case_id]
            )

            self.html_content += (
                f'<li><a href="#{case_html_id}"><span class="{class_name}">{emoji_char}</span>'
                f' <span class="monospaced-text">{text}</span></a></li>\n'
            )


        ##
        self.html_content += '\n\n</ul>\n\n'
        self.html_content += "\n\n<hr />\n\n"
        ##

        separator = Object2D.from_surface(SEPARATOR_SURF)

        separator.rect.top = widgets.rect.bottom + 20
        separator.rect.centerx = self.rect.centerx
        widgets.append(separator)

        ##

        section_text = "Case stats"

        self.html_content += f'<h2>{section_text}</h2>\n\n'

        case_stats_caption = self.case_stats_caption = Object2D.from_surface(

            surface=(
                render_text(
                    text=section_text,
                    **{**TEXT_SETTINGS, 'font_height': 28},
                )
            )

        )

        case_stats_caption.rect.topleft = widgets.rect.move(0, 20).bottomleft

        widgets.append(case_stats_caption)

        ##

        case_related_objs = self.get_case_stats_and_back_to_case_list_buttons()

        case_related_objs.rect.topleft = widgets.rect.move(0, 20).bottomleft

        widgets.extend(case_related_objs)

        ## store case stats (every other object from case_related_objs
        self.case_stats_objs = case_related_objs[::2]

        ### position and store buttons

        self.buttons.rect.bottomright = (
            self.rect.right - 10,
            widgets.rect.bottom + 50,
        )

        widgets.extend(self.buttons)

    def get_overall_stats_object(self):

        ###
        rd = self.report_data

        ###
        overall_objs = List2D()

        ###
        session_result = rd['result']
        ###

        title_label = "Overall result"
        result_text = session_result.title()
        class_name = CSS_CLASS_NAME_MAP[session_result]

        ###

        self.html_content += (
            "<table>\n\n"
            "    <tr>\n"
            f'        <td class="text-right">{title_label}:</td>\n'
            f'        <td><span class="slightly-bigger-text {class_name}">{result_text}</span></td>\n'
            "    </tr>\n"
        )

        ##

        title_obj, result_obj = objs = (

            _get_title_result_labels(
                f'{title_label}:',
                TEXT_SETTINGS,
                result_text,
                TEXT_SETTINGS_FOR_OVERALL_RESULT[session_result],
            )

        )

        title_obj.rect.midright = (0, 0)
        result_obj.rect.midleft = (10, 0)

        overall_objs.extend(objs)

        top = overall_objs.rect.bottom + 10

        ##

        title_text = 'Date'
        result_text = rd['start_time'][:10]

        self.html_content += (
            "    <tr>\n"
            f'        <td class="text-right">{title_text}:</td>\n'
            f'        <td><span class="monospaced-text">{result_text}</span></td>\n'
            "    </tr>\n"
        )

        title_obj, result_obj = objs = (

            _get_title_result_labels(
                f'{title_text}:',
                TEXT_SETTINGS,
                result_text,
                MONO_TEXT_SETTINGS,
            )

        )

        title_obj.rect.midright = (0, top)
        result_obj.rect.midleft = (10, top)

        overall_objs.extend(objs)

        ###

        top = overall_objs.rect.bottom

        for key, title in (
            ('start_time', "Start time"),
            ('end_time', "End time"),
            ('utc_offset', "Timezone"),
        ):

            result_text = rd[key]

            self.html_content += (
                "    <tr>\n"
                f'        <td class="text-right">{title}:</td>\n'
                f'        <td><span class="monospaced-text">{result_text}</span></td>\n'
                "    </tr>\n"
            )

            title_obj, result_obj = objs = (

                _get_title_result_labels(
                    f"{title}:",
                    TEXT_SETTINGS,
                    rd[key],
                    MONO_TEXT_SETTINGS,
                )

            )

            title_obj.rect.topright = (0, top)
            result_obj.rect.topleft = (10, top)

            overall_objs.extend(objs)

            top = overall_objs.rect.bottom

        ##

        title_text = "Duration"

        duration = _get_formatted_duration(
            rd['start_time'], rd['end_time']
        )

        self.html_content += (
            "    <tr>\n"
            f'        <td class="text-right">{title_text}:</td>\n'
            f'        <td><span class="monospaced-text">{duration}</span></td>\n'
            "    </tr>\n"
        )

        title_obj, result_obj = objs = (

            _get_title_result_labels(
                f"{title_text}:",
                TEXT_SETTINGS,
                duration,
                MONO_TEXT_SETTINGS,
            )

        )

        title_obj.rect.topright = (0, top)
        result_obj.rect.topleft = (10, top)

        overall_objs.extend(objs)

        top = overall_objs.rect.bottom


        ##

        fps = rd['playback_speed']

        title_text = "Frames/second"

        result_text = (
            str(fps).rjust(2, '0') if fps else "Maximum/uncapped speed"
        )

        text_settings = MONO_TEXT_SETTINGS if fps else TEXT_SETTINGS
        class_name = 'monospaced-text' if fps else ''

        self.html_content += (
            "    <tr>\n"
            f'        <td class="text-right">{title_text}:</td>\n'
            f'        <td><span class="{class_name}">{result_text}</span></td>\n'
            "    </tr>\n"
        )

        title_obj, result_obj = objs = (

            _get_title_result_labels(
                f"{title_text}:",
                TEXT_SETTINGS,
                result_text,
                text_settings,
            )

        )

        title_obj.rect.topright = (0, top)
        result_obj.rect.topleft = (10, top)

        overall_objs.extend(objs)

        top = overall_objs.rect.bottom + 20

        ##
        self.html_content += "</table>\n\n<br />\n\n<table>\n\n"

        ##

        rc = RESULTS_COUNTER
        total = rc.total()
        max_digits = len(str(total))

        ##
        title_text = "Number of cases"
        result_text = (" " * max_digits) + f"   {total}"
        html_result_text = result_text.strip()

        ##
        self.html_content += (
            "    <tr>\n"
            f'        <td class="text-right">{title_text}:</td>\n'
            f'        <td class="text-right"><span class="monospaced-text">{html_result_text}</span></td>\n'
            "    </tr>\n"
        )

        ##

        title_obj, result_obj = objs = (

            _get_title_result_labels(
                f"{title_text}:",
                TEXT_SETTINGS,
                result_text,
                MONO_TEXT_SETTINGS,
            )

        )

        title_obj.rect.topright = (0, top)
        result_obj.rect.topleft = (10, top)

        overall_objs.extend(objs)

        ##

        top = overall_objs.rect.bottom

        for key, title in (
            ('passed', "Passed"),
            ('failed', "Failed"),
            ('error', "Error"),
        ):

            result_text = (
                str(rc[key]).rjust(max_digits, ' ')
                + f" / {total}"
            )

            self.html_content += (
                "    <tr>\n"
                f'        <td class="text-right">{title}:</td>\n'
                f'        <td class="text-right"><span class="monospaced-text">{result_text}</span></td>\n'
                "    </tr>\n"
            )

            title_obj, result_obj = objs = (

                _get_title_result_labels(
                    f'{title}:',
                    TEXT_SETTINGS,
                    result_text,
                    MONO_TEXT_SETTINGS,
                )

            )

            title_obj.rect.topright = (0, top)
            result_obj.rect.topleft = (10, top)

            overall_objs.extend(objs)

            top = overall_objs.rect.bottom

        ##

        top += 20

        for key in APP_REFS.system_info:

            ## ignore 'utc_offset' key, since its data was already
            ## presented before (as "Timezone")
            if key == 'utc_offset':
                continue

            value = str(rd[key])

            title_text = key

            self.html_content += (
                "    <tr>\n"
                f'        <td class="text-right">{title_text}:</td>\n'
                f'        <td>{value}</td>\n'
                "    </tr>\n"
            )

            title_obj, result_obj = objs = (

                _get_title_result_labels(
                    f"{title_text}:",
                    TEXT_SETTINGS,
                    value,
                    TEXT_SETTINGS,
                )

            )

            title_obj.rect.topright = (0, top)
            result_obj.rect.topleft = (10, top)

            overall_objs.extend(objs)

            top = overall_objs.rect.bottom


        ###
        self.html_content += "</table>\n\n"
        ###

        return (

            Object2D.from_surface(

                unite_surfaces(

                    (
                        (obj.image, obj.rect)
                        for obj in overall_objs
                    ),

                    background_color=REPORT_BG,

                )

            )

        )

    def get_case_buttons(self):

        ###

        rd = self.report_data

        requested_cases = rd['requested_cases']
        cases_stats = rd['test_cases_stats']

        ###

        sorted_case_buttons = List2D(

            Button(

                combine_surfaces(

                    (

                        CASE_RESULT_TO_SURF[cases_stats[case_id]['result']],

                        render_text(
                            text=(
                                'STC '
                                + format(case_id, ID_FORMAT_SPEC)
                                + " - "
                                + TEST_ID_TO_TITLE[case_id]
                            ),
                            **MONO_TEXT_SETTINGS,
                        ),

                    ),
                    retrieve_pos_from='midright',
                    assign_pos_to='midleft',
                    offset_pos_by=(5, 0),
                    padding=2,
                    background_color=REPORT_BG,
                ),
                command=partial(self.jump_to_case_related_stats, case_id),
                case_id=case_id,
            )

            for case_id in sorted(

                ## items
                requested_cases,

                ## - problematics first (error, failed, then passed)
                ## - then by id
                key=(lambda item: (cases_stats[item]['result'], item)),
            )

        )

        sorted_case_buttons.rect.snap_rects_ip(

            retrieve_pos_from='bottomleft',
            assign_pos_to='topleft',
            offset_pos_by=(0, 4),

        )

        ### store copies of the surfaces in a map for future usage
        ### and draw a border around the original surfaces

        ccm = self.case_caption_map = {}

        for obj in sorted_case_buttons:
            ccm[obj.case_id] = obj.image.copy()
            draw_border(obj.image, (0, 0, 0))

        ###
        return sorted_case_buttons

    def get_case_stats_and_back_to_case_list_buttons(self):

        ###
        case_stats = self.report_data['test_cases_stats']

        ###
        case_related_objs = List2D()

        ###

        case_objs = List2D()

        for button in self.case_buttons: # buttons are already sorted

            ##

            case_id = button.case_id
            case_data = case_stats[case_id]

            ###
            top = 0
            ###

            case_html_id = 'stc' + format(case_id, ID_FORMAT_SPEC)
            case_result = case_data['result']
            class_name = CSS_CLASS_NAME_MAP[case_result]
            emoji_char = EMOJI_MAP[case_result]

            text=(
                'STC '
                + format(case_id, ID_FORMAT_SPEC)
                + " - "
                + TEST_ID_TO_TITLE[case_id]
            )

            self.html_content += (
                f'<h3 id="{case_html_id}"><span class="{class_name}">{emoji_char}</span>'
                f' <span class="monospaced-text">{text}</span></h3>\n\n'
            )

            ## result

            self.html_content += '<table>\n\n'

            title_text = 'Result'

            self.html_content += (
                '<tr>\n'
                f'    <td class="text-right">{title_text}:</td>\n'
                f'    <td><span class="{class_name}">{case_result}</span></td>\n'
                '</tr>\n'
            )

            title_obj, result_obj = objs = (

                _get_title_result_labels(
                    f"{title_text}:",
                    TEXT_SETTINGS,
                    case_result,
                    TEXT_SETTINGS_FOR_CASE_RESULT[case_result]
                )

            )

            title_obj.rect.topright = (0, top)
            result_obj.rect.topleft = (10, top)

            case_objs.extend(objs)

            top = case_objs.rect.bottom

            ## include error message if any

            if case_result == 'error':

                error_msgs = case_data['errors']

                error_msg_list = (
                    '<ul>\n'
                    + '\n'.join(f'<li>{error_msg}</li>' for error_msg in error_msgs)
                    + '\n</ul>\n'
                )

                title_text = "Error messages"

                self.html_content += (
                    '<tr>\n'
                    f'    <td class="text-right">{title_text}:</td>\n'
                    f'    <td>\n'
                    f'{error_msg_list}\n'
                    '     </td>\n'
                    '</tr>\n'
                )

                title_obj = Object2D.from_surface(
                    surface=(
                        render_text(
                            text=f"{title_text}:",
                            **TEXT_SETTINGS,
                        )
                    ),
                )

                error_msg_surfs = [

                    render_text(
                        text=f'- {error_message}',
                        **MONO_TEXT_SETTINGS
                    )

                    for error_message in error_msgs

                ]

                result_obj = (
                    Object2D.from_surface(
                        combine_surfaces(
                            error_msg_surfs,
                            retrieve_pos_from='bottomleft',
                            assign_pos_to='topleft',
                            offset_pos_by=(0, 4),
                            background_color=REPORT_BG,
                        )
                    )
                )

                title_obj.rect.topright = (0, top)
                result_obj.rect.topleft = (10, top)

                case_objs.extend((title_obj, result_obj))

                top = case_objs.rect.bottom

            ## start time, end time

            for key, title in (
                ('start_time', "Start time"),
                ('end_time', "End time"),
            ):

                data_text = case_data[key]

                self.html_content += (
                    '<tr>\n'
                    f'    <td class="text-right">{title}:</td>\n'
                    f'    <td><span class="monospaced-text">{data_text}</span></td>\n'
                    '</tr>\n'
                )

                title_obj, result_obj = objs = (

                    _get_title_result_labels(
                        f"{title}:",
                        TEXT_SETTINGS,
                        data_text,
                        MONO_TEXT_SETTINGS,
                    )

                )

                title_obj.rect.topright = (0, top)
                result_obj.rect.topleft = (10, top)

                case_objs.extend(objs)

                top = case_objs.rect.bottom

            ## duration

            title_text = "Duration"

            duration = _get_formatted_duration(
                case_data['start_time'], case_data['end_time']
            )

            self.html_content += (
                '<tr>\n'
                f'    <td class="text-right">{title_text}:</td>\n'
                f'    <td><span class="monospaced-text">{duration}</span></td>\n'
                '</tr>\n'
            )

            title_obj, result_obj = objs = (

                _get_title_result_labels(
                    f"{title_text}:",
                    TEXT_SETTINGS,
                    duration,
                    MONO_TEXT_SETTINGS,
                )

            )

            title_obj.rect.topright = (0, top)
            result_obj.rect.topleft = (10, top)

            case_objs.extend(objs)

            ##

            assertions_result_triplets = case_data['assertions_result_triplets']

            if assertions_result_triplets:

                title_text = "Assertions"

                list_text = '<ul>\n'

                for (
                    frame_index, assertion_text, assertion_result
                ) in assertions_result_triplets:

                    key = 'passed' if assertion_result else 'failed'
                    emoji_char = EMOJI_MAP[key]
                    class_name = CSS_CLASS_NAME_MAP[key]

                    index_text = str(frame_index).rjust(4, '0')

                    list_text += (
                        f'  <li><span class="{class_name}">{emoji_char}</span>'
                        f' <span class="monospaced-text">{index_text}</span>'
                        f' - {assertion_text}</li>\n'
                    )

                list_text += '</ul>\n'

                self.html_content += (
                    '<tr>\n'
                    f'    <td class="text-right text-top">{title_text}:</td>\n'
                    f'    <td>{list_text}</td>\n'
                    '</tr>\n'
                )

                top = case_objs.rect.bottom

                title_obj = Object2D.from_surface(

                    surface=(
                        render_text(
                            text=f'{title_text}:',
                            **TEXT_SETTINGS,
                        )
                    ),
                )

                assertion_surfs = [

                    combine_surfaces(

                        (
                            # icon surf

                            (PASSED_SURF if assertion_result else FAILED_SURF),

                            # text surf

                            combine_surfaces(

                                (
                                    render_text(
                                        text = str(frame_index).rjust(4, '0'),
                                        **MONO_TEXT_SETTINGS,
                                    ),

                                    render_text(
                                        text = ' - ' + assertion_text,
                                        **TEXT_SETTINGS,
                                    ),
                                ),

                                retrieve_pos_from='midright',
                                assign_pos_to='midleft',
                                background_color=REPORT_BG,

                            ),

                        ),

                        retrieve_pos_from='midright',
                        assign_pos_to='midleft',
                        offset_pos_by=(5, 0),
                        background_color=REPORT_BG,

                    )

                    for (
                        frame_index, assertion_text, assertion_result
                    ) in assertions_result_triplets

                ]


                result_obj = (

                    Object2D.from_surface(
                        combine_surfaces(
                            assertion_surfs,
                            retrieve_pos_from='bottomleft',
                            assign_pos_to='topleft',
                            offset_pos_by=(0, 4),
                            background_color=REPORT_BG,
                        )
                    )

                )

                title_obj.rect.topright = (0, top)
                result_obj.rect.topleft = (10, top)

                case_objs.extend((title_obj, result_obj))

            self.html_content += '</table>\n\n'

            ## case title label

            case_title_label = (
                Object2D.from_surface(self.case_caption_map[case_id])
            )

            case_objs.rect.topleft = case_title_label.rect.move(40, 10).bottomleft
            case_objs.insert(0, case_title_label)

            ##

            case_related_objs.append(

                Object2D.from_surface(

                    unite_surfaces(

                        (
                            (obj.image, obj.rect)
                            for obj in case_objs
                        ),

                        background_color=REPORT_BG,

                    ),
                    case_id=case_id,

                )
            )

            case_objs.clear()

            ##

            case_related_objs.append(
                Button(
                    BACK_TO_CASE_LIST_SURF,
                    command=self.back_to_case_list,
                )
            )

            self.html_content += (
                f'<div class="block-link"><a href="#case-list">⇧ Back to case list</a></div>\n\n'
            )

            ##

        ##

        case_related_objs.rect.snap_rects_ip(
            retrieve_pos_from='bottomleft',
            assign_pos_to='topleft',
            offset_pos_by=(0, 20),
        )

        return case_related_objs

def _get_title_result_labels(
        title,
        title_render_settings,
        result,
        result_render_settings
    ):

    title_label = Object2D.from_surface(
        surface=(
            render_text(
                text=title,
                **title_render_settings,
            )
        ),
    )

    result_label = Object2D.from_surface(
        surface=(
            render_text(
                text=result,
                **result_render_settings
            )
        ),
    )

    return (title_label, result_label)


def _get_formatted_duration(start_time_text, end_time_text):
    
    delta = (
        datetime.strptime(end_time_text, DATETIME_STR_FORMAT_CODE)
        - datetime.strptime(start_time_text,  DATETIME_STR_FORMAT_CODE)
    )

    friendly_delta = round(delta.total_seconds(), 1)

    return f"~{friendly_delta}s ({delta})"
