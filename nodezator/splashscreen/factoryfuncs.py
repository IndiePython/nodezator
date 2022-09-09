"""Factory functions for the splash screen."""

### standard library imports

from functools import partial

from webbrowser import open as open_url


### local imports

from ..config import APP_REFS

from ..translation import TRANSLATION_HOLDER as t

from ..logman.main import get_new_logger

from ..ourstdlibs.behaviour import get_oblivious_callable

from ..htsl.main import open_htsl_link

from ..rectsman.main import RectsManager

from ..classes2d.single import Object2D
from ..classes2d.collections import List2D

from ..surfsman.draw import blit_aligned

from ..surfsman.render import (
    combine_surfaces,
    unite_surfaces,
    render_rect,
)

from ..surfsman.icon import render_layered_icon

from ..imagesman.cache import IMAGE_SURFS_DB

from ..textman.render import (
    render_text,
    render_multiline_text,
)

from ..colorsman.colors import (
    BLACK,
    WHITE,
    SPLASH_BG,
    NODE_BODY_BG,
)

from .constants import TEXT_SETTINGS


### create logger for module
logger = get_new_logger(__name__)


### surfs

NATIVE_FILE_ICON = render_layered_icon(
    chars=[chr(ordinal) for ordinal in (183, 184, 185)],
    dimension_name="width",
    dimension_value=22,
    colors=[BLACK, WHITE, (77, 77, 105)],
    background_width=24,
    background_height=24,
)

NEW_NATIVE_FILE_ICON = render_layered_icon(
    chars=[chr(ordinal) for ordinal in (183, 184, 185)],
    dimension_name="width",
    dimension_value=18,
    colors=[BLACK, WHITE, (77, 77, 105)],
    background_width=19,
    background_height=19,
)

PLUS_MINI_SURF = render_layered_icon(
    chars=[chr(ordinal) for ordinal in (79, 80)],
    dimension_name="height",
    dimension_value=14,
    colors=[BLACK, (80, 220, 120)],
)

NEW_NATIVE_FILE_ICON = combine_surfaces(
    [
        NEW_NATIVE_FILE_ICON,
        PLUS_MINI_SURF,
    ],
    retrieve_pos_from="bottomright",
    assign_pos_to="bottomright",
    offset_pos_by=(5, 5),
)

WEB_ICON = render_layered_icon(
    chars=[chr(ordinal) for ordinal in (90, 91)],
    dimension_name="height",
    dimension_value=24,
    colors=[BLACK, (0, 100, 255)],
    background_width=24,
    background_height=24,
)

AWW_ICON = render_layered_icon(
    chars=[chr(ordinal) for ordinal in (90, 91)],
    dimension_name="height",
    dimension_value=20,
    colors=[BLACK, (30, 150, 80)],
    background_width=24,
    background_height=24,
)

FOLDER_ICON = render_layered_icon(
    chars=[chr(ordinal) for ordinal in (33, 34)],
    dimension_name="height",
    dimension_value=20,
    colors=[BLACK, (30, 130, 70)],
    background_width=24,
    background_height=24,
)

node_icons = [
    render_layered_icon(
        chars=[chr(ordinal) for ordinal in (177, 178, 179)],
        dimension_name="height",
        dimension_value=18,
        colors=[
            BLACK,
            color,
            NODE_BODY_BG,
        ],
        background_width=18,
        background_height=18,
    )
    for color in (
        (185, 0, 100),
        (0, 155, 185),
        (0, 185, 100),
    )
]

NODES_GALLERY_ICON = combine_surfaces(
    node_icons,
    retrieve_pos_from="topleft",
    assign_pos_to="topleft",
    offset_pos_by=(5, 5),
)


### main functions


