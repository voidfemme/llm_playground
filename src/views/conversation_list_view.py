# conversation_list_view.py

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QListWidget, QListWidgetItem
from PyQt5.QtCore import Qt

from src.model.conversation_manager import Conversation


class ConversationListView(QWidget):
    def __init__(self, presenter):
        super().__init__()
        self.presenter = presenter
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.conversation_list = QListWidget()
        self.conversation_list.itemClicked.connect(self.on_item_clicked)
        layout.addWidget(self.conversation_list)
        self.setLayout(layout)

    def on_item_clicked(self, item):
        conversation_id = item.data(Qt.UserRole)  # type: ignore
        self.presenter.on_conversation_selected(conversation_id)

    def add_conversation(self, conversation: Conversation):
        item = QListWidgetItem(conversation.title)
        item.setData(Qt.UserRole, conversation.id)  # type: ignore
        self.conversation_list.addItem(item)

    def clear_conversations(self):
        self.conversation_list.clear()

    def remove_conversation(self, conversation: Conversation):
        items = self.conversation_list.findItems(conversation.title, Qt.MatchExactly)  # type: ignore
        if items:
            item = items[0]
            row = self.conversation_list.row(item)
            self.conversation_list.takeItem(row)

    def update_conversation(self, conversation: Conversation):
        items = self.conversation_list.findItems(conversation.title, Qt.MatchExactly)  # type: ignore
        if items:
            item = items[0]
            item.setText(conversation.title)

    def refresh_conversations(self):
        self.conversation_list.clear()
        for conversation in self.presenter.conversation_manager.conversations:
            self.add_conversation(conversation)
