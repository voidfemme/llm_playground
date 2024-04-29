from PyQt5 import QtCore, QtWidgets

from src.utils.file_logger import UI_LOG_FILE_PATH, log_function_call


class ConversationList(QtWidgets.QListView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

    def setupUi(self, conversationListView):
        conversationListView.setGeometry(QtCore.QRect(0, 30, 261, 491))
        conversationListView.setObjectName("conversationListView")

    def retranslateUi(self, conversationListView):
        pass

    def setConversationModel(self, model):
        self.setModel(model)

    def getSelectedConversation(self):
        log_function_call(
            UI_LOG_FILE_PATH,
            "ConversationList.getSelectedConversation",
        )
        index = self.currentIndex()
        if index.isValid():
            return index.data(QtCore.Qt.DisplayRole)  # type: ignore
        return None

    def setSelectedConversation(self, conversation):
        log_function_call(
            UI_LOG_FILE_PATH,
            "ConversationList.setSelectedConversation",
            conversation=conversation,
        )
        model = self.model()
        if model:
            matches = model.match(
                model.index(0, 0),
                QtCore.Qt.DisplayRole,  # type: ignore
                conversation,
                1,
                QtCore.Qt.MatchExactly,  # type: ignore
            )
            if matches:
                self.setCurrentIndex(matches[0])
