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

import sys
import tempfile
from pathlib import Path

import pytest

from pytest_anki import AnkiSession, AnkiStateUpdate

# General tests ####


@pytest.mark.forked
def test_anki_session_launches(anki_session: AnkiSession):
    from aqt import AnkiApp
    from aqt.main import AnkiQt

    assert isinstance(anki_session.app, AnkiApp)
    assert isinstance(anki_session.mw, AnkiQt)
    assert isinstance(anki_session.user, str)
    assert isinstance(anki_session.base, str)


# Indirect parametrization ####

# Session parameters

_base_path = str(Path(tempfile.gettempdir()) / "custom_base")
_base_name = "custom_base_name"
_profile_name = "foo"
_lang = "de_DE"


@pytest.mark.forked
@pytest.mark.parametrize(
    "anki_session",
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
    import anki

    assert anki_session.base.startswith(_base_path)
    assert Path(anki_session.base).name.startswith(_base_name)

    with anki_session.profile_loaded():
        assert anki_session.mw.pm.name == _profile_name
        assert anki.lang.currentLang == _lang.split("_")[0]


# Preloading Anki state


@pytest.mark.forked
@pytest.mark.parametrize("anki_session", [dict(load_profile=True)], indirect=True)
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


@pytest.mark.forked
@pytest.mark.parametrize(
    "anki_session",
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


@pytest.mark.forked
@pytest.mark.parametrize(
    "anki_session",
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
)


@pytest.mark.forked
@pytest.mark.parametrize(
    "anki_session",
    [
        dict(
            unpacked_addons=[(_state_checker_addon_package, _state_checker_addon_path)],
        )
    ],
    indirect=True,
)
def test_can_preset_anki_state(anki_session: AnkiSession):
    # We want to assert that the pre-configured state reaches add-ons, so we
    # use a sample add-on to record all state at its execution time and
    # then run our assertions against that.

    addon = __import__(_state_checker_addon_package)

    # assert addon.meta_storage == _my_anki_state.meta_storage

    # Profile and collection are not loaded, yet:
    assert addon.profile_storage is None
    assert addon.colconf_storage is None

    with anki_session.profile_loaded():
        assert addon.profile_storage == _my_anki_state.profile_storage
        assert addon.colconf_storage == _my_anki_state.colconf_storage


########


@pytest.mark.forked
def test_load_profile(anki_session: AnkiSession):
    from anki.collection import _Collection

    assert anki_session.mw.col is None

    with anki_session.profile_loaded():
        assert isinstance(anki_session.mw.col, _Collection)

    assert anki_session.mw.col is None


@pytest.mark.forked
def test_profile_hooks(anki_session: AnkiSession):
    from anki.hooks import addHook

    foo = False

    def onProfileLoaded():
        nonlocal foo
        foo = True

    def onProfileUnload():
        nonlocal foo
        foo = False

    addHook("profileLoaded", onProfileLoaded)
    addHook("unloadProfile", onProfileUnload)

    with anki_session.profile_loaded():
        assert foo is True

    assert foo is False


_deck_path = Path(__file__).parent / "samples" / "decks" / "sample_deck.apkg"


@pytest.mark.forked
@pytest.mark.parametrize("anki_session", [dict(load_profile=True)], indirect=True)
def test_deck_imported(anki_session: AnkiSession):
    collection = anki_session.collection
    with anki_session.deck_installed(path=_deck_path) as deck_id:
        deck = collection.decks.get(did=deck_id)
        assert deck is not None
        assert deck["id"] == deck_id
