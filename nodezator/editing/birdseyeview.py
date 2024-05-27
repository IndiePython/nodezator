"""Facility for assisting in handling bird's eye view."""

### standard library import
from operator import mul


### third-party imports

from pygame.math import Vector2

from pygame.draw import line as draw_line


### local imports

from ..config import APP_REFS

from ..pygamesetup import SCREEN_RECT

from ..dialog import create_and_show_dialog

from ..loopman.exception import SwitchLoopException

from ..rectsman.utils import get_relative_point

from ..fontsman.constants import (
    ENC_SANS_BOLD_FONT_HEIGHT,
    ENC_SANS_BOLD_FONT_PATH,
)

from ..textman.render import render_text

from ..classes2d.single import Object2D

from ..surfsman.cache import RECT_SURF_MAP

from ..surfsman.icon import render_layered_icon

from ..surfsman.render import combine_surfaces

from ..iconfactory import IMAGE_ICON, TEXT_BLOCK_ICON

from ..colorsman.colors import WHITE, BLACK, WINDOW_FG



### constants

VIEW_ALPHA = 230 # 0 for fully transparent, 255 for fully opaque

VIEW_BG = (0, 0, 0, VIEW_ALPHA)

LABEL_SETTINGS = {
    'font_height': ENC_SANS_BOLD_FONT_HEIGHT,
    'font_path': ENC_SANS_BOLD_FONT_PATH,
    'padding': 5,
    'foreground_color': WINDOW_FG,
}

_EYE_ICON = render_layered_icon(
    chars=[chr(ordinal) for ordinal in (87, 88, 89)],
    dimension_name='height',
    dimension_value=24,
    colors=[BLACK, WHITE, (115, 40, 30)],
    background_height=27,
)

_INFO_ICON = (
    render_layered_icon(
        chars=[chr(ordinal) for ordinal in (167, 63, 64, 168)],
        dimension_name='height',
        dimension_value=24,
        colors=[
            WHITE,
            BLACK,
            WHITE,
            BLACK,
        ],
        background_height=27,
    )
)

IMAGE_RECT = IMAGE_ICON.get_rect()

TEXT_BLOCK_OFFSET = TEXT_BLOCK_ICON.get_rect().center

PANEL_OFFSET = (4, -4) # arbitrary value obtained from naked eye observation


### main class

