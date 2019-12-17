# coding: utf-8
import shutil
import tempfile
from contextlib import contextmanager

import os

import sys
from warnings import warn


@contextmanager
def _temporary_user(dir_name: str, name: str="__Temporary Test User__",
                    lang: str="en_US"):
    from aqt.profiles import ProfileManager

    # prevent popping up language selection dialog
    original = ProfileManager._setDefaultLang

    def set_default_lang(profileManager):
        profileManager.setLang(lang)

    ProfileManager._setDefaultLang = set_default_lang

    pm = ProfileManager(base=dir_name)

    pm.setupMeta()

    if name in pm.profiles():
        warn(f"Temporary user named {name} already exists")
    else:
        pm.create(name)

    pm.name = name

    yield name

    pm.remove(name)
    ProfileManager._setDefaultLang = original


@contextmanager
def _temporary_dir(tmp_path: str, name: str):
    path = os.path.join(tmp_path, name)
    yield path
    shutil.rmtree(path)


@contextmanager
def anki_running(anki_path: str="anki_root",
                 tmp_path: str=tempfile.gettempdir(),
                 lang: str="en_US",
                 keep_profile):

    if anki_path and anki_path not in sys.path:
        sys.path.insert(0, anki_path)

    import aqt
    from aqt import _run

    # we need a new user for the test
    with _temporary_dir(tmp_path, "anki_temp_base") as dir_name:
        with _temporary_user(dir_name, lang=lang) as user_name:
            app = _run(argv=["anki", "-p", user_name,
                             "-b", dir_name], exec=False)
            yield app

    # clean up what was spoiled
    aqt.mw.cleanupAndExit()

    # remove hooks added during app initialization
    from anki import hooks
    hooks._hooks = {}

    # test_nextIvl will fail on some systems if the locales are not restored
    import locale
    locale.setlocale(locale.LC_ALL, locale.getdefaultlocale())
