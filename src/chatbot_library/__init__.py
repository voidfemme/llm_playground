"""
Chatbot Library - A flexible library for managing multiple chatbot providers with MCP support.
"""

from .core.chatbot_manager import ChatbotManager
from .core.conversation_manager import ConversationManager
from .models.conversation_dataclasses import Conversation, Message, Response
from .tools.compatibility import ToolManager

__version__ = "0.1.0"
__all__ = [
    "ChatbotManager",
    "ConversationManager", 
    "Conversation",
    "Message",
    "Response",
    "ToolManager",
]