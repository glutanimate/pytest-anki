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

from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING, Any, Dict, Optional, Union

from ._errors import AnkiSessionError
from ._util import get_nested_attribute

if TYPE_CHECKING:
    from anki.collection import Collection
    from anki.config import ConfigManager
    from aqt.main import AnkiQt


@dataclass
class PresetAnkiState:
    
    """
    Specifies Anki object state to be pre-configured for the test session.
    
    This includes the three main configuration storages used by add-ons:
    
    - mw.col.conf (colconf_storage), available at profile load time
    - mw.pm.profile (profile_storage), available at profile load time
    - mw.pm.meta (meta_storage), available at add-on load time
    """
    
    colconf_storage: Optional[Dict[str, Any]] = None
    profile_storage: Optional[Dict[str, Any]] = None
    meta_storage: Optional[Dict[str, Any]] = None


class AnkiStorageObject(Enum):
    colconf_storage = "col.conf"
    profile_storage = "pm.profile"
    meta_storage = "pm.meta"


def get_collection(main_window: "AnkiQt") -> "Collection":
    if (collection := main_window.col) is None:
        raise AnkiSessionError(
            "Collection has not been loaded, yet. Please use load_profile()."
        )
    return collection


def apply_anki_profile_state(main_window: "AnkiQt", preset_anki_state: PresetAnkiState):
    apply_anki_state(
        main_window=main_window,
        storage_object=AnkiStorageObject.profile_storage,
        preset_anki_state=preset_anki_state,
    )


def apply_anki_meta_state(main_window: "AnkiQt", preset_anki_state: PresetAnkiState):
    apply_anki_state(
        main_window=main_window,
        storage_object=AnkiStorageObject.meta_storage,
        preset_anki_state=preset_anki_state,
    )


def apply_anki_colconf_state(main_window: "AnkiQt", preset_anki_state: PresetAnkiState):
    apply_anki_state(
        main_window=main_window,
        storage_object=AnkiStorageObject.colconf_storage,
        preset_anki_state=preset_anki_state,
    )


def apply_anki_state(
    main_window: "AnkiQt",
    storage_object: AnkiStorageObject,
    preset_anki_state: PresetAnkiState,
):
    data: Optional[Dict[str, Any]] = getattr(preset_anki_state, storage_object.name)
    if data:
        set_anki_object_data(
            main_window=main_window, storage_object=storage_object, data=data
        )


def set_anki_object_data(
    main_window: "AnkiQt", storage_object: AnkiStorageObject, data: dict
) -> Union[Dict[str, Any], "ConfigManager"]:
    """Update the data of a specified Anki storage object

    This may be used to simulate specific Anki and/or add-on states
    during testing."""

    anki_object = get_anki_object(
        main_window=main_window, storage_object=storage_object
    )

    if storage_object == AnkiStorageObject.synced_storage:
        # mw.col.conf dict API is deprecated in favor of ConfigManager API
        collection = get_collection(main_window=main_window)
        for key, value in data.items():
            collection.set_config(key, value)
    else:
        anki_object.update(data)  # type: ignore

    return anki_object


def get_anki_object(
    main_window: "AnkiQt", storage_object: AnkiStorageObject
) -> Union[Dict[str, Any], "ConfigManager"]:
    """Get Anki object for specified AnkiStorageObject type"""
    attribute_path = storage_object.value
    try:
        return get_nested_attribute(obj=main_window, attr=attribute_path)
    except Exception as e:
        raise AnkiSessionError(
            f"Anki storage object {storage_object.name} could not be accessed:"
            f" {str(e)}"
        )
