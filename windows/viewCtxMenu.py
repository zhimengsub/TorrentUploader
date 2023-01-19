from PyQt5.QtWidgets import QMenu, QAction, QTableView

from utils.gui.enums import PubType
from utils.gui.sources import ICONS


class ViewContextMenu(QMenu):
    def __init__(self, pubtype: PubType, parent: QTableView):
        super().__init__(parent)
        self.pubtype = pubtype
        self.actPubMore = QAction(ICONS.PUBMORE, '编辑并发布...', parent)
        self.actPubMore.setStatusTip('进一步编辑后再发布')

        self.actPubDirect = QAction(ICONS.PUBDIRECT, '一键发布', parent)
        self.actPubDirect.setStatusTip('不进行确认，直接发布')
        self.actPubDirect.setEnabled(False)  # TODO debug only

        self.actMoveTo = QAction(ICONS.MOVETO, '移动到' + ('已发布' if pubtype == PubType.Todo else '待发布'), parent)

        self.actOpen = QAction(ICONS.OPEN, '打开所在文件夹', parent)
        self.actOpen.setStatusTip('双击也可以打开所在文件夹')
        self.addActions([
            self.actPubMore,
            self.actPubDirect,
        ])
        self.addSeparator()
        self.addActions([
            self.actMoveTo,
            self.actOpen
        ])
