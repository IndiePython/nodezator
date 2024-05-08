"""Graph management exceptions."""

### standard library import
from textwrap import wrap


### local import
from ..appinfo import MAIN_CALLABLE_VAR_NAME



TWO_LINES = '\n\n'


### raised when loading/processing a native file

class NodeScriptsError(Exception):
    """Raised whenever we can't load/process a node script.

    These errors can be divided into 05 categories:

    1) importing a (supposedly) installed node pack fails;
    2) importing a node script module fails, that is, when the
       script can't be imported;
    3) the user doesn't provide an object to define a node
       stored in a special variable as expected;
    4) the object provided isn't actually callable
       or doesn't contain one;
    5) the callable provided isn't inspectable, that is,
       we can't obtain a signature object from it using
       inspect.signature or inspect.signature plus
       inspect.get_annotations;
    """

    def __init__(
        self,
        installed_pack_not_imported,
        scripts_not_loaded,
        scripts_missing_node_definition,
        not_actually_callables,
        signature_callables_not_inspectable,
    ):
        """Initialize superclass with custom message."""

        msg = TWO_LINES

        for message in installed_pack_not_imported:

            msg += (
                "- "
                + '\n'.join(wrap(message, width=90))
                + TWO_LINES
            )

        for script_filepath, error_message in scripts_not_loaded:

            msg += '\n'.join(

                wrap(
                    (
                        f"error while trying to load '{script_filepath}'"
                        f" node script: {error_message}"
                    ),
                    width=90,
                )

            ) + TWO_LINES

        for script_filepath in scripts_missing_node_definition:

            msg += '\n'.join(

                wrap(
                    (
                        f"the '{script_filepath}' node script is missing a"
                        f" '{MAIN_CALLABLE_VAR_NAME}' variable with a valid"
                        " node definition object"
                    ),
                    width=90,
                )

            ) + TWO_LINES

        for callable_name, script_filepath in not_actually_callables:

            msg += '\n'.join(

                wrap(
                    (
                        f"the '{callable_name}' object provided in the"
                        f" '{script_filepath}' node script must be callable"
                    ),
                    width=90,
                )

            ) + TWO_LINES

        for callable_name, script_filepath in signature_callables_not_inspectable:

            msg += '\n'.join(

                wrap(
                    (
                        f"the '{callable_name}' signature callable from the"
                        f" '{script_filepath}' node script isn't inspectable"
                    ),
                    width=90,
                )

            ) + TWO_LINES

        ###
        super().__init__(msg)


class MissingNodeScriptsError(Exception):
    """Raised whenever there are missing node scripts.

    That is, this happens when we try to load a file
    which has nodes in it for which node scripts weren't
    found.

    It means the graph can't be visually represented,
    and, in consequence, we can neither view, edit or
    execute it.
    """

    def __init__(self, missing_ids):
        """Store the missing scripts ids"""

        self.missing_ids = missing_ids

        ### initialize superclass with custom message

        msg = (
            "node packs have missing scripts (see below)."
            + TWO_LINES
            + '\n'.join(f"- {item}" for item in missing_ids)
        )

        super().__init__(msg)


### raised preparing to execute graph or during its execution

class LackOfInputError(Exception):
    """Raised whenever a parameter has no data.

    That is, when it lacks a default value or a value provided
    via widget or incoming connection.

    This doesn't apply to parameters of variable kind (*args or
    **kwargs), because they have implicit default values (an
    empty tuple and an empty dict respectively).

    Subparameters aren't affected by this problem, since they
    simply cease to exist when there's no source of data to
    them.
    """

    def __init__(
        self,
        inexecutable_node,
        params_or_subparams_lacking_data,
    ):
        """Execute superclass __init__ w/ custom message."""
        ### get a string representing a message in the
        ### form of a custom report about the inexecutable
        ### node

        report_message = (
            "'{}'() node (id {}) was deemed inexecutable due"
            " to lack of data in the following parameters (or"
            " subparameters): {}"
        ).format(
            inexecutable_node.title_text,
            inexecutable_node.id,
            params_or_subparams_lacking_data,
        )

        ### initialize superclass with custom message
        super().__init__(report_message)



class UnexpectedOutputError(Exception):
    """Raised whenever expected mapping output misses one or more keys.

    In Python every callable returns only one output. However, Nodezator
    offers a way for users to return a mapping and have its items treated
    as though they were different outputs.

    When this is the case, if the user doesn't return a mapping

    That is, when the return value of the node's callable is expected
    to be a mappping with specific keys but it either isn't a mapping
    or, if it is, it lacks the needed key.
    """

    def __init__(self, node, expected_outputs):
        """Execute superclass __init__ w/ custom message."""
        ### get a string representing a message in the
        ### form of a custom report about the node and
        ### its missing output

        report_message = (
            "the '{}'() node (id {}) must return a dict"
            " (mapping) with the following keys: {}"
        ).format(
            node.title_text,
            node.id,
            ", ".join(expected_outputs),
        )

        ### initialize superclass with custom message
        super().__init__(report_message)


