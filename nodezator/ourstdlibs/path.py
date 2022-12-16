"""pathlib.path related custom operations."""

### standard library imports

from pathlib import Path

from datetime import datetime

from re import fullmatch

from itertools import count

from tempfile import mkdtemp



TIMESTAMP_PATTERN = "_".join(
    (
        "[0-9]" * 4,  # year
        "[0-1][0-9]",  # month
        "[0-3][0-9]",  # day
        "[0-2][0-9]",  # hour
        "[0-5][0-9]",  # minutes
        "[0-5][0-9]",  # seconds
    )
)

# XXX review docstrings


def get_custom_path_repr(path):
    """Return a custom string representation of given path.

    Parameters
    ==========
    path (pathlib.Path instance)
        path used to retrieve information for
        the custom title

    The custom format is inspired in vim text editor
    window caption: filename followed by parent folder
    surrounded by parenthesis. The parent folder has
    the 'home' portion collapsed, that is, represented
    by a '~' character.
    """
    ### separate path of level file into name and parent
    name, parent = path.name, path.parent

    ### try turning parent into its version relative to
    ### the user directory
    try:
        relative_path = parent.relative_to(Path.home())

    ### if the a ValueError is raised (happens when
    ### the path is not a subpath of the path given to
    ### Path.relative_to), use the entire stringified
    ### parent as the 'parent' part in the custom format
    except ValueError:
        parent = str(parent)

    ### otherwise use a stringified path which is the
    ### result of joining the '~' path (the user
    ### directory) with the version of the parent
    ### relative to the user directory
    else:
        parent = str(Path("~") / relative_path)

    ## assign information to title text
    return "{} ({})".format(name, parent)


def get_swap_path(path):
    """Return new path representing swap file of given path.

    Parameters
    ==========
    path (pathlib.Path instance)
        path used as base to form the swap path.

    The new path uses a vim-like way of naming swap
    files: make the file hidden by adding a dot ('.') to
    the filename and add a '.swp' extension after the
    existing extension.
    """
    ### hide path
    hidden_path = path.with_name("." + path.name)

    ### add suffix
    hidden_swap_path = Path(str(hidden_path) + ".swp")

    return hidden_swap_path


def save_timestamped_backup(path, backup_quantity):
    """Save new backup, if applicable, limiting to quantity.

    That is:

    - if the quantity of backups is higher than 0, a new
      backup is saved;
    - if, as a result, the number of existing backups goes
      above the quantity of backups allowed, delete the
      oldest ones;

    The new path is created by adding a timestamp at the
    end of the extension. For instance, if a file is
    named, 'file.ext', its backups will be
    'file.ext.YYYY_MM_DD_HH_MM_SS' and will be a,

    Parameters
    ==========

    path (instance of pathlib.Path class)
        path for which the backup path objects will be
        created
    backup_quantity (integer)
        quantity of backup files that can exist.
    """
    ### reference objects/data locally for quick/easier
    ### access

    parent = path.parent
    path_name = path.name

    ### if quantity of backup files is above 0, we can save
    ### a backup

    if backup_quantity > 0:

        ### build a custom timestamp in the
        ### 'YYYY_MM_DD_HH_MM_SS' format

        timestamp = "".join(
            ## use either a digit or '_'
            char if char.isdigit() else "_"
            ## for each char from the first
            ## 19 ones in string from
            ## datetime.now()
            for char in str(datetime.now())[:19]
        )

        ### create a backup path at the same folder of the
        ### original one, but whose name is comprised by
        ### the original name plus a '.' and the timestamp
        new_path = parent / "{}.{}".format(path_name, timestamp)

        ### copy the contents of the original path in the
        ### backup

        new_path.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")

    ### now limit the existing backups, if any, to the
    ### allowed number

    ## obtain list of backups, sorted so that the oldest
    ## backups appear last
    backups = retrieve_backups(path_name, parent)

    ## backups listed after jumping a number of items
    ## equivalent to the quantity of allowed backups
    ## are considered backups in excess;
    ##
    ## if they exist, we deleted them

    exceeding_backups = backups[backup_quantity:]

    if exceeding_backups:

        for item in exceeding_backups:

            ## try deleting the item
            try:
                item.unlink()

            ## if deletion fails, raise a RuntimeError
            ## from the original one, explaining what we
            ## were doing when the problem appeared

            except Exception as err:

                msg = ("error while trying to delete excess" " backup file ") + str(
                    item
                )

                raise RuntimeError(msg) from err


