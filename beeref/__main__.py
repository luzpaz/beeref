#!/usr/bin/env python3

# This file is part of BeeRef.
#
# BeeRef is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# BeeRef is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with BeeRef.  If not, see <https://www.gnu.org/licenses/>.

import logging
import signal
import sys

from PyQt6 import QtCore, QtWidgets

from beeref.assets import BeeAssets
from beeref.config import CommandlineArgs, BeeSettings, logfile_name
from beeref import constants
from beeref.view import BeeGraphicsView

logger = logging.getLogger(__name__)


class BeeRefMainWindow(QtWidgets.QWidget):

    def __init__(self, app):
        super().__init__()
        app.setOrganizationName(constants.APPNAME)
        app.setApplicationName(constants.APPNAME)
        self.setWindowIcon(BeeAssets().logo)
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(QtCore.QMargins(0, 0, 0, 0))
        self.setLayout(layout)
        self.resize(500, 300)
        self.view = BeeGraphicsView(app, self)
        layout.addWidget(self.view)
        self.show()

    def __del__(self):
        del self.view


def safe_timer(timeout, func, *args, **kwargs):
    """Create a timer that is safe against garbage collection and
    overlapping calls.
    See: http://ralsina.me/weblog/posts/BB974.html
    """
    def timer_event():
        try:
            func(*args, **kwargs)
        finally:
            QtCore.QTimer.singleShot(timeout, timer_event)
    QtCore.QTimer.singleShot(timeout, timer_event)


def handle_sigint(signum, frame):
    logger.info('Received interrupt. Exiting...')
    QtWidgets.QApplication.quit()


def handle_uncaught_exception(exc_type, exc, traceback):
    logger.critical('Unhandled exception',
                    exc_info=(exc_type, exc, traceback))
    QtWidgets.QApplication.quit()


sys.excepthook = handle_uncaught_exception


def main():
    logger.info(f'Starting {constants.APPNAME} version {constants.VERSION}')
    settings = BeeSettings()
    logger.info(f'Using settings: {settings.fileName()}')
    logger.info(f'Logging to: {logfile_name}')
    CommandlineArgs(with_check=True)  # Force checking
    app = QtWidgets.QApplication(sys.argv)

    bee = BeeRefMainWindow(app)  # NOQA:F841

    signal.signal(signal.SIGINT, handle_sigint)
    # Repeatedly run python-noop to give the interpreter time to
    # handle signals
    safe_timer(50, lambda: None)

    app.exec()
    del bee
    del app


if __name__ == '__main__':
    main()  # pragma: no cover