class PositionalSubparameterUnpackingError(Exception):
    """Raised when positional subparameter unpacking fails.

    That is, when a positional-variable subparameter marked
    for unpacking fails to unpack.
    """

    def __init__(
        self,
        node,
        parameter_name,
        positional_subparameter_index,
    ):
        """Execute superclass __init__ w/ custom message."""
        ### get a string representing a message in the
        ### form of a custom report about the node and
        ### the subparameter that failed to unpack

        report_message = (
            "the '{}'() node (id {}) failed to unpack"
            " the subparameter received in the position"
            " #{} of the '{}' parameter"
        ).format(
            node.title_text,
            node.id,
            positional_subparameter_index,
            parameter_name,
        )

        ### initialize superclass with custom message
        super().__init__(report_message)


class KeywordSubparameterUnpackingError(Exception):
    """Raised when keyword subparameter unpacking fails.

    That is, when a keyword-variable subparameter marked
    for dict unpacking fails to unpack.
    """

    def __init__(
        self,
        node,
        parameter_name,
        keyword_subparameter_index,
    ):
        """Execute superclass __init__ w/ custom message."""
        ### get a string representing a message in the
        ### form of a custom report about the node and
        ### the subparameter that failed to dict-unpack

        report_message = (
            "the '{}'() node (id {}) failed to dict-unpack"
            " the subparameter received in the position"
            " #{} of the '{}' parameter"
        ).format(
            node.title_text,
            node.id,
            keyword_subparameter_index,
            parameter_name,
        )

        ### initialize superclass with custom message
        super().__init__(report_message)


class NodeCallableError(Exception):
    """For errors during node callable call or execution.

    That is, it is raised when an error occurs while
    trying to call a node's callable or during execution
    of such callable.
    """

    def __init__(self, node):
        """Execute superclass __init__ w/ custom message."""
        ### store reference to node wherein the error
        ### bubbled up
        self.node = node

        ### create a string representing a message with
        ### information about the node whose callable
        ### raised an error

        report_message = ("'{}'() callable from node #{} failed.").format(
            node.title_text, node.id
        )

        ### initialize superclass with custom message
        super().__init__(report_message)


### proxy node error


class ProxyNodesLackingDataError(Exception):
    """Raised during graph execution."""

    def __init__(self, nodes):
        """Execute superclass __init__ w/ custom message."""
        ### store reference to node lacking data
        self.nodes = nodes

        ### create a string representing a message with
        ### information about the node

        report_message = "Lack of data source in the" " following proxy node(s):"

        report_message += ", ".join(
            f"id #{node.id} (title={node.title})" for node in nodes
        )

        ### initialize superclass with custom message
        super().__init__(report_message)


### node packs errors


class NodePackNotImportedError(ModuleNotFoundError):
    """Raised when a node pack supposed to be installed can't be imported."""


class NodePackNotFoundError(Exception):
    """Raised when a node pack isn't found."""

    def __init__(self, message, faulty_pack):

        self.faulty_pack = faulty_pack
        super().__init__(message)


class NodePackNotADirectoryError(NotADirectoryError):
    """Raised when the node pack path isn't a directory."""

    def __init__(self, message, faulty_pack):

        self.faulty_pack = faulty_pack
        super().__init__(message)


class NodePackLackingCategoryError(Exception):
    """Raised when node pack hasn't at least 01 category."""

    def __init__(self, message, faulty_pack):

        self.faulty_pack = faulty_pack
        super().__init__(message)


class CategoryLackingScriptDirectoryError(Exception):
    """Raised when category hasn't at least 01 script dir."""

    def __init__(self, message, faulty_pack):

        self.faulty_pack = faulty_pack
        super().__init__(message)


class ScriptDirectoryLackingScriptError(Exception):
    """Raised when script directory lacks script."""

    def __init__(
        self,
        node_pack,
        category_dir,
        script_dir,
        script_file,
    ):

        pack_kind = 'installed' if type(node_pack) == str else 'local'

        message = (
            f"The '{script_dir.name}' script of the"
            f" '{category_dir.name}' category of the"
            f" '{node_pack}' {pack_kind} node pack is missing"
            f" its '{script_file.name}' script file"
        )

        self.faulty_pack = node_pack

        super().__init__(message)


NODE_PACK_ERRORS = (
    NodePackNotImportedError,
    NodePackNotFoundError,
    NodePackNotADirectoryError,
    NodePackLackingCategoryError,
    CategoryLackingScriptDirectoryError,
    ScriptDirectoryLackingScriptError,
)
