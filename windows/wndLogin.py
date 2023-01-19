from PyQt5.QtCore import pyqtSlot, pyqtSignal, pyqtBoundSignal, Qt
from PyQt5.QtWidgets import QDialog

from core.client import Bangumi
from errors import LoginFailed, AccountTeamError
from layouts.layoutLogin import Ui_dlgLogin
from models.bangumi import MyTeam
from utils.bangumi import assert_team
from utils.configs import conf, saveConfigs
from utils.const import PATHS, TEAM_NAME
from utils.gui.exception_hook import UncaughtHook, on_exception
from utils.gui.helpers import wait_on_heavy_process
from utils.gui.sources import ICONS


class WndLogin(QDialog, Ui_dlgLogin):
    loggedIn = pyqtSignal(str, Bangumi, MyTeam)  # type: pyqtBoundSignal

    def __init__(self):
        QDialog.__init__(self)
        self.setupUi(self)
        self.retranslateUi(self)
        self.setWindowFlags(Qt.WindowMinimizeButtonHint | Qt.WindowCloseButtonHint)
        self.setWindowIcon(ICONS.MAIN)

        # exception handling
        err_hook = UncaughtHook()
        err_hook._exception_caught.connect(lambda msg: on_exception(self, msg))

        self.loadFromConfigs()

    """Utils"""
    def loadFromConfigs(self):
        self.chkAutoLog.setChecked(conf.autoLogin)
        self.chkRem.setChecked(conf.remember)
        self.txtUsername.setText(conf.username)
        self.txtPass.setText(conf.pass_)

    @staticmethod
    def updateConfigs(autoLogin:bool, remember: bool, username: str, pass_: str):
        conf.autoLogin = autoLogin
        conf.remember = remember
        conf.username = username
        if remember:
            conf.pass_ = pass_
        else:
            conf.pass_ = ''

    """Slots"""
    @pyqtSlot(int)
    def on_chkAutoLog_stateChanged(self, state: int):
        if state == 2:
            # checked
            self.chkRem.setCheckState(state)

    @pyqtSlot(int)
    def on_chkRem_stateChanged(self, state: int):
        if state == 0:
            # uncheck
            self.chkAutoLog.setCheckState(state)

    @wait_on_heavy_process
    @pyqtSlot()
    def on_btnSubmit_clicked(self):
        username = self.txtUsername.text()
        pass_ = self.txtPass.text()
        if not username or not pass_:
            return

        try:
            client = Bangumi.login_with_password(username, pass_)  # type: Bangumi
            myteam = assert_team(client, TEAM_NAME)

        except (LoginFailed, AccountTeamError, Exception) as e:
            on_exception(self, '账号登录错误：\n', str(e))

        else:
            self.updateConfigs(self.chkAutoLog.isChecked(), self.chkRem.isChecked(), self.txtUsername.text(), self.txtPass.text())
            self.loggedIn.emit(username, client, myteam)
            saveConfigs(PATHS.CONF, conf)
            self.close()
