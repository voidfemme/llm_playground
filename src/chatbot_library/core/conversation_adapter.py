"""
Conversation adapter for hot-swapping models with different capabilities.

This module handles intelligent conversation transformation to make any conversation
compatible with any model, regardless of whether the model supports images, tools, etc.
"""

from typing import List, Dict, Any, Optional
from ..models.conversation import Message, Response, Attachment, ToolUse, ToolResult
from ..adapters.chatbot_adapter import ChatbotCapabilities


class ConversationAdapter:
    """
    Adapts conversations for models with different capabilities.
    
    This allows hot-swapping models in conversations, even when:
    - Model A supports images but Model B doesn't
    - Model A supports tools but Model B doesn't
    - Models have different context length limits
    """
    
    def __init__(self):
        self.image_description_cache = {}  # Cache image descriptions
        self.tool_summary_cache = {}  # Cache tool interaction summaries
    
    def adapt_conversation_for_model(
        self,
        messages: List[Message],
        target_capabilities: ChatbotCapabilities,
        context_limit: Optional[int] = None,
        branch_name: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Adapt a conversation for a model with specific capabilities.
        
        Args:
            messages: List of conversation messages
            target_capabilities: Capabilities of the target model
            context_limit: Maximum context length for the model
            branch_name: Specific response branch to follow
            
        Returns:
            List of adapted messages ready for the target model
        """
        adapted_messages = []
        
        for message in messages:
            # Get the appropriate response for this message
            response = message.get_response(branch_name) if message.responses else None
            
            # Adapt user message
            adapted_user_msg = self._adapt_user_message(message, target_capabilities)
            if adapted_user_msg:
                adapted_messages.append(adapted_user_msg)
            
            # Adapt assistant response if it exists
            if response:
                adapted_response = self._adapt_assistant_response(response, target_capabilities)
                if adapted_response:
                    adapted_messages.append(adapted_response)
        
        # Apply context limit if specified
        if context_limit:
            adapted_messages = self._apply_context_limit(adapted_messages, context_limit)
        
        return adapted_messages
    
    def _adapt_user_message(
        self, 
        message: Message, 
        capabilities: ChatbotCapabilities
    ) -> Optional[Dict[str, Any]]:
        """Adapt a user message based on model capabilities."""
        
        content_parts = []
        
        # Add text content
        if message.text:
            content_parts.append(message.text)
        
        # Handle images
        if message.attachments:
            for attachment in message.attachments:
                if attachment.media_type.startswith("image/"):
                    if capabilities.image_understanding:
                        # Model supports images - include them
                        # This would be handled by the specific adapter
                        content_parts.append(f"[Image: {attachment.id}]")
                    else:
                        # Model doesn't support images - describe them
                        description = self._get_image_description(attachment)
                        if description:
                            content_parts.append(f"[Image Description: {description}]")
                        else:
                            content_parts.append(f"[Image attached: {attachment.id} ({attachment.media_type})]")
                else:
                    # Non-image attachment
                    content_parts.append(f"[Attachment: {attachment.id} ({attachment.media_type})]")
        
        # Handle tool results in user message
        if message.tool_result:
            tool_summary = self._summarize_tool_result(message.tool_result)
            content_parts.append(f"[Tool Result: {tool_summary}]")
        
        final_content = "\\n\\n".join(content_parts)
        
        return {
            "role": "user",
            "content": final_content,
            "timestamp": message.timestamp.isoformat(),
            "message_id": message.id,
            "original_attachments": len(message.attachments) if message.attachments else 0
        }
    
    def _adapt_assistant_response(
        self, 
        response: Response, 
        capabilities: ChatbotCapabilities
    ) -> Optional[Dict[str, Any]]:
        """Adapt an assistant response based on model capabilities."""
        
        content_parts = []
        
        # Add main response text
        if response.text:
            content_parts.append(response.text)
        
        # Handle tool usage
        if response.tool_use:
            if capabilities.function_calling:
                # Model supports tools - this would be handled by the adapter
                # For now, just note that tools were used
                content_parts.append(f"[Using tool: {response.tool_use.tool_name}]")
            else:
                # Model doesn't support tools - explain what would have been done
                tool_explanation = self._explain_tool_usage(response.tool_use)
                content_parts.append(f"[Tool Action: {tool_explanation}]")
        
        # Handle response attachments (rare, but possible)
        if response.attachments:
            for attachment in response.attachments:
                if attachment.media_type.startswith("image/"):
                    if not capabilities.image_understanding:
                        description = self._get_image_description(attachment)
                        content_parts.append(f"[Generated Image: {description or attachment.id}]")
                    # If model supports images, let the adapter handle it
                else:
                    content_parts.append(f"[Generated File: {attachment.id}]")
        
        final_content = "\\n\\n".join(content_parts)
        
        return {
            "role": "assistant", 
            "content": final_content,
            "timestamp": response.timestamp.isoformat(),
            "response_id": response.id,
            "model": response.model,
            "branch_name": response.branch_name,
            "original_tool_use": response.tool_use is not None
        }
    
    def _get_image_description(self, attachment: Attachment) -> Optional[str]:
        """
        Get or generate a description for an image attachment.
        
        In a full implementation, this could:
        1. Check cache for existing description
        2. Use a vision model to generate description
        3. Use image metadata if available
        4. Return a generic description
        """
        # Check cache first
        cache_key = f"{attachment.id}_{attachment.media_type}"
        if cache_key in self.image_description_cache:
            return self.image_description_cache[cache_key]
        
        # Try to get description from metadata
        if hasattr(attachment, 'metadata') and attachment.metadata:
            if 'description' in attachment.metadata:
                desc = attachment.metadata['description']
                self.image_description_cache[cache_key] = desc
                return desc
        
        # Generate basic description from file info
        file_info = f"an image file ({attachment.media_type})"
        if hasattr(attachment, 'file_path') and attachment.file_path:
            file_name = attachment.file_path.split('/')[-1]
            file_info = f"image file '{file_name}' ({attachment.media_type})"
        
        self.image_description_cache[cache_key] = file_info
        return file_info
    
    def _summarize_tool_result(self, tool_result: ToolResult) -> str:
        """Summarize a tool result for models that don't support tools."""
        # Check cache
        cache_key = tool_result.tool_use_id
        if cache_key in self.tool_summary_cache:
            return self.tool_summary_cache[cache_key]
        
        # Create summary
        result_preview = tool_result.tool_result[:100] + "..." if len(tool_result.tool_result) > 100 else tool_result.tool_result
        summary = f"Tool executed and returned: {result_preview}"
        
        self.tool_summary_cache[cache_key] = summary
        return summary
    
    def _explain_tool_usage(self, tool_use: ToolUse) -> str:
        """Explain what a tool would do for models that don't support tools."""
        explanations = {
            "search": f"I would search for: {tool_use.tool_input.get('query', 'information')}",
            "calculator": f"I would calculate: {tool_use.tool_input.get('expression', 'a mathematical expression')}",
            "file_read": f"I would read the file: {tool_use.tool_input.get('path', 'specified file')}",
            "web_search": f"I would search the web for: {tool_use.tool_input.get('query', 'information')}",
            "code_execution": f"I would execute code: {str(tool_use.tool_input.get('code', 'specified code'))[:50]}...",
            "image_generation": f"I would generate an image: {tool_use.tool_input.get('prompt', 'based on description')}",
        }
        
        tool_name = tool_use.tool_name.lower()
        for key, explanation in explanations.items():
            if key in tool_name:
                return explanation
        
        # Generic explanation
        return f"I would use the {tool_use.tool_name} tool with parameters: {str(tool_use.tool_input)[:100]}"
    
    def _apply_context_limit(
        self, 
        messages: List[Dict[str, Any]], 
        context_limit: int
    ) -> List[Dict[str, Any]]:
        """
        Apply context length limits by removing older messages if needed.
        
        This is a simple implementation that removes oldest messages.
        A more sophisticated version could:
        - Estimate token counts
        - Preserve important messages (system, recent)
        - Summarize removed context
        """
        if len(messages) <= context_limit:
            return messages
        
        # Keep the most recent messages
        truncated = messages[-context_limit:]
        
        # Add a note about truncation
        if truncated and truncated[0]["role"] == "user":
            original_content = truncated[0]["content"]
            truncated[0]["content"] = f"[Previous context truncated]\\n\\n{original_content}"
        
        return truncated
    
    def create_model_compatibility_summary(
        self, 
        messages: List[Message],
        target_capabilities: ChatbotCapabilities
    ) -> Dict[str, Any]:
        """
        Create a summary of what adaptations would be needed for a model.
        """
        summary = {
            "total_messages": len(messages),
            "adaptations_needed": [],
            "features_used": {
                "images": 0,
                "tools": 0,
                "attachments": 0
            },
            "compatibility_score": 1.0  # 1.0 = fully compatible, 0.0 = needs major adaptation
        }
        
        compatibility_issues = 0
        total_features = 0
        
        for message in messages:
            # Check for images
            if message.attachments:
                for attachment in message.attachments:
                    if attachment.media_type.startswith("image/"):
                        summary["features_used"]["images"] += 1
                        total_features += 1
                        if not target_capabilities.image_understanding:
                            compatibility_issues += 1
                            if "images" not in [item["type"] for item in summary["adaptations_needed"]]:
                                summary["adaptations_needed"].append({
                                    "type": "images",
                                    "description": "Images will be converted to text descriptions"
                                })
                    else:
                        summary["features_used"]["attachments"] += 1
            
            # Check tool results in messages
            if message.tool_result:
                summary["features_used"]["tools"] += 1
                total_features += 1
                if not target_capabilities.function_calling:
                    compatibility_issues += 1
                    if "tools" not in [item["type"] for item in summary["adaptations_needed"]]:
                        summary["adaptations_needed"].append({
                            "type": "tools", 
                            "description": "Tool results will be summarized as text"
                        })
            
            # Check tool usage in responses
            for response in message.responses:
                if response.tool_use:
                    summary["features_used"]["tools"] += 1
                    total_features += 1
                    if not target_capabilities.function_calling:
                        compatibility_issues += 1
                        if "tool_calls" not in [item["type"] for item in summary["adaptations_needed"]]:
                            summary["adaptations_needed"].append({
                                "type": "tool_calls",
                                "description": "Tool calls will be explained as intended actions"
                            })
        
        # Calculate compatibility score
        if total_features > 0:
            summary["compatibility_score"] = 1.0 - (compatibility_issues / total_features)
        
        return summary
    
    def suggest_alternative_models(
        self, 
        conversation_features: Dict[str, int],
        available_models: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Suggest models that are best suited for a conversation's features.
        
        Args:
            conversation_features: Features used in conversation (from compatibility summary)
            available_models: List of available models with their capabilities
            
        Returns:
            Sorted list of models with compatibility scores
        """
        model_scores = []
        
        for model in available_models:
            score = 0
            max_score = 0
            
            # Score based on image support
            if conversation_features.get("images", 0) > 0:
                max_score += 10
                if model.get("capabilities", {}).get("image_understanding", False):
                    score += 10
                else:
                    score += 3  # Can still handle with descriptions
            
            # Score based on tool support  
            if conversation_features.get("tools", 0) > 0:
                max_score += 10
                if model.get("capabilities", {}).get("function_calling", False):
                    score += 10
                else:
                    score += 5  # Can still handle with explanations
            
            # Base compatibility score
            max_score += 5
            score += 5
            
            final_score = score / max_score if max_score > 0 else 1.0
            
            model_scores.append({
                **model,
                "compatibility_score": final_score,
                "recommended": final_score > 0.8
            })
        
        # Sort by compatibility score (highest first)
        return sorted(model_scores, key=lambda x: x["compatibility_score"], reverse=True)