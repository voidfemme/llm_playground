# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'MainWindow.ui'
#
# Created by: PyQt5 UI code generator 5.15.10
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1035, 905)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setGeometry(QtCore.QRect(0, 0, 971, 871))
        self.tabWidget.setObjectName("tabWidget")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.activeToolsListWidget = QtWidgets.QListWidget(self.tab)
        self.activeToolsListWidget.setGeometry(QtCore.QRect(0, 550, 261, 281))
        self.activeToolsListWidget.setObjectName("activeToolsListWidget")
        self.sendMessagePushButton = QtWidgets.QPushButton(self.tab)
        self.sendMessagePushButton.setGeometry(QtCore.QRect(710, 730, 231, 91))
        self.sendMessagePushButton.setObjectName("sendMessagePushButton")
        self.activeToolsLabel = QtWidgets.QLabel(self.tab)
        self.activeToolsLabel.setGeometry(QtCore.QRect(3, 530, 251, 20))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.activeToolsLabel.setFont(font)
        self.activeToolsLabel.setObjectName("activeToolsLabel")
        self.conversationListView = QtWidgets.QListView(self.tab)
        self.conversationListView.setGeometry(QtCore.QRect(0, 30, 261, 491))
        self.conversationListView.setObjectName("conversationListView")
        self.comboBox = QtWidgets.QComboBox(self.tab)
        self.comboBox.setGeometry(QtCore.QRect(710, 700, 231, 25))
        self.comboBox.setObjectName("comboBox")
        self.messageScrollArea = QtWidgets.QScrollArea(self.tab)
        self.messageScrollArea.setGeometry(QtCore.QRect(270, 10, 681, 681))
        self.messageScrollArea.setWidgetResizable(True)
        self.messageScrollArea.setObjectName("messageScrollArea")
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 679, 679))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.verticalScrollBar = QtWidgets.QScrollBar(self.scrollAreaWidgetContents)
        self.verticalScrollBar.setGeometry(QtCore.QRect(660, 0, 16, 681))
        self.verticalScrollBar.setOrientation(QtCore.Qt.Vertical)
        self.verticalScrollBar.setObjectName("verticalScrollBar")
        self.messageScrollArea.setWidget(self.scrollAreaWidgetContents)
        self.sendMessageTextEdit = QtWidgets.QTextEdit(self.tab)
        self.sendMessageTextEdit.setGeometry(QtCore.QRect(270, 700, 431, 131))
        self.sendMessageTextEdit.setObjectName("sendMessageTextEdit")
        self.conversationsLabel = QtWidgets.QLabel(self.tab)
        self.conversationsLabel.setGeometry(QtCore.QRect(0, 10, 261, 20))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.conversationsLabel.setFont(font)
        self.conversationsLabel.setObjectName("conversationsLabel")
        self.tabWidget.addTab(self.tab, "")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.savedToolsListView = QtWidgets.QListView(self.tab_2)
        self.savedToolsListView.setGeometry(QtCore.QRect(0, 30, 261, 801))
        self.savedToolsListView.setObjectName("savedToolsListView")
        self.savedToolsLabel = QtWidgets.QLabel(self.tab_2)
        self.savedToolsLabel.setGeometry(QtCore.QRect(0, 10, 251, 21))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.savedToolsLabel.setFont(font)
        self.savedToolsLabel.setObjectName("savedToolsLabel")
        self.toolNameLabel = QtWidgets.QLabel(self.tab_2)
        self.toolNameLabel.setGeometry(QtCore.QRect(270, 20, 101, 21))
        self.toolNameLabel.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.toolNameLabel.setObjectName("toolNameLabel")
        self.toolDescriptionLabel = QtWidgets.QLabel(self.tab_2)
        self.toolDescriptionLabel.setGeometry(QtCore.QRect(270, 60, 101, 20))
        self.toolDescriptionLabel.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.toolDescriptionLabel.setObjectName("toolDescriptionLabel")
        self.inputSchemaLabel = QtWidgets.QLabel(self.tab_2)
        self.inputSchemaLabel.setGeometry(QtCore.QRect(270, 140, 101, 20))
        self.inputSchemaLabel.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.inputSchemaLabel.setObjectName("inputSchemaLabel")
        self.functionCodeLabel = QtWidgets.QLabel(self.tab_2)
        self.functionCodeLabel.setGeometry(QtCore.QRect(270, 470, 101, 20))
        self.functionCodeLabel.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.functionCodeLabel.setObjectName("functionCodeLabel")
        self.apiKeyLabel = QtWidgets.QLabel(self.tab_2)
        self.apiKeyLabel.setGeometry(QtCore.QRect(270, 710, 91, 20))
        self.apiKeyLabel.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.apiKeyLabel.setObjectName("apiKeyLabel")
        self.toolNameLineEdit = QtWidgets.QLineEdit(self.tab_2)
        self.toolNameLineEdit.setGeometry(QtCore.QRect(380, 20, 331, 25))
        self.toolNameLineEdit.setObjectName("toolNameLineEdit")
        self.toolDescriptionTextEdit = QtWidgets.QTextEdit(self.tab_2)
        self.toolDescriptionTextEdit.setGeometry(QtCore.QRect(380, 60, 331, 70))
        self.toolDescriptionTextEdit.setObjectName("toolDescriptionTextEdit")
        self.inputSchemaTableView = QtWidgets.QTableView(self.tab_2)
        self.inputSchemaTableView.setGeometry(QtCore.QRect(380, 140, 331, 311))
        self.inputSchemaTableView.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.inputSchemaTableView.setObjectName("inputSchemaTableView")
        self.apiLineEdit = QtWidgets.QLineEdit(self.tab_2)
        self.apiLineEdit.setGeometry(QtCore.QRect(380, 700, 331, 25))
        self.apiLineEdit.setObjectName("apiLineEdit")
        self.toolFunctionTextEdit = QtWidgets.QPlainTextEdit(self.tab_2)
        self.toolFunctionTextEdit.setGeometry(QtCore.QRect(380, 460, 331, 231))
        self.toolFunctionTextEdit.setObjectName("toolFunctionTextEdit")
        self.addSchemaPushButton = QtWidgets.QPushButton(self.tab_2)
        self.addSchemaPushButton.setGeometry(QtCore.QRect(280, 170, 80, 25))
        self.addSchemaPushButton.setObjectName("addSchemaPushButton")
        self.removeSchemaPushButton = QtWidgets.QPushButton(self.tab_2)
        self.removeSchemaPushButton.setGeometry(QtCore.QRect(280, 200, 80, 25))
        self.removeSchemaPushButton.setObjectName("removeSchemaPushButton")
        self.editToolPushButton = QtWidgets.QPushButton(self.tab_2)
        self.editToolPushButton.setGeometry(QtCore.QRect(540, 730, 80, 25))
        self.editToolPushButton.setObjectName("editToolPushButton")
        self.saveToolPushButton = QtWidgets.QPushButton(self.tab_2)
        self.saveToolPushButton.setGeometry(QtCore.QRect(630, 730, 80, 25))
        self.saveToolPushButton.setObjectName("saveToolPushButton")
        self.tabWidget.addTab(self.tab_2, "")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1035, 22))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menuNew = QtWidgets.QMenu(self.menuFile)
        self.menuNew.setObjectName("menuNew")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionNewConversation = QtWidgets.QAction(MainWindow)
        self.actionNewConversation.setObjectName("actionNewConversation")
        self.actionNewTool = QtWidgets.QAction(MainWindow)
        self.actionNewTool.setObjectName("actionNewTool")
        self.actionSettings = QtWidgets.QAction(MainWindow)
        self.actionSettings.setObjectName("actionSettings")
        self.menuNew.addAction(self.actionNewConversation)
        self.menuNew.addAction(self.actionNewTool)
        self.menuFile.addAction(self.menuNew.menuAction())
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionSettings)
        self.menubar.addAction(self.menuFile.menuAction())

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.sendMessagePushButton.setText(_translate("MainWindow", "Send"))
        self.activeToolsLabel.setText(_translate("MainWindow", "Active Tools"))
        self.conversationsLabel.setText(_translate("MainWindow", "Conversations"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("MainWindow", "Chat"))
        self.savedToolsLabel.setText(_translate("MainWindow", "Saved Tools"))
        self.toolNameLabel.setText(_translate("MainWindow", "Tool Name:"))
        self.toolDescriptionLabel.setText(_translate("MainWindow", "Tool Description:"))
        self.inputSchemaLabel.setText(_translate("MainWindow", "Input Schema:"))
        self.functionCodeLabel.setText(_translate("MainWindow", "Function Code:"))
        self.apiKeyLabel.setText(_translate("MainWindow", "API Key:"))
        self.addSchemaPushButton.setToolTip(_translate("MainWindow", "Add a field to the schema"))
        self.addSchemaPushButton.setText(_translate("MainWindow", "+"))
        self.removeSchemaPushButton.setToolTip(_translate("MainWindow", "Remove selected field from the schema"))
        self.removeSchemaPushButton.setText(_translate("MainWindow", "-"))
        self.editToolPushButton.setText(_translate("MainWindow", "Edit"))
        self.saveToolPushButton.setText(_translate("MainWindow", "Save"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("MainWindow", "Tools"))
        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.menuNew.setTitle(_translate("MainWindow", "New"))
        self.actionNewConversation.setText(_translate("MainWindow", "Conversation"))
        self.actionNewTool.setText(_translate("MainWindow", "Tool"))
        self.actionSettings.setText(_translate("MainWindow", "Settings"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())