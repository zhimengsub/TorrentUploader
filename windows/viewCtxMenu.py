from PyQt5.QtWidgets import QMenu, QAction, QTableView

from utils.gui.enums import PubType
from utils.gui.sources import ICONS


class ViewContextMenu(QMenu):
    def __init__(self, pubtype: PubType, parent: QTableView):
        super().__init__(parent)
        self.pubtype = pubtype
        self.actPubMore = QAction(ICONS.PUBMORE, '编辑并发布...', parent)
        self.actPubMore.setObjectName('actPubMore')
        self.actPubMore.setStatusTip('进一步编辑后再发布（一次只能选择一行）')

        self.actPubDirect = QAction(ICONS.PUBDIRECT, '一键发布', parent)
        self.actPubDirect.setObjectName('actPubDirect')
        self.actPubDirect.setStatusTip('不进行确认，直接发布（可以一次处理多行）')

        self.actMakeBTDetail = QAction(ICONS.MAKEBT, '制作种子（显示详情）', parent)
        self.actMakeBTDetail.setObjectName('actMakeBTDetail')
        self.actMakeBTDetail.setStatusTip('显示制作种子的详情页面')

        self.actMakeBTSilent = QAction(ICONS.MAKEBT, '制作种子（跳过详情）', parent)
        self.actMakeBTSilent.setObjectName('actMakeBTSilent')
        self.actMakeBTSilent.setStatusTip('跳过详情页面（会沿用上次制作时的配置，请确认是否正在做种)')

        self.actMoveTo = QAction(ICONS.MOVETO, '移动到' + ('已发布' if pubtype == PubType.Todo else '待发布'), parent)
        self.actMoveTo.setObjectName('actMoveTo')

        self.actOpen = QAction(ICONS.OPEN, '打开所在文件夹', parent)
        self.actOpen.setObjectName('actOpen')
        self.actOpen.setStatusTip('双击也可以打开所在文件夹')

        self.addActions([
            self.actPubMore,
            self.actPubDirect,
            self.addSeparator(),
            self.actMakeBTDetail,
            self.actMakeBTSilent,
            self.addSeparator(),
            self.actMoveTo,
            self.actOpen
        ])
