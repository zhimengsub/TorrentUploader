import sys
import traceback

from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal, pyqtBoundSignal
from PyQt5.QtWidgets import QMessageBox, QWidget

from errors import ApplicationException, GuiException


class UncaughtHook(QtCore.QObject):
    _exception_caught = pyqtSignal(object)  # type: pyqtBoundSignal

    def __init__(self, *args, **kwargs):
        super(UncaughtHook, self).__init__(*args, **kwargs)

        # this registers the exception_hook() function as hook with the Python interpreter
        sys.excepthook = self.exception_hook

    def exception_hook(self, exc_type, exc_value, exc_traceback):
        """Function handling uncaught exceptions.
        It is triggered each time an uncaught exception occurs.
        """
        if issubclass(exc_type, KeyboardInterrupt):
            # ignore keyboard interrupt to support console applications
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
        # 添加新的elif处理错误
        elif issubclass(exc_type, AssertionError) or \
            issubclass(exc_type, GuiException) or \
            issubclass(exc_type, ApplicationException):
            log_msg = '\n'.join(['{0}: {1}'.format(exc_type.__name__, exc_value)])
            self._exception_caught.emit(log_msg)
        else:
            # unhandled exceptions
            # exc_info = (exc_type, exc_value, exc_traceback)
            log_msg = '\n'.join([''.join(traceback.format_tb(exc_traceback)),
                                 '{0}: {1}'.format(exc_type.__name__, exc_value)])
            # log.critical("Uncaught exception:\n {0}".format(log_msg), exc_info=exc_info)

            # trigger message box show
            self._exception_caught.emit(log_msg)


def on_exception(parent: QWidget, *args, sep=''):
    log_msg = sep.join(args)
    QMessageBox.critical(parent, '错误', '{}'.format(log_msg))
    print(log_msg)