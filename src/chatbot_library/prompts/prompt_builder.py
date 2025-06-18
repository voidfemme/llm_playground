"""
Dynamic prompt builder with thinking mode integration.
"""

from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field
from enum import Enum

from .template_manager import TemplateManager, PromptTemplate, ThinkingTemplate
from .template_engine import TemplateEngine, TemplateContext
from ..utils.logging import get_logger


class ThinkingMode(Enum):
    """Available thinking modes for model responses."""
    NONE = "none"
    STEP_BY_STEP = "step_by_step"
    PROS_CONS = "pros_cons"
    ANALYTICAL = "analytical"
    CREATIVE = "creative"
    CUSTOM = "custom"


@dataclass
class PromptConfiguration:
    """Configuration for prompt building."""
    system_template_id: Optional[str] = None
    thinking_mode: ThinkingMode = ThinkingMode.NONE
    thinking_template_name: Optional[str] = None
    include_conversation_summary: bool = False
    include_user_context: bool = True
    max_context_length: Optional[int] = None
    custom_instructions: Optional[str] = None
    variables: Dict[str, Any] = field(default_factory=dict)
    
    
@dataclass
class BuiltPrompt:
    """A fully constructed prompt ready for model consumption."""
    system_message: str
    user_message: str
    thinking_instructions: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    context_used: Dict[str, Any] = field(default_factory=dict)
    template_ids: List[str] = field(default_factory=list)


