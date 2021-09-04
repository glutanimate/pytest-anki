# pytest-anki
#
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

from typing import TYPE_CHECKING, Any, Dict, Iterator, Optional

import pytest

if TYPE_CHECKING:
    from pytest import FixtureRequest
    from pytestqt.qtbot import QtBot

from ._launch import anki_running
from ._session import AnkiSession


@pytest.fixture
def anki_session(request: "FixtureRequest", qtbot: "QtBot") -> Iterator[AnkiSession]:
    """Fixture that instantiates Anki, yielding an AnkiSession object

    All keyword arguments below may be passed to the fixture by using indirect
    parametrization.

    E.g., to specify a custom profile name you would decorate your test method with:

    > @pytest.mark.parametrize("anki_session", [dict(profile_name="foo")],
                               indirect=True)

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
            add-ons, mw.col.conf (colconf_storage), mw.pm.profile (profile_storage),
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

        web_debugging_port {Optional[int]}:
            If specified, launches Anki with QTWEBENGINE_REMOTE_DEBUGGING set, allowing
            you to remotely debug Qt web engine views.

    """

    indirect_parameters: Optional[Dict[str, Any]] = getattr(request, "param", None)

    with anki_running(qtbot=qtbot) if not indirect_parameters else anki_running(
        qtbot=qtbot, **indirect_parameters
    ) as session:
        yield session
