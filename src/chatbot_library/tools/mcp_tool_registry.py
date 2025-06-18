"""
MCP-compatible tool registry for dynamic tool discovery and management.
"""

import json
import inspect
from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
from typing import Dict, List, Any, Callable, Optional, Type, get_type_hints
from pathlib import Path
import importlib
import pkgutil


@dataclass
class MCPToolSchema:
    """MCP-compatible tool schema definition."""
    name: str
    description: str
    input_schema: Dict[str, Any]
    output_schema: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def to_mcp_format(self) -> Dict[str, Any]:
        """Convert to MCP tool format."""
        return {
            "name": self.name,
            "description": self.description,
            "inputSchema": self.input_schema,
            **({"outputSchema": self.output_schema} if self.output_schema else {}),
            **({"metadata": self.metadata} if self.metadata else {})
        }


class MCPTool(ABC):
    """Abstract base class for MCP-compatible tools."""
    
    @abstractmethod
    def get_schema(self) -> MCPToolSchema:
        """Return the tool's schema definition."""
        pass
    
    @abstractmethod
    async def execute(self, **kwargs) -> Any:
        """Execute the tool with given parameters."""
        pass
    
    def validate_input(self, **kwargs) -> bool:
        """Validate input parameters against schema."""
        schema = self.get_schema()
        required_fields = schema.input_schema.get("required", [])
        
        # Check required fields
        for field in required_fields:
            if field not in kwargs:
                raise ValueError(f"Missing required parameter: {field}")
        
        # Check field types (basic validation)
        properties = schema.input_schema.get("properties", {})
        for field, value in kwargs.items():
            if field in properties:
                expected_type = properties[field].get("type")
                if expected_type and not self._validate_type(value, expected_type):
                    raise ValueError(f"Invalid type for {field}: expected {expected_type}")
        
        return True
    
    def _validate_type(self, value: Any, expected_type: str) -> bool:
        """Basic type validation."""
        type_mapping = {
            "string": str,
            "number": (int, float),
            "integer": int,
            "boolean": bool,
            "array": list,
            "object": dict
        }
        
        expected_python_type = type_mapping.get(expected_type)
        if expected_python_type:
            return isinstance(value, expected_python_type)
        return True


