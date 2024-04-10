# message_widget.py

import logging
from typing import TYPE_CHECKING
from PyQt5.QtWidgets import (
    QWidget,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QMenu,
)
from PyQt5.QtCore import Qt

from src.model.conversation_manager import Message, Response

if TYPE_CHECKING:
    from src.presenters.conversation_presenter import ConversationPresenter


class MessageWidget(QWidget):
    def __init__(
        self,
        message: Message,
        conversation_id: str,
        branch_id: str,
        conversation_presenter: "ConversationPresenter",
    ) -> None:
        super().__init__()
        self.message = message
        self.conversation_presenter = conversation_presenter
        self.conversation_id = conversation_id
        self.branch_id = branch_id
        self.hamburger_menu = None
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()

        header_layout = QHBoxLayout()
        header_layout.addStretch()

        self.hamburger_menu = QPushButton("☰")
        self.hamburger_menu.setObjectName("hamburger_menu")
        self.hamburger_menu.setStyleSheet("background: none; border: none;")
        self.hamburger_menu.clicked.connect(self.on_hamburger_menu_clicked)
        header_layout.addWidget(self.hamburger_menu)

        main_layout.addLayout(header_layout)

        user_label = QLabel(self.message.text)
        user_label.setObjectName("user_label")
        user_label.setWordWrap(True)
        user_label.setAlignment(Qt.AlignRight)  # type: ignore
        # Add more styles for user messages
        main_layout.addWidget(user_label)

        if self.message.response:
            assistant_label = QLabel(self.message.response.text)
            assistant_label.setObjectName("assistant_label")
            assistant_label.setWordWrap(True)
            assistant_label.setAlignment(Qt.AlignLeft)  # type: ignore
            # Add more styles for assistant messages
            main_layout.addWidget(assistant_label)

        footer_layout = QHBoxLayout()
        footer_layout.addStretch()

        self.left_arrow = QPushButton("←")
        self.left_arrow.setObjectName("left_arrow")
        self.left_arrow.setStyleSheet("background: none; border: none;")
        self.left_arrow.clicked.connect(self.on_left_arrow_clicked)
        footer_layout.addWidget(self.left_arrow)

        self.right_arrow = QPushButton("→")
        self.right_arrow.setObjectName("right_arrow")
        self.right_arrow.setStyleSheet("background: none; border: none;")
        self.right_arrow.clicked.connect(self.on_right_arrow_clicked)
        footer_layout.addWidget(self.right_arrow)

        main_layout.addLayout(footer_layout)

        self.setLayout(main_layout)

    def on_hamburger_menu_clicked(self):
        if self.hamburger_menu:
            menu = QMenu(self)
            new_branch_action = menu.addAction("Create a new branch")
            prompt_helpers_action = menu.addAction("Use prompt helpers")
            delete_action = menu.addAction("Delete message")
            new_conversation_action = menu.addAction(
                "Start a new conversation with this message"
            )
            regenerate_action = menu.addAction("Regenerate response")

            action = menu.exec_(
                self.hamburger_menu.mapToGlobal(self.hamburger_menu.rect().bottomLeft())
            )

            if action == new_branch_action:
                # Handle creating a new branch
                pass
            elif action == prompt_helpers_action:
                # Handle using prompt helpers
                pass
            elif action == delete_action:
                # Handle deleting the message
                pass
            elif action == new_conversation_action:
                # Handle starting a new conversation with the message
                pass
            elif action == regenerate_action:
                self.on_regenerate_response()

    def on_left_arrow_clicked(self):
        # Handle left arrow click event
        pass

    def on_right_arrow_clicked(self):
        # Handle right arrow click event
        pass

    def on_regenerate_response(self):
        result = self.conversation_presenter.conversation_manager.regenerate_response(
            self.conversation_id, self.branch_id, self.message.id
        )
        if result:
            branch, message = result
            self.conversation_presenter.update_conversation_view(branch.id)
