#!/usr/bin/env python3

# main.py

import logging
import anthropic
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout
from src.model.chatbots import AnthropicChatbot
from src.views.conversation_list_view import ConversationListView
from src.model.conversation_manager import Conversation, ConversationManager
from src.views.main_window_view import MainWindowView
from src.presenters.conversation_presenter import ConversationPresenter

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("app.log"), logging.StreamHandler()],
)

if __name__ == "__main__":
    logging.info("Application started.")
    app = QApplication([])

    claude = AnthropicChatbot(anthropic.Client())
    conversation_manager = ConversationManager(
        chatbot=claude, data_dir="data/conversations/"
    )

    main_window = MainWindowView(None)  # Pass None for now
    conversation_list_view = ConversationListView(None)  # Pass None for now
    conversation_presenter = ConversationPresenter(
        main_window, conversation_list_view, conversation_manager
    )

    main_window.conversation_presenter = conversation_presenter
    conversation_list_view.presenter = conversation_presenter

    # Create a layout for the conversation_list widget
    conversation_list_layout = QVBoxLayout()
    conversation_list_layout.addWidget(conversation_list_view)
    main_window.conversation_list.setLayout(conversation_list_layout)

    logging.info("Loading conversations...")
    conversation_presenter.load_conversations()
    logging.info("Conversations loaded.")

    main_window.show()
    app.exec_()
    logging.info("Application closed.")
