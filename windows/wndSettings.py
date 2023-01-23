import sys
from pathlib import Path

from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtGui import QIcon, QCursor
from PyQt5.QtWidgets import QApplication, QDialog, QMainWindow, QMessageBox, QLineEdit, QFrame, QAbstractButton, \
    QDialogButtonBox

from core.client import Bangumi
from layouts.layoutSettings import Ui_Settings  # 由Designer+pyuic生成
from utils.configs import conf
from utils.const import BANGUMI_MOE_HOST
from utils.gui.exception_hook import UncaughtHook, on_exception  # 见'exception hook'
from utils.gui.filePicker import FilePicker
from utils.gui.sources import ICONS
from utils.helpers import make_proxies


class WndSettings(QFrame, Ui_Settings):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.retranslateUi(self)
        self.setWindowIcon(ICONS.MAIN)

        # window settings
        self.setWindowFlags(Qt.WindowCloseButtonHint)

        self.verticalLayout.setAlignment(self.btnProxyTest, Qt.AlignRight)

        # exception handling
        err_hook = UncaughtHook()
        err_hook._exception_caught.connect(lambda msg: on_exception(self, msg))

        self.picker = FilePicker(self)

        self.setUiByConf()

    """utils"""
    def setUiByConf(self):
        # torrent
        self.txtPathBC.setText(conf.exe.bc)
        self.chkAutomakeBT.setChecked(conf.autoMakeTorrent)
        # proxies
        self.radProxyOff.setChecked(not conf.proxies.enabled)
        self.radProxyOn.setChecked(conf.proxies.enabled)
        self.groupProxyOn.setEnabled(conf.proxies.enabled)
        self.txtProxyAddr.setText(conf.proxies.addr)
        self.txtProxyPort.setValue(int(conf.proxies.port))

    def updateConfByUi(self):
        conf.exe.bc = self.txtPathBC.text()
        conf.autoMakeTorrent = self.chkAutomakeBT.isChecked()
        conf.proxies.enabled = self.radProxyOn.isChecked()
        conf.proxies.addr = self.txtProxyAddr.text()
        conf.proxies.port = self.txtProxyPort.text()

    """slots"""
    @pyqtSlot()
    def on_btnPathBC_clicked(self):
        path = self.picker.pickBitCometExe(Path(conf.exe.bc or r'C:\Program Files\BitComet\BitComet.exe').parent)
        if path:
            self.txtPathBC.setText(str(path))

    @pyqtSlot(bool)
    def on_radProxyOn_toggled(self, checked: bool):
        self.groupProxyOn.setEnabled(checked)

    @pyqtSlot()
    def on_btnProxyTest_clicked(self):
        proxies = make_proxies(self.txtProxyAddr.text(), self.txtProxyPort.text(), self.radProxyOn.isChecked())
        try:
            Bangumi.test_connection(proxies, BANGUMI_MOE_HOST)
        except Exception as e:
            QMessageBox.critical(self, '连接失败', '\n'.join(
                ['无法连接到'+str(BANGUMI_MOE_HOST), type(e).__name__, str(e)]))
        else:
            QMessageBox.information(self, '连接成功', '成功连接至' + str(BANGUMI_MOE_HOST))

    @pyqtSlot(QAbstractButton)
    def on_buttonBox_clicked(self, btn: QAbstractButton):
        role = self.buttonBox.buttonRole(btn)
        if role == QDialogButtonBox.AcceptRole:
            self.updateConfByUi()
            self.close()
        elif role == QDialogButtonBox.ApplyRole:
            self.updateConfByUi()
        elif role == QDialogButtonBox.RejectRole:
            self.close()


if __name__ == '__main__':
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    wnd = WndSettings()
    wnd.show()
    sys.exit(app.exec_())