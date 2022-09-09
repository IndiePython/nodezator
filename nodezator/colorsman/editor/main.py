"""Facility for colors editor class."""

### third-party import
from pygame.math import Vector2


### local imports

from ...config import APP_REFS

from ...pygameconstants import SCREEN_RECT

from ...classes2d.single import Object2D

from ...surfsman.draw import draw_border, draw_depth_finish
from ...surfsman.render import render_rect

from ..colors import WINDOW_BG


## class extensions

from .loopop import LoopOperations
from .widgetop import WidgetOperations

## functions for injection

from .widgetsetup.scale import setup_scales
from .widgetsetup.button import setup_buttons
from .widgetsetup.entry import setup_entries
from .widgetsetup.label import setup_labels


## class for composition
from .panel.main import ColorsPanel


class ColorsEditor(
    LoopOperations,
    WidgetOperations,
):
    """loop holder to pick/edit color(s).

    This class is instantiated only once and its
    edit_colors() method is aliased to be used wherever
    needed in the entire package (look at the last lines
    of this module).
    """

    ### these injected functions create and set up widgets
    ### when instantiating this colors editor

    setup_scales = setup_scales
    setup_buttons = setup_buttons
    setup_entries = setup_entries
    setup_labels = setup_labels

    ### constructor

    def __init__(self):
        """Create and set up support objects."""
        ### build surface and rect representing this
        ### colors editor; the surface will be used as
        ### its background

        ## create and surface in the 'image' attribute,
        ## also referencing it locally for further changes
        image = self.image = render_rect(820, 660, WINDOW_BG)

        ## draw a border on the image
        draw_border(image, thickness=2)

        ## create a surface representing a special area
        ## wherein to locate controls used to edit the
        ## current selected color (the controls will be
        ## created further ahead); then draw it over the
        ## 'image' surface

        # create surface
        controls_area_surf = render_rect(785, 400, WINDOW_BG)

        # add a finish around it to convey depth
        draw_depth_finish(controls_area_surf, outset=False, thickness=5)

        # blit the area over the 'image' surface
        image.blit(controls_area_surf, (20, 215))

        ## create a rect from the 'image' surface
        self.rect = image.get_rect()

        ### instantiate the colors panel, a special panel
        ### widget used to display the colors we are
        ### editing; it also highlights which color is
        ### currently selected for edition

        self.colors_panel = ColorsPanel(
            self,
            no_of_visible_colors=7,
        )

        ### create widget structure to support the
        ### colors editor's operations

        self.setup_scales()
        self.setup_buttons()
        self.setup_entries()
        self.setup_labels()

        ### store topleft coordinates of specific object
        ### groups to use whenever repositioning the
        ### editor when the window is resized

        self.scales_offset = Vector2(self.scales.rect.topleft)

        self.buttons_offset = Vector2(self.buttons.rect.topleft)

        self.labels_offset = Vector2(self.labels.rect.topleft)

        ### center editor on screen and append centering
        ### method used as a window resize setup

        self.center_colors_editor()

        APP_REFS.window_resize_setups.append(self.center_colors_editor)

    def center_colors_editor(self):

        self.rect.center = SCREEN_RECT.center

        (self.colors_panel.reposition_and_define_objects_and_values())

        rect_topleft = self.rect.topleft

        ###

        self.scales.rect.topleft = rect_topleft + self.scales_offset

        for scale in self.scales:
            scale.define_selection_area()
            scale.place_handle()

        ###

        self.buttons.rect.topleft = rect_topleft + self.buttons_offset

        ###

        self.labels.rect.topleft = rect_topleft + self.labels_offset


### instantiate the colors editor, referencing its
### 'edit_colors' method in the module so it can be
### directly imported from this module
edit_colors = ColorsEditor().edit_colors
