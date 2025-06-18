"""
Compatibility layer between old Tool system and new MCP tools.

This module provides backward compatibility for adapters that still 
expect the old Tool interface while using the new MCP tool system.
"""

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional
from .mcp_tool_registry import MCPToolRegistry, MCPTool


@dataclass
class Tool:
    """
    Compatibility Tool class that wraps MCP tools.
    
    This maintains the interface expected by the adapters while
    using the new MCP tool system under the hood.
    """
    name: str
    description: str
    input_schema: Dict[str, Any]
    function: Callable[..., Any]
    api_key: Optional[str] = None
    
    def execute(self, **kwargs) -> Any:
        """Execute the tool function."""
        return self.function(**kwargs)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert tool to dictionary representation."""
        return {
            'name': self.name,
            'description': self.description,
            'input_schema': self.input_schema,
            'api_key': self.api_key
        }


class ToolManager:
    """
    Compatibility ToolManager that wraps the MCP tool registry.
    
    This provides the interface expected by existing code while
    using the new MCP system internally.
    """
    
    def __init__(self):
        self.registry = MCPToolRegistry()
        self.favorites: set[str] = set()
        self.active_tools: set[str] = set()
        
        # Initialize with builtin tools
        self._load_builtin_tools()
    
    def _load_builtin_tools(self):
        """Load builtin tools from the registry."""
        from .builtin_tools import BUILTIN_TOOLS
        
        # Register builtin tools in the MCP registry
        for tool_func in BUILTIN_TOOLS:
            try:
                # Convert builtin function to Tool format
                name = getattr(tool_func, '_mcp_name', tool_func.__name__)
                description = tool_func.__doc__ or "No description available"
                
                # Create a simple input schema from function signature
                import inspect
                sig = inspect.signature(tool_func)
                input_schema = {"type": "object", "properties": {}, "required": []}
                
                for param_name, param in sig.parameters.items():
                    param_type = "string"  # Default type
                    if param.annotation != param.empty:
                        if param.annotation == int:
                            param_type = "integer"
                        elif param.annotation == float:
                            param_type = "number"
                        elif param.annotation == bool:
                            param_type = "boolean"
                    
                    input_schema["properties"][param_name] = {
                        "type": param_type,
                        "description": f"Parameter {param_name}"
                    }
                    
                    if param.default == param.empty:
                        input_schema["required"].append(param_name)
                
            except Exception:
                # Fallback to simple schema
                input_schema = {"type": "object", "properties": {}}
    
    @property
    def tools(self) -> Dict[str, Tool]:
        """Get all tools as Tool objects for compatibility."""
        result = {}
        
        # Convert MCP tools to Tool objects
        for name, mcp_tool in self.registry.tools.items():
            schema = mcp_tool.get_schema()
            
            # Create a wrapper function for the MCP tool
            async def wrapper(**kwargs):
                return await mcp_tool.execute(**kwargs)
            
            tool = Tool(
                name=schema.name,
                description=schema.description,
                input_schema=schema.input_schema,
                function=wrapper
            )
            result[name] = tool
        
        return result
    
    def add_to_favorites(self, tool_name: str) -> None:
        """Add a tool to favorites."""
        if tool_name in self.registry.tools:
            self.favorites.add(tool_name)
    
    def remove_from_favorites(self, tool_name: str) -> None:
        """Remove a tool from favorites."""
        self.favorites.discard(tool_name)
    
    def activate_tool(self, tool_name: str) -> None:
        """Activate a tool."""
        if tool_name in self.registry.tools:
            self.active_tools.add(tool_name)
    
    def deactivate_tool(self, tool_name: str) -> None:
        """Deactivate a tool."""
        self.active_tools.discard(tool_name)
    
    def get_active_tools(self) -> List[Tool]:
        """Get list of active tools as Tool objects."""
        all_tools = self.tools
        return [all_tools[name] for name in self.active_tools if name in all_tools]
    
    def get_tool(self, name: str) -> Optional[Tool]:
        """Get a specific tool by name."""
        all_tools = self.tools
        return all_tools.get(name)


# Create singleton instances for backward compatibility
_tool_manager_instance = None

def get_tool_manager() -> ToolManager:
    """Get the global tool manager instance."""
    global _tool_manager_instance
    if _tool_manager_instance is None:
        _tool_manager_instance = ToolManager()
    return _tool_manager_instance