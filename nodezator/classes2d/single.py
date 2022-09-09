"""Facility w/ custom class for general usage."""

### standard library import
from xml.etree.ElementTree import Element


### third-party import
from pygame.math import Vector2


### local imports

from ..pygameconstants import (
    SCREEN_RECT,
    blit_on_screen,
)


class SingleObjectBase:
    """Basic methods for single objects."""

    def draw(self):
        """Blit itself on screen w/ image and rect attributes.

        Naturally, it should only be used if objects have
        both an image attribute containing a pygame.Surface
        instance and a rect attribute containing a
        pygame.Rect instance.
        """
        blit_on_screen(self.image, self.rect)

    def draw_on_screen(self):
        """Works as self.draw, but check if obj is onscreen.

        Naturally, it should only be used if objects have
        both an image attribute containing a pygame.Surface
        instance and a rect attribute containing a
        pygame.Rect instance.
        """
        if SCREEN_RECT.colliderect(self.rect):
            blit_on_screen(self.image, self.rect)

    def draw_on_surf(self, surf):
        """Work as self.draw, but blit on specified surf.

        surf
            Any pygame.Surface instance. If such instance is
            also the surface returned by
            pygame.display.set_mode then it is recommended
            to use the self.draw or self.draw_on_screen
            method instead.
        """
        surf.blit(self.image, self.rect)

    def draw_relative(self, obj):
        """Draw self.image on given object's image.

        'relative' means we take into account the position
        of this object's rect relative to the rect of the
        given object.
        """
        obj.image.blit(self.image, self.rect.move(-Vector2(obj.rect.topleft)))

    def svg_repr(self):
        """Return svg rect element representing object."""
        rect = self.rect.inflate(-2, -2)

        return Element(
            "rect",
            {
                attr_name: str(getattr(rect, attr_name))
                for attr_name in (
                    "x",
                    "y",
                    "width",
                    "height",
                )
            },
        )


class Object2D(SingleObjectBase):
    def __init__(self, **kwargs):
        """Assign keyword arguments to instance dict."""
        self.__dict__.update(kwargs)

    @classmethod
    def from_surface(
        cls, surface, coordinates_name="topleft", coordinates_value=(0, 0), **kwargs
    ):
        """Store surface and its rect, positioning it.

        Parameters
        ==========

        surface (pygame.Surface)
            surface to store and from where to obtain rect.
        coordinates_name (string)
            string representing attribute name of rect
            wherein to store the position information from
            the 'coordinates_value' parameter.
        coordinates_value (tuple/list of ints)
            position information in the form of a tuple or
            list containing 2 integers representing
            positions in the x and y axes, respectively.
        """
        ### instantiate basic object
        obj = cls(**kwargs)

        ### store surface in 'image' attribute
        obj.image = surface

        ### store and position rect

        obj.rect = surface.get_rect()

        setattr(obj.rect, coordinates_name, coordinates_value)

        return obj
