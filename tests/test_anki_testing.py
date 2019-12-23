import os
import pytest

from anki.hooks import addHook

from anki_testing import anki_running, mw_addons_loaded, mw_profile_loaded

ANKI_RUNNING_ARGS = dict(base_path=os.getcwd())


@pytest.mark.forked
def test_anki_running():
    from aqt.qt import QApplication

    with anki_running(**ANKI_RUNNING_ARGS) as anki_app:
        assert isinstance(anki_app, QApplication)


@pytest.mark.forked
def test_mw_addons_loaded():
    from anki.collection import _Collection

    with anki_running(**ANKI_RUNNING_ARGS):
        with mw_addons_loaded() as mw:
            assert mw.col is None
        assert isinstance(mw.col, _Collection)


@pytest.mark.forked
def test_mw_profile_loaded():
    from anki.collection import _Collection

    with anki_running(**ANKI_RUNNING_ARGS):
        with mw_profile_loaded() as mw:
            assert isinstance(mw.col, _Collection)


@pytest.mark.forked
def test_profile_hook():
    with anki_running(**ANKI_RUNNING_ARGS):
        foo = False

        with mw_addons_loaded():

            def onProfileLoaded():
                nonlocal foo
                foo = True

            addHook("profileLoaded", onProfileLoaded)
            assert foo is False
        assert foo is True
