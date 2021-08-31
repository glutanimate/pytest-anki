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

from pytest_anki import AnkiSession

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

_packed_addons = []
_unpacked_addons = []
_packages = []

for path in _addons_path.iterdir():
    if path.is_dir():
        package_name = path.name
        _unpacked_addons.append((package_name, path))
        _packages.append(package_name)
    elif path.suffix == ".ankiaddon":
        _packed_addons.append(path)
        package_name = path.stem
        _packages.append(package_name)

import time


@pytest.mark.forked
@pytest.mark.parametrize(
    "anki_session",
    [dict(packed_addons=_packed_addons, unpacked_addons=_unpacked_addons)],
    indirect=True,
)
def test_can_install_addons(anki_session: AnkiSession):
    main_window = anki_session.mw
    all_addons = anki_session.mw.addonManager.allAddons()

    time.sleep(600)

    for package in _packages:
        assert package in all_addons
        assert package in sys.modules
        assert getattr(main_window, package) is True


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