def get_project_link_objs():
    """Return custom list with link objects.

    That is, objects whose surfaces represent web links.
    """
    project_link_objs = List2D()

    ### create list of icon surfaces

    surfaces = [
        (
            render_layered_icon(
                chars=[chr(ordinal) for ordinal in (183, 184, 185)],
                dimension_name="width",
                dimension_value=28,
                colors=[BLACK, WHITE, (77, 77, 105)],
                background_width=30,
                background_height=30,
            )
        ),
        (IMAGE_SURFS_DB["github_mark.png"][{"use_alpha": True}]),
        (IMAGE_SURFS_DB["github_mark.png"][{"use_alpha": True}]),
        NODES_GALLERY_ICON,
        (IMAGE_SURFS_DB["indie_python_logo.png"][{"use_alpha": True}]),
        (IMAGE_SURFS_DB["kennedy_logo.png"][{"use_alpha": True}]),
        (IMAGE_SURFS_DB["twitter_logo.png"][{"use_alpha": True}]),
        (IMAGE_SURFS_DB["discord_logo.png"][{"use_alpha": True}]),
        (IMAGE_SURFS_DB["patreon_logo.png"][{"use_alpha": True}]),
        WEB_ICON,
    ]

    ### obtain a list with their rects
    rects = [surf.get_rect() for surf in surfaces]

    ### use a rects manager to position their rects relative
    ### to each other

    rectsman = RectsManager(rects.__iter__)

    rectsman.snap_rects_ip(
        retrieve_pos_from="bottomleft",
        assign_pos_to="topleft",
        offset_pos_by=(0, 5),
    )

    ### store the rectsman right, slightly offset to the
    ### right
    right = rectsman.move(10, 0).right

    ### define data to create link objects;
    ### that is, icon, label text and url for each link

    project_links_data = (
        (
            t.splash_screen.application_website,
            t.splash_screen.application_website_url,
        ),
        (
            "Source code",
            "https://github.com/IndiePython/nodezator",
        ),
        (
            "Discussions/forum",
            "https://github.com/IndiePython/nodezator/discussions",
        ),
        (
            "Find, download, publish nodes",
            "https://gallery.nodezator.com",
        ),
        (
            t.splash_screen.project_website,
            t.splash_screen.project_website_url,
        ),
        (
            t.splash_screen.developer_website,
            t.splash_screen.developer_website_url,
        ),
        (
            t.splash_screen.developer_twitter,
            "https://twitter.com/KennedyRichard",
        ),
        (
            "Join us on discord",
            "https://indiepython.com/discord",
        ),
        (
            "Support us on patreon",
            "https://patreon.com/KennedyRichard",
        ),
        (
            "Other support options",
            "https://indiepython.com/donate",
        ),
    )

    ### iterate over the surfaces, recs and link data,
    ### creating the link objects

    for icon, rect, (text, url) in zip(surfaces, rects, project_links_data):

        ### create text surface

        text_surf = render_text(text=text, **TEXT_SETTINGS)

        ### obtain a rect for the text surface and position
        ### it relative to icon rect and the rectsman right
        ### we obtained

        text_rect = text_surf.get_rect()
        text_rect.midleft = (right, rect.centery)

        ### finally obtain an union of the text and icon
        ### surfaces

        final_surf = unite_surfaces(
            [(icon, rect), (text_surf, text_rect)],
            padding=3,
            background_color=SPLASH_BG,
        )

        ### create object

        link_obj = Object2D.from_surface(
            surface=final_surf,
            on_mouse_release=(get_oblivious_callable(partial(open_url, url))),
            href=url,
        )

        ### store the link object
        project_link_objs.append(link_obj)

    ### position link objects relative to each other

    project_link_objs.rect.snap_rects_ip(
        retrieve_pos_from="bottomleft",
        assign_pos_to="topleft",
        offset_pos_by=(0, 3),
    )

    ### instantiate special label and position it relative
    ### to the links

    project_links_caption = Object2D.from_surface(
        surface=(render_text(text=t.splash_screen.links, **TEXT_SETTINGS))
    )

    project_links_caption.rect.bottomleft = project_link_objs.rect.move(-10, -5).topleft

    ### then add the label to the list of objects
    project_link_objs.insert(0, project_links_caption)

    ### finally return the list of objects
    return project_link_objs


