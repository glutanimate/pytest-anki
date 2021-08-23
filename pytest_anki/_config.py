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
from typing import Dict, Iterator, NamedTuple, Optional, Union

from aqt.main import AnkiQt

from ._util import get_nested_attribute, create_json

# Other helpers


class LocalConfigPaths(NamedTuple):
    defaults: str
    user: str


@contextmanager
def local_addon_config(
    base: Union[str, Path],
    module_name: str,
    defaults: dict,
    user: Optional[dict] = None,
    keep: bool = False,
) -> Iterator[LocalConfigPaths]:
    """Context manager that creates a config.json (and optionally a meta.json) file
    for an add-on and preloads them with the specified data

    Arguments:
        base {Union[str, Path]} -- base Anki path
        module_name {str} -- add-on module name
        defaults {dict} -- data to load into config.json (the default config file)
        user {dict} -- data to load into meta.json (the user config file)

    Keyword Arguments:
        keep {bool} -- whether to keep created files after context exit
                       (default: {False})

    Yields:
        Iterator[ConfigPaths] -- tuple of paths to config.json and meta.json
    """
    addon_path = Path(base) / "addons21" / module_name
    addon_path.mkdir(parents=True, exist_ok=True)

    defaults_path = addon_path / "config.json"
    meta_path = addon_path / "meta.json"

    create_json(defaults_path, defaults)

    create_meta = user is not None

    if create_meta:
        create_json(meta_path, {"config": user})

    yield LocalConfigPaths(str(defaults_path), str(meta_path))

    if keep:
        return

    defaults_path.unlink()

    if create_meta:
        meta_path.unlink()


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
