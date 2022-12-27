import sys

from PyQt5.QtWidgets import QApplication

from windows.wndMain import WndMain


def main():
    app = QApplication(sys.argv)
    main_window = WndMain()
    main_window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
