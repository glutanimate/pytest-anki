# coding: utf-8
import shutil
import tempfile
from contextlib import contextmanager

import os

import sys
from warnings import warn


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
        with _temporary_user(dir_name, lang, profile_name, keep_profile) as user_name:
            app = _run(argv=["anki", "-p", user_name, "-b", dir_name], exec=False)
            yield app

    # clean up what was spoiled
    aqt.mw.cleanupAndExit()

    # remove hooks added during app initialization
    from anki import hooks

    hooks._hooks = {}

    # test_nextIvl will fail on some systems if the locales are not restored
    import locale

    locale.setlocale(locale.LC_ALL, locale.getdefaultlocale())
