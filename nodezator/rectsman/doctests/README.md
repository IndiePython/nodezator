# RectsManager Documentation and Tests

This folder contains many chapters that work as documentation and tests for the RectsManager class.

The tests were updated to work with the `pygame-ce` library rather than regular `pygame`. Therefore, whenever we mention `pygame` we are referring to the `pygame-ce` implementation, unless explicitly stated otherwise.


## Table of contents

Below we provide a table of contents.

1. [Introduction](introduction.test.md)
1. [Operations part 01](operations_part01.test.md)
1. [Operations part 02](operations_part02.test.md)
1. [Operations part 03](operations_part03.test.md)
1. [Special methods part 01](special_methods_part01.test.md)
1. [Special methods part 02](special_methods_part02.test.md)
1. [Other topics part 01](other_topics_part01.test.md)
1. [Other topics part 02](other_topics_part02.test.md)
1. [Other topics part 03](other_topics_part03.test.md)
1. [Individual positioning of rects](individual_positioning.test.md)


## Imports

Note that the doctests contain no import statements, since the needed objects are imported and fed to the namespace automatically in the `testmarkdown.py` module (using the `globs` parameter of `doctest.DocFileSuite()`). The imported objects are described in the following paragraphs.

The `pygame.Rect` class is used to instantiate normal pygame rects.

The `RectsManager` class is used as well, since it is the class we are testing/documenting.

The `rect_property` property is meant for injection and helps classes that use the `RectsManager`.

The `ListGroup` class is a `list` subclass used to hold multiple objects.

The `Simple` class is a custom class that contains a rect instance in its `rect` attribute.

The `get_fresh_groups` function returns two custom instances of a class representing a group of objects. Each object in the groups have a "rect" attribute containing a pygame.Rect object representing its position and dimensions. Sections will get the groups from this function at the beginning, using them for testing. Since the groups returned are new instances, freshly set, there's no effects from previous tests, so they can be used to keep the effects of different sets of tests independent from each other.

The `check_error_raising` function performs method calls using the given method names and arguments and checks if the expected error is raised, with the expected message, too. Sections will use this function to test if the operations being tested raise errors as expected from the given invalid/insufficient arguments.
