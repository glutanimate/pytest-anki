from anki_testing import anki_running
import os


def test_my_addon():
    with anki_running(base_path=os.getcwd(), keep_profile=True) as anki_app:
        assert True

