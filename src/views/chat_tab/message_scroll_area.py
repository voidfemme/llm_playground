from PyQt5 import QtCore, QtWidgets
from src.utils.file_logger import UI_LOG_FILE_PATH, log_function_call

from src.views.chat_tab.message_widget import MessageWidget
from src.model.conversation_dataclasses import Message


class MessageScrollArea(QtWidgets.QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

    def setupUi(self, messageScrollArea):
        log_function_call(
            UI_LOG_FILE_PATH,
            "MessageScrollArea.setupUi",
            messageScrollArea=messageScrollArea,
        )
        messageScrollArea.setGeometry(QtCore.QRect(270, 10, 681, 681))
        messageScrollArea.setWidgetResizable(True)
        messageScrollArea.setObjectName("messageScrollArea")

        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 679, 679))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")

        messageScrollArea.setWidget(self.scrollAreaWidgetContents)

        # Initialize the layout for the scrollAreaWidgetContents
        layout = QtWidgets.QVBoxLayout(self.scrollAreaWidgetContents)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.scrollAreaWidgetContents.setLayout(layout)

    def retranslateUi(self, messageScrollArea):
        pass

    def setMessageWidget(self, widget):
        log_function_call(
            UI_LOG_FILE_PATH, "MessageScrollArea.setMessageWidget", widget=widget
        )
        self.scrollAreaWidgetContents.layout().addWidget(widget)  # type: ignore

    def clear(self):
        log_function_call(UI_LOG_FILE_PATH, "MessageScrollArea.clear")
        layout = self.scrollAreaWidgetContents.layout()
        if layout:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()  # type: ignore
                if widget:
                    widget.deleteLater()
        else:
            self.scrollAreaWidgetContents = QtWidgets.QWidget()
            self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
            self.setWidget(self.scrollAreaWidgetContents)
            layout = QtWidgets.QVBoxLayout(self.scrollAreaWidgetContents)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(0)
            self.scrollAreaWidgetContents.setLayout(layout)

    def scrollToBottom(self):
        log_function_call(UI_LOG_FILE_PATH, "MessageScrollArea.scrollToBottom")
        vertical_scroll_bar = self.verticalScrollBar()
        vertical_scroll_bar.setValue(vertical_scroll_bar.maximum())

    def display_messages(self, messages: list[Message]):
        log_function_call(
            UI_LOG_FILE_PATH,
            "MessageScrollArea.display_messages",
            number_of_messages=len(messages),
        )
        self.clear()  # Clear previous messages
        root_messages = [msg for msg in messages if not msg.parent_message_id]
        for message in root_messages:
            self.display_message_recursively(message, messages)
        self.scrollToBottom()

    def display_message_recursively(
        self, message, messages, parent_widget=None, indent_level=0
    ):
        log_function_call(
            UI_LOG_FILE_PATH,
            "MessageScrollArea.display_message_recursively",
            message=message,
            number_of_messages=len(messages),
            parent_widget=parent_widget,
            indent_level=indent_level,
        )
        msg_widget = MessageWidget(message, parent_widget, message.parent_message_id)
        self.scrollAreaWidgetContents.layout().addWidget(msg_widget)

        # Indent the message based on its level in the branching structure
        msg_widget.setStyleSheet(f"margin-left: {indent_level * 20}px;")

        child_messages = [
            msg for msg in messages if msg.parent_message_id == message.id
        ]
        for child_message in child_messages:
            self.display_message_recursively(
                child_message, messages, msg_widget, indent_level + 1
            )
