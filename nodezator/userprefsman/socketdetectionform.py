"""Form for socket detection preferences editing."""

### standard library import
from functools import partialmethod


### third-paraty imports

from pygame import Rect

from pygame.locals import (
    QUIT,
    MOUSEBUTTONDOWN,
    MOUSEBUTTONUP,
    KEYUP,
    K_ESCAPE,
    K_RETURN,
    K_KP_ENTER,
)

from pygame.draw import (
    circle as draw_circle,
    line as draw_line,
)


### local imports

from ..pygamesetup import (
    SERVICES_NS,
    SCREEN,
    SCREEN_RECT,
    blit_on_screen,
)

from ..config import APP_REFS

from ..translation import TRANSLATION_HOLDER as t

from ..rectsman.main import RectsManager

from ..ourstdlibs.pyl import save_pyl

from ..ourstdlibs.collections.general import CallList

from ..our3rdlibs.button import Button

from ..our3rdlibs.behaviour import set_status_message

from ..imagesman.cache import IMAGE_SURFS_DB

from ..classes2d.single import Object2D
from ..classes2d.collections import List2D

from ..fontsman.constants import (
    ENC_SANS_BOLD_FONT_HEIGHT,
    ENC_SANS_BOLD_FONT_PATH,
    FIRA_MONO_BOLD_FONT_HEIGHT,
    FIRA_MONO_BOLD_FONT_PATH,
)

from ..textman.render import render_text

from ..textman.label.main import Label

from ..surfsman.cache import UNHIGHLIGHT_SURF_MAP

from ..surfsman.draw import draw_border, draw_depth_finish

from ..surfsman.render import render_rect

from ..graphman.socket.surfs import SOCKET_DIAMETER

from ..loopman.main import LoopHolder

from ..widget.optionmenu.main import OptionMenu

from ..colorsman.colors import (
    CONTRAST_LAYER_COLOR,
    BUTTON_FG,
    BUTTON_BG,
    WINDOW_FG,
    WINDOW_BG,
)

from .main import USER_PREFS, CONFIG_FILEPATH

from .validation import (
    ORDERED_SOCKET_DETECTION_GRAPHICS,
    validate_prefs_data,
)



### constants

TEXT_SETTINGS = {
    "font_height": ENC_SANS_BOLD_FONT_HEIGHT,
    "font_path": ENC_SANS_BOLD_FONT_PATH,
    "padding": 5,
    "foreground_color": WINDOW_FG,
    "background_color": WINDOW_BG,
}

NUMBER_LABEL_SETTINGS = {
    "font_height": FIRA_MONO_BOLD_FONT_HEIGHT,
    "font_path": FIRA_MONO_BOLD_FONT_PATH,
    "padding": 0,
    "foreground_color": WINDOW_FG,
    "background_color": WINDOW_BG,
}

BUTTON_SETTINGS = {
    "font_height": ENC_SANS_BOLD_FONT_HEIGHT,
    "font_path": ENC_SANS_BOLD_FONT_PATH,
    "padding": 5,
    "depth_finish_thickness": 1,
    "foreground_color": BUTTON_FG,
    "background_color": BUTTON_BG,
}

OPEN_HAND = IMAGE_SURFS_DB['hand_open.png'][{'use_alpha': True}]
OPH_RECT = OPEN_HAND.get_rect()

CLOSED_HAND = IMAGE_SURFS_DB['hand_closed.png'][{'use_alpha': True}]
CLH_RECT = CLOSED_HAND.get_rect()


### class definition

