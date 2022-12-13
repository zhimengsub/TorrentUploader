import sys

from PyQt5.QtWidgets import QApplication

from windows.wndMain import WndMain

app = QApplication(sys.argv)
mainwindow = WndMain()
mainwindow.show()
sys.exit(app.exec_())
