# src/model/conversation_store.py

from abc import ABC, abstractmethod
from src.model.conversation_dataclasses import Conversation


class ConversationStore(ABC):
    @abstractmethod
    def save_conversation(self, conversation: Conversation) -> None:
        pass

    @abstractmethod
    def get_conversation(self, conversation_id: str) -> Conversation:
        pass
