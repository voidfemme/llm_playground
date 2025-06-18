"""
Consolidated imports for conversation data models.

This module provides a single import point for all conversation-related
data classes and maintains compatibility with existing code.
"""

# Import all conversation models
from .conversation import (
    Attachment,
    ToolUse, 
    ToolResult,
    Response,
    Message,
    Conversation,
    conversation_to_dict,
    conversation_from_dict,
    create_conversation_pair_embedding
)

# Import ChatbotParameters from the adapter module
from ..adapters.chatbot_adapter import ChatbotParameters

# Re-export everything for easy importing
__all__ = [
    'Attachment',
    'ToolUse',
    'ToolResult', 
    'Response',
    'Message',
    'Conversation',
    'ChatbotParameters',
    'conversation_to_dict',
    'conversation_from_dict',
    'create_conversation_pair_embedding'
]