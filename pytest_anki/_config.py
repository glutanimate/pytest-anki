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


from typing import Dict

from aqt.main import AnkiQt

from ._util import get_nested_attribute

# Other helpers


def update_anki_config(mw: AnkiQt, storage_name: str, data: dict) -> dict:
    attr_paths: Dict[str, str] = {
        "synced": "col.conf",
        "profile": "pm.profile",
        "meta": "pm.meta",
    }

    try:
        attr_path = attr_paths[storage_name]
    except KeyError:
        raise ValueError(
            f"Unsupported storage '{storage_name}'. Please select one of the following:"
            f" {', '.join(attr_paths.keys())}"
        )

    try:
        storage_object = get_nested_attribute(mw, attr_path)
    except AttributeError:
        raise AttributeError(
            f"Anki object not found under mw.{attr_path}. Is your Anki profile loaded?"
        )

    storage_object.update(data)
    if "col" in attr_path.split(".") and mw.col:
        mw.col.setMod()

    return storage_object
