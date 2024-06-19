
### standard library import
from functools import partialmethod

### third-party imports

from pygame.locals import (
    QUIT,
    KEYDOWN,
    KEYUP,
    K_ESCAPE,
    K_w, K_s, K_UP, K_DOWN,
    K_END, K_HOME,
    K_PAGEDOWN, K_PAGEUP,
    MOUSEWHEEL,
    MOUSEBUTTONDOWN,
    MOUSEBUTTONUP,
)


### local imports

from ...config import APP_REFS

from ...pygamesetup import SERVICES_NS

from ...dialog import create_and_show_dialog

from ...classes2d.single import Object2D

from ...loopman.exception import QuitAppException, SwitchLoopException

from ...surfsman.draw import draw_border



class ReportViewerOperations(Object2D):

    def handle_input(self):
        """Process events from event queue."""

        dy = 0

        for event in SERVICES_NS.get_events():

            ### QUIT
            if event.type == QUIT:
                raise QuitAppException

            ### KEYUP

            elif event.type == KEYUP:

                if event.key == K_ESCAPE:
                    self.exit()

            ### KEYDOWN

            elif event.type == KEYDOWN:

                if event.key == K_PAGEUP:
                    dy += self.rect.height - 100

                elif event.key == K_PAGEDOWN:
                    dy += -(self.rect.height - 100)

                elif event.key == K_HOME:
                    dy += self.widgets.rect.height

                elif event.key == K_END:
                    dy += -self.widgets.rect.height

            ### MOUSEBUTTONDOWN

            elif event.type == MOUSEBUTTONDOWN:

                if event.button == 1:

                    if self.rect.collidepoint(event.pos):
                        self.on_mouse_click(event)

            ### MOUSEBUTTONUP

            elif event.type == MOUSEBUTTONUP:

                ### if mouse button is mouse button 1..

                if event.button == 1:

                    ## if it is released within boundaries,
                    ## process event with corresponding method

                    if self.rect.collidepoint(event.pos):
                        self.on_mouse_release(event)

                    ## otherwise cancel editing form

                    else:
                        self.exit()

            ### MOUSEWHEEL

            elif event.type == MOUSEWHEEL:
                dy = event.y * 100

        ### process key states

        key_input, modif_bitmask = (
            SERVICES_NS.get_pressed_keys(), SERVICES_NS.get_pressed_mod_keys()
        )

        if key_input[K_w] or key_input[K_UP]:
            dy += 70

        elif key_input[K_s] or key_input[K_DOWN]:
            dy += -70

        ##

        if dy:
            self.scroll(dy)

    def scroll(self, dy):

        _, top, _, height = self.widgets.rect

        bottom = top + height

        _, scroll_top, _, scroll_height = self.scroll_area

        scroll_bottom = scroll_top + scroll_height

        if height <= scroll_height:
            return

        if dy > 0:

            if (top + dy) > scroll_top:
                dy = scroll_top - top

        else:

            if (bottom + dy) < scroll_bottom:
                dy = scroll_bottom - bottom

        self.widgets.rect.move_ip(0, dy)

    def mouse_method_on_collision(self, method_name, event):
        """Invoke inner widget if it collides with mouse.

        Parameters
        ==========

        method_name (string)
            name of method to be called on the colliding
            widget.
        event (event object of MOUSEBUTTON[...] type)
            it is required in order to comply with
            mouse interaction protocol used; here we
            use it to retrieve the position of the
            mouse when the first button was released.

            Check pygame.event module documentation on
            pygame website for more info about this event
            object.
        """
        ### retrieve position from attribute in event obj
        mouse_pos = event.pos

        ### search for a colliding obj among the widgets

        for obj in self.widgets:

            if obj.rect.collidepoint(mouse_pos):

                colliding_obj = obj
                break

        else:
            return

        ### if you manage to find a colliding obj, execute
        ### the requested method on it, passing along the
        ### received event

        try:
            method = getattr(colliding_obj, method_name)
        except AttributeError:
            pass
        else:
            method(event)

    on_mouse_click = partialmethod(mouse_method_on_collision, "on_mouse_click")

    on_mouse_release = partialmethod(mouse_method_on_collision, "on_mouse_release")

    def jump_to_case_related_stats(self, case_id):
        """Scroll to case related stats for case of given id."""
        for obj in self.case_stats_objs:

            if obj.case_id == case_id:
                break

        else:

            raise RuntimeError(
                "This block should never execute, because we expect the given"
                " 'case_id' to always exist"
            )

        ###
        self.scroll_to_rect(obj.rect)

    def back_to_case_list(self):
        """Scroll back to case list."""
        self.scroll_to_rect(self.case_list_caption.rect)

    def scroll_to_rect(self, rect):

        top = rect.top
        scroll_top = self.scroll_area.top

        if scroll_top != top:
            self.scroll(scroll_top - top)

    def draw(self):
        """Draw itself and widgets.

        Extends Object2D.draw.
        """
        ### reference image locally
        image = self.image

        ### clean image
        image.blit(self.clean_bg, (0, 0))

        ### draw widgets on self

        ## reference rect locally
        rect = self.rect

        ## draw widgets

        for widget in self.widgets:

            if widget.rect.colliderect(rect):
                widget.draw_relative(self)

        ### draw border
        draw_border(image)

        ### draw self
        super().draw()

        ### update screen
        SERVICES_NS.update_screen()

    def view_last_report(self):
        """Show report if there are report data, otherwise notify user."""

        ### if there are report data, show report

        if self.report_data is not None:

            ### set loop holder to None
            self.loop_holder = None

            ### set itself as the current loop holder by raising
            ### the corresponding exception
            raise SwitchLoopException(self)

        ### otherwise, notify user via dialog

        else:

            create_and_show_dialog(
                "Must first perform system tests in order to produce report."
                " Go to \"GUI automation > System testing\" to set and start"
                " a system testing session using one of the presented"
                " options."
            )

    def exit(self):
        """Exit report viewer."""
        ### draw window manager
        ###
        ### if we were displaying the report just after finishing the tests,
        ### then the splash screen will appear just in front of the
        ### report, so we draw the window manager before leaving so that
        ### the report viewer doesn't appear behind the splash screen
        APP_REFS.wm.draw()

        ### exit report viewer by raising exception that causes the loop
        ### holder to be switched (in this case we'll switch either to
        ### the window manager or to the splash screen)
        raise SwitchLoopException(self.loop_holder)
