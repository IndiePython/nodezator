"""Facility with function to evaluate numeric expression."""

### standard library imports

import builtins, math, random, statistics

from keyword import kwlist as python_reserved_keywords

from io import BytesIO

from tokenize import (
    ### tokens for analysis
    OP,
    NAME,
    ### tool to tokenize string with
    ### Python code
    tokenize,
)


### constants

## formatter for error messages when finding forbidden
## tokens

FORBIDDEN_OPERATION_FORMATTER = ("forbidden operator used: {}").format

FORBIDDEN_NAME_FORMATTER = ("forbidden name used: {}").format

## forbidden operators

FORBIDDEN_OPERATORS = {
    "=",
    ":",
    ";",
    "@",
    "+=",
    "-=",
    "*=",
    "/=",
    "//=",
    "%=",
    "@=",
    "&=",
    "|=",
    "^=",
    ">>=",
    "<<=",
    "**=",
}

## allowed builtins

ALLOWED_BUILTINS = {
    ## keywords
    "True",
    "False",
    ## builtins functions
    "abs",
    "all",
    "min",
    "any",
    "slice",
    "divmod",
    "bool",
    "int",
    "sum",
    "pow",
    "float",
    "range",
    "zip",
    "map",
    "max",
    "round",
}

## allowed names

ALLOWED_NAMES = set.union(
    ## keywords that we allow
    {"and", "else", "for", "if", "in", "is", "not", "or"},
    ## allowed builtins
    ALLOWED_BUILTINS,
)

## forbidden names

FORBIDDEN_NAMES = (
    set.union(
        ## all python reserved keywords
        set(python_reserved_keywords),
        ## all builtin functions
        set(
            builtin_name
            for builtin_name in dir(builtins)
            if builtin_name.islower()
            if not builtin_name.startswith("_")
        ),
        ## all builtin exceptions plus True, False, None and
        ## Ellipsis;
        ##
        ## that is, all builtins starting with an uppercase letter
        set(builtin_name for builtin_name in dir(builtins) if builtin_name[0].isupper())
        ## minus all the names we allowed
    )
    - ALLOWED_NAMES
)


## attributes from imported modules
##
## depending on the Python version being used, some of
## these names might not be available

# from 'math' library

ATTRS_FROM_MATH = {
    # from python 3.5+
    "acos",
    "acosh",
    "asin",
    "asinh",
    "atan",
    "atanh",
    "atan2",
    "cos",
    "ceil",
    "degrees",
    "hypot",
    "exp",
    "expm1",
    "e",
    "erf",
    "erfc",
    "fabs",
    "factorial",
    "floor",
    "fmod",
    "frexp",
    "fsum",
    "gamma",
    "gcd",
    "inf",
    "lgamma",
    "ldexp",
    "log",
    "log1p",
    "log2",
    "log10",
    "modf",
    "nan",
    "pi",
    "pow as math_pow",
    "radians",
    "sin",
    "sinh",
    "sqrt",
    "tan",
    "tanh",
    "trunc",
    # from python 3.6+
    "tau",
    # from python 3.7+
    "remainder",
    # from python 3.8+
    "comb",
    "dist",
    "isqrt",
    "perm",
    "prod"
    # from python 3.9+
    "lcm",
    "nextafter",
    "ulp",
}

# from 'random' library

ATTRS_FROM_RANDOM = {
    # from python 3.5+
    "betavariate",
    "choice",
    "expovariate",
    "gammavariate",
    "gauss",
    "getrandbits",
    "lognormvariate",
    "randint",
    "random",
    "randrange",
    "normalvariate",
    "paretovariate",
    "triangular",
    "uniform",
    "vonmisesvariate",
    "weibullvariate",
}

# from 'statistics' library

ATTRS_FROM_STATISTICS = {
    # from python 3.5+
    "mean",
    "median",
    "median_low",
    "median_high",
    "median_grouped",
    "mode",
    "stdev",
    "variance",
    "pstdev",
    "pvariance",
    # from python 3.6+
    "harmonic_mean",
    # from python 3.8+
    "fmean",
    "geometric_mean",
    "multimode",
    "quantiles",
    # from python 3.10+
    "covariance",
    "correlation",
}


### create and populate custom globals dictionary to use
### when evaluating numerical expressions

## create dict
CUSTOM_GLOBALS_DICT = {}

## iterate over each module and respective set of names
## of objects in that module's attributes;
##
## the purpose here is to populate the custom global dict
## with such objects

