"""
Tests for the template store functionality.
"""

import pytest
import tempfile
import json
from pathlib import Path
from datetime import datetime

from chatbot_library.prompts.template_store import TemplateStore
from chatbot_library.prompts.template_manager import TemplateManager, PromptTemplate


class TestTemplateStore:
    """Test the TemplateStore class."""
    
    @pytest.fixture
    def temp_store(self):
        """Create a temporary template store for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield TemplateStore(temp_dir)
    
    @pytest.fixture
    def sample_template(self):
        """Create a sample template for testing."""
        return PromptTemplate(
            id="test-template",
            name="Test Template",
            description="A test template",
            template="Hello {name}! This is a test.",
            variables=["name"],
            category="test",
            tags=["test", "sample"]
        )
    
    def test_storage_structure_creation(self, temp_store):
        """Test that storage directory structure is created."""
        storage_path = Path(temp_store.storage_path)
        
        assert storage_path.exists()
        assert (storage_path / "templates").exists()
        assert (storage_path / "collections").exists()
        assert (storage_path / "backups").exists()
    
    def test_save_and_load_template(self, temp_store, sample_template):
        """Test saving and loading a template."""
        # Save template
        success = temp_store.save_template(sample_template)
        assert success is True
        
        # Load template
        loaded = temp_store.load_template("test-template")
        assert loaded is not None
        assert loaded.id == sample_template.id
        assert loaded.name == sample_template.name
        assert loaded.template == sample_template.template
        assert loaded.variables == sample_template.variables
    
    def test_load_nonexistent_template(self, temp_store):
        """Test loading a template that doesn't exist."""
        loaded = temp_store.load_template("nonexistent")
        assert loaded is None
    
    def test_delete_template(self, temp_store, sample_template):
        """Test deleting a template."""
        # Save template first
        temp_store.save_template(sample_template)
        assert temp_store.load_template("test-template") is not None
        
        # Delete template
        success = temp_store.delete_template("test-template")
        assert success is True
        
        # Verify it's deleted
        loaded = temp_store.load_template("test-template")
        assert loaded is None
    
    def test_delete_nonexistent_template(self, temp_store):
        """Test deleting a template that doesn't exist."""
        success = temp_store.delete_template("nonexistent")
        assert success is False
    
    def test_list_templates(self, temp_store):
        """Test listing templates."""
        # Initially empty
        templates = temp_store.list_templates()
        assert len(templates) == 0
        
        # Add some templates
        template1 = PromptTemplate(id="t1", name="T1", description="Test 1", template="Template 1")
        template2 = PromptTemplate(id="t2", name="T2", description="Test 2", template="Template 2")
        
        temp_store.save_template(template1)
        temp_store.save_template(template2)
        
        # List templates
        templates = temp_store.list_templates()
        assert len(templates) == 2
        assert "t1" in templates
        assert "t2" in templates
    
    def test_save_and_load_collection(self, temp_store):
        """Test saving and loading template collections."""
        # Create templates
        templates = [
            PromptTemplate(id="c1", name="Collection 1", description="Test", template="T1"),
            PromptTemplate(id="c2", name="Collection 2", description="Test", template="T2")
        ]
        
        metadata = {"author": "test", "version": "1.0"}
        
        # Save collection
        success = temp_store.save_template_collection("test-collection", templates, metadata)
        assert success is True
        
        # Load collection
        loaded_templates = temp_store.load_template_collection("test-collection")
        assert loaded_templates is not None
        assert len(loaded_templates) == 2
        assert loaded_templates[0].id == "c1"
        assert loaded_templates[1].id == "c2"
    
    def test_load_nonexistent_collection(self, temp_store):
        """Test loading a collection that doesn't exist."""
        loaded = temp_store.load_template_collection("nonexistent")
        assert loaded is None
    
    def test_list_collections(self, temp_store):
        """Test listing collections."""
        # Initially empty
        collections = temp_store.list_collections()
        assert len(collections) == 0
        
        # Add collection
        templates = [PromptTemplate(id="test", name="Test", description="Test", template="Test")]
        temp_store.save_template_collection("test-collection", templates)
        
        # List collections
        collections = temp_store.list_collections()
        assert len(collections) == 1
        assert collections[0]["name"] == "test-collection"
        assert collections[0]["template_count"] == 1
    
    def test_backup_and_restore(self, temp_store):
        """Test creating and restoring backups."""
        # Add some templates and collections
        template = PromptTemplate(id="backup-test", name="Backup Test", description="Test", template="Test")
        temp_store.save_template(template)
        
        collection_templates = [
            PromptTemplate(id="col1", name="Col1", description="Test", template="Test")
        ]
        temp_store.save_template_collection("backup-collection", collection_templates)
        
        # Create backup
        backup_name = temp_store.create_backup()
        assert backup_name is not None
        assert backup_name.startswith("backup_")
        
        # Delete original data
        temp_store.delete_template("backup-test")
        assert temp_store.load_template("backup-test") is None
        
        # Restore backup
        success = temp_store.restore_backup(backup_name, overwrite=True)
        assert success is True
        
        # Verify data is restored
        restored_template = temp_store.load_template("backup-test")
        assert restored_template is not None
        assert restored_template.name == "Backup Test"
        
        restored_collection = temp_store.load_template_collection("backup-collection")
        assert restored_collection is not None
        assert len(restored_collection) == 1
    
    def test_restore_nonexistent_backup(self, temp_store):
        """Test restoring a backup that doesn't exist."""
        success = temp_store.restore_backup("nonexistent-backup")
        assert success is False
    
    def test_list_backups(self, temp_store):
        """Test listing backups."""
        # Initially empty
        backups = temp_store.list_backups()
        assert len(backups) == 0
        
        # Create backup
        backup_name = temp_store.create_backup()
        
        # List backups
        backups = temp_store.list_backups()
        assert len(backups) == 1
        assert backups[0]["name"] == backup_name
        assert "created_at" in backups[0]
        assert "template_count" in backups[0]
    
    def test_sync_with_template_manager(self, temp_store):
        """Test syncing with template manager."""
        # Create template manager with templates
        manager = TemplateManager()
        
        # Add custom template to manager
        custom_template = PromptTemplate(
            id="sync-test",
            name="Sync Test",
            description="Test sync",
            template="Sync content"
        )
        manager.add_template(custom_template)
        
        # Sync from manager to store
        synced_count = temp_store.sync_from_template_manager(manager)
        assert synced_count > 0  # Should sync built-in templates plus custom one
        
        # Verify custom template was synced
        loaded = temp_store.load_template("sync-test")
        assert loaded is not None
        assert loaded.name == "Sync Test"
        
        # Create new store and sync to manager
        new_manager = TemplateManager()
        initial_count = len(new_manager.templates)
        
        synced_count = temp_store.sync_to_template_manager(new_manager)
        assert synced_count > 0
        assert len(new_manager.templates) > initial_count
        
        # Verify custom template was synced to new manager
        synced_template = new_manager.get_template("sync-test")
        assert synced_template is not None
        assert synced_template.name == "Sync Test"
    
    def test_search_templates(self, temp_store):
        """Test searching templates in storage."""
        # Add some templates
        templates = [
            PromptTemplate(id="search1", name="Python Helper", description="Help with Python", template="Python code"),
            PromptTemplate(id="search2", name="JavaScript Guide", description="JS guidance", template="JavaScript code"),
            PromptTemplate(id="search3", name="General Assistant", description="General help", template="General content", tags=["python"])
        ]
        
        for template in templates:
            temp_store.save_template(template)
        
        # Search for Python
        results = temp_store.search_templates("python")
        assert len(results) == 2  # Should find "Python Helper" and tagged template
        
        result_names = [t.name for t in results]
        assert "Python Helper" in result_names
        assert "General Assistant" in result_names
        
        # Search for JavaScript
        results = temp_store.search_templates("javascript")
        assert len(results) == 1
        assert results[0].name == "JavaScript Guide"
        
        # Search for nonexistent term
        results = temp_store.search_templates("nonexistent")
        assert len(results) == 0
    
    def test_storage_stats(self, temp_store):
        """Test getting storage statistics."""
        # Add some data
        template = PromptTemplate(id="stats-test", name="Stats Test", description="Test", template="Test")
        temp_store.save_template(template)
        
        collection_templates = [template]
        temp_store.save_template_collection("stats-collection", collection_templates)
        
        backup_name = temp_store.create_backup()
        
        # Get stats
        stats = temp_store.get_storage_stats()
        
        assert stats["template_count"] == 1
        assert stats["collection_count"] == 1
        assert stats["backup_count"] == 1
        assert stats["total_size_bytes"] > 0
        assert "storage_path" in stats
    
    def test_cleanup_old_backups(self, temp_store):
        """Test cleaning up old backups."""
        # Create multiple backups
        backup_names = []
        for i in range(5):
            backup_name = temp_store.create_backup(f"test-backup-{i}")
            backup_names.append(backup_name)
        
        # Verify all backups exist
        backups = temp_store.list_backups()
        assert len(backups) == 5
        
        # Clean up, keeping only 3
        removed_count = temp_store.cleanup_old_backups(keep_count=3)
        assert removed_count == 2
        
        # Verify only 3 backups remain
        backups = temp_store.list_backups()
        assert len(backups) == 3
    
    def test_error_handling(self, temp_store):
        """Test error handling in template store operations."""
        # Test loading nonexistent templates
        result = temp_store.load_template("nonexistent")
        assert result is None
        
        # Test deleting nonexistent template
        result = temp_store.delete_template("nonexistent")
        assert result is False
        
        # Test loading nonexistent collection
        result = temp_store.load_template_collection("nonexistent")
        assert result is None