"""Facility w/ loop holder representing a splash screen."""


### local imports

from ..config import APP_REFS

from ..translation import TRANSLATION_HOLDER as t

from ..pygameconstants import SCREEN

from ..appinfo import (
    APP_VERSION,
    NO_RELEASE_LEVEL_FULL_TITLE,
)

from ..recentfile import get_recent_files

from ..logman.main import get_new_logger

from ..classes2d.single import Object2D
from ..classes2d.collections import List2D

from ..surfsman.draw import (
    draw_depth_finish,
    draw_linear_gradient,
)

from ..surfsman.render import render_rect

from ..surfsman.icon import render_layered_icon

from ..imagesman.cache import CachedImageObject

from ..textman.render import render_text

from ..textman.label.main import Label

from ..colorsman.colors import (
    BLACK,
    WHITE,
    SPLASH_BG,
    SPLASH_ROBOT_BG,
    SPLASH_SHADOW_COLOR,
    NODE_BODY_BG,
)

from .constants import (
    TEXT_SETTINGS,
    URL_TEXT_SETTINGS,
    TITLE_FONT_HEIGHT,
    SOFTWARE_KIND_FONT_HEIGHT,
    SUBHEADING_FONT_HEIGHT,
    RELEASE_LEVEL_TEXT_SETTINGS,
    SHADOW_THICKNESS,
)

from .factoryfuncs import (
    get_project_link_objs,
    get_powered_link_objs,
    get_action_objs,
    get_recent_file_objs,
    get_license_declaration_obj,
)

from .animsetup import (
    set_node_animation,
    set_robot_animation,
)

## class extension
from .op import SplashScreenOperations


### create logger for module
logger = get_new_logger(__name__)


