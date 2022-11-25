import sys
from typing import Optional

from PyQt5.QtWidgets import QApplication, QWidget

from core.client import Bangumi
from utils import Singleton


class Application(Singleton):
    _app: QApplication = QApplication(sys.argv)
    _client: Optional[Bangumi] = None

    @property
    def app(self) -> QApplication:
        return self._app

    @property
    def client(self) -> Bangumi:
        with self._lock:
            self._client = Bangumi()
        return self._client

    def __init__(self):
        ...

    def run(self):
        w = QWidget()
        w.resize(250, 150)
        w.move(300, 300)
        w.setWindowTitle("Simple")
        w.show()
        self.app.exec_()
