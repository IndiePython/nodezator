"""Facility for colors editor class."""

### local imports

from pygameconstants import SCREEN_RECT

from classes2d.single import Object2D

from surfsman.draw   import draw_border, draw_depth_finish
from surfsman.render import render_rect

from colorsman.colors import WINDOW_BG


## class extensions

from colorsman.editor.loopop   import LoopOperations
from colorsman.editor.widgetop import WidgetOperations

## functions for injection

from colorsman.editor.widgetsetup.scale  import setup_scales
from colorsman.editor.widgetsetup.button import setup_buttons
from colorsman.editor.widgetsetup.entry  import setup_entries
from colorsman.editor.widgetsetup.label  import setup_labels


## class for composition
from colorsman.editor.panel.main import ColorsPanel


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

    setup_scales  = setup_scales
    setup_buttons = setup_buttons
    setup_entries = setup_entries
    setup_labels  = setup_labels


    ### constructor

    def __init__(self):
        """Create and set up support objects."""
        ### build surface and rect representing this
        ### colors editor; the surface will be used as
        ### its background

        ## create and surface in the 'image' attribute, also
        ## referencing it locally for further changes
        image = self.image = \
            render_rect(820, 660, WINDOW_BG)

        ## draw a border on the image
        draw_border(image, thickness=2)

        ## create a surface representing a special area
        ## wherein to locate controls used to edit the
        ## current selected color (the controls will be
        ## created further ahead); then draw it over the
        ## 'image' surface

        # create surface
        controls_area_surf = \
                render_rect(785, 400, WINDOW_BG)

        # add a finish around it to convey depth
        draw_depth_finish(
            controls_area_surf, outset=False, thickness=5)

        # blit the area over the 'image' surface
        image.blit(controls_area_surf, (20, 215))

        ## create a rect from the 'image' surface and
        ## center it on the screen

        self.rect        = image.get_rect()
        self.rect.center = SCREEN_RECT.center

        ### instantiate the colors panel, a special panel
        ### widget used to display the colors we are
        ### editing; it also highlights which color is
        ### currently selected for edition

        midtop = self.rect.move(0, 45).midtop

        self.colors_panel = \
          ColorsPanel(
            self,
            no_of_visible_colors = 7,
            coordinates_name     = 'midtop',
            coordinates_value    = midtop
          )

        ### create widget structure to support the
        ### colors editor's operations

        self.setup_scales()
        self.setup_buttons()
        self.setup_entries()
        self.setup_labels()


### instantiate the colors editor, referencing its
### 'edit_colors' method in the module so it can be
### directly imported from this module
edit_colors = ColorsEditor().edit_colors
