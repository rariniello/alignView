# alignView

> GUI for aiding laser alignment with machine vision cameras.

[![License][license]][license-url]

A GUI to help with laser alignment by providing live display and analysis on laser beam images.

![alignView Interface](header.png)

## Installation

Windows users are supplied self-contained builds of specView on the [latest releases](https://github.com/rariniello/alignView/releases/latest) page.

## Usage example

Examples incoming...

_For more examples and usage, please refer to the [Wiki][wiki]._

## Development setup

Clone the repository

```sh
git clone <repo> 
```

Navigate into the repository's directory

```sh
cd alignView
```

Create the virtual environment

```sh
conda env create -f requirements.yml
```

Activate the virtual environment

```sh
conda activate alignView
```

Test that the application is starting properly

```sh
python alignView.py
```

### Install drivers on windows

Install [pylon](https://www.baslerweb.com/pylon).

## Latest Version and Changelogs

The latest version along with release notes can always be found on the project's [releases](https://github.com/rariniello/alignView/releases) page.

## Meta

Robert Ariniello

Distributed under the GNU GPL v3.0 license. See ``LICENSE`` for more information.

[https://github.com/rariniello/](https://github.com/rariniello/)

## Contributing

1. Fork it (<https://github.com/rariniello/alignView/fork>)
2. Create your feature branch (`git checkout -b feature/fooBar`)
3. Commit your changes (`git commit -am 'Add some fooBar'`)
4. Push to the branch (`git push origin feature/fooBar`)
5. Create a new Pull Request

<!-- Markdown link & img dfn's -->
[license]: https://img.shields.io/github/license/rariniello/alignView
[license-url]: https://github.com/rariniello/alignView/blob/main/LICENSE
[wiki]: https://github.com/rariniello/alignView/wiki
