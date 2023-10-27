
### standard library imports

from unittest import TestCase

from pathlib import Path

from tempfile import TemporaryDirectory

from zipfile import ZipFile

from string import ascii_letters

from random import shuffle

from importlib.util import find_spec


### local imports

from . import load_scripts

from ..exception import NodeScriptsError



HERE = Path(__file__).parent


### utility function

def load_local_from_zip(zip_filename):
    """Load local node pack from the given name of zip file."""

    with TemporaryDirectory() as tempdir:

        node_pack_zip = HERE / zip_filename

        with ZipFile(str(node_pack_zip), 'r') as myzip:
            myzip.extractall(tempdir)

        node_pack_path = str(next(Path(tempdir).iterdir()))

        load_scripts([node_pack_path],[], store_references_on_success=False)


### test case

class LoadTest(TestCase):

    def test_success(self):
        ### expected to execute without problems
        load_local_from_zip('node_pack_nodes.zip')

    def test_installed_not_loaded(self):

        ### attempt to load a installable node pack which is
        ### not installed

        ## find the name of a module that doesn't exists

        letters = list(ascii_letters)

        while True:

            shuffle(letters)
            module_name = ''.join(letters)

            # if module name has no spec, we assume it doesn't exist
            if find_spec(module_name) is None:
                break

        ## try loading that module (knowing that it will fail)

        with self.assertRaises(NodeScriptsError) as context_manager:
            load_scripts([],[module_name], store_references_on_success=False)

        exception_str = str(context_manager.exception)
        self.assertIn("could not import", exception_str)
        self.assertIn("(it is supposed to be installed)", exception_str)

    def test_not_loaded(self):
        ### intentional syntax error to prevent node script from loading

        with self.assertRaises(NodeScriptsError) as context_manager:
            load_local_from_zip('node_pack_with_error.zip')

        self.assertIn(
            "error while trying to load", str(context_manager.exception)
        )

    def test_no_callable(self):
        # the script is simply lacking the main_callable assigment

        with self.assertRaises(NodeScriptsError) as context_manager:
            load_local_from_zip('node_pack_no_callable.zip')

        self.assertIn(
            "node script is missing a", str(context_manager.exception)
        )

    def test_no_callable_object(self):
        # main_callable is an int

        with self.assertRaises(NodeScriptsError) as context_manager:
            load_local_from_zip('node_pack_not_callable_object.zip')

        self.assertIn("must be callable", str(context_manager.exception))


    def test_no_signature(self):
        ### callable object in 'main_callable' variable is provided,
        ### it can't be inspected, that is, inspect.signature() raises
        ### an error

        # we expect the specified error with specified substring
        # was raised

        with self.assertRaises(NodeScriptsError) as context_manager:
            load_local_from_zip('node_pack_not_inspectable.zip')

        self.assertIn(
            "node script isn't inspectable", str(context_manager.exception)
        )
