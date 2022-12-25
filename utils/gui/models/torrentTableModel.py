from pathlib import Path
from typing import Iterable

from PyQt5.QtCore import QObject, QModelIndex, pyqtSignal, pyqtBoundSignal
from PyQt5.QtSql import QSqlTableModel, QSqlError

from errors import SqlError
from utils.gui.enums import PubType
from utils.gui.torrentDatabase import TorrentDatabase as TDB
from utils.gui.torrentManager import TorrentManager


class TorrentTableModel(QSqlTableModel):
    """Connect to torrent database"""
    updatedRoot = pyqtSignal()  # type: pyqtBoundSignal
    torrentChanged = pyqtSignal()  # type: pyqtBoundSignal

    def __init__(self, parent: QObject):
        self.manager = TorrentManager(parent)
        super().__init__(parent, self.manager.db)
        # update model data on torrentChanged
        self.manager.torrentChanged.connect(self.select)
        self.manager.torrentChanged.connect(self.torrentChanged)
        self.setEditStrategy(self.OnManualSubmit)
        self.root = None

    def updateRoot(self, root: Path) -> None:
        """Set model data according to `root`"""
        self.root = root
        # watch `root` and sync current file system status to database
        self.manager.updateRoot(root)
        # change to table `root`
        self.setTable(str(self.root))
        # update model
        self.select()
        self.updatedRoot.emit()

    def updatePubtype(self, index: QModelIndex, newPubtype: PubType):
        self.updatePubtypes([index], newPubtype)

    def updatePubtypes(self, indexes: Iterable[QModelIndex], newPubtype: PubType):
        for index in indexes:
            pubtypeIndex = index.siblingAtColumn(TDB.COL_PUBTYPE)
            self.setData(pubtypeIndex, newPubtype.value)

        if not self.submitAll():
            self.raiseOnError()

    def raiseOnError(self):
        err = self.lastError()
        if err.type() != QSqlError.NoError:
            raise SqlError(err.text())

    def printValues(self):
        for row in range(self.rowCount()):
            for col in range(self.columnCount()):
                idx = self.index(row, col)
                print(idx.data(), end=' ')
            print()
        print()
