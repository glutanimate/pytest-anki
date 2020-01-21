## pytest-anki

[![](https://github.com/glutanimate/pytest-anki/workflows/tests/badge.svg)](https://github.com/glutanimate/pytest-anki/actions?query=workflow%3Atests)

> a simple pytest plugin for testing Anki add-ons

This project is a rewrite of [krassowski/anki_testing](https://github.com/glutanimate/pytest-anki/blob/master/.github/workflows/tests.yml) as a pytest plugin, with a number of added convenience features and adjustments for more recent Anki releases.


### Disclaimer

#### Project State

This is still very much a work-in-progress. Neither the API, nor the implementation are set in stone.

#### Platform Support

`pytest-anki` has only been tested on Linux so far.

### Installation

1. [Set up an Anki development environment](https://github.com/dae/anki/blob/master/README.development) and add your local Anki source folder to your `PYTHONPATH` (so that both the `anki` and `aqt` packages can be resolved by Python, see [run_tests.sh](tools/run_tests.sh) for an example).

2. Install `pytest-anki` into your testing environment:

    ```bash
    pip install --upgrade git+https://github.com/glutanimate/pytest-anki.git
    ```

### Usage

#### Basic Use

In your tests add:
   
```python
def test_my_addon(anki_session):
    # add some tests in here
```

The `anki_session` fixture yields an `AnkiSession` object that gives you access to the following attributes:

```
app {AnkiApp} -- Anki QApplication instance
mw {AnkiQt} -- Anki QMainWindow instance
user {str} -- User profile name (e.g. "User 1")
base {str} -- Path to Anki base directory
```

This allows you to perform actions like loading or unloading Anki profiles, e.g.:

```python
def test_my_addon(anki_session):
    anki_session.mw.loadProfile()
    assert anki_session.mw.col is not None
```

Finally, assuming that your tests are located in a `tests` folder at the root of your project, you can then run your tests with:

```bash
python3 -m pytest tests
```

(also see the [sample script under tools](./tools/run_tests.sh))

#### Configuring the Anki Session

You can customize the Anki session context with a series of arguments that can be passed to the `anki_session` fixture using indirect parametrization, e.g.

```python
@pytest.mark.parametrize("anki_session", [dict(profile_name="foo")], indirect=True)
def test_my_addon(anki_session):
    assert anki_session.user == "foo"
```

A full list of supported arguments follows below:

```
Keyword Arguments:
    base_path {str} -- Path to write Anki base folder to
                        (default: {tempfile.gettempdir()})
    base_name {str} -- Base folder name (default: {"anki_base"})
    profile_name {str} -- User profile name (default: {"__Temporary Test User__"})
    keep_profile {bool} -- Whether to preserve profile at context exit
                            (default: {False})
    load_profile {bool} -- Whether to return an Anki session with the user profile
                            and collection fully preloaded (default: {False})
    lang {str} -- Language to use for the user profile (default: {"en_US"})
```

#### Other Features

`pytest-anki` also provides a convenient context manager called `profile_loaded` that simplifies testing your add-ons at different profile load states:

```python
from pytest_anki import AnkiSession  # used here for type annotations
from pytest_anki import profile_loaded

def test_my_addon(anki_session: AnkiSession):
    assert anki_session.mw.col is None  # profile / collection not yet loaded

    with profile_loaded(anki_session.mw):
        assert anki_session.mw.col is not None  # loaded
    
    assert anki_session.mw.col is None  # safely unloaded again
```

Additional helper functions and context managers are also available. Please refer to the source code for the latest feature-set.

#### Other Notes

Running your test in an Anki environment is expensive and introduces an additional layer of confounding factors, so I would recommend avoiding the `anki_session` fixture as much as possible, `mock`ing away Anki runtime dependencies where you can. The `anki_session` fixture is in many ways more suited towards end-to-end testing rather more fundamental tests in the test pyramid.

If you do use `anki_session`, I would highly recommend running your tests in separate subprocesses using `pytest-forked`. Because of the way Anki works (e.g. in terms of monkey-patching, etc.) exiting out of the `anki_session` fixture is never quite clean, and so you run the risk of state persisting across to your next tests. This could lead to unexpected behavior, or worse still, your tests crashing. Forking a new subprocess for each test bypasses these limitations.

Running a test in a separate subprocess is as easy as decorating it with `pytest.mark.forked`:

```python
@pytest.mark.forked
def test_my_addon(anki_session):
    # add some tests in here
```

### Automated Testing

`pytest-anki` is designed to work well with continuous integration systems such as GitHub actions. For an example see `pytest-anki`'s own [GitHub workflows](./.github/workflows/tests.yml).


### Troubleshooting

#### pytest hanging when using xvfb

Especially if you run your tests headlessly with `xvfb`, you might run into cases where pytest will sometimes appear to hang. Oftentimes this is due to blocking non-dismissable prompts that Anki your add-on code might invoke in some scenarios. If you suspect that might be the case, my advice would be to temporarily bypass `xvfb` locally via `pytest --no-xvfb` to debug the issue.

### License and Credits

*pytest-anki* is

*Copyright © [Ankitects Pty Ltd and contributors](https://github.com/ankitects/)*

*Copyright © 2017-2019 [Michal Krassowski](https://github.com/krassowski/anki_testing) (krassowski)*

*Copyright © 2019-2020 [Aristotelis P.](https://glutanimate.com/) (glutanimate)*

All credits for the original idea for this project go to Michal. _pytest-anki_ would not exist without his work.

_pytest-anki_ is free and open-source software. Its source-code is released under the GNU AGPLv3 license, extended by a number of additional terms. For more information please see the [license file](https://github.com/glutanimate/pytest-anki/blob/master/LICENSE) that accompanies this program.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY. Please see the license file for more details.