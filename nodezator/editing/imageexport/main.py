"""Facility for editing assistant exporting operations."""

### standard library imports

from os import linesep

from time import time

from pathlib import Path

from itertools import chain

from functools import partial

from xml.etree.ElementTree import (
    Element,
    tostring as element_to_string,
)

from xml.dom.minidom import parseString

from html import unescape

from textwrap import dedent


### third-party imports

from pygame import Surface

from pygame.image import save as save_image


### local imports

from ...config import APP_REFS

from ...dialog import create_and_show_dialog

from ...logman.main import get_new_logger

from ...our3rdlibs.userlogger import USER_LOGGER

from ...ourstdlibs.timeutils import friendly_delta_from_secs

from ...our3rdlibs.behaviour import set_status_message

from ...surfsman.svgexport import GENERAL_SURFACES_CSS

from ...graphman.callablenode.export import CALLABLE_NODE_CSS
from ...graphman.proxynode.export import PROXY_NODE_CSS
from ...graphman.stlibnode.export import STLIB_NODE_CSS
from ...graphman.thirdlibnode.export import THIRDLIB_NODE_CSS
from ...graphman.builtinnode.export import BUILTIN_NODE_CSS
from ...graphman.capsulenode.export import CAPSULE_NODE_CSS
from ...graphman.genviewernode.export import GENVIEWER_NODE_CSS
from ...graphman.operatornode.export import OPERATOR_NODE_CSS
from ...graphman.textblock.export import TEXT_BLOCK_CSS
from ...graphman.socket.surfs import SOCKET_AND_LINE_CSS
from ...graphman.widget.export import WIDGET_CSS

from ...graphman.callablenode.outputviz import PREVIEW_OBJECTS_CSS

from .form import get_image_exporting_settings


### create logger for module
logger = get_new_logger(__name__)


def export_as_image():
    """Export loaded file as .html/.svg or .png file.

    The current state of the file is exported, that is,
    the objects currently alive, regardless of whether
    they are saved or not in the disk.
    """
    ###
    gm = APP_REFS.gm

    ### if there are no live objects at all in the
    ### file, notify user via dialog and cancel
    ### operation by returning earlier

    if not gm.nodes and not gm.text_blocks:

        create_and_show_dialog(
            (
                "To export the loaded file as an image there"
                " must exist at least one live object in it"
            ),
            level_name='info',
        )

        return

    ### reference instance of a rects manager that controls the
    ### position of all objects in the loaded file
    all_rectsman = gm.rectsman

    ### store the size of the resulting rects manager
    size = all_rectsman.size

    ### prompt user for image exporting settings
    ### (passing along the total size occupied by
    ### the objects in the loaded file as additional
    ### info to be displayed to the user)
    settings = get_image_exporting_settings(size)

    ### if the settings received are actually None,
    ### it means the user cancelled the operation,
    ### so we exit the method by returning
    if settings is None:
        return

    ### otherwise we proceed with the image exporting
    ### operation...

    ### let's measure the time taken to export the
    ### image
    start = time()

    ### backup the topleft
    original_topleft = all_rectsman.topleft

    ### move objects' topleft to the given margins

    all_rectsman.topleft = (
        settings.pop("horizontal_margin"),
        settings.pop("vertical_margin"),
    )

    ### obtain a pathlib.Path version of the image path
    image_path = Path(settings["image_path"])

    ### retrieve the extension
    extension = image_path.suffix.lower()

    ### pick image exporting method according to the
    ### file format

    if extension == ".png":
        export_method = export_file_as_png

    elif extension == ".svg":
        export_method = export_file_as_svg

    elif extension == ".html":
        export_method = export_file_as_html

    ### try creating and saving image

    try:
        export_method(**settings)

    except Exception as err:

        ## log traceback in regular
        ## log and and user log

        error_message = (
            "An unexpected error ocurred"
            " while trying to export node"
            f" layout as {extension}."
        )

        logger.exception(error_message)
        USER_LOGGER.exception(error_message)

    else:
        error_message = ''

    ### then restore the objects to their original
    ### positions
    all_rectsman.topleft = original_topleft

    ### store the total time taken to execute the
    ### operations above
    total = time() - start

    ### if there was an error (there is an error messsage),
    ### notify the user via a dialog

    if error_message:

        dialog_message = error_message + (
            " Check the user log for more info (on the graph/canvas, press"
            " <Ctrl+Shift+j> or access the \"Help > Show user log\" option"
            " on the menubar)."
        )

        create_and_show_dialog(dialog_message, level_name='error')

    ### otherwise just display a message in the
    ### statusbar, showing the time taken in a
    ### friendly format

    else:

        message = ("File exported as '{}' image in {}").format(
            image_path.name, friendly_delta_from_secs(total)
        )

        set_status_message(message)


