# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'layouts\layoutLogin.ui'
#
# Created by: PyQt5 UI code generator 5.15.7
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_dlgLogin(object):
    def setupUi(self, dlgLogin):
        dlgLogin.setObjectName("dlgLogin")
        dlgLogin.resize(372, 210)
        self.verticalLayout = QtWidgets.QVBoxLayout(dlgLogin)
        self.verticalLayout.setContentsMargins(40, 20, 40, 30)
        self.verticalLayout.setSpacing(20)
        self.verticalLayout.setObjectName("verticalLayout")
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setLabelAlignment(QtCore.Qt.AlignCenter)
        self.formLayout.setFormAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.formLayout.setVerticalSpacing(15)
        self.formLayout.setObjectName("formLayout")
        self.labUsername = QtWidgets.QLabel(dlgLogin)
        self.labUsername.setObjectName("labUsername")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.labUsername)
        self.txtUsername = QtWidgets.QLineEdit(dlgLogin)
        self.txtUsername.setClearButtonEnabled(True)
        self.txtUsername.setObjectName("txtUsername")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.txtUsername)
        self.labPass = QtWidgets.QLabel(dlgLogin)
        self.labPass.setObjectName("labPass")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.labPass)
        self.txtPass = QtWidgets.QLineEdit(dlgLogin)
        self.txtPass.setEchoMode(QtWidgets.QLineEdit.Password)
        self.txtPass.setClearButtonEnabled(True)
        self.txtPass.setObjectName("txtPass")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.txtPass)
        self.verticalLayout.addLayout(self.formLayout)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.chkAutoLog = QtWidgets.QCheckBox(dlgLogin)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.chkAutoLog.sizePolicy().hasHeightForWidth())
        self.chkAutoLog.setSizePolicy(sizePolicy)
        self.chkAutoLog.setObjectName("chkAutoLog")
        self.horizontalLayout.addWidget(self.chkAutoLog)
        self.chkRem = QtWidgets.QCheckBox(dlgLogin)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.chkRem.sizePolicy().hasHeightForWidth())
        self.chkRem.setSizePolicy(sizePolicy)
        self.chkRem.setObjectName("chkRem")
        self.horizontalLayout.addWidget(self.chkRem)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.btnSubmit = QtWidgets.QPushButton(dlgLogin)
        self.btnSubmit.setMinimumSize(QtCore.QSize(0, 35))
        self.btnSubmit.setAutoDefault(False)
        self.btnSubmit.setObjectName("btnSubmit")
        self.verticalLayout.addWidget(self.btnSubmit)

        self.retranslateUi(dlgLogin)
        QtCore.QMetaObject.connectSlotsByName(dlgLogin)

    def retranslateUi(self, dlgLogin):
        _translate = QtCore.QCoreApplication.translate
        dlgLogin.setWindowTitle(_translate("dlgLogin", "登录"))
        self.labUsername.setText(_translate("dlgLogin", "用户名"))
        self.labPass.setText(_translate("dlgLogin", "密码"))
        self.chkAutoLog.setText(_translate("dlgLogin", "自动登录"))
        self.chkRem.setText(_translate("dlgLogin", "记住密码"))
        self.btnSubmit.setText(_translate("dlgLogin", "登录"))
