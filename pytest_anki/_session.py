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
from enum import Enum
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    Iterator,
    NamedTuple,
    Optional,
    Union,
)

from ._errors import AnkiSessionError
from ._util import create_json, get_nested_attribute

if TYPE_CHECKING:
    from anki.collection import Collection
    from anki.config import ConfigManager
    from aqt import AnkiApp
    from aqt.main import AnkiQt


class ConfigPaths(NamedTuple):
    default_config: Path
    user_config: Optional[Path]


class AnkiStorageObject(Enum):
    synced_storage = "col.conf"
    profile_storage = "pm.profile"
    meta_storage = "pm.meta"


class AnkiSession:
    def __init__(self, app: "AnkiApp", mw: "AnkiQt", user: str, base: str):
        """Anki test session

        Arguments:
            app {AnkiApp} -- Anki QApplication instance
            mw {AnkiQt} -- Anki QMainWindow instance
            user {str} -- User profile name (e.g. "User 1")
            base {str} -- Path to Anki base directory
        """

        self._app = app
        self._mw = mw
        self._user = user
        self._base = base

    # Key session properties ####

    @property
    def app(self) -> "AnkiApp":
        return self._app

    @property
    def mw(self) -> "AnkiQt":
        return self._mw

    @property
    def user(self) -> str:
        return self._user

    @property
    def base(self) -> str:
        return self._base

    # Collection and profiles ####

    @property
    def collection(self) -> "Collection":
        if self._mw.col is None:
            raise AnkiSessionError(
                "Collection has not been loaded, yet. Please use load_profile()."
            )
        return self._mw.col

    def load_profile(self) -> "Collection":
        self._mw.setupProfile()
        if self._mw.col is None:
            raise AnkiSessionError("Could not load collection")
        return self._mw.col

    def unload_profile(self, on_profile_unloaded: Optional[Callable] = None):
        if on_profile_unloaded is None:
            on_profile_unloaded = lambda *args, **kwargs: None  # noqa: E731
        self._mw.unloadProfile(on_profile_unloaded)

    @contextmanager
    def profile_loaded(self) -> Iterator["Collection"]:
        collection = self.load_profile()

        yield collection

        self.unload_profile()

    # Add-on config handling

    def create_addon_config(
        self,
        addon_package: str,
        default_config: Dict[str, Any],
        user_config: Optional[Dict[str, Any]],
    ) -> ConfigPaths:
        addon_path = Path(self._base) / "addons21" / addon_package
        addon_path.mkdir(parents=True, exist_ok=True)

        defaults_path = addon_path / "config.json"

        create_json(defaults_path, default_config)

        if user_config is not None:
            meta_path = addon_path / "meta.json"
            create_json(meta_path, {"config": user_config})
        else:
            meta_path = None

        return ConfigPaths(defaults_path, meta_path)

    @contextmanager
    def addon_config_created(
        self,
        addon_package: str,
        default_config: Dict[str, Any],
        user_config: Dict[str, Any],
    ) -> Iterator[ConfigPaths]:
        config_paths = self.create_addon_config(
            addon_package=addon_package,
            default_config=default_config,
            user_config=user_config,
        )

        yield config_paths

        if config_paths.default_config.exists():
            config_paths.default_config.unlink()

        if config_paths.user_config and config_paths.user_config.exists():
            config_paths.user_config.unlink()

    def set_anki_object_data(
        self, storage_object: AnkiStorageObject, data: dict
    ) -> Union[Dict[str, Any], ConfigManager]:

        anki_object = self.get_anki_object(storage_object=storage_object)

        if storage_object == AnkiStorageObject.synced_storage:
            # mw.col.conf dict API is deprecated in favor of ConfigManager API
            collection = self.collection
            for key, value in data.items():
                collection.set_config(key, value)
        else:
            anki_object.update(data)  # type: ignore

        return anki_object

    def get_anki_object(
        self, storage_object: AnkiStorageObject
    ) -> Union[Dict[str, Any], ConfigManager]:
        attribute_path = storage_object.value
        try:
            return get_nested_attribute(obj=self._mw, attr=attribute_path)
        except Exception as e:
            raise AnkiSessionError(
                f"Anki storage object {storage_object.name} could not be accessed:"
                f" {str(e)}"
            )