class BirdsEyeViewHandling:

    def __init__(self):

        ## create/reset flag indicating whether we must update objects
        ## of the bird's eye view state;
        ##
        ## must be set to true whenever objects or connections are created,
        ## resized, moved or removed
        ##
        ## since we are either creating the flag now or starting a new
        ## session (either with a new empty file or new loaded one),
        ## we indicate that we must indeed update such objects
        self.must_update_birdseye_view_objects = True

        ### no need to initialize instance past this point if it was already
        ### initialized
        ###
        ### (we leave method earlier by returning)
        if hasattr(self, 'birdseye_base_initialized'):
            return

        ### create and store objects/values to assist in the
        ### bird's eye view handling

        ## rect wherein to fit the graph when scaling it down to fit
        ## the screen
        self.birdseye_fit_area = SCREEN_RECT.inflate(-100, -100)

        ## create placeholder attribute to hold union rect representing
        ## full-sized graph
        self.birdseye_union_rect = None

        ## last mouse position used in birdseye view
        self.birdseye_view_last_mouse_pos = (0, 0)

        ## temp collections for storing data when creating the graph
        ## representation for the bird's eye view state

        self.birdseye_id_to_pos_map = {}
        self.birdseye_blit_pairs = []

        ### create birdseye_graph object
        self.birdseye_graph = Object2D()

        ### create labels

        _caption_text_surf = (
            render_text("Bird's Eye View", **LABEL_SETTINGS)
        )

        self.birdseye_caption_label = (
            Object2D.from_surface(
                combine_surfaces(
                    [_EYE_ICON, _caption_text_surf],
                    retrieve_pos_from='midright',
                    assign_pos_to='midleft',
                    padding=5,
                    background_color=VIEW_BG,
                )
            )
        )

        _instruction_text_surf = render_text(
            "Hover with mouse pressed to move graph",
            **LABEL_SETTINGS,
        )

        self.birdseye_instruction_label = (
            Object2D.from_surface(
                combine_surfaces(
                    [_INFO_ICON, _instruction_text_surf],
                    retrieve_pos_from='midright',
                    assign_pos_to='midleft',
                    padding=5,
                    background_color=VIEW_BG,
                )
            )
        )

        ### append window resize setup method
        APP_REFS.window_resize_setups.append(self.birdseye_view_resize_setup)

        ### create attribute indicating the instance was already
        ### initialized
        self.birdseye_base_initialized = True


    def birdseye_view_resize_setup(self):
        """Only perform setups if bird's eye view is active.

        Otherwise, we don't need to do it, cause the checks/setups are done
        automatically upon entering the bird's eye view.
        """

        if APP_REFS.wm.state_name == 'birdseye_view':
            self.perform_birdseye_view_checks_and_setups()

    def prepare_and_present_birdseye_view(self):

        ### if there are no nodes or text blocks, we cannot enter the
        ### the bird's eye view mode, since there's no graph to represent;
        ###
        ### so instead we just notify the user via dialog and exit the
        ### method earlier by returning

        gm = APP_REFS.gm

        if (
            (not gm.nodes)
            and (not gm.text_blocks)
        ):

            create_and_show_dialog(
                (
                    "The graph is empty, so we cannot enter"
                    " bird's eye view mode."
                ),
                level_name='info',
            )

            return

        ### otherwise we perform the setups needed to show the bird's
        ### eye view and activate the state

        self.perform_birdseye_view_checks_and_setups()
        APP_REFS.wm.set_state('birdseye_view')

        ### then we raise a switch loop exception
        ###
        ### a simple ContinueLoopException wouldn't be enough because
        ### this method may be called from the menubar (in which case
        ### we need to set the window manager as the loop manager, which
        ### can be done by raising this method without arguments)
        raise SwitchLoopException

    def perform_birdseye_view_checks_and_setups(self):
        """Perform checks and setups as needed.

        In order to reset values, perform specific operations and also
        in order to change the graphical elements when stuff changes.

        For instance: when the whole graph changes, when the graph itself
        was moved or when the screen was resized.
        """

        ### update "birdseye fit area" as needed

        if self.birdseye_fit_area != SCREEN_RECT.inflate(-100, -100):

            self.birdseye_fit_area.update(SCREEN_RECT.inflate(-100, -100))
            self.must_update_birdseye_view_objects = True

        ### update objects of bird's eye view state as needed

        if self.must_update_birdseye_view_objects:

            self.redraw_birdseye_graph_surf()
            self.must_update_birdseye_view_objects = False

        else:

            ## this is also performed within the call to the
            ## redraw_birdseye_graph_surf method in the if block above,
            ## but if that block isn't executed, we must do it here
            ##
            ## this is needed because although the union rect didn't
            ## change dimensions, it may have been moved from its
            ## original place since the last time we visited it
            self.birdseye_union_rect = APP_REFS.gm.rectsman.copy()

        ### reset the attribute used to track the mouse position
        self.birdseye_view_last_mouse_pos = (0, 0)

        ### draw the graphical elements;
        ###
        ### the method is prefixed "_once" because it is only called
        ### once whenever needed, not in every loop
        APP_REFS.wm.birdseye_view_draw_once()

    def redraw_birdseye_graph_surf(self):
        """(Re)create a representation of the whole graph that fits the screen.

        That is, that fits the bird's eye fit area, which is slightly smaller
        than the screen in order to provide some margin.

        Other objects created along the way are also stored for their
        usefulness.
        """
        ### reference the graph manager
        gm = APP_REFS.gm

        ### grab a reference to a rects manager that references rects
        ### from all objects in the graph
        objs_rectsman = gm.rectsman

        ### obtain a copy of the rectsman, which represents a union rect
        ### of all the rects managed by it
        ###
        ### it will also be stored as an attribute since it will be
        ### useful in other operations outside this method
        union_rect = self.birdseye_union_rect = objs_rectsman.copy()

        ### store the topleft of the objects
        original_topleft = union_rect.topleft

        ### create rect from union that fits the fit area

        birdseye_graph_rect = union_rect.fit(self.birdseye_fit_area)

        ### define the difference in proportion and perform extra setups
        ### and definitions depending on whether the area of the fitted
        ### rect is smaller than the whole graph or not
        ###
        ### defining the difference in proportion (proportion_diff) is
        ### important cause it will tell us how much we need to shrink
        ### various distances between objects and the center of the screen
        ### in order to properly position them in the graph representation

        if mul(*birdseye_graph_rect.size) < mul(*union_rect.size):

            target_distance, actual_distance = (
                Vector2(rect.center).distance_to(rect.bottomright)
                for rect in (birdseye_graph_rect, union_rect)
            )

            proportion_diff = target_distance / actual_distance

        else:

            birdseye_graph_rect = union_rect.copy()
            birdseye_graph_rect.center = SCREEN_RECT.center
            proportion_diff = 1.0

        ### create the surf on which we'll draw the graph representation

        graph_surf = self.birdseye_graph.image = (
            RECT_SURF_MAP[(*birdseye_graph_rect.size, VIEW_BG)].copy()
        )

        ### position labels according to the rect of such representation

        self.birdseye_caption_label.rect.bottomleft = birdseye_graph_rect.topleft

        self.birdseye_instruction_label.rect.topright = (
            birdseye_graph_rect.bottomright
        )

        ### store the rect's representation for later use
        self.birdseye_graph.rect = birdseye_graph_rect 

        ### now draw all the elements of the graph as icons in the graph
        ### representation;
        ###
        ### such icons must be properly distributed according to their
        ### relative position to each other in the whole graph, so, as the
        ### name implies, the graph representation accurately represents
        ### the positions of the objects in the whole graph

        ## obtain an offset for the origin of the representation's rect
        offset = -Vector2(birdseye_graph_rect.topleft)

        ## reference the center of the screen locally and also assign it
        ## to the center of whole graph so the whole graph is centered
        ## on the screen center as well
        objs_rectsman.center = center = Vector2(SCREEN_RECT.center)

        ## reference the blit operation of the representation's surf
        ## locally for quicker and easier access
        blit_on_graph_surf = graph_surf.blit

        ## reference support objects and relevant method

        blit_pairs = self.birdseye_blit_pairs
        store = blit_pairs.append

        id_to_pos_map = self.birdseye_id_to_pos_map

        ## iterate over existing nodes, calculating the new positions
        ## where their icons must be drawn and storing references to
        ## their icons and such new positions so they can be drawn later
        ## in this method
        ##
        ## the reason they'll be drawn later is that we need to
        ## draw the connections between them before drawing them
        ##
        ## the reason they'll be iterated now despite only being drawn
        ## later is that we need the calculate the new positions so
        ## we can drawn the connections between such positions

        for node in gm.nodes:

            point = (
                center.lerp(node.rectsman.center, proportion_diff)
            ) + offset

            id_to_pos_map[node.id] = point

            icon = node.tiny_icon
            icon_offset = icon.get_rect().center

            if hasattr(node, 'preview_panel'):

                topleft = point + PANEL_OFFSET
                store((IMAGE_ICON, topleft))

            store((icon, point - icon_offset))

        ## iterate over the output sockets that have children,
        ## drawing the connections between them and their children
        ## using the new positions we just calculated

        for parent in gm.parents:

            a = id_to_pos_map[parent.node.id]

            segment_color = parent.line_color

            for child in parent.children:

                b = id_to_pos_map[child.node.id]
                draw_line(graph_surf, segment_color, a, b, 2)

        ## clear support object since we won't need its values
        ## anymore
        id_to_pos_map.clear()

        ## we can now draw the nodes

        for surf, topleft in blit_pairs:
            blit_on_graph_surf(surf, topleft)

        ## clear support object since we won't need its values
        ## anymore
        blit_pairs.clear()

        ## now we calculate the new positions for the text blocks
        ## and draw their icons on that positions

        for block in gm.text_blocks:

            point = (
                center.lerp(block.rect.center, proportion_diff)
            ) + offset

            blit_on_graph_surf(TEXT_BLOCK_ICON, point - TEXT_BLOCK_OFFSET)


        ### restore the position of the whole graph
        objs_rectsman.topleft = original_topleft

        ### also assign that same position to the union rect of the
        ### whole graph (remember we also have this object stored
        ### as an attribute, since it is useful for other operations)
        union_rect.topleft = original_topleft

    def scroll_from_birdseye_view(self, mouse_pos):
        """Scroll whole graph so point of interest in centered on screen.

        This point of interest is the spot in the whole graph that represents
        the spot in the graph representation that the given mouse position
        is touching.
        """
        ### keep track of mouse position used so we don't need to do this
        ### again if the same mouse pos is given
        self.birdseye_view_last_mouse_pos = mouse_pos

        ### calculate the respective point in the whole graph

        relative_point = (
            get_relative_point(
                self.birdseye_graph.rect,
                mouse_pos,
                self.birdseye_union_rect
            )
        )

        ### round coordinates to prevent innacuracies from
        ### floating point numbers
        relative_point = tuple(map(round, relative_point))

        ### define amount to scroll so that the respective point in the whole
        ### graph appears centered on the screen
        dx, dy = Vector2(SCREEN_RECT.center) - relative_point

        ### scroll the graph and our union rect copy by the calculated amount

        self.scroll(dx, dy)
        self.birdseye_union_rect.move_ip(dx, dy)