for module, attr_names in (
    (math, ATTRS_FROM_MATH),
    (statistics, ATTRS_FROM_STATISTICS),
    (random, ATTRS_FROM_RANDOM),
):

    ## iterate over each attribute name, preprocessing it,
    ## then trying to retrieve it from the module to insert
    ## in the dict

    for attr_name in attr_names:

        ## preprocessing step;
        ##
        ## check whether the attribute name is in fact
        ## a pair of names separated by an ' as ' substring;
        ##
        ## if it is, the first name is the actual attribute
        ## name and the second name is the name to which the
        ## object in the attribute must be bound, that is,
        ## the name to use as a keyword in the custom
        ## globals dict

        attr_name, is_pair_of_names, new_name = attr_name.partition(" as ")

        keyword = new_name if is_pair_of_names else attr_name

        ## try retrieving object from module's attribute
        try:
            obj = getattr(module, attr_name)

        ## attribute errors should be considered the result
        ## of trying to retrieve from the module an object
        ## not existent/available in the Python version used;
        ## in such case we just pass
        except AttributeError:
            pass

        ## if otherwise we succeed, store the retrieved
        ## attribute in our custom global dictionary
        else:
            CUSTOM_GLOBALS_DICT[keyword] = obj


### main function


def numeric_evaluation(string):
    """Evaluate string representing numeric value/expression.

    Before evaluating the string, it is checked for safety.
    If string isn't safe, an error is raised.
    """
    ### raise error if string isn't safe
    check_string_safety(string)

    ### finally evaluate the string with the custom globals
    ### dict we put together, returning the resulting value
    return eval(string, CUSTOM_GLOBALS_DICT)


### utility function


def check_string_safety(string):
    """Raise ValueError if string isn't safe for evaluation.

    Introduction
    ============

    Safe strings are the ones which don't have forbidden
    tokens, that is, forbidden operators and names.

    All other tokens are considered allowed and the string
    considered safe.

    Forbidden tokens are tokens which we assume won't
    contribute to form a valid number or numerical
    expression or may cause the application to crash,
    like when the user types 'quit()', for instance.


    Reasoning
    =========

    why bother at all to prevent some tokens to be used?
    Because the expression is evaluated using the built-in
    function 'eval()'. Thus, some expressions could be
    harmful or not meaningful at all. For instance, the user
    could type 'quit()' or 'exit()'.

    This function works by preventing a known set of
    forbidden operators and names to be used. This way,
    only safe names/operators shall remain. Thus, no harmful
    code can be evaluated.


    Only a layer of protection
    ==========================

    We don't need to cover all possible cases of unsafe or
    not meaningful content in this function. There are 02
    reasons for this:

    1) the intfloatentry widget limits which characters
       can be typed, so a lot of otherwise wrong syntax
       just cannot be typed, so there's no need to check
       them here;

    2) other wrong/innappropriate syntax that may pass
       unnoticed by this function isn't harmful, because
       further down the pipeline, in other functions/methods
       that take over from where this function ends, if an
       innapropriate syntax is detected, then the widget
       just reverts back to its previous value;

    In other words, this function is just one more layer of
    protection. Each layer has its importance/role.
    """
    ### tokenize the string;
    ###
    ### that is, get an iterable which yields named tuples
    ### representing tokens (data from each token) when we
    ### iterate over it

    raw_tokens = tokenize(BytesIO(string.encode("utf-8")).readline)

    ### iterate over the tokens, raising a ValueError
    ### if an invalid token appears;

    for token_type, token_string, _, _, _ in raw_tokens:

        ### if a scenario where the token is forbidden
        ### happens, pick the corresponding formatter for
        ### an error message explaining the problem which
        ### will be used in the 'raise' statement at the
        ### end of this "for loop"'s body

        if token_type == OP and token_string in FORBIDDEN_OPERATORS:
            formatter = FORBIDDEN_OPERATION_FORMATTER

        elif token_type == NAME and token_string in FORBIDDEN_NAMES:
            formatter = FORBIDDEN_NAME_FORMATTER

        ### if no forbidden scenario was found, just skip
        ### to next token using the 'continue' statement,
        ### therefore avoiding the error raising statement
        ### further below
        else:
            continue

        ### if one of the forbidden scenarios above happened,
        ### raise a ValueError explaining the problem using
        ### the chosen formatter
        raise ValueError(formatter(token_string))
