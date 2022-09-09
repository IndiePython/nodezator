"""Facility for button widget."""

### local imports

from ..ourstdlibs.behaviour import empty_function

from ..classes2d.single import Object2D

from ..imagesman.cache import IMAGE_SURFS_DB

from ..textman.render import render_text

from ..fontsman.constants import ENC_SANS_BOLD_FONT_HEIGHT, ENC_SANS_BOLD_FONT_PATH

from ..colorsman.colors import BUTTON_FG, BUTTON_BG


### XXX needs lots of refactoring and implementing
### extra interfaces (change surfaces according to state,
### etc.)


### XXX in the future, the constructor will receive
### three surfaces (one for each state: normal, hovered,
### pressed) and a tooltip text; the alternative creators
### should receive data in order to produce such surfaces;
### for instance, the "from_text" constructor would
### receive three tuples, each containing
### foreground color/background color values for each
### state; the "from_image" constructor should receive
### background colors too, and the name of an image
### with transparency, so that you can use the different
### background colors; the "from_image" should maybe
### receive a shape argument helping define the shape
### of the button (for instance, circular, etc.) so that
### the background is blitted accordingly; I could also
### use a lru_cache for storing surfaces resulting from
### commonly used settings;


class Button(Object2D):
    """A button widget."""

    def __init__(
        self,
        surface,
        command=empty_function,
        coordinates_name="topleft",
        coordinates_value=(0, 0),
    ):
        """
        surface (pygame.Surface instance)
            surface representing button.
        command (callable)
            command to execute when clicking the button.
        coordinates_name (string)
            represents attribute name of rect wherein to
            store the position information from the
            coordinates value parameter.
        coordinates_value (sequence with two integers)
            position info, usually in the form of a tuple
            or list. The 2 integers represent coordinates
            in the x and y axes, respectively, for a
            position in 2d space.
        """
        ### store command
        self.command = command

        ### instantiate image and rect attributes

        self.image = surface
        self.rect = self.image.get_rect()

        ### position rect
        setattr(self.rect, coordinates_name, coordinates_value)

    def on_mouse_release(self, event):
        """Execute button command when mouse is released.

        Parameters
        ==========

        event (pygame.event.Event of MOUSEBUTTONUP type)
              although not used in this method, it is
              required in order to comply with protocol
              used; can be used to retrieve the mouse
              position when release, for instance, if the
              information is needed.

              Check pygame.event module documentation on
              pygame website for more info about this event
              object.
        """
        self.command()

    def move(self, x, y):
        """Move button rect by (x, y).

        Parameters
        ==========

        x and y (integers)
            number of pixels on the x and y axis
            respectively used to move the button's rect.
        """
        self.rect.move_ip(x, y)

    ### XXX complete missing info on docstring about
    ### parameters

    @classmethod
    def from_text(
        cls,
        text,
        font_height=ENC_SANS_BOLD_FONT_HEIGHT,
        font_path=ENC_SANS_BOLD_FONT_PATH,
        foreground_color=BUTTON_FG,
        background_color=BUTTON_BG,
        antialiased=True,
        padding=0,
        depth_finish_thickness=0,
        depth_finish_outset=True,
        border_thickness=0,
        border_color=BUTTON_FG,
        max_width=0,
        ommit_direction="right",
        command=empty_function,
        coordinates_name="topleft",
        coordinates_value=(0, 0),
    ):
        """Create surface from text args and pass to class.

        text (string)
            text to be rendered as the button surface.
        font_height (positive integer)
            height of the text surface in pixels.
        font_path (string)
            represents the font used. Check local font.py
            module to see available values. In doubt, use
            'default' for the default font.
        foreground_color
            A tuple or list of r, g, b values which are
            integers ranging from 0 to 255.

        For definitions of the remaining parameters,
        please check the __init__ method.
        """
        surface = render_text(
            text=text,
            font_height=font_height,
            font_path=font_path,
            foreground_color=foreground_color,
            background_color=background_color,
            antialiased=antialiased,
            padding=padding,
            depth_finish_thickness=depth_finish_thickness,
            depth_finish_outset=depth_finish_outset,
            border_thickness=border_thickness,
            border_color=border_color,
            max_width=max_width,
            ommit_direction=ommit_direction,
        )

        return cls(
            surface,
            command=command,
            coordinates_name=coordinates_name,
            coordinates_value=coordinates_value,
        )

    @classmethod
    def from_image(
        cls,
        image_name,
        use_alpha,
        command=empty_function,
        coordinates_name="topleft",
        coordinates_value=(0, 0),
    ):
        """Create surface from image args and pass to class.

        image_name (string)
            name of the image file to be used.
        use_alpha (boolean)
            indicates whether the loaded image must be
            rendered with alpha an alpha channel
            (transparency).

        For definitions of the remaining parameters,
        please check the __init__ method.
        """
        surface = IMAGE_SURFS_DB[image_name][{"use_alpha": use_alpha}]

        return cls(
            surface,
            command=command,
            coordinates_name=coordinates_name,
            coordinates_value=coordinates_value,
        )
