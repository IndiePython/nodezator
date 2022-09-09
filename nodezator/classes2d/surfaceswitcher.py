### standard library import
from functools import partialmethod


### local imports

from .single import SingleObjectBase

from ..ourstdlibs.collections.general import FactoryDict


###


def get_surface_switcher_class(states_frozenset):

    return type(
        "SurfaceSwitcher",
        (SingleObjectBase,),
        {
            "__init__": custom_init,
            "switch_to_surface": switch_to_surface,
            "__repr__": custom_repr,
            **{
                f"switch_to_{surface_name}_surface": (
                    partialmethod(
                        switch_to_surface,
                        surface_name,
                    )
                )
                for surface_name in states_frozenset
            },
        },
    )


SURF_SWITCHER_CLASS_MAP = FactoryDict(get_surface_switcher_class)

###


def custom_init(
    self,
    surf_map,
    coordinates_name="topleft",
    coordinates_value=(0, 0),
    **kwargs,
):

    self.__dict__.update(kwargs)
    self.__dict__.update(surf_map)

    self.image = surf_map[sorted(surf_map)[0]]
    self.rect = self.image.get_rect()

    setattr(self.rect, coordinates_name, coordinates_value)


def custom_repr(self):
    return "SurfaceSwitcher()"


def switch_to_surface(self, surface_name):
    self.image = self.__dict__[surface_name]
