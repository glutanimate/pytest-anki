# pytest-anki

pytest-anki is a [pytest](https://docs.pytest.org/) plugin that allows developers to write tests for their [Anki add-ons](https://addon-docs.ankiweb.net/).

At its core lies the `anki_session` fixture that provides add-on authors with the ability to create and control headless Anki sessions to test their add-ons in:

```python
from pytest_anki import AnkiSession

def test_addon_registers_deck(anki_session: AnkiSession):
    my_addon = anki_session.load_addon("my_addon")
    with anki_session.load_profile()
        with anki_session.deck_installed(deck_path) as deck_id:
            assert deck_id in my_addon.deck_ids

```

`anki_session` comes with a comprehensive API that allows developers to programmatically manipulate Anki, set up and reproduce specific configurations, simulate user interactions, and much more.

The goal is to provide add-on authors with a one-stop-shop for their functional testing needs, while also enabling them to QA their add-ons against a battery of different Anki versions, catching incompatibilities as they arise.

![PyPI](https://img.shields.io/pypi/v/pytest-anki) <a title="License: GNU AGPLv3" href="https://github.com/glutanimate/anki-addon-builder/blob/master/LICENSE"><img  src="https://img.shields.io/badge/license-GNU AGPLv3-f37f40.svg"></a>  <a href="https://github.com/psf/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>  [![tests](https://github.com/glutanimate/pytest-anki/actions/workflows/general.yml/badge.svg)](https://github.com/glutanimate/pytest-anki/actions/workflows/general.yml) 

## Disclaimer

### Project State

**Important**: The plugin is currently undergoing a major rewrite and expansion of its feature-set, so the documentation below is very sparse at the moment. I am working on bringing the docs up to speed, but until then, please feel free to check out the inline documentation and also take a look at the plug-in's tests for a number of hopefully helpful examples.

### Platform Support

`pytest-anki` has only been confirmed to work on Linux so far.


## Installation

### Requirements

`pytest-anki` requires Python 3.8+.

### Installing the latest packaged build

```bash
$ pip install pytest-anki
```

or

```bash
$ poetry add --dev pytest-anki
```


## Usage

### Basic Use

In your tests add:
   
```python
from pytest_anki import AnkiSession  # for type checking and completions

@pytest.mark.forked
def test_my_addon(anki_session: AnkiSession):
    # add some tests in here
```

The `anki_session` fixture yields an `AnkiSession` object that gives you access to the following attributes, among others:

```
app {AnkiApp} -- Anki QApplication instance
mw {AnkiQt} -- Anki QMainWindow instance
user {str} -- User profile name (e.g. "User 1")
base {str} -- Path to Anki base directory
```

Additionally, the fixture provides a number of helpful methods and context managers, e.g. for initializing an Anki profile:

```python
@pytest.mark.forked
def test_my_addon(anki_session: AnkiSession):
    with anki_session.profile_loaded():
        assert anki_session.collection
```


### Configuring the Anki Session

You can customize the Anki session context by passing arguments to the `anki_session` fixture using pytest's indirect parametrization, e.g.

```python
import pytest

@pytest.mark.forked
@pytest.mark.parametrize("anki_session", [dict(load_profile=True)], indirect=True)
def test_my_addon(anki_session: AnkiSession):
    # profile / collection already pre-loaded!
    assert anki_session.collection
```

## Additional Notes

### When to use pytest-anki

Running your test in an Anki environment is expensive and introduces an additional layer of confounding factors. If you can `mock` your Anki runtime dependencies away, then that should always be your first tool of choice.

Where `anki_session` comes in handy is further towards the upper levels of the test pyramid, i.e. functional tests, end-to-end tests, and UI tests. Additionally the plugin can provide you with a convenient way to automate testing for incompatibilities with Anki and other add-ons.

### The importance of forking your tests

You might have noticed that most of the examples above use a `@pytest.mark.forked` decorator. This is because, while the plugin does attempt to tear down Anki sessions as cleanly as possible on exit, this process is never quite perfect, especially for add-ons that monkey-patch Anki.

With unforked test runs, factors like that can lead to unexpected behavior, or worse still, your tests crashing. Forking a new subprocess for each test bypasses these limitations, and therefore my advice would be to mark any `anki_session` tests as forked by default.

To do this in batch for an entire test module, you can use the following pytest hook:

```python
def pytest_collection_modifyitems(items):
    for item in items:
        item.add_marker("forked")
```

Future versions of `pytest-anki` will possibly do this by default.

### Automated Testing

`pytest-anki` is designed to work well with continuous integration systems such as GitHub actions. For an example see `pytest-anki`'s own [GitHub workflows](./.github/workflows/).


### Troubleshooting

#### pytest hanging when using xvfb

Especially if you run your tests headlessly with `xvfb`, you might run into cases where pytest will sometimes appear to hang. Oftentimes this is due to blocking non-dismissable prompts that your add-on code might invoke in some scenarios. If you suspect that might be the case, my advice would be to temporarily bypass `xvfb` locally via `pytest --no-xvfb` to show the UI and manually debug the issue.

## Contributing

Contributions are welcome! To set up `pytest-anki` for development, please first make sure you have Python 3.8+ and [poetry](https://python-poetry.org/docs/) installed, then run the following steps:

```
$ git clone https://github.com/glutanimate/pytest-anki.git

$ cd pytest-anki

# Either set up a new Python virtual environment at this stage
# (e.g. using pyenv), or let poetry create the venv for you

$ make install
```

Before submitting any changes, please make sure that `pytest-anki`'s checks and tests pass:

```bash
make check
make lint
make test
```

This project uses `black`, `isort` and `autoflake` to enforce a consistent code style. To auto-format your code you can use:

```bash
make format
```

## License and Credits

*pytest-anki* is

*Copyright © 2019-2021 [Aristotelis P.](https://glutanimate.com/contact/) (Glutanimate) and [contributors](./CONTRIBUTORS)*

*Copyright © 2017-2019 [Michal Krassowski](https://github.com/krassowski/anki_testing)*

*Copyright © 2017-2021 [Ankitects Pty Ltd and contributors](https://github.com/ankitects/)*


All credits for the original idea for creating a context manager to test Anki add-ons with go to Michal. _pytest-anki_ would not exist without his [anki_testing](https://github.com/krassowski/anki_testing) project.

I would also like to extend a heartfelt thanks to [AMBOSS](https://github.com/amboss-mededu/) for their major part in supporting the development of this plugin! Most of the recent feature additions leading up to v1.0.0 of the plugin were implemented as part of my work on the [AMBOSS add-on](https://www.amboss.com/us/anki-amboss).

_pytest-anki_ is free and open-source software. Its source-code is released under the GNU AGPLv3 license, extended by a number of additional terms. For more information please see the [license file](https://github.com/glutanimate/pytest-anki/blob/master/LICENSE) that accompanies this program.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY. Please see the license file for more details.