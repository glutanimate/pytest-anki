# pytest-anki
#
# Copyright (C)  2019-2025 Aristotelis P. <https://glutanimate.com/>
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

import os
from collections import defaultdict
from typing import TYPE_CHECKING, Dict, Optional

if TYPE_CHECKING:
    from _pytest.config import Config
    from pytest import Item


# Fork all tests to avoid side effects


def pytest_collection_modifyitems(items: list["Item"], config: "Config") -> None:
    pass


# Mini pytest plugin to set environment variables for specific tests


_env_store: Dict[str, Dict[str, Optional[str]]] = defaultdict(dict)


def pytest_configure(config: "Config") -> None:
    config.addinivalue_line(
        "markers", "env(dict): set environment variables for a specific test"
    )


def pytest_runtest_setup(item: "Item") -> None:
    marker = item.get_closest_marker("env")
    if marker:
        env_vars = marker.args[0] if marker.args else marker.kwargs
        node_id = item.nodeid

        for key, value in env_vars.items():
            _env_store[node_id][key] = os.environ.get(key)
            os.environ[key] = str(value)


def pytest_runtest_teardown(item: "Item") -> None:
    marker = item.get_closest_marker("env")
    if marker:
        node_id = item.nodeid
        if node_id in _env_store:
            for key, original_value in _env_store[node_id].items():
                if original_value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = original_value
            del _env_store[node_id]
