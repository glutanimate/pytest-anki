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

from pathlib import Path

import pytest

from pytest_anki import AnkiSession, profile_loaded
from pytest_anki import deck_installed


@pytest.mark.forked
def test_anki_session_types(anki_session: AnkiSession):
    from aqt import AnkiApp
    from aqt.main import AnkiQt

    assert isinstance(anki_session.app, AnkiApp)
    assert isinstance(anki_session.mw, AnkiQt)
    assert isinstance(anki_session.user, str)
    assert isinstance(anki_session.base, str)


@pytest.mark.forked
@pytest.mark.parametrize("anki_session", [dict(profile_name="foo")], indirect=True)
def test_anki_session_parametrization(anki_session: AnkiSession):
    from aqt import AnkiApp
    from aqt.main import AnkiQt

    assert isinstance(anki_session.app, AnkiApp)
    assert isinstance(anki_session.mw, AnkiQt)
    assert isinstance(anki_session.user, str)
    assert isinstance(anki_session.base, str)


@pytest.mark.forked
def test_load_profile(anki_session: AnkiSession):
    from anki.collection import _Collection

    assert anki_session.mw.col is None

    with profile_loaded(anki_session.mw):
        assert isinstance(anki_session.mw.col, _Collection)

    assert anki_session.mw.col is None


@pytest.mark.forked
@pytest.mark.parametrize("anki_session", [dict(load_profile=True)], indirect=True)
def test_profile_preloaded(anki_session: AnkiSession):
    from anki.collection import _Collection

    assert isinstance(anki_session.mw.col, _Collection)


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

    with profile_loaded(anki_session.mw):
        assert foo is True

    assert foo is False


_deck_path = Path(__file__).parent / "samples" / "sample_deck.apkg"

@pytest.mark.forked
@pytest.mark.parametrize("anki_session", [dict(load_profile=True)], indirect=True)
def test_deck_imported(anki_session: AnkiSession):
    collection = anki_session.mw.col
    with deck_installed(
        file_path=_deck_path, collection=anki_session.mw.col
    ) as deck_id:
        deck = collection.decks.get(did=deck_id)
        assert deck is not None
        assert deck["id"] == deck_id
