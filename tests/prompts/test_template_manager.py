"""
Tests for the template manager functionality.
"""

import pytest
import tempfile
import json
from datetime import datetime
from pathlib import Path

from chatbot_library.prompts.template_manager import TemplateManager, PromptTemplate, ThinkingTemplate


class TestPromptTemplate:
    """Test the PromptTemplate class."""
    
    def test_template_creation(self):
        """Test creating a basic prompt template."""
        template = PromptTemplate(
            id="test-1",
            name="Test Template",
            description="A test template",
            template="Hello {name}!",
            variables=["name"]
        )
        
        assert template.id == "test-1"
        assert template.name == "Test Template"
        assert template.template == "Hello {name}!"
        assert "name" in template.variables
        assert template.category == "general"
    
    def test_template_serialization(self):
        """Test template to/from dict conversion."""
        template = PromptTemplate(
            id="test-2",
            name="Serialization Test",
            description="Test serialization",
            template="Test content",
            category="test",
            tags=["test", "serialization"]
        )
        
        # Convert to dict
        template_dict = template.to_dict()
        assert template_dict["id"] == "test-2"
        assert template_dict["name"] == "Serialization Test"
        assert "test" in template_dict["tags"]
        
        # Convert back from dict
        restored = PromptTemplate.from_dict(template_dict)
        assert restored.id == template.id
        assert restored.name == template.name
        assert restored.tags == template.tags


class TestThinkingTemplate:
    """Test the ThinkingTemplate class."""
    
    def test_thinking_template_creation(self):
        """Test creating a thinking template."""
        template = ThinkingTemplate(
            thinking_style="step_by_step",
            thinking_depth="deep",
            show_reasoning=True,
            reasoning_format="structured"
        )
        
        assert template.thinking_style == "step_by_step"
        assert template.thinking_depth == "deep"
        assert template.show_reasoning is True
    
    def test_thinking_prompt_generation(self):
        """Test generating thinking prompts."""
        template = ThinkingTemplate(
            thinking_style="analytical",
            thinking_depth="medium",
            show_reasoning=True,
            reasoning_format="bullet_points"
        )
        
        prompt = template.to_thinking_prompt()
        assert len(prompt) > 0  # Should generate some prompt
        assert "analy" in prompt.lower()  # Should contain analytical-related content
        assert "bullet" in prompt.lower() or "point" in prompt.lower()  # Should mention bullet points
    
    def test_confidence_scoring(self):
        """Test thinking template with confidence scoring."""
        template = ThinkingTemplate(
            thinking_style="pros_cons",
            thinking_depth="shallow",
            confidence_scoring=True
        )
        
        prompt = template.to_thinking_prompt()
        assert "confidence" in prompt.lower()


