# pytest-anki
#
# Copyright (C)  2017-2021 Ankitects Pty Ltd and contributors
# Copyright (C)  2017-2019 Michal Krassowski <https://github.com/krassowski>
# Copyright (C)  2019-2021 Aristotelis P. <https://glutanimate.com/>
#                and contributors (see CONTRIBUTORS file)
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

import os
import shutil
import tempfile
from contextlib import contextmanager
from typing import Iterator, List, Optional, Tuple
from warnings import warn

from ._errors import AnkiLaunchException
from ._patch import patch_anki
from ._session import AnkiSession
from ._types import PathLike
from ._util import nullcontext


@contextmanager
def temporary_user(base_dir: str, name: str, lang: str, keep: bool) -> Iterator[str]:

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

    if not keep and pm.db:
        # reimplement pm.remove() to avoid trouble with trash
        p = pm.profileFolder()
        if os.path.exists(p):
            shutil.rmtree(p)
        pm.db.execute("delete from profiles where name = ?", name)
        pm.db.commit()


@contextmanager
def base_directory(base_path: str, base_name: str, keep: bool) -> Iterator[str]:
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
    load_profile: bool = False,
    force_early_profile_load: bool = False,
    lang: str = "en_US",
    packed_addons: Optional[List[PathLike]] = None,
    unpacked_addons: Optional[List[Tuple[PathLike, str]]] = None,
) -> Iterator[AnkiSession]:
    """Context manager that safely launches an Anki session, cleaning up after itself

    Keyword Arguments:
        base_path {str} -- Path to write Anki base folder to
            (default: system-wide temporary directory)
        base_name {str} -- Base folder name (default: {"anki_base"})
        profile_name {str} -- User profile name (default: {"__Temporary Test User__"})
        keep_profile {bool} -- Whether to preserve profile at context exit
            (default: {False})
        load_profile {bool} -- Whether to preload Anki user profile (with collection)
            (default: {False})
        force_early_profile_load {bool} -- Whether to load Anki profile at app
            initialization time (without collection). Replicates the behavior when
            passing profile as a CLI argument (default: {False})
        lang {str} -- Language to use for the user profile (default: {"en_US"})
        packed_addons {Optional[List[PathLike]]}: List of paths to .ankiaddon-packaged
            add-ons that should be installed ahead of starting Anki
        unpacked_addons {Optional[List[Tuple[PathLike, str]]]}:
            List of unpacked add-ons that should be installed ahead of starting Anki.
            Add-ons need to be specified as tuple of the path to the add-on directory
            and the package name under which they should be installed.

    Returns:
        Iterator[AnkiSession] -- [description]

    Yields:
        Iterator[AnkiSession] -- [description]
    """

    import aqt
    from aqt import _run

    # we need a new user for the test

    with base_directory(base_path, base_name, keep_profile) as base_dir:
        with patch_anki(
            base_dir=base_dir,
            packed_addons=packed_addons or [],
            unpacked_addons=unpacked_addons or [],
        ):
            with temporary_user(
                base_dir, profile_name, lang, keep_profile
            ) as user_name:
                # Do not pass in -p <profile> in order to avoid profile loading.
                # This helps replicate the profile availability at add-on init time
                # for most users. Anki will automatically open the profile at
                # mw.setupProfile time in single-profile setups
                app = _run(argv=["anki", "-b", base_dir], exec=False)
                mw = aqt.mw

                if mw is None or app is None:
                    raise AnkiLaunchException("Main window not initialized correctly")

                if force_early_profile_load:
                    mw.pm.openProfile(profile_name)

                anki_session = AnkiSession(
                    app=app, mw=mw, user=user_name, base=base_dir
                )

                with anki_session.profile_loaded() if load_profile else nullcontext():
                    yield anki_session

    # NOTE: clean up does not seem to work properly in all cases,
    # so use pytest-forked for now

    # clean up what was spoiled
    if aqt.mw:
        aqt.mw.cleanupAndExit()

    # remove hooks added during app initialization
    from anki import hooks

    hooks._hooks = {}

    # test_nextIvl will fail on some systems if the locales are not restored
    import locale

    locale.setlocale(locale.LC_ALL, locale.getdefaultlocale())  # type: ignore
