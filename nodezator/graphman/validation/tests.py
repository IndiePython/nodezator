"""Doctests for the graphman/validation/main.py module 

Introduction
============
The module being tested here contains a function
to validate function metadata called
check_return_annotation_mini_lang().


Imports and utilities
=====================

Before presenting the doctests, let's import the objects
to be tested in this module and import/define other
utilities for our tests.

>>> ### let's start by loading the function we want to
>>> ### test
>>> from .main import check_return_annotation_mini_lang

>>> ### define an exception class map to convert strings into
>>> ### the exception classes to which they refer

>>> exception_class_map = {
...   "TypeError"  : TypeError,
...   "ValueError" : ValueError
... }

>>> ### XXX maybe I could search for a way to automatically
>>> ### prepend '... ' at the beginning of lines, so that
>>> ### I can properly indent code blocks with doctests,
>>> ### like the body of the function below (I more or less
>>> ### manually type the dots in some lines)

>>> ### function to test given function using given test data
>>> def test_function_with_test_data(function, test_data):
...     
...     ### store the function name
...     func_name = function.__name__
... 
...     ### let's test compliant cases
... 
...     ## load compliant cases
...     compliant_cases = test_data['compliant_cases']
... 
...     ## iterate over them
...     for case_name, case_data in compliant_cases.items():
... 
...         ## try executing function with case data
...         try: function(case_data)
... 
...         ## if an exception is raised, we report it along
...         ## with the case name by printing them, which
...         ## causes this doctest to fail, since it doesn't
...         ## expect anything to be printed
... 
...         except Exception as err:
...         
...             msg = (
...               '{} of function {} failed: {}'
...             ).format(case_name, func_name, str(err))
... 
...             print(msg)
... 
...     ### and let's now test all the non-compliant cases
... 
...     ## load the non-compliant cases
...     non_compliant_cases = test_data['non_compliant_cases']
... 
...     ## load the error data about the cases
...     error_data = test_data['non_compliance_error_data']
... 
...     ## iterate over non-compliant case items, testing them
... 
...     items = non_compliant_cases.items()
... 
...     for case_name, case_data in items:
... 
...         ## let's check whether the case actually raises
...         ## errors, as expected validates, reporting if
...         ## one of them succeeds
... 
...         # try executing function with case data
...         try: function(case_data)
... 
...         # if an exception is raised, check whether it is
...         # of the expected class and has an expect excerpt
...         # of text
... 
...         except Exception as err:
... 
...             # get error data for case
... 
...             specific_error_data = error_data[case_name]
... 
...             cls_string = specific_error_data['type']
...             cls = exception_class_map[cls_string]
... 
...             excerpt = specific_error_data[
...                                      'message_excerpt']
... 
...             # check whether actuall error is the expected
...             # error by checking its type and whether it
...             # contains an expected excerpt of the message
... 
...             if not isinstance(err, cls):
... 
...                 msg = (
...                   "non-compliant case {} of function {}"
...                   " failed with an unexpected error"
...                   " type: {}"
...                 ).format(case_name, func_name,
...                                          str(type(err)))
... 
...                 print(msg)
... 
...             if excerpt not in str(err):
... 
...                 msg = (
...                   "non-compliant case {} of function {}"
...                   " failed with an unexpected error"
...                   " message: {}"
...                 ).format(case_name, func_name, str(err))
... 
...                 print(msg)
... 
...         # if no exception is raise, then it meann
...         # something is wrong; report this by printing
...         # the case name, which will cause this test to
...         # fail, since it wasn't supposed to print
...         # anything
... 
...         else:
... 
...             msg = (
...               "non-compliant case {} of function {}"
...               " didn't raise an error when it should"
...             ).format(case_name, func_name)
... 
...             print(msg)
>>> 


Doctests for check_return_annotation_mini_lang function
=======================================================

>>> ### load test data for the the function and test it
>>> from .fixtures import TEST_DATA
>>> 
>>> ## pass function along with test data to the function
>>> ## used to test them together; no output must be
>>> ## generated
>>> 
>>> test_function_with_test_data(
...   check_return_annotation_mini_lang, TEST_DATA)
>>> 

"""

from doctest import DocTestSuite


def load_tests(loader, tests, pattern):
    """Return a test suite.

    This function is used for test discovery and its name,
    signature and return value are defined by the load_tests
    protocol described in the standard library unittest
    module online documentation.
    """
    ### return a test suite from the doctests in this module
    return DocTestSuite()
