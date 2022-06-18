Glossary
========


500 lines max (ideal line count)
********************************

Just a convention I use of trying my best to constrain the line count of modules to close to 500 lines. Whenever a module exceeds such line count by too much, I usually split said module into two. In my opinion this has a number of positive outcomes:

- reading and refactoring the source code is easier because you can divide the effort into quick incursions into small modules instead of having to tackling large modules;
- having to split a big module into small modules or into a subpackage forces you to think about the structure of the code, leading to a better understanding of such code;

Keep in mind that some modules do exceed this line count, but usually not by much. Maybe not more than 600-700 lines. There may also be some rare cases where even such numbers are exceeded. When such happens, it is usually in modules which I didn't properly refactor yet. It could also mean that the code is so tightly coupled that splitting it would make it somehow more difficult to understand, but I personally don't remember to have ever encountered such case, even though I acknowledge the possibility.

Also, I learned that there is book called "500 lines or less". I didn't come up with the mentioned principle because of the book. I also didn't read such book, even though it has an interesting premise which makes me want to read it in the future. However, I might have read the book's title somewhere and have it stuck in my mind, which might have ultimately influenced my coming up with such principle.

Nonetheless, the point is that 500 lines is a very manageable number of lines in a module, and going above it may turn maintenance of the module unnecessarily more difficult. Such maintenance, of course, includes development, bug fixing, refactoring, knowledge management and, above all else, understanding.


Class extension
***************

A class extension is just a class that exists for the sole purpose of being inherited by another one, and no other class other than that one. In this sense, the class extension is just the continuation of the code in the original class importing it. It is different from a mixin class in which it isn't inherited by multiple classes, but only a single one.


Factor
******

We usually use this word to refer to an integer which, when multiplied by a value in the unit interval (and rounded to an integer with the built-in "round"), results in a value which is said to be the full form of that value.

Another property of the "factor" is that it represents the maximum value the value can achieve in its full form.

Related words/expressions: "Unit interval", "Full value"


free_up_memory()
****************

See "Memory management".


Freeing memory
**************

See "Memory management".


User log(ger)
*************

The user logger is an object used to log messages to be presented to the user, to help the user better understand what is happening while the application is being used.

In addition to help log the messages, the user logger also stores them in itself, since it is a collections.deque subclass. The messages are stored in the form of lines of text. This collection of lines is what we call the "user log".

We use a deque, storing the text as individual lines, due to a constraint in the text viewer implementation that makes it memory costing to display large texts many consecutive times. There's a ready design awaiting implementation that may solve this issue, in which case we'll be able to store the log as a string. No guarantees are made, though, since the text viewer isn't a feature per se, but rather a convenience made to display small to medium-sized text, not to become a full-fledged text display widget (see the "Software Development/Design Decisions" definition).

As it must be apparent by now, the difference between this logger and the usual ones from the logging standard library module is that it is not meant to be kept in files to help identify issues, but is used solely for communication with the user (though such communication does include issues as well) during the session.

Every time a file is opened, the user logger is cleared.


Function for injection
**********************

As the name implies, a function which exists for the sole-purpose of being used as a method in a class. Probably using code similar to the one below (where func_a is the function for injection, defined in another module):


### code begins

from a_module import func_a

Class SomeCustomClass:
    
    func_a = func_a

### code ends

Just like a method defined in the body of a class definition, the first argument of the function (maybe the only one) is called 'self'.


Full value
**********

When a value is present in its full form, rather than its equivalent in the unit value. For instance, in some systems, the value of color channels can go from 0 to 255 and in others, it is in the unit interval, that is, from 0.0 to 1.0.

So, for example, we could say that [255, 255, 255] represents the color white, with full values, while [1, 1, 1] or [1.0, 1.0, 1.0] also represents the color white, but with values in the unit interval, or unit values.

Related words/expressions: "Unit interval", "Unit value"


Full form
*********

Same as full value.


Full color
**********

A color whose values are in their full form. For instance, (255, 255, 255), represents white in RGB full form/value;

Related words/expressions: "Unit interval", "Unit value"


GUD methods/operations
**********************

See 'Loop holder methods/operations'


Python for data
***************

Python literals are simple yet powerful. Working with it is easy and straightforward and allow us to work with tuples and non-empty sets as well as used keys other than strings in dictionaries. Therefore, whenever I need to work with data, Python literals are my favorite format; I save such files are .pyl instead of .py, to differentiate them from regular Python scripts.


Loop holder
***********

Any Python object which has operations named 'get_input', 'update' and 'draw', which are executed once per loop. A single loop holder is always controlling the application at any given time and the application as a whole is managed by having multiple loop holders swap control of the application between themselves many times from the moment it is started to the moment the user closes it.

The operations are responsible for:

- get_input : read input from the user and react to it;
- update    : behaviour unrelated to input;
- draw      : drawing the visuals of the application;

Thus, each loop holder has its own unique way of getting/reading input, behaving and drawing.


Loop holder methods/operations
******************************

