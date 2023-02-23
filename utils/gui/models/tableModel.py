from pathlib import Path
from typing import Iterable

from PyQt5.QtCore import QObject, QModelIndex, pyqtSignal, pyqtBoundSignal, Qt
from PyQt5.QtSql import QSqlTableModel, QSqlError

from errors import SqlError
from utils.const import SYMB
from utils.gui.enums import PubType
from utils.gui.fileDatabase import FileDatabase as TDB
from utils.gui.fileManager import FileManager
from utils.mypathlib import escape


class TableModel(QSqlTableModel):
    """Connect to torrent database"""
    updatedRoot = pyqtSignal()  # type: pyqtBoundSignal

    def __init__(self, parent: QObject):
        self.manager = FileManager(parent)
        super().__init__(parent, self.manager.db)
        # update model data on torrentChanged
        self.manager.tableChanged.connect(self.select)
        self.setEditStrategy(self.OnManualSubmit)
        self.root = None
        self.pendingPaths = set()

    def updateRoot(self, root: Path) -> None:
        """Set model data according to `root`"""
        self.root = root
        # watch `root` and sync current file system status to database
        self.manager.updateRoot(root)
        # update `bt`, `mtime` fields
        self.manager.db.updateAllRedundancies(root)
        # change to table `root`
        self.setTable(escape(self.root))
        print('last error:', self.lastError().text())
        # update model
        self.select()
        self.updatedRoot.emit()

    def updatePubtype(self, index: QModelIndex, newPubtype: PubType):
        nameIndex = index.siblingAtColumn(TDB.COL_NAME)
        relpathIndex = index.siblingAtColumn(TDB.COL_RELPATH)

        name = nameIndex.data()
        relpath = relpathIndex.data()
        self.manager.db.updatePubtype(self.root, name, relpath, newPubtype)
        self.select()

    def updatePubtypes(self, indexes: Iterable[QModelIndex], newPubtype: PubType):
        names = []
        relpaths = []
        for index in indexes:
            nameIndex = index.siblingAtColumn(TDB.COL_NAME)
            relpathIndex = index.siblingAtColumn(TDB.COL_RELPATH)
            names.append(nameIndex.data())
            relpaths.append(relpathIndex.data())

        self.manager.db.updatePubtypes(self.root, names, relpaths, newPubtype)
        self.select()

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if index.column() == TDB.COL_BT:
                # change column BT display symbol
                nameIdx = index.siblingAtColumn(TDB.COL_NAME)
                relpathIdx = index.siblingAtColumn(TDB.COL_RELPATH)
                path = self.root.joinpath(relpathIdx.data(), nameIdx.data())
                if path in self.pendingPaths:
                    return SYMB.PEND
                exists_bt = bool(super().data(index))
                return SYMB.YES if exists_bt else SYMB.NO
        return super().data(index, role)

    def addPendings(self, vidpaths: set[Path]):
        self.pendingPaths = self.pendingPaths.union(vidpaths)

    def removePendings(self, vidpaths: set[Path]):
        self.pendingPaths = self.pendingPaths - vidpaths

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
