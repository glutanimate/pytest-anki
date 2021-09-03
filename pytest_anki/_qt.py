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


from typing import Any, Callable, Dict, Optional, Tuple

from PyQt5.QtCore import QMessageLogContext, QObject, QRunnable, QtMsgType, pyqtSignal


class QtMessageMatcher(QObject):

    match_found = pyqtSignal()

    def __init__(self, matched_phrase: str):
        super().__init__()
        self._matched_phrase = matched_phrase

    def __call__(self, type: QtMsgType, context: QMessageLogContext, msg: str):
        if self._matched_phrase in msg:
            self.match_found.emit()


class Signals(QObject):
    finished = pyqtSignal()


class SignallingWorker(QRunnable):
    def __init__(
        self,
        task: Callable,
        task_args: Optional[Tuple[Any, ...]] = None,
        task_kwargs: Optional[Dict[str, Any]] = None,
    ):
        super().__init__()
        self.signals = Signals()
        self._task = task
        self._task_args = task_args or tuple()
        self._task_kwargs = task_kwargs or {}
        self._result: Optional[Any] = None
        self._error: Optional[Exception] = None

    def run(self):
        try:
            self._result = self._task(*self._task_args, **self._task_kwargs)
        except Exception as error:
            self._error = error
        finally:
            self.signals.finished.emit()

    @property
    def result(self) -> Optional[Any]:
        return self._result

    @property
    def error(self) -> Optional[Exception]:
        return self._error
