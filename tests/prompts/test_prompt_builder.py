"""
Tests for the prompt builder functionality.
"""

import pytest
from chatbot_library.prompts import TemplateManager, TemplateEngine, PromptBuilder, ThinkingMode
from chatbot_library.prompts.prompt_builder import PromptConfiguration, BuiltPrompt
from chatbot_library.prompts.template_engine import TemplateContext


class TestPromptConfiguration:
    """Test the PromptConfiguration class."""
    
    def test_default_configuration(self):
        """Test creating a default configuration."""
        config = PromptConfiguration()
        
        assert config.thinking_mode == ThinkingMode.NONE
        assert config.system_template_id is None
        assert config.include_user_context is True
        assert config.include_conversation_summary is False
        assert len(config.variables) == 0
    
    def test_custom_configuration(self):
        """Test creating a custom configuration."""
        config = PromptConfiguration(
            system_template_id="system_coding",
            thinking_mode=ThinkingMode.STEP_BY_STEP,
            thinking_template_name="step_by_step_deep",
            include_conversation_summary=True,
            custom_instructions="Be very careful with code.",
            variables={"language": "Python", "level": "advanced"}
        )
        
        assert config.system_template_id == "system_coding"
        assert config.thinking_mode == ThinkingMode.STEP_BY_STEP
        assert config.thinking_template_name == "step_by_step_deep"
        assert config.include_conversation_summary is True
        assert config.custom_instructions == "Be very careful with code."
        assert config.variables["language"] == "Python"


class TestBuiltPrompt:
    """Test the BuiltPrompt class."""
    
    def test_built_prompt_creation(self):
        """Test creating a built prompt."""
        prompt = BuiltPrompt(
            system_message="You are a helpful assistant.",
            user_message="What is Python?",
            thinking_instructions="Think step by step.",
            metadata={"mode": "coding"}
        )
        
        assert prompt.system_message == "You are a helpful assistant."
        assert prompt.user_message == "What is Python?"
        assert prompt.thinking_instructions == "Think step by step."
        assert prompt.metadata["mode"] == "coding"


