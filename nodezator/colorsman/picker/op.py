"""Colors picker's class extension w/ extra operations."""

### standard library import
from functools import partialmethod


### third-party imports

from pygame import (
    QUIT,
    KEYUP,
    K_ESCAPE,
    K_RETURN,
    K_KP_ENTER,
    MOUSEBUTTONUP,
    MOUSEMOTION,
)

from pygame.event import get as get_events

from pygame.draw import rect as draw_rect


### local imports

from ...pygameconstants import (
    SCREEN,
    SCREEN_RECT,
    blit_on_screen,
)

from ...ourstdlibs.color.largemaps import (
    HTML_COLOR_MAP,
    PYGAME_COLOR_MAP,
)

from ...ourstdlibs.color.custom import (
    custom_format_color,
    get_custom_sorted_colors,
)

from ...surfsman.icon import render_layered_icon

from ...surfsman.cache import (
    UNHIGHLIGHT_SURF_MAP,
    RECT_SURF_MAP,
    cache_screen_state,
    draw_cached_screen_state,
)

from ...loopman.main import LoopHolder

from ..colors import BLACK, WHITE, WINDOW_BG

from ..color2d import Color2D

from .constants import (
    DEFAULT_LABEL_MESSAGE,
)

### constants

COLOR_INFO_TITLES = (
    "HTML",
    "pygame",
    "Luma",
    "HEX",
    "RGB",
    "HLS",
)

MAX_CHAR_NO = max(len(item) for item in COLOR_INFO_TITLES)

COLOR_INFO_KEYS = (
    "html",
    "pygame",
    "luma",
    "hex",
    "rgb",
    "hls",
)


