import os
import sys
from pathlib import Path
from typing import Optional

from PyQt5 import QtGui
from PyQt5.QtCore import Qt, pyqtSlot, QAbstractItemModel, QModelIndex
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableView

from core.client import Bangumi
from errors import UploadTorrentException, LoginFailed, AccountTeamError
from layouts.layoutMain import Ui_MainWindow  # 由Designer+pyuic生成
from models.bangumi import MyTeam, UploadResponse
from utils.bangumi import assert_team
from utils.configs import saveConfigs, conf
from utils.const import VERSION, PATHS, TEAM_NAME
from utils.gui.enums import PubType
from utils.gui.exception_hook import UncaughtHook, on_exception
from utils.gui.filePicker import FilePicker
from utils.gui.helpers import wait_on_heavy_process
from utils.gui.models.torrentFilterTableModel import TorrentFilterTableModel
from utils.gui.models.torrentTableModel import TorrentTableModel
from utils.gui.torrentDatabase import TorrentDatabase as TDB
from windows.viewCtxMenu import ViewContextMenu
from windows.wndLogin import WndLogin
from windows.wndPubPreview import WndPubPreview


class WndMain(QMainWindow, Ui_MainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.setupUi(self)
        self.retranslateUi(self)
        self.setWindowTitle(self.windowTitle() + ' ver. ' + VERSION)
        self.setWindowIcon(QIcon(str(PATHS.ICON)))

        # window settings
        self.setWindowFlags(Qt.WindowMinimizeButtonHint | Qt.WindowCloseButtonHint)

        # exception handling
        err_hook = UncaughtHook()
        err_hook._exception_caught.connect(lambda msg: on_exception(self, msg))

        # sub windows
        self.wndPubPreviews = []  # type: list[WndPubPreview]
        # 其他初始化设置
        DEBUG = False
        # self.btnLogin.setEnabled(False)
        self.btnTest.setVisible(DEBUG)

        self.client = None  # type: Optional[Bangumi]
        self.myteam = None  # type: Optional[MyTeam]
        self.loggedIn = False

        self.picker = FilePicker(self)  # TODO 监视mp4、mkv->未做种，用qb自动生成种子放入未发布
        self.viewTodo.contextMenuEvent = lambda a0: self.onContextmenuEvent(PubType.Todo, PubType.Done, a0)
        self.viewDone.contextMenuEvent = lambda a0: self.onContextmenuEvent(PubType.Done, PubType.Todo, a0)

        # Must be absolute path
        self.root = None  # type: Optional[Path]
        # sourceModel读取数据库，不直接显示
        self.sourceModel = TorrentTableModel(self)
        self.sourceModel.updatedRoot.connect(lambda: [self.setViewSize(self.viewTodo, self.filterModels[PubType.Todo]),
                                                      self.setViewSize(self.viewDone, self.filterModels[PubType.Done])])
        self.sourceModel.torrentChanged.connect(lambda: [self.setViewSize(self.viewTodo, self.filterModels[PubType.Todo]),
                                                         self.setViewSize(self.viewDone, self.filterModels[PubType.Done])])

        # 把sourceModel按pubtype过滤后分别显示在各自TableView里
        self.filterModels = {
            pubtype: TorrentFilterTableModel(pubtype, self) for pubtype in [PubType.Todo, PubType.Done]
        }  # type: dict[PubType, TorrentFilterTableModel]
        for filterModel in self.filterModels.values():
            filterModel.setSourceModel(self.sourceModel)

        print('proxy model')
        self.viewTodo.setModel(self.filterModels[PubType.Todo])
        self.viewDone.setModel(self.filterModels[PubType.Done])
        # for debug:
        # print('source model')
        # self.viewTodo.setModel(self.sourceModel)
        # self.viewDone.setModel(self.sourceModel)

        self.loadFromConfigs()

        if DEBUG:
            # self.updateRoot(Path(r"D:\字幕组\成片"))
            self.updateRoot(Path(r"D:\Coding\Pycharm\PyProjects\Aegisub\TorrentUploader\test"))
            # self.onLoggedIn(None)
            # self.client = Bangumi.login_with_password('bazingaw', '850462618')

        if conf.autoLogin:
            self.autoLogin()

    # utils
    def onPublishSucceed(self, row: int, filterModel: TorrentFilterTableModel, newPubtype: PubType):
        self.updatePubtypeByRow(row, filterModel, newPubtype)

    @wait_on_heavy_process
    def autoLogin(self):
        if not conf.autoLogin:
            return

        username = conf.username
        pass_ = conf.pass_

        try:
            client = Bangumi.login_with_password(username, pass_)  # type: Bangumi
            myteam = assert_team(client, TEAM_NAME)

        except (LoginFailed, AccountTeamError, Exception) as e:
            on_exception(self, '账号登录错误：\n', str(e))

        else:
            self.onLoggedIn(username, client, myteam)


    def onLoggedIn(self, username: str, client: Bangumi, myteam: MyTeam):
        self.client = client
        self.myteam = myteam
        self.labAccntDisp.setText(username)
        self.loggedIn = True

    @wait_on_heavy_process
    def uploadTorrent(self, path: Path) -> UploadResponse:
        try:
            resp = self.client.upload_torrent(path, self.myteam.id)
            # if not resp.torrents:
            #     raise UploadTorrentException('无法读取已上传的种子信息，resp的种子列表为空！')
        except UploadTorrentException as e:
            on_exception(self, str(e))
        else:
            print('upload success')
            return resp

    @wait_on_heavy_process
    def updatePubtypeByRow(self, row: int, filterModel: TorrentFilterTableModel, newPubtype: PubType):
        idx = filterModel.index(row, 0)
        idx = idx.siblingAtColumn(TDB.COL_NAME)
        self.sourceModel.updatePubtype(filterModel.mapToSource(idx), newPubtype)
        self.setAllViewSize()

    @wait_on_heavy_process
    def updatePubtypeBySelection(self, view: QTableView, filterModel: TorrentFilterTableModel, newPubtype: PubType):
        self.sourceModel.updatePubtypes([filterModel.mapToSource(idx.siblingAtColumn(TDB.COL_NAME)) for idx in view.selectedIndexes()], newPubtype)
        self.setAllViewSize()

    @wait_on_heavy_process
    def updateRoot(self, root: Path):
        self.labRootDisp.setText(str(root))
        self.sourceModel.updateRoot(root)
        self.root = root
        conf.root = str(root)

    # Action slots
    def onPubMoreAction(self, view: QTableView, filterModel: TorrentFilterTableModel, newPubtype: PubType):
        # update pubtype if publish success
        assert self.loggedIn, '请先登录！'
        idxes = view.selectedIndexes()
        if not idxes:
            return
        # only publish the first selection
        # TODO publish multiple selections together
        idx = idxes[0]
        row = idx.row()
        view.selectRow(row)

        nameIdx = idx.siblingAtColumn(TDB.COL_NAME)
        relpathIdx = idx.siblingAtColumn(TDB.COL_RELPATH)
        path = self.root.joinpath(relpathIdx.data(), nameIdx.data())
        resp = self.uploadTorrent(path)
        if not resp:
            return

        while path.suffix:
            path = path.with_suffix('')
        title = path.stem

        wndPubPreview = WndPubPreview(self.client, self.myteam, resp, title)
        wndPubPreview.setAttribute(Qt.WA_DeleteOnClose)
        wndPubPreview.destroyed.connect(lambda: self.wndPubPreviews.remove(wndPubPreview))
        wndPubPreview.published.connect(lambda: self.onPublishSucceed(row, filterModel, newPubtype))
        self.wndPubPreviews.append(wndPubPreview)
        wndPubPreview.show()

    def onPubDirectAction(self):
        # TODO
        ...

    def onMoveToAction(self, view: QTableView, filterModel: TorrentFilterTableModel, newPubtype: PubType):
        self.updatePubtypeBySelection(view, filterModel, newPubtype)

    def onOpenAction(self, view: QTableView):
        for idx in view.selectedIndexes():
            nameIdx = idx.siblingAtColumn(TDB.COL_NAME)
            relpath = nameIdx.siblingAtColumn(TDB.COL_RELPATH).data()
            self.openInExplorer(self.root.joinpath(relpath))
            # only open the first file in selection
            break

    # Context Menu
    def connectContextmenuActions(self, ctxMenu: ViewContextMenu, view: QTableView, filterModel: TorrentFilterTableModel, newPubtype: PubType):
        # TODO connect ctx menu action signals
        ctxMenu.actPubMore.triggered.connect(lambda: self.onPubMoreAction(view, filterModel, newPubtype))
        ctxMenu.actMoveTo.triggered.connect(lambda: self.onMoveToAction(view, filterModel, newPubtype))
        ctxMenu.actOpen.triggered.connect(lambda: self.onOpenAction(view))

    def onContextmenuEvent(self, pubtype: PubType, newPubtype: PubType, a0: QtGui.QContextMenuEvent):
        page = self.tab.currentWidget()
        view = page.findChild(QTableView)  # type: QTableView
        filterModel = self.filterModels[pubtype]
        ctxMenu = ViewContextMenu(pubtype, view)
        self.connectContextmenuActions(ctxMenu, view, filterModel, newPubtype)
        ctxMenu.exec(a0.globalPos())

    # Slots
    @pyqtSlot()
    def on_btnLogin_clicked(self):
        wndLogin = WndLogin()
        wndLogin.loggedIn.connect(self.onLoggedIn)
        wndLogin.exec()

    @pyqtSlot()
    def on_btnTest_clicked(self):
        print(self.client.my_teams())

    @pyqtSlot()
    def on_btnBrowse_clicked(self):
        if dir := self.picker.pickDir(str(self.root)):
            assert dir.is_dir(), '所选路径'+str(dir)+'不存在！'
            self.updateRoot(dir)

    def on_view_doubleClicked(self, index: QModelIndex):
        # open in explorer
        relpath = index.siblingAtColumn(TDB.COL_RELPATH).data()
        self.openInExplorer(self.root.joinpath(relpath))

    @pyqtSlot(QModelIndex)
    def on_viewTodo_doubleClicked(self, index: QModelIndex):
        self.on_view_doubleClicked(index)

    @pyqtSlot(QModelIndex)
    def on_viewDone_doubleClicked(self, index: QModelIndex):
        self.on_view_doubleClicked(index)

    # Events
    def resizeEvent(self, a0: QtGui.QResizeEvent) -> None:
        self.updateConfigs(a0.size().width(), a0.size().height())

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        saveConfigs(PATHS.CONF, conf)
        a0.accept()

    # Misc
    def setAllViewSize(self):
        self.setViewSize(self.viewTodo, self.filterModels[PubType.Todo])
        self.setViewSize(self.viewDone, self.filterModels[PubType.Done])

    @staticmethod
    def setViewSize(view: QTableView, model: QAbstractItemModel):
        """设置View显示的Column"""
        for col in range(1, model.columnCount()):
            view.hideColumn(col)
        view.resizeColumnsToContents()
        view.resizeRowsToContents()

    def loadFromConfigs(self):
        if conf.wndWidth != -1:
            self.resize(conf.wndWidth, conf.wndHeight)
        if conf.root:
            self.updateRoot(Path(conf.root))

    @staticmethod
    def updateConfigs(width: int, height: int):
        conf.wndWidth = width
        conf.wndHeight = height

    @staticmethod
    def openInExplorer(path: Path):
        if path.is_file():
            path = path.parent
        if path.is_dir():
            os.system('explorer ' + str(path))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainwindow = WndMain()
    mainwindow.show()
    sys.exit(app.exec_())  # 如果有多线程，需要os._exit(app.exec_())
