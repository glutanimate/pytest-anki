## anki-testing

[![](https://github.com/glutanimate/anki-testing/workflows/tests/badge.svg)](https://github.com/glutanimate/anki-testing/actions?query=workflow%3Atests)

> a small helper package for testing Anki add-ons

This is a fork of [krassowski/anki_testing](https://github.com/glutanimate/anki-testing/blob/master/.github/workflows/tests.yml) with a number of minor adjustments for use in my add-ons.


### Disclaimer

#### Project State

This is still very much a work-in-progress. Neither the API, nor the implementation are set in stone.

#### Platform Support

`anki-testing` has only been tested on Linux so far.

### Usage

1. Install `anki_testing` into your testing environment:

<!-- TODO: update URLs in case of merged PR ↓ -->

```bash
pip install --upgrade git+https://github.com/glutanimate/anki-testing.git
```

1. [Set up an Anki development environment](https://github.com/dae/anki/blob/master/README.development) and add the cloned Anki folder to your `PYTHONPATH` (so that both the `anki` and `aqt` package can be resolved by Python, see [run_tests.sh](tools/run_tests.sh) for an example).

2. In your tests add:
```python
from anki_testing import anki_running

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

1. (optional) Set up continuous integration with a [GitHub workflow similar to this one](./.github/workflows/tests.yml).


### License and Credits

*anki-testing* is

*Copyright © 2017-2019 [Michal Krassowski](https://github.com/krassowski/anki_testing) (krassowski)*

*Copyright © 2019 [Aristotelis P.](https://glutanimate.com/) (glutanimate)*

This is Michal's work, by a large margin. My changes are only minor and simply seek to make a few things easier for my add-on development workflow (I initially planned on submitting them as a PR, but as these things often go, the codebase just started straying too far away at some point.)