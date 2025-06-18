"""
Iterative tool execution system.

This module provides functionality for tools to call other tools in a chain,
with loop detection, approval workflows, and execution tracking.
"""

import uuid
import time
import asyncio
from typing import Dict, List, Any, Optional, Set, Callable, Union
from dataclasses import dataclass, field
from datetime import datetime

from ..models.conversation import ToolUse, ToolResult
from ..utils.logging import get_logger


@dataclass
class ToolExecutionContext:
    """Context for tool execution with iterative capabilities."""
    conversation_id: str
    message_id: str
    max_iterations: int = 10
    max_depth: int = 5
    current_iteration: int = 1
    current_depth: int = 0
    execution_chain: List[str] = field(default_factory=list)
    tool_results: Dict[str, ToolResult] = field(default_factory=dict)
    approval_callback: Optional[Callable[[ToolUse], bool]] = None
    

@dataclass
class IterativeExecutionResult:
    """Result from iterative tool execution."""
    final_result: Any
    execution_chain: List[ToolResult]
    total_iterations: int
    total_execution_time: float
    success: bool = True
    error: Optional[str] = None
    loop_detected: bool = False
    max_iterations_reached: bool = False


class IterativeToolExecutor:
    """
    Executes tools with support for iterative calling and chain management.
    
    Features:
    - Loop detection to prevent infinite recursion
    - Maximum iteration and depth limits
    - Tool dependency tracking
    - Optional human approval for sensitive operations
    - Comprehensive execution logging
    """
    
    def __init__(self, tool_registry, max_iterations: int = 10, max_depth: int = 5):
        self.tool_registry = tool_registry
        self.max_iterations = max_iterations
        self.max_depth = max_depth
        self.logger = get_logger(self.__class__.__name__.lower())
        
    async def execute_tool_chain(
        self, 
        initial_tool: str,
        initial_parameters: Dict[str, Any],
        context: ToolExecutionContext
    ) -> IterativeExecutionResult:
        """
        Execute a tool that may trigger other tools in a chain.
        
        Args:
            initial_tool: Name of the first tool to execute
            initial_parameters: Parameters for the initial tool
            context: Execution context with limits and callbacks
            
        Returns:
            Complete execution result including all iterations
        """
        start_time = time.time()
        execution_chain = []
        current_context = context
        
        try:
            # Execute the initial tool
            result = await self._execute_single_tool(
                initial_tool, 
                initial_parameters, 
                current_context
            )
            
            execution_chain.append(result)
            
            # Check if tool triggered additional tools
            while (result.triggered_tools and 
                   current_context.current_iteration < current_context.max_iterations and
                   current_context.current_depth < current_context.max_depth):
                
                # Check for loops
                if self._detect_loop(execution_chain):
                    return IterativeExecutionResult(
                        final_result=result.tool_result,
                        execution_chain=execution_chain,
                        total_iterations=current_context.current_iteration,
                        total_execution_time=time.time() - start_time,
                        success=False,
                        loop_detected=True
                    )
                
                # Execute triggered tools
                next_tools = result.triggered_tools.copy()
                result.triggered_tools.clear()  # Clear to avoid re-execution
                
                for tool_name in next_tools:
                    current_context.current_iteration += 1
                    current_context.current_depth += 1
                    
                    # Extract parameters from previous result if needed
                    tool_params = self._extract_parameters_for_tool(
                        tool_name, result.tool_result
                    )
                    
                    next_result = await self._execute_single_tool(
                        tool_name, 
                        tool_params, 
                        current_context,
                        parent_tool_id=result.tool_use_id
                    )
                    
                    execution_chain.append(next_result)
                    result = next_result  # Continue chain with latest result
                    
                    current_context.current_depth -= 1
            
            # Check if we hit limits
            max_iterations_reached = (
                current_context.current_iteration >= current_context.max_iterations
            )
            
            return IterativeExecutionResult(
                final_result=result.tool_result,
                execution_chain=execution_chain,
                total_iterations=current_context.current_iteration,
                total_execution_time=time.time() - start_time,
                success=result.success,
                error=result.error,
                max_iterations_reached=max_iterations_reached
            )
            
        except Exception as e:
            return IterativeExecutionResult(
                final_result=None,
                execution_chain=execution_chain,
                total_iterations=current_context.current_iteration,
                total_execution_time=time.time() - start_time,
                success=False,
                error=str(e)
            )
    
    async def _execute_single_tool(
        self, 
        tool_name: str, 
        parameters: Dict[str, Any],
        context: ToolExecutionContext,
        parent_tool_id: Optional[str] = None
    ) -> ToolResult:
        """Execute a single tool with full tracking."""
        tool_use_id = str(uuid.uuid4())
        start_time = time.time()
        
        # Create tool use record
        tool_use = ToolUse(
            tool_name=tool_name,
            tool_input=parameters,
            tool_use_id=tool_use_id,
            iteration=context.current_iteration,
            parent_tool_id=parent_tool_id
        )
        
        # Check if approval is needed
        if (context.approval_callback and 
            await self._requires_approval(tool_name, parameters)):
            tool_use.requires_human_approval = True
            
            if not context.approval_callback(tool_use):
                return ToolResult(
                    tool_use_id=tool_use_id,
                    tool_result="Tool execution denied by user",
                    success=False,
                    error="Human approval required but denied",
                    execution_time=time.time() - start_time,
                    iteration=context.current_iteration
                )
        
        try:
            # Execute the tool
            result = await self.tool_registry.execute_tool(tool_name, **parameters)
            
            # Check if tool wants to trigger other tools
            triggered_tools = []
            if isinstance(result, dict) and 'next_tools' in result:
                triggered_tools = result.get('next_tools', [])
                # Remove metadata from result
                result = {k: v for k, v in result.items() if k != 'next_tools'}
            
            execution_time = time.time() - start_time
            
            tool_result = ToolResult(
                tool_use_id=tool_use_id,
                tool_result=str(result),
                success=True,
                execution_time=execution_time,
                iteration=context.current_iteration,
                triggered_tools=triggered_tools
            )
            
            # Add to context
            context.tool_results[tool_use_id] = tool_result
            context.execution_chain.append(tool_use_id)
            
            self.logger.info(
                f"Tool execution completed: {tool_name} (iteration {context.current_iteration})"
            )
            
            return tool_result
            
        except Exception as e:
            execution_time = time.time() - start_time
            
            tool_result = ToolResult(
                tool_use_id=tool_use_id,
                tool_result="",
                success=False,
                error=str(e),
                execution_time=execution_time,
                iteration=context.current_iteration
            )
            
            context.tool_results[tool_use_id] = tool_result
            context.execution_chain.append(tool_use_id)
            
            self.logger.error(
                f"Tool execution failed: {tool_name} - {str(e)}"
            )
            
            return tool_result
    
    def _detect_loop(self, execution_chain: List[ToolResult]) -> bool:
        """Detect if we're in an infinite loop of tool calls."""
        if len(execution_chain) < 3:
            return False
        
        # Get tool names from execution chain
        tool_names = []
        for result in execution_chain:
            # Extract tool name from tool_result if it contains tool info
            if isinstance(result.tool_result, str) and 'tool_name' in result.tool_result:
                try:
                    import ast
                    parsed = ast.literal_eval(result.tool_result)
                    if isinstance(parsed, dict) and 'tool_name' in parsed:
                        tool_names.append(parsed['tool_name'])
                    else:
                        tool_names.append('unknown')
                except:
                    tool_names.append('unknown')
            else:
                tool_names.append('unknown')
        
        # Check recent tools for loops
        recent_tools = tool_names[-5:]
        
        # Simple loop detection: same tool called multiple times recently
        tool_counts = {}
        for tool_name in recent_tools:
            tool_counts[tool_name] = tool_counts.get(tool_name, 0) + 1
        
        # If any tool appears more than 2 times in recent history, likely a loop
        return any(count > 2 for count in tool_counts.values())
    
    def _extract_parameters_for_tool(
        self, 
        tool_name: str, 
        previous_result: str
    ) -> Dict[str, Any]:
        """Extract parameters for the next tool from previous result."""
        # This is a simplified implementation
        # In practice, this would use AI or predefined rules to extract parameters
        
        if tool_name == "calculate":
            # Try to extract mathematical expressions
            import re
            # Look for mathematical expressions with operators
            expressions = re.findall(r'[\d\s]*[\d]\s*[\+\-\*/]\s*[\d][\d\s]*', previous_result)
            if expressions:
                return {"expression": expressions[0].strip()}
            # Also check if "calculate" keyword is present with numbers
            elif "calculate" in previous_result.lower() or any(op in previous_result for op in ['+', '-', '*', '/', '=']):
                numbers_and_ops = re.findall(r'[\d\+\-\*/\(\)\s\.=]+', previous_result)
                for expr in numbers_and_ops:
                    expr = expr.strip()
                    if len(expr) > 1 and any(op in expr for op in ['+', '-', '*', '/']):
                        return {"expression": expr}
        
        if tool_name == "get_weather":
            # Try to extract location - look for words after "in" or capitalized location names
            import re
            # Pattern for "in LocationName"
            location_match = re.search(r'\bin\s+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*)', previous_result)
            if location_match:
                return {"location": location_match.group(1)}
            
            # Look for capitalized words that might be locations (but not common words)
            words = previous_result.split()
            common_words = {'The', 'Check', 'Get', 'Find', 'Show', 'Today', 'Tomorrow', 'Weather'}
            locations = [word for word in words if word[0].isupper() and len(word) > 2 and word not in common_words]
            if locations:
                return {"location": locations[0]}
        
        # Default: pass the result as input using tool-specific parameter names
        # Try to extract the main result value from structured results
        if isinstance(previous_result, str):
            try:
                import ast
                parsed_result = ast.literal_eval(previous_result)
                if isinstance(parsed_result, dict):
                    # For chain_starter, use processed_data as input_text
                    if tool_name == "chain_starter" and "processed_data" in parsed_result:
                        return {"input_text": parsed_result["processed_data"]}
                    # For other tools, try to find the most relevant data
                    elif "processed_data" in parsed_result:
                        return {"input": parsed_result["processed_data"]}
                    elif "result" in parsed_result:
                        return {"input": parsed_result["result"]}
            except:
                pass
        
        # Fall back to generic input parameter
        return {"input": previous_result}
    
    async def _requires_approval(
        self, 
        tool_name: str, 
        parameters: Dict[str, Any]
    ) -> bool:
        """Check if a tool requires human approval before execution."""
        # Define tools that require approval
        sensitive_tools = {
            "file_write", "file_delete", "send_email", "make_payment", 
            "system_command", "database_modify"
        }
        
        return tool_name in sensitive_tools
    
    def get_execution_summary(self, result: IterativeExecutionResult) -> Dict[str, Any]:
        """Get a human-readable summary of the execution."""
        return {
            "total_tools_executed": len(result.execution_chain),
            "total_iterations": result.total_iterations,
            "execution_time_seconds": round(result.total_execution_time, 3),
            "success": result.success,
            "tools_used": [r.tool_use_id for r in result.execution_chain],
            "loop_detected": result.loop_detected,
            "max_iterations_reached": result.max_iterations_reached,
            "final_result": result.final_result
        }