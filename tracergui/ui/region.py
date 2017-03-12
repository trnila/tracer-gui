# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'region.ui'
#
# Created by: PyQt5 UI code generator 5.7.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtWidgets

class Ui_Region(object):
    def setupUi(self, Region):
        Region.setObjectName("Region")
        Region.resize(800, 601)
        self.centralwidget = QtWidgets.QWidget(Region)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.next = QtWidgets.QPushButton(self.centralwidget)
        self.next.setObjectName("next")
        self.gridLayout.addWidget(self.next, 0, 2, 1, 1)
        self.num = QtWidgets.QSpinBox(self.centralwidget)
        self.num.setObjectName("num")
        self.gridLayout.addWidget(self.num, 0, 1, 1, 1)
        self.prev = QtWidgets.QPushButton(self.centralwidget)
        self.prev.setObjectName("prev")
        self.gridLayout.addWidget(self.prev, 0, 0, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        self.content = TextView(self.centralwidget)
        self.content.setObjectName("content")
        self.verticalLayout.addWidget(self.content)
        self.code = Code(self.centralwidget)
        self.code.setObjectName("code")
        self.verticalLayout.addWidget(self.code)
        Region.setCentralWidget(self.centralwidget)

        self.retranslateUi(Region)
        QtCore.QMetaObject.connectSlotsByName(Region)

    def retranslateUi(self, Region):
        _translate = QtCore.QCoreApplication.translate
        Region.setWindowTitle(_translate("Region", "MainWindow"))
        self.next.setText(_translate("Region", "Next"))
        self.prev.setText(_translate("Region", "Previous"))

from tracergui.widgets.code import Code
from tracergui.widgets.text_view import TextView
