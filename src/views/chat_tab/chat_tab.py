from PyQt5 import QtCore, QtGui, QtWidgets
from src.model.conversation_dataclasses import Conversation
from src.presenters.conversation_presenter import ConversationPresenter
from src.utils.file_logger import UI_LOG_FILE_PATH, log_function_call
from src.views.chat_tab.active_tools_list import ActiveToolsList
from src.views.chat_tab.conversation_list import ConversationList
from src.views.chat_tab.message_scroll_area import MessageScrollArea
from src.views.chat_tab.send_message_button import SendMessageButton
from src.views.chat_tab.send_message_text_edit import SendMessageTextEdit


class ChatTab(QtWidgets.QWidget):
    def __init__(self, presenter: ConversationPresenter, parent=None):
        super().__init__(parent)
        self.presenter = presenter
        self.setupUi(self)
        self.presenter.load_conversations()
        self.update_conversation_list(self.presenter.get_conversations())

    def setupUi(self, tab):
        log_function_call(UI_LOG_FILE_PATH, "ChatTab.setupUi", tab=tab)
        tab.setObjectName("tab")

        self.activeToolsListWidget = ActiveToolsList(tab)
        self.sendMessagePushButton = SendMessageButton(tab)
        self.activeToolsLabel = QtWidgets.QLabel(tab)
        self.activeToolsLabel.setGeometry(QtCore.QRect(3, 530, 251, 20))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.activeToolsLabel.setFont(font)
        self.activeToolsLabel.setObjectName("activeToolsLabel")

        self.conversationListView = ConversationList(tab)
        self.comboBox = QtWidgets.QComboBox(tab)
        self.comboBox.setGeometry(QtCore.QRect(710, 700, 231, 25))
        self.comboBox.setObjectName("comboBox")

        self.messageScrollArea = MessageScrollArea(tab)
        self.sendMessageTextEdit = SendMessageTextEdit(tab)

        self.conversationsLabel = QtWidgets.QLabel(tab)
        self.conversationsLabel.setGeometry(QtCore.QRect(0, 10, 261, 20))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.conversationsLabel.setFont(font)
        self.conversationsLabel.setObjectName("conversationsLabel")
        self.conversationsLabel.setText("Conversations")

    def send_message(self):
        log_function_call(UI_LOG_FILE_PATH, "ChatTab.send_message")
        text = self.sendMessageTextEdit.toPlainText()
        conversation_id = (
            self.conversationListView.get_selected_conversation_id()
        )  # Implement this method
        if text.strip():  # Ensure we're not sending empty messages
            self.presenter.send_message(conversation_id, text)
            self.sendMessageTextEdit.clear()

    def update_conversation_display(self, conversation_id):
        log_function_call(
            UI_LOG_FILE_PATH,
            "ChatTab.update_conversation_display",
            conversation_id=conversation_id,
        )
        messages = self.presenter.get_messages(conversation_id)
        self.messageScrollArea.display_messages(messages)

    def update_conversation_list(self, conversations):
        log_function_call(
            UI_LOG_FILE_PATH,
            "ChatTab.update_conversation_list",
            number_of_conversations=len(conversations),
        )
        model = QtGui.QStandardItemModel()
        for conversation in conversations:
            item = QtGui.QStandardItem(conversation.title)
            item.setData(conversation.id, QtCore.Qt.UserRole)  # type: ignore
            model.appendRow(item)
        self.conversationListView.setModel(model)

        # Connect the selectionChanged signal after setting the model
        self.conversationListView.selectionModel().selectionChanged.connect(
            self.on_conversation_selected
        )

    def on_conversation_selected(self):
        log_function_call(UI_LOG_FILE_PATH, "ChatTab.on_conversation_selected")
        selected_indicies = self.conversationListView.selectedIndexes()
        if selected_indicies:
            conversation_id = selected_indicies[0].data(QtCore.Qt.UserRole)  # type: ignore
            self.display_conversation(conversation_id)

    def display_conversation(self, conversation_id):
        log_function_call(
            UI_LOG_FILE_PATH,
            "ChatTab.display_conversation",
            conversation_id=conversation_id,
        )
        conversation = self.presenter.get_conversation(conversation_id)
        messages = self.presenter.get_messages(conversation_id)
        self.messageScrollArea.display_messages(messages)

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.activeToolsLabel.setText(_translate("ChatTab", "Active Tools"))
        self.conversationsLabel.setText(_translate("ChatTab", "Conversations"))
        self.sendMessagePushButton.setText(_translate("ChatTab", "Send"))

        # If the SendMessageButton or other widgets have additional translatable attributes like
        # tooltips, include them here.
        self.sendMessagePushButton.setToolTip(
            _translate("ChatTab", "Click to send message")
        )
