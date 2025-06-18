"""Chatbot adapter implementations for different providers."""

from .chatbot_adapter import ChatbotAdapter, ChatbotParameters, ChatbotCapabilities

# Optional imports for adapters
__all__ = [
    "ChatbotAdapter", 
    "ChatbotParameters", 
    "ChatbotCapabilities",
]

try:
    from .anthropic_api_adapter import AnthropicAdapter
    __all__.append("AnthropicAdapter")
except ImportError:
    pass

try:
    from .openai_api_adapter import OpenAIAdapter
    __all__.append("OpenAIAdapter")
except ImportError:
    pass