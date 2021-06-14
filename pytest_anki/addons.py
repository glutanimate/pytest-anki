# pytest-anki
#
# Copyright (C)  2017-2021 Ankitects Pty Ltd and contributors
# Copyright (C)  2017-2019 Michal Krassowski <https://github.com/krassowski>
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
from typing import Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from pytest_anki import AnkiSession


def install_addon(
    addon_path: Union[Path, str],
    anki_session: "AnkiSession",
    package_name: Optional[str],
):
    addon_path = Path(addon_path)
    if not addon_path.exists():
        raise IOError("Provided path does not exist")

    if addon_path.is_dir():
        if not package_name:
            raise ValueError(
                "When installing from a folder, package_name needs to be provided"
            )
        destination_path = Path(anki_session.base) / "addons21" / package_name
        shutil.copytree(src=addon_path, dst=destination_path, dirs_exist_ok=True)

    elif addon_path.suffix == ".ankiaddon":
        addon_manager = anki_session.mw.addonManager
        addon_manager.install(addon_path)

    else:
        raise IOError("Provided path is not a directory or ankiaddon file")
