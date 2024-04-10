from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import (
    QComboBox,
    QFileDialog,
    QInputDialog,
    QMainWindow,
    QMenu,
    QMessageBox,
    QScrollArea,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QListWidget,
    QTextEdit,
    QPushButton,
)
from src.model.conversation_manager import Message
from src.presenters.conversation_presenter import ConversationPresenter
from src.presenters.message_presenter import MessagePresenter
from src.utils.file_logger import LOG_FILE_PATH, log_function_call, log_variable
from src.utils.error_handling import (
    ChatbotError,
    ConversationManagerError,
    InvalidMessageError,
)


class MainWindowView(QMainWindow):
    new_conversation_requested = pyqtSignal()
    delete_conversation_requested = pyqtSignal()

    def __init__(self, conversation_presenter: ConversationPresenter | None):
        super().__init__()
        self.message_presenter: MessagePresenter | None = None
        self.setWindowTitle("LLM Playground")
        self.setGeometry(100, 100, 1000, 600)
        self.conversation_presenter = conversation_presenter

        # Create the central widget and layout
        central_widget = QWidget(self)
        central_layout = QHBoxLayout(central_widget)
        self.setCentralWidget(central_widget)

        # Create the conversation list widget
        self.conversation_list = QListWidget()
        self.conversation_list.setMinimumWidth(200)
        central_layout.addWidget(self.conversation_list)
        central_layout.setStretchFactor(self.conversation_list, 1)

        # Create the right-side layout
        right_layout = QVBoxLayout()
        central_layout.addLayout(right_layout)
        central_layout.setStretchFactor(right_layout, 3)

        # Create the conversation scroll area
        self.add_conversation_scroll_area = QScrollArea()
        self.add_conversation_scroll_area.setWidgetResizable(True)
        right_layout.addWidget(self.add_conversation_scroll_area)
        right_layout.setStretchFactor(self.add_conversation_scroll_area, 3)

        # Create a container widget for the message widgets
        self.conversation_container = QWidget()
        self.conversation_layout = QVBoxLayout(self.conversation_container)
        self.add_conversation_scroll_area.setWidget(self.conversation_container)

        # Create the input layout
        input_layout = QHBoxLayout()
        right_layout.addLayout(input_layout)

        # Create the input text widget
        self.input_text = QTextEdit()
        self.input_text.setFixedHeight(100)
        input_layout.addWidget(self.input_text)

        # Create the chatbot selection combo box
        self.chatbot_combo_box = QComboBox()
        self.chatbot_combo_box.addItem("Claude 3 Opus")
        self.chatbot_combo_box.addItem("Claude 3 Sonnet")
        self.chatbot_combo_box.addItem("Claude 3 Haiku")
        self.chatbot_combo_box.addItem("OpenAI 3.5")
        self.chatbot_combo_box.addItem("OpenAI 4.5")
        input_layout.addWidget(self.chatbot_combo_box)

        # Create the attach document button
        self.attach_button = QPushButton("Attach Document")
        self.attach_button.clicked.connect(self.on_attach_document)
        input_layout.addWidget(self.attach_button)

        # Create the send button
        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.on_send_button_clicked)
        input_layout.addWidget(self.send_button)

        # Create the conversation-level hamburger menu
        self.conversation_menu = QMenu(self)
        self.conversation_menu.addAction(
            "Start a new conversation", self.on_new_conversation
        )
        self.conversation_menu.addAction(
            "Delete current conversation", self.on_delete_conversation
        )
        self.conversation_menu.addAction(
            "Rename conversation", self.on_rename_conversation
        )
        self.conversation_menu.addAction("Apply conversation-level prompt helpers")
        self.conversation_menu.addAction("Export conversation data")
        self.conversation_menu.addAction("Import conversation data")

        # Create the hamburger menu button
        self.hamburger_button = QPushButton("☰")
        self.hamburger_button.setStyleSheet("background: none; border: none;")
        self.hamburger_button.setMenu(self.conversation_menu)
        self.hamburger_button.setFixedSize(30, 30)

        # Add the hamburger button to the top-right corner of the conversation view
        hamburger_layout = QHBoxLayout()
        hamburger_layout.addStretch()
        hamburger_layout.addWidget(self.hamburger_button)
        right_layout.insertLayout(0, hamburger_layout)

        # Status bar
        self.init_status_bar()

    def init_status_bar(self):
        self.status_bar = self.statusBar()
        self.set_status_message("Ready")

    def set_status_message(self, message: str):
        if self.status_bar:
            self.status_bar.showMessage(message)

    def show_error_dialog(self, error_message: str):
        error_dialog = QMessageBox(self)
        error_dialog.setIcon(QMessageBox.Critical)
        error_dialog.setWindowTitle("Error")
        error_dialog.setText("An error occurred:")
        error_dialog.setDetailedText(error_message)
        error_dialog.exec_()

    def on_new_conversation(self):
        self.set_status_message("Creating a new conversation...")
        try:
            self.new_conversation_requested.emit()
            self.set_status_message("New conversation created.")
        except (ChatbotError, ConversationManagerError) as e:
            self.set_status_message("Failed to create a new conversation.")
            self.show_error_dialog(str(e))
        except Exception as e:
            self.set_status_message("An unexpected error occurred.")
            self.show_error_dialog(str(e))

    def on_delete_conversation(self):
        self.set_status_message("Deleting the current conversation...")
        try:
            self.delete_conversation_requested.emit()
            self.set_status_message("Conversation deleted.")
        except (ChatbotError, ConversationManagerError) as e:
            self.set_status_message("Failed to delete the conversation.")
            self.show_error_dialog(str(e))
        except Exception as e:
            self.set_status_message("An unexpected error occurred.")
            self.show_error_dialog(str(e))

    def on_rename_conversation(self):
        if (
            self.conversation_presenter
            and self.conversation_presenter.current_conversation
        ):
            current_title = self.conversation_presenter.current_conversation.title
            new_title, ok = QInputDialog.getText(
                self, "Rename Conversation", "Enter a new title:", text=current_title
            )
            if ok and new_title:
                self.set_status_message("Renaming the conversation...")
                try:
                    self.conversation_presenter.rename_current_conversation(new_title)
                    self.set_status_message("Conversation renamed.")
                except (ChatbotError, ConversationManagerError) as e:
                    self.set_status_message("Failed to rename the conversation.")
                    self.show_error_dialog(str(e))
                except Exception as e:
                    self.set_status_message("An unexpected error occurred.")
                    self.show_error_dialog(str(e))

    def set_message_presenter(self, message_presenter: MessagePresenter):
        self.message_presenter = message_presenter

    def add_message_widget(
        self,
        message: Message,
        conversation_id: str,
        branch_id: str,
        assistant_response=None,
    ):
        log_function_call(
            LOG_FILE_PATH,
            "MainWindowView.add_message_widget",
            message=message,
            conversation_id=conversation_id,
            branch_id=branch_id,
            assistant_response=assistant_response,
        )

        log_variable(LOG_FILE_PATH, "message_presenter", self.message_presenter)
        if self.message_presenter:
            message_widget = self.message_presenter.create_message_widget(
                message, conversation_id, branch_id
            )
            self.conversation_layout.addWidget(message_widget)

    def clear_message_widgets(self):
        if self.message_presenter:
            self.message_presenter.clear_message_widgets()

    def on_attach_document(self):
        self.set_status_message("Attaching a document...")
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(
            self, "Select Document", "", "All Files (*)"
        )
        if file_path:
            # Handle the selected document file path
            self.set_status_message(f"Document attached: {file_path}")
            print(f"Attached document: {file_path}")
        else:
            self.set_status_message("No document selected.")

    def add_conversation(self, conversation_title):
        self.conversation_list.addItem(conversation_title)

    def set_conversation_text(self, text):
        self.conversation_text.setHtml(text)

    def get_input_text(self):
        return self.input_text.toPlainText()

    def clear_input_text(self):
        self.input_text.clear()

    def on_send_button_clicked(self):
        log_function_call(LOG_FILE_PATH, "MainWindowView.on_send_button_clicked")
        self.set_status_message("Sending message...")
        try:
            input_text = self.get_input_text()
            log_variable(LOG_FILE_PATH, "input_text", input_text)
            if self.conversation_presenter:
                self.conversation_presenter.send_message(input_text)
            self.clear_input_text()
            self.set_status_message("Message sent.")
        except (ChatbotError, ConversationManagerError, InvalidMessageError) as e:
            self.set_status_message("Failed to send message.")
            self.show_error_dialog(str(e))
        except Exception as e:
            self.set_status_message("An unexpected error occurred.")
            self.show_error_dialog(str(e))
