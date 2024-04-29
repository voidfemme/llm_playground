from PyQt5 import QtCore, QtWidgets

from src.utils.file_logger import UI_LOG_FILE_PATH, log_function_call


class MenuBar(QtWidgets.QMenuBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

    def setupUi(self, menuBar):
        log_function_call(UI_LOG_FILE_PATH, "MenuBar.setupUi", menuBar=menuBar)
        menuBar.setGeometry(QtCore.QRect(0, 0, 1035, 22))
        menuBar.setObjectName("menuBar")

        self.menuFile = QtWidgets.QMenu(menuBar)
        self.menuFile.setObjectName("menuFile")

        self.menuNew = QtWidgets.QMenu(self.menuFile)
        self.menuNew.setObjectName("menuNew")

        self.actionNewConversation = QtWidgets.QAction(menuBar)
        self.actionNewConversation.setObjectName("actionNewConversation")

        self.actionNewTool = QtWidgets.QAction(menuBar)
        self.actionNewTool.setObjectName("actionNewTool")

        self.actionSettings = QtWidgets.QAction(menuBar)
        self.actionSettings.setObjectName("actionSettings")

        self.menuNew.addAction(self.actionNewConversation)
        self.menuNew.addAction(self.actionNewTool)

        self.menuFile.addAction(self.menuNew.menuAction())
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionSettings)

        menuBar.addAction(self.menuFile.menuAction())

    def retranslateUi(self, menuBar):
        log_function_call(UI_LOG_FILE_PATH, "MenuBar.retranslateUi", menuBar=menuBar)
        _translate = QtCore.QCoreApplication.translate
        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.menuNew.setTitle(_translate("MainWindow", "New"))
        self.actionNewConversation.setText(_translate("MainWindow", "Conversation"))
        self.actionNewTool.setText(_translate("MainWindow", "Tool"))
        self.actionSettings.setText(_translate("MainWindow", "Settings"))

    def connectActions(self, newConversationSlot, newToolSlot, settingsSlot):
        log_function_call(
            UI_LOG_FILE_PATH,
            "MenuBar.connectActions",
            newConversationSlot=newConversationSlot,
            newToolSlot=newToolSlot,
            settingsSlot=settingsSlot,
        )
        self.actionNewConversation.triggered.connect(newConversationSlot)
        self.actionNewTool.triggered.connect(newToolSlot)
        self.actionSettings.triggered.connect(settingsSlot)
