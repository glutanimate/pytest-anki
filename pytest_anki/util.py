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

import json
from pathlib import Path
from typing import Union, Iterator

from contextlib import contextmanager


@contextmanager
def nullcontext() -> Iterator[None]:
    yield None


def create_json(path: Union[str, Path], data: dict, keep: bool = False) -> str:
    """Creates a JSON file at the specified path, preloading it with the specified data.
    
    Arguments:
        path {Union[str, Path]} -- path to JSON file
        data {dict} -- data to write to file
    
    Keyword Arguments:
        keep {bool} -- whether to keep file after context exit (default: {False})
    
    Returns:
        Path -- path to JSON file
    """
    json_path = Path(path)
    with json_path.open("w") as f:
        f.write(json.dumps(data))
    return str(json_path)
