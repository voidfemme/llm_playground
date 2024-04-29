from PyQt5 import QtCore, QtWidgets


class SavedToolsList(QtWidgets.QListView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

    def setupUi(self, savedToolsListView):
        savedToolsListView.setGeometry(QtCore.QRect(0, 30, 261, 801))
        savedToolsListView.setObjectName("savedToolsListView")

    def retranslateUi(self, savedToolsListView):
        pass

    def setToolsModel(self, model):
        self.setModel(model)

    def getSelectedTool(self):
        index = self.currentIndex()
        if index.isValid():
            return index.data(QtCore.Qt.DisplayRole)  # type: ignore
        return None

    def setSelectedTool(self, tool):
        model = self.model()
        if model:
            matches = model.match(
                model.index(0, 0),
                QtCore.Qt.DisplayRole,  # type: ignore
                tool,
                1,
                QtCore.Qt.MatchExactly,  # type: ignore
            )
            if matches:
                self.setCurrentIndex(matches[0])
