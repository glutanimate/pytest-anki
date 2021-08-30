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

import shutil
from pathlib import Path
from typing import Any, Dict, NamedTuple, Optional

from aqt.addons import AddonManager

from ._types import PathLike
from ._util import create_json


def _to_path(path: PathLike) -> Path:
    path_obj = Path(path)
    if not path_obj.exists():
        raise IOError("Provided path does not exist")
    return path_obj


def install_addon_from_package(addon_manager: AddonManager, addon_path: PathLike):
    addon_path = _to_path(addon_path)
    if addon_path.suffix != ".ankiaddon":
        raise ValueError("Provided path is not an .ankiaddon file")
    addon_manager.install(str(addon_path))


def install_addon_from_folder(
    anki_base_dir: PathLike,
    package_name: str,
    addon_path: PathLike,
):
    addon_path = _to_path(addon_path)
    anki_base_dir = _to_path(anki_base_dir)
    if not addon_path.is_dir() or not anki_base_dir.is_dir():
        raise ValueError("Provided path is not a folder")
    if not package_name:
        raise ValueError("Package name must not be empty")
    destination_path = anki_base_dir / "addons21" / package_name
    shutil.copytree(src=addon_path, dst=destination_path, dirs_exist_ok=True)


class ConfigPaths(NamedTuple):
    default_config: Optional[Path]
    user_config: Optional[Path]


def create_addon_config(
    anki_base_dir: PathLike,
    package_name: str,
    default_config: Optional[Dict[str, Any]] = None,
    user_config: Optional[Dict[str, Any]] = None,
) -> ConfigPaths:
    addon_path = Path(anki_base_dir) / "addons21" / package_name
    addon_path.mkdir(parents=True, exist_ok=True)

    defaults_path = meta_path = None

    if default_config:
        defaults_path = addon_path / "config.json"
        create_json(defaults_path, default_config)

    if user_config:
        meta_path = addon_path / "meta.json"
        create_json(meta_path, {"config": user_config})

    return ConfigPaths(defaults_path, meta_path)
