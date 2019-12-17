## Easy testing of Anki add-ons

[![Build Status](https://travis-ci.org/krassowski/anki_testing.svg?branch=master)](https://travis-ci.org/krassowski/anki_testing)

A small utility for testing Anki 2.1 add-ons.
The code from this repository is used by [Anki-Night-Mode](https://github.com/krassowski/Anki-Night-Mode) and [AwesomeTTS](https://github.com/AwesomeTTS/awesometts-anki-addon).

### Usage

1. (Optional) add the following to you .gitignore:
```
anki_root
```

2. Install `anki_testing` into your testing environment:

<!-- TODO: update URLs in case of merged PR ↓ -->

```bash
pip install --upgrade git+https://github.com/glutanimate/anki-testing.git
```

3. In your tests add:
```python
from anki_testing import anki_running

def test_my_addon():
    with anki_running() as anki_app:
        import my_addon
        # add some tests in here
```

4. Create a testing script which will install Anki and then call your test-runner. For example:

```bash
#!/usr/bin/env bash
bash anki_testing/install_anki.sh
python3 -m pytest tests
```

Lets call the file above `run_tests.sh`.

5. (Optional) configure `.travis.yml` using following template:

<!-- TODO: update URLs in case of merged PR ↓ -->

```yml
language: python
sudo: required

python:
  - 3.6

install: 
  - pip install --upgrade git+https://github.com/glutanimate/anki-testing.git
  - git clone https://github.com/glutanimate/anki-testing
  - source anki_testing/setup.sh 

script:
  - bash run_tests.sh
```
