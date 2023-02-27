import os
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
from utils.gui.fileDatabase import FileDatabase as TDB
from utils.gui.filePicker import FilePicker
from utils.gui.helpers import wait_on_heavy_process, setOverrideCursorToWait, restoreOverrideCursor, TorrentMakerThread
from utils.gui.models.proxyTableModel import ProxyTableModel
from utils.gui.models.tableModel import TableModel
from utils.gui.sources import ICONS, init_icons
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

        self.picker = FilePicker(self)
        self.viewTodo.contextMenuEvent = lambda a0: self.onContextmenuEvent(PubType.Todo, PubType.Done, a0)
        self.viewDone.contextMenuEvent = lambda a0: self.onContextmenuEvent(PubType.Done, PubType.Todo, a0)

        # Must be absolute path
        self.root = None  # type: Optional[Path]
        # sourceModel读取数据库，不直接显示
        self.sourceModel = TableModel(self)
        self.sourceModel.updatedRoot.connect(
            lambda: [self.updateView(self.viewTodo, self.proxyModels[PubType.Todo]),
                     self.updateView(self.viewDone, self.proxyModels[PubType.Done])])
        self.sourceModel.manager.tableChanged.connect(
            lambda: [self.updateView(self.viewTodo, self.proxyModels[PubType.Todo]),
                     self.updateView(self.viewDone, self.proxyModels[PubType.Done])])
        self.sourceModel.manager.namesAdded.connect(self.onNamesAdded)
        self.sourceModel.manager.torrentsAdded.connect(self.onTorrentsAdded)

        # 把sourceModel按pubtype过滤后分别显示在各自TableView里
        self.proxyModels = {
            pubtype: ProxyTableModel(pubtype, self) for pubtype in [PubType.Todo, PubType.Done]
        }  # type: dict[PubType, ProxyTableModel]
        for proxyModel in self.proxyModels.values():
            proxyModel.setSourceModel(self.sourceModel)

        # print('proxy model')
        self.viewTodo.setModel(self.proxyModels[PubType.Todo])
        self.viewTodo.setSortingEnabled(True)
        self.viewTodo.sortByColumn(TDB.COL_MTIME, Qt.DescendingOrder)

        self.viewDone.setModel(self.proxyModels[PubType.Done])
        self.viewDone.setSortingEnabled(True)
        self.viewDone.sortByColumn(TDB.COL_RELDIR, Qt.DescendingOrder)
        # for debug:
        # print('source model')
        # self.viewTodo.setModel(self.sourceModel)
        # self.viewDone.setModel(self.sourceModel)

        # load configs
        if conf.wndWidth != -1:
            self.resize(conf.wndWidth, conf.wndHeight)
        if conf.root:
            root = Path(conf.root)
            if root.exists():
                self.updateRoot(root)
            else:
                on_exception(self, '工作目录', str(root), '不存在！', sep=' ')
                conf.root = ''
        if conf.autoLogin:
            self.autoLogin()

    """Utils"""
    def onPublishSucceed(self, row: Union[list[int], int], proxyModel: ProxyTableModel, newPubtype: PubType):
        if isinstance(row, list):
            self.updatePubtypeByRows(row, proxyModel, newPubtype)
        else:
            self.updatePubtypeByRow(row, proxyModel, newPubtype)

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

    def onNamesAdded(self, dir: Path, added_names: set[str]):
        """auto make torrents on new names added"""
        # 不需要select，内容会直接更新
        paths = set(dir.joinpath(name) for name in added_names)
        print('on added', paths)
        self.sourceModel.addPendings(paths)
        td = TorrentMakerThread(self, paths, silent=True)
        td.start()
        # 无论种子是否添加都要removePending，防止卡住
        td.finished.connect(lambda: self.sourceModel.removePendings(paths))

    def onTorrentsAdded(self, dir: Path, added_torrents: set[str]):
        print('add torrents:', '\n'.join(added_torrents))
        vidpaths = set()
        for added in added_torrents:
            name = added.removesuffix('.torrent')
            vidpaths.add(dir.joinpath(name))
        self.sourceModel.removePendings(vidpaths)

    @wait_on_heavy_process
    def updatePubtypeByRow(self, row: int, proxyModel: ProxyTableModel, newPubtype: PubType):
        idx = proxyModel.index(row, TDB.COL_NAME)
        self.sourceModel.updatePubtype(proxyModel.mapToSource(idx), newPubtype)
        self.updateAllViews()

    @wait_on_heavy_process
    def updatePubtypeByRows(self, rows: list[int], proxyModel: ProxyTableModel, newPubtype: PubType):
        idxes = [proxyModel.index(row, TDB.COL_NAME) for row in rows]
        src_idxes = [proxyModel.mapToSource(idx) for idx in idxes]
        self.sourceModel.updatePubtypes(src_idxes, newPubtype)
        self.updateAllViews()

    @wait_on_heavy_process
    def updatePubtypeBySelection(self, view: QTableView, proxyModel: ProxyTableModel, newPubtype: PubType):
        idxes = [idx for idx in view.selectedIndexes() if idx.column() == TDB.COL_NAME]
        self.sourceModel.updatePubtypes([proxyModel.mapToSource(idx) for idx in idxes], newPubtype)
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
    def onPubMoreAction(self, view: QTableView, proxyModel: ProxyTableModel, newPubtype: PubType):
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
        reldirIdx = idx.siblingAtColumn(TDB.COL_RELDIR)
        fullname = self.root.joinpath(reldirIdx.data(), nameIdx.data())
        fulltorrent = Path(str(fullname) + '.torrent')
        try:
            resp = self.client.upload_torrent(fulltorrent, self.myteam.id)
            assert resp, 'resp 为空!'
        except (UploadTorrentException, Exception) as e:
            on_exception(self, '文件上传失败 ' + type(e).__name__ + '\n', str(e))
            return

        while fulltorrent.suffix:
            fulltorrent = fulltorrent.with_suffix('')
        title = fulltorrent.stem

        wndPubPreview = WndPubPreview(self.client, self.myteam, resp, title)
        wndPubPreview.setAttribute(Qt.WA_DeleteOnClose)
        wndPubPreview.published.connect(lambda: self.onPublishSucceed(row, proxyModel, newPubtype))
        self.wndPubPreviews.append(wndPubPreview)
        wndPubPreview.show()

    def onPubDirectAction(self, view: QTableView, proxyModel: ProxyTableModel, newPubtype: PubType):
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
            reldirIdx = idx.siblingAtColumn(TDB.COL_RELDIR)
            fullname = self.root.joinpath(reldirIdx.data(), nameIdx.data())
            fulltorrent = Path(str(fullname) + '.torrent')
            try:
                resp = self.client.upload_torrent(fulltorrent, self.myteam.id)
                assert resp, 'resp 为空!'
            except (UploadTorrentException, Exception) as e:
                on_exception(self, nameIdx.data() + ' 文件上传失败 ' + type(e).__name__ + '\n', str(e))
                continue

            while fulltorrent.suffix:
                fulltorrent = fulltorrent.with_suffix('')
            title = fulltorrent.stem

            try:
                pubInfo = PublishInfo(self.myteam, resp, title)
                pubInfo.loadInfoFromBestPrediction(resp, allow_edit=False)

                self.client.publish(**pubInfo.to_publish_info())
            except Exception as e:
                restoreOverrideCursor()
                # 如果出错跳转到编辑窗口
                # res = QMessageBox.warning(None, '自动发布失败', nameIdx.data() + ' 发布失败\n' + type(e).__name__ + '\n' + str(e) + '\n是否打开手动编辑窗口？', QMessageBox.Yes | QMessageBox.No)
                res = QMessageBox.warning(None, '自动发布失败', nameIdx.data() + ' 发布失败\n' + type(e).__name__ + '\n' + str(e), QMessageBox.Ok)
                if res == QMessageBox.Yes:
                    wndPubPreview = WndPubPreview(self.client, self.myteam, resp, title)
                    wndPubPreview.setAttribute(Qt.WA_DeleteOnClose)
                    wndPubPreview.published.connect(lambda: self.onPublishSucceed(row, proxyModel, newPubtype))
                    self.wndPubPreviews.append(wndPubPreview)
                    # FIXME 如果已经打开过编辑窗口，则需要暂时阻塞循环
                    wndPubPreview.show()
                continue
            else:
                self.onPublishSucceed(row, proxyModel, newPubtype)
                restoreOverrideCursor()

    def onMakeBTAction(self, view: QTableView, silent: bool):
        idxes = [idx for idx in view.selectedIndexes() if idx.column() == TDB.COL_NAME]
        if not idxes:
            return
        if not Path(conf.exe.bc).exists():
            raise FileNotFoundError(conf.exe.bc + ' 不存在！\n请重新配置路径！')

        paths = set()
        for idx in idxes:
            reldirIdx = idx.siblingAtColumn(TDB.COL_RELDIR)
            nameIdx = idx.siblingAtColumn(TDB.COL_NAME)
            # 从idx得到的结果是符号
            btExisted = self.sourceModel.manager.db.selectBtByPath(self.root, reldirIdx.data(), nameIdx.data())
            if btExisted:
                continue
            path = self.root.joinpath(reldirIdx.data(), nameIdx.data())
            paths.add(path)

        self.sourceModel.addPendings(paths)
        td = TorrentMakerThread(self, paths, silent)
        td.start()
        # 无论种子是否添加都要removePending，防止卡住
        td.finished.connect(lambda: self.sourceModel.removePendings(paths))

    def onMoveToAction(self, view: QTableView, proxyModel: ProxyTableModel, newPubtype: PubType):
        self.updatePubtypeBySelection(view, proxyModel, newPubtype)

    def onOpenAction(self, view: QTableView):
        for idx in view.selectedIndexes():
            # note multiple indexes when selecting the whole line
            nameIdx = idx.siblingAtColumn(TDB.COL_NAME)
            reldirIdx = nameIdx.siblingAtColumn(TDB.COL_RELDIR)
            path = self.root.joinpath(reldirIdx.data(), nameIdx.data())
            self.openInExplorer(path)
            # only open the first file in selection
            break

    def connectContextmenuActions(self, ctxMenu: ViewContextMenu, view: QTableView, proxyModel: ProxyTableModel, newPubtype: PubType):
        ctxMenu.actPubMore.triggered.connect(lambda: self.onPubMoreAction(view, proxyModel, PubType.Done))
        ctxMenu.actPubDirect.triggered.connect(lambda: self.onPubDirectAction(view, proxyModel, PubType.Done))
        ctxMenu.actMakeBTDetail.triggered.connect(lambda: self.onMakeBTAction(view, silent=False))
        ctxMenu.actMakeBTSilent.triggered.connect(lambda: self.onMakeBTAction(view, silent=True))
        ctxMenu.actMoveTo.triggered.connect(lambda: self.onMoveToAction(view, proxyModel, newPubtype))
        ctxMenu.actOpen.triggered.connect(lambda: self.onOpenAction(view))

    def onContextmenuEvent(self, pubtype: PubType, newPubtype: PubType, a0: QtGui.QContextMenuEvent):
        page = self.tab.currentWidget()
        view = page.findChild(QTableView)  # type: QTableView
        proxyModel = self.proxyModels[pubtype]
        ctxMenu = ViewContextMenu(pubtype, view)
        self.connectContextmenuActions(ctxMenu, view, proxyModel, newPubtype)
        ctxMenu.exec(a0.globalPos())

    """Slots"""
    @pyqtSlot()
    def on_btnLogin_clicked(self):
        wndLogin = WndLogin()
        wndLogin.loggedIn.connect(self.onLoggedIn)
        wndLogin.exec()

    @pyqtSlot()
    def on_btnTest_clicked(self):
        self.onPublishSucceed(0, self.proxyModels[PubType.Done], PubType.Todo)

    @pyqtSlot()
    def on_btnBrowse_clicked(self):
        if dir := self.picker.pickDir(str(self.root)):
            assert dir.is_dir(), '所选路径'+str(dir)+'不存在！'
            self.updateRoot(dir)

    def on_view_doubleClicked(self, index: QModelIndex):
        # open in explorer
        nameIdx = index.siblingAtColumn(TDB.COL_NAME)
        reldirIdx = index.siblingAtColumn(TDB.COL_RELDIR)
        path = self.root.joinpath(reldirIdx.data(), nameIdx.data())
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
        self.updateView(self.viewTodo, self.proxyModels[PubType.Todo])
        self.updateView(self.viewDone, self.proxyModels[PubType.Done])

    @staticmethod
    def updateView(view: QTableView, model: ProxyTableModel):
        """更新View显示内容"""
        view.hideColumn(TDB.COL_PUBTYPE)  # 必须每次更新数据时都调用
        model.update_headers()  # 必须每次更新数据时都调用
        view.resizeColumnToContents(TDB.COL_BT)
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