def export_file_as_web_markup(
    width,
    height,
    background_color,
    image_path,
    raster_for_previews,
    export_html,
):
    """Export loaded file as a .svg image file.

    That is, the current state of the file is exported,
    the objects currently alive, regardless of whether
    they are saved on disk.
    """
    ### create svg element

    svg = Element(
        "svg",
        {
            "width": str(width),
            "height": str(height),
            "xmlns": "http://www.w3.org/2000/svg",
            "xmlns:xlink": "http://www.w3.org/1999/xlink",
        },
    )

    ## create style element

    try:
        background_color[3]

    except IndexError:

        bg_color_style = f"fill:rgb{background_color};"

    else:

        bg_color_style = (
            f"fill:rgb{background_color[:3]};"
            "fill-opacity:"
            f"{round(background_color[3]/255, 3)};",
        )

    style = Element("style")

    style.text = (
        dedent(
            f"""
      rect.graph_bg {{{bg_color_style}}}

      .checker_a {{
        fill: rgb(235, 235, 235);
      }}

      .checker_b {{
        fill: rgb(20, 20, 20);
      }}
      """
        )
        + GENERAL_SURFACES_CSS
        + CALLABLE_NODE_CSS
        + PROXY_NODE_CSS
        + STLIB_NODE_CSS
        + THIRDLIB_NODE_CSS
        + BUILTIN_NODE_CSS
        + CAPSULE_NODE_CSS
        + GENVIEWER_NODE_CSS
        + OPERATOR_NODE_CSS
        + SOCKET_AND_LINE_CSS
        + TEXT_BLOCK_CSS
        + WIDGET_CSS
        + PREVIEW_OBJECTS_CSS
    )

    ### if we are to export an html page, create
    ### related tags and append style in the
    ### head element

    if export_html:

        html = Element("html")
        head = Element("head")
        body = Element("body")

        html.extend([head, body])

        title = Element("title")

        title.text = "Nodezator graph (python callables graph)"

        head.extend([title, style])

        body.append(svg)

    ### otherwise...
    else:
        svg.append(style)

    ## append a rect representing the background

    svg.append(
        Element(
            "rect",
            {
                "x": "0",
                "y": "0",
                "width": str(width),
                "height": str(height),
                "class": "graph_bg",
            },
        )
    )

    ## create and append pattern

    pattern = Element(
        "pattern",
        {
            "x": "0",
            "y": "0",
            "width": "10",
            "height": "10",
            "id": "checker_pattern",
            "patternUnits": "userSpaceOnUse",
        },
    )

    for x, y in ((0, 0), (5, 5)):

        pattern.append(
            Element(
                "rect",
                {
                    "x": str(x),
                    "y": str(y),
                    "width": "5",
                    "height": "5",
                    "class": "checker_a",
                },
            )
        )

    for x, y in ((0, 5), (5, 0)):

        pattern.append(
            Element(
                "rect",
                {
                    "x": str(x),
                    "y": str(y),
                    "width": "5",
                    "height": "5",
                    "class": "checker_b",
                },
            )
        )

    svg.append(pattern)

    ##

    if raster_for_previews:

        path = Path(image_path)

        parent = path.parent / (path.stem + "_files")

        APP_REFS.preview_handling_kit = (
            {},
            {},
            parent.name,
        )

    ###
    gm = APP_REFS.gm

    ## append preview panels and toolbars

    svg.extend(
        [
            obj.svg_repr()
            for obj in chain(
                gm.preview_panels,
                gm.preview_toolbars,
            )
        ]
    )

    ## append lines
    svg.extend(list(gm.yield_lines_as_svg()))

    ## append nodes and text blocks

    svg.extend(
        [
            obj.svg_repr()
            for obj in chain(
                gm.nodes,
                gm.text_blocks,
            )
        ]
    )

    ### save raster previews

    if raster_for_previews:

        if parent.is_file():

            raise RuntimeError(
                "Exporting can't proceed;"
                f" {parent} must not be a file"
                " (it must either be a directory"
                " or not exist at all, so that"
                " we can create/use it) to save"
                " the raster previews"
            )

        ## save raster previews

        preview_surf_map, preview_name_map = APP_REFS.preview_handling_kit[:2]

        # if there are raster previews to be saved
        # and the parent folder to be used doesn't
        # exist, create the parent folder
        if preview_surf_map and not parent.exists():
            parent.mkdir()

        # save

        for (key, surf) in preview_surf_map.items():

            name = preview_name_map[key]
            save_image(surf, str(parent / name))

        ## clear collections and delete preview
        ## handling kit

        for obj in APP_REFS.preview_handling_kit[:2]:
            obj.clear()

        del APP_REFS.preview_handling_kit

    ### define root element to save
    root = html if export_html else svg

    ### then save the root as markup text in the given
    ### path

    with (
        open(
            image_path,
            mode="w",
            encoding="utf-8",
        )
    ) as f:

        text = parseString(
            element_to_string(root, encoding="unicode")
        ).toprettyxml()

        if export_html:

            text = linesep.join(["<!DOCTYPE html>"] + text.splitlines()[1:])

        ### unescape all css lines

        for index, line in enumerate(text.splitlines()):

            if line.strip() == "<style>":
                css_start = index + 1

            elif line.strip() == "</style>":
                css_end = index

        text = linesep.join(
            unescape(line) if css_start <= index <= css_end else line
            for index, line in enumerate(text.splitlines())
        )

        ###
        f.write(text)

