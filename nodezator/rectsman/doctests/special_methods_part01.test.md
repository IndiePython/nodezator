# Special methods part 01

[Back to table of contents](README.md#table-of-contents)

This document is part of a series containing both documentation and tests for the RectsManager class.  In this document we present operations performed by special methods, that is, those which use double underscores in their names.

The `__repr__` method, however, was presented much earlier, in the [Introduction](introduction.test.md) chapter, due to how informative it is about the values in RectsManager instances.

Not all special methods have custom implementations, though. This is so because either such methods are not needed or because the default implementation from the "object" type is used instead.


## `__iter__()`: returning an iterator

Officially, a class is iterable if it provides an `__iter__` method returning an iterator. This is not the only way to make a class iterable, though. As long as a class has a `__getitem__` method and such method accept integers starting with 0, this mechanism is used to iterate the class instead, making it so it is accepted as a valid iterable.

That is how iteration takes place in pygame.Rect, via the `__getitem__` method. pygame.Rect doesn't rely on an `__iter__` method. The reason the RectsManager class has an `__iter__` method, not relying on its `__getitem__` method, is because the `__getitem__` method is unnecessarily slower for iteration, since it builds an union rect every time it returns a new item.

The RectsManager `__iter__` implementation, on the other hand, yields items from an union rect built only once.  As a result, the operation ends up taking only 1/4 of the time it would take in comparison with the `__getitem__` solution.

The `__iter__` method is used automatically every time someone iterates over the RectsManager instance's items.

```python
# get group instance
>>> g1, _ = get_fresh_groups()

>>> for item in g1.rect: print(item)
... 
0
-10
40
50

```

The `__getitem__` method is still needed for getting items individually, as we'll see in the next section.


## `__getitem__(index)` or `instance[index]`

pygame.Rect has a `__getitem__` implementation. It is emulated in the RectsManager class too. We generate an union rect of all underlying rects and return the index given in the argument from such union rect.

It is important to remember that each index in a rect object corresponds to a property:

- 0 or -4 returns "left";
- 1 or -3 returns "top";
- 2 or -2 returns "width";
- 4 or -1 returns "height";

For instance:

```python
# get group instance
>>> g1, _ = get_fresh_groups()

>>> g1.rect[0] == g1.rect.left
True
>>> g1.rect[3] == g1.rect.height
True

```

The error handling is accurately emulated too. Well, mostly, at least: check the [Error handling in `__getitem__`, `__setitem__` and `__delitem__`](special_methods_part01.test.md#error-handling-in-__getitem__-__setitem__-and-__delitem__) section in this chapter to know why, and also to know why we don't use the function `check_error_raising` to test the error handling of this method. Let's demonstrate the error handling:

For instance, let's use the RectsManager instance and the first rect in the group (since it is a a pygame.Rect instance) and compare the error messages when causing different errors; as can be seen below, both objects raise the same errors when faced with the same problems.

```python
>>> rects_man, pygame_rect = g1.rect, g1[0].rect
>>> pygame_rect[5] # outside allowed range
Traceback (most recent call last):
...
IndexError: Invalid rect Index

>>> rects_man[5] # same problem and same error
Traceback (most recent call last):
...
IndexError: Invalid rect Index

>>> pygame_rect[2.2] # type not allowed
Traceback (most recent call last):
...
TypeError: Invalid Rect slice

>>> rects_man[2.2] # same problem and same error
Traceback (most recent call last):
...
TypeError: Invalid Rect slice

```

Note that slicing is allowed in pygame.Rect, and thereby in RectsManager too.

```python
>>> pygame_rect[1:3]
[0, 20]
>>> rects_man[1:3]
[-10, 40]

```


## `__setitem__(index, value)` or `instance[index] = value`

pygame.Rect also has a `__setitem__` implementation and it is also emulated in the RectsManager class too. When the index received is an integer within the allowed range (from -4 to 3) and the value is allowed (an integer or a type that pygame.Rect can constrain to an integer), the corresponding property value is set to the new value, just as would happen with a pygame.Rect instance.

For instance:

```python
# get group instance
>>> g1, _ = get_fresh_groups()

# setting left

>>> g1.rect[0] # current value
0
>>> g1.rect[0] = 20 # setting new value
>>> g1.rect[0] # new value
20

# setting height

>>> g1.rect[3] # current value
50
>>> g1.rect[3] = 80 # setting new value
>>> g1.rect[3] # new value
80

```

The error handling is accurately emulated too. Well, mostly, at least: check the [Error handling in `__getitem__`, `__setitem__` and `__delitem__`](special_methods_part01.test.md#error-handling-in-__getitem__-__setitem__-and-__delitem__) section in this chapter to know why, and also to know why we don't use the function `check_error_raising` to test the error handling of this method. Let's demonstrate the error handling:

For instance, let's use the first rect in the group (since it is a pygame.Rect instance) and the RectsManager instance itself and compare the error messages when causing different errors.

```python
>>> rects_man, pygame_rect = g1.rect, g1[0].rect

# pygame.Rect: value is ok, but index is outside allowed range
>>> pygame_rect[5] = 20
Traceback (most recent call last):
...
IndexError: Invalid rect Index

# RectsManager: the same problem and same error
>>> rects_man[5] = 20
Traceback (most recent call last):
...
IndexError: Invalid rect Index

# pygame.Rect: value is ok, but index type not allowed (float)
>>> pygame_rect[2.2] = 20
Traceback (most recent call last):
...
TypeError: Invalid Rect slice

# RectsManager: the same problem and same error
>>> rects_man[2.2] = 20
Traceback (most recent call last):
...
TypeError: Invalid Rect slice

# pygame.Rect: index is ok, but value type is not allowed (string)
>>> pygame_rect[2] = '20'
Traceback (most recent call last):
...
TypeError: Must assign numeric values

# RectsManager: the same problem and same error
>>> rects_man[2] = '20'
Traceback (most recent call last):
...
TypeError: Must assign numeric values

```

Curiosity: at the time I was developing the RectsManager class, I noticed that some unexpected types are allowed for values, though they are converted to integers in the end. float is allowed (note that they have their decimal part stripped, when assigned, instead of being rounded).  decimal.Decimal is allowed, too. fractions.Fraction is not allowed though, even when the value represents an "exact" value, like Fractions(4, 2), for instance.


## `__delitem__(index)` or `del instance[index]`

pygame.Rect has yet another item related method, the `_delitem__` method, which, as the other, is emulated in the RectsManager class. However, there's no purpose in the usage of this method, since pygame.Rect items (which represent the values of specific properties) cannot be deleted, that is, every usage of this method will result in an error being raised.

Even if it just serves to raise errors, we implemented the error handling to accurately emulate the pygame.Rect class.

Well, mostly, at least: check the [Error handling in `__getitem__`, `__setitem__` and `__delitem__`](special_methods_part01.test.md#error-handling-in-__getitem__-__setitem__-and-__delitem__) section in this chapter to know why, and also to know why we don't use the function `check_error_raising` to test the error handling of this method. Let's demonstrate the error handling:

For instance, let's use the first rect in the group (since it is a pygame.Rect instance) and the RectsManager instance itself and compare the error messages when we try to delete items.

```python
# get group instance
>>> g1, _ = get_fresh_groups()

>>> rects_man, pygame_rect = g1.rect, g1[0].rect

# trying to delete an existing item of the rect from the first object in
# the group (a pygame rect) causes a segmentation fault, so we skip the
# test below
>>> del pygame_rect[0] # doctest: +SKIP
Traceback (most recent call last):
...
TypeError: Must assign numeric values

# the rectsman tries to emulate the behavior, so a segmentation fault
# happens as well, so we need to skip the test as well
>>> del rects_man[0] # doctest: +SKIP
Traceback (most recent call last):
...
TypeError: Must assign numeric values

```

On a side note, though we designed the RectsManager to emulate pygame.Rect behaviour, we don't think the error message when deleting is helpful at all. Something like "can't delete rect item" would be more appropriate.

Trying to delete a nonexistent index will raise a TypeError as well, pointing out that item deletion is not supported

```python
# try to delete the 5th nonexistent item of the rect from the first
# object in the group
>>> del pygame_rect[5]
Traceback (most recent call last):
...
TypeError: item deletion is not supported

# now the 5th nonexistent item of the RectsManager instance
>>> del rects_man[5]
Traceback (most recent call last):
...
TypeError: item deletion is not supported

```

## Error handling in `__getitem__`, `__setitem__` and `__delitem__`

As pointed out in the sections for the `__getitem__`, `__setitem__` and `__delitem__` methods, we could not use the `check_error_raising` function to test their error raising behaviour. This is so because in some pygame versions (regular `pygame` library), the pygame.Rect class has an irregular behaviour for these three methods: it raises different errors for them depending on the syntax used and the argument received.

For instance, `rect[2.2]` and `rect.__getitem__(2.2)` raise different errors, even though theoretically they should perform the same operation.

Additionally, RectsManager instances delegate the execution of such methods, regardless of the syntax used, to an instance of a pygame.Rect which always uses the syntax sugar version (`rect[2.2]`).

This means that while calling `pygame_rect.__getitem__(2.2)` raises the error associated with the direct method call, calling `rects_man.__getitem__(2.2)` raises the error associated with the syntax sugar call, because internally it delegates to a pygame.Rect instance using such syntax (`rect[2.2]`).

This is why we said the RectsManager "mostly" emulates pygame.Rect behaviour, because it isn't able to emulate this tiny piece of behaviour due to the pygame.Rect inconsistency.

Thus, by using `check_error_raising`, we'd have to pass the method name and would result in mismatched errors between the pygame.Rect instance and RectsManager instance.

This all refers to regular the regular `pygame` library, not the `pygame-ce` version, which should be the one used in this repository by the time you are reading this. As such, all of this might not apply anymore, in which case it should be updated in a future revision.

Finally, I'd just like to add that this inconsistency was also already fixed in the online repository for regular `pygame`. If you use that library your version might already be free from this problem (although this doctests were update to work with `pygame-ce` rather than regular `pygame`.

Also, regardless of all this, the tests used in lieu of the `check_error_raising` function work just as fine whether your pygame version has this problem or not.

This section will most likely be deleted in future revisions of this documentation, and the tests updated to use the `check_error_raising` function.

[Back to table of contents](README.md#table-of-contents)
