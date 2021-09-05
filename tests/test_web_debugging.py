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

from unittest.mock import Mock

import requests
from selenium import webdriver

from pytest_anki import AnkiSession, AnkiWebViewType


def test_run_in_thread(anki_session: AnkiSession):
    mock_task = Mock()
    args = tuple((1, 2, 3))
    kwargs = {"foo": 1, "bar": 2, "zing": 3}
    anki_session.run_in_thread_and_wait(task=mock_task, task_args=args, task_kwargs=kwargs)
    mock_task.assert_called_once_with(*args, **kwargs)


def test_web_debugging_available_on_launch(anki_session: AnkiSession):
    port = anki_session.web_debugging_port

    def assert_web_debugging_interface_up():
        result = requests.get(f"http://127.0.0.1:{port}/")
        assert result.status_code == 200
        assert "Inspectable pages" in result.text

    anki_session.run_in_thread_and_wait(assert_web_debugging_interface_up)


def test_web_driver_can_connect(anki_session: AnkiSession):
    def assert_web_driver_connected(driver: webdriver.Chrome):
        assert driver.window_handles

    anki_session.run_with_chrome_driver(assert_web_driver_connected)


def test_web_driver_can_select_web_view(anki_session: AnkiSession):
    def assert_web_driver_connected_to_main_web_view(driver: webdriver.Chrome):
        assert driver.title == AnkiWebViewType.main_webview.value

    with anki_session.profile_loaded():
        anki_session.run_with_chrome_driver(
            assert_web_driver_connected_to_main_web_view, AnkiWebViewType.main_webview
        )


def test_web_driver_can_interact_with_anki(anki_session: AnkiSession):
    def switch_to_deck_view(driver: webdriver.Chrome):
        driver.find_element_by_xpath("//*[text()='Default']").click()

    with anki_session.profile_loaded():
        assert anki_session.mw.state == "deckBrowser"
        anki_session.run_with_chrome_driver(
            switch_to_deck_view, AnkiWebViewType.main_webview
        )

        def mw_state_switched():
            assert anki_session.mw.state == "overview"

        anki_session.qtbot.wait_until(mw_state_switched)
