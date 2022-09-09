"""Facility w/ class extension w/ splash screen operations."""

### standard library import
from functools import partialmethod


### third-party imports

from pygame import (
    QUIT,
    KEYUP,
    K_ESCAPE,
    K_RETURN,
    K_KP_ENTER,
    KEYDOWN,
    KMOD_CTRL,
    K_w,
    MOUSEBUTTONDOWN,
    MOUSEBUTTONUP,
    MOUSEMOTION,
)

from pygame.event import get as get_events

from pygame.display import update

from pygame.draw import rect as draw_rect


### local imports

from ..pygameconstants import SCREEN

from ..classes2d.single import Object2D

from ..loopman.exception import (
    SwitchLoopException,
    QuitAppException,
)

from ..colorsman.colors import SPLASH_FONT

from ..recentfile import get_recent_files

from .factoryfuncs import get_recent_file_objs

from .animsetup import keep_animation_playing, keep_animation_paused


class SplashScreenOperations(Object2D):
    """SplashScreen extension w/ lifetime operations.

    That is, operations performed during the lifetime of
    the splash screen, rather than upon its instantiation.
    """

    def get_focus(self):
        """Perform setups and give focus to splash screen."""
        ### get current list of recent files
        recent_files = get_recent_files()

        ### if such list changed since last time we created
        ### objects representing buttons to load recent
        ### files, we recreate such objects and also, as a
        ### result, we reposition all objects in the splash
        ### screen to account for the change, redefining
        ### its boundaries

        if self.recent_files != recent_files:

            ## store the current list of recent files
            self.recent_files = recent_files

            ## recreate the recent file objects
            self.recent_file_objs = get_recent_file_objs(self.recent_files)

            ### reposition all objects in the splash screen
            ### and redefine its boundaries
            self.position_and_define_boundaries()

        ### finally raise an special exception, passing
        ### along a reference to the splash screen, so it
        ### obtains control of the application
        raise SwitchLoopException(self)

    def handle_input(self):
        """Iterate over events reacting to them."""
        ### iterate over events from the event queue

        for event in get_events():

            ### if the user attempts to close the window,
            ### raise a custom exception to trigger the
            ### proper behaviour to quit the application
            if event.type == QUIT:
                raise QuitAppException

            ### if one of the following keys is released,
            ### raise the SwitchLoopException without
            ### arguments, which causes the window manager
            ### to obtain control of the screen, that is,
            ### the splash screen looses focus and
            ### disappears

            elif event.type == KEYUP:

                if event.key in (K_ESCAPE, K_RETURN, K_KP_ENTER):
                    raise SwitchLoopException

            ### pressing "Ctrl" + "W" also triggers
            ### behaviours to quit application, just
            ### like in the QUIT event above

            elif event.type == KEYDOWN:

                if event.key == K_w and event.mod & KMOD_CTRL:
                    raise QuitAppException

            ### for each type of mouse event (motion,
            ### button pressing or button release),
            ### execute the corresponding event, passing
            ### along the event object

            elif event.type == MOUSEMOTION:
                self.on_mouse_motion(event)

            elif event.type == MOUSEBUTTONDOWN:
                self.on_mouse_click(event)

            elif event.type == MOUSEBUTTONUP:
                self.on_mouse_release(event)

    def on_mouse_action(self, method_name, event):
        """Act according to method name and mouse event."""
        ### retrieve the mouse position from the event
        mouse_pos = event.pos

        ### if the event, regardless of type, occurred
        ### outside the splash screen boundaries, raise
        ### a SwitchLoopException without arguments,
        ### which causes the window manager to obtain
        ### control of the screen, that is, the splash
        ### screen looses focus and disappears
        if not self.rect.collidepoint(mouse_pos):
            raise SwitchLoopException

        ### otherwise, iterate over the buttons, checking
        ### whether any of them collides with the mouse
        ### and has a method with the same name as the one
        ### received, in which case it is executed;
        ###
        ### regardless of whether the colliding button has
        ### the mentioned method or not, we then break out
        ### of the "for loop"

        else:

            ## iterate over buttons

            for button in self.buttons:

                ## if a button collides check existence of
                ## method with given name and execute it
                ## if it is the case, then break out of
                ## the "for loop" after such check,
                ## regardless of what happened

                if button.rect.collidepoint(mouse_pos):

                    try:
                        method = getattr(button, method_name)
                    except AttributeError:
                        pass
                    else:
                        method(event)

                    break

    on_mouse_click = partialmethod(on_mouse_action, "on_mouse_click")

    on_mouse_release = partialmethod(on_mouse_action, "on_mouse_release")

    def on_mouse_motion(self, event):
        """React to mouse motion event."""
        ### retrieve mouse position from event object
        mouse_pos = event.pos

        ### iterate over the buttons, checking whether
        ### any among them is hovered by the mouse
        ### (that is, the mouse collides with the button);
        ###
        ### if a hovered one is found, store a reference
        ### to its rect in the 'hovered_rect' attribute,
        ### breaking out of the "for loop" immediately;
        ###
        ### if it has an href attribute (it is a link),
        ### set it on the url label;

        for button in self.buttons:

            if button.rect.collidepoint(mouse_pos):

                self.hovered_rect = button.rect

                url_label = self.url_label

                if hasattr(button, "href"):

                    url_label = self.url_label
                    url_label.set(f"Go to {button.href}")

                    url_label.rect.bottomleft = self.rect.move(1, -1).bottomleft

                else:
                    url_label.set("")

                break

        ### if we don't break out of the "for loop" above,
        ### that is, if we don't find a hovered button,
        ### we assign None to the 'hovered_rect' attribute
        ### and set the url label to an empty string

        else:

            self.hovered_rect = None
            self.url_label.set("")

    def dont_update_animation(self):
        """Keep animation paused."""
        if keep_animation_paused():
            return

        self.update = self.update_animation

    def update_animation(self):
        """Keep animation playing."""
        for update_anim in self.anim_update_operations:
            update_anim()

        if keep_animation_playing():
            return

        self.update = self.dont_update_animation

    def draw(self):
        """Draw splash screen and its components."""
        ### draw the splash screen surface in the screen
        super().draw()

        ### draw all objects in the screen
        self.all_objs.draw()

        ### if there is a hovered rect, draw it
        ### in the screen

        if self.hovered_rect:

            draw_rect(SCREEN, SPLASH_FONT, self.hovered_rect, 1)

        ### if there is text set on the url label, draw it
        ### in the screen

        if self.url_label.get():
            self.url_label.draw()

        ### draw the shadows of the splash screen

        self.lower_shadow.draw()
        self.right_shadow.draw()

        ### finally update the screen
        update()  # pygame.display.update()
