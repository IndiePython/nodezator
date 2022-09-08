# Nodezator

Nodezator is a multi-purpose visual node editor for the Python programming language. It works by connecting Python functions (and callables in general) visually in order to produce flexible parametric behavior/data/applications/snippets.

![nodezator screenshot](https://nodezator.com/images/screenshot.png)

Nodezator also allows you to export your node layouts as plain Python code, so your workflow is never overly dependent on the app itself. We guarantee your freedom!

Moreover, creating nodes is very straightforward: all you need to define a node is a function, since Nodezator automatically converts functions into nodes. For instance, the function below is automatically turned into the following node:

```python
def get_circle_area(radius:float=0.0):
    return math.pi * (radius ** 2)

main_callable = get_circle_area
```

![node image](https://nodezator.com/images/get_circle_area_node.png)

Visit the app's [homepage][] and check this [youtube video][] presenting it.

It is a Python desktop app made with [pygame][], by Kennedy Richard Silva Guerra ([me][]), 31, as part of the [Indie Python][] project.


## Installation

This app can be used as a standalone application (that is, an app that doesn't require installation) or can be installed with pip.

If you have Python installed in your system and it has both pygame and numpy available, all you need to do is download this repository and inside the repository folder run the `python -m nodezator` command.

If you want to install it, just execute the command below. It will install nodezator and also, if not available yet, pygame and numpy.
 
```bash
pip install nodezator
```

If everything went well, after installing, you should be able to start by simply typing `nodezator` or `python3 -m nodezator` in your command line.

That's all, but, if you encounter any problems, contact me with one of the methods described further below in the contact section.


## Usage

Check the app [manual][] to know how to use it. It is also available in-app in the menu **Help > Open manual**. The in-app version is always the most accurate, since it is updated first, whereas the web-version is exported from it. Nonetheless, effort is made to always keep both of them up to date and in sync.


## Finding and sharing nodes for download

Node packs for download are available in the [nodes gallery][]. For now it is only a humble static website, but soon it will be turned into a google for nodes, where you'll be able to search nodes by name, author and tags.

Remember that when loading nodes you might need to install extra modules if the nodes use them.

If you want to publish your nodes for download as well, create a new repository on your github profile and upload your node pack there, then ask for your node pack to be included on the [nodes gallery][] via [email][].


## Contributing

Everyone is welcome to suggest and contribute changes.

If the proposed change is small enough, you can submit your pull request for analysis right away and it will be answered ASAP.

More complex pull requests will also be welcome in the future, but due to the complexity of the app, I will first need to implement some automated GUI tests to ensure everyone's future contributions do not break each other.


## Nodezator online forum

If you have:

  - suggestions
  - ideas
  - concerns
  - questions
  - constructive criticism

Please consider [github discussions][] for Nodezator as the official online forum for the app. Just comment an existing discussion there or create a new one.


## Issues

Please, include as much information as you can: your operating system, Python version, what was your goal and the steps followed that resulted in the problem as well as the logs from when the error occurred.

If possible, please, also read the Nodezator's [manual][] to ensure you are doing everything as they are supposed to be done. I often find myself wondering if I there is any problem only to later find out that I was doing something wrong myself.

Nevertheless, never hesitate to ask for help.


## Contact

Contact me any time via [Twitter][] or [email][].

You are also welcome on the Indie Python's [discord server].


## Patreon and donations

Please support Nodezator and other useful apps of the Indie Python project by becoming our patron on [patreon][] or [liberapay][]. Also check the project's [donation page][] for other donation methods.

## License

Nodezator is dedicated to the public domain with [The Unlicense][].

## Code quality

Nodezator is the result of more than 04 years of development. Some of the code was reviewed and refactored many times and is not only carefully designed but also commented in detail, as if you were on a field/school trip inside the code. A few unit tests are available as well. Also, whenever possible, I kept the line count of the modules close to 500 lines.

Other parts of the code, however, specially the most recent ones, are not so refined. Bear this in mind as you browse the code for the first time. Expect such parts of the code to be refactored and properly commented in the near future.

Also, other parts of the code, despite being carefully designed, might be redesigned in the future, since now that the app is published, it should evolve as we find problems and contribute to improve the app. In other words, some of the design may change in the future, so bear in mind that the software is still evolving.


[homepage]: https://nodezator.com
[youtube video]: https://www.youtube.com/watch?v=GlQJvuU7Z_8
[pygame]: https://pygame.org
[me]: https://kennedyrichard.com
[Indie Python]: https://indiepython.com
[manual]: https://manual.nodezator.com
[nodes gallery]: https://gallery.nodezator.com
[github discussions]: https://github.com/IndiePython/nodezator/discussions
[Twitter]: https://twitter.com/KennedyRichard
[email]: mailto:kennedy@kennedyrichard.com
[discord server]: https://indiepython.com/discord
[patreon]: https://patreon.com/KennedyRichard
[liberapay]: https://liberapay.com/KennedyRichard
[donation page]: https://indiepython.com/donate
[The Unlicense]: https://unlicense.org/