class SocketDetectionEditionForm(Object2D, LoopHolder):
    """Form for editing user preferences for socket detection."""

    def __init__(self):
        """Setup form objects."""
        ### create list wherein to store all rects in form
        self.all_rects = []

        ### build widgets
        self.build_form_widgets()

        ### assign rect and surf for background

        self.rect = self.all_rects_man.inflate(20, 20)
        self.image = render_rect(*self.rect.size, WINDOW_BG)

        draw_border(self.image)

        ###
        self.all_rects.append(self.rect)

        ### store a semitransparent object

        self.rect_size_semitransp_obj = Object2D.from_surface(
            surface=render_rect(*self.rect.size, (*CONTRAST_LAYER_COLOR, 130)),
            coordinates_name="center",
            coordinates_value=SCREEN_RECT.center,
        )

        ### attributes to keep track of mouse when editing distances

        self.tracking_rect = None
        self.mouse_x_offset = 0

        ### center edition form and append centering
        ### method as a window resize setup

        self.center_preferences_form()

        APP_REFS.window_resize_setups.append(self.center_preferences_form)

    def center_preferences_form(self):

        self.all_rects_man.center = self.widgets.rect.center = (
            SCREEN_RECT.center
        )

    def build_form_widgets(self):
        """Build widgets to hold settings for edition."""
        ### create list to hold widgets
        widgets = self.widgets = List2D()

        ### instantiate a caption for the form

        caption_label = Object2D.from_surface(
            surface=(
                render_text(
                    text="Socket detection settings",
                    border_thickness=2,
                    border_color=(TEXT_SETTINGS["foreground_color"]),
                    **TEXT_SETTINGS,
                )
            ),
        )

        widgets.append(caption_label)

        ###

        all_rects = self.all_rects
        all_rects.append(widgets.rect)

        ###
        topleft = widgets.rect.move(0, 20).bottomleft

        ###

        socket_detection_graphics_label = Object2D.from_surface(
            surface=(
                render_text(
                    text="Socket detection graphics:",
                    **TEXT_SETTINGS,
                )
            ),
            coordinates_name='topleft',
            coordinates_value=topleft,
        )

        widgets.append(socket_detection_graphics_label)

        midleft = socket_detection_graphics_label.rect.move(5, 0).midright

        socket_graphics_option_menu = self.socket_graphics_option_menu = (

            OptionMenu(
                loop_holder=self,
                options=ORDERED_SOCKET_DETECTION_GRAPHICS,
                value=USER_PREFS["SOCKET_DETECTION_GRAPHICS"],
                draw_on_window_resize=self.draw,
                name="SOCKET_DETECTION_GRAPHICS",
                max_width=0,
                coordinates_name='midleft',
                coordinates_value=midleft,
            )

        )

        widgets.append(socket_graphics_option_menu)

        ###

        topleft = widgets.rect.move(0, 20).bottomleft

        ###

        distances_setting_label = Object2D.from_surface(
            surface=(
                render_text(
                    text="Drag hands below to set specific distances:",
                    **TEXT_SETTINGS,
                )
            ),
            coordinates_name='topleft',
            coordinates_value=topleft,
        )

        widgets.append(distances_setting_label)

        ###

        topleft = widgets.rect.move(0, 5).bottomleft

        drect = self.distances_rect = Rect(*topleft, 250, 80)
        x_padded_drect = self.x_padded_drect = drect.inflate(80, 0)
        x_padded_drect.left = 0
        drect.center = x_padded_drect.center

        all_rects.extend((drect, x_padded_drect))

        socket_rect = self.socket_rect = Rect(0, 0, SOCKET_DIAMETER, SOCKET_DIAMETER)
        socket_rect.center = drect.midright

        OPH_RECT.top = drect.centery
        OPH_RECT.y += 5

        detection_distance = USER_PREFS['DETECTION_DISTANCE']
        OPH_RECT.centerx = socket_rect.move(-detection_distance, 0).centerx

        grasping_distance = USER_PREFS['GRASPING_DISTANCE']
        CLH_RECT.midbottom = socket_rect.move(-grasping_distance, 0).center
        CLH_RECT.y += -5

        all_rects.extend((socket_rect, OPH_RECT, CLH_RECT))

        all_rects_man = self.all_rects_man = RectsManager(all_rects.__iter__)

        ###

        topleft = all_rects_man.move(0, 10).bottomleft

        detection_distance_value_label = self.detection_distance_value_label = (

            Label(
                text="000",
                name='DETECTION_DISTANCE',
                coordinates_name='topleft',
                coordinates_value=topleft,
                **NUMBER_LABEL_SETTINGS,
            )

        )

        detection_distance_value_label.set(f'{detection_distance}')

        widgets.append(detection_distance_value_label)

        midleft = detection_distance_value_label.rect.move(5, 0).midright

        detection_distance_label = Object2D.from_surface(
            surface=(
                render_text(
                    text="pixels for target socket to start reaching for cursor",
                    **TEXT_SETTINGS,
                )
            ),
            coordinates_name='midleft',
            coordinates_value=midleft,
        )

        widgets.append(detection_distance_label)

        ###

        topleft = widgets.rect.move(0, 5).bottomleft

        grasping_distance_value_label = self.grasping_distance_value_label = (

            Label(
                text="000",
                name="grasping_distance",
                coordinates_name='topleft',
                coordinates_value=topleft,
                **NUMBER_LABEL_SETTINGS,
            )

        )

        grasping_distance_value_label.set(f'{grasping_distance}')

        widgets.append(grasping_distance_value_label)

        midleft = grasping_distance_value_label.rect.move(5, 0).midright

        grasping_distance_label = Object2D.from_surface(
            surface=(
                render_text(
                    text="pixels for target socket to grasp the cursor",
                    **TEXT_SETTINGS,
                )
            ),
            coordinates_name='midleft',
            coordinates_value=midleft,
        )

        widgets.append(grasping_distance_label)

        ### create, position and store form related buttons

        ### create form buttons

        ## submit button

        self.finish_button = Button.from_text(
            text="Confirm changes",
            command=CallList(
                [
                    self.finish_form,
                    self.exit_loop,
                ]
            ),
            **BUTTON_SETTINGS,
        )

        draw_depth_finish(self.finish_button.image)

        ## cancel button

        self.cancel_button = Button.from_text(
            text=(t.user_preferences_form.cancel),
            command=self.exit_loop,
            **BUTTON_SETTINGS,
        )

        draw_depth_finish(self.cancel_button.image)

        ## store

        self.finish_button.rect.topright = all_rects_man.move(0, 20).bottomright

        self.cancel_button.rect.topright = (
            self.finish_button.rect.move(-5, 0).topleft
        )

        widgets.extend((self.cancel_button, self.finish_button))

    def edit_socket_detection_settings(self):
        ### update the value of socket detection graphics in the
        ### corresponding option menu

        self.socket_graphics_option_menu.set(
            USER_PREFS['SOCKET_DETECTION_GRAPHICS']
        )

        ### blit the screen-size semitransparent surf in the
        ### canvas to increase constrast
        blit_on_screen(UNHIGHLIGHT_SURF_MAP[SCREEN_RECT.size], (0, 0))

        ###
        self.loop()

        ### blit semitransparent surface over area occupied
        ### by self.rect so the form appears unhighlighted
        self.unhighlight()

    def handle_input(self):
        """Process events from event queue."""

        for event in SERVICES_NS.get_events():

            ### QUIT
            if event.type == QUIT:
                self.quit()

            ### KEYUP

            elif event.type == KEYUP:

                ## exit the preferences dialog by
                ## pressing "Esc"

                if event.key == K_ESCAPE:
                    self.exit_loop()

                ## confirm edition and exit form by
                ## pressing one of the "enter" keys

                elif event.key in (K_RETURN, K_KP_ENTER):

                    self.finish_form()
                    self.exit_loop()

            ### MOUSEBUTTONDOWN

            elif event.type == MOUSEBUTTONDOWN:

                if event.button == 1:

                    if self.rect.collidepoint(event.pos):
                        self.on_mouse_click(event)

            ### MOUSEBUTTONUP

            elif event.type == MOUSEBUTTONUP:

                if event.button == 1:

                    if self.rect.collidepoint(event.pos):
                        self.on_mouse_release(event)

                    ## cancel editing form if mouse left
                    ## button is released out of boundaries
                    else:
                        self.exit_loop()

    def mouse_method_on_collision(self, method_name, event):
        """Invoke inner widget if it collides with mouse.

        Parameters
        ==========

        method_name (string)
            name of method to be called on the colliding
            widget.
        event (event object of MOUSEBUTTON~ type)
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
                self.unhighlight()
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

    on_mouse_click = partialmethod(
        mouse_method_on_collision,
        "on_mouse_click",
    )

    on_mouse_release = partialmethod(
        mouse_method_on_collision,
        "on_mouse_release",
    )

    def finish_form(self):
        """Assign new category indices and exit loop."""

        prefs_copy = USER_PREFS.copy()

        prefs_copy.update({
            'SOCKET_DETECTION_GRAPHICS': self.socket_graphics_option_menu.get(),
            'DETECTION_DISTANCE': int(self.detection_distance_value_label.get()),
            'GRASPING_DISTANCE': int(self.grasping_distance_value_label.get()),
        })

        try:
            validate_prefs_data(prefs_copy)

        except Exception:
            return

        else:

            try:
                save_pyl(prefs_copy, CONFIG_FILEPATH)

            except Exception:
                return

            else:

                USER_PREFS.update(prefs_copy)
                APP_REFS.gm.reference_socket_detection_graphics()

        ### notify user via status message

        message = "Socket detection preferences changed."
        set_status_message(message)

    def update(self):

        mouse_pos = SERVICES_NS.get_mouse_pos()

        if not self.x_padded_drect.collidepoint(mouse_pos):
            self.tracking_rect = None

        elif SERVICES_NS.get_mouse_pressed()[0]:

            tr = self.tracking_rect

            if tr is OPH_RECT:

                new_left = mouse_pos[0] - self.mouse_x_offset
                OPH_RECT.centerx = min(max(new_left, self.distances_rect.left), CLH_RECT.centerx - 20)

                detection_distance = self.socket_rect.centerx - OPH_RECT.centerx
                self.detection_distance_value_label.set(f'{detection_distance}')

            elif tr is CLH_RECT:

                new_centerx = mouse_pos[0] - self.mouse_x_offset
                CLH_RECT.centerx = min(max(new_centerx, OPH_RECT.centerx + 20), self.socket_rect.centerx - 20)

                grasping_distance = self.socket_rect.centerx - CLH_RECT.centerx
                self.grasping_distance_value_label.set(f'{grasping_distance}')

            else:

                if OPH_RECT.collidepoint(mouse_pos):

                    self.mouse_x_offset = mouse_pos[0] - OPH_RECT.centerx
                    self.tracking_rect = OPH_RECT

                elif CLH_RECT.collidepoint(mouse_pos):

                    self.mouse_x_offset = mouse_pos[0] - CLH_RECT.centerx
                    self.tracking_rect = CLH_RECT
        else:
            self.tracking_rect = None

    def draw(self):
        """Draw itself and widgets.

        Extends Object2D.draw.
        """
        ### draw self (background)
        super().draw()

        ### draw widgets
        self.widgets.call_draw()

        ### draw distance guides/selectors
        self.draw_distance_guides_and_selectors()

        ### update screen
        SERVICES_NS.update_screen()

    def draw_distance_guides_and_selectors(self):

        dr = self.distances_rect
        ddr = dr.inflate(0, -60)

        draw_line(SCREEN, 'black', dr.midleft, dr.midright, 2)
        draw_line(SCREEN, 'black', ddr.topleft, ddr.bottomleft, 2)

        socket_center = self.socket_rect.center
        detection_dist = OPH_RECT.move(0, -5).midtop
        grasping_dist = CLH_RECT.move(0, 5).midbottom

        draw_line(SCREEN, 'white', detection_dist, socket_center, 2)
        draw_line(SCREEN, 'red', grasping_dist, socket_center, 2)

        blit_on_screen(OPEN_HAND, OPH_RECT)
        draw_circle(SCREEN, 'black', detection_dist, 5)

        draw_circle(SCREEN, 'green', socket_center, SOCKET_DIAMETER/2)
        draw_circle(SCREEN, 'black', socket_center, SOCKET_DIAMETER/2, 2)

        blit_on_screen(CLOSED_HAND, CLH_RECT)
        draw_circle(SCREEN, 'black', grasping_dist, 5)

    def unhighlight(self):
        """Draw semitransparent surface on self.rect area.

        Done to make form appear unhighlighted.
        """
        blit_on_screen(UNHIGHLIGHT_SURF_MAP[self.rect.size], self.rect)


edit_socket_detection_settings = SocketDetectionEditionForm().edit_socket_detection_settings