class PromptBuilder:
    """Builds dynamic prompts with thinking mode and context integration."""
    
    def __init__(self, template_manager: TemplateManager, template_engine: TemplateEngine):
        self.template_manager = template_manager
        self.template_engine = template_engine
        self.logger = get_logger(self.__class__.__name__.lower())
        
        # Default configurations for different modes
        self.default_configs = {
            ThinkingMode.STEP_BY_STEP: PromptConfiguration(
                thinking_mode=ThinkingMode.STEP_BY_STEP,
                thinking_template_name="step_by_step_deep"
            ),
            ThinkingMode.PROS_CONS: PromptConfiguration(
                thinking_mode=ThinkingMode.PROS_CONS,
                thinking_template_name="analytical_brief"
            ),
            ThinkingMode.ANALYTICAL: PromptConfiguration(
                thinking_mode=ThinkingMode.ANALYTICAL,
                thinking_template_name="analytical_brief"
            ),
            ThinkingMode.CREATIVE: PromptConfiguration(
                thinking_mode=ThinkingMode.CREATIVE,
                thinking_template_name="creative_exploration"
            )
        }
    
    def build_prompt(
        self,
        user_message: str,
        config: Optional[PromptConfiguration] = None,
        conversation_context: Optional[Dict[str, Any]] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> BuiltPrompt:
        """Build a complete prompt with system message, thinking mode, and context."""
        if config is None:
            config = PromptConfiguration()
        
        # Create template context
        context = self._build_template_context(
            config, conversation_context, user_context, user_message
        )
        
        # Build system message
        system_message = self._build_system_message(config, context)
        
        # Build thinking instructions if needed
        thinking_instructions = None
        if config.thinking_mode != ThinkingMode.NONE:
            thinking_instructions = self._build_thinking_instructions(config, context)
        
        # Process user message with context if needed
        processed_user_message = self._process_user_message(user_message, config, context)
        
        # Create the built prompt
        built_prompt = BuiltPrompt(
            system_message=system_message,
            user_message=processed_user_message,
            thinking_instructions=thinking_instructions,
            metadata={
                'thinking_mode': config.thinking_mode.value,
                'system_template_id': config.system_template_id,
                'thinking_template_name': config.thinking_template_name,
                'build_timestamp': context.get_variable('now', '')
            },
            context_used=context.to_dict(),
            template_ids=[tid for tid in [config.system_template_id] if tid]
        )
        
        self.logger.debug(f"Built prompt with thinking mode: {config.thinking_mode.value}")
        return built_prompt
    
    def _build_template_context(
        self,
        config: PromptConfiguration,
        conversation_context: Optional[Dict[str, Any]],
        user_context: Optional[Dict[str, Any]],
        user_message: str
    ) -> TemplateContext:
        """Build the template context for rendering."""
        context = TemplateContext(
            variables=config.variables.copy(),
            conversation_data=conversation_context,
            user_data=user_context
        )
        
        # Add standard variables
        context.add_variable('user_message', user_message)
        context.add_variable('thinking_mode', config.thinking_mode.value)
        
        # Add conversation summary if requested
        if config.include_conversation_summary and conversation_context:
            summary = self._generate_conversation_summary(conversation_context)
            context.add_variable('conversation_summary', summary)
        
        # Add user context variables
        if config.include_user_context and user_context:
            for key, value in user_context.items():
                context.add_variable(f'user_{key}', value)
        
        return context
    
    def _build_system_message(self, config: PromptConfiguration, context: TemplateContext) -> str:
        """Build the system message using templates and configuration."""
        # Get base system template
        system_template = None
        if config.system_template_id:
            system_template = self.template_manager.get_template(config.system_template_id)
        
        # Use default if no template specified
        if not system_template:
            system_template = self.template_manager.get_template("system_default")
        
        # Render the system message
        system_message = ""
        if system_template:
            system_message = self.template_engine.render_template(system_template, context)
        
        # Add custom instructions if provided
        if config.custom_instructions:
            if system_message:
                system_message += f"\n\n{config.custom_instructions}"
            else:
                system_message = config.custom_instructions
        
        return system_message
    
    def _build_thinking_instructions(self, config: PromptConfiguration, context: TemplateContext) -> str:
        """Build thinking mode instructions."""
        thinking_template = None
        
        # Get thinking template
        if config.thinking_template_name:
            thinking_template = self.template_manager.get_thinking_template(config.thinking_template_name)
        elif config.thinking_mode in self.default_configs:
            template_name = self.default_configs[config.thinking_mode].thinking_template_name
            thinking_template = self.template_manager.get_thinking_template(template_name)
        
        if thinking_template:
            return self.template_engine.render_thinking_prompt(thinking_template, "", context)
        
        # Fallback to simple thinking instruction
        return self._get_simple_thinking_instruction(config.thinking_mode)
    
    def _get_simple_thinking_instruction(self, thinking_mode: ThinkingMode) -> str:
        """Get simple thinking instruction for fallback."""
        instructions = {
            ThinkingMode.STEP_BY_STEP: "Think through this step by step before responding.",
            ThinkingMode.PROS_CONS: "Consider the pros and cons before responding.",
            ThinkingMode.ANALYTICAL: "Analyze this systematically before responding.",
            ThinkingMode.CREATIVE: "Think creatively about this before responding."
        }
        return instructions.get(thinking_mode, "Think carefully before responding.")
    
    def _process_user_message(
        self, 
        user_message: str, 
        config: PromptConfiguration, 
        context: TemplateContext
    ) -> str:
        """Process the user message with template rendering."""
        # Apply template rendering to user message
        processed_message = self.template_engine.render_template(user_message, context)
        
        return processed_message
    
    def _generate_conversation_summary(self, conversation_context: Dict[str, Any]) -> str:
        """Generate a summary of the conversation context."""
        # Simple summary generation - could be enhanced with AI summarization
        summary_parts = []
        
        if 'message_count' in conversation_context:
            summary_parts.append(f"Messages exchanged: {conversation_context['message_count']}")
        
        if 'topics' in conversation_context:
            topics = conversation_context['topics']
            if isinstance(topics, list) and topics:
                summary_parts.append(f"Main topics: {', '.join(topics[:3])}")
        
        if 'last_response_time' in conversation_context:
            summary_parts.append(f"Last interaction: {conversation_context['last_response_time']}")
        
        return "; ".join(summary_parts) if summary_parts else "New conversation"
    
    def create_config_for_task(self, task_type: str) -> PromptConfiguration:
        """Create a prompt configuration optimized for a specific task type."""
        task_configs = {
            'coding': PromptConfiguration(
                system_template_id="system_coding",
                thinking_mode=ThinkingMode.STEP_BY_STEP,
                include_user_context=True
            ),
            'analysis': PromptConfiguration(
                system_template_id="system_analysis",
                thinking_mode=ThinkingMode.ANALYTICAL,
                include_conversation_summary=True
            ),
            'creative': PromptConfiguration(
                thinking_mode=ThinkingMode.CREATIVE,
                include_user_context=True
            ),
            'problem_solving': PromptConfiguration(
                thinking_mode=ThinkingMode.STEP_BY_STEP,
                include_conversation_summary=True,
                custom_instructions="Focus on finding practical solutions."
            ),
            'decision_making': PromptConfiguration(
                thinking_mode=ThinkingMode.PROS_CONS,
                include_conversation_summary=True,
                custom_instructions="Weigh all options carefully before recommending."
            )
        }
        
        return task_configs.get(task_type, PromptConfiguration())
    
    def build_quick_prompt(
        self,
        user_message: str,
        thinking_mode: ThinkingMode = ThinkingMode.NONE,
        system_template_id: Optional[str] = None
    ) -> BuiltPrompt:
        """Quick prompt building with minimal configuration."""
        config = PromptConfiguration(
            system_template_id=system_template_id,
            thinking_mode=thinking_mode
        )
        return self.build_prompt(user_message, config)
    
    def build_thinking_prompt(
        self,
        user_message: str,
        thinking_style: str = "analytical",
        thinking_depth: str = "medium"
    ) -> BuiltPrompt:
        """Build a prompt specifically focused on thinking mode."""
        # Create custom thinking template
        thinking_template = ThinkingTemplate(
            thinking_style=thinking_style,
            thinking_depth=thinking_depth,
            show_reasoning=True,
            reasoning_format="structured"
        )
        
        # Add to template manager temporarily
        temp_name = f"temp_{thinking_style}_{thinking_depth}"
        self.template_manager.add_thinking_template(temp_name, thinking_template)
        
        config = PromptConfiguration(
            thinking_mode=ThinkingMode.CUSTOM,
            thinking_template_name=temp_name
        )
        
        return self.build_prompt(user_message, config)
    
    def validate_configuration(self, config: PromptConfiguration) -> List[str]:
        """Validate a prompt configuration and return any errors."""
        errors = []
        
        # Check if system template exists
        if config.system_template_id:
            template = self.template_manager.get_template(config.system_template_id)
            if not template:
                errors.append(f"System template not found: {config.system_template_id}")
        
        # Check if thinking template exists
        if config.thinking_template_name:
            thinking_template = self.template_manager.get_thinking_template(config.thinking_template_name)
            if not thinking_template:
                errors.append(f"Thinking template not found: {config.thinking_template_name}")
        
        # Validate thinking mode consistency
        if config.thinking_mode != ThinkingMode.NONE and not config.thinking_template_name:
            # Check if default template exists
            if config.thinking_mode in self.default_configs:
                default_template_name = self.default_configs[config.thinking_mode].thinking_template_name
                if not self.template_manager.get_thinking_template(default_template_name):
                    errors.append(f"Default thinking template missing for mode: {config.thinking_mode.value}")
        
        return errors
    
    def get_available_configurations(self) -> Dict[str, Any]:
        """Get information about available prompt configurations."""
        return {
            'system_templates': [
                {'id': t.id, 'name': t.name, 'category': t.category}
                for t in self.template_manager.templates.values()
                if t.category == 'system'
            ],
            'thinking_templates': list(self.template_manager.thinking_templates.keys()),
            'thinking_modes': [mode.value for mode in ThinkingMode],
            'task_configs': [
                'coding', 'analysis', 'creative', 'problem_solving', 'decision_making'
            ]
        }