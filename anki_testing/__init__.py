# coding: utf-8
from argparse import Namespace
from contextlib import contextmanager
import os
import shutil
import sys
import tempfile
from typing import Any, List, Optional
from warnings import warn

from anki.collection import _Collection
import aqt
from aqt.profiles import ProfileManager as ProfileManagerType
from aqt.qt import QApplication, QMainWindow
from aqt.main import AnkiQt


def _patched_ankiqt_init(
    self: AnkiQt,
    app: QApplication,
    profileManager: ProfileManagerType,
    opts: Namespace,
    args: List[Any],
) -> None:
    """Terminates before profile initialization, allowing more fine-
    grained control of the testing environment (and replication of the
    actual environment add-ons are loaded in)
    """
    QMainWindow.__init__(self)
    self.state = "startup"
    self.opts = opts
    self.col: Optional[_Collection] = None  # type: ignore
    aqt.mw = self
    self.app = app
    self.pm = profileManager
    self.safeMode = False  # disable safe mode, of no use to us
    self.setupUI()


@contextmanager
def _patch_ankiqt_init():
    from aqt.main import AnkiQt

    old_init = AnkiQt.__init__
    AnkiQt.__init__ = _patched_ankiqt_init
    yield
    AnkiQt.__init__ = old_init


@contextmanager
def _temporary_user(dir_name: str, name: str, lang: str, keep: bool):

    from aqt.profiles import ProfileManager

    # prevent popping up language selection dialog
    original = ProfileManager._setDefaultLang

    def set_default_lang(profileManager):
        profileManager.setLang(lang)

    ProfileManager._setDefaultLang = set_default_lang

    pm = ProfileManager(base=dir_name)

    pm.setupMeta()

    if not keep and name in pm.profiles():
        warn(f"Temporary user named {name} already exists")
    else:
        pm.create(name)

    pm.name = name

    yield name

    if not keep:
        pm.remove(name)

    ProfileManager._setDefaultLang = original


@contextmanager
def _base_directory(base_path: str, base_name: str, keep: bool):
    path = os.path.join(base_path, base_name)
    yield path
    if not keep:
        shutil.rmtree(path)


@contextmanager
def anki_running(
    anki_path: str = "anki_root",
    base_path: str = tempfile.gettempdir(),
    base_name: str = "anki_temp_base",
    profile_name: str = "__Temporary Test User__",
    keep_profile: bool = False,
    lang: str = "en_US",
):

    if anki_path and anki_path not in sys.path:
        sys.path.insert(0, anki_path)

    import aqt
    from aqt import _run

    # we need a new user for the test

    with _base_directory(base_path, base_name, keep_profile) as dir_name:
        with _temporary_user(dir_name, profile_name, lang, keep_profile) as user_name:
            with _patch_ankiqt_init():
                app = _run(argv=["anki", "-p", user_name, "-b", dir_name], exec=False)
                yield app

    # NOTE: clean up does not seem to work properly in all cases,
    # so use pytest-forked for now

    # clean up what was spoiled
    aqt.mw.cleanupAndExit()

    # remove hooks added during app initialization
    from anki import hooks

    hooks._hooks = {}

    # test_nextIvl will fail on some systems if the locales are not restored
    import locale

    locale.setlocale(locale.LC_ALL, locale.getdefaultlocale())


@contextmanager
def mw_addons_loaded():
    from aqt import mw

    mw.setupAddons()

    yield mw

    mw.setupProfile()


@contextmanager
def mw_profile_loaded():
    from aqt import mw

    mw.setupProfile()

    yield mw