class MCPToolRegistry:
    """Registry for managing MCP-compatible tools."""
    
    def __init__(self):
        self.tools: Dict[str, MCPTool] = {}
        self.tool_schemas: Dict[str, MCPToolSchema] = {}
    
    def register_tool(self, tool: MCPTool) -> None:
        """Register a tool instance."""
        schema = tool.get_schema()
        self.tools[schema.name] = tool
        self.tool_schemas[schema.name] = schema
    
    def register_tool_class(self, tool_class: Type[MCPTool], **init_kwargs) -> None:
        """Register a tool class with initialization parameters."""
        tool_instance = tool_class(**init_kwargs)
        self.register_tool(tool_instance)
    
    def register_function_as_tool(
        self, 
        func: Callable,
        name: Optional[str] = None,
        description: Optional[str] = None,
        input_schema: Optional[Dict[str, Any]] = None
    ) -> None:
        """Register a regular function as an MCP tool."""
        tool_name = name or func.__name__
        tool_description = description or func.__doc__ or f"Function {func.__name__}"
        
        # Auto-generate schema from function signature if not provided
        if input_schema is None:
            input_schema = self._generate_schema_from_function(func)
        
        # Create a dynamic tool class
        class FunctionTool(MCPTool):
            def get_schema(self) -> MCPToolSchema:
                return MCPToolSchema(
                    name=tool_name,
                    description=tool_description,
                    input_schema=input_schema
                )
            
            async def execute(self, **kwargs) -> Any:
                # Handle both sync and async functions
                if inspect.iscoroutinefunction(func):
                    return await func(**kwargs)
                else:
                    return func(**kwargs)
        
        self.register_tool(FunctionTool())
    
    def _generate_schema_from_function(self, func: Callable) -> Dict[str, Any]:
        """Auto-generate JSON schema from function signature."""
        sig = inspect.signature(func)
        type_hints = get_type_hints(func)
        
        properties = {}
        required = []
        
        for param_name, param in sig.parameters.items():
            if param_name == 'self':
                continue
                
            param_type = type_hints.get(param_name, str)
            json_type = self._python_type_to_json_type(param_type)
            
            properties[param_name] = {
                "type": json_type,
                "description": f"Parameter {param_name}"
            }
            
            # Check if parameter is required (no default value)
            if param.default == inspect.Parameter.empty:
                required.append(param_name)
        
        return {
            "type": "object",
            "properties": properties,
            "required": required
        }
    
    def _python_type_to_json_type(self, python_type: Type) -> str:
        """Convert Python type to JSON schema type."""
        type_mapping = {
            str: "string",
            int: "integer", 
            float: "number",
            bool: "boolean",
            list: "array",
            dict: "object"
        }
        
        # Handle Union types (e.g., Optional[str])
        if hasattr(python_type, '__origin__'):
            if python_type.__origin__ is list:
                return "array"
            elif python_type.__origin__ is dict:
                return "object"
        
        return type_mapping.get(python_type, "string")
    
    def get_tool(self, name: str) -> Optional[MCPTool]:
        """Get a tool by name."""
        return self.tools.get(name)
    
    def list_tools(self) -> List[str]:
        """List all registered tool names."""
        return list(self.tools.keys())
    
    def get_tool_schema(self, name: str) -> Optional[MCPToolSchema]:
        """Get tool schema by name."""
        return self.tool_schemas.get(name)
    
    def get_all_schemas(self) -> List[Dict[str, Any]]:
        """Get all tool schemas in MCP format."""
        return [schema.to_mcp_format() for schema in self.tool_schemas.values()]
    
    async def execute_tool(self, name: str, **kwargs) -> Any:
        """Execute a tool by name."""
        tool = self.get_tool(name)
        if not tool:
            raise ValueError(f"Tool '{name}' not found")
        
        # Validate input
        tool.validate_input(**kwargs)
        
        # Execute tool
        return await tool.execute(**kwargs)
    
    def discover_tools_in_package(self, package_path: str) -> None:
        """Automatically discover and register tools in a package."""
        try:
            package = importlib.import_module(package_path)
            
            for importer, modname, ispkg in pkgutil.iter_modules(package.__path__):
                if not ispkg:
                    module_path = f"{package_path}.{modname}"
                    try:
                        module = importlib.import_module(module_path)
                        self._register_tools_from_module(module)
                    except Exception as e:
                        print(f"Failed to import {module_path}: {e}")
        
        except Exception as e:
            print(f"Failed to discover tools in {package_path}: {e}")
    
    def _register_tools_from_module(self, module) -> None:
        """Register tools from a module."""
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            
            # Register tool classes
            if (inspect.isclass(attr) and 
                issubclass(attr, MCPTool) and 
                attr != MCPTool):
                try:
                    self.register_tool_class(attr)
                except Exception as e:
                    print(f"Failed to register tool class {attr_name}: {e}")
            
            # Register functions with tool decorators
            elif (inspect.isfunction(attr) and 
                  hasattr(attr, '_mcp_tool_config')):
                config = attr._mcp_tool_config
                self.register_function_as_tool(
                    attr,
                    name=config.get('name'),
                    description=config.get('description'),
                    input_schema=config.get('input_schema')
                )


def mcp_tool(name: Optional[str] = None, description: Optional[str] = None, 
             input_schema: Optional[Dict[str, Any]] = None):
    """Decorator to mark functions as MCP tools."""
    def decorator(func):
        func._mcp_tool_config = {
            'name': name,
            'description': description, 
            'input_schema': input_schema
        }
        return func
    return decorator


# Global registry instance
mcp_tool_registry = MCPToolRegistry()