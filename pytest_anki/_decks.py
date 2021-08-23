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

from contextlib import contextmanager
from pathlib import Path
from typing import TYPE_CHECKING, Iterator, List, Union

from anki.importing.apkg import AnkiPackageImporter

if TYPE_CHECKING:
    from anki.collection import Collection


@contextmanager
def deck_installed(
    file_path: Union[Path, str], collection: "Collection", keep: bool = False
) -> Iterator[int]:

    old_ids = set(_get_deck_ids(collection=collection))

    importer = AnkiPackageImporter(col=collection, file=str(file_path))
    importer.run()

    new_ids = set(_get_deck_ids(collection=collection))

    deck_id = next(iter(new_ids - old_ids))

    yield deck_id

    if keep:
        return

    try:
        collection.decks.remove([deck_id])
    except AttributeError:  # legacy
        collection.decks.rem(deck_id)


def _get_deck_ids(collection: "Collection") -> List[int]:
    try:
        return [d.id for d in collection.decks.all_names_and_ids()]
    except AttributeError:  # legacy
        return collection.decks.allIds()
