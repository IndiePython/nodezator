
### standard library imports

from pathlib import Path

from doctest import DocFileSuite

from ast import literal_eval


### local import
from .main import check_return_annotation_mini_lang



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

        TEST_DATA = literal_eval(
            (THIS_DIR / 'test_data.pyl').read_text(encoding='utf-8')
        )

        tests.addTests(

            ## test suite
            DocFileSuite(

                ## test files to include
                *test_md_files,

                ## names to include in the namespace of each test

                globs={
                    'TEST_DATA': TEST_DATA,
                    'check_return_annotation_mini_lang': (
                        check_return_annotation_mini_lang
                    ),
                },
            )
        )

    return tests

