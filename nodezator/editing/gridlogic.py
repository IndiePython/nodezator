"""Logic for grid creation and management for editor."""

### standard library imports

from itertools import chain
from functools import partialmethod


### third-party imports

from pygame import Rect

from pygame.math import Vector2

from pygame.display import get_surface


### local imports

from ..config import APP_REFS

from ..pygameconstants import SCREEN, SCREEN_RECT

from ..dialog import create_and_show_dialog

from ..ourstdlibs.collections.general import CallList

from ..ourstdlibs.behaviour import (
    empty_function,
    get_attribute_rotator,
)

from ..our3rdlibs.grid.oop import ScrollableGrid

from ..rectsman.main import RectsManager

from ..colorsman.colors import (
    SMALL_GRID_COLOR,
    LARGE_GRID_COLOR,
)


class GridHandling:
    """Defines grids and manages underlying logic."""

    def __init__(self):
        """Set grid behaviour and related objects."""

        ### define grid-related behaviours

        ## create a grid drawing behaviour so it can be
        ## assigned to the grid_routine attribute
        ## whenever we want to draw the grid

        self.draw_grid = CallList()

        ## define and store a simple toggle for grid drawing
        ## behaviours

        # behaviours
        behaviours = (empty_function, self.draw_grid)

        # toggle

        self.toggle_grid = get_attribute_rotator(
            self,
            "grid_drawing_behaviour",
            behaviours,
        )

        ### set a control to keep track of scrolling amount
        self.scrolling_amount = Vector2()

        ### generate grid objects and also store the
        ### grid generation method as a window resize
        ### setup

        self.generate_grids()

        APP_REFS.window_resize_setups.append(self.generate_grids)

    def generate_grids(self):
        ### generate and store grids

        ## unit grid

        unit_rect = Rect(0, 0, 80, 80)

        self.unit_grid = ScrollableGrid(
            screen=SCREEN,
            line_width=1,
            color=SMALL_GRID_COLOR,
            unit_rect=unit_rect,
            area_rect=SCREEN_RECT,
        )

        ## screen grid

        self.screen_borders = ScrollableGrid(
            screen=SCREEN,
            line_width=5,
            color=LARGE_GRID_COLOR,
            unit_rect=SCREEN_RECT,
            area_rect=SCREEN_RECT,
        )

        ###

        self.draw_grid.clear()

        self.draw_grid.extend(
            (
                self.unit_grid.draw,
                self.screen_borders.draw,
            )
        )

        ###

        dx, dy = self.scrolling_amount

        self.unit_grid.scroll(dx, dy)
        self.screen_borders.scroll(dx, dy)

    def scroll_grids(self, dx, dy):
        """Scroll grids by supplied amounts.

        dx, dy
            Integers representing amount of pixels to scroll
            in the x and y axes, respectively.
        """
        ### increment scrolling amount by the deltas
        self.scrolling_amount += (dx, dy)

        ### scroll each grid

        self.unit_grid.scroll(dx, dy)
        self.screen_borders.scroll(dx, dy)

    def scroll_to_origin(self):
        """Scroll back to (0, 0) scrolling amount."""
        dx, dy = -self.scrolling_amount
        self.scroll(dx, dy)

    def jump_to_corner(self, corner_name):
        """Scroll objects to reach corner of area of object.

        The area of objects is the invisible area occupied
        by all the objects.

        By corner we mean one of the rect coordinates
        like 'topleft', 'center', 'midright', etc.
        """
        ### create a rectsman with rects from all objects

        rectsman = RectsManager(
            ## create a list of rects from live objects
            ##
            ## note that even for nodes, which are complex
            ## objects with more than one rect we use 'rect'
            ## instead of 'rectsman';
            ##
            ## this is so because we don't need to control
            ## the position of the objects with the rectsman:
            ## we are creating it only for the purpose of
            ## reading the position of one of its corners;
            [obj.rect for obj in chain(APP_REFS.gm.nodes, APP_REFS.gm.text_blocks)]
            ## now grab the __iter__ method of the created
            ## list
            .__iter__
        )

        ### try retrieving the requested corner of the
        ### objects as if they were a single rect

        try:
            objs_corner = getattr(rectsman, corner_name)

        ### if trying to retrieve the corner from the
        ### rects manager raises a RuntimeError, it means
        ### there's no objects in the graph, much less a
        ### corner from which to retrieve a position, so
        ### we notify the user and cancel the operation
        ### by returning

        except RuntimeError:

            create_and_show_dialog(
                "there must be at least one object in the"
                " file in order to jump to corner"
            )

            return

        ### finally align the objects' corner with the
        ### center of the screen, by scrolling the
        ### difference between the positions

        self.scroll(*(SCREEN_RECT.center - Vector2(objs_corner)))

    def scroll(self, dx, dy):
        """Scroll grid and objects."""
        ### scroll grids
        self.scroll_grids(dx, dy)

        ### scroll objects

        ## origin rect
        APP_REFS.gm.origin_rect.move_ip(dx, dy)

        ## nodes

        for node in APP_REFS.gm.nodes:
            node.rectsman.move_ip(dx, dy)

        ## text blocks

        for block in APP_REFS.gm.text_blocks:
            block.rect.move_ip(dx, dy)

    scroll_up = partialmethod(scroll, 0, 25)
    scroll_down = partialmethod(scroll, 0, -25)
    scroll_left = partialmethod(scroll, 25, 0)
    scroll_right = partialmethod(scroll, -25, 0)
