"""Facility for text surfaces storage and sharing.

This module provides 02 objects of interest for when
we want to reuse text surfaces. The other objects are
support objects not meant to be imported/touched in
any way.

The ones you want to import are:

1) The TextSurfacesDatabase instance called TEXT_SURFS_DB,
   which is created and stored at the end of the module;

     This one is a dict which, given a dict containing
     text rendering settings (the dict is internally
     converted to a hashable representation),
     automatically creates another dict containing
     a surface map and a width map.
   
     Both the surface map and width map are dicts which
     associate text to surfaces and the width of such
     surfaces, respectively. They are stored in the
     'surf_map' and 'width_map' keys.

     Such maps and their values are always created
     automatically by passing the required keys, so you
     never need to check if a map has some item.

     This is an example of its usage:

     text_surf = (
       TEXT_SURFS_DB[text_settings]['surf_map'][text]
     )

     In other words, here we obtain a cached text surface
     for the given text and its rendering settings. It
     means everytime we do this it will return the same
     surface for that text, thus saving memory whenever
     we want to reuse the same surface over and over again,
     instead of creating a new ones as it is the case
     when using textman.render.render_text().

     For instance, the text editor does this to ensure all
     equal characters in the text use the same text
     surface. However, the text editor doesn't do so
     directly, using the mechanism we just showed in the
     example above, but does so using the CachedTextObject
     class, which we'll present next.

02) The CachedTextObject class

      A Object2D subclass which instantiates objects with
      a text surface and respective rect. This class is used
      to automate the creation of objects which use cached
      text surfaces.

      In other words, the example given in the item above
      explaining the usage of the TEXT_SURFS_DB object
      is performed internally in this class so it always
      obtains cached text surfaces for its 'image' attribute,
      just needing to instantiate a new pygame.Rect object
      for its 'rect' attribute.

      To obtain a new instance, you just need to pass the
      text you want plus the text settings.

      new_instance = CachedTextObject(text, text_settings)
"""

### local imports

from ..ourstdlibs.dictutils import settings_to_hashable_repr

from ..classes2d.single import Object2D

from .render import render_text


### constant: pairs containing special characters and
### their representations

CHAR_VS_REPR_PAIRS = (
    ("\n", "\\n"),
    ("\r", "\\r"),
    ("\t", " " * 4),  # 4 spaces, as in the text editor
)


### classes


class TextSurfacesDatabase(dict):
    """Dict used store maps related to text surfaces.

    Extends the built-in dict.
    """

    def __getitem__(self, text_settings):
        """Return dict with maps related to text settings.

        If the maps for the specific given text settings
        don't exist yet, they are created before being
        returned.

        Parameters
        ==========
        text_settings (dict)
            contains settings defining how the text must
            be rendered;
        """
        ### convert the text settings (a dict) to a custom
        ### tuple representing them, to use as dictionary key
        tuple_key = settings_to_hashable_repr(text_settings)

        ### try returning the value for the tuple we
        ### just obtained
        try:
            return super().__getitem__(tuple_key)

        ### if such value doesn't exist (a key error is
        ### raised), we create the corresponding data,
        ### and return it while at the same time creating
        ### a new item using the tuple key

        except KeyError:

            surf_map = TextSurfaceMap(text_settings)

            return self.setdefault(
                tuple_key, {"surf_map": surf_map, "width_map": surf_map.width_map}
            )

    def free_up_memory(self):
        """Call free_up_memory() in the surf and width maps.

        Check "Memory management" in the glossary.
        """
        for maps in self.values():

            maps["surf_map"].free_up_memory()
            maps["width_map"].free_up_memory()


