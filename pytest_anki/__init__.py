# pytest-anki
#
# Copyright (C)  2017-2019 Michal Krassowski <https://github.com/krassowski>
# Copyright (C)  2019-2020 Aristotelis P. <https://glutanimate.com/>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version, with the additions
# listed at the end of the license file that accompanied this program.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# NOTE: This program is subject to certain additional terms pursuant to
# Section 7 of the GNU Affero General Public License.  You should have
# received a copy of these additional terms immediately following the
# terms and conditions of the GNU Affero General Public License that
# accompanied this program.
#
# If not, please request a copy through one of the means of contact
# listed here: <https://glutanimate.com/contact/>.
#
# Any modifications to this file must keep this entire header intact.


"""
A simple pytest plugin for testing Anki add-ons
"""

import os
import random
import shutil
import tempfile
import uuid
from argparse import Namespace
from contextlib import contextmanager
from typing import Any, Iterator, List, NamedTuple, Optional
from warnings import warn

import pytest
from pyvirtualdisplay import abstractdisplay

from aqt import AnkiApp
from aqt.main import AnkiQt
from anki.collection import _Collection
from aqt.profiles import ProfileManager as ProfileManagerType
from aqt.qt import QApplication, QMainWindow

__version__ = "0.3.0"
__author__ = "Michal Krassowski, Aristotelis P. (Glutanimate)"
__title__ = "pytest-anki"
__homepage__ = "https://github.com/glutanimate/pytest-anki"


# Ugly workaround: patch pyvirtualdisplay to allow for concurrent pytest-xdist tests
# cf. https://github.com/The-Compiler/pytest-xvfb/issues/16#issuecomment-355005600
abstractdisplay.RANDOMIZE_DISPLAY_NR = True
abstractdisplay.random = random
random.seed()


@contextmanager
def _nullcontext():
    yield None


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
    import aqt

    QMainWindow.__init__(self)
    self.state = "startup"
    self.opts = opts
    self.col: Optional[_Collection] = None  # type: ignore
    aqt.mw = self
    self.app = app
    self.pm = profileManager
    self.safeMode = False  # disable safe mode, of no use to us
    self.setupUI()
    self.setupAddons()


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
def _temporary_user(base_dir: str, name: str, lang: str, keep: bool):

    from aqt.profiles import ProfileManager

    pm = ProfileManager(base=base_dir)

    pm.setupMeta()
    pm.setLang(lang)

    if not keep and name in pm.profiles():
        warn(f"Temporary user named {name} already exists")
    else:
        pm.create(name)

    pm.name = name

    yield name

    if not keep:
        # reimplement pm.remove() to avoid trouble with trash
        p = pm.profileFolder()
        if os.path.exists(p):
            shutil.rmtree(p)
        pm.db.execute("delete from profiles where name = ?", name)
        pm.db.commit()


@contextmanager
def _base_directory(base_path: str, base_name: str, keep: bool):
    if not os.path.isdir(base_path):
        os.mkdir(base_path)
    path = tempfile.mkdtemp(prefix=f"{base_name}_", dir=base_path)
    yield path
    if not keep:
        shutil.rmtree(path)


class AnkiSession(NamedTuple):
    """Named tuple characterizing an Anki test session
    
    Arguments:
        app {AnkiApp} -- Anki QApplication instance
        mw {AnkiQt} -- Anki QMainWindow instance
        user {str} -- User profile name (e.g. "User 1")
        base {str} -- Path to Anki base directory
    """

    app: AnkiApp
    mw: AnkiQt
    user: str
    base: str


@contextmanager
def profile_loaded(mw: AnkiQt) -> Iterator[AnkiQt]:
    """Context manager that safely loads and unloads Anki profile
    
    Arguments:
        mw {AnkiQt} -- Anki QMainWindow instance
    
    Yields:
        AnkiQt -- Anki QMainWindow instance
    """
    mw.setupProfile()

    yield mw

    mw.unloadProfile(lambda *args, **kwargs: None)


@contextmanager
def anki_running(
    base_path: str = tempfile.gettempdir(),
    base_name: str = "anki_base",
    profile_name: str = "__Temporary Test User__",
    keep_profile: bool = False,
    load_profile: bool = False,
    lang: str = "en_US",
) -> Iterator[AnkiSession]:
    """Context manager that safely launches an Anki session, cleaning up after itself
    
    Keyword Arguments:
        base_path {str} -- Path to write Anki base folder to
                           (default: {tempfile.gettempdir()})
        base_name {str} -- Base folder name (default: {"anki_base"})
        profile_name {str} -- User profile name (default: {"__Temporary Test User__"})
        keep_profile {bool} -- Whether to preserve profile at context exit
                               (default: {False})
        load_profile {bool} -- Whether to return an Anki session with the user profile
                               and collection fully preloaded (default: {False})
        lang {str} -- Language to use for the user profile (default: {"en_US"})
    
    Returns:
        Iterator[AnkiSession] -- [description]
    
    Yields:
        Iterator[AnkiSession] -- [description]
    """

    import aqt
    from aqt import _run

    # we need a new user for the test

    with _patch_anki():
        with _base_directory(base_path, base_name, keep_profile) as base_dir:
            with _temporary_user(
                base_dir, profile_name, lang, keep_profile
            ) as user_name:
                app = _run(argv=["anki", "-p", user_name, "-b", base_dir], exec=False)
                mw = aqt.mw

                with profile_loaded(mw) if load_profile else _nullcontext():
                    yield AnkiSession(app=app, mw=mw, user=user_name, base=base_dir)

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


@pytest.fixture
def anki_session(request) -> Iterator[AnkiSession]:
    """Fixture that instantiates Anki, yielding an AnkiSession object
    
    Additional arguments may be passed to the fixture by using indirect parametrization,
    e.g.:
    
    > @pytest.mark.parametrize("anki_session", [dict(profile_name="foo")],
                               indirect=True)
    
    Full list of supported keyword arguments as parameters:
        base_path {str} -- Path to write Anki base folder to
                           (default: {tempfile.gettempdir()})
        base_name {str} -- Base folder name (default: {"anki_base"})
        profile_name {str} -- User profile name (default: {"__Temporary Test User__"})
        keep_profile {bool} -- Whether to preserve profile at context exit
                               (default: {False})
        load_profile {bool} -- Whether to return an Anki session with the user profile
                               and collection fully preloaded (default: {False})
        lang {str} -- Language to use for the user profile (default: {"en_US"})

    Yields:
        Iterator[AnkiSession] -- [description]
    """
    # uses the pytest request fixture
    # https://docs.pytest.org/en/latest/reference.html#request
    param = getattr(request, "param", None)

    with anki_running() if not param else anki_running(**param) as session:
        yield session
