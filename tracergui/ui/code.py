# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'code.ui'
#
# Created by: PyQt5 UI code generator 5.7.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtWidgets


class Ui_code(object):
    def setupUi(self, code):
        code.setObjectName("code")
        code.resize(400, 300)
        self.verticalLayout = QtWidgets.QVBoxLayout(code)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.toolButton = QtWidgets.QToolButton(code)
        self.toolButton.setObjectName("toolButton")
        self.horizontalLayout.addWidget(self.toolButton)
        self.btn_load_file = QtWidgets.QToolButton(code)
        self.btn_load_file.setObjectName("btn_load_file")
        self.horizontalLayout.addWidget(self.btn_load_file)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.content = QtWidgets.QPlainTextEdit(code)
        self.content.setObjectName("content")
        self.verticalLayout.addWidget(self.content)

        self.retranslateUi(code)
        QtCore.QMetaObject.connectSlotsByName(code)

    def retranslateUi(self, code):
        _translate = QtCore.QCoreApplication.translate
        code.setWindowTitle(_translate("code", "Form"))
        self.toolButton.setText(_translate("code", "Execute"))
        self.btn_load_file.setText(_translate("code", "Load from file"))
