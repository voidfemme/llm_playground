"""
Template manager for handling prompt templates and template operations.
"""

import json
import uuid
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from ..utils.logging import get_logger


@dataclass
class PromptTemplate:
    """Represents a reusable prompt template."""
    
    id: str
    name: str
    description: str
    template: str
    variables: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    version: str = "1.0"
    category: str = "general"
    tags: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert template to dictionary for serialization."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'template': self.template,
            'variables': self.variables,
            'metadata': self.metadata,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'version': self.version,
            'category': self.category,
            'tags': self.tags
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PromptTemplate':
        """Create template from dictionary."""
        return cls(
            id=data['id'],
            name=data['name'],
            description=data['description'],
            template=data['template'],
            variables=data.get('variables', []),
            metadata=data.get('metadata', {}),
            created_at=datetime.fromisoformat(data.get('created_at', datetime.now().isoformat())),
            updated_at=datetime.fromisoformat(data.get('updated_at', datetime.now().isoformat())),
            version=data.get('version', '1.0'),
            category=data.get('category', 'general'),
            tags=data.get('tags', [])
        )


@dataclass
class ThinkingTemplate:
    """Template specifically for thinking/reasoning prompts."""
    
    thinking_style: str  # 'step_by_step', 'pros_cons', 'analytical', 'creative'
    thinking_depth: str  # 'shallow', 'medium', 'deep'
    show_reasoning: bool = True
    reasoning_format: str = 'structured'  # 'structured', 'natural', 'bullet_points'
    confidence_scoring: bool = False
    
    def to_thinking_prompt(self) -> str:
        """Generate thinking mode prompt based on configuration."""
        prompts = {
            'step_by_step': {
                'shallow': "Think through this step by step:",
                'medium': "Let's approach this systematically. Think through each step carefully:",
                'deep': "Take a deep, methodical approach. Break this down into clear logical steps and analyze each one thoroughly:"
            },
            'pros_cons': {
                'shallow': "Consider the pros and cons:",
                'medium': "Analyze the advantages and disadvantages of different approaches:",
                'deep': "Conduct a comprehensive analysis weighing all pros and cons, considering short-term and long-term implications:"
            },
            'analytical': {
                'shallow': "Analyze this systematically:",
                'medium': "Provide a structured analysis considering key factors:",
                'deep': "Perform a comprehensive analytical breakdown, examining all relevant dimensions and their interconnections:"
            },
            'creative': {
                'shallow': "Think creatively about this:",
                'medium': "Explore creative approaches and alternative perspectives:",
                'deep': "Engage in deep creative thinking, exploring unconventional ideas and innovative solutions:"
            }
        }
        
        base_prompt = prompts.get(self.thinking_style, prompts['analytical'])[self.thinking_depth]
        
        if self.show_reasoning:
            if self.reasoning_format == 'structured':
                base_prompt += "\n\nStructure your reasoning as follows:\n1. Initial assessment\n2. Key considerations\n3. Analysis\n4. Conclusion"
            elif self.reasoning_format == 'bullet_points':
                base_prompt += "\n\nOrganize your thoughts using clear bullet points for each major point."
            
        if self.confidence_scoring:
            base_prompt += "\n\nInclude confidence scores (0-100%) for key conclusions."
            
        return base_prompt


