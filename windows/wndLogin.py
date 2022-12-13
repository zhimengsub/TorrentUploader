from PyQt5.QtCore import pyqtSlot, pyqtSignal, pyqtBoundSignal, Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QDialog

from core.client import Bangumi
from errors import LoginFailed, AccountTeamError
from layouts.layoutLogin import Ui_dlgLogin
from models.bangumi import MyTeam
from utils.configs import conf, saveConfigs
from utils.const import PATHS, TEAM_NAME
from utils.gui.exception_hook import UncaughtHook, on_exception
from utils.gui.helpers import wait_on_heavy_process


# TODO 自动登录
class WndLogin(QDialog, Ui_dlgLogin):
    loggedIn = pyqtSignal(str, Bangumi, MyTeam)  # type: pyqtBoundSignal

    def __init__(self):
        QDialog.__init__(self)
        self.setupUi(self)
        self.retranslateUi(self)
        self.setWindowFlags(Qt.WindowMinimizeButtonHint | Qt.WindowCloseButtonHint)
        self.setWindowIcon(QIcon(str(PATHS.ICON)))

        # exception handling
        err_hook = UncaughtHook()
        err_hook._exception_caught.connect(lambda msg: on_exception(self, msg))

        self.loadFromConfigs()

    def loadFromConfigs(self):
        self.chkRem.setChecked(conf.remember)
        self.txtUsername.setText(conf.username)
        self.txtPass.setText(conf.pass_)

    @staticmethod
    def updateConfigs(remember: bool, username: str, pass_: str):
        conf.remember = remember
        conf.username = username
        if remember:
            conf.pass_ = pass_
        else:
            conf.pass_ = ''

    @wait_on_heavy_process
    @pyqtSlot()
    def on_btnSubmit_clicked(self):
        username = self.txtUsername.text()
        pass_ = self.txtPass.text()
        if not username or not pass_:
            return
        try:
            client = Bangumi.login_with_password(username, pass_)  # type: Bangumi
            myteam = None
            for myteam in client.my_teams():
                if myteam.name == TEAM_NAME:
                    break

            if not myteam:
                raise AccountTeamError('该账户不属于"'+TEAM_NAME+'"团队！')

        except (LoginFailed, AccountTeamError) as e:
            on_exception(self, str(e))
        else:
            self.updateConfigs(self.chkRem.isChecked(), self.txtUsername.text(), self.txtPass.text())
            self.loggedIn.emit(username, client, myteam)
            saveConfigs(PATHS.CONF, conf)
            self.close()
