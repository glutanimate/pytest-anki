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

from typing import Iterator

import pytest

from ._launch import AnkiSession, anki_running


@pytest.fixture
def anki_session(request) -> Iterator[AnkiSession]:
    """Fixture that instantiates Anki, yielding an AnkiSession object

    Additional arguments may be passed to the fixture by using indirect parametrization,
    e.g.:

    > @pytest.mark.parametrize("anki_session", [dict(profile_name="foo")],
                               indirect=True)

    Full list of supported keyword arguments as parameters:
        base_path {str} -- Path to write Anki base folder to
                           (default: {tempfile.gettempdir()})
        base_name {str} -- Base folder name (default: {"anki_base"})
        profile_name {str} -- User profile name (default: {"__Temporary Test User__"})
        keep_profile {bool} -- Whether to preserve profile at context exit
                               (default: {False})
        load_profile {bool} -- Whether to preload Anki user profile (with collection)
                               (default: {False})
        force_early_profile_load {bool} -- Whether to load Anki profile
            (without collection) at app init time. Replicates the behavior when
            passing profile as a CLI argument (default: {False})
        lang {str} -- Language to use for the user profile (default: {"en_US"})
        packaged_addons {Optional[List[PathLike]]}: List of paths to .ankiaddon-packaged
            add-ons that should be installed ahead of starting Anki
        unpackaged_addons {Optional[List[UnpackagedAddons]]}: List of unpackaged add-ons
            that should be installed ahead of starting Anki, described via the
            UnpackagedAddon datatype as found in pytest_anki.types

    Yields:
        Iterator[AnkiSession] -- [description]
    """
    # uses the pytest request fixture
    # https://docs.pytest.org/en/latest/reference.html#request
    param = getattr(request, "param", None)

    with anki_running() if not param else anki_running(**param) as session:
        yield session
