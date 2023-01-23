import os
import subprocess
import sys
from pathlib import Path
from typing import Optional, Union

from PyQt5 import QtGui
from PyQt5.QtCore import Qt, pyqtSlot, QModelIndex
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableView, QMessageBox

from core.client import Bangumi
from errors import UploadTorrentException, LoginFailed, AccountTeamError
from layouts.layoutMain import Ui_MainWindow  # 由Designer+pyuic生成
from models.bangumi import MyTeam
from utils.bangumi import assert_team, PublishInfo
from utils.configs import saveConfigs, conf
from utils.const import VERSION, PATHS, TEAM_NAME
from utils.gui.enums import PubType
from utils.gui.exception_hook import UncaughtHook, on_exception
from utils.gui.filePicker import FilePicker
from utils.gui.helpers import wait_on_heavy_process, setOverrideCursorToWait, restoreOverrideCursor, heavy_process
from utils.gui.models.torrentFilterTableModel import TorrentFilterTableModel
from utils.gui.models.torrentTableModel import TorrentTableModel
from utils.gui.sources import ICONS, init_icons
from utils.gui.torrentDatabase import TorrentDatabase as TDB
from utils.helpers import make_proxies
from windows.viewCtxMenu import ViewContextMenu
from windows.wndLogin import WndLogin
from windows.wndPubPreview import WndPubPreview
from windows.wndSettings import WndSettings


