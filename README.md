# Nodezator

Nodezator is a multi-purpose visual node editor for the Python programming language. It is a desktop application that works by connecting Python functions (and callables in general) visually in order to produce flexible parametric behavior/data/applications/snippets.

![nodezator screenshot](https://nodezator.com/images/screenshot.png)

Nodezator enables node-based programming with Python and allows its integration with regular text-based programming in Python, by letting users export their node layouts as plain Python code. This means your workflow is never overly dependent on the app itself. We guarantee your freedom!

Creating nodes is very straightforward: all you need to define a node is a function, since Nodezator automatically converts functions into nodes. For instance, the function below...

```python
def get_circle_area(radius:float=0.0):
    return math.pi * (radius ** 2)

main_callable = get_circle_area
```

...is automatically turned into the following node:

![node image](https://nodezator.com/images/get_circle_area_node.png)

You can actually turn **any** callable into a node very easily: classes, methods, etc. All callables available in the Python ecosystem can be turned into a node (even the ones defined in C, for instance).

This means you can turn callables from existing Python libraries into nodes very easily! That is, the callables in all hundreds of thousands of projects in the Python Package Index ([PyPI][]) can be easily used as nodes already!

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

Nodezator is made with [pygame][], by [Kennedy Richard Silva Guerra][] (born in 1990), as part of the [Indie Python][] project.

After you finish reading this README file, you may also want to visit Nodezator's [homepage][]. 


## Installation/usage
 
To launch and use Nodezator you can either install it with `pip` or you can just download the source and launch Nodezator as a standalone/portable application (that is, without installing it).


### Installing Nodezator with pip

If you want to install it, just execute the command below. It will install nodezator and also, if not available yet, [pygame][] and [numpy][].
 
```
pip install nodezator
```

If everything goes well, after installing you should be able to launch the app by typing `nodezator` or `python -m nodezator` in your command line (or `python3 -m nodezator` depending on you system).


### Using Nodezator as a standalone/portable app (without installing it)

If you want to use Nodezator without installing it, you'll need 02 things:

- to have Python installed in your system along with the [pygame][] and [numpy][] libraries;
- to download Nodezator's source (the `nodezator` folder in the top level of this repository).

Then, to launch the app, you just need to go to the location where you put the `nodezator` folder containing the source (not inside it), open the command line and run `python -m nodezator` or `python3 -m nodezator`, depending on your system.


## User Manual

Check the user [manual][] to know how to use Nodezator.

The manual is also available inside the app in the menu **Help > Open manual**.

The in-app version is always the most accurate, since it is updated first, whereas the web version is exported from it. Nonetheless, effort is made to always keep both of them up to date and in sync.


## How nodes are created, loaded and shared

Nodezator already comes with a lot of useful general nodes representing common Python operations, built-ins and callables from the standard library.

However, users are encouraged to define their own nodes for their specific purposes, or use existing nodes from other users.

Nodes are created and organized within folders that we call **node packs**.

Since node packs are just folders containing your Python functions/callables, you can:

- keep them local to your own machine;
- share them with other people in a pen drive or over the internet;
- upload them to [PyPI][] (the Python Package Index) as Python packages so anyone can install them with the `pip` command;

This chapter of the manual shows how to define your own node packs: [defining your first node][]. The chapters following it are also useful to learn additional ways to define nodes and access more features.

To learn how to load node packs, you can check this chapter: [loading nodes][].

Finally, to learn how to distribute node packs, you can check this chapter: [distributing your nodes][].


## Finding and sharing nodes for download

Node packs for download are available in the [nodes gallery][]. There you can search node packs by name, author and tags.

To have your node pack added to the nodes gallery/database, upload it somewhere people can download/install it from, as described in the manual's chapter about [distributing your nodes][], then submit the relevant info about your node pack in this [node pack submission form][]. Alternatively, you can also submit a pull request to the [nodes gallery repository][] on github following the instructions on the README.md file.

You can also [email][] me if you need any help.

Remember that before loading nodes you download from the web you might need to install extra modules if the nodes use them.


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

Nevertheless, never hesitate to ask for help, regardless of how much info you have about the problem or your technical expertise.

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

Contact me any time via [Twitter][] or [email][].

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


[homepage]: https://nodezator.com
[Kennedy Richard Silva Guerra]: https://kennedyrichard.com
[PyPI]: https://pypi.org
[numpy.save()]: https://numpy.org/doc/stable/reference/generated/numpy.save.html
[youtube video]: https://www.youtube.com/watch?v=GlQJvuU7Z_8
[pygame]: https://pygame.org
[numpy]: https://numpy.org
[Indie Python]: https://indiepython.com

[manual]: https://manual.nodezator.com

[Twitter]: https://twitter.com/KennedyRichard
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

