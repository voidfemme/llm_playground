"""
Template storage and persistence for prompt templates.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

from .template_manager import PromptTemplate, TemplateManager
from ..utils.logging import get_logger


class TemplateStore:
    """Handles persistence and storage of prompt templates."""
    
    def __init__(self, storage_path: str):
        self.storage_path = Path(storage_path)
        self.logger = get_logger(self.__class__.__name__.lower())
        self._ensure_storage_structure()
    
    def _ensure_storage_structure(self):
        """Ensure the storage directory structure exists."""
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        (self.storage_path / "templates").mkdir(exist_ok=True)
        (self.storage_path / "collections").mkdir(exist_ok=True)
        (self.storage_path / "backups").mkdir(exist_ok=True)
    
    def save_template(self, template: PromptTemplate) -> bool:
        """Save a single template to storage."""
        try:
            template_file = self.storage_path / "templates" / f"{template.id}.json"
            with open(template_file, 'w') as f:
                json.dump(template.to_dict(), f, indent=2)
            
            self.logger.debug(f"Saved template: {template.name}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to save template {template.id}: {e}")
            return False
    
    def load_template(self, template_id: str) -> Optional[PromptTemplate]:
        """Load a single template from storage."""
        try:
            template_file = self.storage_path / "templates" / f"{template_id}.json"
            if not template_file.exists():
                return None
            
            with open(template_file, 'r') as f:
                data = json.load(f)
            
            return PromptTemplate.from_dict(data)
        except Exception as e:
            self.logger.error(f"Failed to load template {template_id}: {e}")
            return None
    
    def delete_template(self, template_id: str) -> bool:
        """Delete a template from storage."""
        try:
            template_file = self.storage_path / "templates" / f"{template_id}.json"
            if template_file.exists():
                template_file.unlink()
                self.logger.debug(f"Deleted template: {template_id}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Failed to delete template {template_id}: {e}")
            return False
    
    def list_templates(self) -> List[str]:
        """List all template IDs in storage."""
        template_dir = self.storage_path / "templates"
        return [
            f.stem for f in template_dir.glob("*.json")
            if f.is_file()
        ]
    
    def save_template_collection(
        self, 
        collection_name: str, 
        templates: List[PromptTemplate],
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Save a collection of templates."""
        try:
            collection_data = {
                'name': collection_name,
                'created_at': datetime.now().isoformat(),
                'metadata': metadata or {},
                'templates': [template.to_dict() for template in templates]
            }
            
            collection_file = self.storage_path / "collections" / f"{collection_name}.json"
            with open(collection_file, 'w') as f:
                json.dump(collection_data, f, indent=2)
            
            self.logger.info(f"Saved template collection: {collection_name} ({len(templates)} templates)")
            return True
        except Exception as e:
            self.logger.error(f"Failed to save collection {collection_name}: {e}")
            return False
    
    def load_template_collection(self, collection_name: str) -> Optional[List[PromptTemplate]]:
        """Load a template collection."""
        try:
            collection_file = self.storage_path / "collections" / f"{collection_name}.json"
            if not collection_file.exists():
                return None
            
            with open(collection_file, 'r') as f:
                data = json.load(f)
            
            templates = []
            for template_data in data.get('templates', []):
                templates.append(PromptTemplate.from_dict(template_data))
            
            return templates
        except Exception as e:
            self.logger.error(f"Failed to load collection {collection_name}: {e}")
            return None
    
    def list_collections(self) -> List[Dict[str, Any]]:
        """List all template collections."""
        collections = []
        collection_dir = self.storage_path / "collections"
        
        for collection_file in collection_dir.glob("*.json"):
            try:
                with open(collection_file, 'r') as f:
                    data = json.load(f)
                
                collections.append({
                    'name': data.get('name', collection_file.stem),
                    'created_at': data.get('created_at', ''),
                    'template_count': len(data.get('templates', [])),
                    'metadata': data.get('metadata', {})
                })
            except Exception as e:
                self.logger.warning(f"Failed to read collection {collection_file}: {e}")
        
        return collections
    
    def create_backup(self, backup_name: Optional[str] = None) -> str:
        """Create a backup of all templates."""
        if backup_name is None:
            backup_name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        backup_data = {
            'backup_name': backup_name,
            'created_at': datetime.now().isoformat(),
            'templates': [],
            'collections': []
        }
        
        # Backup all templates
        for template_id in self.list_templates():
            template = self.load_template(template_id)
            if template:
                backup_data['templates'].append(template.to_dict())
        
        # Backup all collections
        for collection_info in self.list_collections():
            collection_name = collection_info['name']
            try:
                collection_file = self.storage_path / "collections" / f"{collection_name}.json"
                with open(collection_file, 'r') as f:
                    collection_data = json.load(f)
                backup_data['collections'].append(collection_data)
            except Exception as e:
                self.logger.warning(f"Failed to backup collection {collection_name}: {e}")
        
        # Save backup
        backup_file = self.storage_path / "backups" / f"{backup_name}.json"
        try:
            with open(backup_file, 'w') as f:
                json.dump(backup_data, f, indent=2)
            
            self.logger.info(f"Created backup: {backup_name}")
            return backup_name
        except Exception as e:
            self.logger.error(f"Failed to create backup: {e}")
            raise
    
    def restore_backup(self, backup_name: str, overwrite: bool = False) -> bool:
        """Restore templates from a backup."""
        backup_file = self.storage_path / "backups" / f"{backup_name}.json"
        if not backup_file.exists():
            self.logger.error(f"Backup not found: {backup_name}")
            return False
        
        try:
            with open(backup_file, 'r') as f:
                backup_data = json.load(f)
            
            restored_count = 0
            
            # Restore templates
            for template_data in backup_data.get('templates', []):
                template = PromptTemplate.from_dict(template_data)
                
                # Check if template exists
                if not overwrite and self.load_template(template.id):
                    self.logger.warning(f"Template {template.id} already exists, skipping")
                    continue
                
                if self.save_template(template):
                    restored_count += 1
            
            # Restore collections
            for collection_data in backup_data.get('collections', []):
                collection_name = collection_data.get('name', 'unknown')
                collection_file = self.storage_path / "collections" / f"{collection_name}.json"
                
                if not overwrite and collection_file.exists():
                    self.logger.warning(f"Collection {collection_name} already exists, skipping")
                    continue
                
                with open(collection_file, 'w') as f:
                    json.dump(collection_data, f, indent=2)
            
            self.logger.info(f"Restored {restored_count} templates from backup: {backup_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to restore backup {backup_name}: {e}")
            return False
    
    def list_backups(self) -> List[Dict[str, Any]]:
        """List all available backups."""
        backups = []
        backup_dir = self.storage_path / "backups"
        
        for backup_file in backup_dir.glob("*.json"):
            try:
                with open(backup_file, 'r') as f:
                    data = json.load(f)
                
                backups.append({
                    'name': data.get('backup_name', backup_file.stem),
                    'created_at': data.get('created_at', ''),
                    'template_count': len(data.get('templates', [])),
                    'collection_count': len(data.get('collections', [])),
                    'file_size': backup_file.stat().st_size
                })
            except Exception as e:
                self.logger.warning(f"Failed to read backup {backup_file}: {e}")
        
        return sorted(backups, key=lambda x: x['created_at'], reverse=True)
    
    def sync_from_template_manager(self, template_manager: TemplateManager) -> int:
        """Sync templates from a template manager to storage."""
        synced_count = 0
        
        for template in template_manager.templates.values():
            if self.save_template(template):
                synced_count += 1
        
        self.logger.info(f"Synced {synced_count} templates to storage")
        return synced_count
    
    def sync_to_template_manager(self, template_manager: TemplateManager, overwrite: bool = False) -> int:
        """Sync templates from storage to a template manager."""
        synced_count = 0
        
        for template_id in self.list_templates():
            template = self.load_template(template_id)
            if template:
                # Check if template exists in manager
                if not overwrite and template_manager.get_template(template_id):
                    continue
                
                template_manager.add_template(template)
                synced_count += 1
        
        self.logger.info(f"Synced {synced_count} templates to template manager")
        return synced_count
    
    def search_templates(self, query: str) -> List[PromptTemplate]:
        """Search templates in storage by content."""
        results = []
        query_lower = query.lower()
        
        for template_id in self.list_templates():
            template = self.load_template(template_id)
            if template:
                if (query_lower in template.name.lower() or
                    query_lower in template.description.lower() or
                    query_lower in template.template.lower() or
                    any(query_lower in tag.lower() for tag in template.tags)):
                    results.append(template)
        
        return results
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """Get statistics about the template storage."""
        template_count = len(self.list_templates())
        collection_count = len(self.list_collections())
        backup_count = len(self.list_backups())
        
        # Calculate storage size
        total_size = 0
        for path in self.storage_path.rglob("*.json"):
            total_size += path.stat().st_size
        
        return {
            'template_count': template_count,
            'collection_count': collection_count,
            'backup_count': backup_count,
            'total_size_bytes': total_size,
            'storage_path': str(self.storage_path)
        }
    
    def cleanup_old_backups(self, keep_count: int = 10) -> int:
        """Clean up old backups, keeping only the most recent ones."""
        backups = self.list_backups()
        if len(backups) <= keep_count:
            return 0
        
        # Sort by creation date and remove oldest
        backups_to_remove = backups[keep_count:]
        removed_count = 0
        
        for backup in backups_to_remove:
            backup_file = self.storage_path / "backups" / f"{backup['name']}.json"
            try:
                backup_file.unlink()
                removed_count += 1
            except Exception as e:
                self.logger.warning(f"Failed to remove backup {backup['name']}: {e}")
        
        self.logger.info(f"Cleaned up {removed_count} old backups")
        return removed_count