class TestTemplateManager:
    """Test the TemplateManager class."""
    
    @pytest.fixture
    def template_manager(self):
        """Create a template manager for testing."""
        return TemplateManager()
    
    def test_builtin_templates_loaded(self, template_manager):
        """Test that built-in templates are loaded."""
        templates = template_manager.list_templates()
        assert len(templates) > 0
        
        # Check for specific built-in templates
        template_names = [t['name'] for t in templates]
        assert "Default System Prompt" in template_names
        assert "Coding Assistant" in template_names
    
    def test_add_template(self, template_manager):
        """Test adding a custom template."""
        template = PromptTemplate(
            id="custom-1",
            name="Custom Template",
            description="A custom test template",
            template="Custom content with {variable}",
            variables=["variable"],
            category="custom"
        )
        
        template_manager.add_template(template)
        
        retrieved = template_manager.get_template("custom-1")
        assert retrieved is not None
        assert retrieved.name == "Custom Template"
        assert retrieved.category == "custom"
    
    def test_get_templates_by_category(self, template_manager):
        """Test retrieving templates by category."""
        system_templates = template_manager.get_templates_by_category("system")
        assert len(system_templates) > 0
        
        for template in system_templates:
            assert template.category == "system"
    
    def test_get_templates_by_tag(self, template_manager):
        """Test retrieving templates by tag."""
        coding_templates = template_manager.get_templates_by_tag("coding")
        assert len(coding_templates) > 0
        
        for template in coding_templates:
            assert "coding" in template.tags
    
    def test_search_templates(self, template_manager):
        """Test searching templates."""
        results = template_manager.search_templates("coding")
        assert len(results) > 0
        
        # All results should contain "coding" somewhere
        for template in results:
            content = f"{template.name} {template.description} {template.template} {' '.join(template.tags)}"
            assert "coding" in content.lower()
    
    def test_update_template(self, template_manager):
        """Test updating an existing template."""
        # Add a template first
        template = PromptTemplate(
            id="update-test",
            name="Original Name",
            description="Original description",
            template="Original template"
        )
        template_manager.add_template(template)
        
        # Update it
        success = template_manager.update_template(
            "update-test",
            name="Updated Name",
            description="Updated description"
        )
        
        assert success is True
        
        # Verify update
        updated = template_manager.get_template("update-test")
        assert updated.name == "Updated Name"
        assert updated.description == "Updated description"
        assert updated.template == "Original template"  # Unchanged
    
    def test_delete_template(self, template_manager):
        """Test deleting a template."""
        # Add a template first
        template = PromptTemplate(
            id="delete-test",
            name="To Be Deleted",
            description="Will be deleted",
            template="Delete me"
        )
        template_manager.add_template(template)
        
        # Verify it exists
        assert template_manager.get_template("delete-test") is not None
        
        # Delete it
        success = template_manager.delete_template("delete-test")
        assert success is True
        
        # Verify it's gone
        assert template_manager.get_template("delete-test") is None
    
    def test_thinking_templates(self, template_manager):
        """Test thinking template management."""
        thinking_templates = template_manager.list_thinking_templates()
        assert len(thinking_templates) > 0
        
        # Test getting a specific thinking template
        step_by_step = template_manager.get_thinking_template("step_by_step_deep")
        assert step_by_step is not None
        assert step_by_step.thinking_style == "step_by_step"
        assert step_by_step.thinking_depth == "deep"
    
    def test_export_import_templates(self, template_manager):
        """Test exporting and importing templates."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            export_file = f.name
        
        try:
            # Add a custom template
            template = PromptTemplate(
                id="export-test",
                name="Export Test",
                description="Test export/import",
                template="Export content"
            )
            template_manager.add_template(template)
            
            # Export templates
            success = template_manager.export_templates(export_file, ["export-test"])
            assert success is True
            
            # Verify export file exists and has content
            export_path = Path(export_file)
            assert export_path.exists()
            
            with open(export_file, 'r') as f:
                data = json.load(f)
            
            assert len(data['templates']) == 1
            assert data['templates'][0]['id'] == "export-test"
            
            # Delete the template
            template_manager.delete_template("export-test")
            assert template_manager.get_template("export-test") is None
            
            # Import it back
            imported_count = template_manager.import_templates(export_file)
            assert imported_count == 1
            
            # Verify it's back
            imported = template_manager.get_template("export-test")
            assert imported is not None
            assert imported.name == "Export Test"
            
        finally:
            # Clean up
            Path(export_file).unlink(missing_ok=True)
    
    def test_template_info(self, template_manager):
        """Test getting template info."""
        # Get info for a built-in template
        template_id = "system_default"
        info = template_manager.get_template_info(template_id)
        
        assert info is not None
        assert info['id'] == template_id
        assert 'name' in info
        assert 'description' in info
        assert 'template' in info
        assert 'created_at' in info


class TestTemplateManagerWithStorage:
    """Test TemplateManager with file storage."""
    
    def test_custom_template_loading(self):
        """Test loading custom templates from file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a template file
            template_file = Path(temp_dir) / "templates.json"
            template_data = {
                "templates": [
                    {
                        "id": "file-test",
                        "name": "File Test Template",
                        "description": "Loaded from file",
                        "template": "File content: {data}",
                        "variables": ["data"],
                        "category": "file",
                        "tags": ["file", "test"],
                        "created_at": datetime.now().isoformat(),
                        "updated_at": datetime.now().isoformat(),
                        "version": "1.0"
                    }
                ]
            }
            
            with open(template_file, 'w') as f:
                json.dump(template_data, f)
            
            # Create manager with custom templates
            manager = TemplateManager(str(template_file))
            
            # Verify custom template is loaded
            template = manager.get_template("file-test")
            assert template is not None
            assert template.name == "File Test Template"
            assert template.category == "file"
            assert "file" in template.tags