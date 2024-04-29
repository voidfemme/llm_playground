from PyQt5 import QtCore, QtGui, QtWidgets
from src.presenters.conversation_presenter import ConversationPresenter
from src.utils.file_logger import UI_LOG_FILE_PATH, log_function_call
from src.views.chat_tab.chat_tab import ChatTab
from src.views.tools_tab.tools_tab import ToolsTab
from src.views.main_window.menu_bar import MenuBar


class Ui_MainWindow(object):
    def setupUi(self, MainWindow, presenter: ConversationPresenter):
        log_function_call(
            UI_LOG_FILE_PATH,
            "Ui_MainWindow.setupUi",
            MainWindow=MainWindow,
            presenter=presenter,
        )
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1035, 905)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setGeometry(QtCore.QRect(0, 0, 971, 871))
        self.tabWidget.setObjectName("tabWidget")
        self.presenter = presenter

        self.tab = ChatTab(self.presenter, self.tabWidget)
        self.tabWidget.addTab(self.tab, "")

        self.tab_2 = ToolsTab(self.tabWidget)
        self.tabWidget.addTab(self.tab_2, "")

        MainWindow.setCentralWidget(self.centralwidget)

        self.menubar = MenuBar(MainWindow)
        MainWindow.setMenuBar(self.menubar)

        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        log_function_call(
            UI_LOG_FILE_PATH, "Ui_MainWindow.retranslateUi", MainWindow=MainWindow
        )
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.tab), _translate("MainWindow", "Chat")
        )
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.tab_2), _translate("MainWindow", "Tools")
        )
        # Update texts in ToolsTab
        self.tab_2.retranslateUi()
        # Update texts in ChatTab
        self.tab.retranslateUi()
