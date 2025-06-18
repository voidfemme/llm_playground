"""
Integration tests for the prompt conversation manager.
"""

import pytest
import tempfile
from datetime import datetime

from chatbot_library.core.prompt_conversation_manager import PromptConversationManager
from chatbot_library.prompts import ThinkingMode
from chatbot_library.prompts.prompt_builder import PromptConfiguration


class TestPromptConversationManager:
    """Test the PromptConversationManager integration."""
    
    @pytest.fixture
    def prompt_manager(self):
        """Create a prompt conversation manager for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield PromptConversationManager(temp_dir)
    
    def test_initialization(self, prompt_manager):
        """Test that the prompt conversation manager initializes correctly."""
        assert prompt_manager.template_store is not None
        assert prompt_manager.template_manager is not None
        assert prompt_manager.template_engine is not None
        assert prompt_manager.prompt_builder is not None
        
        # Should have built-in templates loaded
        templates = prompt_manager.template_manager.list_templates()
        assert len(templates) > 0
    
    def test_create_conversation_with_prompt(self, prompt_manager):
        """Test creating a conversation with prompt configuration."""
        conversation_id = prompt_manager.create_conversation_with_prompt(
            title="Test Conversation",
            system_template_id="system_coding",
            thinking_mode=ThinkingMode.STEP_BY_STEP,
            prompt_variables={"language": "Python"}
        )
        
        assert conversation_id is not None
        
        # Verify prompt configuration is stored
        config = prompt_manager.get_conversation_prompt_config(conversation_id)
        assert config is not None
        assert config["system_template_id"] == "system_coding"
        assert config["thinking_mode"] == "step_by_step"
        assert config["prompt_variables"]["language"] == "Python"
    
    def test_add_message_with_thinking(self, prompt_manager):
        """Test adding a message with thinking mode."""
        conversation_id = prompt_manager.create_conversation("Test Thinking")
        
        message = prompt_manager.add_message_with_thinking(
            conversation_id=conversation_id,
            user_id="user1",
            text="Solve this problem step by step",
            thinking_mode=ThinkingMode.ANALYTICAL,
            prompt_variables={"difficulty": "medium"}
        )
        
        assert message is not None
        assert message.text == "Solve this problem step by step"
        assert message.thinking_mode == "analytical"
        assert message.prompt_context["difficulty"] == "medium"
    
    def test_available_templates(self, prompt_manager):
        """Test getting available templates."""
        available = prompt_manager.get_available_templates()
        
        assert "system_templates" in available
        assert "thinking_templates" in available
        assert "all_templates" in available
        assert "thinking_modes" in available
        
        # Should have built-in system templates
        system_templates = available["system_templates"]
        assert len(system_templates) > 0
        
        # Should have thinking modes
        thinking_modes = available["thinking_modes"]
        assert "none" in thinking_modes
        assert "step_by_step" in thinking_modes
        assert "analytical" in thinking_modes
    
    def test_create_custom_template(self, prompt_manager):
        """Test creating a custom template."""
        template_id = prompt_manager.create_custom_template(
            name="Custom Test Template",
            description="A custom template for testing",
            template="Hello {name}! Your task is {task}.",
            category="custom",
            variables=["name", "task"],
            tags=["test", "custom"]
        )
        
        assert template_id is not None
        
        # Verify template was created
        template = prompt_manager.template_manager.get_template(template_id)
        assert template is not None
        assert template.name == "Custom Test Template"
        assert template.category == "custom"
        assert "test" in template.tags
    
    def test_test_template(self, prompt_manager):
        """Test testing a template with variables."""
        # Create a custom template first
        template_id = prompt_manager.create_custom_template(
            name="Test Template",
            description="Template for testing",
            template="Hello {name}! Today is {today()}.",
            variables=["name"]
        )
        
        # Test the template
        result = prompt_manager.test_template(
            template_id,
            variables={"name": "Alice"}
        )
        
        assert "Hello Alice!" in result
        assert len(result) > len("Hello Alice! Today is .")  # Should have date
    
    def test_update_conversation_prompt_config(self, prompt_manager):
        """Test updating conversation prompt configuration."""
        conversation_id = prompt_manager.create_conversation_with_prompt(
            title="Config Test",
            thinking_mode=ThinkingMode.NONE
        )
        
        # Update the configuration
        success = prompt_manager.update_conversation_prompt_config(
            conversation_id,
            system_template_id="system_analysis",
            thinking_mode="analytical",
            prompt_variables={"focus": "data"}
        )
        
        assert success is True
        
        # Verify updates
        config = prompt_manager.get_conversation_prompt_config(conversation_id)
        assert config["system_template_id"] == "system_analysis"
        assert config["thinking_mode"] == "analytical"
        assert config["prompt_variables"]["focus"] == "data"
    
    def test_backup_templates(self, prompt_manager):
        """Test creating template backups."""
        # Add a custom template
        prompt_manager.create_custom_template(
            name="Backup Test",
            description="Test backup functionality",
            template="Backup content"
        )
        
        # Create backup
        backup_name = prompt_manager.backup_templates()
        assert backup_name is not None
        assert backup_name.startswith("backup_")
        
        # Verify backup exists
        backups = prompt_manager.template_store.list_backups()
        assert len(backups) > 0
        assert any(b["name"] == backup_name for b in backups)
    
    def test_conversation_analysis(self, prompt_manager):
        """Test analyzing conversation prompts."""
        conversation_id = prompt_manager.create_conversation_with_prompt(
            title="Analysis Test",
            thinking_mode=ThinkingMode.STEP_BY_STEP
        )
        
        # Add messages with different thinking modes
        prompt_manager.add_message_with_thinking(
            conversation_id=conversation_id,
            user_id="user1",
            text="First message",
            thinking_mode=ThinkingMode.ANALYTICAL
        )
        
        prompt_manager.add_message_with_thinking(
            conversation_id=conversation_id,
            user_id="user1",
            text="Second message",
            thinking_mode=ThinkingMode.CREATIVE
        )
        
        # Analyze conversation
        analysis = prompt_manager.analyze_conversation_prompts(conversation_id)
        
        assert analysis["total_messages"] == 2
        assert analysis["messages_with_thinking"] == 2
        assert "analytical" in analysis["thinking_modes_used"]
        assert "creative" in analysis["thinking_modes_used"]
    
    def test_nonexistent_conversation_operations(self, prompt_manager):
        """Test operations on nonexistent conversations."""
        # Test getting config for nonexistent conversation
        config = prompt_manager.get_conversation_prompt_config("nonexistent")
        assert config is None
        
        # Test updating config for nonexistent conversation
        success = prompt_manager.update_conversation_prompt_config("nonexistent")
        assert success is False
        
        # Test analysis for nonexistent conversation
        analysis = prompt_manager.analyze_conversation_prompts("nonexistent")
        assert analysis == {}


class TestPromptIntegrationWithBuiltins:
    """Test integration with built-in templates and functionality."""
    
    @pytest.fixture
    def prompt_manager(self):
        """Create a prompt conversation manager for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield PromptConversationManager(temp_dir)
    
    def test_builtin_system_templates(self, prompt_manager):
        """Test that built-in system templates work correctly."""
        # Test with coding template
        conversation_id = prompt_manager.create_conversation_with_prompt(
            title="Coding Test",
            system_template_id="system_coding"
        )
        
        config = prompt_manager.get_conversation_prompt_config(conversation_id)
        assert config["system_template_id"] == "system_coding"
        
        # Test with analysis template
        conversation_id2 = prompt_manager.create_conversation_with_prompt(
            title="Analysis Test",
            system_template_id="system_analysis"
        )
        
        config2 = prompt_manager.get_conversation_prompt_config(conversation_id2)
        assert config2["system_template_id"] == "system_analysis"
    
    def test_builtin_thinking_templates(self, prompt_manager):
        """Test that built-in thinking templates work correctly."""
        thinking_templates = prompt_manager.template_manager.list_thinking_templates()
        
        # Should have built-in thinking templates
        template_names = [t["name"] for t in thinking_templates]
        assert "step_by_step_deep" in template_names
        assert "creative_exploration" in template_names
        assert "analytical_brief" in template_names
        
        # Test using a thinking template
        conversation_id = prompt_manager.create_conversation_with_prompt(
            title="Thinking Test",
            thinking_mode=ThinkingMode.STEP_BY_STEP
        )
        
        message = prompt_manager.add_message_with_thinking(
            conversation_id=conversation_id,
            user_id="user1",
            text="Think about this problem",
            thinking_mode=ThinkingMode.STEP_BY_STEP
        )
        
        assert message.thinking_mode == "step_by_step"
    
    def test_template_variable_substitution(self, prompt_manager):
        """Test that template variables work in practice."""
        # Create template with variables
        template_id = prompt_manager.create_custom_template(
            name="Variable Test",
            description="Test variables",
            template="System: {system_name}\nUser: {user_name} ({user_role})\nTask: {task_type}",
            variables=["system_name", "user_name", "user_role", "task_type"]
        )
        
        # Test the template
        result = prompt_manager.test_template(
            template_id,
            variables={
                "system_name": "ChatBot",
                "user_name": "Alice",
                "user_role": "developer",
                "task_type": "code review"
            }
        )
        
        assert "System: ChatBot" in result
        assert "User: Alice (developer)" in result
        assert "Task: code review" in result
    
    def test_thinking_mode_combinations(self, prompt_manager):
        """Test different combinations of thinking modes and templates."""
        test_cases = [
            (ThinkingMode.STEP_BY_STEP, "system_coding"),
            (ThinkingMode.ANALYTICAL, "system_analysis"),
            (ThinkingMode.CREATIVE, "system_default"),
            (ThinkingMode.PROS_CONS, "system_coding")
        ]
        
        for thinking_mode, system_template in test_cases:
            conversation_id = prompt_manager.create_conversation_with_prompt(
                title=f"Test {thinking_mode.value}",
                system_template_id=system_template,
                thinking_mode=thinking_mode
            )
            
            config = prompt_manager.get_conversation_prompt_config(conversation_id)
            assert config["thinking_mode"] == thinking_mode.value
            assert config["system_template_id"] == system_template
    
    def test_template_storage_persistence(self, prompt_manager):
        """Test that templates persist in storage."""
        # Create custom template
        template_id = prompt_manager.create_custom_template(
            name="Persistence Test",
            description="Test persistence",
            template="Persistent content: {data}",
            variables=["data"]
        )
        
        # Verify it's in the template manager
        template = prompt_manager.template_manager.get_template(template_id)
        assert template is not None
        
        # Verify it's in storage
        stored_template = prompt_manager.template_store.load_template(template_id)
        assert stored_template is not None
        assert stored_template.name == "Persistence Test"
        
        # Create new manager instance and verify template is loaded
        new_manager = PromptConversationManager(prompt_manager.data_dir)
        loaded_template = new_manager.template_manager.get_template(template_id)
        assert loaded_template is not None
        assert loaded_template.name == "Persistence Test"