def get_powered_link_objs():
    """Return custom list with link objects.

    That is, objects whose surfaces represent web links.
    """
    powered_link_objs = List2D()

    ### define data to create link objects;
    ### that is, icon, label text and url for each link

    powered_links_data = (
        (
            (IMAGE_SURFS_DB["python_splashscreen_icon.png"][{"use_alpha": True}]),
            "Python",
            "https://python.org",
        ),
        (
            (IMAGE_SURFS_DB["pygame_logo.png"][{"use_alpha": True}]),
            "pygame",
            "https://pygame.org/",
        ),
    )

    ### iterate over the data, creating the link objects

    for icon, text, url in powered_links_data:

        text_surf = render_text(text=text, **TEXT_SETTINGS)

        ### combine surfaces

        final_surf = combine_surfaces(
            [
                icon,
                text_surf,
            ],
            retrieve_pos_from="midright",
            assign_pos_to="midleft",
            offset_pos_by=(8, 0),
            padding=3,
            background_color=SPLASH_BG,
        )

        ### create object

        link_obj = Object2D.from_surface(
            surface=final_surf,
            on_mouse_release=(get_oblivious_callable(partial(open_url, url))),
            href=url,
        )

        ### store the link object
        powered_link_objs.append(link_obj)

    ### position link objects relative to each other

    powered_link_objs.rect.snap_rects_ip(
        retrieve_pos_from="topright",
        assign_pos_to="topleft",
        offset_pos_by=(15, 0),
    )

    ### instantiate special label and position it relative
    ### to the links

    powered_links_caption = Object2D.from_surface(
        surface=(render_text(text=t.splash_screen.powered_by, **TEXT_SETTINGS))
    )

    powered_links_caption.rect.midbottom = powered_link_objs.rect.move(0, -5).midtop

    ### then add the label to the list of objects
    powered_link_objs.insert(0, powered_links_caption)

    ### finally return the list of objects
    return powered_link_objs


def get_action_objs():
    """Return custom list with action objects.

    That is, objects which perform specific action when
    clicked (when the mouse is released, actually).
    """
    ### instantiate a custom list
    objs = List2D()

    ### instantiate and store a label with 'Actions' as
    ### its text

    actions_label = Object2D.from_surface(
        render_text(text=t.splash_screen.actions, **TEXT_SETTINGS)
    )

    objs.append(actions_label)

    ### define data for action objects to be created;
    ###
    ### each item is a tuple containing the image filename,
    ### a boolean indicating whether to use alpha or not,
    ### the text for the object and the command triggered
    ### by the object, respectively

    actions_data = (
        (NEW_NATIVE_FILE_ICON, t.splash_screen.new_file, APP_REFS.window_manager.new),
        (FOLDER_ICON, t.splash_screen.open_file, APP_REFS.window_manager.open),
        (
            AWW_ICON,
            "Read manual",
            partial(open_htsl_link, "htap://manual.nodezator.pysite"),
        ),
    )

    ### iterate over it, creating and positioning action
    ### objects

    ## define an initial topleft for the objects
    topleft = actions_label.rect.move(10, 5).bottomleft

    ## iterate

    for surf, text, command in actions_data:

        ## text surface

        text_surf = render_text(
            text=text,
            **TEXT_SETTINGS,
        )

        ## instantiate

        action_obj = Object2D.from_surface(
            surface=(
                combine_surfaces(
                    [surf, text_surf],
                    retrieve_pos_from="midright",
                    assign_pos_to="midleft",
                    offset_pos_by=(3, 0),
                )
            )
        )

        ## set 'on_mouse_release' command to perform the
        ## action
        action_obj.on_mouse_release = get_oblivious_callable(command)

        ## position the object
        action_obj.rect.topleft = topleft

        ## update the topleft used so the next object is
        ## properly positioned if there is one
        topleft = action_obj.rect.move(0, 3).bottomleft

        ## store the action object
        objs.append(action_obj)

    ### finally return the list of objects
    return objs


