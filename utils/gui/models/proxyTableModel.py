import datetime

from PyQt5.QtCore import QObject, QSortFilterProxyModel, QModelIndex, Qt, QDateTime

from utils.gui.enums import PubType
from utils.gui.fileDatabase import FileDatabase as TDB


class ProxyTableModel(QSortFilterProxyModel):
    """Filter rows according to its PubType field"""
    def __init__(self, pubtype: PubType, parent: QObject):
        super().__init__(parent)
        self.pubtype = pubtype

    def update_headers(self):
        # set col name
        self.setHeaderData(TDB.COL_BT, Qt.Horizontal, '种子')
        self.setHeaderData(TDB.COL_NAME, Qt.Horizontal, '视频')
        self.setHeaderData(TDB.COL_RELDIR, Qt.Horizontal, '路径')
        self.setHeaderData(TDB.COL_MTIME, Qt.Horizontal, '修改日期')

    def filterAcceptsRow(self, source_row: int, source_parent: QModelIndex) -> bool:
        pubtypeIndex = self.sourceModel().index(source_row, TDB.COL_PUBTYPE, source_parent)
        return self.sourceModel().data(pubtypeIndex) == self.pubtype.value

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole):
        if role == Qt.DisplayRole and index.column() == TDB.COL_MTIME:
            # 修改时间显示格式
            mtime = super().data(index)
            # 默认显示格式为yy/mm/dd h:m
            if mtime:
                return QDateTime(datetime.datetime.fromtimestamp(mtime))
            return ''
        return super().data(index, role)
