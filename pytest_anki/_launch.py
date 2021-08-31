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
from typing import Any, Dict, Iterator, List, Optional, Tuple

from ._anki import AnkiStateUpdate, update_anki_colconf_state, update_anki_profile_state
from ._errors import AnkiSessionError
from ._patch import patch_anki, post_ui_setup_callback_factory
from ._session import AnkiSession
from ._types import PathLike


@contextmanager
def temporary_user(anki_base_dir: str, name: str, lang: str) -> Iterator[str]:

    from aqt.profiles import ProfileManager

    pm = ProfileManager(base=anki_base_dir)

    pm.setupMeta()
    pm.setLang(lang)
    pm.create(name)

    pm.name = name

    yield name

    if pm.db:
        # reimplement pm.remove() to avoid trouble with trash
        p = pm.profileFolder()
        if os.path.exists(p):
            shutil.rmtree(p)
        pm.db.execute("delete from profiles where name = ?", name)
        pm.db.commit()


@contextmanager
def base_directory(base_path: str, base_name: str) -> Iterator[str]:
    if not os.path.isdir(base_path):
        os.mkdir(base_path)
    anki_base_dir = tempfile.mkdtemp(prefix=f"{base_name}_", dir=base_path)
    yield anki_base_dir
    shutil.rmtree(anki_base_dir)


@contextmanager
def anki_running(
    base_path: str = tempfile.gettempdir(),
    base_name: str = "anki_base",
    profile_name: str = "User 1",
    lang: str = "en_US",
    load_profile: bool = False,
    packed_addons: Optional[List[PathLike]] = None,
    unpacked_addons: Optional[List[Tuple[str, PathLike]]] = None,
    addon_configs: Optional[List[Tuple[str, Dict[str, Any]]]] = None,
    preset_anki_state: Optional[AnkiStateUpdate] = None,
) -> Iterator[AnkiSession]:
    """Context manager that safely launches an Anki session, cleaning up after itself

    Keyword Arguments:
        base_path {str} -- Path to write Anki base folder to
            (default: system-wide temporary directory)

        base_name {str} -- Base folder name (default: {"anki_base"})

        profile_name {str} -- User profile name (default: {"User 1"})

        lang {str} -- Language to use for the user profile (default: {"en_US"})

        load_profile {bool} -- Whether to preload Anki user profile (with collection)
            (default: {False})

        preset_anki_state {Optional[pytest_anki.AnkiStateUpdate]}:
            Allows pre-configuring Anki object state, as described by a PresetAnkiState
            dataclass. This includes the three main configuration storages used by
            add-ons, mw.col.conf (colconf_strage), mw.pm.profile (profile_storage),
            and mw.pm.meta (meta_storage).

            The provided data is applied on top of the existing data in each case
            (i.e. in the same way as dict.update(new_data) would).

            State specified in this manner is guaranteed to be pre-configured ahead of
            add-on load time (in the case of meta_storage), or ahead of
            gui_hooks.profile_did_open fire time (in the case of colconf_storage and
            profile_storage).

            Please note that, in the case of colconf_storage and profile_storage, the
            caller is responsible for either passing 'load_profile=True', or manually
            loading the profile at a later stage.

        packed_addons {Optional[List[PathLike]]}: List of paths to .ankiaddon-packaged
            add-ons that should be installed ahead of starting Anki

        unpacked_addons {Optional[List[Tuple[str, PathLike]]]}:
            List of unpacked add-ons that should be installed ahead of starting Anki.
            Add-ons need to be specified as tuple of the add-on package name under which
            to install the add-on, and the path to the source folder (the package
            folder containing the add-on __init__.py)

        addon_configs {Optional[List[Tuple[str, Dict[str, Any]]]]}:
            List of add-on package names and config values to set the user configuration
            for the specified add-on to. Useful for simulating specific config set-ups.
            Each list member needs to be specified as a tuple of add-on package name
            and dictionary of user configuration values to set.

    Returns:
        Iterator[AnkiSession] -- [description]

    Yields:
        Iterator[AnkiSession] -- [description]
    """

    import aqt
    from aqt import _run, gui_hooks

    with base_directory(base_path=base_path, base_name=base_name) as anki_base_dir:

        # Callback to run between main UI initialization and finishing steps of UI
        # initialization (add-on loading time)

        post_ui_setup_callback = post_ui_setup_callback_factory(
            anki_base_dir=anki_base_dir,
            packed_addons=packed_addons,
            unpacked_addons=unpacked_addons,
            addon_configs=addon_configs,
            preset_anki_state=preset_anki_state,
        )

        # Apply preset Anki profile and collection.conf storage on profile load

        def profile_loaded_callback():
            if not aqt.mw or not preset_anki_state:
                return
            update_anki_profile_state(
                main_window=aqt.mw, anki_state_update=preset_anki_state
            )
            update_anki_colconf_state(
                main_window=aqt.mw, anki_state_update=preset_anki_state
            )

        if preset_anki_state and (
            preset_anki_state.colconf_storage or preset_anki_state.profile_storage
        ):
            gui_hooks.profile_did_open.append(profile_loaded_callback)
            profile_hooked = True
        else:
            profile_hooked = False

        # Start Anki session

        with patch_anki(post_ui_setup_callback=post_ui_setup_callback):
            with temporary_user(
                anki_base_dir=anki_base_dir, name=profile_name, lang=lang
            ) as user_name:

                # We don't pass in -p <profile> in order to avoid profile loading.
                # This helps replicate the profile availability at add-on init time
                # for most users. Anki will automatically open the profile at
                # mw.setupProfile time in single-profile setups
                app = _run(argv=["anki", "-b", anki_base_dir], exec=False)
                mw = aqt.mw

                if mw is None or app is None:
                    raise AnkiSessionError("Main window not initialized correctly")

                anki_session = AnkiSession(
                    app=app, mw=mw, user=user_name, base=anki_base_dir
                )

                if not load_profile:
                    yield anki_session

                else:
                    with anki_session.profile_loaded():
                        yield anki_session

    # NOTE: clean up does not seem to work properly in all cases,
    # so use pytest-forked for now

    # clean up what was spoiled
    if aqt.mw:
        aqt.mw.cleanupAndExit()

    # remove hooks added by pytest-anki

    if profile_hooked:
        gui_hooks.profile_did_open.remove(profile_loaded_callback)

    # remove hooks added during app initialization
    from anki import hooks

    hooks._hooks = {}

    # test_nextIvl will fail on some systems if the locales are not restored
    import locale

    locale.setlocale(locale.LC_ALL, locale.getdefaultlocale())  # type: ignore