class SplashScreen(SplashScreenOperations):
    """loop holder representing a splash screen."""

    def __init__(self):
        """Create support objects for the splash screen."""

        logger.info("Instantiating splash screen.")

        ### obtain and store an object w/ a surface
        ### representing the application icon used in
        ### the splash screen

        self.app_icon = Object2D.from_surface(
            render_layered_icon(
                chars=[chr(ordinal) for ordinal in (183, 184, 185)],
                dimension_name="width",
                dimension_value=88,
                colors=[BLACK, WHITE, (77, 77, 105)],
                background_width=92,
                background_height=92,
            )
        )

        ### obtain and store an object whose surface
        ### represents text describing the kind of software
        ### this application represents

        self.kind_label = Object2D.from_surface(
            surface=render_text(
                text=t.splash_screen.node_editor,
                ## text settings w/ different
                ## font height
                **{
                    **TEXT_SETTINGS,
                    "font_height": (SOFTWARE_KIND_FONT_HEIGHT),
                },
            )
        )

        ### obtain and store an object whose surface
        ### represents the text of the application title

        self.title_label = Object2D.from_surface(
            surface=render_text(
                text=NO_RELEASE_LEVEL_FULL_TITLE,
                ## text settings w/ different
                ## font height
                **{**TEXT_SETTINGS, "font_height": TITLE_FONT_HEIGHT},
            )
        )

        ### obtain and store an object whose surface
        ### represents the text of a subheading for
        ### the application

        self.subheading_label = Object2D.from_surface(
            surface=render_text(
                text=(t.splash_screen.nodes_from_functions),
                ## text settings w/ different
                ## font height
                **{**TEXT_SETTINGS, "font_height": SUBHEADING_FONT_HEIGHT},
            )
        )

        ### obtain and store an object whose surface
        ### represents the text of the application
        ### release level

        self.release_level_label = Object2D.from_surface(
            surface=render_text(
                text=APP_VERSION.release_level,
                ## different text settings for
                ## release level
                **RELEASE_LEVEL_TEXT_SETTINGS,
            )
        )

        ### create objects whose surfaces contain both
        ### images and text, representing links and actions
        ### (things like creating a new file)

        ## link objects

        self.project_link_objs = get_project_link_objs()
        self.powered_link_objs = get_powered_link_objs()

        ## action objects
        self.action_objs = get_action_objs()

        ### also create the same kind of objects, but
        ### representing recent files the user can choose
        ### to open (if there are such files)

        self.recent_files = get_recent_files()

        self.recent_file_objs = get_recent_file_objs(self.recent_files)

        ### create and store an object representing
        ### the license declaration

        self.license_declaration = get_license_declaration_obj()

        ### create and set objects to support animation
        self.set_animation_support_objects()

        ### url label;
        ###
        ### the 100 is a temporary value which is
        ### replaced by self.rect.width minus 10 within
        ### the positioning method

        self.url_label = Label(
            text="url",
            max_width=100,
            **URL_TEXT_SETTINGS,
        )

        ### position objects
        self.position_and_define_boundaries()

        ### define an attribute to hold a reference to
        ### the rect of an object hovered by the mouse
        ### or hold None, when there aren't any
        self.hovered_rect = None

        ### define a flag to indicate when the url label
        ### must be drawn
        self.draw_url_label = False

        ### append the splash screen centering method
        ### as a window resizing setup

        APP_REFS.window_resize_setups.append(self.center_splashscreen)

        ### set update operation
        self.update = self.update_animation

    def set_animation_support_objects(self):
        """Create and set objects for the animation."""
        ### create object whose image attribute represents
        ### a robot

        self.robot = CachedImageObject(
            "splash_nodezator_robot.png",
            {"use_alpha": True},
        )

        ### define a reference center position for the
        ### nodes
        center = self.robot.rect.move(-20, -5).topright

        ### create objects representing nodes

        ## build a custom list of objects representing
        ## nodes

        self.floating_nodes = List2D(
            Object2D.from_surface(
                render_layered_icon(
                    chars=[chr(ordinal) for ordinal in (177, 178, 179)],
                    dimension_name="height",
                    dimension_value=20,
                    colors=[
                        BLACK,
                        color,
                        NODE_BODY_BG,
                    ],
                    background_width=27,
                    background_height=27,
                )
            )
            for color in (
                (185, 0, 100),
                (0, 185, 100),
                (0, 155, 185),
            )
        )

        ### set animation for each node and update the
        ### node animation

        for index, node in enumerate(self.floating_nodes):

            set_node_animation(
                index=index,
                node=node,
                parent=self.robot,
            )

            node.update()

        ### reference all objects in the same custom list

        self.animation_objects = List2D(
            [
                self.robot,
                *self.floating_nodes,
            ]
        )

        ### create and store an object whose image will
        ### be used as a background for the animation,
        ### representing a gradient

        ## define the size of the object starting from
        ## the area occupied by the existing objects,
        ## incremented 60 and 30 pixels in width and
        ## height, respectively

        width, height = self.animation_objects.rect.inflate(30, 40).size

        ## use the center of the existing objects as
        ## the center for this gradient object
        center = self.animation_objects.rect.center

        ## create the object with a surface made of
        ## a solid color (default is black), already
        ## properly positioned

        gradient_bg = Object2D.from_surface(
            surface=render_rect(width, height),
            coordinates_name="center",
            coordinates_value=center,
        )

        ## now, finally draw the gradient in the object's
        ## surface then store it in the beginning of the
        ## custom list for animation objects

        # draw gradient

        draw_linear_gradient(
            gradient_bg.image,
            SPLASH_ROBOT_BG,
            start_percentage=0.5,
            stop_percentage=1,
            max_lightness_percentage=1.0,
            min_lightness_percentage=0.4,
            direction="top_to_bottom",
        )

        # store object
        self.animation_objects.insert(0, gradient_bg)

        ### set robot animation

        set_robot_animation(
            robot=self.robot,
            parent=gradient_bg,
        )

        self.robot.update()

        ### gather update operations for animated objects
        ### in a single list stored in a dedicated attribute

        ## robot's update operation must come first
        self.anim_update_operations = [self.robot.update]

        ## then we extend the list with the nodes' update
        ## operations

        self.anim_update_operations.extend(node.update for node in self.floating_nodes)

    def position_and_define_boundaries(self):
        """Position objs, defining splash screen boundaries.

        The boundaries are only defined if they were not
        defined before or if, after positioning the objects,
        the resulting area is different than in the previous
        time the boundaries were defined.

        In other words, we only (re)define the boundaries
        when absolutely needed.
        """
        ### create custom list representing objects
        ### inside a header and use it to reference
        ### and position objects that should be inside
        ### it

        header = List2D()

        ## append the app icon to the header
        header.append(self.app_icon)

        ## position the title label relative to header
        ## and append it too

        self.title_label.rect.bottomleft = self.app_icon.rect.move(5, 0).bottomright

        header.append(self.title_label)

        ## do the same with the kind and subheading labels

        self.kind_label.rect.bottomleft = self.title_label.rect.move(0, 8).topleft

        header.append(self.kind_label)

        self.subheading_label.rect.midtop = header.rect.midbottom

        header.append(self.subheading_label)

        ## position the release level label relative to
        ## the kind label and also append it to the header

        self.release_level_label.rect.midleft = self.kind_label.rect.move(
            10, 0
        ).midright

        header.append(self.release_level_label)

        ### create custom list representing objects
        ### inside the splash screen body and use it to
        ### reference and position objects that should be
        ### inside it

        body = List2D()

        ## append the animation objects
        body.extend(self.animation_objects)

        ##

        file_related_objs = List2D(self.action_objs + self.recent_file_objs)

        if self.recent_file_objs:

            self.recent_file_objs.rect.topleft = self.action_objs.rect.move(
                0, 10
            ).bottomleft

        file_related_objs.rect.topleft = body.rect.move(20, 0).topright

        body.extend(file_related_objs)

        ##
        self.project_link_objs.rect.topleft = body.rect.move(20, 0).topright

        body.extend(self.project_link_objs)

        ### position header, license declaration and
        ### powered link objects relative to body

        header.rect.midbottom = body.rect.move(0, -20).midtop

        self.license_declaration.rect.topright = body.rect.move(-30, 30).midbottom

        self.powered_link_objs.rect.topleft = body.rect.move(30, 20).midbottom

        ### reference all objects in the header and body
        ### and also the license declaration and powered
        ### link objects list in a single special list,
        ### stored both locally and in its own attribute

        all_objs = self.all_objs = List2D(
            header + body + [self.license_declaration] + self.powered_link_objs
        )

        ### create and store a surface representing the
        ### splash screen, which is 30 pixels larger
        ### both horizontally and vertically

        self.image = render_rect(*all_objs.rect.inflate(20, 40).size, SPLASH_BG)

        ### draw a depth finish around the image
        draw_depth_finish(self.image)

        ### obtain a rect for the surface
        self.rect = self.image.get_rect()

        ### update the url_label's max_width
        self.url_label.max_width = self.rect.width - 10

        ### create and store a custom list wherein to
        ### store buttons; the list must be store both
        ### in an attribute and in local variable
        buttons = self.buttons = List2D()

        ### now iterate over all objects, storing those
        ### which work as buttons in the corresponding
        ### list, that is, those which have specific
        ### attributes

        for obj in all_objs:

            if any(
                hasattr(obj, attr) for attr in ("on_mouse_click", "on_mouse_release")
            ):
                buttons.append(obj)

        ### define surfaces with solid colors to represent
        ### the shadows at the bottom and right of the
        ### splash screen

        ## define the width and height of the shadows

        lower_shadow_width, right_shadow_height = self.rect.size

        right_shadow_width = lower_shadow_height = SHADOW_THICKNESS

        ## create the lower shadow

        self.lower_shadow = Object2D.from_surface(
            surface=render_rect(
                lower_shadow_width,
                lower_shadow_height,
                color=SPLASH_SHADOW_COLOR,
            ),
        )

        ## create the right shadow

        self.right_shadow = Object2D.from_surface(
            surface=render_rect(
                right_shadow_width,
                right_shadow_height,
                color=SPLASH_SHADOW_COLOR,
            ),
        )

        ### center the splashscreen
        self.center_splashscreen()

    def center_splashscreen(self):

        center = SCREEN.get_rect().center

        self.rect.center = center

        self.all_objs.rect.center = center

        ## define values to offset the lower shadow
        ## horizontally and the right shadow vertically

        lower_shadow_x_offset = right_shadow_y_offset = SHADOW_THICKNESS

        topleft_of_lower = self.rect.move(lower_shadow_x_offset, 0).bottomleft

        self.lower_shadow.rect.topleft = topleft_of_lower

        topleft_of_right = self.rect.move(0, right_shadow_y_offset).topright

        self.right_shadow.rect.topleft = topleft_of_right

        ###
        self.url_label.rect.bottomleft = self.rect.move(1, -1).bottomleft