class TestPromptBuilder:
    """Test the PromptBuilder class."""
    
    @pytest.fixture
    def prompt_builder(self):
        """Create a prompt builder for testing."""
        template_manager = TemplateManager()
        template_engine = TemplateEngine()
        return PromptBuilder(template_manager, template_engine)
    
    def test_basic_prompt_building(self, prompt_builder):
        """Test building a basic prompt."""
        config = PromptConfiguration()
        built = prompt_builder.build_prompt("Hello, how are you?", config)
        
        assert isinstance(built, BuiltPrompt)
        assert built.user_message == "Hello, how are you?"
        assert built.system_message is not None
        assert len(built.system_message) > 0
        assert built.thinking_instructions is None  # No thinking mode
    
    def test_prompt_with_system_template(self, prompt_builder):
        """Test building a prompt with a system template."""
        config = PromptConfiguration(system_template_id="system_coding")
        built = prompt_builder.build_prompt("Write a Python function", config)
        
        assert "programming" in built.system_message.lower() or "code" in built.system_message.lower()
        assert built.metadata["system_template_id"] == "system_coding"
    
    def test_prompt_with_thinking_mode(self, prompt_builder):
        """Test building a prompt with thinking mode."""
        config = PromptConfiguration(thinking_mode=ThinkingMode.STEP_BY_STEP)
        built = prompt_builder.build_prompt("Solve this problem", config)
        
        assert built.thinking_instructions is not None
        assert "step" in built.thinking_instructions.lower()
        assert built.metadata["thinking_mode"] == "step_by_step"
    
    def test_prompt_with_variables(self, prompt_builder):
        """Test building a prompt with template variables."""
        config = PromptConfiguration(
            variables={"user_name": "Alice", "task": "coding"}
        )
        
        # Create a template that uses variables
        from chatbot_library.prompts.template_manager import PromptTemplate
        template = PromptTemplate(
            id="variable_test",
            name="Variable Test",
            description="Test template with variables",
            template="Hello {user_name}! Your task is {task}.",
            variables=["user_name", "task"]
        )
        prompt_builder.template_manager.add_template(template)
        
        config.system_template_id = "variable_test"
        built = prompt_builder.build_prompt("Let's begin", config)
        
        assert "Hello Alice!" in built.system_message
        assert "Your task is coding" in built.system_message
    
    def test_prompt_with_conversation_context(self, prompt_builder):
        """Test building a prompt with conversation context."""
        config = PromptConfiguration(include_conversation_summary=True)
        conversation_context = {
            "message_count": 5,
            "topics": ["Python", "programming"],
            "last_response_time": "2023-01-01T12:00:00"
        }
        
        built = prompt_builder.build_prompt(
            "Continue our discussion",
            config,
            conversation_context=conversation_context
        )
        
        # The context should be available for template rendering
        assert built.context_used["conversation_data"] == conversation_context
    
    def test_prompt_with_user_context(self, prompt_builder):
        """Test building a prompt with user context."""
        config = PromptConfiguration(include_user_context=True)
        user_context = {
            "name": "Bob",
            "role": "developer",
            "experience": "senior"
        }
        
        built = prompt_builder.build_prompt(
            "Help me with coding",
            config,
            user_context=user_context
        )
        
        assert built.context_used["user_data"] == user_context
    
    def test_prompt_with_custom_instructions(self, prompt_builder):
        """Test building a prompt with custom instructions."""
        config = PromptConfiguration(
            custom_instructions="Always provide code examples."
        )
        
        built = prompt_builder.build_prompt("Explain loops", config)
        
        assert "Always provide code examples" in built.system_message
    
    def test_quick_prompt_building(self, prompt_builder):
        """Test the quick prompt building method."""
        built = prompt_builder.build_quick_prompt(
            "What is AI?",
            thinking_mode=ThinkingMode.ANALYTICAL,
            system_template_id="system_analysis"
        )
        
        assert built.user_message == "What is AI?"
        assert built.thinking_instructions is not None
        assert "analy" in built.thinking_instructions.lower()
        assert built.metadata["thinking_mode"] == "analytical"
    
    def test_thinking_prompt_building(self, prompt_builder):
        """Test building a thinking-focused prompt."""
        built = prompt_builder.build_thinking_prompt(
            "Solve this puzzle",
            thinking_style="pros_cons",
            thinking_depth="deep"
        )
        
        assert built.thinking_instructions is not None
        assert built.metadata["thinking_mode"] == "custom"
    
    def test_task_specific_configurations(self, prompt_builder):
        """Test creating configurations for specific tasks."""
        # Test coding configuration
        coding_config = prompt_builder.create_config_for_task("coding")
        assert coding_config.system_template_id == "system_coding"
        assert coding_config.thinking_mode == ThinkingMode.STEP_BY_STEP
        
        # Test analysis configuration
        analysis_config = prompt_builder.create_config_for_task("analysis")
        assert analysis_config.system_template_id == "system_analysis"
        assert analysis_config.thinking_mode == ThinkingMode.ANALYTICAL
        
        # Test creative configuration
        creative_config = prompt_builder.create_config_for_task("creative")
        assert creative_config.thinking_mode == ThinkingMode.CREATIVE
        
        # Test unknown task (should return default)
        unknown_config = prompt_builder.create_config_for_task("unknown")
        assert unknown_config.thinking_mode == ThinkingMode.NONE
    
    def test_configuration_validation(self, prompt_builder):
        """Test validating prompt configurations."""
        # Valid configuration
        valid_config = PromptConfiguration(system_template_id="system_default")
        errors = prompt_builder.validate_configuration(valid_config)
        assert len(errors) == 0
        
        # Invalid system template
        invalid_config = PromptConfiguration(system_template_id="nonexistent")
        errors = prompt_builder.validate_configuration(invalid_config)
        assert len(errors) > 0
        assert "not found" in errors[0].lower()
        
        # Invalid thinking template
        invalid_thinking_config = PromptConfiguration(
            thinking_mode=ThinkingMode.CUSTOM,
            thinking_template_name="nonexistent"
        )
        errors = prompt_builder.validate_configuration(invalid_thinking_config)
        assert len(errors) > 0
    
    def test_available_configurations(self, prompt_builder):
        """Test getting available configuration options."""
        available = prompt_builder.get_available_configurations()
        
        assert "system_templates" in available
        assert "thinking_templates" in available
        assert "thinking_modes" in available
        assert "task_configs" in available
        
        # Check that we have expected thinking modes
        thinking_modes = available["thinking_modes"]
        assert "none" in thinking_modes
        assert "step_by_step" in thinking_modes
        assert "analytical" in thinking_modes
        assert "creative" in thinking_modes
        
        # Check that we have system templates
        system_templates = available["system_templates"]
        assert len(system_templates) > 0
        
        # Check task configs
        task_configs = available["task_configs"]
        assert "coding" in task_configs
        assert "analysis" in task_configs
    
    def test_complex_prompt_building(self, prompt_builder):
        """Test building a complex prompt with multiple features."""
        config = PromptConfiguration(
            system_template_id="system_coding",
            thinking_mode=ThinkingMode.STEP_BY_STEP,
            include_conversation_summary=True,
            include_user_context=True,
            custom_instructions="Focus on clean, readable code.",
            variables={"language": "Python", "difficulty": "intermediate"}
        )
        
        conversation_context = {
            "message_count": 3,
            "topics": ["functions", "classes"],
            "last_model": "gpt-4"
        }
        
        user_context = {
            "name": "Charlie",
            "experience": "beginner",
            "preferences": "detailed explanations"
        }
        
        built = prompt_builder.build_prompt(
            "How do I create a class?",
            config,
            conversation_context=conversation_context,
            user_context=user_context
        )
        
        # Verify all components are present
        assert "programming" in built.system_message.lower() or "code" in built.system_message.lower()
        assert "Focus on clean, readable code" in built.system_message
        assert built.thinking_instructions is not None
        assert "step" in built.thinking_instructions.lower()
        assert built.user_message == "How do I create a class?"
        
        # Verify metadata
        assert built.metadata["thinking_mode"] == "step_by_step"
        assert built.metadata["system_template_id"] == "system_coding"
        
        # Verify context was captured
        assert built.context_used["conversation_data"] == conversation_context
        assert built.context_used["user_data"] == user_context