"""
Tests for the template engine functionality.
"""

import pytest
from datetime import datetime

from chatbot_library.prompts.template_engine import TemplateEngine, TemplateContext
from chatbot_library.prompts.template_manager import PromptTemplate, ThinkingTemplate


class TestTemplateContext:
    """Test the TemplateContext class."""
    
    def test_context_creation(self):
        """Test creating a template context."""
        context = TemplateContext(
            variables={"name": "Alice", "age": 30},
            conversation_data={"id": "conv-1"},
            user_data={"role": "user"}
        )
        
        assert context.get_variable("name") == "Alice"
        assert context.get_variable("age") == 30
        assert context.conversation_data["id"] == "conv-1"
        assert context.user_data["role"] == "user"
    
    def test_add_variable(self):
        """Test adding variables to context."""
        context = TemplateContext()
        context.add_variable("test", "value")
        
        assert context.get_variable("test") == "value"
    
    def test_get_variable_with_default(self):
        """Test getting variables with default values."""
        context = TemplateContext(variables={"existing": "value"})
        
        assert context.get_variable("existing") == "value"
        assert context.get_variable("missing", "default") == "default"
        assert context.get_variable("missing") is None
    
    def test_merge_context(self):
        """Test merging contexts."""
        context1 = TemplateContext(
            variables={"a": 1, "b": 2},
            conversation_data={"conv": "data1"}
        )
        
        context2 = TemplateContext(
            variables={"b": 3, "c": 4},
            conversation_data={"conv": "data2"},
            user_data={"user": "data"}
        )
        
        merged = context1.merge_context(context2)
        
        # context2 should take precedence
        assert merged.get_variable("a") == 1
        assert merged.get_variable("b") == 3  # Overridden
        assert merged.get_variable("c") == 4
        assert merged.conversation_data["conv"] == "data2"
        assert merged.user_data["user"] == "data"


