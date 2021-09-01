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


"""
Tests for the AnkiSession API
"""

import sys
import tempfile
from pathlib import Path
from typing import Final

import pytest

from pytest_anki import AnkiSession, AnkiStateUpdate

# Indirect parametrization ####

ANKI_SESSION: Final = "anki_session"

# Session parameters

_base_path = str(Path(tempfile.gettempdir()) / "custom_base")
_base_name = "custom_base_name"
_profile_name = "foo"
_lang = "de_DE"


@pytest.mark.parametrize(
    ANKI_SESSION,
    [
        dict(
            base_path=_base_path,
            base_name=_base_name,
            profile_name=_profile_name,
            lang=_lang,
        )
    ],
    indirect=True,
)
def test_can_set_anki_session_properties(anki_session: AnkiSession):
    from anki import lang

    assert anki_session.base.startswith(_base_path)
    assert Path(anki_session.base).name.startswith(_base_name)

    with anki_session.profile_loaded():
        assert anki_session.mw.pm.name == _profile_name
        assert lang.currentLang == _lang.split("_")[0]


# Preloading Anki state


@pytest.mark.parametrize(ANKI_SESSION, [dict(load_profile=True)], indirect=True)
def test_can_preload_profile(anki_session: AnkiSession):
    from anki.collection import _Collection

    assert anki_session.mw.pm.profile is not None
    assert isinstance(anki_session.mw.col, _Collection)


# Installing and configuring add-ons

_addons_path = Path(__file__).parent / "samples" / "add-ons"
_simple_addons_path = _addons_path / "simple"

_packed_addons = []
_unpacked_addons = []
_packages = []

for path in _simple_addons_path.iterdir():
    if path.is_dir():
        package_name = path.name
        _unpacked_addons.append((package_name, path))
        _packages.append(package_name)
    elif path.suffix == ".ankiaddon":
        _packed_addons.append(path)
        package_name = path.stem
        _packages.append(package_name)


@pytest.mark.parametrize(
    ANKI_SESSION,
    [dict(packed_addons=_packed_addons, unpacked_addons=_unpacked_addons)],
    indirect=True,
)
def test_can_install_addons(anki_session: AnkiSession):
    main_window = anki_session.mw
    all_addons = anki_session.mw.addonManager.allAddons()

    for package in _packages:
        assert package in all_addons
        assert package in sys.modules
        assert getattr(main_window, package) is True


_state_checker_addon_package = "state_checker_addon"
_state_checker_addon_path = _addons_path / "advanced" / _state_checker_addon_package

_unpacked_addons = []
_addon_configs = []

_config_key = "foo"

for addon_copy in range(2):
    package_name = f"{_state_checker_addon_package}_{addon_copy}"
    config = {_config_key: addon_copy}
    _unpacked_addons.append((package_name, _state_checker_addon_path))
    _addon_configs.append((package_name, config))


@pytest.mark.parametrize(
    ANKI_SESSION,
    [dict(unpacked_addons=_unpacked_addons, addon_configs=_addon_configs)],
    indirect=True,
)
def test_can_configure_addons(anki_session: AnkiSession):
    addon_manager = anki_session.mw.addonManager
    for package_name, config in _addon_configs:
        addon = __import__(package_name)
        assert addon.config == config
        assert addon_manager.getConfig(package_name) == config


_my_anki_state = AnkiStateUpdate(
    meta_storage={_state_checker_addon_package: True},
    profile_storage={_state_checker_addon_package: True},
    colconf_storage={_state_checker_addon_package: True},
)


@pytest.mark.parametrize(
    ANKI_SESSION,
    [
        dict(
            unpacked_addons=[(_state_checker_addon_package, _state_checker_addon_path)],
            preset_anki_state=_my_anki_state,
        )
    ],
    indirect=True,
)
def test_can_preset_anki_state(anki_session: AnkiSession):
    # We want to assert that the pre-configured state reaches add-ons, so we
    # use a sample add-on to record all state at its execution time and
    # then run our assertions against that.
    package_name = _state_checker_addon_package

    addon = __import__(package_name)

    # assert addon.meta_storage == _my_anki_state.meta_storage

    # Profile and collection are not loaded, yet:
    assert addon.profile_storage is None
    assert addon.colconf_storage is None

    with anki_session.profile_loaded():
        assert (
            addon.profile_storage
            == _my_anki_state.profile_storage[package_name]  # type: ignore
        )
        assert (
            addon.colconf_storage
            == _my_anki_state.colconf_storage[package_name]  # type: ignore
        )
