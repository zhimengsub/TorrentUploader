from PyQt5.QtCore import QObject, QSortFilterProxyModel, QModelIndex

from utils.gui.enums import PubType
from utils.gui.torrentDatabase import TorrentDatabase as TDB


class TorrentFilterTableModel(QSortFilterProxyModel):
    """Filter rows according to its PubType field"""
    def __init__(self, pubtype: PubType, parent: QObject):
        super().__init__(parent)
        self.pubtype = pubtype
        # TODO 加个对row的排序

    def filterAcceptsRow(self, source_row: int, source_parent: QModelIndex) -> bool:
        pubtypeIndex = self.sourceModel().index(source_row, TDB.COL_PUBTYPE, source_parent)
        return self.sourceModel().data(pubtypeIndex) == self.pubtype.value