def retrieve_backups(filename, directory):
    """Return list of existing backups.

    Works by listing paths that are considered backups of
    the file with the given name, in the given directory.

    Also, the backups are sorted so that the oldest backups
    appear at the end of the list.

    Parameters
    ==========

    filename (string)
        name of the file for whose backups we are looking
        for.
    directory (pathlib.Path instance)
        directory wherein to look for backups.
    """
    ### return list of backups, sorted so that the oldest
    ### backups appear last

    return sorted(
        ## all backups
        (
            ## backups are items within the given directory...
            item
            for item in directory.iterdir()
            ## ...whose digits before the last 20 ones are
            ## equal to the original path name (we use 20
            ## instead of 19 to account for the '.' before the
            ## timestamp)...
            if item.name[:-20] == filename
            ## ...and whose last 19 digits are a timestamp,
            ## that is, they match our timestamp pattern
            if fullmatch(TIMESTAMP_PATTERN, item.name[-19:])
        ),
        ## sorted by their timestamps
        key=lambda item: item.name[-19:],
        ## in reverse order
        reverse=True,
    )


### get new filename: solve naming conflicts


def get_new_filename(
    conflicting_name,
    existing_names,
    index_format_spec=">03",
):

    path = Path(conflicting_name)

    stem = path.stem
    suffix = "".join(path.suffixes)

    get_new_index = count().__iter__().__next__

    while True:

        new_name = stem + format(get_new_index(), index_format_spec) + suffix

        if new_name not in existing_names:
            break

    return new_name


### class definition

class TemporaryFilepathsManager:
    
    created_filepaths = set()

    def __init__(
        self,
        temp_dir_suffix=None,
        temp_dir_prefix=None,
        temp_file_prefix='',
        temp_file_suffix='',
        _dir=None,
    ):

        self.suffix = temp_dir_suffix
        self.prefix = temp_dir_prefix

        self.temp_file_prefix = temp_file_prefix
        self.temp_file_suffix = temp_file_suffix

        self.dir = _dir

        self.temp_dir = None

    def get_new_temp_filepath(self):
        """Return a new temporary filepath."""

        ###

        if self.temp_dir is None:

            self.temp_dir = (
                Path(
                    mkdtemp(
                        suffix=self.suffix,
                        prefix=self.prefix,
                        dir=self.dir,
                    )
                )
            )

        ###

        stem_base = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")

        filename = (
            self.temp_file_prefix
            + stem_base
            + self.temp_file_suffix
        )

        new_path = self.temp_dir / filename

        ###

        if new_path in self.created_filepaths:

            get_new_index = count().__iter__().__next__

            while True:

                filename = (
                    self.temp_file_prefix
                    + stem_base
                    + "_n"
                    + f"{get_new_index():0>3}"
                    + self.temp_file_suffix
                )

                new_path = self.temp_dir / filename

                if new_path not in self.created_filepaths:
                    break

        self.created_filepaths.add(new_path)

        return new_path

    def is_temp_path(self, path):
        """Return whether path is within created filepaths."""
        return path in self.created_filepaths

    def ensure_removed(self):
        """Make temporary folder and files within are deleted."""

        if self.temp_dir is None: return

        for path in self.created_filepaths:

            try:
                path.unlink()
            except FileNotFoundError:
                pass

        self.temp_dir.rmdir()
        self.temp_dir = None
