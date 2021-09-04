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


import uuid
from argparse import Namespace
from contextlib import contextmanager
from typing import TYPE_CHECKING, Any, Callable, Dict, Iterator, List, Optional, Tuple
from unittest.mock import Mock

import aqt
from aqt.main import AnkiQt
from aqt.mediasync import MediaSyncer
from aqt.taskman import TaskManager
from PyQt5.QtWidgets import QMainWindow

if TYPE_CHECKING:
    from anki._backend import RustBackend
    from anki.collection import Collection
    from aqt.profiles import ProfileManager as ProfileManagerType

from ._addons import (
    create_addon_config,
    install_addon_from_folder,
    install_addon_from_package,
)
from ._anki import AnkiStateUpdate, update_anki_meta_state
from ._types import PathLike

PostUISetupCallbackType = Callable[[AnkiQt], None]


def post_ui_setup_callback_factory(
    anki_base_dir: PathLike,
    packed_addons: Optional[List[PathLike]] = None,
    unpacked_addons: Optional[List[Tuple[str, PathLike]]] = None,
    addon_configs: Optional[List[Tuple[str, Dict[str, Any]]]] = None,
    preset_anki_state: Optional[AnkiStateUpdate] = None,
):
    def post_ui_setup_callback(main_window: AnkiQt):
        """Initialize add-on manager, install add-ons, load add-ons"""
        main_window.addonManager = aqt.addons.AddonManager(main_window)

        if packed_addons:
            for packed_addon in packed_addons:
                install_addon_from_package(
                    addon_manager=main_window.addonManager, addon_path=packed_addon
                )

        if unpacked_addons:
            for package_name, addon_path in unpacked_addons:
                install_addon_from_folder(
                    anki_base_dir=anki_base_dir,
                    package_name=package_name,
                    addon_path=addon_path,
                )

        if addon_configs:
            for package_name, config_values in addon_configs:
                create_addon_config(
                    anki_base_dir=anki_base_dir,
                    package_name=package_name,
                    user_config=config_values,
                )

        if preset_anki_state and preset_anki_state.meta_storage:
            update_anki_meta_state(
                main_window=main_window, anki_state_update=preset_anki_state
            )

        main_window.addonManager.loadAddons()

    return post_ui_setup_callback


def custom_init_factory(post_ui_setup_callback: PostUISetupCallbackType):
    def custom_init(
        main_window: AnkiQt,
        app: aqt.AnkiApp,
        profileManager: "ProfileManagerType",
        backend: "RustBackend",
        opts: Namespace,
        args: List[Any],
        **kwargs,
    ):
        import aqt

        QMainWindow.__init__(main_window)
        main_window.backend = backend
        main_window.state = "startup"
        main_window.opts = opts
        main_window.col: Optional["Collection"] = None  # type: ignore

        try:  # 2.1.28+
            main_window.taskman = TaskManager(main_window)
        except TypeError:
            main_window.taskman = TaskManager()  # type: ignore

        main_window.media_syncer = MediaSyncer(main_window)

        try:  # 2.1.45+
            from aqt.flags import FlagManager

            main_window.flags = FlagManager(main_window)
        except (ImportError, ModuleNotFoundError):
            pass

        aqt.mw = main_window
        main_window.app = app
        main_window.pm = profileManager
        main_window.safeMode = False  # disable safe mode, of no use to us
        main_window.setupUI()

        post_ui_setup_callback(main_window)

        try:  # 2.1.28+
            main_window.finish_ui_setup()
        except AttributeError:
            pass

    return custom_init


@contextmanager
def patch_anki(
    post_ui_setup_callback: PostUISetupCallbackType,
) -> Iterator[str]:
    """Patch Anki to:
    - allow more fine-grained control of test execution environment
    - enable concurrent testing
    - bypass blocking update dialog
    """
    from anki.utils import checksum
    from aqt import AnkiApp, errors
    from aqt.main import AnkiQt

    old_init = AnkiQt.__init__
    old_key = AnkiApp.KEY
    old_setupAutoUpdate = AnkiQt.setupAutoUpdate
    old_maybe_check_for_addon_updates = AnkiQt.maybe_check_for_addon_updates
    old_errorHandler = errors.ErrorHandler

    patched_ankiqt_init = custom_init_factory(
        post_ui_setup_callback=post_ui_setup_callback
    )

    AnkiQt.__init__ = patched_ankiqt_init  # type: ignore
    AnkiApp.KEY = "anki" + checksum(str(uuid.uuid4()))
    AnkiQt.setupAutoUpdate = Mock()  # type: ignore[assignment]
    AnkiQt.maybe_check_for_addon_updates = Mock()  # type: ignore[assignment]
    errors.ErrorHandler = Mock()  # type: ignore[misc]

    yield AnkiApp.KEY

    AnkiQt.__init__ = old_init  # type: ignore[assignment]
    AnkiApp.KEY = old_key  # type: ignore[assignment]
    AnkiQt.setupAutoUpdate = old_setupAutoUpdate  # type: ignore[assignment]
    AnkiQt.maybe_check_for_addon_updates = (  # type: ignore[assignment]
        old_maybe_check_for_addon_updates
    )
    errors.ErrorHandler = old_errorHandler  # type: ignore[misc]


def set_qt_message_handler_installer(message_handler_installer: Callable):
    aqt.qInstallMessageHandler = message_handler_installer  # type: ignore[assignment]
