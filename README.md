# Nodezator

Nodezator is a multi-purpose visual editor to connect Python functions (and callables in general) visually in order to produce flexible parametric behavior/data/applications/snippets.

![nodezator screenshot](https://nodezator.com/images/screenshot.png)

Visit the app's [homepage][] and check this [youtube video] presenting it.

It is a Python desktop app made with [pygame][], by Kennedy Richard Silva Guerra ([me][]), 31, as part of the [Indie Python][] project.

## Installation

This app can be used as a standalone application (that is, an app that doesn't require installation) or can be installed with pip.

If you have Python installed in your system and it has both pygame and numpy available, all you need to do is download this repository and run the `nodezator/__main__.py` file.

If you want to install it, just type the commands below in a terminal with Python 3 available. It will install nodezator and also, if not available yet, pygame and numpy.
 
```bash
python3 -m pip install --upgrade pip
python3 -m pip install --upgrade nodezator
```

If everything went well, after installing, you should be able to start by simply typing `nodezator` or `python3 -m nodezator` in your command line.

That's all, but, if you encounter any problems, contact me with one of the methods described further below in the contact section.

## Usage

Check the app [manual][] to know how to use it. It is also available in-app in the menu **Help > Open manual**

## Nodes for download

Example node packs for download are available in the [nodes gallery][].

Also remember that when loading nodes you might need to install extra modules if the nodes use them.

## Contributing

Pull requests will be welcome in the future. But before doing so, due to the complexity of the app, I'd like to implement some automated GUI tests to ensure everyone's future contributions do not break each other and also publish some guides to ensure contributions follow good principles and the best practices.

This should take a couple of months. Please, consider this time as an opportunity to get acquainted with the app and its source if you desire to contribute in the future. Check the code quality section further below for more info about the source code.

## Issues

Please, include as much information as you can: your operating system, Python version, what was your goal and the steps followed that resulted in the problem as well as the logs from when the error occurred.

If possible, please, also read the Nodezator's [manual][] to ensure you are doing everything as they are supposed to be done. I often find myself wondering if I there is any problem only to later find out that I was doing something wrong myself.

Nevertheless, never hesitate to ask for help.

## Contact

Contact me any time via [Twitter][] or [email][] (kennedy@kennedyrichard.com)

You are also welcome on the Indie Python's [discord server].

## Patreon and donations

Please support Nodezator and other useful apps of the Indie Python project by becoming our patron on [patreon][]. Also check the project's [donation page][] for other donation methods.

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
[Twitter]: https://twitter.com/KennedyRichard
[email]: mailto:kennedy@kennedyrichard.com
[discord server]: https://indiepython.com/discord
[patreon]: https://patreon.com/KennedyRichard
[donation page]: https://indiepython.com/donate
[The Unlicense]: https://unlicense.org/
