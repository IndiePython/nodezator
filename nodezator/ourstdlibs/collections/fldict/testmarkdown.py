
### standard library imports

from pathlib import Path

from doctest import DocFileSuite

from collections.abc import Mapping

from copy import copy, deepcopy


### local imports

from ...behaviour import flatten_mapping_values

from .main import FlatListDict



### function responsible for including the doctests from the .test.md
### files among the tests run when executing "python3 -m unittest" from
### the top level directory of the repository

def load_tests(loader, tests, ignore):

    topleveldir = Path(__file__).parent

    test_md_files = [
        str(item.relative_to(topleveldir))
        for item in topleveldir.iterdir()
        if ''.join(item.suffixes) == '.test.md'
    ]

    if test_md_files:

        tests.addTests(

            ## test suite
            DocFileSuite(

                ## test files to include
                *test_md_files,

                ## names to include in the namespace of each test

                globs={
                    'Mapping': Mapping,
                    'copy': copy,
                    'deepcopy': deepcopy,
                    'FlatListDict': FlatListDict,
                    'flatten_mapping_values': flatten_mapping_values,
                },
            )
        )

    return tests

