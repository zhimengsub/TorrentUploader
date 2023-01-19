import logging
import sys
import traceback

from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal, pyqtBoundSignal
from PyQt5.QtWidgets import QMessageBox, QWidget

from utils.gui.helpers import restoreOverrideCursor
from utils.const import PATHS


class UncaughtHook(QtCore.QObject):
    _exception_caught = pyqtSignal(object)  # type: pyqtBoundSignal

    def __init__(self, *args, **kwargs):
        super(UncaughtHook, self).__init__(*args, **kwargs)

        # this registers the exception_hook() function as hook with the Python interpreter
        sys.excepthook = self.exception_hook

        # save exceptions to file
        fmt = '%(asctime)s [%(levelname)s] %(message)s'
        datefmt = '%Y-%m-%d %H:%M:%S'
        fmter = logging.Formatter(fmt=fmt, datefmt=datefmt)
        hdlr = logging.FileHandler(PATHS.LOGFILE, encoding='utf8')
        hdlr.setFormatter(fmter)
        self.logger = logging.getLogger('exception_hook')
        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(hdlr)

    def exception_hook(self, exc_type, exc_value, exc_traceback):
        """Function handling uncaught exceptions.
        It is triggered each time an uncaught exception occurs.
        """
        if issubclass(exc_type, KeyboardInterrupt):
            # ignore keyboard interrupt to support console applications
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
        else:
            # unhandled exceptions
            if issubclass(exc_type, AssertionError):
                log_msg = '{1}'.format(exc_type.__name__, exc_value)
            else:
                log_msg = '{0}: {1}'.format(exc_type.__name__, exc_value)

            # save to log file
            # log_msg_all = '\n'.join([''.join(traceback.format_tb(exc_traceback)),
            #                         '{0}: {1}'.format(exc_type.__name__, exc_value)])
            exc_info = (exc_type, exc_value, exc_traceback)
            self.logger.critical("\n", exc_info=exc_info)

            # trigger message box show
            self._exception_caught.emit(log_msg)

# TODO log写入文件，并单独做一个log窗口，防止错误信息太长显示不全。
def on_exception(parent: QWidget, *args, sep=''):
    restoreOverrideCursor()
    log_msg = sep.join(args)
    QMessageBox.critical(parent, '错误', '{}'.format(log_msg))
    print(log_msg)