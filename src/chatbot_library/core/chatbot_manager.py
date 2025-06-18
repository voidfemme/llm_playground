# src/chatbots/chatbot_manager.py

from typing import Type
from ..adapters.chatbot_adapter import (
    ChatbotAdapter,
    ChatbotParameters,
)


class ChatbotManager:
    def __init__(self) -> None:
        self.chatbots: dict[str, ChatbotAdapter] = {}

    def register_chatbot(self, chatbot_name: str, chatbot_adapter: ChatbotAdapter):
        self.chatbots[chatbot_name] = chatbot_adapter

    def unregister_chatbot(self, chatbot_name: str) -> None:
        if chatbot_name in self.chatbots:
            del self.chatbots[chatbot_name]
        else:
            raise ValueError(
                f"Chatbot '{chatbot_name}' not found.\n"
                f"Available Chatbots: {[chatbot for chatbot in self.chatbots]}"
            )

    def get_chatbot(self, chatbot_name: str) -> ChatbotAdapter:
        chatbot = self.chatbots.get(chatbot_name)
        if not chatbot:
            raise ValueError(
                f"Chatbot '{chatbot_name}' not found.\n"
                f"Available Chatbots: {[chatbot for chatbot in self.chatbots]}"
            )
        return chatbot

    def has_chatbot(self, chatbot_name: str) -> bool:
        return chatbot_name in self.chatbots

    def get_chatbot_names(self) -> list[str]:
        return list(self.chatbots.keys())

    @staticmethod
    def create_chatbot(
        chatbot_type: Type[ChatbotAdapter], parameters: ChatbotParameters
    ) -> ChatbotAdapter:
        if not issubclass(chatbot_type, ChatbotAdapter):
            raise ValueError(
                f"Invalid chatbot type: {chatbot_type}. Must be a subclass of ChatbotAdapter."
            )
        return chatbot_type(parameters)