class WndMain(QMainWindow, Ui_MainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.setupUi(self)
        self.retranslateUi(self)
        self.setWindowTitle(self.windowTitle() + ' ver. ' + VERSION)
        self.setWindowIcon(ICONS.MAIN)

        # window settings
        self.setWindowFlags(Qt.WindowMinimizeButtonHint | Qt.WindowCloseButtonHint)

        # exception handling
        err_hook = UncaughtHook()
        err_hook._exception_caught.connect(lambda msg: on_exception(self, msg))

        # sub windows
        self.wndPubPreviews = []  # type: list[WndPubPreview]
        self.wndSettings = WndSettings()
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
        self.sourceModel.updatedRoot.connect(lambda: [self.updateView(self.viewTodo, self.filterModels[PubType.Todo]),
                                                      self.updateView(self.viewDone, self.filterModels[PubType.Done])])
        self.sourceModel.torrentChanged.connect(lambda: [self.updateView(self.viewTodo, self.filterModels[PubType.Todo]),
                                                         self.updateView(self.viewDone, self.filterModels[PubType.Done])])

        # 把sourceModel按pubtype过滤后分别显示在各自TableView里
        self.filterModels = {
            pubtype: TorrentFilterTableModel(pubtype, self) for pubtype in [PubType.Todo, PubType.Done]
        }  # type: dict[PubType, TorrentFilterTableModel]
        for filterModel in self.filterModels.values():
            filterModel.setSourceModel(self.sourceModel)

        # print('proxy model')
        self.viewTodo.setModel(self.filterModels[PubType.Todo])
        self.viewTodo.setSortingEnabled(True)
        self.viewTodo.sortByColumn(TDB.COL_MTIME, Qt.DescendingOrder)

        self.viewDone.setModel(self.filterModels[PubType.Done])
        self.viewDone.setSortingEnabled(True)
        self.viewDone.sortByColumn(TDB.COL_RELPATH, Qt.DescendingOrder)
        # for debug:
        # print('source model')
        # self.viewTodo.setModel(self.sourceModel)
        # self.viewDone.setModel(self.sourceModel)

        # load configs
        if conf.wndWidth != -1:
            self.resize(conf.wndWidth, conf.wndHeight)
        if conf.root:
            self.updateRoot(Path(conf.root))
        if conf.autoLogin:
            self.autoLogin()

    """Utils"""
    def onPublishSucceed(self, row: Union[list[int], int], filterModel: TorrentFilterTableModel, newPubtype: PubType):
        if isinstance(row, list):
            self.updatePubtypeByRows(row, filterModel, newPubtype)
        else:
            self.updatePubtypeByRow(row, filterModel, newPubtype)

    @wait_on_heavy_process
    def autoLogin(self):
        if not conf.autoLogin:
            return

        username = conf.username
        pass_ = conf.pass_

        try:
            proxies = make_proxies(conf.proxies.addr, conf.proxies.port, conf.proxies.enabled)
            client = Bangumi.login_with_password(username, pass_, proxies)  # type: Bangumi
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
    def updatePubtypeByRow(self, row: int, filterModel: TorrentFilterTableModel, newPubtype: PubType):
        idx = filterModel.index(row, TDB.COL_NAME)
        self.sourceModel.updatePubtype(filterModel.mapToSource(idx), newPubtype)
        self.updateAllViews()

    @wait_on_heavy_process
    def updatePubtypeByRows(self, rows: list[int], filterModel: TorrentFilterTableModel, newPubtype: PubType):
        idxes = [filterModel.index(row, TDB.COL_NAME) for row in rows]
        src_idxes = [filterModel.mapToSource(idx) for idx in idxes]
        self.sourceModel.updatePubtypes(src_idxes, newPubtype)
        self.updateAllViews()

    @wait_on_heavy_process
    def updatePubtypeBySelection(self, view: QTableView, filterModel: TorrentFilterTableModel, newPubtype: PubType):
        idxes = [idx for idx in view.selectedIndexes() if idx.column() == TDB.COL_NAME]
        self.sourceModel.updatePubtypes([filterModel.mapToSource(idx) for idx in idxes], newPubtype)
        self.updateAllViews()

    @wait_on_heavy_process
    def updateRoot(self, root: Path):
        print('set new root:', root)
        self.sourceModel.updateRoot(root)
        self.root = root
        conf.root = str(root)
        self.labRootDisp.setText(str(root))

    """Action slots"""
    @pyqtSlot()
    def on_actSettings_triggered(self):
        self.wndSettings.show()


    """Context Menu"""
    @wait_on_heavy_process
    def onPubMoreAction(self, view: QTableView, filterModel: TorrentFilterTableModel, newPubtype: PubType):
        # update pubtype if publish success
        idxes = view.selectedIndexes()
        if not idxes:
            return
        assert self.loggedIn, '请先登录！'
        # only publish the first selection
        idx = idxes[0]
        row = idx.row()
        view.selectRow(row)

        nameIdx = idx.siblingAtColumn(TDB.COL_NAME)
        relpathIdx = idx.siblingAtColumn(TDB.COL_RELPATH)
        path = self.root.joinpath(relpathIdx.data(), nameIdx.data())
        try:
            resp = self.client.upload_torrent(path, self.myteam.id)
            assert resp, 'resp 为空!'
        except (UploadTorrentException, Exception) as e:
            on_exception(self, '文件上传失败 ' + type(e).__name__ + '\n', str(e))
            return

        while path.suffix:
            path = path.with_suffix('')
        title = path.stem

        wndPubPreview = WndPubPreview(self.client, self.myteam, resp, title)
        wndPubPreview.setAttribute(Qt.WA_DeleteOnClose)
        wndPubPreview.published.connect(lambda: self.onPublishSucceed(row, filterModel, newPubtype))
        # TODO try not append to list
        self.wndPubPreviews.append(wndPubPreview)
        wndPubPreview.show()

    def onPubDirectAction(self, view: QTableView, filterModel: TorrentFilterTableModel, newPubtype: PubType):
        # TODO 待测试
        # update pubtype if publish success
        idxes = [idx for idx in view.selectedIndexes() if idx.column() == TDB.COL_NAME]
        if not idxes:
            return
        assert self.loggedIn, '请先登录！'
        # publish multiple selections together

        for idx in idxes:
            setOverrideCursorToWait()
            row = idx.row()

            nameIdx = idx.siblingAtColumn(TDB.COL_NAME)
            relpathIdx = idx.siblingAtColumn(TDB.COL_RELPATH)
            path = self.root.joinpath(relpathIdx.data(), nameIdx.data())
            try:
                resp = self.client.upload_torrent(path, self.myteam.id)
                assert resp, 'resp 为空!'
            except (UploadTorrentException, Exception) as e:
                on_exception(self, nameIdx.data() + ' 文件上传失败 ' + type(e).__name__ + '\n', str(e))
                continue

            while path.suffix:
                path = path.with_suffix('')
            title = path.stem

            try:
                pubInfo = PublishInfo(self.myteam, resp, title)
                pubInfo.loadInfoFromBestPrediction(resp, allow_edit=False)

                self.client.publish(**pubInfo.to_publish_info())
            except Exception as e:
                # TODO 如果出错跳转到编辑窗口，如果已经打开了编辑窗口，则需要暂时阻塞循环
                restoreOverrideCursor()
                res = QMessageBox.warning(None, '自动发布失败', nameIdx.data() + ' 发布失败\n' + type(e).__name__ + '\n' + str(e) + '\n是否打开手动编辑窗口？', QMessageBox.Yes | QMessageBox.No)
                if res == QMessageBox.Yes:
                    wndPubPreview = WndPubPreview(self.client, self.myteam, resp, title)
                    wndPubPreview.setAttribute(Qt.WA_DeleteOnClose)
                    wndPubPreview.published.connect(lambda: self.onPublishSucceed(row, filterModel, newPubtype))
                    self.wndPubPreviews.append(wndPubPreview)
                    wndPubPreview.show()
                continue
            else:
                self.onPublishSucceed(row, filterModel, newPubtype)

    def onMakeBTAction(self, view: QTableView, silent: bool):
        idxes = [idx for idx in view.selectedIndexes() if idx.column() == TDB.COL_NAME]
        if not idxes:
            return
        if not Path(conf.exe.bc).exists():
            raise FileNotFoundError(conf.exe.bc + ' 不存在！\n请重新配置路径！')

        for idx in idxes:
            nameIdx = idx.siblingAtColumn(TDB.COL_NAME)
            relpathIdx = idx.siblingAtColumn(TDB.COL_RELPATH)
            path = self.root.joinpath(relpathIdx.data(), nameIdx.data())
            cmd = [conf.exe.bc, '-m', str(path)]
            if silent:
                cmd.append('-s')
            print(cmd)
            with heavy_process():
                subprocess.run(cmd)

    def onMoveToAction(self, view: QTableView, filterModel: TorrentFilterTableModel, newPubtype: PubType):
        self.updatePubtypeBySelection(view, filterModel, newPubtype)

    def onOpenAction(self, view: QTableView):
        for idx in view.selectedIndexes():
            nameIdx = idx.siblingAtColumn(TDB.COL_NAME)
            relpathIdx = nameIdx.siblingAtColumn(TDB.COL_RELPATH)
            path = self.root.joinpath(relpathIdx.data(), nameIdx.data())
            self.openInExplorer(path)
            # only open the first file in selection
            break

    def connectContextmenuActions(self, ctxMenu: ViewContextMenu, view: QTableView, filterModel: TorrentFilterTableModel, newPubtype: PubType):
        # TODO connect ctx menu action signals
        ctxMenu.actPubMore.triggered.connect(lambda: self.onPubMoreAction(view, filterModel, PubType.Done))
        ctxMenu.actPubDirect.triggered.connect(lambda: self.onPubDirectAction(view, filterModel, PubType.Done))
        ctxMenu.actMakeBTDetail.triggered.connect(lambda: self.onMakeBTAction(view, silent=False))
        ctxMenu.actMakeBTSilent.triggered.connect(lambda: self.onMakeBTAction(view, silent=True))
        ctxMenu.actMoveTo.triggered.connect(lambda: self.onMoveToAction(view, filterModel, newPubtype))
        ctxMenu.actOpen.triggered.connect(lambda: self.onOpenAction(view))

    def onContextmenuEvent(self, pubtype: PubType, newPubtype: PubType, a0: QtGui.QContextMenuEvent):
        page = self.tab.currentWidget()
        view = page.findChild(QTableView)  # type: QTableView
        filterModel = self.filterModels[pubtype]
        ctxMenu = ViewContextMenu(pubtype, view)
        self.connectContextmenuActions(ctxMenu, view, filterModel, newPubtype)
        ctxMenu.exec(a0.globalPos())

    """Slots"""
    @pyqtSlot()
    def on_btnLogin_clicked(self):
        wndLogin = WndLogin()
        wndLogin.loggedIn.connect(self.onLoggedIn)
        wndLogin.exec()

    @pyqtSlot()
    def on_btnTest_clicked(self):
        self.onPublishSucceed(0, self.filterModels[PubType.Done], PubType.Todo)

    @pyqtSlot()
    def on_btnBrowse_clicked(self):
        if dir := self.picker.pickDir(str(self.root)):
            assert dir.is_dir(), '所选路径'+str(dir)+'不存在！'
            self.updateRoot(dir)

    def on_view_doubleClicked(self, index: QModelIndex):
        # open in explorer
        nameIdx = index.siblingAtColumn(TDB.COL_NAME)
        relpathIdx = index.siblingAtColumn(TDB.COL_RELPATH)
        path = self.root.joinpath(relpathIdx.data(), nameIdx.data())
        self.openInExplorer(path)

    @pyqtSlot(QModelIndex)
    def on_viewTodo_doubleClicked(self, index: QModelIndex):
        self.on_view_doubleClicked(index)

    @pyqtSlot(QModelIndex)
    def on_viewDone_doubleClicked(self, index: QModelIndex):
        self.on_view_doubleClicked(index)

    """Events"""
    def resizeEvent(self, a0: QtGui.QResizeEvent) -> None:
        self.updateConfigs(a0.size().width(), a0.size().height())

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        saveConfigs(PATHS.CONF, conf)
        a0.accept()

    """Misc"""
    def updateAllViews(self):
        self.updateView(self.viewTodo, self.filterModels[PubType.Todo])
        self.updateView(self.viewDone, self.filterModels[PubType.Done])

    @staticmethod
    def updateView(view: QTableView, model: TorrentFilterTableModel):
        """更新View显示内容"""
        view.hideColumn(TDB.COL_PUBTYPE)  # 必须每次更新数据时都调用
        model.update_headers()  # 必须每次更新数据时都调用
        view.resizeColumnToContents(TDB.COL_NAME)
        view.resizeColumnToContents(TDB.COL_MTIME)
        # view.resizeColumnsToContents()
        # view.resizeRowsToContents()


    @staticmethod
    def updateConfigs(width: int, height: int):
        conf.wndWidth = width
        conf.wndHeight = height

    @staticmethod
    def openInExplorer(path: Path):
        if path.is_dir() or path.is_file():
            os.system('explorer /select,' + str(path))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    init_icons()
    mainwindow = WndMain()
    mainwindow.show()
    sys.exit(app.exec_())  # 如果有多线程，需要os._exit(app.exec_())
