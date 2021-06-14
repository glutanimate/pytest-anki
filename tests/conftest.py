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


import sys
from pathlib import Path

# Make current source tree available to pytest
sys.path.append(str(Path(__file__).parent.parent))

# Dynamically register plugin with pytest (rather than rely on setuptools entry point)
# cf.: https://docs.pytest.org/en/6.2.x/writing_plugins.html
pytest_plugins = ["pytest_anki"]