The typical operations performed by loop holders: get_input(), update() and draw(), also known as GUD methods/operations. Check the definition of loop holder.


Lowercase preference
********************

Another convention I use of whenever possible, use lowercase characters to name things. This is because using uppercase characters brings the extra confusion of not only having to remember the name of stuff, but also whether the are capitalized or not.

The only thing for which I use uppercase characters is in the name of classes (for instance: MySpecialClass) and in the name of constants (for instance: A_SPECIAL_COLOR).

Most other things use lowercase characters, like names of files and folders.


Memory management
*****************

By memory management, in this package, we mean practices to help keep the memory usage low and free memory used by objects which we won't need anymore.

As it is known, Python garbage-collects objects when there are no references to them anymore, or when they only reference each other, but are not referenced in the execution context.

However, when we use third-party libraries of even local code written by ourselves, part of what we're doing may perhaps be obscured by layers of abstractions or simply be code too low for us to be able to understand, reach or yet code that we don't want to touch because is out of our scope and we don't want to focus our development efforts there.

In such cases, there is no clear way to guarantee an attribute we delete will cause its value to be garbage-collected. When toying with Python in the interactive interpreter I could easily see the usage of memory by a list I kept alive in a variable, through the system's task manager. After deleting that variable, I could immediately see the memory usage be reduced since the list was garbage-collected.

However, an instance of a custom list subclass I kept alive in an attribute, full of pygame.Surface instances, were not letting go of the memory used when I deleted that attribute. I searched for other places where the list could be referenced but didn't find such references in my code. And yet, the memory was clearly being used by something in my code, even though I deleted the attribute holding the list.

Even when I replaced that list altogether by a new one, identical to the original one, in that attribute, the memory usage in the task manager still indicated that somehow the memory used by the first list was still in use, now added by the memory used by the new identical list.

This is when I tried something new: instead of deleting the list, I cleared it (using the list.clear() method); suddenly, the memory taken by the contents of the list was clearly garbage-collected, or at least seemed so, since the memory usage was reduced, as I could see in the task manager.

This is why a large part of our memory manage measures, to keep memory usage low, is made of operations to clear collections. The impact of such operations was not taken for granted, though, but were actually tested, monitored in the task manager as they reduced memory usage and also, in some cases, prevented memory usage to increase past some value.

However, such tests were made with the purpose of improving the memory usage and preventing problems for the users, specially with the purpose of having everything going smooth for the users upon releasing of the software. Such improvement were already documented, refactored and pushed.

Such tests shall be remade in the future, though, this time with the purpose of extensively documenting them so further measures can be taken as needed and our memory management approach can continue to evolve as we better understand its inner workings.

The cleanup operations implemented are performed whenever a new session of the application is started (for instance, when a file is loaded), but also even while still editing the current file loaded in some cases when many objects must be created for some operation to complete.

For instance, both the text text viewer have a collection holding text surfaces that are created every time they are used. Such collections is cleared every time it is exited.

On the other hand, the graphman/node/surfs.py module has a dictionary that holds surfaces for the body of some nodes. Such dictionary is cleared only when the user loads another file (or when it reloads the current one).

Of course, when the application is closed all the memory is freed, but this isn't relevant here, as it is done automatically by Python and doesn't need our intervention.

The memory freeing operations performed adopt the same name, in the form of a callable called 'free_up_memory()'. The ones used to free up memory at the beginning of a session (loading a file, starting an app session without a file) are all called in the same function, which is imported from the same top level module called memoryman.py; such function calls other free_up_memory() operations so free up memory is specific spots throughout the package.


Mouse action protocol
*********************

Just some arbitrary conventions used when dealing with mouse events (MOUSEBUTTONDOWN, MOUSEBUTTONUP and MOUSEMOTION). The convention include the name of methods used to perform actions and the signature used:

- names of the methods:
    - on_mouse_click()   (when the mouse left button is pressed);
    - on_mouse_release() (when the mouse left button is released);
    - on_mouse_motion()  (when the mouse moves);

- signature: all methods have a single parameter called "event", which receives a pygame.event.Event instance.

As can be seen in the name of the methods, we tried to used names used in Javascript just for familiarity, but this is a quite loose protocol, at least for the moment, so don't expect a 100% compliance all the time. At least not until I revise and update this protocol and the codebase.


Software Development/Design Decisions
*************************************

Though we are more fond of principles than rules, there are a set of rules, laws and principles we try to follow so that our development decisions and efforts are always made with clear goals or at least more or less the same direction in mind.

Below we list some of them:

- 1) Laws, rules, principles: everything pointed out in the "Code Simplicity" book, by Kanat-Alexander;

- 2) Principle: Python design choices are top priority (or whichever language you are using);
    that is, since we are designing/developing software for Python users, the closer we can get of using its design principles and the closer we can mimick its design choices, the more natural the usage of our software will fell for incoming Python users.

    on the other hand, though, we must tend to our user needs and other things like usability as well, so there may be circumnstances were deviating from Python design is the right thing to do, so keep an eye out for this kind of stuff and listen to your users;