class Operations(LoopHolder):
    """Extra operations for the colors picker class."""

    def pick_colors(
        self,
        color_value,
        widget_width=36,
        icon_width=32,
        position_method_name=("snap_rects_intermittently_ip"),
        position_method_kwargs={
            "dimension_name": "width",
            "dimension_unit": "rects",
            "max_dimension_value": 15,
        },
    ):
        """Execute the picker loop.

        Presents given colors for the user to pick.
        """
        ### treat the color properly in order to obtain a
        ### tuple of full rgb colors

        ## convert color value to a tuple of rgb colors

        try:
            colors = custom_format_color(color_value, "rgb_tuple", False)

        ## XXX maybe show a dialog with the
        ## error message here? or just print on the
        ## screen? probably also log the error;
        ## ponder;

        ## if a value error is raised, though,
        ## it means  there's something wrong with
        ## the given value, so we return earlier
        except ValueError:
            return None

        ### create/set widgets for color picking

        self.prepare_color_widgets(
            colors,
            widget_width,
            icon_width,
            position_method_name,
            position_method_kwargs,
        )

        ### center color picker
        self.center_color_picker()

        ### turn the 'reset' flag off
        self.cancel = False

        ### update screen copy; we'll use it to clean the
        ### screen whenever we draw
        cache_screen_state()

        ### draw everything on screen, only once
        self.draw_once()

        ### loop the loop holder operations of the color
        ### picker
        self.loop()

        ### blit screen copy on screen, so picker objects
        ### vanish from view
        draw_cached_screen_state()

        ### once the loop is exited, return a tuple of picked
        ### colors according to whether the cancel flag
        ### is on or off

        return (
            ## return an empty list if the cancel flag is on
            ()
            if self.cancel
            ## otherwise return a tuple with each picked color
            else tuple(
                color_widget.color
                for color_widget in self.color_widgets
                if color_widget.chosen
            )
        )

    pick_html_colors = partialmethod(
        pick_colors,
        ## note that before turning the
        ## values into a tuple, we turn
        ## them into a set in order to
        ## eliminate duplicate values,
        ## since there are colors with
        ## different names, but same value
        tuple(set(HTML_COLOR_MAP.values())),
    )

    pick_pygame_colors = partialmethod(
        pick_colors,
        ## note that before turning the
        ## values into a tuple, we turn
        ## them into a set in order to
        ## eliminate duplicate values,
        ## since there are colors with
        ## different names, but same
        ## value
        tuple(set(PYGAME_COLOR_MAP.values())),
        widget_width=24,
        icon_width=20,
        position_method_name=("snap_rects_intermittently_ip"),
        position_method_kwargs={
            "dimension_name": "width",
            "dimension_unit": "rects",
            "max_dimension_value": 28,
        },
    )

    def prepare_color_widgets(
        self,
        colors,
        widget_width,
        icon_width,
        position_method_name,
        position_method_kwargs,
    ):
        """Set/create widgets to hold and display colors."""
        ## iterate over the black and white colors, creating
        ## a heavy check mark of each color

        black_tick, white_tick = (
            render_layered_icon(
                chars=[chr(124)],
                dimension_name="width",
                dimension_value=icon_width,
                colors=[color],
                background_width=widget_width,
                background_height=widget_width,
            )
            for color in (BLACK, WHITE)
        )

        ### we must sort the colors in a pleasing, logical
        ### way as to make it easier for the user to choose
        ### colors

        ## begin by ensuring the given colors are inside a
        ## list, so it can be sorted
        colors = list(colors)

        ## then obtain a new list with the colors already
        ## sorted according to a custom useful recipe
        sorted_colors = get_custom_sorted_colors(colors)

        ### store amount of color widgets needed
        no_of_colors = len(sorted_colors)

        ### now that the colors are nicely sorted, let's
        ### set them in existing color widgets, creating
        ### them if needed

        ## reference existing color objects locally
        existing_color2d_objs = self.existing_color2d_objs

        ## create more color objects if needed

        no_of_needed = no_of_colors - len(existing_color2d_objs)

        if no_of_needed > 0:

            existing_color2d_objs.extend(
                Color2D(widget_width, widget_width, BLACK) for _ in range(no_of_needed)
            )

        ## reference list of color widgets to be used
        ## locally
        color_widgets = self.color_widgets

        ## clear the list and extend it with the number of
        ## color widgets equivalent to the number of colors

        color_widgets.clear()
        color_widgets.extend(existing_color2d_objs[:no_of_colors])

        ## iterate over the color widgets and colors, setting
        ## each color in its respective widget and
        ## performing other setups

        for color_widget, color in zip(color_widgets, sorted_colors):

            ## set the color and size

            color_widget.set_color(color)
            color_widget.set_size((widget_width, widget_width))

            ## set the 'chosen' attribute to False;
            ## it is a flag indicating whether or not
            ## the color it represents is picked
            color_widget.chosen = False

            ## reference either the black or the white
            ## tick surface in the 'tick_surf' attribute
            ## of the widget, whichever contrasts more with
            ## its color

            color_widget.tick_surf = (
                black_tick
                if color_widget.contrasting_color == (0, 0, 0)
                else white_tick
            )

        ### now position all color widgets relative to
        ### each other

        method = getattr(
            color_widgets.rect,
            position_method_name,
        )

        method(**position_method_kwargs)

    def event_handling(self):
        """Handle events from the event queue."""
        ### iterate over the events in the event queue,
        ### processing the relevant ones according to their
        ### settings

        for event in get_events():

            ### quit the application
            if event.type == QUIT:
                self.quit()

            ### if one of the following keys is released,
            ### turn on the the 'cancel' flag and trigger
            ### the exit of the loop

            elif event.type == KEYUP:

                if event.key in (K_ESCAPE, K_RETURN, K_KP_ENTER):

                    self.cancel = True
                    self.exit_loop()

            ### if the mouse left button is release,
            ### execute the corresponding operation
            ### with the event object

            elif event.type == MOUSEBUTTONUP:
                if event.button == 1:
                    self.on_mouse_release(event)

            ### if the mouse moves, execute the
            ### corresponding operation with the event
            ### object

            elif event.type == MOUSEMOTION:
                self.on_mouse_motion(event)

    ### alias the event handling operation as the
    ### "gud operation" named 'handle_input'
    handle_input = event_handling

    def on_mouse_release(self, event):
        """Select/unselect colors or invoke buttons.

        If a color widget is hovered by the mouse when
        its left button is release, the color is
        picked/unpicked, depending on its current state;

        if it is a button which is hovered, that button
        is pressed if it has the appropriate method.

        Method compliant with the mouse action protocol.

        Parameters
        ==========
        event (pygame.event.Event instance)
            event whose event.type is MOUSEBUTTONUP;
            it is used to retrieve the position of the
            mouse when its left button was released,
            stored in its 'pos' attribute.
        """
        ### retrieve the mouse position
        mouse_pos = event.pos

        ### iterate over each color widget, toggling the
        ### 'chosen' flag of the one hovered by the mouse
        ### if there is one

        for color_widget in self.color_widgets:

            ## if color widget collides, toggle the
            ## 'chosen' flag, redraw respective surfaces
            ## and the widget outline and break out of
            ## the "for loop"

            if color_widget.rect.collidepoint(mouse_pos):

                color_widget.chosen = not color_widget.chosen

                color_widget.draw()

                if color_widget.chosen:

                    blit_on_screen(color_widget.tick_surf, color_widget.rect)

                ## draw outline around color widget

                draw_rect(
                    SCREEN,
                    color_widget.contrasting_color,
                    color_widget.rect,
                    2,
                )

                break

        ### if no hovered color widget is found,
        ### look between the buttons for the hovered one,
        ### invoking its mouse release action if it has
        ### one

        else:

            ## if a button collides, execute its mouse
            ## release action if it has one (passing the
            ## event object along) and break out of the
            ## "for loop"

            for button in self.buttons:

                if button.rect.collidepoint(mouse_pos):

                    try:
                        method = button.on_mouse_release
                    except AttributeError:
                        pass
                    else:
                        method(event)

                    break

    def on_mouse_motion(self, event):
        """Set text on labels according to mouse position.

        That is, if mouse hovers a color widget, shows
        info about that color, otherwise reset the labels
        to their default values.

        Method compliant with the mouse action protocol.

        Parameters
        ==========
        event (pygame.event.Event instance)
            event whose event.type is MOUSEMOTION;
            it is used to retrieve the position of the
            mouse when it moved, stored in its 'pos'
            attribute.
        """
        ### retrieve the mouse position
        mouse_pos = event.pos

        ### iterate over the color widgets, looking for
        ### one hovered by the mouse

        for color_widget in self.color_widgets:

            ## if a color widget hovered by the mouse is
            ## found, set the text of the labels to display
            ## information about its color, highlight it
            ## by drawing an outline around and break out
            ## of the "for loop"

            if color_widget.rect.collidepoint(mouse_pos):

                ## set text of labels

                # retrieve color info
                info = self.color_info[color_widget.color]

                # iterate over labels and respective
                # titles/keys, setting the text of the
                # label

                for label, title, key in zip(
                    self.labels,
                    COLOR_INFO_TITLES,
                    COLOR_INFO_KEYS,
                ):
                    label.set(f'{title.ljust(MAX_CHAR_NO, " ")}:' + f" {info[key]}")

                ##
                self.draw_once()

                ## draw outline around color widget

                draw_rect(
                    SCREEN,
                    color_widget.contrasting_color,
                    color_widget.rect,
                    2,
                )

                ## then return
                return

        ### if reach this point in the method, then a
        ### hovered widget wasn't found, so set the
        ### text of the labels to their default values

        ## set all labels to '' (no text)
        for label in self.labels:
            label.set("")

        ## set the last label to display the default
        ## message
        self.labels[-1].set(DEFAULT_LABEL_MESSAGE)

        ###
        self.draw_once()

    def draw_once(self):
        """Draw picker and objects it comprises."""
        ### clean screen
        draw_cached_screen_state()

        ### draw a semitransparent background behind
        ### an inflated union of the areas occupied
        ### by the caption, color widgets and buttons

        inflated_union = self.caption.rect.unionall(
            [
                self.color_widgets.rect,
                self.buttons.rect,
            ]
        ).inflate(16, 16)

        blit_on_screen(
            RECT_SURF_MAP[(*inflated_union.size, (30, 30, 30, 200))],
            inflated_union,
        )

        ### draw the caption
        self.caption.draw()

        ### draw each widget, also drawing its tick surface
        ### at the same spot if its color is chosen

        for color_widget in self.color_widgets:

            ## draw widget
            color_widget.draw()

            ## if widget's 'chosen' flag is on,
            ## draw its tick surface at the same spot
            ## as its rect

            if color_widget.chosen:

                blit_on_screen(color_widget.tick_surf, color_widget.rect)

        ### draw the buttons
        self.buttons.draw()

        ### draw a semitransparent background behind the
        ### labels and the labels themselves

        blit_on_screen(
            RECT_SURF_MAP[(*self.labels.rect.size, WINDOW_BG)], self.labels.rect
        )

        self.labels.draw()
