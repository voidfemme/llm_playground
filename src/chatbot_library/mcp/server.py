"""
MCP Server implementation for the chatbot library.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable
from dataclasses import asdict

from .protocol import (
    MCPProtocol,
    MCPMessage,
    MCPResource,
    MCPTool,
    MCPPrompt,
    MCPServerCapabilities,
    MCPInitializeResult,
    MCPErrorCode,
    MCPMethod,
)
from ..core.chatbot_manager import ChatbotManager
from ..tools.compatibility import ToolManager
from ..models.conversation_dataclasses import Conversation


class MCPServer(MCPProtocol):
    """MCP Server for exposing chatbot library functionality."""
    
    def __init__(
        self,
        chatbot_manager: ChatbotManager,
        tool_manager: ToolManager,
        name: str = "chatbot-library-server",
        version: str = "1.0.0"
    ):
        super().__init__()
        self.chatbot_manager = chatbot_manager
        self.tool_manager = tool_manager
        self.name = name
        self.version = version
        self.logger = logging.getLogger(__name__)
        
        # Set up server capabilities
        self.capabilities = MCPServerCapabilities(
            tools={"listChanged": True},
            resources={"listChanged": True},
            prompts={"listChanged": True},
            logging={}
        )
        
        # Message handlers
        self.handlers: Dict[str, Callable] = {
            MCPMethod.INITIALIZE.value: self._handle_initialize,
            MCPMethod.PING.value: self._handle_ping,
            MCPMethod.LIST_TOOLS.value: self._handle_list_tools,
            MCPMethod.CALL_TOOL.value: self._handle_call_tool,
            MCPMethod.LIST_RESOURCES.value: self._handle_list_resources,
            MCPMethod.READ_RESOURCE.value: self._handle_read_resource,
            MCPMethod.LIST_PROMPTS.value: self._handle_list_prompts,
            MCPMethod.GET_PROMPT.value: self._handle_get_prompt,
        }
    
    async def handle_message(self, message_data: str) -> Optional[str]:
        """Handle incoming MCP message."""
        try:
            message = self.parse_message(message_data)
            
            if not message.method:
                # This is a response or notification, not a request
                return None
            
            handler = self.handlers.get(message.method)
            if not handler:
                error_response = self.create_error_response(
                    message.id or 0,
                    MCPErrorCode.METHOD_NOT_FOUND,
                    f"Method '{message.method}' not found"
                )
                return self.serialize_message(error_response)
            
            # Call handler
            result = await handler(message)
            
            if message.id is not None:
                # This is a request that expects a response
                response = MCPMessage(id=message.id, result=result)
                return self.serialize_message(response)
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error handling message: {e}")
            error_response = self.create_error_response(
                0,
                MCPErrorCode.INTERNAL_ERROR,
                str(e)
            )
            return self.serialize_message(error_response)
    
    async def _handle_initialize(self, message: MCPMessage) -> Dict[str, Any]:
        """Handle initialize request."""
        self.initialized = True
        
        result = MCPInitializeResult(
            protocolVersion="2024-11-05",
            capabilities=self.capabilities,
            serverInfo={
                "name": self.name,
                "version": self.version
            }
        )
        
        return asdict(result)
    
    async def _handle_ping(self, message: MCPMessage) -> Dict[str, Any]:
        """Handle ping request."""
        return {}
    
    async def _handle_list_tools(self, message: MCPMessage) -> Dict[str, Any]:
        """Handle list tools request."""
        tools = []
        
        # Get tools from tool manager
        for tool_name in self.tool_manager.get_tools_list():
            tool = self.tool_manager.get_tool(tool_name)
            if tool:
                mcp_tool = MCPTool(
                    name=tool.name,
                    description=tool.description,
                    inputSchema=tool.input_schema.serialize() if tool.input_schema else {}
                )
                tools.append(asdict(mcp_tool))
        
        return {"tools": tools}
    
    async def _handle_call_tool(self, message: MCPMessage) -> Dict[str, Any]:
        """Handle call tool request."""
        if not message.params:
            raise ValueError("Missing parameters for tool call")
        
        tool_name = message.params.get("name")
        arguments = message.params.get("arguments", {})
        
        if not tool_name:
            raise ValueError("Missing tool name")
        
        try:
            # Execute the tool
            result = self.tool_manager.execute_tool(tool_name, arguments)
            
            return {
                "content": [
                    {
                        "type": "text",
                        "text": str(result)
                    }
                ]
            }
            
        except Exception as e:
            return {
                "content": [
                    {
                        "type": "text", 
                        "text": f"Error executing tool: {str(e)}"
                    }
                ],
                "isError": True
            }
    
    async def _handle_list_resources(self, message: MCPMessage) -> Dict[str, Any]:
        """Handle list resources request."""
        resources = []
        
        # Add chatbot models as resources
        for chatbot_name in self.chatbot_manager.get_chatbot_names():
            chatbot = self.chatbot_manager.get_chatbot(chatbot_name)
            if chatbot:
                models = chatbot.get_supported_models()
                for model in models:
                    resource = MCPResource(
                        uri=f"chatbot://{chatbot_name}/{model}",
                        name=f"{chatbot_name}: {model}",
                        description=f"Chatbot model {model} from {chatbot_name}",
                        mimeType="application/json"
                    )
                    resources.append(asdict(resource))
        
        return {"resources": resources}
    
    async def _handle_read_resource(self, message: MCPMessage) -> Dict[str, Any]:
        """Handle read resource request."""
        if not message.params:
            raise ValueError("Missing parameters for resource read")
        
        uri = message.params.get("uri")
        if not uri:
            raise ValueError("Missing resource URI")
        
        # Parse URI to get chatbot and model info
        if uri.startswith("chatbot://"):
            path = uri[10:]  # Remove "chatbot://" prefix
            parts = path.split("/")
            if len(parts) >= 2:
                chatbot_name, model = parts[0], parts[1]
                chatbot = self.chatbot_manager.get_chatbot(chatbot_name)
                if chatbot:
                    info = {
                        "name": chatbot_name,
                        "model": model,
                        "capabilities": {
                            "supports_function_calling": chatbot.supports_function_calling(),
                            "supports_image_understanding": chatbot.supports_image_understanding(),
                            "supported_models": chatbot.get_supported_models(),
                            "supported_image_types": chatbot.get_supported_image_types()
                        }
                    }
                    return {
                        "contents": [
                            {
                                "uri": uri,
                                "mimeType": "application/json",
                                "text": str(info)
                            }
                        ]
                    }
        
        raise ValueError(f"Resource not found: {uri}")
    
    async def _handle_list_prompts(self, message: MCPMessage) -> Dict[str, Any]:
        """Handle list prompts request."""
        prompts = []
        
        # Add some default prompts for chatbot interaction
        default_prompts = [
            MCPPrompt(
                name="chat",
                description="Start a conversation with a chatbot",
                arguments=[
                    {"name": "message", "description": "The message to send", "required": True},
                    {"name": "chatbot", "description": "The chatbot to use", "required": False}
                ]
            ),
            MCPPrompt(
                name="summarize",
                description="Summarize a conversation",
                arguments=[
                    {"name": "conversation_id", "description": "ID of conversation to summarize", "required": True}
                ]
            )
        ]
        
        for prompt in default_prompts:
            prompts.append(asdict(prompt))
        
        return {"prompts": prompts}
    
    async def _handle_get_prompt(self, message: MCPMessage) -> Dict[str, Any]:
        """Handle get prompt request."""
        if not message.params:
            raise ValueError("Missing parameters for get prompt")
        
        prompt_name = message.params.get("name")
        arguments = message.params.get("arguments", {})
        
        if prompt_name == "chat":
            message_text = arguments.get("message", "Hello!")
            chatbot_name = arguments.get("chatbot", "anthropic")
            
            return {
                "description": f"Chat with {chatbot_name}",
                "messages": [
                    {
                        "role": "user",
                        "content": {
                            "type": "text",
                            "text": message_text
                        }
                    }
                ]
            }
        
        elif prompt_name == "summarize":
            conversation_id = arguments.get("conversation_id")
            
            return {
                "description": f"Summarize conversation {conversation_id}",
                "messages": [
                    {
                        "role": "user",
                        "content": {
                            "type": "text",
                            "text": f"Please summarize the conversation with ID: {conversation_id}"
                        }
                    }
                ]
            }
        
        raise ValueError(f"Prompt not found: {prompt_name}")