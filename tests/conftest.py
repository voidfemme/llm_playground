"""
Pytest configuration and shared fixtures for the test suite.
"""

import pytest
import asyncio
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any
from unittest.mock import AsyncMock, MagicMock

# Add src to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from chatbot_library.core.conversation_manager import ConversationManager
from chatbot_library.core.mcp_integration import MCPConversationManager
from chatbot_library.adapters.chatbot_adapter import ChatbotCapabilities
from chatbot_library.tools.mcp_tool_registry import MCPToolRegistry
from chatbot_library.models.conversation import Conversation, Message, Response, Attachment


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def temp_data_dir():
    """Create a temporary directory for test data."""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)


@pytest.fixture
def mock_api_response():
    """Mock API response data."""
    return {
        "content": "This is a test response from the AI model.",
        "model": "test-model",
        "usage": {
            "input_tokens": 10,
            "output_tokens": 15
        }
    }


@pytest.fixture
def sample_conversation_data():
    """Sample conversation data for testing."""
    return {
        "id": "test-conv-123",
        "title": "Test Conversation",
        "user_id": "test-user",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
    }


@pytest.fixture
def sample_message_data():
    """Sample message data for testing."""
    return {
        "id": "test-msg-456",
        "conversation_id": "test-conv-123", 
        "user_id": "test-user",
        "text": "Hello, this is a test message",
        "timestamp": "2024-01-01T00:00:00Z"
    }


@pytest.fixture
def sample_response_data():
    """Sample response data for testing."""
    return {
        "id": "test-resp-789",
        "message_id": "test-msg-456",
        "model": "test-model",
        "text": "Hello! This is a test response.",
        "timestamp": "2024-01-01T00:00:00Z",
        "branch_name": "main"
    }


@pytest.fixture
def sample_attachment():
    """Sample attachment for testing."""
    return Attachment(
        id="test-attachment-1",
        content_type="image/png",
        media_type="image",
        data="iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==",
        source_type="base64"
    )


@pytest.fixture
def test_capabilities():
    """Test chatbot capabilities."""
    return {
        "basic": ChatbotCapabilities(
            function_calling=False,
            image_understanding=False,
            supported_images=[]
        ),
        "vision": ChatbotCapabilities(
            function_calling=False,
            image_understanding=True,
            supported_images=["image/png", "image/jpeg"]
        ),
        "full": ChatbotCapabilities(
            function_calling=True,
            image_understanding=True,
            supported_images=["image/png", "image/jpeg", "image/gif"]
        )
    }


@pytest.fixture
def mock_anthropic_client():
    """Mock Anthropic API client."""
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text="Test response from Claude")]
    mock_response.usage.input_tokens = 10
    mock_response.usage.output_tokens = 15
    mock_client.messages.create.return_value = mock_response
    return mock_client


@pytest.fixture
def mock_openai_client():
    """Mock OpenAI API client."""
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "Test response from GPT"
    mock_response.usage.prompt_tokens = 10
    mock_response.usage.completion_tokens = 15
    mock_client.chat.completions.create.return_value = mock_response
    return mock_client


@pytest.fixture
def conversation_manager(temp_data_dir):
    """Create a ConversationManager for testing."""
    manager = ConversationManager(temp_data_dir)
    
    # Register test models
    manager.register_model(
        "test-basic",
        ChatbotCapabilities(function_calling=False, image_understanding=False),
        {"provider": "test", "cost": "free"}
    )
    manager.register_model(
        "test-vision",
        ChatbotCapabilities(
            function_calling=False, 
            image_understanding=True, 
            supported_images=["image/png"]
        ),
        {"provider": "test", "cost": "low"}
    )
    manager.register_model(
        "test-full",
        ChatbotCapabilities(
            function_calling=True, 
            image_understanding=True,
            supported_images=["image/png", "image/jpeg"]
        ),
        {"provider": "test", "cost": "medium"}
    )
    
    return manager


@pytest.fixture
def mcp_conversation_manager(temp_data_dir):
    """Create an MCPConversationManager for testing."""
    return MCPConversationManager(temp_data_dir)


@pytest.fixture
def tool_registry():
    """Create a clean MCPToolRegistry for testing."""
    return MCPToolRegistry()


@pytest.fixture
async def sample_conversation(conversation_manager):
    """Create a sample conversation for testing."""
    conversation = conversation_manager.create_conversation("Test Conversation")
    
    # Add a message and response
    message = conversation_manager.add_message(
        conversation.id, 
        "test-user", 
        "Hello, this is a test message"
    )
    
    response = conversation_manager.add_response(
        conversation.id,
        message.id,
        "test-basic",
        "Hello! This is a test response.",
        metadata={"test": True}
    )
    
    return conversation


@pytest.fixture
def mock_async_api_call():
    """Mock async API call function."""
    async def mock_api(messages, model, **kwargs):
        return {
            "content": f"Mock response from {model}",
            "model": model,
            "usage": {"input_tokens": 10, "output_tokens": 15}
        }
    
    return mock_api


# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "requires_api: mark test as requiring API keys"
    )


def pytest_collection_modifyitems(config, items):
    """Automatically mark tests based on their location."""
    for item in items:
        # Mark integration tests
        if "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        
        # Mark unit tests 
        elif "unit" in str(item.fspath) or "test_" in item.name:
            item.add_marker(pytest.mark.unit)
        
        # Mark slow tests
        if "slow" in item.name or "performance" in str(item.fspath):
            item.add_marker(pytest.mark.slow)


# Helper functions for tests
def assert_conversation_structure(conversation: Conversation):
    """Assert that a conversation has the expected structure."""
    assert hasattr(conversation, 'id')
    assert hasattr(conversation, 'title')
    assert hasattr(conversation, 'messages')
    assert isinstance(conversation.messages, list)
    
    for message in conversation.messages:
        assert hasattr(message, 'id')
        assert hasattr(message, 'text')
        assert hasattr(message, 'responses')
        assert isinstance(message.responses, list)


def assert_message_structure(message: Message):
    """Assert that a message has the expected structure."""
    assert hasattr(message, 'id')
    assert hasattr(message, 'conversation_id')
    assert hasattr(message, 'user_id')
    assert hasattr(message, 'text')
    assert hasattr(message, 'responses')
    assert hasattr(message, 'timestamp')


def assert_response_structure(response: Response):
    """Assert that a response has the expected structure."""
    assert hasattr(response, 'id')
    assert hasattr(response, 'message_id')
    assert hasattr(response, 'model')
    assert hasattr(response, 'text')
    assert hasattr(response, 'timestamp')