class TemplateManager:
    """Manages prompt templates and provides template operations."""
    
    def __init__(self, template_store_path: Optional[str] = None):
        self.logger = get_logger(self.__class__.__name__.lower())
        self.templates: Dict[str, PromptTemplate] = {}
        self.thinking_templates: Dict[str, ThinkingTemplate] = {}
        self.template_store_path = template_store_path
        
        # Load built-in templates
        self._load_builtin_templates()
        
        # Load custom templates if store path provided
        if template_store_path:
            self._load_custom_templates(template_store_path)
    
    def _load_builtin_templates(self):
        """Load built-in templates."""
        # System prompt templates
        self.add_template(PromptTemplate(
            id="system_default",
            name="Default System Prompt",
            description="Standard system prompt for general conversation",
            template="You are a helpful, harmless, and honest AI assistant. Respond clearly and concisely.",
            category="system"
        ))
        
        self.add_template(PromptTemplate(
            id="system_coding",
            name="Coding Assistant",
            description="System prompt for coding assistance",
            template="""You are an expert programming assistant. Help with:
- Writing clean, efficient code
- Debugging and troubleshooting
- Explaining programming concepts
- Code review and best practices

Always provide working code examples and explain your reasoning.""",
            category="system",
            tags=["coding", "programming"]
        ))
        
        self.add_template(PromptTemplate(
            id="system_analysis",
            name="Analytical Assistant",
            description="System prompt for analytical tasks",
            template="""You are an analytical AI assistant specialized in:
- Breaking down complex problems
- Providing structured analysis
- Data interpretation
- Research assistance

Always structure your responses logically and provide evidence for your conclusions.""",
            category="system",
            tags=["analysis", "research"]
        ))
        
        # Task-specific templates
        self.add_template(PromptTemplate(
            id="summarize_conversation",
            name="Conversation Summary",
            description="Template for summarizing conversation history",
            template="""Please provide a concise summary of our conversation so far, including:
- Main topics discussed: {topics}
- Key decisions or conclusions: {decisions}
- Outstanding questions or next steps: {next_steps}

Keep the summary under {max_length} words.""",
            variables=["topics", "decisions", "next_steps", "max_length"],
            category="utility",
            tags=["summary", "conversation"]
        ))
        
        self.add_template(PromptTemplate(
            id="code_review",
            name="Code Review",
            description="Template for code review requests",
            template="""Please review the following {language} code:

```{language}
{code}
```

Focus on:
- Code quality and readability
- Potential bugs or issues
- Performance considerations
- Best practices
- Security concerns (if applicable)

Provide specific, actionable feedback.""",
            variables=["language", "code"],
            category="coding",
            tags=["code-review", "programming"]
        ))
        
        # Thinking mode templates
        self.add_thinking_template("step_by_step_deep", ThinkingTemplate(
            thinking_style="step_by_step",
            thinking_depth="deep",
            show_reasoning=True,
            reasoning_format="structured",
            confidence_scoring=True
        ))
        
        self.add_thinking_template("creative_exploration", ThinkingTemplate(
            thinking_style="creative",
            thinking_depth="medium",
            show_reasoning=True,
            reasoning_format="natural"
        ))
        
        self.add_thinking_template("analytical_brief", ThinkingTemplate(
            thinking_style="analytical",
            thinking_depth="shallow",
            show_reasoning=True,
            reasoning_format="bullet_points"
        ))
    
    def _load_custom_templates(self, store_path: str):
        """Load custom templates from file system."""
        store_path = Path(store_path)
        if store_path.exists() and store_path.is_file():
            try:
                with open(store_path, 'r') as f:
                    data = json.load(f)
                    
                for template_data in data.get('templates', []):
                    template = PromptTemplate.from_dict(template_data)
                    self.templates[template.id] = template
                    
                self.logger.info(f"Loaded {len(data.get('templates', []))} custom templates")
            except Exception as e:
                self.logger.error(f"Failed to load custom templates: {e}")
    
    def add_template(self, template: PromptTemplate) -> None:
        """Add a new template."""
        template.updated_at = datetime.now()
        self.templates[template.id] = template
        self.logger.debug(f"Added template: {template.name}")
    
    def add_thinking_template(self, name: str, template: ThinkingTemplate) -> None:
        """Add a thinking mode template."""
        self.thinking_templates[name] = template
        self.logger.debug(f"Added thinking template: {name}")
    
    def get_template(self, template_id: str) -> Optional[PromptTemplate]:
        """Get template by ID."""
        return self.templates.get(template_id)
    
    def get_thinking_template(self, name: str) -> Optional[ThinkingTemplate]:
        """Get thinking template by name."""
        return self.thinking_templates.get(name)
    
    def get_templates_by_category(self, category: str) -> List[PromptTemplate]:
        """Get all templates in a category."""
        return [t for t in self.templates.values() if t.category == category]
    
    def get_templates_by_tag(self, tag: str) -> List[PromptTemplate]:
        """Get all templates with a specific tag."""
        return [t for t in self.templates.values() if tag in t.tags]
    
    def search_templates(self, query: str) -> List[PromptTemplate]:
        """Search templates by name, description, or content."""
        query_lower = query.lower()
        results = []
        
        for template in self.templates.values():
            if (query_lower in template.name.lower() or 
                query_lower in template.description.lower() or
                query_lower in template.template.lower()):
                results.append(template)
        
        return results
    
    def update_template(self, template_id: str, **updates) -> bool:
        """Update an existing template."""
        if template_id not in self.templates:
            return False
        
        template = self.templates[template_id]
        for key, value in updates.items():
            if hasattr(template, key):
                setattr(template, key, value)
        
        template.updated_at = datetime.now()
        self.logger.debug(f"Updated template: {template.name}")
        return True
    
    def delete_template(self, template_id: str) -> bool:
        """Delete a template."""
        if template_id in self.templates:
            template_name = self.templates[template_id].name
            del self.templates[template_id]
            self.logger.debug(f"Deleted template: {template_name}")
            return True
        return False
    
    def export_templates(self, file_path: str, template_ids: Optional[List[str]] = None) -> bool:
        """Export templates to file."""
        try:
            templates_to_export = []
            
            if template_ids:
                templates_to_export = [
                    self.templates[tid].to_dict() 
                    for tid in template_ids 
                    if tid in self.templates
                ]
            else:
                templates_to_export = [t.to_dict() for t in self.templates.values()]
            
            export_data = {
                'templates': templates_to_export,
                'exported_at': datetime.now().isoformat(),
                'version': '1.0'
            }
            
            with open(file_path, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            self.logger.info(f"Exported {len(templates_to_export)} templates to {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to export templates: {e}")
            return False
    
    def import_templates(self, file_path: str, overwrite: bool = False) -> int:
        """Import templates from file."""
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            imported_count = 0
            for template_data in data.get('templates', []):
                template = PromptTemplate.from_dict(template_data)
                
                if template.id not in self.templates or overwrite:
                    self.templates[template.id] = template
                    imported_count += 1
            
            self.logger.info(f"Imported {imported_count} templates from {file_path}")
            return imported_count
            
        except Exception as e:
            self.logger.error(f"Failed to import templates: {e}")
            return 0
    
    def list_templates(self) -> List[Dict[str, Any]]:
        """List all templates with basic info."""
        return [
            {
                'id': template.id,
                'name': template.name,
                'description': template.description,
                'category': template.category,
                'tags': template.tags,
                'variables': template.variables,
                'updated_at': template.updated_at.isoformat()
            }
            for template in self.templates.values()
        ]
    
    def list_thinking_templates(self) -> List[Dict[str, Any]]:
        """List all thinking mode templates."""
        return [
            {
                'name': name,
                'thinking_style': template.thinking_style,
                'thinking_depth': template.thinking_depth,
                'show_reasoning': template.show_reasoning,
                'reasoning_format': template.reasoning_format,
                'confidence_scoring': template.confidence_scoring
            }
            for name, template in self.thinking_templates.items()
        ]
    
    def get_template_info(self, template_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a template."""
        template = self.get_template(template_id)
        if template:
            return template.to_dict()
        return None