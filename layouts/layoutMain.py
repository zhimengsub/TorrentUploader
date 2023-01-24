# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'layouts\layoutMain.ui'
#
# Created by: PyQt5 UI code generator 5.15.7
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(721, 545)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setContentsMargins(-1, -1, -1, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.frame = QtWidgets.QFrame(self.centralwidget)
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.frame)
        self.horizontalLayout.setContentsMargins(-1, 0, -1, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.labAccnt = QtWidgets.QLabel(self.frame)
        self.labAccnt.setObjectName("labAccnt")
        self.horizontalLayout.addWidget(self.labAccnt)
        self.labAccntDisp = QtWidgets.QLabel(self.frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.labAccntDisp.sizePolicy().hasHeightForWidth())
        self.labAccntDisp.setSizePolicy(sizePolicy)
        self.labAccntDisp.setWordWrap(True)
        self.labAccntDisp.setObjectName("labAccntDisp")
        self.horizontalLayout.addWidget(self.labAccntDisp)
        self.btnLogin = QtWidgets.QPushButton(self.frame)
        self.btnLogin.setObjectName("btnLogin")
        self.horizontalLayout.addWidget(self.btnLogin)
        self.btnTest = QtWidgets.QPushButton(self.frame)
        self.btnTest.setObjectName("btnTest")
        self.horizontalLayout.addWidget(self.btnTest)
        self.verticalLayout.addWidget(self.frame)
        self.frame_2 = QtWidgets.QFrame(self.centralwidget)
        self.frame_2.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_2.setObjectName("frame_2")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.frame_2)
        self.horizontalLayout_2.setContentsMargins(-1, 0, -1, 0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.labRoot = QtWidgets.QLabel(self.frame_2)
        self.labRoot.setObjectName("labRoot")
        self.horizontalLayout_2.addWidget(self.labRoot)
        self.labRootDisp = QtWidgets.QLabel(self.frame_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.labRootDisp.sizePolicy().hasHeightForWidth())
        self.labRootDisp.setSizePolicy(sizePolicy)
        self.labRootDisp.setObjectName("labRootDisp")
        self.horizontalLayout_2.addWidget(self.labRootDisp)
        self.btnBrowse = QtWidgets.QPushButton(self.frame_2)
        self.btnBrowse.setObjectName("btnBrowse")
        self.horizontalLayout_2.addWidget(self.btnBrowse)
        self.verticalLayout.addWidget(self.frame_2)
        self.frame_4 = QtWidgets.QFrame(self.centralwidget)
        self.frame_4.setObjectName("frame_4")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.frame_4)
        self.horizontalLayout_4.setContentsMargins(-1, 0, -1, 0)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.tab = QtWidgets.QTabWidget(self.frame_4)
        self.tab.setObjectName("tab")
        self.pgTodo = QtWidgets.QWidget()
        self.pgTodo.setObjectName("pgTodo")
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout(self.pgTodo)
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.viewTodo = QtWidgets.QTableView(self.pgTodo)
        font = QtGui.QFont()
        font.setPointSize(9)
        self.viewTodo.setFont(font)
        self.viewTodo.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.viewTodo.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.viewTodo.setHorizontalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        self.viewTodo.setObjectName("viewTodo")
        self.viewTodo.horizontalHeader().setHighlightSections(False)
        self.viewTodo.verticalHeader().setVisible(False)
        self.viewTodo.verticalHeader().setHighlightSections(False)
        self.horizontalLayout_5.addWidget(self.viewTodo)
        self.tab.addTab(self.pgTodo, "")
        self.pgDone = QtWidgets.QWidget()
        self.pgDone.setObjectName("pgDone")
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout(self.pgDone)
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.viewDone = QtWidgets.QTableView(self.pgDone)
        font = QtGui.QFont()
        font.setPointSize(9)
        self.viewDone.setFont(font)
        self.viewDone.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.viewDone.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.viewDone.setHorizontalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        self.viewDone.setObjectName("viewDone")
        self.viewDone.horizontalHeader().setHighlightSections(False)
        self.viewDone.verticalHeader().setVisible(False)
        self.viewDone.verticalHeader().setHighlightSections(False)
        self.horizontalLayout_6.addWidget(self.viewDone)
        self.tab.addTab(self.pgDone, "")
        self.horizontalLayout_4.addWidget(self.tab)
        self.verticalLayout.addWidget(self.frame_4)
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 721, 23))
        self.menubar.setObjectName("menubar")
        self.menu = QtWidgets.QMenu(self.menubar)
        self.menu.setObjectName("menu")
        self.menu_2 = QtWidgets.QMenu(self.menubar)
        self.menu_2.setObjectName("menu_2")
        MainWindow.setMenuBar(self.menubar)
        self.actShowLog = QtWidgets.QAction(MainWindow)
        self.actShowLog.setObjectName("actShowLog")
        self.actSettings = QtWidgets.QAction(MainWindow)
        self.actSettings.setObjectName("actSettings")
        self.menu.addAction(self.actShowLog)
        self.menu_2.addAction(self.actSettings)
        self.menubar.addAction(self.menu_2.menuAction())
        self.menubar.addAction(self.menu.menuAction())

        self.retranslateUi(MainWindow)
        self.tab.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "萌番组发布工具 - 织梦字幕组"))
        self.labAccnt.setText(_translate("MainWindow", "当前账号："))
        self.labAccntDisp.setText(_translate("MainWindow", "未登录"))
        self.btnLogin.setText(_translate("MainWindow", "登录..."))
        self.btnTest.setText(_translate("MainWindow", "PushButton"))
        self.labRoot.setText(_translate("MainWindow", "工作目录："))
        self.labRootDisp.setText(_translate("MainWindow", "未选择"))
        self.btnBrowse.setText(_translate("MainWindow", "浏览..."))
        self.tab.setTabText(self.tab.indexOf(self.pgTodo), _translate("MainWindow", "待发布"))
        self.tab.setTabText(self.tab.indexOf(self.pgDone), _translate("MainWindow", "已发布"))
        self.menu.setTitle(_translate("MainWindow", "帮助"))
        self.menu_2.setTitle(_translate("MainWindow", "选项"))
        self.actShowLog.setText(_translate("MainWindow", "查看日志..."))
        self.actSettings.setText(_translate("MainWindow", "设置"))
