from PyQt5 import QtWidgets

from src.utils.file_logger import UI_LOG_FILE_PATH, log_function_call


class MessageWidget(QtWidgets.QWidget):
    def __init__(self, message, parent_widget=None, parent_message=None):
        super().__init__(parent_widget)
        self.message = message
        self.parent_message = parent_message
        self.child_messages = []
        self.initUI()

    def initUI(self):
        log_function_call(UI_LOG_FILE_PATH, "MessageWidget.initUI")
        layout = QtWidgets.QVBoxLayout(self)

        # Header with model name, branch ID, message ID, and parent message ID
        header = QtWidgets.QLabel(
            f"{self.message.response.model if self.message.response else 'User'} "
            f"<{self.message.branch_id}:{self.message.id}> "
            f"(Parent: {self.message.parent_message_id})"
        )
        layout.addWidget(header)

        # User text
        user_text = QtWidgets.QTextEdit(self.message.text)
        user_text.setReadOnly(True)
        layout.addWidget(user_text)

        # Response text
        response_text = QtWidgets.QTextEdit(
            self.message.response.text if self.message.response else ""
        )
        response_text.setReadOnly(True)
        if self.message.response and self.message.response.is_error:
            response_text.setStyleSheet("color: red;")
        layout.addWidget(response_text)

        # Buttons for branching and regeneration
        button_layout = QtWidgets.QHBoxLayout()
        if not self.message.response or not self.message.response.is_error:
            self.left_arrow = QtWidgets.QPushButton("←")
            self.right_arrow = QtWidgets.QPushButton("→")
            button_layout.addWidget(self.left_arrow)
            button_layout.addWidget(self.right_arrow)

        self.regenerate_button = QtWidgets.QPushButton("⟳")
        button_layout.addWidget(self.regenerate_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def on_left_arrow_clicked(self):
        log_function_call(UI_LOG_FILE_PATH, "MessageWidget.on_left_arrow_clicked")
        pass

    def on_right_arrow_clicked(self):
        log_function_call(UI_LOG_FILE_PATH, "MessageWidget.on_right_arrow_clicked")
        pass

    def on_regenerate_clicked(self):
        log_function_call(UI_LOG_FILE_PATH, "MessageWidget.on_regenerate_clicked")
        pass

    def add_child_message(self, message_widget):
        log_function_call(UI_LOG_FILE_PATH, "MessageWidget.add_child_message")
        self.child_messages.append(message_widget)
