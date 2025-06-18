"""
Enhanced conversation manager with prompt template and thinking mode integration.
"""

import os
from typing import Dict, List, Any, Optional, Union
from pathlib import Path

from .conversation_manager import ConversationManager
from ..prompts import TemplateManager, TemplateEngine, PromptBuilder, ThinkingMode, TemplateStore
from ..prompts.prompt_builder import PromptConfiguration, BuiltPrompt
from ..prompts.template_engine import TemplateContext
from ..models.conversation import Message, Response, Conversation
from ..utils.logging import get_logger


class PromptConversationManager(ConversationManager):
    """Enhanced conversation manager with prompt template and thinking mode support."""
    
    def __init__(self, data_dir: str, template_store_path: Optional[str] = None):
        super().__init__(data_dir)
        self.logger = get_logger(self.__class__.__name__.lower())
        
        # Initialize prompt management components
        self._setup_prompt_system(template_store_path)
    
    def _setup_prompt_system(self, template_store_path: Optional[str] = None):
        """Initialize the prompt management system."""
        # Set up template store path
        if template_store_path is None:
            template_store_path = os.path.join(self.data_dir, "templates")
        
        # Initialize components
        self.template_store = TemplateStore(template_store_path)
        self.template_manager = TemplateManager(template_store_path)
        self.template_engine = TemplateEngine()
        self.prompt_builder = PromptBuilder(self.template_manager, self.template_engine)
        
        # Sync templates from store to manager
        self.template_store.sync_to_template_manager(self.template_manager)
        
        self.logger.info("Prompt management system initialized")
    
    def create_conversation_with_prompt(
        self,
        title: str,
        system_template_id: Optional[str] = None,
        thinking_mode: Union[str, ThinkingMode] = ThinkingMode.NONE,
        prompt_variables: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create a new conversation with prompt template configuration."""
        conversation_id = self.create_conversation(title)
        conversation = self.get_conversation(conversation_id)
        
        # Store prompt configuration in conversation metadata
        if not conversation.metadata:
            conversation.metadata = {}
        
        conversation.metadata.update({
            'prompt_config': {
                'system_template_id': system_template_id,
                'thinking_mode': thinking_mode.value if isinstance(thinking_mode, ThinkingMode) else thinking_mode,
                'prompt_variables': prompt_variables or {}
            }
        })
        
        self.save_conversation(conversation)
        self.logger.debug(f"Created conversation with prompt config: {conversation_id}")
        return conversation_id
    
    def add_message_with_thinking(
        self,
        conversation_id: str,
        user_id: str,
        text: str,
        thinking_mode: Union[str, ThinkingMode] = None,
        prompt_template_id: Optional[str] = None,
        prompt_variables: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Message:
        """Add a message with thinking mode and prompt template support."""
        conversation = self.get_conversation(conversation_id)
        if not conversation:
            raise ValueError(f"Conversation {conversation_id} not found")
        
        # Create the message with prompt information
        message = conversation.add_message(
            user_id=user_id,
            text=text,
            prompt_template_id=prompt_template_id,
            thinking_mode=thinking_mode.value if isinstance(thinking_mode, ThinkingMode) else thinking_mode,
            prompt_context=prompt_variables,
            **kwargs
        )
        
        # Save the conversation
        self.save_conversation(conversation)
        
        self.logger.debug(f"Added message with thinking mode: {thinking_mode}")
        return message
    
    def generate_response_with_thinking(
        self,
        conversation_id: str,
        message_id: str,
        model: str,
        thinking_mode: Union[str, ThinkingMode] = None,
        system_template_id: Optional[str] = None,
        thinking_template_name: Optional[str] = None,
        prompt_variables: Optional[Dict[str, Any]] = None,
        branch_name: Optional[str] = None,
        **adapter_kwargs
    ) -> Response:
        """Generate a response using prompt templates and thinking mode."""
        conversation = self.get_conversation(conversation_id)
        if not conversation:
            raise ValueError(f"Conversation {conversation_id} not found")
        
        message = conversation.get_message(message_id)
        if not message:
            raise ValueError(f"Message {message_id} not found")
        
        # Build prompt configuration
        config = self._build_prompt_config(
            conversation, message, thinking_mode, system_template_id, 
            thinking_template_name, prompt_variables
        )
        
        # Build the prompt
        built_prompt = self._build_prompt_for_message(conversation, message, config)
        
        # Get the model adapter
        adapter = self.get_model_adapter(model)
        if not adapter:
            raise ValueError(f"Model {model} not registered")
        
        # Prepare messages for the adapter with the built prompt
        api_messages = self._prepare_messages_with_prompt(conversation, message, built_prompt)
        
        # Generate the response
        response = adapter.send_message_without_tools(api_messages, **adapter_kwargs)
        
        # Enhance response with prompt information
        response.system_prompt = built_prompt.system_message
        response.thinking_instructions = built_prompt.thinking_instructions
        response.prompt_template_ids = built_prompt.template_ids
        response.branch_name = branch_name
        
        # Extract thinking trace if model supports it (e.g., Claude with thinking tags)
        response.thinking_trace = self._extract_thinking_trace(response.text)
        
        # Add response to message
        message.responses.append(response)
        
        # Save conversation
        self.save_conversation(conversation)
        
        self.logger.info(f"Generated response with thinking mode: {config.thinking_mode}")
        return response
    
    def _build_prompt_config(
        self,
        conversation: Conversation,
        message: Message,
        thinking_mode: Union[str, ThinkingMode, None],
        system_template_id: Optional[str],
        thinking_template_name: Optional[str],
        prompt_variables: Optional[Dict[str, Any]]
    ) -> PromptConfiguration:
        """Build prompt configuration from parameters and conversation context."""
        # Start with conversation-level config
        conversation_config = conversation.metadata.get('prompt_config', {})
        
        # Override with message-level and method parameters
        config = PromptConfiguration(
            system_template_id=system_template_id or conversation_config.get('system_template_id'),
            thinking_mode=thinking_mode or ThinkingMode(conversation_config.get('thinking_mode', 'none')),
            thinking_template_name=thinking_template_name or conversation_config.get('thinking_template_name'),
            variables={
                **conversation_config.get('prompt_variables', {}),
                **(prompt_variables or {}),
                **(message.prompt_context or {})
            },
            include_conversation_summary=True,
            include_user_context=True
        )
        
        return config
    
    def _build_prompt_for_message(
        self,
        conversation: Conversation,
        message: Message,
        config: PromptConfiguration
    ) -> BuiltPrompt:
        """Build the complete prompt for a message."""
        # Build conversation context
        conversation_context = self._build_conversation_context(conversation)
        
        # Build user context
        user_context = self._build_user_context(message)
        
        # Build the prompt
        built_prompt = self.prompt_builder.build_prompt(
            user_message=message.text,
            config=config,
            conversation_context=conversation_context,
            user_context=user_context
        )
        
        return built_prompt
    
    def _build_conversation_context(self, conversation: Conversation) -> Dict[str, Any]:
        """Build context information about the conversation."""
        context = {
            'conversation_id': conversation.id,
            'title': conversation.title,
            'message_count': len(conversation.messages),
            'created_at': conversation.created_at.isoformat(),
            'last_response_time': None
        }
        
        # Add information about recent messages
        if conversation.messages:
            last_message = conversation.messages[-1]
            context['last_response_time'] = last_message.timestamp.isoformat()
            
            if last_message.responses:
                context['last_model'] = last_message.responses[-1].model
        
        # Extract topics and themes (simple keyword extraction)
        all_text = []
        for msg in conversation.messages[-5:]:  # Last 5 messages
            all_text.append(msg.text)
            for response in msg.responses:
                all_text.append(response.text)
        
        if all_text:
            context['recent_content'] = ' '.join(all_text)
            context['topics'] = self._extract_topics(' '.join(all_text))
        
        return context
    
    def _build_user_context(self, message: Message) -> Dict[str, Any]:
        """Build context information about the user and message."""
        context = {
            'user_id': message.user_id,
            'message_timestamp': message.timestamp.isoformat(),
            'has_attachments': len(message.attachments) > 0,
            'attachment_types': [att.content_type for att in message.attachments]
        }
        
        # Add message-specific context
        if message.prompt_context:
            context.update(message.prompt_context)
        
        return context
    
    def _extract_topics(self, text: str) -> List[str]:
        """Simple topic extraction from text."""
        # This is a simple implementation - could be enhanced with NLP
        import re
        
        # Find capitalized words that might be topics
        words = re.findall(r'\b[A-Z][a-z]+\b', text)
        
        # Filter common words and get unique topics
        common_words = {'The', 'This', 'That', 'When', 'Where', 'What', 'How', 'Why', 'I', 'You', 'We', 'They'}
        topics = list(set(word for word in words if word not in common_words))
        
        return topics[:10]  # Return top 10 topics
    
    def _prepare_messages_with_prompt(
        self,
        conversation: Conversation,
        current_message: Message,
        built_prompt: BuiltPrompt
    ) -> List[Dict[str, Any]]:
        """Prepare messages for the adapter with the built prompt."""
        # Start with system message from prompt
        messages = []
        if built_prompt.system_message:
            messages.append({
                'role': 'system',
                'content': built_prompt.system_message
            })
        
        # Add conversation history (excluding current message)
        for msg in conversation.messages:
            if msg.id == current_message.id:
                break
                
            # Add user message
            messages.append({
                'role': 'user',
                'content': msg.text
            })
            
            # Add assistant responses
            for response in msg.responses:
                if not response.is_error:
                    messages.append({
                        'role': 'assistant',
                        'content': response.text
                    })
        
        # Add current message (with potential thinking instructions)
        messages.append({
            'role': 'user',
            'content': built_prompt.user_message
        })
        
        return messages
    
    def _extract_thinking_trace(self, response_text: str) -> Optional[str]:
        """Extract thinking trace from response if present."""
        # Look for thinking tags (e.g., Claude's <thinking> tags)
        import re
        
        thinking_match = re.search(r'<thinking>(.*?)</thinking>', response_text, re.DOTALL)
        if thinking_match:
            return thinking_match.group(1).strip()
        
        # Look for other thinking patterns
        reasoning_patterns = [
            r'Let me think about this step by step:(.*?)(?:\n\n|\Z)',
            r'My reasoning:(.*?)(?:\n\n|\Z)',
            r'Analysis:(.*?)(?:\n\n|\Z)'
        ]
        
        for pattern in reasoning_patterns:
            match = re.search(pattern, response_text, re.DOTALL | re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return None
    
    def get_conversation_prompt_config(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """Get the prompt configuration for a conversation."""
        conversation = self.get_conversation(conversation_id)
        if conversation and conversation.metadata:
            return conversation.metadata.get('prompt_config')
        return None
    
    def update_conversation_prompt_config(
        self,
        conversation_id: str,
        system_template_id: Optional[str] = None,
        thinking_mode: Optional[str] = None,
        prompt_variables: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Update the prompt configuration for a conversation."""
        conversation = self.get_conversation(conversation_id)
        if not conversation:
            return False
        
        if not conversation.metadata:
            conversation.metadata = {}
        
        if 'prompt_config' not in conversation.metadata:
            conversation.metadata['prompt_config'] = {}
        
        config = conversation.metadata['prompt_config']
        
        if system_template_id is not None:
            config['system_template_id'] = system_template_id
        if thinking_mode is not None:
            config['thinking_mode'] = thinking_mode
        if prompt_variables is not None:
            config['prompt_variables'] = prompt_variables
        
        self.save_conversation(conversation)
        self.logger.debug(f"Updated prompt config for conversation: {conversation_id}")
        return True
    
    def get_available_templates(self) -> Dict[str, Any]:
        """Get information about available prompt templates."""
        return {
            'system_templates': self.template_manager.get_templates_by_category('system'),
            'thinking_templates': self.template_manager.list_thinking_templates(),
            'all_templates': self.template_manager.list_templates(),
            'thinking_modes': [mode.value for mode in ThinkingMode]
        }
    
    def create_custom_template(
        self,
        name: str,
        description: str,
        template: str,
        category: str = "custom",
        variables: Optional[List[str]] = None,
        tags: Optional[List[str]] = None
    ) -> str:
        """Create a custom prompt template."""
        from ..prompts.template_manager import PromptTemplate
        import uuid
        
        template_obj = PromptTemplate(
            id=str(uuid.uuid4()),
            name=name,
            description=description,
            template=template,
            category=category,
            variables=variables or [],
            tags=tags or []
        )
        
        self.template_manager.add_template(template_obj)
        self.template_store.save_template(template_obj)
        
        self.logger.info(f"Created custom template: {name}")
        return template_obj.id
    
    def test_template(
        self,
        template_id: str,
        variables: Optional[Dict[str, Any]] = None
    ) -> str:
        """Test a template with given variables."""
        template = self.template_manager.get_template(template_id)
        if not template:
            raise ValueError(f"Template {template_id} not found")
        
        context = TemplateContext(variables=variables or {})
        return self.template_engine.render_template(template, context)
    
    def backup_templates(self) -> str:
        """Create a backup of all templates."""
        backup_name = self.template_store.create_backup()
        self.logger.info(f"Created template backup: {backup_name}")
        return backup_name
    
    def get_thinking_trace(self, conversation_id: str, message_id: str, response_id: str) -> Optional[str]:
        """Get the thinking trace for a specific response."""
        conversation = self.get_conversation(conversation_id)
        if not conversation:
            return None
        
        message = conversation.get_message(message_id)
        if not message:
            return None
        
        for response in message.responses:
            if response.id == response_id:
                return response.thinking_trace
        
        return None
    
    def analyze_conversation_prompts(self, conversation_id: str) -> Dict[str, Any]:
        """Analyze prompt usage in a conversation."""
        conversation = self.get_conversation(conversation_id)
        if not conversation:
            return {}
        
        analysis = {
            'total_messages': len(conversation.messages),
            'thinking_modes_used': set(),
            'templates_used': set(),
            'messages_with_thinking': 0,
            'responses_with_traces': 0
        }
        
        for message in conversation.messages:
            if message.thinking_mode:
                analysis['thinking_modes_used'].add(message.thinking_mode)
                analysis['messages_with_thinking'] += 1
            
            if message.prompt_template_id:
                analysis['templates_used'].add(message.prompt_template_id)
            
            for response in message.responses:
                if response.thinking_trace:
                    analysis['responses_with_traces'] += 1
                
                analysis['templates_used'].update(response.prompt_template_ids)
        
        # Convert sets to lists for JSON serialization
        analysis['thinking_modes_used'] = list(analysis['thinking_modes_used'])
        analysis['templates_used'] = list(analysis['templates_used'])
        
        return analysis