- 3) Principle: define what your software is/does and develop towards those things;
    everything you develop towards what your software is/does are features; everything else is, at most, conveniences, though they might eventually evolve into features (see next principle);

- 4) Principle: evolution/flexibility;
    the world is dynamic and both you and your userbase are creative beings, so new usages and points of views emerge, probably more often than not, so pay attention to such things and adjust what your software is/does over time, so it can evolve/be flexible.

- 5) Principle: a piece of software is not implemented until:

  - it works;
  - it is well commented and documented;
  - it is refactored;

  Below we explaing a bit more, using basic concepts:

  - understanding;

    This one is heavily influenced by Kanat-Alexander's ideas, that is, that good programmers are those who understand what they are doing; thus, understanding must be at the center of your development efforts, though it may often come a bit later in lots of cases;

  - the implementation itself (the raw code);

    If you don't have something implemented and working, you have nothing to work with; we sure can theorize by software not written, but in lots of cases it is difficult or not accurate enough to evaluate software which doesn't exist or work;

    even if you don't know how to implement something you can start by implementing the parts you understand, and see how they can fit together to form a complete solution;

  - registered understanding (comments and documentation);

    The understanding you have about a piece of software is not guaranteed until you register it somewhere; comment your code properly and/or discuss its design/merits somewhere; make the purpose of your piece of code very evident in the body of the script (comment the code, document it);

    well-written code is great, but reading code is time consuming, even well-written one; it is quicker to read well-placed comments around your code that explains what each section of it does; what about the possibility of they being wrong? yes, it is a true possibility, but only for those who consider comments and documentation to not be part of the code;

    if you develop with the mindset that the comments and documentation are integral parts of the code, the comments and docs in your scripts will increase in value and save you time;

    don't consider anything implemented if it is not well commented and documented; of course, again, this is a principle, not a rule, but you find out we follow it in most cases here;

    furthermore, let's say you developed something and implemented very quickly, without refactoring it; it will be very difficult to understand once you come back to it some weeks/months later; however, if you at least used comments to highlight/explain the different sections of the code, your initial effort to develop it can be quickly restored and you'll be able to refactor and improve it and finish documenting it;

    in summary, write in the body of your code what it is supposed to do, what each part of it means; if such information is there, you can do almost anything with it once you have time;
    
    but if your code lacks information, you may very well have to spend invaluable time trying to figure out exactly what you were trying to do; even if your code is well-writter, someone who never visited it will have to spend time reading and analysing your software, following the execution flow of the data, taking minutes to reach conclusions that could be reached in seconds by reading comments/documentation in human language;

  - refactored code;

    Just like with comments and documentation, don't consider anything implemented until it is refactored;

    this is not just for convenience and for the code to look better; refactoring your code will help you understand it better and improve its value and quality;

    that is, after refactoring a function, for instance, it may be split into different functions, some of those parts are more modular and may be reused in other parts of you code, or it may become more flexible and be able to handle more data or more different types of data then you originally designed it to handle;

    such transformations may look complex, but when you nurture the habit of refactoring, no, when you make it a requirement of your development practice, you'll see that such things start to occur more often and very naturally in some cases;

  - interdependency of concepts/practices above;

    all the concepts/practices discussed above intermingle to form the software design/development; they help each other and are constantly revisited during development of the same piece of code;

    commenting each meaningful block of the code you write will help you understand it better; once you understand it better, it will be user to come up with better ways to refactor it;

    sometimes you don't even understand how you'll develop a piece of software, you only have the problem and pieces of what may become a solution, but by putting those things together and striving to understand and document them (even in the form of simple sketches or pseudocode), a full solution may start to take form and eventually you'll have a full design in your head of even already implemented code in your hands;

Todo comments
*************

Python comments which start with todo words.


Todo words
**********

The words 'TODO', 'FIXME' and 'XXX'. They are called todo words because they are used in code comments to indicate a task to be done; it seems there's several conventions as to the precise meaning of each word. Here, TODO is the most used one and simply represent a task to be done; 'FIXME' means the task is related to a bug and usually also carries the additional meaning of urgency; 'XXX' is also a task which is less urgent than the other two and is usually postponed in favor of the other ones;


Unit interval
*************

The interval including 0.0, 1.0 and all the floats in-between, though the integers 0 and 1 may also be used (see also the wikipedia definition: https://en.wikipedia.org/wiki/Unit_interval). So, when we say a value is in the unit interval, we say that it it can be any value from 0.0 to 1.0.

Related words/expressions: "Unit value", "Full value"


Unit value
**********

Any value in the unit interval.

Related words/expressions: "Unit interval", "Full value"


Unit form
*********

Same as unit value.

Related words/expressions: "Unit value"


Unit color
**********

A color whose values are in the unit interval. For instance, (1.0, 1.0, 1.0) or (1, 1, 1) represent white in RGB unit form/interval, so sometimes we call it unit color or unit rgb color.

Related words/expressions: "Unit interval", "Full color"
