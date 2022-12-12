"""Colors panel class extension to import/export colors."""

### standard library import
from pathlib import Path


### local imports

from ....ourstdlibs.pyl import load_pyl, save_pyl

from ....ourstdlibs.color.custom import custom_format_color

from ....dialog import create_and_show_dialog

from ....fileman.main import select_paths


class ImportExportOperations:
    """Operations to import/export colors."""

    def import_colors(self):
        """Import colors from python literals in path(s)."""

        ### retrieve path(s) from file browser
        paths = select_paths(caption="Select path(s)")

        ### if a path or list of paths was not returned,
        ### just exit the method by returning
        if not paths:
            return

        ### otherwise, load and set colors

        try:
            colors = sum(
                (
                    custom_format_color(
                        load_pyl(path),
                        "rgb_tuple",
                        False,
                    )
                    for path in paths
                ),
                (),
            )

        ## inform user if error occur

        except Exception as err:

            create_and_show_dialog(
                f"Error while loading colors: {str(err)}",
                level_name="error",
            )

        else:

            ### set the colors into the colors panel
            self.set_colors(colors)

    def export_colors(self):
        """Export colors as a python literal."""

        ### retrieve path(s) from file browser

        path = select_paths(caption=("Provide a single path wherein to save" " colors"))

        ### if a path or list of paths was not returned,
        ### just exit the method by returning
        if not path:
            return

        ### if path returned isn't a single pathlib.Path
        ### object, inform user and exit method

        if len(path) > 1:

            create_and_show_dialog(
                "must provide a single file path",
                level_name="warning",
            )

            return

        ### otherwise, export colors

        try:
            save_pyl(
                self.get_colors(),
                path[0],
                width=10,
            )

        except Exception as err:

            create_and_show_dialog(
                f"error while saving colors: {str(err)}",
                level_name="error",
            )