class TextSurfaceMap(dict):
    """Map to store text surfaces; has extra behaviour."""

    def __init__(self, text_settings):
        """Store given text settings, perform extra setups."""
        ### store text settings
        self.text_settings = text_settings

        ### create a width map with a reference to this
        ### surface map
        self.width_map = TextWidthMap(self)

        ### create text surfaces to represent some special
        ### characters
        self.create_special_surfs()

    def create_special_surfs(self):
        """Create and store surface for special characters.

        The pygame library represents some whitespace
        characters as empty boxes or other replacement
        characters, depending on the font used.

        However, when the text appears in some widgets,
        we do want some of those characters to be
        represented in some meaningful way, so here we
        create custom representations for them.
        """
        ### iterate over the characters and their custom
        ### representations, creating text surfaces for
        ### such representations and storing them in this
        ### surface map

        for char, custom_repr in CHAR_VS_REPR_PAIRS:

            ## set a new item in this surface map using
            ## the character as the key and the text surface
            ## from the custom representation as the value

            self[char] = render_text(custom_repr, **self.text_settings)

    def __missing__(self, key):
        """Create, store and return surface for key (string).

        Parameters
        ==========
        key (string)
            text from which we want a surface rendered
            using the stored text settings.
        """
        return self.setdefault(key, render_text(key, **self.text_settings))

    def free_up_memory(self):
        """Call clear all items except for special characters.

        Check "Memory management" in the glossary.
        """
        ### backup (key, value) pairs for special chars
        ### temporarily

        key_value_pairs = [(char, self[char]) for char, _ in CHAR_VS_REPR_PAIRS]

        ### clear entire surface map
        self.clear()

        ### restore the (key, value) pairs backed up
        self.update(key_value_pairs)


class TextWidthMap(dict):
    """Map to store text surfs width; has extra behaviour."""

    def __init__(self, surf_map):
        """Store the given surface map."""
        self.surf_map = surf_map

    def __missing__(self, key):
        """Return width for surface represented by key.

        The mentioned width is also stored in this width map.
        """
        return self.setdefault(key, self.surf_map[key].get_width())

    def free_up_memory(self):
        """Clear the items."""
        self.clear()


class CachedTextObject(Object2D):
    """A text object whose surface is cached."""

    def __init__(
        self,
        text,
        text_settings,
        coordinates_name="topleft",
        coordinates_value=(0, 0),
        **kwargs,
    ):
        """Store arguments, set image and rect."""
        ### store arguments

        self.text = text
        self.text_settings = text_settings
        self.__dict__.update(kwargs)

        ### set image and rect

        self.image = TEXT_SURFS_DB[text_settings]["surf_map"][text]

        self.rect = self.image.get_rect()
        setattr(self.rect, coordinates_name, coordinates_value)

    def change_text_settings(self, text_settings):
        """Change text settings and replace surface.

        Only does so if the given text settings are
        different than the ones in use.

        Profiling note
        ==============

        I measured the speed of this method both with and
        without the "if block" in a context where the text
        settings were constantly changed between different
        settings. We did so by decorating this method with
        appcommon.debug.measure_average_speed function. We
        used 4, 100, 1000, and 10000 repetitions.

        It turned out, unexpectedly so, that the solution
        with the "if block" made the method quicker when
        the number of repetitions where 4, 100, 1000. The
        speed was about 10% faster.

        We expected all experiments to yield results
        favorable to the solution without the "if block",
        since we know every time the "if check" was
        performed, it came out negative and ended up
        executing the rest of the method anyway, so it
        was just an unnecessary step.

        Only when the repetitions were 10000 the solution
        without the "if block" performed better, but it
        isn't that relevant, cause this method is intended
        to not be repeated so much in a short amount of
        time, so the results with a small number of
        repetitions are assumed to be more useful.

        This needs further investigation, but it shall be
        postponed for a number of reasons:

        1) Counter-intuitive as they may be, the numbers
           still indicate we should keep the "if block";
        2) I don't know enough of Python internals to be
           able to effectively understand why the results
           were like so;
        3) Though speed is important, I have more urgent
           and important tasks to which to attend;
        4) I need a more systematic way to profile code,
           store the results and manage the resulting
           knowledge, so that the profiling experiments
           I run occasionally all contribute together to
           understand profilling and keeping my code as
           quick as it can be without sacrificing
           maintainability/readability; (though in a way,
           this point is related to the point 2).
        """
        if self.text_settings == text_settings:
            return

        self.image = TEXT_SURFS_DB[text_settings]["surf_map"][self.text]

        self.text_settings = text_settings


### special dict to use as database of surface-related
### data
TEXT_SURFS_DB = TextSurfacesDatabase()
