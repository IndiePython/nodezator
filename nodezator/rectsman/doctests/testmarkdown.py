
### standard library imports

from pathlib import Path

from doctest import DocFileSuite


### third-party imports

import pygame

from pygame import Rect


### local imports

from ..main import RectsManager, rect_property

from .fixtures import (
    Simple,
    ListGroup,
    get_fresh_groups,
    check_error_raising,
)



### this directory
THIS_DIR = Path(__file__).parent

### function responsible for including the doctests from the .test.md
### files among the tests run when executing "python3 -m unittest" from
### the top level directory of the repository

def load_tests(loader, tests, ignore):

    test_md_files = [
        str(item.relative_to(THIS_DIR))
        for item in THIS_DIR.iterdir()
        if ''.join(item.suffixes) == '.test.md'
    ]

    if test_md_files:

        tests.addTests(
            DocFileSuite(
                *test_md_files,
                globs={
                    'pygame': pygame,
                    'Rect': Rect,
                    'RectsManager': RectsManager,
                    'Simple': Simple,
                    'ListGroup': ListGroup,
                    'rect_property': rect_property,
                    'get_fresh_groups': get_fresh_groups,
                    'check_error_raising': check_error_raising,
                },
            )
        )

    return tests

