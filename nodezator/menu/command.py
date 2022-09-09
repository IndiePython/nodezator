"""Facility for managing widgets for menubar."""

### local imports

from ..config import APP_REFS

from ..ourstdlibs.behaviour import empty_function

from ..classes2d.single import Object2D


class Command(Object2D):
    """A versatile button-like widget for menus.

    It can be used as a simple command, a checkbutton,
    a radiobutton or even a separator widget.

    A button always have a parent attribute, but never
    children. It is like a 'leaf' on the menu manager
    tree-like structure.
    """

    def __init__(
        self,
        parent,
        data,
        surface_map,
    ):
        """Store variables and perform setups.

        Parameters
        ==========

        parent (menu.submenu.main.Menu or
                menu.main.MenuManager instance)
            object regarded as parent of this Command
            instance.
        data (dict)
            command additional data.
        surface_map (dict)
            dict containing surfaces, nested or not.
        """
        ### store arguments

        self.parent = parent
        self.label_text = data["label"]

        ### perform extra setups depending on data received

        if set(data["label"]) == {"-"}:

            self.invoke = empty_function
            self.surface_map = surface_map

        elif "widget" in data:

            self.attribute_name = data["attribute_name"]

            self.top_surface_map = surface_map

            if data["widget"] == "checkbutton":
                self.invoke = self.toggle_boolean

            elif data["widget"] == "radiobutton":

                self.value = data["value"]
                self.invoke = self.set_value

            else:
                raise ValueError(
                    "if 'widget' key exists, it must"
                    " be either 'checkbutton' or"
                    " 'radiobutton'"
                )

            ##

            self.surface_map_updating_routine = self.update_surface_map

            self.surface_map_updating_routine()

        else:

            self.invoke = data["command"]
            self.surface_map = surface_map

        ### reference the normal surface as the 'image'
        ### attribute of this instance and also obtain
        ### a rect from it

        self.image = self.surface_map["normal"]
        self.rect = self.image.get_rect()

    def highlight(self):
        """Change image to highlighted surface.

        Also collapse all sibling items (other commands and
        menu.submenu.main.Menu instances).
        """
        self.image = self.surface_map["highlighted"]
        self.collapse_siblings()

    def unhighlight(self):
        """Change image to normal surface."""
        self.image = self.surface_map["normal"]

    def collapse_siblings(self):
        """Collapse all sibling items.

        Sibling items are either other commands and/or
        menu.submenu.main.Menu instances.
        """
        for child in self.parent.children:

            if hasattr(child, "is_expanded"):
                child.is_expanded = False

    def get_formatted_tree(self):
        """Return formatted text representing tree."""

        texts = []

        obj = self

        while hasattr(obj, "label_text"):

            texts.append(obj.label_text)
            obj = obj.parent

        return " > ".join(reversed(texts))

    def update_surface_map(self):
        """Update surface map according to attribute value.

        Current surface is update as well to its normal
        state.

        That is, an attribute whose name is stored in this
        instance is checked and, depending on its value
        the appropriate surface map is assigned to the
        'surface_map' attribute.
        """
        current_value = getattr(APP_REFS, self.attribute_name)

        key = (
            current_value
            if isinstance(current_value, bool)
            else self.value == current_value
        )

        self.surface_map = self.top_surface_map[key]

        self.image = self.surface_map["normal"]

    def set_value(self):
        """Set 'value' as current value."""
        setattr(APP_REFS, self.attribute_name, self.value)

    def toggle_boolean(self):
        """Toogle boolean value."""

        setattr(
            APP_REFS, self.attribute_name, not getattr(APP_REFS, self.attribute_name)
        )

    def __repr__(self):
        """Return string representation.

        The command object is a fairly simple object.
        However, it's essence is mostly defined by the
        callable it carries. There's no way to faithfully
        communicate the contents of such callable, though.
        We could add its string representation or docstring
        to the command string representation, but it would
        fill the terminal with too much information.

        Hence, we use the simplest representation: just
        returning the command label.

        Overrides object.__repr__.
        """
        return 'Command "{}"'.format(self.label_text)