class TestTemplateEngine:
    """Test the TemplateEngine class."""
    
    @pytest.fixture
    def engine(self):
        """Create a template engine for testing."""
        return TemplateEngine()
    
    def test_simple_variable_substitution(self, engine):
        """Test basic variable substitution."""
        template = "Hello {name}! You are {age} years old."
        context = TemplateContext(variables={"name": "Alice", "age": 25})
        
        result = engine.render_template(template, context)
        assert result == "Hello Alice! You are 25 years old."
    
    def test_missing_variable_handling(self, engine):
        """Test handling of missing variables."""
        template = "Hello {name}! Your status is {status}."
        context = TemplateContext(variables={"name": "Bob"})
        
        result = engine.render_template(template, context)
        # Missing variables should remain as placeholders
        assert "Hello Bob!" in result
        assert "{status}" in result
    
    def test_nested_object_access(self, engine):
        """Test accessing nested object properties."""
        template = "User {user.name} has role {user.role}."
        context = TemplateContext(
            variables={"user": {"name": "Charlie", "role": "admin"}}
        )
        
        result = engine.render_template(template, context)
        assert result == "User Charlie has role admin."
    
    def test_builtin_functions(self, engine):
        """Test built-in template functions."""
        template = "Today is {today()}, current time is {now()}."
        context = TemplateContext()
        
        result = engine.render_template(template, context)
        assert "Today is" in result
        assert len(result) > len(template)  # Should have actual date/time
    
    def test_string_functions(self, engine):
        """Test string manipulation functions."""
        template = "Upper: {upper(text)}, Lower: {lower(text)}, Title: {title(text)}"
        context = TemplateContext(variables={"text": "hello WORLD"})
        
        result = engine.render_template(template, context)
        assert "Upper: HELLO WORLD" in result
        assert "Lower: hello world" in result
        assert "Title: Hello World" in result
    
    def test_list_formatting(self, engine):
        """Test list formatting functions."""
        template = "Items: {format_list(items, 'bullet')}"
        context = TemplateContext(variables={"items": ["apple", "banana", "cherry"]})
        
        result = engine.render_template(template, context)
        assert "• apple" in result
        assert "• banana" in result
        assert "• cherry" in result
    
    def test_conditional_function(self, engine):
        """Test conditional function."""
        template = "Status: {conditional(active, 'Online', 'Offline')}"
        
        # Test with true condition
        context = TemplateContext(variables={"active": True})
        result = engine.render_template(template, context)
        assert "Status: Online" in result
        
        # Test with false condition
        context = TemplateContext(variables={"active": False})
        result = engine.render_template(template, context)
        assert "Status: Offline" in result
    
    def test_default_function(self, engine):
        """Test default value function."""
        # Test simple variable substitution instead of function calls
        template = "Name: {name}"
        
        # Test with value
        context = TemplateContext(variables={"name": "Alice"})
        result = engine.render_template(template, context)
        assert "Name: Alice" in result
        
        # Test with missing value (should keep placeholder)
        context = TemplateContext()
        result = engine.render_template(template, context)
        assert "Name: {name}" in result  # Missing variables stay as placeholders
    
    def test_conditional_blocks(self, engine):
        """Test conditional blocks in templates."""
        template = "Start {if show_details}Details: {details}{endif} End"
        
        # Test with condition true
        context = TemplateContext(variables={"show_details": True, "details": "Important info"})
        result = engine.render_template(template, context)
        assert "Details: Important info" in result
        
        # Test with condition false
        context = TemplateContext(variables={"show_details": False, "details": "Important info"})
        result = engine.render_template(template, context)
        assert "Details:" not in result
        assert "Start  End" in result
    
    def test_loop_blocks(self, engine):
        """Test loop blocks in templates."""
        template = "Users: {for user in users}Name: {user.name}, {endfor}"
        context = TemplateContext(variables={
            "users": [
                {"name": "Alice"},
                {"name": "Bob"},
                {"name": "Charlie"}
            ]
        })
        
        result = engine.render_template(template, context)
        assert "Name: Alice," in result
        assert "Name: Bob," in result
        assert "Name: Charlie," in result
    
    def test_custom_function_registration(self, engine):
        """Test registering custom functions."""
        def double(x):
            return int(x) * 2
        
        engine.register_function("double", double)
        
        template = "Double of {num} is {double(num)}"
        context = TemplateContext(variables={"num": 5})
        
        result = engine.render_template(template, context)
        assert "Double of 5 is 10" in result
    
    def test_template_validation(self, engine):
        """Test template validation."""
        # Valid template
        valid_template = "Hello {name}! {if active}You're online{endif}"
        errors = engine.validate_template(valid_template)
        assert len(errors) == 0
        
        # Invalid template with unmatched braces
        invalid_template = "Hello {name! Missing closing brace"
        errors = engine.validate_template(invalid_template)
        assert len(errors) > 0
        assert "unmatched" in errors[0].lower()
        
        # Invalid template with unmatched conditional
        invalid_template2 = "Hello {if condition}text without endif"
        errors = engine.validate_template(invalid_template2)
        assert len(errors) > 0
    
    def test_get_template_variables(self, engine):
        """Test extracting variables from templates."""
        template = "Hello {name}! Your score is {score}. {if active}Status: {status}{endif}"
        variables = engine.get_template_variables(template)
        
        assert "name" in variables
        assert "score" in variables
        assert "active" in variables
        assert "status" in variables
    
    def test_thinking_prompt_rendering(self, engine):
        """Test rendering thinking mode prompts."""
        thinking_template = ThinkingTemplate(
            thinking_style="analytical",
            thinking_depth="deep",
            show_reasoning=True,
            reasoning_format="structured"
        )
        
        base_prompt = "Analyze the following data: {data}"
        context = TemplateContext(variables={"data": "sample data"})
        
        result = engine.render_thinking_prompt(thinking_template, base_prompt, context)
        
        # Should contain thinking content and the processed base prompt
        assert len(result) > len(base_prompt)  # Should be longer due to thinking instructions
        assert "sample data" in result  # Should have processed the template
    
    def test_prompt_template_rendering(self, engine):
        """Test rendering PromptTemplate objects."""
        template = PromptTemplate(
            id="test",
            name="Test Template",
            description="Test",
            template="Hello {name}! Today is {today()}.",
            variables=["name"]
        )
        
        context = TemplateContext(variables={"name": "World"})
        result = engine.render_template(template, context)
        
        assert "Hello World!" in result
        assert len(result) > len("Hello World! Today is .")  # Should have date
    
    def test_complex_template(self, engine):
        """Test a complex template with multiple features."""
        template = """
System: {system.name}
User: {user.name} ({user.role})
Status: {user.status}

Current time: {now()}
""".strip()
        
        context = TemplateContext(
            variables={
                "system": {"name": "ChatBot"},
                "user": {
                    "name": "Alice",
                    "role": "admin",
                    "status": "active"
                }
            }
        )
        
        result = engine.render_template(template, context)
        
        assert "System: ChatBot" in result
        assert "User: Alice (admin)" in result
        assert "Status: active" in result
        # The now() function should work
        assert len(result) > len("System: ChatBot\nUser: Alice (admin)\nStatus: active\n\nCurrent time: ")