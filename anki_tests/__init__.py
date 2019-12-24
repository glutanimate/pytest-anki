# coding: utf-8
import os
import random
import shutil
import tempfile
import uuid
from argparse import Namespace
from contextlib import contextmanager
from typing import Any, List, Optional
from warnings import warn

from pyvirtualdisplay import abstractdisplay

import aqt
from anki.collection import _Collection
from aqt.main import AnkiQt
from aqt.profiles import ProfileManager as ProfileManagerType
from aqt.qt import QApplication, QMainWindow

__version__ = "0.2.0"
__author__ = "Michal Krassowski, Aristotelis P. (Glutanimate)"
__title__ = "anki-tests"
__homepage__ = "https://github.com/glutanimate/anki-tests"


# Ugly workaround: patch pyvirtualdisplay to allow for concurrent pytest-xdist tests
# cf. https://github.com/The-Compiler/pytest-xvfb/issues/16#issuecomment-355005600
abstractdisplay.RANDOMIZE_DISPLAY_NR = True
abstractdisplay.random = random
random.seed()


def _patched_ankiqt_init(
    self: AnkiQt,
    app: QApplication,
    profileManager: ProfileManagerType,
    opts: Namespace,
    args: List[Any],
) -> None:
    """Terminates before profile initialization, replicating the
    actual environment add-ons are loaded in and preventing
    weird race conditions with QTimer
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
def _patch_anki():
    """Patch Anki to:
    - allow more fine-grained control of test execution environment
    - enable concurrent testing
    """
    from aqt.main import AnkiQt
    from aqt import AnkiApp
    from anki.utils import checksum

    old_init = AnkiQt.__init__
    old_key = AnkiApp.KEY

    AnkiQt.__init__ = _patched_ankiqt_init
    AnkiApp.KEY = "anki" + checksum(str(uuid.uuid4()))

    yield AnkiApp.KEY

    AnkiQt.__init__ = old_init
    AnkiApp.KEY = old_key


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
    if not os.path.isdir(base_path):
        os.mkdir(base_path)
    path = tempfile.mkdtemp(prefix=f"{base_name}_", dir=base_path)
    yield path
    if not keep:
        shutil.rmtree(path)


@contextmanager
def anki_running(
    base_path: str = tempfile.gettempdir(),
    base_name: str = "anki_base",
    profile_name: str = "__Temporary Test User__",
    keep_profile: bool = False,
    lang: str = "en_US",
):

    import aqt
    from aqt import _run

    # we need a new user for the test

    with _base_directory(base_path, base_name, keep_profile) as dir_name:
        with _temporary_user(dir_name, profile_name, lang, keep_profile) as user_name:
            with _patch_anki():
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

    def do_nothing():
        pass

    mw.unloadProfile(do_nothing)
