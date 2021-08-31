# pytest-anki
#
# Copyright (C)  2019-2021 Aristotelis P. <https://glutanimate.com/>
# Copyright (C)  2017-2019 Michal Krassowski <https://github.com/krassowski>
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

from typing import TYPE_CHECKING

from pathlib import Path

import pytest

from pytest_anki import AnkiSession, AnkiSessionError

if TYPE_CHECKING:
    from pytestqt.qtbot import QtBot


# General tests ####


def test_anki_session_launches(anki_session: AnkiSession):
    from aqt import AnkiApp
    from aqt.main import AnkiQt

    assert isinstance(anki_session.app, AnkiApp)
    assert isinstance(anki_session.mw, AnkiQt)
    assert isinstance(anki_session.user, str)
    assert isinstance(anki_session.base, str)


# AnkiSession API ####


def test_collection_loading_unloading(anki_session: AnkiSession, qtbot: "QtBot"):
    from anki.collection import Collection
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


@pytest.mark.parametrize("anki_session", [dict(load_profile=True)], indirect=True)
def test_deck_imported(anki_session: AnkiSession):
    collection = anki_session.collection
    with anki_session.deck_installed(path=_deck_path) as deck_id:
        deck = collection.decks.get(did=deck_id)
        assert deck is not None
        assert deck["id"] == deck_id
