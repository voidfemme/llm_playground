#!/usr/bin/env python3

# main.py

import sys
import logging
from pathlib import Path
import anthropic
import openai
from PyQt5.QtWidgets import QApplication, QMainWindow
from src.chatbots.adapters.anthropic_api_adapter import AnthropicAdapter
from src.chatbots.adapters.openai_api_adapter import OpenAIAPIAdapter
from src.chatbots.adapters.chatbot_adapter import ChatbotParameters, ChatbotCapabilities
from src.chatbots.chatbot_manager import ChatbotManager
from src.tools.tool_manager import ToolManager
from src.model.conversation_manager import ConversationManager
from src.model.conversation_utils import ConversationUtils
from src.views.main_window.ui_main_window import Ui_MainWindow
from src.utils.file_logger import initialize_log_file, UI_LOG_FILE_PATH
from src.presenters.conversation_presenter import ConversationPresenter

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("app.log"), logging.StreamHandler()],
)

initialize_log_file(UI_LOG_FILE_PATH)

if __name__ == "__main__":
    logging.info("Application started.")
    app = QApplication(sys.argv)

    anthropic_client = anthropic.Client()
    openai_client = openai.Client()

    # Create ChatbotParameters for each chatbot adapter
    claude_opus_parameters = ChatbotParameters(
        model_name="claude-3-opus-20240229",
        system_message="You are Claude, an AI assistant created by Anthropic.",
        max_tokens=500,
        stop_sequences=[],
        temperature=0.7,
        tools=[],
        capabilities=ChatbotCapabilities(
            function_calling=True, image_understanding=True
        ),
    )

    claude_sonnet_parameters = ChatbotParameters(
        model_name="claude-3-sonnet-20240229",
        system_message="You are Claude, an AI assistant created by Anthropic.",
        max_tokens=500,
        stop_sequences=[],
        temperature=0.7,
        tools=[],
        capabilities=ChatbotCapabilities(
            function_calling=True, image_understanding=True
        ),
    )

    claude_haiku_parameters = ChatbotParameters(
        model_name="claude-3-haiku-20240307",
        system_message="You are Claude, an AI assistant created by Anthropic.",
        max_tokens=500,
        stop_sequences=[],
        temperature=0.7,
        tools=[],
        capabilities=ChatbotCapabilities(
            function_calling=False, image_understanding=True
        ),
    )

    openai_parameters = ChatbotParameters(
        model_name="gpt-4-turbo",
        system_message="You are an AI assistant created by OpenAI.",
        max_tokens=500,
        stop_sequences=[],
        temperature=0.7,
        tools=[],
        capabilities=ChatbotCapabilities(
            function_calling=True, image_understanding=True
        ),
    )

    # Create chatbot adapters with the respective parameters
    claude_opus_adapter = AnthropicAdapter(parameters=claude_opus_parameters)
    claude_sonnet_adapter = AnthropicAdapter(parameters=claude_sonnet_parameters)
    claude_haiku_adapter = AnthropicAdapter(parameters=claude_haiku_parameters)
    openai_adapter = OpenAIAPIAdapter(parameters=openai_parameters)

    # Create chatbot manager and register adapters
    chatbot_manager = ChatbotManager()
    chatbot_manager.register_chatbot("claude_opus", claude_opus_adapter)
    chatbot_manager.register_chatbot("claude_sonnet", claude_sonnet_adapter)
    chatbot_manager.register_chatbot("claude_haiku", claude_haiku_adapter)
    chatbot_manager.register_chatbot("openai", openai_adapter)

    conversation_utils = ConversationUtils(
        chatbot_manager, conversation_store=None
    )  # Pass conversation_store if needed

    conversation_manager = ConversationManager(
        chatbot_manager=chatbot_manager,
        conversation_utils=conversation_utils,
        tool_manager=ToolManager(),
        data_dir=Path("data/conversations/"),
    )

    main_window = QMainWindow()
    ui = Ui_MainWindow()
    conversation_presenter = ConversationPresenter(conversation_manager, ui)
    ui.setupUi(main_window, conversation_presenter)

    # TODO: Implement the ConversationPresenter and connect it to the UI components

    main_window.show()
    sys.exit(app.exec_())
    logging.info("Application closed.")