def get_recent_file_objs(recent_files):
    """Return custom "recent file" objects.

    That is, objects which load a recent file when clicked
    (when the mouse is released, actually).

    Parameters
    ==========
    recent_files (list)
        if not empty, each item in this list is a string
        representing the path to a previously opened file.
    """
    ### instantiate a custom list
    objs = List2D()

    ### if there are no paths listed, return the empty list,
    ### exiting the function
    if not recent_files:
        return objs

    ### otherwise, create objects representing the first
    ### files in the list

    ## instantiate and store a label with
    ## 'Open recent files..' as its text

    recent_files_label = Object2D.from_surface(
        render_text(text=t.splash_screen.open_recent_files, **TEXT_SETTINGS)
    )

    objs.append(recent_files_label)

    ## define an initial topleft for the next objects
    topleft = recent_files_label.rect.move(10, 5).bottomleft

    ## reference the 'open()' method of the window manager
    window_manager_open = APP_REFS.window_manager.open

    ## iterate over the 08 most recent files among the ones
    ## listed, creating the "recent file" objects;
    ##
    ## the quantity of files was chosen arbitrarily, based
    ## on what looked best next to the other elements;

    for filepath in recent_files[:8]:

        ## obtain text

        text_surf = render_text(
            text=filepath.name,
            **{
                **TEXT_SETTINGS,
                "max_width": 300,
            },
        )

        ## instantiate

        recent_file_obj = Object2D.from_surface(
            combine_surfaces(
                [NATIVE_FILE_ICON, text_surf],
                retrieve_pos_from="midright",
                assign_pos_to="midleft",
                offset_pos_by=(3, 0),
            )
        )

        ## set 'on_mouse_release' command to load the file

        recent_file_obj.on_mouse_release = get_oblivious_callable(
            partial(window_manager_open, filepath)
        )

        ## position the object
        recent_file_obj.rect.topleft = topleft

        ## update the topleft used so the next object is
        ## properly positioned if there is one
        topleft = recent_file_obj.rect.move(0, 3).bottomleft

        ## store the recent file object
        objs.append(recent_file_obj)

    ### finally return the list of objects
    return objs


def get_license_declaration_obj():
    """Return object representing license declaration."""
    unlicense_obj = Object2D.from_surface(
        (IMAGE_SURFS_DB["unlicense_logo.png"][{"use_alpha": True}]),
    )

    badge_obj = Object2D.from_surface(
        render_layered_icon(
            chars=[chr(ordinal) for ordinal in (56, 57, 58)],
            dimension_name="width",
            dimension_value=19,
            colors=[
                BLACK,
                (215, 215, 25),
                (200, 30, 30),
            ],
            background_width=22,
            background_height=22,
        )
    )

    text_obj = Object2D.from_surface(
        render_multiline_text(
            text=(t.splash_screen.license_declaration_text),
            max_character_no=40,
            retrieve_pos_from="bottomleft",
            assign_pos_to="topleft",
            **TEXT_SETTINGS,
        )
    )

    objs = List2D()

    objs.append(unlicense_obj)

    badge_obj.rect.topleft = unlicense_obj.rect.move(-17, -11).bottomright
    objs.append(badge_obj)

    text_obj.rect.midleft = objs.rect.move(10, 0).midright
    objs.append(text_obj)

    objs.rect.topleft = (0, 0)

    url = "https://unlicense.org"

    return Object2D.from_surface(
        surface=(
            unite_surfaces(
                [(obj.image, obj.rect) for obj in objs],
                padding=3,
                background_color=SPLASH_BG,
            )
        ),
        on_mouse_release=(get_oblivious_callable(partial(open_url, url))),
        href=url,
    )
