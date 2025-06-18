"""
Tests for the conversation data models.
"""

import pytest
from datetime import datetime
from dataclasses import asdict
import json

from chatbot_library.models.conversation import (
    Conversation, Message, Response, Attachment, 
    conversation_from_dict, conversation_to_dict
)


class TestAttachment:
    """Test the Attachment dataclass."""
    
    def test_attachment_creation(self):
        """Test creating an attachment."""
        attachment = Attachment(
            id="test-1",
            content_type="image/png",
            media_type="image",
            data="base64data",
            source_type="base64"
        )
        
        assert attachment.id == "test-1"
        assert attachment.content_type == "image/png"
        assert attachment.media_type == "image"
        assert attachment.data == "base64data"
        assert attachment.source_type == "base64"
    
    def test_attachment_with_optional_fields(self):
        """Test attachment with optional fields."""
        attachment = Attachment(
            id="test-2",
            content_type="image/jpeg", 
            media_type="image",
            data="base64data",
            source_type="base64",
            url="https://example.com/image.jpg",
            detail="high"
        )
        
        assert attachment.url == "https://example.com/image.jpg"
        assert attachment.detail == "high"
    
    def test_attachment_serialization(self):
        """Test attachment serialization to dict."""
        attachment = Attachment(
            id="test-3",
            content_type="text/plain",
            media_type="text", 
            data="Hello world",
            source_type="inline"
        )
        
        data = asdict(attachment)
        assert data["id"] == "test-3"
        assert data["content_type"] == "text/plain"
        assert data["data"] == "Hello world"


class TestResponse:
    """Test the Response dataclass."""
    
    def test_response_creation(self):
        """Test creating a response."""
        response = Response(
            id="resp-1",
            message_id="msg-1", 
            model="test-model",
            text="This is a test response"
        )
        
        assert response.id == "resp-1"
        assert response.message_id == "msg-1"
        assert response.model == "test-model"
        assert response.text == "This is a test response"
        assert response.branch_name is None
        assert response.metadata is None
        assert isinstance(response.timestamp, datetime)
    
    def test_response_with_branch_and_metadata(self):
        """Test response with branch name and metadata."""
        metadata = {"temperature": 0.7, "tokens": 100}
        response = Response(
            id="resp-2",
            message_id="msg-1",
            model="gpt-4",
            text="Response with metadata",
            branch_name="alternative",
            metadata=metadata
        )
        
        assert response.branch_name == "alternative"
        assert response.metadata == metadata
        assert response.metadata["temperature"] == 0.7
    
    def test_response_serialization(self):
        """Test response serialization."""
        response = Response(
            id="resp-3",
            message_id="msg-1",
            model="claude-3",
            text="Serialization test",
            metadata={"cost": 0.01}
        )
        
        data = asdict(response)
        assert data["id"] == "resp-3"
        assert data["model"] == "claude-3"
        assert data["metadata"]["cost"] == 0.01
        assert "timestamp" in data


class TestMessage:
    """Test the Message dataclass."""
    
    def test_message_creation(self):
        """Test creating a message."""
        message = Message(
            id="msg-1",
            conversation_id="conv-1",
            user_id="user-1", 
            text="Hello, this is a test message"
        )
        
        assert message.id == "msg-1"
        assert message.conversation_id == "conv-1"
        assert message.user_id == "user-1"
        assert message.text == "Hello, this is a test message"
        assert message.responses == []
        assert message.attachments == []
        assert isinstance(message.timestamp, datetime)
    
    def test_message_with_attachments(self, sample_attachment):
        """Test message with attachments."""
        message = Message(
            id="msg-2",
            conversation_id="conv-1",
            user_id="user-1",
            text="Message with image",
            attachments=[sample_attachment]
        )
        
        assert len(message.attachments) == 1
        assert message.attachments[0] == sample_attachment
    
    def test_message_with_responses(self):
        """Test message with responses."""
        response = Response(
            id="resp-1",
            message_id="msg-3",
            model="test-model",
            text="Response to message"
        )
        
        message = Message(
            id="msg-3",
            conversation_id="conv-1",
            user_id="user-1",
            text="Message with response",
            responses=[response]
        )
        
        assert len(message.responses) == 1
        assert message.responses[0] == response
        assert message.responses[0].message_id == message.id
    
    def test_message_embedding(self):
        """Test message with embedding."""
        embedding = [0.1, 0.2, 0.3, 0.4, 0.5]
        message = Message(
            id="msg-4",
            conversation_id="conv-1",
            user_id="user-1",
            text="Message with embedding",
            embedding=embedding
        )
        
        assert message.embedding == embedding
        assert len(message.embedding) == 5


