"""
Demo adapter for testing and development purposes.

This adapter provides a simple implementation that doesn't require any API keys
and returns predefined responses for testing the chatbot library.
"""

from datetime import datetime
from typing import List
from .chatbot_adapter import ChatbotAdapter, ChatbotParameters
from ..models.conversation_dataclasses import Message, Response
from ..tools.compatibility import Tool
from ..utils.logging import get_logger, log_function_call


class DemoAdapter(ChatbotAdapter):
    """Demo chatbot adapter that provides mock responses for testing."""
    
    def __init__(self, parameters: ChatbotParameters) -> None:
        super().__init__(parameters)
        self.logger = get_logger(self.__class__.__name__.lower())
        self.response_count = 0
    
    @staticmethod
    def supported_models() -> List[str]:
        """Return list of demo models."""
        return [
            "demo-model",
            "demo-advanced",
            "demo-simple"
        ]
    
    @staticmethod
    def models_supporting_tools() -> List[str]:
        """Return demo models that support tools."""
        return [
            "demo-model",
            "demo-advanced"
        ]
    
    @staticmethod
    def models_supporting_image_understanding() -> List[str]:
        """Return demo models that support image understanding."""
        return [
            "demo-advanced"
        ]
    
    def send_message_with_tools(
        self, messages: List[Message], active_tools: List[Tool]
    ) -> Response:
        """Send a message with tools and return a demo response."""
        log_function_call(
            self.logger,
            "DemoAdapter.send_message_with_tools",
            message_count=len(messages),
            tool_count=len(active_tools),
        )
        
        self.response_count += 1
        
        # Create a demo response that mentions the tools
        tool_names = [tool.name for tool in active_tools]
        demo_text = (
            f"Demo response #{self.response_count}. "
            f"I can see {len(messages)} message(s) and have access to "
            f"{len(active_tools)} tool(s): {', '.join(tool_names) if tool_names else 'none'}. "
            "This is a mock response for testing purposes."
        )
        
        return Response(
            id=f"demo-{self.response_count}",
            message_id=messages[-1].id if messages else "unknown",
            model=self.parameters.model_name,
            text=demo_text,
            timestamp=datetime.now(),
        )
    
    def send_message_without_tools(self, messages: List[Message]) -> Response:
        """Send a message without tools and return a demo response."""
        log_function_call(
            self.logger,
            "DemoAdapter.send_message_without_tools",
            message_count=len(messages),
        )
        
        self.response_count += 1
        
        # Create a simple demo response
        last_message_text = messages[-1].text if messages else "No message"
        demo_text = (
            f"Demo response #{self.response_count}. "
            f"You said: '{last_message_text[:50]}{'...' if len(last_message_text) > 50 else ''}'. "
            "This is a mock response for testing purposes."
        )
        
        return Response(
            id=f"demo-{self.response_count}",
            message_id=messages[-1].id if messages else "unknown",
            model=self.parameters.model_name,
            text=demo_text,
            timestamp=datetime.now(),
        )