"""
Modern conversation manager with model hot-swapping capabilities.

This manager provides comprehensive conversation management with support for
switching models mid-conversation, even when models have different capabilities.
"""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable

from .conversation_adapter import ConversationAdapter
from ..models.conversation import Conversation, Message, Response, conversation_to_dict, conversation_from_dict
from ..adapters.chatbot_adapter import ChatbotCapabilities
from ..utils.logging import get_logger, log_conversation_event, log_function_call


class ConversationManager:
    """
    Comprehensive conversation manager with hot-swapping capabilities.
    
    Features:
    - Create, load, save, and delete conversations
    - Switch models mid-conversation
    - Automatic conversation adaptation for model capabilities
    - Model compatibility analysis
    - Intelligent context management
    - Response regeneration and branching
    - Conversation persistence and retrieval
    """
    
    def __init__(self, data_dir: Path):
        """
        Initialize the conversation manager.
        
        Args:
            data_dir: Directory for storing conversation data
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.conversations: Dict[str, Conversation] = {}
        self.model_registry: Dict[str, Dict[str, Any]] = {}
        self.conversation_adapter = ConversationAdapter()
        self.logger = get_logger(self.__class__.__name__.lower())
        
        # Load existing conversations
        self._load_all_conversations()
    
    def register_model(
        self, 
        model_id: str, 
        api_function: Callable,
        capabilities: ChatbotCapabilities,
        **metadata
    ) -> None:
        """
        Register a model with its capabilities.
        
        Args:
            model_id: Unique identifier for the model
            api_function: Function to call for generating responses
            capabilities: Model capabilities (tools, images, etc.)
            **metadata: Additional model metadata
        """
        self.model_registry[model_id] = {
            'api_function': api_function,
            'capabilities': capabilities,
            'metadata': metadata,
            'registered_at': datetime.now()
        }
        
        log_conversation_event(
            self.logger,
            "model_registered",
            "",
            model_id=model_id,
            capabilities=capabilities.__dict__
        )
    
    def create_conversation(self, title: str, conversation_id: Optional[str] = None) -> str:
        """
        Create a new conversation.
        
        Args:
            title: Title for the conversation
            conversation_id: Optional specific ID to use
            
        Returns:
            The conversation ID
        """
        if conversation_id is None:
            conversation_id = str(uuid.uuid4())
        
        conversation = Conversation(
            id=conversation_id,
            title=title,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        self.conversations[conversation_id] = conversation
        self._save_conversation(conversation)
        
        log_conversation_event(
            self.logger,
            "conversation_created",
            conversation_id,
            title=title
        )
        
        return conversation_id
    
    def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """Get a conversation by ID."""
        return self.conversations.get(conversation_id)
    
    def save_conversation(self, conversation: Conversation) -> None:
        """Save a conversation to disk manually."""
        self._save_conversation(conversation)
    
    def list_conversations(self) -> List[Dict[str, Any]]:
        """
        List all conversations with basic metadata.
        
        Returns:
            List of conversation summaries
        """
        summaries = []
        for conv in self.conversations.values():
            summaries.append({
                'id': conv.id,
                'title': conv.title,
                'created_at': conv.created_at,
                'updated_at': conv.updated_at,
                'message_count': len(conv.messages),
                'branches': conv.get_all_branches()
            })
        
        return sorted(summaries, key=lambda x: x['updated_at'], reverse=True)
    
    def send_message_and_get_response(
        self,
        conversation_id: str,
        user_id: str,
        message_text: str,
        model_id: str,
        branch_name: Optional[str] = None,
        **kwargs
    ) -> Response:
        """
        Send a message and get a response using the specified model.
        
        Args:
            conversation_id: ID of the conversation
            user_id: ID of the user sending the message
            message_text: The message text
            model_id: Model to use for response generation
            branch_name: Optional branch name for the response
            **kwargs: Additional parameters for the model
            
        Returns:
            The generated response
        """
        log_function_call(
            self.logger,
            "send_message_and_get_response",
            conversation_id=conversation_id,
            model_id=model_id,
            branch_name=branch_name
        )
        
        conversation = self.get_conversation(conversation_id)
        if not conversation:
            raise ValueError(f"Conversation {conversation_id} not found")
        
        if model_id not in self.model_registry:
            raise ValueError(f"Model {model_id} not registered")
        
        # Add the user message
        message = conversation.add_message(user_id, message_text)
        
        # Generate response using the specified model
        response = self._generate_response(conversation, message, model_id, branch_name, **kwargs)
        
        # Save the updated conversation
        self._save_conversation(conversation)
        
        return response
    
    def add_response_with_hotswap(
        self,
        conversation_id: str,
        message_id: str,
        target_model: str,
        branch_name: Optional[str] = None,
        **kwargs
    ) -> Response:
        """
        Add a response to an existing message using a different model (hot-swap).
        
        This allows generating alternative responses or switching models mid-conversation.
        
        Args:
            conversation_id: ID of the conversation
            message_id: ID of the message to respond to
            target_model: Model to use for the new response
            branch_name: Optional branch name for the response
            **kwargs: Additional parameters for the model
            
        Returns:
            The generated response
        """
        conversation = self.get_conversation(conversation_id)
        if not conversation:
            raise ValueError(f"Conversation {conversation_id} not found")
        
        message = conversation.get_message(message_id)
        if not message:
            raise ValueError(f"Message {message_id} not found")
        
        if target_model not in self.model_registry:
            raise ValueError(f"Model {target_model} not registered")
        
        # Generate response with the target model
        response = self._generate_response(conversation, message, target_model, branch_name, **kwargs)
        
        # Save the updated conversation
        self._save_conversation(conversation)
        
        log_conversation_event(
            self.logger,
            "response_hotswapped",
            conversation_id,
            message_id=message_id,
            target_model=target_model,
            branch_name=branch_name
        )
        
        return response
    
    def regenerate_response(
        self,
        conversation_id: str,
        message_id: str,
        model_id: Optional[str] = None,
        branch_name: Optional[str] = None,
        **kwargs
    ) -> Response:
        """
        Regenerate a response for an existing message.
        
        Args:
            conversation_id: ID of the conversation
            message_id: ID of the message to regenerate response for
            model_id: Optional model to use (defaults to original model)
            branch_name: Optional branch name for the regenerated response
            **kwargs: Additional parameters for the model
            
        Returns:
            The regenerated response
        """
        conversation = self.get_conversation(conversation_id)
        if not conversation:
            raise ValueError(f"Conversation {conversation_id} not found")
        
        message = conversation.get_message(message_id)
        if not message:
            raise ValueError(f"Message {message_id} not found")
        
        # Use original model if none specified
        if model_id is None:
            if message.responses:
                model_id = message.responses[0].model
            else:
                raise ValueError("No existing response to determine model from")
        
        if model_id not in self.model_registry:
            raise ValueError(f"Model {model_id} not registered")
        
        # Generate new response
        response = self._generate_response(conversation, message, model_id, branch_name, **kwargs)
        
        # Save the updated conversation
        self._save_conversation(conversation)
        
        log_conversation_event(
            self.logger,
            "response_regenerated",
            conversation_id,
            message_id=message_id,
            model_id=model_id,
            branch_name=branch_name
        )
        
        return response
    
    def delete_conversation(self, conversation_id: str) -> bool:
        """
        Delete a conversation.
        
        Args:
            conversation_id: ID of the conversation to delete
            
        Returns:
            True if deleted, False if not found
        """
        if conversation_id not in self.conversations:
            return False
        
        # Remove from memory
        del self.conversations[conversation_id]
        
        # Remove file
        conversation_file = self.data_dir / f"{conversation_id}.json"
        if conversation_file.exists():
            conversation_file.unlink()
        
        log_conversation_event(
            self.logger,
            "conversation_deleted",
            conversation_id
        )
        
        return True
    
    def get_model_compatibility(
        self, 
        conversation_id: str, 
        target_model: str
    ) -> Dict[str, Any]:
        """
        Analyze compatibility between a conversation and target model.
        
        Args:
            conversation_id: ID of the conversation
            target_model: Model to check compatibility with
            
        Returns:
            Compatibility analysis
        """
        conversation = self.get_conversation(conversation_id)
        if not conversation:
            raise ValueError(f"Conversation {conversation_id} not found")
        
        if target_model not in self.model_registry:
            raise ValueError(f"Model {target_model} not registered")
        
        return self.conversation_adapter.analyze_compatibility(
            conversation, 
            self.model_registry[target_model]['capabilities']
        )
    
    def adapt_conversation_for_model(
        self, 
        conversation_id: str, 
        target_model: str
    ) -> List[Dict[str, str]]:
        """
        Adapt a conversation for a specific model's capabilities.
        
        Args:
            conversation_id: ID of the conversation
            target_model: Model to adapt for
            
        Returns:
            Adapted conversation context suitable for the model
        """
        conversation = self.get_conversation(conversation_id)
        if not conversation:
            raise ValueError(f"Conversation {conversation_id} not found")
        
        if target_model not in self.model_registry:
            raise ValueError(f"Model {target_model} not registered")
        
        return self.conversation_adapter.adapt_for_model(
            conversation,
            self.model_registry[target_model]['capabilities']
        )
    
    def _generate_response(
        self,
        conversation: Conversation,
        message: Message,
        model_id: str,
        branch_name: Optional[str] = None,
        **kwargs
    ) -> Response:
        """Generate a response using the specified model."""
        model_info = self.model_registry[model_id]
        api_function = model_info['api_function']
        
        # Get conversation context suitable for the model
        context = self.conversation_adapter.adapt_for_model(
            conversation,
            model_info['capabilities']
        )
        
        try:
            # Call the model's API function
            result = api_function(context, **kwargs)
            
            # Create response object
            response = message.add_response(
                model=model_id,
                text=result.get('text', str(result)),
                branch_name=branch_name,
                metadata=result if isinstance(result, dict) else {}
            )
            
            return response
            
        except Exception as e:
            # Create error response
            error_response = message.add_response(
                model=model_id,
                text=f"Error generating response: {str(e)}",
                branch_name=branch_name,
                is_error=True
            )
            
            log_conversation_event(
                self.logger,
                "response_generation_failed",
                conversation.id,
                message_id=message.id,
                model_id=model_id,
                error=str(e)
            )
            
            return error_response
    
    def _save_conversation(self, conversation: Conversation) -> None:
        """Save a conversation to disk."""
        conversation_file = self.data_dir / f"{conversation.id}.json"
        
        with open(conversation_file, 'w') as f:
            json.dump(conversation_to_dict(conversation), f, indent=2)
        
        conversation.updated_at = datetime.now()
    
    def _load_all_conversations(self) -> None:
        """Load all conversations from disk."""
        for conversation_file in self.data_dir.glob("*.json"):
            try:
                with open(conversation_file, 'r') as f:
                    data = json.load(f)
                
                conversation = conversation_from_dict(data)
                self.conversations[conversation.id] = conversation
                
            except Exception as e:
                log_conversation_event(
                    self.logger,
                    "conversation_load_failed",
                    conversation_file.stem,
                    error=str(e)
                )
    
    def get_conversation_stats(self) -> Dict[str, Any]:
        """Get statistics about all conversations."""
        stats = {
            'total_conversations': len(self.conversations),
            'total_messages': 0,
            'total_responses': 0,
            'models_used': set(),
            'branches_used': set(),
            'avg_messages_per_conversation': 0
        }
        
        for conv in self.conversations.values():
            stats['total_messages'] += len(conv.messages)
            
            for message in conv.messages:
                stats['total_responses'] += len(message.responses)
                
                for response in message.responses:
                    stats['models_used'].add(response.model)
                    if response.branch_name:
                        stats['branches_used'].add(response.branch_name)
        
        if stats['total_conversations'] > 0:
            stats['avg_messages_per_conversation'] = stats['total_messages'] / stats['total_conversations']
        
        stats['models_used'] = list(stats['models_used'])
        stats['branches_used'] = list(stats['branches_used'])
        
        return stats