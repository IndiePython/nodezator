"""Pygame debug facility."""

### third-party imports

from pygame import (
    QUIT,
    KEYUP,
    K_ESCAPE,
    K_RETURN,
    K_KP_ENTER,
    Surface,
)

from pygame.display import update

from pygame.event import get as get_events

from pygame.draw import rect as draw_rect


### local imports

from ..pygameconstants import (
    FPS,
    SCREEN,
    SCREEN_RECT,
    maintain_fps,
    blit_on_screen,
)

from ..classes2d.single import Object2D

from ..textman.render import render_text

from ..colorsman.colors import WHITE, BLACK, GREY


### function to display surface

## text obj with exit information

EXIT_TEXT_OBJ = Object2D.from_surface(
    render_text(
        "press <ESCAPE> to leave surface view",
        font_height=17,
        foreground_color=WHITE,
        background_color=BLACK,
    )
)

## function definition


def show_surface(surf, background_color=GREY, should_draw_rect=False):
    """Display a surface in center of screen.

    After the user exits, the surface is returned.

    surf (pygame.Surface instance)
        surface to be blitted in the center of the screen.
    background_color (list or tuple of integers or
                      a pygame.Color instance)
        contains r, g, b values which are integers ranging
        from 0 to 255. Used to fill the background surface
        created.
    should_draw_rect (bool)
        whether to outline surface or not.
    """
    ### store a rect from the surface and center it on screen

    rect = surf.get_rect()
    rect.center = SCREEN_RECT.center

    ### create and fill a background surface

    background = Surface(SCREEN_RECT.size).convert()
    background.fill(background_color)

    ### set up a running state (flag) and start the loop

    running = True

    while running:

        ## keep a constant framerate
        maintain_fps(FPS)

        ## do not keep track of window resizing here
        ## with our3rdlibs.behaviour.watch_window_size(),
        ## as you'd normally do (unless you are really
        ## going to need), since it adds uneeded
        ## complexity to the small inspections this
        ## function is usually meant to perform;

        ## handle events

        for event in get_events():

            if event.type == QUIT:
                running = False

            elif event.type == KEYUP:

                if event.key in (K_ESCAPE, K_RETURN, K_KP_ENTER):
                    running = False

        ## blit in this order: background, text, surface,
        ## then the outline

        blit_on_screen(background, (0, 0))
        EXIT_TEXT_OBJ.draw()
        blit_on_screen(surf, rect)

        if should_draw_rect:
            draw_rect(SCREEN, BLACK, rect, 1)

        ## update screen
        update()

    return surf
