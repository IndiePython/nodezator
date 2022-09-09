"""Documentation/tests for the FlatListDict class

FlatListDict
    dictionary with a list of all values, nested or not.

Development note: in the future such list might be
replaced by a "view-like" version of it


### Introduction

The FlatListDict class was designed as a dict that keeps
track of all values, nested or not, within multiple
dictionaries inside it. Such values are all kept in a
list, which represents a flat version of the entire
nested value structure in the dict, hence the name of the
class.

As we know from the Zen of Python text, "flat is better
than nested". However, for those cases where you
couldn't come up with a good abstraction using a flat
structure to represent your nested one, you can use this
class which does the job of keeping a list with all
the dictionary values for you, nested or not.

Actually, even when working with nested values in multiple
dictionaries, you might not necessarily need this class.
You can use the flatten_mapping_values function, which
returns a generator expression of all values (nested or
not) from a dictionary. This class actually rely heavily
on said function.

This class, thus, is only need when you need to keep track
of the changes in the nested values of a dictionary at all
times. However, there is a limitation in this "tracking"
feature, namely that in some cases you have to execute
its "update" method after some operations to make sure the
changes are reflected in the list of values. This will be
discussed further ahead.

This class was first created because I had this dictionary
whose values were nested in different levels. Such values
were custom objects which I needed to keep nested in
different levels because they were also managed depending
on their levels. However, in order to draw then on the
screen, I need references to all of them every loop.
And what's more, I wouldn't be enough to just reference
them in a list, because some of those objects could be
replace at any time or there could be objects added or
removed.

I didn't want to execute the flatten_mapping_values
function every loop to get references to all of them,
because though the values could change at any time,
such changes only happened at the user command. That is,
the function would be needlessly executed every loop.

Thus I implemented this dictionary subclass. It has the
distinct feature of keeping a list of all of its values
in the "flat_values" attribute, which is actually a
read-only property.

Also bear in mind that this class was created to be used
with nested dicts with really low item count, probably
hardly exceeding ten values. Like the one I described in
the previous paragraphs whose values I needed to draw. This
is not to say this class can't be used for instances with
higher or much higher item count. I just want to state the
fact so you know you may try optimizing it even further if
you need.


### Limitation

The FlatListDict has a limitation, though: it doesn't
keep track of changes made in its nested items directly.
However, you can easily overcome this limitation by
executing the flat list dict "update" method without
arguments after this kind of transformation.

This is because the flat list dict is cleared and
repopulated again as a side effect of its "update" method,
so all nested values are checked. This behaviour is good
enough for our needs, but research may be done in the
future to further optimize this behaviour or somehow come
up with a way to keep track of changes in the nested
dictionaries inside the FlatListDict.

One possibility I'm considering is turning all the nested
dictionaries into FlatListDict instances which could store
a reference to its "parent" dictionary so it could
report changes to it.

Or maybe instead I could use another custom class (maybe
called "NestedTrackedDict") dict which would just be like
normal dictionaries, but report any changes to a dict
reference stored in a "tracker_dict" attribute. And any
new mapping stored anywhere in the nested structure
would automatically be turned into a nested tracked dict.

Those are just possibilities. Turning every dict in the
nested structure in an instance of a known mapping class
would somehow be a pity, though, since one advantage of
the flatten_mapping_values function used so much in the
FlatListDict is precisely the fact that it works with
any mapping. It doesn't mean this would be less worthy.
It is still somehow an idea I may implement someday.

Additionally such nested flat list dicts structure (or the
nested tracked dicts) would need much more time to study and
develop. This is fine, but not necessary nor urgent right
now, since the current solution suffices.


### Ordering

Since some internal operations depend on the
flatten_nested_mapping function, which retrieves values
from dicts in the order different nested dicts instances
see fit, there's no way to guarantee the ordering the
"flat_values" list will assume in the end.

Thus, use the "sorted" builtin function or list.sort method
of the flat values list whenever the ordering is important.
In the docstests here, for instance, we made heavy use of
it, so that we could properly compare lists with one
another.


### Using the Class

Let's load the class and the utility function it uses.
You don't need to import the utility function, but I
wanted to show it in action, since the class uses it many
times in its implementation. As you'll hear many times, the
function may actually be more useful than the class itself
in many cases. We'll also load the collections.abc.Mapping
abstract base class to help with testing.

>>> ### standard library import
>>> from collections.abc import Mapping

>>> ### loading the class and the utility function
>>> from .main import FlatListDict
>>> from ...behaviour import flatten_mapping_values

Below we have names of games mapped to their respective
genre (fighting, actions, etc.), in a variable called
fav_game_by_genre. The names represent some of my
favorite games by genre, as far I could remember at least.

Note: games are such rich works of art/products
that categorizing them may actually hinder our ability
to truly appreciate them or limit our view to what is
the norm, devaluing the creativity of the game's
creators. I advise using game categories for the sole
purpose of organization or cataloging, never to
evaluate their true worth.

>>> favorite_games = {
...   "fighting": "King of Fighters 97",
...   "action": "Just Cause 2",
...   "rpg": {
...     "JRPG": "Chrono Trigger",
...     "Action RPG": "The Elder Scrolls: Skyrim"
...   },
...   "platformer" : {
...     "2D": "Super Mario World",
...     "3D": "Toy Story 2 (PS1)",
...   }
... }

As you could see, the dictionary has genres and subgenres
further nested in some keys like "rpg" and "platformer".

Now let's say I simply want a list with all the games
in that dictionary. I don't need to create a FlatListDict
instance just for that: the flatten_mapping_values
function can do that for us. In fact, even the class uses
that function multiple times in its source.

The function returns a generator object which can be
used to retrieve all the values in a dictionary, no matter
the nesting level. Just remember that the order of values
returned by the generator depend on the specific
implementation of the dicts nested in the structure and
thus is virtually unpredictable.

>>> ### since we don't know the order in which the items
>>> ### are returned by the flatten_mapping_values
>>> ### generator, we create a sorted list version of the
>>> ### items
>>> actual = sorted(flatten_mapping_values(favorite_games))

>>> ### we then we define another list with the items
>>> ### we expect to find in the "actual" list
>>> expected = sorted([
...   "Chrono Trigger",
...   "Just Cause 2",
...   "King of Fighters 97",
...   "Super Mario World",
...   "The Elder Scrolls: Skyrim",
...   "Toy Story 2 (PS1)"
... ])

>>> ### naturally, the actual list must be equal to the
>>> ### "expected" one we put together
>>> actual == expected
True

However, it might be the case that you need to know at
all times when new games are added to the dictionary
or old ones are removed/replaced and it is not feasible
or desirable to use the flatten_mapping_values function
every time.

You simply need to know right away when the items change.
That is, whenever any of the values change or is deleted
or the dict have values added to it, you want a updated
list of all values, the names of games. This use case is
the reason for the existence of the FlatListDict class.

Here we have the class in action:

>>> fl_dict = FlatListDict(favorite_games)

>>> ### notice how the flat_values attribute (actually
>>> ### a read-only property) contains the same expected
>>> ### values (we use a sorted copy of the "flat_values"
>>> ### list in the comparison, since we can't predict its
>>> ### order)
>>> sorted(fl_dict.flat_values) == expected
True

The flat_values, as a read-only property, cannot be
reassigned or deleted. This works as a poka-yoke mechanism
to prevent unintentional misuse:

>>> fl_dict.flat_values = list() # doctest: +ELLIPSIS
Traceback (most recent call last):
...
AttributeError: can\'t set attribute 'flat_values'

>>> del fl_dict.flat_values # doctest: +ELLIPSIS
Traceback (most recent call last):
...
AttributeError: can\'t delete attribute 'flat_values'


### Utility function

Before we proceed, we define an utility function below to
help eliminate repetitive tasks when presenting doctests
in the following sections.

>>> def check_expected_items(expected_items, fl_dict):
...     '''Return whether flat list has expected results.
...
...     ### Parameters:
...
...     expected_items (iterable)
...         contains the items we expect to find in the
...         "flat_values" attribute of the flat values
...         list instance.
...     fl_dict (FlatValuesList instance)
...         contains list in "flat_values" attribute which
...         whose items must be the same as the items from
...         the expected_items argument.
... 
...     Both lists have sorted copies created to use for
...     the comparison, since there's no way to guarantee
...     whether the order will be the same.
...     '''
...     ### get a sorted copy of the expected items of the
...     ### flat_values list
...     sorted_expected = sorted(expected_items)
... 
...     ### get a sorted copy of the contents of the
...     ### flat_values list
...     sorted_actual_values = sorted(fl_dict.flat_values)
... 
...     ### return the result of the equality comparison
...     ### between the expected_values list and the
...     ### sorted copy of the flat_values list
...     return sorted_expected == sorted_actual_values


### Automatic Effects of Changing the FlatListDict instance

As expected, the usage of any method which changes the
dictionary will also automatically change the flat_values
list too, for your convenience. However, the changes must
affect the dictionary directly, that is, one of its items.

That is, if you change a nested dictionary, instead
of the FlatListDict instance directly, the change in the
nested dictionary won't automatically be accounted for in
the "flat_values" list.

To achieve this effect, you'll need to execute the "update"
method of the FlatListDict instance without argument so the
flat list is updated (this works as a side-effect of the
"update" method).

We'll now visit each method separately.


## Creating/changing dictionary items with "__setitem__":

>>> ### setting new item
>>> fl_dict["racing"] = "Need for Speed Underground 2"
>>> ### changing existing item
>>> fl_dict["fighting"] = "Marvel VS Capcom"

>>> ### now let's see if the changes made produced the
>>> ### expected result

>>> ## we produce a list with the expected items
>>> expected_items = [
...   "Chrono Trigger",
...   "Just Cause 2",
...   "Marvel VS Capcom",
...   "Need for Speed Underground 2",
...   "Super Mario World",
...   "The Elder Scrolls: Skyrim",
...   "Toy Story 2 (PS1)"
... ]

>>> ## and pass it to the function we defined to automate
>>> ## the testing process
>>> check_expected_items(expected_items, fl_dict)
True

>>> ## Also as expected, this works even with nested
>>> ## values:
>>> fl_dict["strategy"] = {
...   "turn-based": "Battle for Wesnoth",
...   "real time strategy": "Age of Empires II"
... }

>>> ### again, let's see if the changes made produced the
>>> ### expected result

>>> ## first we produce a list with the expected items
>>> expected_result = [
...   "Age of Empires II",
...   "Battle for Wesnoth",
...   "Chrono Trigger",
...   "Just Cause 2",
...   "Marvel VS Capcom",
...   "Need for Speed Underground 2",
...   "Super Mario World",
...   "The Elder Scrolls: Skyrim",
...   "Toy Story 2 (PS1)"
... ]

>>> ## and then compare them for equality
>>> check_expected_items(expected_result, fl_dict)
True

Notice we didn't need to use the "update" method of the
fl_dict instance in the examples above, since we changed
the instance directly, that is, we executed the method
of the instance fl_dict.__setitem__ (via the
"fl_dict[key] = value" syntax).

However, you must beware of hte limitation of the
FlatListDict class presented in previous sections: there's
currently no way to keep track of changes made directly
into the nested dictionaries of the FlatListDict, so
changes made directly to them won't be reflected in the
flat_values list automatically:

>>> ### changing the dict present in the strategy key won't
>>> ### automatically make the flat_values list in the
>>> ### FlatListDict instance aware of the change
>>> fl_dict["strategy"]["real time strategy"] = "Warcraft 3"
>>> "Warcraft 3" in fl_dict.flat_values
False

Instead, to make the FlatListDict aware of the change,
execute the update method (it is ok to execute it without
arguments), since a side-effect of this method is that the
flat_values list gets cleared and repopulated with the
appropriate items:

>>> fl_dict.update()
>>> "Warcraft 3" in fl_dict.flat_values
True

This is valid for all methods which change the dictionary,
including the ones in the following section, thus this
specific information won't be repeated anymore. Just
be aware of this.


## Deleting dictionary items with "del" (__delitem__):

>>> ### let us try deleting the item corresponding to
>>> ### the "platformer" key
>>> del fl_dict["platformer"]

>>> ### this should have eliminated two games listed
>>> ### as platformers (super mario and toy story) in the
>>> ### flat_values list, because the value associated with
>>> ### "platformer" is a dict containing those two values;
>>> ### let's check:
>>> expected_result = [ # no Toy Story nor Mario anymore
...   "Warcraft 3",
...   "Battle for Wesnoth",
...   "Chrono Trigger",
...   "Just Cause 2",
...   "Marvel VS Capcom",
...   "Need for Speed Underground 2",
...   "The Elder Scrolls: Skyrim"
... ]
>>> check_expected_items(expected_result, fl_dict)
True


## Updating the dictionary with "update":

Besides the already discussed side-effect of clearing and
repopulating the list in the "flat_values" property, the
"update" method works just the same as dict.update.

>>> ### let's now update our FlatListDict with the
>>> ### following dictionary
>>> more_games = {
...   "isometric": "Transistor",
...   "mobile": {
...      "free": {
...         "puzzle": "Angry Birds"
...      },
...      "paid": {
...         "puzzle-platform": "Limbo"
...      }
...   },
...  "card games" : {
...     "traditional": "Solitaire",
...     "trading cards": "Yu-Gi-Oh!",
...   }
... }
>>> fl_dict.update(more_games)

>>> ### the "more_games" dict has even more nesting levels
>>> ### (the "mobile" key, for instance, points to a
>>> ### dictionary whose keys, "free" and "paid" point to
>>> ### yet other dictionaries);
>>> ### however, it is no problem for the FlatListDict,
>>> ### it can keep track of all values in its "flat_values"
>>> ### list with no problems (as long as the update is
>>> ### performed on the fl_dict instance itself);
>>> ### let's check if it now has the expected values:
>>> expected_values = [
...   "Warcraft 3",
...   "Battle for Wesnoth",
...   "Chrono Trigger",
...   "Just Cause 2",
...   "Marvel VS Capcom",
...   "Need for Speed Underground 2",
...   "The Elder Scrolls: Skyrim",
...   "Transistor",
...   "Angry Birds",
...   "Limbo",
...   "Solitaire",
...   "Yu-Gi-Oh!"
... ]
>>> check_expected_items(expected_values, fl_dict)
True


## Removing dictionary item with "pop":

>>> ### now let's use "pop" to remove the item associated
>>> ### with the "rpg" key; the return value must be
>>> ### equal to the expected one
>>> return_value = fl_dict.pop("rpg")
>>> expected = {
...   "JRPG": "Chrono Trigger",
...   "Action RPG": "The Elder Scrolls: Skyrim"
... }
>>> return_value == expected
True


>>> ### by design, the FlatListDict must have also removed
>>> ### the nested values within the "rpg" key from the
>>> ### flat_values list (Chrono Trigger and Skyrim);
>>> ### let's check
>>> expected_values = [ # no Chrono Trigger nor Skyrim
...   "Warcraft 3",
...   "Battle for Wesnoth",
...   "Just Cause 2",
...   "Marvel VS Capcom",
...   "Need for Speed Underground 2",
...   "Transistor",
...   "Angry Birds",
...   "Limbo",
...   "Solitaire",
...   "Yu-Gi-Oh!"
... ]
>>> check_expected_items(expected_values, fl_dict)
True

>>> ### the FlatListDict also works as expected for keys
>>> ### which don't exist
>>> fl_dict.pop("abcd") # 'abcd' key doesn't exist
Traceback (most recent call last):
KeyError: 'abcd'
>>> fl_dict.pop("abcd", "doesn't exist")
"doesn't exist"


## Removing dictionary item with "popitem":

>>> ### let's test "popitem" now; we'll remove 5 items and
>>> ### check whether the quantity of values removed
>>> ### from the flat_values list corresponds to the
>>> ### quantity of values removed from the dict in
>>> ### that item (regardless of whether the values were
>>> ### nested or not); we do this because there's no safe
>>> ### way to determine which item the "popitem" method
>>> ### will remove, but we know there's only 4 keys in the
>>> ### fl_dict right now which don't contain nested
>>> ### dictionaries; thus we ensure that at least
>>> ### one nested dict will be removed (so we can see if
>>> ### the corresponding quantity of values will be
>>> ### removed from the flat_values list);
>>> for _ in range(5):
...      
...      ## retrieve initial length
...      initial_len = len(fl_dict.flat_values)
...      
...      ## pop item, storing value
...      _, value = fl_dict.popitem()
...      
...      ## get the number of values removed, taking into
...      ## account whether it is a single value or multiple
...      ## values nested within a mapping
...      
...      if isinstance(value, Mapping):
...          # get generator with flattened values
...          flattened_values = flatten_mapping_values(value)
... 
...          # the generator must be turned into a list
...          # before measuring its length
...          no_of_removed = len(list(flattened_values))
...      
...      else: no_of_removed = 1
...      
...      ## determine whether the final length is equal to
...      ## the difference between the initial length and
...      ## the number of removed values, printing the
...      ## result of the equality test
...      
...      final_len = len(fl_dict.flat_values)
...      print(initial_len - no_of_removed == final_len)
True
True
True
True
True

In other words, as can be seen above, the same amount of
values contained in the removed item (no matter in how many
levels they are nested or not) is also removed from the
flat_values list.


## Removing all dictionary items with "clear":

>>> ### in the previous sections, we removed 5 items from
>>> ### the fl_dict instance, which means we still have 2
>>> ### items left in the dict
>>> len(fl_dict)
2

>>> ### the "flat_values" list also naturally has items,
>>> ### though we can't predict for sure the length (since
>>> ### we didn't know which items were remove previouly
>>> ### and thus how many values they contained)
>>> len(fl_dict.flat_values) > 0
True

>>> ### let's see if clearing the dict will also clear the
>>> ### flat_values list
>>> fl_dict.clear()
>>> len(fl_dict), len(fl_dict.flat_values)
(0, 0)

Yes, as expected, it does.


## Retrieving dictionary item with "setdefault":

As we know, dict.setdefault method works just like dict.get,
but has the side-effect of setting the default value into
the dictionary when the key doesn't exists (besides
returning it as dict.get does). Since it is a method which
can change the dict contents, the FlatListDict properly
updates the flat_values list when the absence of the key
causes the dictionary to set the new key/value pair as a
new item.

>>> ### since the fl_dict is empty, the key used doesn't
>>> ### exist yet and will be created on the spot (the
>>> ### default value is also returned, as we can see)
>>> fl_dict.setdefault("city management", "Cities Skylines")
'Cities Skylines'

>>> ### the flat_values list must be updated accordingly
>>> len(fl_dict.flat_values)
1
>>> fl_dict.flat_values[0] == 'Cities Skylines'
True

>>> ### using nested dictionaries as default values should
>>> ### have the desired effect too when the key doesn't
>>> ### exist; let's create one and use it with "setdefault"
>>> n_dict = {
...    "shooting game": "Metal Slug",
...    "retro": {
...       "1980": "Pac Man",
...       "1981": "Donkey Kong"
...    }
... }
>>> ### notice we caught the return value of "setdefault" on
>>> ### the "_" variable since we can't predict the order
>>> ### in which the contents of n_dict would be displayed
>>> _ = fl_dict.setdefault("arcade", n_dict)

>>> ### without further ado, let's see if the values within
>>> ### the nested dicts added are present along with the
>>> ### existing ones, as should be expected:
>>> expected_values = [
...   "Cities Skylines",
...   "Metal Slug",
...   "Pac Man",
...   "Donkey Kong"
... ]
>>> check_expected_items(expected_values, fl_dict)
True

>>> ### of course, when the key already exists, no change
>>> ### takes place in the FlatListDict; the value of the
>>> ### key is just returned, just like would happen with
>>> ### dict.setdefault;
>>> fl_dict.setdefault("city management")
'Cities Skylines'


### Automatic Effect of Creating New FlatListDict instance
### using the "fromkeys" class method

Creating new dictionaries using the "fromkeys" class method
works just like in dict.fromkeys:

>>> ### let's define an iterable with names of family
>>> ### members
>>> family = [
...   "Amanda",
...   "Renata",
...   "Jackeline",
...   "Ember",
...   "Nathalie",
... ]
>>> ### now, using "fromkeys" you can have a FlatListDict
>>> ### instance for monthly expenditures per family member,
>>> ### and even categorize expenditures for each member
>>> monthly_exp = FlatListDict.fromkeys(family, 0)

>>> ### as expected, there's a 0 (zero) for each family
>>> ### member listed
>>> monthly_exp.flat_values
[0, 0, 0, 0, 0]

>>> ### just as an example of how the FlatListDict can
>>> ### be used, we can assign numbers to each key, and/or
>>> ### nested other dictionaries with keys representing
>>> ### categories of expenditures
>>> monthly_exp["Renata"] = 2000.0
>>> monthly_exp["Nathalie"] = {
...    "tuition": 1000.0,
...    "rent": 2000.0
... }
>>> sum(monthly_exp.flat_values)
5000.0


### copy operations

Before performing the related doctests, let's import the
copy operations from the "copy" standard library module.

>>> from copy import copy, deepcopy


## regular copying operation

The regular copy operation can be performed by using both
FlatListDict.copy method or by passing the FlatListDict
instance to the copy.copy function. Let's begin by
demonstrating the usage of the "copy" method.

>>> expenditures_copy = monthly_exp.copy()
>>> expenditures_copy == monthly_exp
True
>>> expenditures_copy is monthly_exp
False
>>> expenditures_copy["Nathalie"] == monthly_exp["Nathalie"]
True
>>> expenditures_copy["Nathalie"] is monthly_exp["Nathalie"]
True

>>> ### let's perform some changes in the regular copy...
>>> expenditures_copy["Anna"] = 1000.0
>>> expenditures_copy["Nathalie"]["car repair"] = 1200.0
>>> expenditures_copy.update() # since the change above
>>> # wasn't made directly in the expenditures_copy
>>> # FlatListDict instance, but in the normal dict inside
>>> # its "Nathalie" key, we must use FlatListDict.update

>>> monthly_exp.update() # not required, but done anyway so
>>> # there's no doubt that there are no changes

>>> ### as expected, the first change will not affect the
>>> ### original, since they are different objects, but the
>>> ### second change will, since the objects inside both
>>> ### instances are the same:
>>> sum(monthly_exp.flat_values) # only 1200 higher
6200.0
>>> sum(expenditures_copy.flat_values) # 2200 higher
7200.0

Using copy.copy works the same way. Actually, to be precise,
the FlatListDict.copy method uses the same implementation
as copy.copy. The copy.copy function calls the __copy__
method, which was also used by FlatListDict.copy in the
previous example.

>>> another_copy = copy(monthly_exp)

>>> another_copy == monthly_exp
True
>>> another_copy is monthly_exp
False

>>> another_copy["Nathalie"] == monthly_exp["Nathalie"]
True
>>> another_copy["Nathalie"] is monthly_exp["Nathalie"]
True


## deep copying operation

Use copy.deepcopy to get a new deep copy. Though equal, no
object inside the FlatListDict deep copy is the same
anymore.

>>> ### get deep copy
>>> exp_deepcopy = deepcopy(monthly_exp)

>>> ### perform equality and identiy comparisons

>>> exp_deepcopy == monthly_exp
True
>>> exp_deepcopy is monthly_exp
False

>>> exp_deepcopy["Nathalie"] == monthly_exp["Nathalie"]
True
>>> exp_deepcopy["Nathalie"] is monthly_exp["Nathalie"]
False

>>> ### thus, changing an object inside the deep copy should
>>> ### not affect the original instance
>>> exp_deepcopy["Nathalie"]["health"] = 1500.0
>>> exp_deepcopy.update()
>>> monthly_exp.update() # not required, but done anyway so
>>> # there's no doubt that there are no changes
>>> sum(exp_deepcopy.flat_values)
7700.0

>>> ### to ensure the original object wasn't affected,
>>> ### let's see if the sum of expenditures is still
>>> ### 6200.0
>>> sum(monthly_exp.flat_values)
6200.0
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
