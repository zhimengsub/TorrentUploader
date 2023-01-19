import sys

from PyQt5.QtWidgets import QApplication

from utils.gui.sources import init_icons
from windows.wndMain import WndMain

app = QApplication(sys.argv)
init_icons()
mainwindow = WndMain()
mainwindow.show()
sys.exit(app.exec_())
