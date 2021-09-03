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

import json
import socket
from contextlib import closing
from functools import reduce
from pathlib import Path
from typing import Any, Union


def create_json(path: Union[str, Path], data: dict) -> str:
    """Creates a JSON file at the specified path, preloading it with the specified data.

    Arguments:
        path {Union[str, Path]} -- path to JSON file
        data {dict} -- data to write to file

    Returns:
        Path -- path to JSON file
    """
    json_path = Path(path)
    with json_path.open("w") as f:
        f.write(json.dumps(data))
    return str(json_path)


def get_nested_attribute(obj: Any, attr: str, *args) -> Any:
    """
    Gets nested attribute from "."-separated string

    Arguments:
        obj {object} -- object to parse
        attr {string} -- attribute name, optionally including
                         "."-characters to denote different levels
                         of nesting

    Returns:
        Any -- object corresponding to attribute name

    Credits:
        https://gist.github.com/wonderbeyond/d293e7a2af1de4873f2d757edd580288
    """

    def _getattr(obj: Any, attr: str):
        return getattr(obj, attr, *args)

    return reduce(_getattr, [obj] + attr.split("."))


def find_free_port():
    # https://stackoverflow.com/a/45690594
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(("", 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s.getsockname()[1]
