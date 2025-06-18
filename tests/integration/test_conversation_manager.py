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
        assert len(manager.registered_models) == 0
        assert len(manager.model_capabilities) == 0
        assert len(manager.model_metadata) == 0
    
    def test_model_registration(self, conversation_manager):
        """Test registering models with capabilities."""
        # Models should be pre-registered in fixture
        models = conversation_manager.get_available_models()
        
        assert len(models) >= 3
        model_names = [m["name"] for m in models]
        assert "test-basic" in model_names
        assert "test-vision" in model_names
        assert "test-full" in model_names
    
    def test_model_capabilities_query(self, conversation_manager):
        """Test querying model capabilities."""
        # Test basic model
        caps = conversation_manager.get_model_capabilities("test-basic")
        assert caps.function_calling is False
        assert caps.image_understanding is False
        
        # Test vision model
        caps = conversation_manager.get_model_capabilities("test-vision")
        assert caps.function_calling is False
        assert caps.image_understanding is True
        
        # Test full model
        caps = conversation_manager.get_model_capabilities("test-full")
        assert caps.function_calling is True
        assert caps.image_understanding is True
    
    def test_conversation_creation(self, conversation_manager):
        """Test creating conversations."""
        conversation = conversation_manager.create_conversation("Test Conversation")
        
        assert conversation.id is not None
        assert conversation.title == "Test Conversation"
        assert len(conversation.messages) == 0
        
        # Should be saved to disk
        loaded = conversation_manager.get_conversation(conversation.id)
        assert loaded is not None
        assert loaded.title == "Test Conversation"
    
    def test_message_addition(self, conversation_manager):
        """Test adding messages to conversations."""
        conversation = conversation_manager.create_conversation("Message Test")
        
        message = conversation_manager.add_message(
            conversation.id,
            "test-user",
            "Hello, this is a test message"
        )
        
        assert message.id is not None
        assert message.conversation_id == conversation.id
        assert message.user_id == "test-user"
        assert message.text == "Hello, this is a test message"
        assert len(message.responses) == 0
        
        # Verify conversation is updated
        updated_conv = conversation_manager.get_conversation(conversation.id)
        assert len(updated_conv.messages) == 1
        assert updated_conv.messages[0].id == message.id
    
    def test_response_addition(self, conversation_manager):
        """Test adding responses to messages."""
        conversation = conversation_manager.create_conversation("Response Test")
        message = conversation_manager.add_message(
            conversation.id, "test-user", "Test message"
        )
        
        response = conversation_manager.add_response(
            conversation.id,
            message.id,
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
        updated_conv = conversation_manager.get_conversation(conversation.id)
        updated_message = updated_conv.messages[0]
        assert len(updated_message.responses) == 1
        assert updated_message.responses[0].id == response.id


class TestModelHotSwapping:
    """Test model hot-swapping functionality."""
    
    @pytest.mark.asyncio
    async def test_hot_swap_response_addition(self, conversation_manager, mock_async_api_call):
        """Test adding responses with hot-swapping."""
        conversation = conversation_manager.create_conversation("Hot Swap Test")
        message = conversation_manager.add_message(
            conversation.id, "test-user", "Test hot-swapping"
        )
        
        # Add response with hot-swapping
        response = conversation_manager.add_response_with_hotswap(
            conversation.id,
            message.id,
            "test-basic",
            mock_async_api_call
        )
        
        assert response is not None
        assert response.model == "test-basic"
        assert "Mock response from test-basic" in response.text
        
        # Should track hot-swap usage
        stats = conversation_manager.get_hotswap_statistics()
        assert stats["total_usage"] > 0
    
    def test_model_compatibility_analysis(self, conversation_manager):
        """Test model compatibility analysis."""
        conversation = conversation_manager.create_conversation("Compatibility Test")
        
        # Add a message with image
        attachment = Attachment(
            id="test-img",
            content_type="image/png",
            media_type="image",
            data="base64data",
            source_type="base64"
        )
        
        message = conversation_manager.add_message(
            conversation.id,
            "test-user", 
            "Analyze this image",
            attachments=[attachment]
        )
        
        # Test compatibility for different models
        adapter = conversation_manager.conversation_adapter
        
        # Basic model shouldn't handle images well
        context = adapter.adapt_conversation_for_model(
            [message],
            conversation_manager.get_model_capabilities("test-basic")
        )
        # Should have fallback description instead of image
        assert any("image" in str(msg).lower() for msg in context)
        
        # Vision model should handle images
        context = adapter.adapt_conversation_for_model(
            [message],
            conversation_manager.get_model_capabilities("test-vision")
        )
        # Should preserve image capability
        assert len(context) > 0
    
    def test_model_recommendations(self, conversation_manager):
        """Test getting model recommendations."""
        conversation = conversation_manager.create_conversation("Recommendation Test")
        
        # Add some messages to create context
        conversation_manager.add_message(
            conversation.id, "user", "Can you analyze this image?"
        )
        conversation_manager.add_message(
            conversation.id, "user", "I need function calling capabilities"
        )
        
        recommendations = conversation_manager.get_model_recommendations(conversation.id)
        
        assert len(recommendations) > 0
        # Should be sorted by compatibility score
        assert all(
            rec["compatibility_score"] >= next_rec["compatibility_score"]
            for rec, next_rec in zip(recommendations[:-1], recommendations[1:])
        )
        
        # Should prefer models with required capabilities
        model_names = [rec["name"] for rec in recommendations]
        assert "test-full" in model_names  # Should rank high for diverse needs


class TestConversationPersistence:
    """Test conversation persistence and loading."""
    
    def test_conversation_saving_and_loading(self, conversation_manager):
        """Test that conversations are properly saved and loaded."""
        # Create a conversation with messages and responses
        conversation = conversation_manager.create_conversation("Persistence Test")
        message = conversation_manager.add_message(
            conversation.id, "user", "Test persistence"
        )
        response = conversation_manager.add_response(
            conversation.id, message.id, "test-basic", "Persisted response"
        )
        
        # Create a new manager instance with same data directory
        new_manager = ConversationManager(conversation_manager.data_dir)
        
        # Should be able to load the conversation
        loaded_conv = new_manager.get_conversation(conversation.id)
        assert loaded_conv is not None
        assert loaded_conv.title == "Persistence Test"
        assert len(loaded_conv.messages) == 1
        assert len(loaded_conv.messages[0].responses) == 1
        assert loaded_conv.messages[0].responses[0].text == "Persisted response"
    
    def test_conversation_list_and_metadata(self, conversation_manager):
        """Test getting conversation lists and metadata."""
        # Create multiple conversations
        conv1 = conversation_manager.create_conversation("First Conversation")
        conv2 = conversation_manager.create_conversation("Second Conversation")
        
        # Add messages to create different sizes
        conversation_manager.add_message(conv1.id, "user", "Message 1")
        conversation_manager.add_message(conv2.id, "user", "Message 1")
        conversation_manager.add_message(conv2.id, "user", "Message 2")
        
        # Get conversation list
        conv_list = conversation_manager.get_conversation_list()
        
        assert len(conv_list) >= 2
        
        # Find our conversations
        conv1_info = next((c for c in conv_list if c["id"] == conv1.id), None)
        conv2_info = next((c for c in conv_list if c["id"] == conv2.id), None)
        
        assert conv1_info is not None
        assert conv2_info is not None
        assert conv1_info["message_count"] == 1
        assert conv2_info["message_count"] == 2
    
    def test_conversation_deletion(self, conversation_manager):
        """Test deleting conversations."""
        conversation = conversation_manager.create_conversation("To Delete")
        conversation_id = conversation.id
        
        # Verify it exists
        assert conversation_manager.get_conversation(conversation_id) is not None
        
        # Delete it
        conversation_manager.delete_conversation(conversation_id)
        
        # Should not exist anymore
        assert conversation_manager.get_conversation(conversation_id) is None
        
        # Should not appear in conversation list
        conv_list = conversation_manager.get_conversation_list()
        conv_ids = [c["id"] for c in conv_list]
        assert conversation_id not in conv_ids


class TestConversationAdaptation:
    """Test conversation adaptation for different models."""
    
    def test_context_adaptation_for_basic_model(self, conversation_manager):
        """Test adapting conversation context for basic model."""
        conversation = conversation_manager.create_conversation("Adaptation Test")
        
        # Add various types of messages
        msg1 = conversation_manager.add_message(
            conversation.id, "user", "Simple text message"
        )
        
        # Add message with image
        attachment = Attachment(
            id="test-img",
            content_type="image/png", 
            media_type="image",
            data="base64data",
            source_type="base64"
        )
        msg2 = conversation_manager.add_message(
            conversation.id, "user", "Message with image", attachments=[attachment]
        )
        
        # Get adapted context for basic model (no image support)
        context = conversation_manager.get_conversation_context_for_model(
            conversation.id, "test-basic"
        )
        
        assert len(context) > 0
        # Should have adapted the image message somehow
        assert any("role" in msg for msg in context)
    
    def test_context_adaptation_for_vision_model(self, conversation_manager):
        """Test adapting conversation context for vision model."""
        conversation = conversation_manager.create_conversation("Vision Test")
        
        attachment = Attachment(
            id="test-img",
            content_type="image/png",
            media_type="image", 
            data="base64data",
            source_type="base64"
        )
        
        message = conversation_manager.add_message(
            conversation.id, "user", "Analyze this image", attachments=[attachment]
        )
        
        # Get adapted context for vision model
        context = conversation_manager.get_conversation_context_for_model(
            conversation.id, "test-vision"
        )
        
        assert len(context) > 0
        # Should preserve image capabilities
        assert any("role" in msg for msg in context)
    
    def test_context_limit_handling(self, conversation_manager):
        """Test handling context limits."""
        conversation = conversation_manager.create_conversation("Context Limit Test")
        
        # Add many messages to exceed typical context limit
        for i in range(50):
            conversation_manager.add_message(
                conversation.id, "user", f"Message {i} with some content"
            )
        
        # Get limited context
        context = conversation_manager.get_conversation_context_for_model(
            conversation.id, "test-basic", context_limit=5
        )
        
        # Should be limited to recent messages
        assert len(context) <= 5


class TestHotSwapStatistics:
    """Test hot-swap usage statistics."""
    
    @pytest.mark.asyncio
    async def test_statistics_tracking(self, conversation_manager, mock_async_api_call):
        """Test that hot-swap statistics are tracked."""
        conversation = conversation_manager.create_conversation("Stats Test")
        message = conversation_manager.add_message(
            conversation.id, "user", "Test statistics"
        )
        
        # Use different models
        conversation_manager.add_response_with_hotswap(
            conversation.id, message.id, "test-basic", mock_async_api_call
        )
        conversation_manager.add_response_with_hotswap(
            conversation.id, message.id, "test-vision", mock_async_api_call, branch_name="vision"
        )
        
        stats = conversation_manager.get_hotswap_statistics()
        
        assert stats["total_usage"] >= 2
        assert stats["total_models"] >= 2
        assert len(stats["models"]) >= 2
        
        # Should track per-model usage
        model_stats = {m["name"]: m for m in stats["models"]}
        assert "test-basic" in model_stats
        assert "test-vision" in model_stats
        assert model_stats["test-basic"]["usage_count"] >= 1
        assert model_stats["test-vision"]["usage_count"] >= 1
    
    def test_statistics_persistence(self, conversation_manager, mock_async_api_call):
        """Test that statistics persist across manager restarts."""
        # Use some models
        conversation = conversation_manager.create_conversation("Persistence Stats")
        message = conversation_manager.add_message(
            conversation.id, "user", "Test"
        )
        
        conversation_manager.add_response_with_hotswap(
            conversation.id, message.id, "test-basic", mock_async_api_call
        )
        
        original_stats = conversation_manager.get_hotswap_statistics()
        
        # Create new manager with same data directory
        new_manager = ConversationManager(conversation_manager.data_dir)
        # Re-register models
        new_manager.register_model(
            "test-basic",
            ChatbotCapabilities(function_calling=False, image_understanding=False),
            {"provider": "test", "cost": "free"}
        )
        
        new_stats = new_manager.get_hotswap_statistics()
        
        # Statistics should be preserved
        assert new_stats["total_usage"] == original_stats["total_usage"]


class TestErrorHandling:
    """Test error handling in conversation manager."""
    
    def test_invalid_conversation_id(self, conversation_manager):
        """Test handling invalid conversation IDs."""
        # Should return None for non-existent conversation
        assert conversation_manager.get_conversation("invalid-id") is None
        
        # Should raise error when trying to add message to non-existent conversation
        with pytest.raises(Exception):
            conversation_manager.add_message("invalid-id", "user", "test")
    
    def test_invalid_model_name(self, conversation_manager):
        """Test handling invalid model names."""
        conversation = conversation_manager.create_conversation("Error Test")
        message = conversation_manager.add_message(
            conversation.id, "user", "test"
        )
        
        # Should handle unknown model gracefully
        with pytest.raises(Exception):
            conversation_manager.add_response(
                conversation.id, message.id, "unknown-model", "response"
            )
    
    def test_corrupted_conversation_file(self, conversation_manager, temp_data_dir):
        """Test handling corrupted conversation files."""
        # Create a valid conversation first
        conversation = conversation_manager.create_conversation("Corruption Test")
        
        # Corrupt the file
        conversation_file = temp_data_dir / f"{conversation.id}.json"
        conversation_file.write_text("invalid json content")
        
        # Should handle corruption gracefully
        loaded = conversation_manager.get_conversation(conversation.id)
        assert loaded is None  # Should fail to load but not crash