class TestConversation:
    """Test the Conversation dataclass."""
    
    def test_conversation_creation(self):
        """Test creating a conversation."""
        conversation = Conversation(
            id="conv-1",
            title="Test Conversation"
        )
        
        assert conversation.id == "conv-1"
        assert conversation.title == "Test Conversation"
        assert conversation.messages == []
        assert isinstance(conversation.created_at, datetime)
        assert isinstance(conversation.updated_at, datetime)
    
    def test_conversation_with_messages(self):
        """Test conversation with messages."""
        message = Message(
            id="msg-1",
            conversation_id="conv-1", 
            user_id="user-1",
            text="Test message"
        )
        
        conversation = Conversation(
            id="conv-1",
            title="Test with Messages",
            messages=[message]
        )
        
        assert len(conversation.messages) == 1
        assert conversation.messages[0] == message
        assert conversation.messages[0].conversation_id == conversation.id
    
    def test_conversation_metadata(self):
        """Test conversation with metadata."""
        metadata = {
            "model_switches": 3,
            "total_tokens": 1500,
            "cost": 0.15
        }
        
        conversation = Conversation(
            id="conv-2",
            title="Conversation with Metadata",
            metadata=metadata
        )
        
        assert conversation.metadata == metadata
        assert conversation.metadata["model_switches"] == 3


class TestConversationSerialization:
    """Test conversation serialization and deserialization."""
    
    def test_simple_conversation_to_dict(self):
        """Test converting simple conversation to dict."""
        conversation = Conversation(
            id="conv-1",
            title="Simple Conversation"
        )
        
        data = conversation_to_dict(conversation)
        
        assert data["id"] == "conv-1"
        assert data["title"] == "Simple Conversation"
        assert data["messages"] == []
        assert "created_at" in data
        assert "updated_at" in data
    
    def test_conversation_from_dict(self):
        """Test creating conversation from dict."""
        data = {
            "id": "conv-1",
            "title": "From Dict",
            "messages": [],
            "created_at": "2024-01-01T00:00:00",
            "updated_at": "2024-01-01T00:00:00"
        }
        
        conversation = conversation_from_dict(data)
        
        assert conversation.id == "conv-1"
        assert conversation.title == "From Dict"
        assert isinstance(conversation.created_at, datetime)
        assert isinstance(conversation.updated_at, datetime)
    
    def test_full_conversation_serialization(self):
        """Test full conversation with messages and responses."""
        # Create response
        response = Response(
            id="resp-1",
            message_id="msg-1",
            model="test-model",
            text="Test response",
            metadata={"tokens": 50}
        )
        
        # Create message with response
        message = Message(
            id="msg-1",
            conversation_id="conv-1",
            user_id="user-1",
            text="Test message",
            responses=[response]
        )
        
        # Create conversation
        conversation = Conversation(
            id="conv-1",
            title="Full Test",
            messages=[message],
            metadata={"test": True}
        )
        
        # Convert to dict
        data = conversation_to_dict(conversation)
        
        # Verify structure
        assert data["id"] == "conv-1"
        assert len(data["messages"]) == 1
        assert len(data["messages"][0]["responses"]) == 1
        assert data["messages"][0]["responses"][0]["text"] == "Test response"
        assert data["metadata"]["test"] is True
        
        # Convert back from dict
        restored = conversation_from_dict(data)
        
        assert restored.id == conversation.id
        assert restored.title == conversation.title
        assert len(restored.messages) == 1
        assert len(restored.messages[0].responses) == 1
        assert restored.messages[0].responses[0].text == "Test response"
    
    def test_json_serialization(self):
        """Test JSON serialization compatibility."""
        conversation = Conversation(
            id="conv-json",
            title="JSON Test"
        )
        
        # Convert to dict then JSON
        data = conversation_to_dict(conversation)
        json_str = json.dumps(data, default=str)
        
        # Parse back from JSON
        parsed_data = json.loads(json_str)
        restored = conversation_from_dict(parsed_data)
        
        assert restored.id == "conv-json"
        assert restored.title == "JSON Test"


class TestConversationValidation:
    """Test conversation data validation."""
    
    def test_message_conversation_id_consistency(self):
        """Test that message conversation_id matches conversation id."""
        message = Message(
            id="msg-1",
            conversation_id="conv-1",
            user_id="user-1",
            text="Test"
        )
        
        conversation = Conversation(
            id="conv-1",
            title="Test",
            messages=[message]
        )
        
        # Should match
        assert message.conversation_id == conversation.id
    
    def test_response_message_id_consistency(self):
        """Test that response message_id matches message id."""
        response = Response(
            id="resp-1",
            message_id="msg-1",
            model="test",
            text="Response"
        )
        
        message = Message(
            id="msg-1",
            conversation_id="conv-1",
            user_id="user-1",
            text="Message",
            responses=[response]
        )
        
        # Should match
        assert response.message_id == message.id
    
    def test_conversation_structure_integrity(self):
        """Test overall conversation structure integrity."""
        # Build a conversation with proper relationships
        conversation = Conversation(id="conv-1", title="Structure Test")
        
        message1 = Message(
            id="msg-1",
            conversation_id="conv-1",
            user_id="user-1", 
            text="First message"
        )
        
        response1 = Response(
            id="resp-1",
            message_id="msg-1",
            model="model-1",
            text="First response"
        )
        
        message1.responses.append(response1)
        conversation.messages.append(message1)
        
        # Verify all relationships
        assert len(conversation.messages) == 1
        assert conversation.messages[0].conversation_id == conversation.id
        assert len(conversation.messages[0].responses) == 1
        assert conversation.messages[0].responses[0].message_id == message1.id