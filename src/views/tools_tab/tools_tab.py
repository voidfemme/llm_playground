from PyQt5 import QtCore, QtGui, QtWidgets

from src.views.tools_tab.saved_tools_list import SavedToolsList
from src.views.tools_tab.tool_details import ToolDetails


class ToolsTab(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

    def setupUi(self, tab):
        tab.setObjectName("tab_2")

        self.savedToolsListView = SavedToolsList(tab)

        self.savedToolsLabel = QtWidgets.QLabel(tab)
        self.savedToolsLabel.setGeometry(QtCore.QRect(0, 10, 251, 21))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.savedToolsLabel.setFont(font)
        self.savedToolsLabel.setObjectName("savedToolsLabel")

        self.toolDetails = ToolDetails(tab)

    def setToolsModel(self, model):
        self.savedToolsListView.setModel(model)

    def getSelectedTool(self):
        return self.savedToolsListView.getSelectedTool()

    def setSelectedTool(self, tool):
        self.savedToolsListView.setSelectedTool(tool)
        self.toolDetails.setToolDetails(tool)

    def clearToolDetails(self):
        self.toolDetails.clearToolDetails()

    def getToolDetails(self):
        return self.toolDetails.getToolDetails()

    def connectSavedToolsSelectionChanged(self, slot):
        self.savedToolsListView.selectionModel().currentChanged.connect(slot)  # type: ignore

    def connectAddSchemaButtonClicked(self, slot):
        self.toolDetails.addSchemaPushButton.clicked.connect(slot)

    def connectRemoveSchemaButtonClicked(self, slot):
        self.toolDetails.removeSchemaPushButton.clicked.connect(slot)

    def connectEditToolButtonClicked(self, slot):
        self.toolDetails.editToolPushButton.clicked.connect(slot)

    def connectSaveToolButtonClicked(self, slot):
        self.toolDetails.saveToolPushButton.clicked.connect(slot)

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.savedToolsLabel.setText(_translate("ToolsTab", "Saved Tools"))
        self.toolDetails.retranslateUi()