export_file_as_html = partial(
    export_file_as_web_markup,
    export_html=True,
)

export_file_as_svg = partial(
    export_file_as_web_markup,
    export_html=False,
)

def export_file_as_png(width, height, background_color, image_path):
    """Export loaded file as an .png image file.

    That is, the current state of the file is exported,
    the objects currently alive, regardless of whether
    they are saved on disk.
    """
    ### create a new surface according to the color
    ### picked and image file format

    ## pick surface conversion method according to
    ## whether the color has alpha (transparency)

    try:
        alpha = background_color[3]

    except IndexError:
        conversion_method = Surface.convert

    else:

        conversion_method = (
            Surface.convert if alpha == 255 else Surface.convert_alpha
        )

    ## create the surface using the appropriate
    ## conversion method
    surf = conversion_method(Surface((width, height)))

    ## fill surface with chosen color
    surf.fill(background_color)

    ###
    gm = APP_REFS.gm

    ### draw objects on the surface we just created

    ## preview objects

    for obj in chain(
        gm.preview_panels,
        gm.preview_toolbars,
    ):
        obj.draw_on_surf(surf)

    ## lines
    gm.draw_lines_on_surf(surf)

    ## nodes

    for node in gm.nodes:
        node.draw_on_surf(surf)

    ## text blocks
    gm.text_blocks.draw_on_surf(surf)

    ### then save the image in the given path
    save_image(surf, image_path)
