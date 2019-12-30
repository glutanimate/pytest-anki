## pytest-anki

[![](https://github.com/glutanimate/pytest-anki/workflows/tests/badge.svg)](https://github.com/glutanimate/pytest-anki/actions?query=workflow%3Atests)

> a simple pytest plugin for testing Anki add-ons

This is a fork of [krassowski/anki_testing](https://github.com/glutanimate/pytest-anki/blob/master/.github/workflows/tests.yml) with a number of minor adjustments for use in my add-ons.


### Disclaimer

#### Project State

This is still very much a work-in-progress. Neither the API, nor the implementation are set in stone.

#### Platform Support

`pytest-anki` has only been tested on Linux so far.

### Usage

1. Install `pytest-anki` into your testing environment:

```bash
pip install --upgrade git+https://github.com/glutanimate/pytest-anki.git
```

1. [Set up an Anki development environment](https://github.com/dae/anki/blob/master/README.development) and add the cloned Anki folder to your `PYTHONPATH` (so that both the `anki` and `aqt` package can be resolved by Python, see [run_tests.sh](tools/run_tests.sh) for an example).

2. In your tests add:
```python
from pytest_anki import anki_running

@pytest.mark.forked  # run this test in a subprocess (!)
def test_my_addon():
    with anki_running() as anki_app:
        import my_addon
        # add some tests in here
```

  I highly recommend running your tests in separate subprocesses using `pytest-forked` as that prevents state persisting across tests, which frequently happens with Anki and can lead to your tests crashing.

4. Assuming that your tests are located in a `tests` folder at the root of your project, run your tests with:

```bash
python3 -m pytest tests
```

(also see the [sample script under tools](./tools/run_tests.sh))

5. (optional) Set up continuous integration with a [GitHub workflow similar to this one](./.github/workflows/tests.yml).


### License and Credits

*pytest-anki* is

*Copyright © 2017-2019 [Michal Krassowski](https://github.com/krassowski/anki_testing) (krassowski)*

*Copyright © 2019-2020 [Aristotelis P.](https://glutanimate.com/) (glutanimate)*

All credits for the original idea for this project go to Michal. _pytest-anki_ would not exist without his work.

_pytest-anki_ is free and open-source software. Its source-code is released under the GNU AGPLv3 license.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY. Please see the license file for more details.