"""
Integration tests for ConversationManager.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from pathlib import Path

from chatbot_library.core.conversation_manager import ConversationManager
from chatbot_library.adapters.chatbot_adapter import ChatbotCapabilities
from chatbot_library.models.conversation import Attachment


class TestConversationManager:
    """Test the conversation manager."""
    
    def test_manager_initialization(self, temp_data_dir):
        """Test manager initialization."""
        manager = ConversationManager(temp_data_dir)
        
        assert manager.data_dir == temp_data_dir
        assert len(manager.model_registry) == 0
        assert len(manager.conversations) == 0
    
    def test_model_registration(self, conversation_manager):
        """Test registering models with capabilities."""
        # Models should be pre-registered in fixture
        assert len(conversation_manager.model_registry) >= 3
        assert "test-basic" in conversation_manager.model_registry
        assert "test-vision" in conversation_manager.model_registry
        assert "test-full" in conversation_manager.model_registry
    
    def test_model_capabilities_query(self, conversation_manager):
        """Test querying model capabilities."""
        # Test basic model
        caps = conversation_manager.model_registry["test-basic"]["capabilities"]
        assert caps.function_calling is False
        assert caps.image_understanding is False
        
        # Test vision model
        caps = conversation_manager.model_registry["test-vision"]["capabilities"]
        assert caps.function_calling is False
        assert caps.image_understanding is True
        
        # Test full model
        caps = conversation_manager.model_registry["test-full"]["capabilities"]
        assert caps.function_calling is True
        assert caps.image_understanding is True
    
    def test_conversation_creation(self, conversation_manager):
        """Test creating conversations."""
        conversation_id = conversation_manager.create_conversation("Test Conversation")
        conversation = conversation_manager.get_conversation(conversation_id)
        
        assert conversation.id is not None
        assert conversation.title == "Test Conversation"
        assert len(conversation.messages) == 0
        
        # Should be saved to disk
        loaded = conversation_manager.get_conversation(conversation_id)
        assert loaded is not None
        assert loaded.title == "Test Conversation"
    
    def test_message_addition(self, conversation_manager):
        """Test adding messages to conversations."""
        conversation_id = conversation_manager.create_conversation("Message Test")
        conversation = conversation_manager.get_conversation(conversation_id)
        
        message = conversation.add_message(
            "test-user",
            "Hello, this is a test message"
        )
        
        assert message.id is not None
        assert message.conversation_id == conversation_id
        assert message.user_id == "test-user"
        assert message.text == "Hello, this is a test message"
        assert len(message.responses) == 0
        
        # Verify conversation is updated
        updated_conv = conversation_manager.get_conversation(conversation_id)
        assert len(updated_conv.messages) == 1
        assert updated_conv.messages[0].id == message.id
    
    def test_response_addition(self, conversation_manager):
        """Test adding responses to messages."""
        conversation_id = conversation_manager.create_conversation("Response Test")
        conversation = conversation_manager.get_conversation(conversation_id)
        message = conversation.add_message("test-user", "Test message")
        
        response = message.add_response(
            "test-basic",
            "This is a test response",
            branch_name="main",
            metadata={"temperature": 0.7}
        )
        
        assert response.id is not None
        assert response.message_id == message.id
        assert response.model == "test-basic"
        assert response.text == "This is a test response"
        assert response.branch_name == "main"
        assert response.metadata["temperature"] == 0.7
        
        # Verify message is updated
        updated_conv = conversation_manager.get_conversation(conversation_id)
        updated_message = updated_conv.messages[0]
        assert len(updated_message.responses) == 1
        assert updated_message.responses[0].id == response.id


class TestModelHotSwapping:
    """Test model hot-swapping functionality."""
    
    @pytest.mark.asyncio
    async def test_hot_swap_response_addition(self, conversation_manager, mock_async_api_call):
        """Test adding responses with hot-swapping."""
        conversation_id = conversation_manager.create_conversation("Hot Swap Test")
        conversation = conversation_manager.get_conversation(conversation_id)
        message = conversation.add_message("test-user", "Test hot-swapping")
        
        # Add response with hot-swapping
        response = conversation_manager.add_response_with_hotswap(
            conversation_id,
            message.id,
            "test-basic"
        )
        
        assert response is not None
        assert response.model == "test-basic"
        assert "Mock response" in response.text
        
        # Should track hot-swap usage
        stats = conversation_manager.get_conversation_stats()
        assert stats["total_responses"] > 0
    
    def test_model_compatibility_analysis(self, conversation_manager):
        """Test model compatibility analysis."""
        conversation_id = conversation_manager.create_conversation("Compatibility Test")
        conversation = conversation_manager.get_conversation(conversation_id)
        
        # Add a message with image
        attachment = Attachment(
            id="test-img",
            content_type="image/png",
            media_type="image",
            data="base64data",
            source_type="base64"
        )
        
        message = conversation.add_message(
            "test-user", 
            "Analyze this image",
            attachments=[attachment]
        )
        
        # Test compatibility for different models
        compatibility = conversation_manager.get_model_compatibility(
            conversation_id,
            "test-basic"
        )
        assert "compatibility_score" in compatibility or "issues" in compatibility
        
        # Test adaptation
        context = conversation_manager.adapt_conversation_for_model(
            conversation_id,
            "test-vision"
        )
        assert len(context) > 0
    
    def test_model_recommendations(self, conversation_manager):
        """Test getting model recommendations."""
        conversation_id = conversation_manager.create_conversation("Recommendation Test")
        conversation = conversation_manager.get_conversation(conversation_id)
        
        # Add some messages to create context
        conversation.add_message("user", "Can you analyze this image?")
        conversation.add_message("user", "I need function calling capabilities")
        
        # Test compatibility with different models
        basic_compat = conversation_manager.get_model_compatibility(conversation_id, "test-basic")
        vision_compat = conversation_manager.get_model_compatibility(conversation_id, "test-vision")
        full_compat = conversation_manager.get_model_compatibility(conversation_id, "test-full")
        
        # All should return compatibility info
        assert isinstance(basic_compat, dict)
        assert isinstance(vision_compat, dict)
        assert isinstance(full_compat, dict)


class TestConversationPersistence:
    """Test conversation persistence and loading."""
    
    def test_conversation_saving_and_loading(self, conversation_manager):
        """Test that conversations are properly saved and loaded."""
        # Create a conversation with messages and responses
        conversation_id = conversation_manager.create_conversation("Persistence Test")
        conversation = conversation_manager.get_conversation(conversation_id)
        message = conversation.add_message("user", "Test persistence")
        response = message.add_response("test-basic", "Persisted response")
        
        # Save the conversation manually since we modified it directly
        conversation_manager.save_conversation(conversation)
        
        # Create a new manager instance with same data directory
        new_manager = ConversationManager(conversation_manager.data_dir)
        
        # Should be able to load the conversation
        loaded_conv = new_manager.get_conversation(conversation_id)
        assert loaded_conv is not None
        assert loaded_conv.title == "Persistence Test"
        assert len(loaded_conv.messages) == 1
        assert len(loaded_conv.messages[0].responses) == 1
        assert loaded_conv.messages[0].responses[0].text == "Persisted response"
    
    def test_conversation_list_and_metadata(self, conversation_manager):
        """Test getting conversation lists and metadata."""
        # Create multiple conversations
        conv1_id = conversation_manager.create_conversation("First Conversation")
        conv2_id = conversation_manager.create_conversation("Second Conversation")
        
        # Add messages to create different sizes
        conv1 = conversation_manager.get_conversation(conv1_id)
        conv2 = conversation_manager.get_conversation(conv2_id)
        conv1.add_message("user", "Message 1")
        conv2.add_message("user", "Message 1")
        conv2.add_message("user", "Message 2")
        
        # Get conversation list
        conv_list = conversation_manager.list_conversations()
        
        assert len(conv_list) >= 2
        
        # Find our conversations
        conv1_info = next((c for c in conv_list if c["id"] == conv1_id), None)
        conv2_info = next((c for c in conv_list if c["id"] == conv2_id), None)
        
        assert conv1_info is not None
        assert conv2_info is not None
        assert conv1_info["message_count"] == 1
        assert conv2_info["message_count"] == 2
    
    def test_conversation_deletion(self, conversation_manager):
        """Test deleting conversations."""
        conversation_id = conversation_manager.create_conversation("To Delete")
        
        # Verify it exists
        assert conversation_manager.get_conversation(conversation_id) is not None
        
        # Delete it
        conversation_manager.delete_conversation(conversation_id)
        
        # Should not exist anymore
        assert conversation_manager.get_conversation(conversation_id) is None
        
        # Should not appear in conversation list
        conv_list = conversation_manager.list_conversations()
        conv_ids = [c["id"] for c in conv_list]
        assert conversation_id not in conv_ids


class TestConversationAdaptation:
    """Test conversation adaptation for different models."""
    
    def test_context_adaptation_for_basic_model(self, conversation_manager):
        """Test adapting conversation context for basic model."""
        conversation_id = conversation_manager.create_conversation("Adaptation Test")
        conversation = conversation_manager.get_conversation(conversation_id)
        
        # Add various types of messages
        msg1 = conversation.add_message("user", "Simple text message")
        
        # Add message with image
        attachment = Attachment(
            id="test-img",
            content_type="image/png", 
            media_type="image",
            data="base64data",
            source_type="base64"
        )
        msg2 = conversation.add_message(
            "user", "Message with image", attachments=[attachment]
        )
        
        # Get adapted context for basic model (no image support)
        context = conversation_manager.adapt_conversation_for_model(
            conversation_id, "test-basic"
        )
        
        assert len(context) > 0
        # Should have adapted the image message somehow
        assert any("role" in msg for msg in context)
    
    def test_context_adaptation_for_vision_model(self, conversation_manager):
        """Test adapting conversation context for vision model."""
        conversation_id = conversation_manager.create_conversation("Vision Test")
        conversation = conversation_manager.get_conversation(conversation_id)
        
        attachment = Attachment(
            id="test-img",
            content_type="image/png",
            media_type="image", 
            data="base64data",
            source_type="base64"
        )
        
        message = conversation.add_message(
            "user", "Analyze this image", attachments=[attachment]
        )
        
        # Get adapted context for vision model
        context = conversation_manager.adapt_conversation_for_model(
            conversation_id, "test-vision"
        )
        
        assert len(context) > 0
        # Should preserve image capabilities
        assert any("role" in msg for msg in context)
    
    def test_context_limit_handling(self, conversation_manager):
        """Test handling context limits."""
        conversation_id = conversation_manager.create_conversation("Context Limit Test")
        conversation = conversation_manager.get_conversation(conversation_id)
        
        # Add many messages to exceed typical context limit
        for i in range(10):
            conversation.add_message("user", f"Message {i} with some content")
        
        # Get context
        context = conversation_manager.adapt_conversation_for_model(
            conversation_id, "test-basic"
        )
        
        # Should return some context
        assert len(context) > 0


class TestHotSwapStatistics:
    """Test hot-swap usage statistics."""
    
    @pytest.mark.asyncio
    async def test_statistics_tracking(self, conversation_manager, mock_async_api_call):
        """Test that statistics are tracked."""
        conversation_id = conversation_manager.create_conversation("Stats Test")
        conversation = conversation_manager.get_conversation(conversation_id)
        message = conversation.add_message("user", "Test statistics")
        
        # Add responses
        message.add_response("test-basic", "Response 1")
        message.add_response("test-vision", "Response 2", branch_name="vision")
        
        stats = conversation_manager.get_conversation_stats()
        
        assert stats["total_responses"] >= 2
        assert len(stats["models_used"]) >= 2
        assert "test-basic" in stats["models_used"]
        assert "test-vision" in stats["models_used"]
    
    def test_statistics_persistence(self, conversation_manager, mock_async_api_call):
        """Test that statistics persist across manager restarts."""
        # Use some models
        conversation_id = conversation_manager.create_conversation("Persistence Stats")
        conversation = conversation_manager.get_conversation(conversation_id)
        message = conversation.add_message("user", "Test")
        message.add_response("test-basic", "Test response")
        
        # Save the conversation manually since we modified it directly
        conversation_manager.save_conversation(conversation)
        
        original_stats = conversation_manager.get_conversation_stats()
        
        # Create new manager with same data directory  
        def mock_api_function(context, **kwargs):
            return {"text": f"Mock response from {kwargs.get('model', 'unknown')}"}
        
        new_manager = ConversationManager(conversation_manager.data_dir)
        new_manager.register_model(
            "test-basic",
            mock_api_function,
            ChatbotCapabilities(function_calling=False, image_understanding=False),
            provider="test", cost="free"
        )
        
        new_stats = new_manager.get_conversation_stats()
        
        # Statistics should be preserved
        assert new_stats["total_responses"] == original_stats["total_responses"]


class TestErrorHandling:
    """Test error handling in conversation manager."""
    
    def test_invalid_conversation_id(self, conversation_manager):
        """Test handling invalid conversation IDs."""
        # Should return None for non-existent conversation
        assert conversation_manager.get_conversation("invalid-id") is None
        
        # Should raise error when trying to use invalid conversation ID
        with pytest.raises(Exception):
            conversation_manager.send_message_and_get_response(
                "invalid-id", "user", "test", "test-basic"
            )
    
    def test_invalid_model_name(self, conversation_manager):
        """Test handling invalid model names."""
        conversation_id = conversation_manager.create_conversation("Error Test")
        
        # Should handle unknown model gracefully
        with pytest.raises(Exception):
            conversation_manager.send_message_and_get_response(
                conversation_id, "user", "test", "unknown-model"
            )
    
    def test_corrupted_conversation_file(self, conversation_manager, temp_data_dir):
        """Test handling corrupted conversation files."""
        # Create a valid conversation first
        conversation_id = conversation_manager.create_conversation("Corruption Test")
        
        # Corrupt the file
        conversation_file = temp_data_dir / f"{conversation_id}.json"
        conversation_file.write_text("invalid json content")
        
        # Create new manager to trigger file loading
        new_manager = ConversationManager(temp_data_dir)
        
        # Should handle corruption gracefully
        loaded = new_manager.get_conversation(conversation_id)
        assert loaded is None  # Should fail to load but not crash