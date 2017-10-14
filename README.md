## Easy testing of Anki add-ons

A small utility for testing Anki 2.1 addons 

### Usage

1. (Optional) add following to you .gitignore:
```
anki_root
anki_testing
```

2. Clone this repository into the root of your add-on repo:

```bash
git clone anki_testing
```

2. In your tests add:
```python
from anki_testing import anki_running

def test_my_addon():
    with anki_running() as ankI_app:
        import my_addon
        # add some tests in here
```

3. Create a testing script which will install Anki and then call your test-runner. For example:

```bash
#!/usr/bin/env bash
bash anki_testing/install_anki.sh
python3 -m pytest tests
```

Lets call the file above `run_tests.sh`. Remember to `chmod u+x run_tests.sh`.

4. (Optional) configure `.travis.yml` using following template:

```yml
language: python

python:
  - 3.6

install: 
  - git clone anki_testing
  - source anki_testing/setup.sh 

script:
  - bash run_tests.sh
```
