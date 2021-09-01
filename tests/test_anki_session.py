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
Tests for all pytest fixtures provided by the plug-in
"""

import copy
import dataclasses
import json
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional

import pytest
from aqt import AnkiApp
from aqt.main import AnkiQt

from pytest_anki import AnkiSession, AnkiSessionError

if TYPE_CHECKING:
    from pytestqt.qtbot import QtBot

    try:
        from anki.collection import Collection
    except ImportError:
        from anki.collection import _Collection as Collection


# General tests ####


def test_anki_session_launches(anki_session: AnkiSession):
    assert isinstance(anki_session.app, AnkiApp)
    assert isinstance(anki_session.mw, AnkiQt)
    assert isinstance(anki_session.user, str)
    assert isinstance(anki_session.base, str)


# AnkiSession API ####


def test_collection_loading_unloading(anki_session: AnkiSession, qtbot: "QtBot"):
    try:
        from anki.collection import Collection
    except ImportError:  # <=2.1.26
        from anki.collection import _Collection as Collection  # type: ignore[no-redef]

    from aqt import gui_hooks

    is_profile_loaded = False

    def on_profile_did_open():
        nonlocal is_profile_loaded
        is_profile_loaded = True

    def on_profile_will_close():
        nonlocal is_profile_loaded
        is_profile_loaded = False

    gui_hooks.profile_did_open.append(on_profile_did_open)
    gui_hooks.profile_will_close.append(on_profile_will_close)

    with pytest.raises(AnkiSessionError) as exception_info:
        _ = anki_session.collection
    assert "Collection has not been loaded" in str(exception_info.value)

    assert is_profile_loaded is False

    with anki_session.profile_loaded():
        assert isinstance(anki_session.collection, Collection)
        assert is_profile_loaded is True

    assert anki_session.mw.col is None
    assert is_profile_loaded is False

    collection = anki_session.load_profile()

    assert collection is not None
    assert anki_session.mw.col == collection
    assert is_profile_loaded is True

    with qtbot.wait_callback() as callback:
        anki_session.unload_profile(on_profile_unloaded=callback)

    callback.assert_called_with()
    assert is_profile_loaded is False


_deck_path = Path(__file__).parent / "samples" / "decks" / "sample_deck.apkg"


def _get_deck_ids(collection: "Collection") -> List[int]:
    try:
        return [int(deck.id) for deck in collection.decks.all_names_and_ids()]
    except AttributeError:
        return [
            int(deck_id)
            for deck_id in collection.decks.allIds()  # type: ignore[attr-defined]
        ]


def _assert_deck_exists(collection: "Collection", deck_id: int):
    deck = collection.decks.get(did=deck_id)  # type: ignore[arg-type]
    assert deck is not None and deck["id"] == deck_id


def test_deck_management(anki_session: AnkiSession):
    with anki_session.profile_loaded():
        collection = anki_session.collection
        assert len(_get_deck_ids(collection)) == 1

        with anki_session.deck_installed(path=_deck_path) as deck_id:
            assert len(_get_deck_ids(anki_session.collection)) == 2
            _assert_deck_exists(collection=collection, deck_id=deck_id)

        assert len(_get_deck_ids(anki_session.collection)) == 1

        deck_id = anki_session.install_deck(path=_deck_path)
        assert len(_get_deck_ids(anki_session.collection)) == 2
        _assert_deck_exists(collection=collection, deck_id=deck_id)

        anki_session.remove_deck(deck_id=deck_id)
        assert len(_get_deck_ids(anki_session.collection)) == 1


@dataclasses.dataclass
class AddonConfig:
    package_name: str
    default_config: Optional[Dict[str, Any]] = None
    user_config: Optional[Dict[str, Any]] = None


_addon_configs = [
    AddonConfig(
        package_name="sample_addon",
        default_config={"foo": True},
        user_config={"foo": False},
    ),
    AddonConfig(package_name="32452234234", default_config={"foo": True}),
    AddonConfig(
        package_name="11211211221",
        user_config={"foo": True},
    ),
]


def _assert_config_written(anki_base_dir: str, addon_config: AddonConfig):
    addon_path = Path(anki_base_dir) / "addons21" / addon_config.package_name
    user_config_path = addon_path / "meta.json"
    default_config_path = addon_path / "config.json"

    if addon_config.user_config:
        assert user_config_path.exists()
        with user_config_path.open() as user_config_file:
            user_config = json.load(user_config_file)
            assert user_config["config"] == addon_config.user_config

    else:
        assert not user_config_path.exists()

    if addon_config.default_config:
        assert default_config_path.exists()
        with default_config_path.open() as default_config_file:
            default_config = json.load(default_config_file)
            assert default_config == addon_config.default_config

    else:
        assert not default_config_path.exists()


def test_addon_config_management(anki_session: AnkiSession):
    with pytest.raises(ValueError):
        anki_session.create_addon_config(package_name="sample_addon")

    for addon_config in _addon_configs:
        anki_session.create_addon_config(**dataclasses.asdict(addon_config))

        _assert_config_written(
            anki_base_dir=anki_session.base, addon_config=addon_config
        )

    for addon_config in _addon_configs:
        addon_config = copy.deepcopy(addon_config)
        addon_config.package_name = addon_config.package_name + "2"

        all_config_paths = []

        with anki_session.addon_config_created(
            **dataclasses.asdict(addon_config)
        ) as config_paths:
            all_config_paths.append(config_paths)
            _assert_config_written(
                anki_base_dir=anki_session.base, addon_config=addon_config
            )

        for config_paths in all_config_paths:
            if config_paths.default_config:
                assert not config_paths.default_config.exists()
            if config_paths.user_config:
                assert not config_paths.user_config.exists()
