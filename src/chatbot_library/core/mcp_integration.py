"""
Integration layer between MCP tools and the conversation manager.
"""

import asyncio
import json
import time
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass

from ..tools.mcp_tool_registry import MCPToolRegistry, mcp_tool_registry
from ..tools.builtin_tools import register_builtin_tools
from ..tools.iterative_execution import (
    IterativeToolExecutor, ToolExecutionContext, IterativeExecutionResult
)
from .conversation_manager import ConversationManager
from ..models.conversation import Message, Response


@dataclass 
class ToolExecutionResult:
    """Result of executing an MCP tool."""
    tool_name: str
    success: bool
    result: Any = None
    error: Optional[str] = None
    execution_time: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None


class MCPConversationManager(ConversationManager):
    """Enhanced conversation manager with MCP tool integration."""
    
    def __init__(self, data_dir, tool_registry: Optional[MCPToolRegistry] = None):
        super().__init__(data_dir)
        self.tool_registry = tool_registry or mcp_tool_registry
        self.iterative_executor = IterativeToolExecutor(self.tool_registry)
        self._setup_builtin_tools()
    
    def _setup_builtin_tools(self):
        """Setup built-in MCP tools."""
        import os
        weather_api_key = os.getenv("OPENWEATHER_API_KEY")
        register_builtin_tools(self.tool_registry, weather_api_key)
    
    def get_available_tools(self) -> List[Dict[str, Any]]:
        """Get all available tools in MCP format."""
        return self.tool_registry.get_all_schemas()
    
    def get_tool_schema(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """Get schema for a specific tool."""
        schema = self.tool_registry.get_tool_schema(tool_name)
        return schema.to_mcp_format() if schema else None
    
    async def execute_tool(
        self, 
        tool_name: str, 
        parameters: Dict[str, Any],
        conversation_id: Optional[str] = None,
        message_id: Optional[str] = None
    ) -> ToolExecutionResult:
        """Execute an MCP tool and optionally record it in conversation."""
        import time
        
        start_time = time.time()
        
        try:
            result = await self.tool_registry.execute_tool(tool_name, **parameters)
            execution_time = time.time() - start_time
            
            tool_result = ToolExecutionResult(
                tool_name=tool_name,
                success=True,
                result=result,
                execution_time=execution_time,
                metadata={
                    "parameters": parameters,
                    "timestamp": time.time()
                }
            )
            
            # Optionally record tool usage in conversation
            if conversation_id and message_id:
                await self._record_tool_usage(
                    conversation_id, message_id, tool_result
                )
            
            return tool_result
            
        except Exception as e:
            execution_time = time.time() - start_time
            
            tool_result = ToolExecutionResult(
                tool_name=tool_name,
                success=False,
                error=str(e),
                execution_time=execution_time,
                metadata={
                    "parameters": parameters,
                    "timestamp": time.time()
                }
            )
            
            # Record failed tool usage in conversation
            if conversation_id and message_id:
                await self._record_tool_usage(
                    conversation_id, message_id, tool_result
                )
            
            return tool_result
    
    async def _record_tool_usage(
        self, 
        conversation_id: str, 
        message_id: str, 
        tool_result: ToolExecutionResult
    ):
        """Record tool usage in conversation metadata."""
        conversation = self.get_conversation(conversation_id)
        if not conversation:
            return
        
        # Find the message and add tool usage to metadata
        for message in conversation.messages:
            if message.id == message_id:
                if not hasattr(message, 'metadata') or message.metadata is None:
                    message.metadata = {}
                
                if 'tool_usage' not in message.metadata:
                    message.metadata['tool_usage'] = []
                
                message.metadata['tool_usage'].append({
                    'tool_name': tool_result.tool_name,
                    'success': tool_result.success,
                    'execution_time': tool_result.execution_time,
                    'timestamp': tool_result.metadata.get('timestamp') if tool_result.metadata else None,
                    'error': tool_result.error
                })
                
                # Save the updated conversation
                self.save_conversation(conversation)
                break
    
    async def add_response_with_tools(
        self,
        conversation_id: str,
        message_id: str,
        model: str,
        text: str,
        tools_used: Optional[List[Dict[str, Any]]] = None,
        branch_name: Optional[str] = None,
        **kwargs
    ) -> Response:
        """Add a response that may have used tools."""
        
        # Execute any requested tools
        tool_results = []
        if tools_used:
            for tool_call in tools_used:
                tool_name = tool_call.get('name')
                parameters = tool_call.get('parameters', {})
                
                if tool_name:
                    result = await self.execute_tool(
                        tool_name, 
                        parameters,
                        conversation_id,
                        message_id
                    )
                    tool_results.append(result)
        
        # Include tool results in response metadata
        metadata = kwargs.get('metadata', {})
        if tool_results:
            metadata['tools_executed'] = [
                {
                    'tool_name': result.tool_name,
                    'success': result.success,
                    'execution_time': result.execution_time,
                    'result_summary': str(result.result)[:200] if result.result else None
                }
                for result in tool_results
            ]
        
        # Add the response with tool metadata
        conversation = self.get_conversation(conversation_id)
        if not conversation:
            raise ValueError(f"Conversation {conversation_id} not found")
        
        message = conversation.get_message(message_id)
        if not message:
            raise ValueError(f"Message {message_id} not found")
        
        response = message.add_response(
            model=model,
            text=text,
            branch_name=branch_name,
            metadata=metadata,
            **kwargs
        )
        
        # Save the conversation
        self.save_conversation(conversation)
        
        return response
    
    def get_conversation_tool_usage(self, conversation_id: str) -> Dict[str, Any]:
        """Get tool usage statistics for a conversation."""
        conversation = self.get_conversation(conversation_id)
        if not conversation:
            return {}
        
        tool_stats = {}
        total_executions = 0
        total_errors = 0
        total_time = 0.0
        
        for message in conversation.messages:
            if hasattr(message, 'metadata') and message.metadata:
                tool_usage = message.metadata.get('tool_usage', [])
                
                for usage in tool_usage:
                    tool_name = usage['tool_name']
                    total_executions += 1
                    
                    if usage['execution_time']:
                        total_time += usage['execution_time']
                    
                    if not usage['success']:
                        total_errors += 1
                    
                    if tool_name not in tool_stats:
                        tool_stats[tool_name] = {
                            'count': 0,
                            'errors': 0,
                            'total_time': 0.0
                        }
                    
                    tool_stats[tool_name]['count'] += 1
                    if not usage['success']:
                        tool_stats[tool_name]['errors'] += 1
                    if usage['execution_time']:
                        tool_stats[tool_name]['total_time'] += usage['execution_time']
        
        return {
            'total_tool_executions': total_executions,
            'total_errors': total_errors,
            'total_execution_time': total_time,
            'success_rate': (total_executions - total_errors) / max(total_executions, 1),
            'tools': tool_stats
        }
    
    def discover_external_tools(self, package_paths: List[str]):
        """Discover tools from external packages."""
        for package_path in package_paths:
            self.tool_registry.discover_tools_in_package(package_path)
    
    async def get_tool_recommendations(
        self, 
        conversation_id: str,
        message_text: str
    ) -> List[Dict[str, Any]]:
        """Get tool recommendations based on conversation context and message."""
        
        # Simple keyword-based recommendations (could be enhanced with ML)
        recommendations = []
        
        # Get available tools
        available_tools = self.get_available_tools()
        
        # Keyword matching for recommendations
        message_lower = message_text.lower()
        
        for tool in available_tools:
            score = 0
            tool_name = tool['name']
            description = tool['description'].lower()
            
            # Simple scoring based on keyword matches
            keywords = {
                'time': ['time', 'date', 'when', 'clock'],
                'weather': ['weather', 'temperature', 'rain', 'sunny', 'cloudy'],
                'calculate': ['calculate', 'math', 'compute', '+', '-', '*', '/', 'equation'],
                'text': ['count', 'length', 'characters', 'words'],
                'encode': ['encode', 'base64', 'encrypt'],
                'decode': ['decode', 'base64', 'decrypt']
            }
            
            for category, words in keywords.items():
                if category in tool_name or category in description:
                    for word in words:
                        if word in message_lower:
                            score += 1
            
            if score > 0:
                recommendations.append({
                    'tool_name': tool_name,
                    'score': score,
                    'description': tool['description'],
                    'relevance': 'high' if score >= 2 else 'medium'
                })
        
        # Sort by score
        recommendations.sort(key=lambda x: x['score'], reverse=True)
        
        return recommendations[:5]  # Return top 5
    
    # Iterative Tool Execution Methods
    
    async def execute_tool_chain(
        self,
        initial_tool: str,
        initial_parameters: Dict[str, Any],
        conversation_id: str,
        message_id: str,
        max_iterations: int = 10,
        max_depth: int = 5,
        approval_callback: Optional[Callable] = None
    ) -> IterativeExecutionResult:
        """
        Execute a tool that may trigger other tools in a chain.
        
        Args:
            initial_tool: Name of the first tool to execute
            initial_parameters: Parameters for the initial tool
            conversation_id: ID of the conversation
            message_id: ID of the message
            max_iterations: Maximum number of tool iterations
            max_depth: Maximum depth of tool calls
            approval_callback: Optional callback for tool approval
            
        Returns:
            Complete execution result including all iterations
        """
        context = ToolExecutionContext(
            conversation_id=conversation_id,
            message_id=message_id,
            max_iterations=max_iterations,
            max_depth=max_depth,
            approval_callback=approval_callback
        )
        
        result = await self.iterative_executor.execute_tool_chain(
            initial_tool, initial_parameters, context
        )
        
        # Record the execution in conversation metadata
        await self._record_iterative_execution(conversation_id, message_id, result)
        
        return result
    
    async def _record_iterative_execution(
        self,
        conversation_id: str,
        message_id: str,
        result: IterativeExecutionResult
    ):
        """Record iterative tool execution in conversation metadata."""
        conversation = self.get_conversation(conversation_id)
        if not conversation:
            return
        
        message = conversation.get_message(message_id)
        if not message:
            return
        
        # Add execution summary to message metadata
        if not hasattr(message, 'metadata') or message.metadata is None:
            message.metadata = {}
        
        if 'iterative_executions' not in message.metadata:
            message.metadata['iterative_executions'] = []
        
        execution_summary = self.iterative_executor.get_execution_summary(result)
        execution_summary['timestamp'] = time.time()
        
        message.metadata['iterative_executions'].append(execution_summary)
        
        # Save the conversation
        self.save_conversation(conversation)
    
    def get_iterative_execution_stats(self, conversation_id: str) -> Dict[str, Any]:
        """Get statistics about iterative tool executions in a conversation."""
        conversation = self.get_conversation(conversation_id)
        if not conversation:
            return {}
        
        total_executions = 0
        total_tools_used = 0
        total_execution_time = 0.0
        loop_detections = 0
        max_iterations_reached = 0
        
        for message in conversation.messages:
            if hasattr(message, 'metadata') and message.metadata:
                executions = message.metadata.get('iterative_executions', [])
                
                for execution in executions:
                    total_executions += 1
                    total_tools_used += execution.get('total_tools_executed', 0)
                    total_execution_time += execution.get('execution_time_seconds', 0)
                    
                    if execution.get('loop_detected'):
                        loop_detections += 1
                    
                    if execution.get('max_iterations_reached'):
                        max_iterations_reached += 1
        
        return {
            'total_iterative_executions': total_executions,
            'total_tools_in_chains': total_tools_used,
            'total_execution_time': round(total_execution_time, 3),
            'average_tools_per_chain': (
                round(total_tools_used / total_executions, 2) 
                if total_executions > 0 else 0
            ),
            'loop_detections': loop_detections,
            'max_iterations_reached': max_iterations_reached
        }
    
    async def approve_tool_execution(self, tool_use_id: str) -> bool:
        """Approve a tool execution that requires human approval."""
        # This is a placeholder - in a real implementation, this would
        # connect to a UI or notification system for human approval
        return True
    
    def set_iterative_limits(self, max_iterations: int = 10, max_depth: int = 5):
        """Set limits for iterative tool execution."""
        self.iterative_executor.max_iterations = max_iterations
        self.iterative_executor.max_depth = max_depth