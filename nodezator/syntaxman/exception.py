"""Custom exception for errors when mapping syntax."""


class SyntaxMappingError(Exception):
    """To raise when an error occurs while mapping syntax.

    Syntax may be complex to handle depending on the
    specific syntax being used.

    Instead of trying to diagnose problems, whenever an
    error is raised while mapping the highlight of text,
    we just indicate the error occured while mapping the
    highlight.

    This way other utilities using syntax highlighting
    can choose what to do, like ignoring the problem
    and rendering the text without highlighting instead,
    etc.
    """
