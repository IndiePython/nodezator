# Nodezator

Nodezator is a generalist Python node editor. It is a desktop application that works by connecting Python functions (and callables in general) visually in order to produce flexible parametric behavior/data/applications/snippets.

![nodezator screenshot](https://nodezator.com/images/screenshot.png)

Original pomegranate tree image by [AselvadaAna](https://pixabay.com/pt/users/aselvadaana-16928598/) can be found [here](https://pixabay.com/pt/photos/rom%C3%A3-fruta-%C3%A1rvore-folhas-suculento-5609442/).

**What Nodezator IS**: a ready-to-use and versatile Python node-based interface on top of which you can define your own nodes and distribute them so others can download/install and use.

Also, in addition to being able to distribute their nodes using their own means, users can also distribute them as Python libraries via [PyPI][].

The usage of PyPI to distribute your nodes is very advantageous actually, cause it relies solely on the infrastructure already made available for free to all Python users by the [Python Software Foundation](https://www.python.org/psf-landing/), not on me (the developer) or some third-party unknown service/organization. This makes Nodezator a safe bet when it comes to defining and distributing your nodes.

**What Nodezator is NOT**: Nodezator is NOT a framework, which means you can't use it to create your own node-based interface.

> [!WARNING]
> AI developers: Nodezator's UI struggles with the super long processing times required by artificial intelligence workflows. Even so users actually do some AI experimentation from time to time.

Nodezator enables node-based programming with Python and allows its integration with regular text-based programming in Python, by letting users export their node layouts as plain Python code. This means your workflow is never overly dependent on the app itself. We guarantee your freedom!

Creating nodes is very straightforward: all you need to define a node is a function, since Nodezator automatically converts functions into nodes. For instance, the function below...

```python
def get_circle_area(radius:float=0.0):
    return math.pi * (radius ** 2)

main_callable = get_circle_area
```

...is automatically turned into the following node:

![node image](https://nodezator.com/images/get_circle_area_node.png)

You can store these functions/node definitions anywhere you want in your disk and once you launch Nodezator just provide the path so Nodezator can load them. The only requirement is that you organize these nodes definitions in separate files and store then in a folder (more about that further ahead in another section).

You can actually turn **any** callable into a node very easily: classes, methods, etc. All callables available in the Python ecosystem can be turned into a node (even the ones defined in C, for instance).

This means you can turn callables from existing Python libraries into nodes very easily! That is, any callable from all hundreds of thousands of projects in the Python Package Index ([PyPI][]) can be virtually be turned into a node already!

For instance, this is all you need to turn [numpy.save()][] into a node:

```python
from numpy import save

main_callable = save

third_party_import_text = 'from numpy import save'
```

With just those 03 lines of code you generate this node:

![numpy save node](https://nodezator.com/images/numpy_save.png)

There's also a [youtube video][] presenting Nodezator:

[![thumb of youtube video](https://img.youtube.com/vi/GlQJvuU7Z_8/hqdefault.jpg)](https://www.youtube.com/watch?v=GlQJvuU7Z_8)

Nodezator is made with pure Python on top of the [pygame-ce][] library (and a bit of the excellent [numpy][] library as well), by [Kennedy Richard Silva Guerra][] (born in 1990), as part of the [Indie Python][] project.

> [!NOTE]
> Despite being maintained mostly by a single person, Nodezator is a serious and active project that gets a couple of large releases every year.

We recommend Nodezator for **intermediate Python users**. Or, in case you are not a programmer, have an intermediate Python user next to you so that person can help you set up a no-code/low-code workflow for you.

Nodezator can already be used in production and supports a vast variety of workflows. It still has a long way to go, though. So, please, be patient and also consider supporting it: https://indiepython.com/donate

After you finish reading this README file, you may also want to visit Nodezator's homepage: https://nodezator.com


## Features

On top of making it very easy to define nodes, Nodezator comes packed full of useful features for both Python programmers and other professionals that (likely with the help of a fellow programmer) can setup a no-code/low-code workflow.

### Work effortlessly with other libraries

As we said before, Nodezator allows you to convert callables from third-party libraries with minimal effort. Here are just a few screenshots showing the usage of Nodezator with different libraries.

Here's is a simple graph showing Nodezator usage with the [Pillow](https://python-pillow.org/) library.

![Pillow demonstration](https://nodezator.com/images/nodezator_pillow_demo.png)

Original strawberry basket image by [NickyPe](https://pixabay.com/pt/users/nickype-10327513/) can be found [here](https://pixabay.com/pt/photos/morangos-fruta-refei%c3%a7%c3%a3o-vermelho-4255928/).

And here's another one showing the usage of [matplotlib](https://matplotlib.org/) to generate charts.

![Matplotlib demonstration](https://nodezator.com/images/nodezator_matplotlib_demo.png)

And a more complex graph showing usage of the [CadQuery](https://github.com/CadQuery/cadquery) library to generate a 3D model along with a 2D preview shown in the graph itself:

![CadQuery demonstration](https://nodezator.com/images/nodezator_cadquery_demo.png)

The CadQuery graph above in particular uses only nodes available by default in Nodezator (you can tell cause nodes available by default either do not have a header or have a black one, whereas custom nodes have colored headers). That is, we didn't even need to create custom nodes to achieve those results.


### Nodezator is Python

On top of being able to define nodes directly from Python functions/callables, any graph in Nodezator can be directly exported back as Python code. This means you are never overly dependent on the app.

If you ever create nodes and graphs in another app, it will be much harder to port all the codebase you built over the time to plain Python or another Python API. In Nodezator, this problem is much reduced cause it requires much less changes in your code in order for it to be loaded in the app and you can convert graphs you create on it back to Python scripts.

Check the example at the top of this `README` document again, for instance. The only change required was to add a simple line: `main_callable = ...`.

If you were to use other apps you'd probably have to export a class and subclass it in order to define a node, increasing the complexity of you code and its reliance on external interfaces and tech. Most other apps don't even offer the ability to export your graphs back as Python code.

As an example of Nodezator's Python exporting capabilities, here's a simple graph followed by the Python code exported from it:

![Graph to be exported as Python](https://nodezator.com/images/graph_to_be_exported_as_python.png)

```python
### main function

def temp_2024_08_30_11_11_12():
    """Execute script version of Python visual graph."""

    _1_number_b = 10
    _0_number_a = 10
    _2_output = _0_number_a + _1_number_b
    _3_output = print(*(_2_output, ), sep=' ', end='\n', flush=False, )


if __name__ == '__main__':
    temp_2024_08_30_11_11_12()
```

Nodezator can export graphs of any size and complexity as Python code, including graphs containing user-defined nodes.

Simply put, Nodezator is just a visual, node-based representation of Python.


### Socket proximity detection

Having to click exactly over a socket to drag a new connection out of it and on top of that having to drop such new connection exactly on top of another socket are both repetitive tasks that are difficult to do right in one quick motion. Often, people loose precious time trying to ensure the mouse is exactly over the desired socket, specially considering how often those tasks are performed in any graph edition session.

Because of that, Nodezator features socket proximity detection to assist the user when establishing or replacing existing connection. The user doesn't need to click exactly over a socket to drag a new connection out of it anymore. Dropping the new connection exactly over the other socket isn't necessary either. As long as the mouse is close enough, these actions can be carried over effortlessly. Here you can see it in action:

![Socket detection demonstration](https://nodezator.com/images/socket_detection_hands_and_eyes.gif)

The user can even customize how close the mouse needs to be for the socket to be detected and for the connection to be recognized!

On top of that, there's no need to worry about being precise with your mouse motion either, cause the connection is only confirmed if the user releases the mouse. This way you can freely move the mouse near a desired socket with no fear of it being accidentally connected to another socket next to it:

![Socket detection near many sockets](https://nodezator.com/images/socket_detection_near_many_sockets.gif)

Users can even choose the detection graphics used. From the most serious and distraction-free to the most fun and silly ones:

![Socket detection using assisting line](https://nodezator.com/images/socket_detection_assisting_line.gif)

![Socket detection using baseball elements and eyes](https://nodezator.com/images/socket_detection_baseball_elements_and_eyes.gif)


### Additional Python-related tools

Being a node-based representation of Python, Nodezator includes a few extra features that help you access Python features in a node-based interface.


#### Variable-kind parameters (`*args` and `**kwargs`)

Nodezator offers the ability to define nodes with variable-kind parameters, that is, `*args` and `**kwargs`, parameters that can receive as arguments as needed. All you need is for the callabe you create/provide to have such parameters (of course, you can name these parameters whatever you want, as long as they have the `*` or `**` to indicate their kind).

This results in nodes with placeholder sockets that accept as many connections as needed. They do so by creating an additional socket on the node for each connection received. Like so:

![Connecting sockets to a variable-kind parameters](https://nodezator.com/images/connecting_to_variable_kind_parameter.gif)

If the received argument is an iterable, you can even unpack it by right-clicking the socket receiving the argument and selecting the corresponding option in the menu that pops up:

![Unpacking argument received in a variable-kind parameter](https://nodezator.com/images/unpacking_received_arg.gif)

Dictionaries/mappings can be dict-unpacked in the same way:

![Dict-unpacking argument received in a variable-kind parameter](https://nodezator.com/images/dict_unpacking_received_arg.gif)


#### Specialized widgets

Although Nodezator still has much to implement when it comes to widget support, it already offers widgets with many useful features for Pythonistas.

Take the entry used for holding and editing integers and floats, for instance: in addition to allowing the user to click and drag the mouse in both directions to increment or decrement the value and writing simple arithmetic expressions (features that are present in other node editors, like Blender's), also allow users to write expressions using some Python built-in functions and some functions from standard library modules.

![Features of entry used to hold integers/floats](https://nodezator.com/images/features_of_int_float_entry.gif)


#### Functional style programming

In addition to representing a call to a specific function/callable, a node can also represent a reference to the function/callable itself. This unlocks powerful capabilities like the usage of higher-order functions and other functional programming tools/concepts.

All you need to do for a node to reference its callable (instead of a call to it), is to right-click the node and change its mode to `callable` in the menu that pops up, like this:

![Making a node reference its callable](https://nodezator.com/images/making_node_reference_the_callable.gif)

As explained on [Python's Functional Programming HOWTO](https://docs.python.org/3/howto/functional.html) and programming with Python in a functional style offers many advantages, both theoretical and practical:

- Formal provability
- Modularity
- Composability
- Ease of debugging and testing

For instance, the `pow` node, which represents Python's built-in function [pow](https://docs.python.org/3/library/functions.html#pow), can be used to calculate the power of several numbers at once instead of just a single number, when used in callable mode, in conjunction with the `map` node, which represents the higher-order built-in function [map](https://docs.python.org/3/library/functions.html#map). Like in the graph below where we produce and display a list of numbers to the power of 2 from a given range of integers:

![Using the pow node in callable mode](https://nodezator.com/images/pow_callable_mode_demo.png)

Again, Nodezator is just a node-based visual representation of Python, so it is only natural that we also offer such capability.


## How nodes are created, loaded and distributed

Nodezator already comes with a lot of useful general nodes representing common Python operations, built-ins and callables from the standard library. You can easily spot them cause they either have a black header or no header at all, like demonstrated in the image below:

![some default nodes](https://nodezator.com/images/some_default_nodes.png)

Original cherries image by [congerdesign](https://pixabay.com/pt/users/congerdesign-509903/) can be found [here](https://pixabay.com/pt/photos/cerejas-fruta-doce-de-cereja-1503977/).

However, users are encouraged to define their own nodes for their specific purposes, or use existing nodes from other users. Nodes defined by users have colored headers (green, blue, etc.), like the one below:

![A user-defined node](https://nodezator.com/images/node.png)

Nodes are created from Python scripts organized within folders that we call **node packs**. You can create a node pack folder **anywhere you want in your disk**. Under the hood, Nodezator treats it as a package in some contexts, so you can name that folder whatever you like, as long as it is a Python identifier. That is, it must start with a letter or underscore and contain only letters, digits and underscores.

In other words, you **create nodes by writing Python functions/callables using your preferred text editor or IDE** and only then you **launch Nodezator in order to load them as nodes**, so you can create, edit and execute graphs.

Since node packs are just folders containing your Python functions/callables, you can:

- keep them local to your own machine;
- share them with other people by your own means (in a pen drive or over the internet, etc.);
- upload them to [PyPI][] (the Python Package Index) as Python packages so anyone can install them with the `pip` command;

This chapter of the manual teaches you how to define your own node packs: [defining your first node][].

Node scripts are meant to be completely independent from one another, that is, they shouldn't import resources from one another. However, when necesary, you can make common resources available to them so they can import such resources.

In case you need to do that, all you have to do to **share common resources among your nodes** is to create an additional library/package and place it in your `site-packages` directory. Then, in each node script that needs such resources, you can simply import from that library/package.

The process is also explained in the first chapter of the manual we linked earlier. The chapters following it are also useful to learn additional ways to define nodes and access more features.

To learn how to load node packs, you can check this chapter: [loading nodes][].

Finally, to learn all the different ways by which you can distribute node packs, you can check this chapter: [distributing your nodes][].


## Finding and letting people find nodes for download

Once you distributed your nodes, you may want a place wherein to let people know they exist! Or maybe you yourself is looking for nodes to download.

You can do all this on the [nodes gallery][] website. There you can search node packs by name, author and tags.

To have a link to your node pack added to the nodes gallery/database, upload it somewhere people can download/install it from, as described in the manual's chapter about [distributing your nodes][], then submit the relevant info about your node pack in this [node pack submission form][]. Alternatively, you can also submit a pull request to the [nodes gallery repository][] on github following the instructions on the README.md file.

You can also [email][] me if you need any help.

Remember that before loading nodes you download from the web you might need to install extra modules if the nodes use them.


## Installation/usage
 
To launch and use Nodezator you can either install it with `pip` or you can just download the source and launch Nodezator as a standalone/portable application (that is, without installing it).


### Installing Nodezator with pip

If you want to install it, just execute the command below. It will install nodezator and also, if not available yet, [pygame-ce][] and [numpy][].
 
```
pip install --upgrade nodezator
```

If everything goes well, after installing you should be able to launch the app by typing `nodezator` or `python -m nodezator` in your command line (or `python3 -m nodezator` depending on you system).


### Using Nodezator as a standalone/portable app (without installing it)

If you want to use Nodezator without installing it, you'll need 02 things:

- to have Python installed in your system along with the [pygame-ce][] and [numpy][] libraries;
- to download Nodezator's source (the `nodezator` folder in the top level of this repository).

Then, to launch the app, you just need to go to the location where you put the `nodezator` folder containing the source (not inside it), open the command line and run `python -m nodezator` or `python3 -m nodezator`, depending on your system.


## User Manual

Check the user [manual][] to know how to use Nodezator.

The manual is also available inside the app in the menu **Help > Open manual**.

The in-app version is always the most accurate, since it is updated first, whereas the web version is exported from it. Nonetheless, effort is made to always keep both of them up to date and in sync.


## Contributing

Everyone is welcome to suggest and contribute changes.

If the proposed change is small enough, you can submit your pull request for analysis right away and it will be answered ASAP.

More complex pull requests will also be welcome in the future, but due to the complexity of the app, I will first need to implement some automated GUI tests to ensure everyone's future contributions do not break each other.


## Issues


### Urgent/critical issues

If you find a bug that...

- causes Nodezator to crash;
- representing something malfunctioning or not working at all;

...then, please, use [github issues][] to submit an issue as soon as possible.

Please, include as much information as you can:

- your operating system;
- your Python version;
- what was your goal;
- the steps that resulted in the problem;
- screenshots/videos, if applicable.

If possible, also read the Nodezator's [manual][] to ensure you are doing everything as they are supposed to be done. I often find myself wondering if I there is any problem only to later find out that I was doing something wrong myself.

Nevertheless, never hesitate to ask for help, even if you don't have much info about the problem or don't have any technical expertise.


### Minor issues

If however, the problem is not as serious/urgent, that is, it doesn't cause Nodezator to crash or malfunction, then, please, open a discussion on [github discussions][] instead. There's a dedicated category for this kind of problem called "Minor issue".

It doesn't mean your issue is any less important. It is just that in Nodezator and other Indie Python repos we use [github issues][] for things that crash the app or otherwise prevent the user from doing something that is supposed to be available (stuff that cause crashes or malfunctioning). When such a critical issue appears, any other work is paused and all attention is given to that issue so that it can be fixed ASAP.

This measure is taken for the benefit of the users: by doing things this way, whenever you have an urgent/critical issue, it won't compete for space with other less urgent matters. We'll be able to promptly schedule time to solve the issue.

Minor issues, suggestions of improvements, feature requests, feedback about bad experiences, etc. are all important, but they don't have the same urgency as something that crashes the app or causes it to malfunction. This is why we use [github discussions][] for the less urgent stuff. They'll be tended to all the same, just not with the same urgency.

Of course, [github discussions][] is used for many other important stuff as well, as we'll see in the next section.


## Discussions/forum

Consider [github discussions][] as the official online forum for Nodezator.

It is used for many things like announcements to the community, to list planned/requested features, to communicate and discuss current work, etc.

If you have...

- feedback;
- suggestions;
- ideas;
- concerns;
- questions;
- constructive criticism;
- minor issues that don't cause the app to crash or malfunction;

...you are encouraged to post there.


## Contact

Contact me any time via [Twitter/X][] or [email][].

You are also welcome on the Indie Python's [discord server][].


## Patreon and donations

Please, support Nodezator and other useful apps of the Indie Python project by becoming our patron on [patreon][]. You can also make recurrent donations using [github sponsors][], [liberapay][] or [Ko-fi][].

Both [github sponsors][] and [Ko-fi][] also accept one-time donations.

Any amount is welcome and helps. Check the project's [donation page][] for all donation methods available.


## License

Nodezator's source is dedicated to the public domain with [The Unlicense][].

The `nodezator_icons` font used in the app for its icons was created by me and is dedicated to the public domain with a [CC0 license][]. All other fonts are not mine and are licensed under the [Open Font License][].

The logos/images listed below, featured in Nodezator's splash screen (and sometimes in other spots in the app), are all mine:

- the Kennedy Richard "KR" logo;
- the Indie Python project logo;
- the Nodezator logo;
- the robot, called Zenith Green, Nodezator's mascot.

Please, don't use them for questionable ends. Use them only as references to the stuff they represent.


## Code quality

Nodezator is the result of more than 04 years of development. Some of the code was reviewed and refactored many times and is not only carefully designed but also commented in detail, as if you were on a field/school trip inside the code. A few unit tests are available as well. Also, whenever possible, I kept the line count of the modules close to 500 lines.

Other parts of the code, however, specially the most recent ones, are not so refined. Bear this in mind as you browse the code for the first time. Expect such parts of the code to be refactored and properly commented in the future.

Also, other parts of the code, despite being carefully designed, might be redesigned in the future, since now that the app is published, it should evolve as we find problems and contribute to improve the app. In other words, some of the design may change in the future, so bear in mind that the software is still evolving.


[Kennedy Richard Silva Guerra]: https://kennedyrichard.com
[PyPI]: https://pypi.org
[numpy.save()]: https://numpy.org/doc/stable/reference/generated/numpy.save.html
[youtube video]: https://www.youtube.com/watch?v=GlQJvuU7Z_8
[pygame-ce]: https://pyga.me
[numpy]: https://numpy.org
[Indie Python]: https://indiepython.com

[manual]: https://manual.nodezator.com

[Twitter/X]: https://x.com/KennedyRichard
[email]: mailto:kennedy@kennedyrichard.com
[discord server]: https://indiepython.com/discord

[patreon]: https://patreon.com/KennedyRichard
[github sponsors]: https://github.com/sponsors/KennedyRichard
[liberapay]: https://liberapay.com/KennedyRichard
[Ko-fi]: https://ko-fi.com/kennedyrichard
[donation page]: https://indiepython.com/donate

[defining your first node]: https://manual.nodezator.com/ch-defining-your-first-node.html
[loading nodes]: https://manual.nodezator.com/ch-loading-nodes.html
[distributing your nodes]: https://manual.nodezator.com/ch-distributing-nodes.html
[nodes gallery]: https://gallery.nodezator.com

[node pack submission form]: https://docs.google.com/forms/d/e/1FAIpQLSd1XceOnzEeaBZcpkkXEFiAVO_5YUbd43sieQUekh1PZ8dm5A/viewform?usp=sf_link
[nodes gallery repository]: https://github.com/IndiePython/gallery.nodezator.com

[github issues]: https://github.com/IndiePython/nodezator/issues
[github discussions]: https://github.com/IndiePython/nodezator/discussions

[The Unlicense]: https://unlicense.org/
[Open Font License]: https://en.wikipedia.org/wiki/SIL_Open_Font_License
[CC0 license]: https://creativecommons.org/publicdomain/zero/1.0/

