from functools import wraps
from pathlib import Path

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication


def setOverrideCursorToWait():
    QApplication.setOverrideCursor(Qt.WaitCursor)


def restoreOverrideCursor():
    QApplication.restoreOverrideCursor()


def wait_on_heavy_process(func):
    """Change global cursor to wait during `func`"""
    @wraps(func)
    def decorated(*args, **kwargs):
        setOverrideCursorToWait()
        res = func(*args, **kwargs)
        restoreOverrideCursor()
        return res
    return decorated

def get_mtime(file: Path) -> float:
    return file.stat().st_mtime


