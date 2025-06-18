"""
Tests for the MCP tool registry system.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from typing import Dict, Any

from chatbot_library.tools.mcp_tool_registry import (
    MCPTool, MCPToolSchema, MCPToolRegistry, mcp_tool
)


class TestMCPToolSchema:
    """Test the MCPToolSchema dataclass."""
    
    def test_schema_creation(self):
        """Test creating a tool schema."""
        schema = MCPToolSchema(
            name="test_tool",
            description="A test tool",
            input_schema={
                "type": "object",
                "properties": {
                    "param1": {"type": "string", "description": "First parameter"}
                },
                "required": ["param1"]
            }
        )
        
        assert schema.name == "test_tool"
        assert schema.description == "A test tool"
        assert "param1" in schema.input_schema["properties"]
    
    def test_to_mcp_format(self):
        """Test converting schema to MCP format."""
        schema = MCPToolSchema(
            name="format_test",
            description="Format test tool",
            input_schema={"type": "object", "properties": {}},
            output_schema={"type": "string"},
            metadata={"category": "test"}
        )
        
        mcp_format = schema.to_mcp_format()
        
        assert mcp_format["name"] == "format_test"
        assert mcp_format["description"] == "Format test tool"
        assert mcp_format["inputSchema"]["type"] == "object"
        assert mcp_format["outputSchema"]["type"] == "string"
        assert mcp_format["metadata"]["category"] == "test"


class SimpleMCPTool(MCPTool):
    """Simple test tool implementation."""
    
    def __init__(self, name: str = "simple_tool"):
        self.name = name
    
    def get_schema(self) -> MCPToolSchema:
        return MCPToolSchema(
            name=self.name,
            description="A simple test tool",
            input_schema={
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "Input text"}
                },
                "required": ["text"]
            }
        )
    
    async def execute(self, text: str) -> Dict[str, Any]:
        return {"result": f"Processed: {text}", "length": len(text)}


class ErrorMCPTool(MCPTool):
    """Tool that throws errors for testing error handling."""
    
    def get_schema(self) -> MCPToolSchema:
        return MCPToolSchema(
            name="error_tool",
            description="Tool that throws errors",
            input_schema={
                "type": "object",
                "properties": {
                    "should_error": {"type": "boolean", "default": False}
                }
            }
        )
    
    async def execute(self, should_error: bool = False) -> Dict[str, Any]:
        if should_error:
            raise ValueError("Intentional test error")
        return {"success": True}


class TestMCPTool:
    """Test the MCPTool base class."""
    
    @pytest.mark.asyncio
    async def test_tool_execution(self):
        """Test basic tool execution."""
        tool = SimpleMCPTool()
        result = await tool.execute(text="hello world")
        
        assert result["result"] == "Processed: hello world"
        assert result["length"] == 11
    
    def test_tool_schema(self):
        """Test tool schema generation."""
        tool = SimpleMCPTool("test_schema")
        schema = tool.get_schema()
        
        assert schema.name == "test_schema"
        assert schema.description == "A simple test tool"
        assert "text" in schema.input_schema["properties"]
    
    def test_input_validation_success(self):
        """Test successful input validation."""
        tool = SimpleMCPTool()
        
        # Should not raise
        assert tool.validate_input(text="valid input") is True
    
    def test_input_validation_missing_required(self):
        """Test validation with missing required parameter."""
        tool = SimpleMCPTool()
        
        with pytest.raises(ValueError, match="Missing required parameter: text"):
            tool.validate_input()
    
    def test_input_validation_wrong_type(self):
        """Test validation with wrong parameter type."""
        tool = SimpleMCPTool()
        
        # Create schema that expects integer
        tool.get_schema = lambda: MCPToolSchema(
            name="type_test",
            description="Type test",
            input_schema={
                "type": "object",
                "properties": {
                    "number": {"type": "integer"}
                },
                "required": ["number"]
            }
        )
        
        with pytest.raises(ValueError, match="Invalid type for number"):
            tool.validate_input(number="not_a_number")


class TestMCPToolRegistry:
    """Test the MCPToolRegistry class."""
    
    def test_registry_creation(self, tool_registry):
        """Test creating a registry."""
        assert len(tool_registry.tools) == 0
        assert len(tool_registry.tool_schemas) == 0
    
    def test_register_tool(self, tool_registry):
        """Test registering a tool instance."""
        tool = SimpleMCPTool("registered_tool")
        tool_registry.register_tool(tool)
        
        assert "registered_tool" in tool_registry.tools
        assert "registered_tool" in tool_registry.tool_schemas
        assert tool_registry.get_tool("registered_tool") == tool
    
    def test_register_tool_class(self, tool_registry):
        """Test registering a tool class."""
        tool_registry.register_tool_class(SimpleMCPTool, name="class_tool")
        
        assert "class_tool" in tool_registry.tools
        assert isinstance(tool_registry.get_tool("class_tool"), SimpleMCPTool)
    
    def test_list_tools(self, tool_registry):
        """Test listing registered tools."""
        tool1 = SimpleMCPTool("tool1")
        tool2 = SimpleMCPTool("tool2")
        
        tool_registry.register_tool(tool1)
        tool_registry.register_tool(tool2)
        
        tools = tool_registry.list_tools()
        assert "tool1" in tools
        assert "tool2" in tools
        assert len(tools) == 2
    
    def test_get_all_schemas(self, tool_registry):
        """Test getting all schemas in MCP format."""
        tool = SimpleMCPTool("schema_test")
        tool_registry.register_tool(tool)
        
        schemas = tool_registry.get_all_schemas()
        assert len(schemas) == 1
        assert schemas[0]["name"] == "schema_test"
        assert "inputSchema" in schemas[0]
    
    @pytest.mark.asyncio
    async def test_execute_tool(self, tool_registry):
        """Test executing a tool through the registry."""
        tool = SimpleMCPTool("execute_test")
        tool_registry.register_tool(tool)
        
        result = await tool_registry.execute_tool("execute_test", text="test input")
        
        assert result["result"] == "Processed: test input"
        assert result["length"] == 10
    
    @pytest.mark.asyncio
    async def test_execute_nonexistent_tool(self, tool_registry):
        """Test executing a tool that doesn't exist."""
        with pytest.raises(ValueError, match="Tool 'nonexistent' not found"):
            await tool_registry.execute_tool("nonexistent")
    
    @pytest.mark.asyncio
    async def test_execute_tool_with_validation_error(self, tool_registry):
        """Test executing a tool with invalid input."""
        tool = SimpleMCPTool("validation_test")
        tool_registry.register_tool(tool)
        
        with pytest.raises(ValueError, match="Missing required parameter"):
            await tool_registry.execute_tool("validation_test")  # Missing 'text' parameter
    
    @pytest.mark.asyncio
    async def test_execute_tool_with_execution_error(self, tool_registry):
        """Test executing a tool that throws an error."""
        tool = ErrorMCPTool()
        tool_registry.register_tool(tool)
        
        # Should not raise - execution errors are caught by the tool
        with pytest.raises(ValueError, match="Intentional test error"):
            await tool_registry.execute_tool("error_tool", should_error=True)


class TestFunctionRegistration:
    """Test registering regular functions as tools."""
    
    def test_register_simple_function(self, tool_registry):
        """Test registering a simple function."""
        def simple_func(text: str) -> str:
            return f"Result: {text}"
        
        tool_registry.register_function_as_tool(simple_func)
        
        assert "simple_func" in tool_registry.tools
        schema = tool_registry.get_tool_schema("simple_func")
        assert schema.name == "simple_func"
        assert "text" in schema.input_schema["properties"]
    
    def test_register_function_with_custom_name(self, tool_registry):
        """Test registering a function with custom name and description."""
        def my_function(x: int, y: int = 5) -> int:
            return x + y
        
        tool_registry.register_function_as_tool(
            my_function,
            name="add_numbers",
            description="Add two numbers together"
        )
        
        assert "add_numbers" in tool_registry.tools
        schema = tool_registry.get_tool_schema("add_numbers")
        assert schema.name == "add_numbers"
        assert schema.description == "Add two numbers together"
    
    @pytest.mark.asyncio
    async def test_execute_registered_function(self, tool_registry):
        """Test executing a registered function."""
        def multiply(a: int, b: int) -> int:
            return a * b
        
        tool_registry.register_function_as_tool(multiply)
        
        result = await tool_registry.execute_tool("multiply", a=6, b=7)
        assert result == 42
    
    @pytest.mark.asyncio
    async def test_execute_async_function(self, tool_registry):
        """Test executing an async function."""
        async def async_func(message: str) -> Dict[str, Any]:
            await asyncio.sleep(0.01)  # Simulate async work
            return {"processed": message, "async": True}
        
        tool_registry.register_function_as_tool(async_func)
        
        result = await tool_registry.execute_tool("async_func", message="hello")
        assert result["processed"] == "hello"
        assert result["async"] is True


class TestToolDecorator:
    """Test the @mcp_tool decorator."""
    
    def test_decorated_function_has_config(self):
        """Test that decorated function has config attribute."""
        @mcp_tool(name="decorated_test", description="Test decoration")
        def test_func():
            return "test"
        
        assert hasattr(test_func, '_mcp_tool_config')
        config = test_func._mcp_tool_config
        assert config['name'] == "decorated_test"
        assert config['description'] == "Test decoration"
    
    def test_decorator_with_schema(self):
        """Test decorator with custom input schema."""
        custom_schema = {
            "type": "object",
            "properties": {
                "value": {"type": "number"}
            },
            "required": ["value"]
        }
        
        @mcp_tool(
            name="schema_test",
            description="Test with schema",
            input_schema=custom_schema
        )
        def schema_func(value: float) -> float:
            return value * 2
        
        config = schema_func._mcp_tool_config
        assert config['input_schema'] == custom_schema
    
    def test_register_decorated_function(self, tool_registry):
        """Test registering a decorated function."""
        @mcp_tool(name="decorated_register")
        def decorated_func(text: str) -> str:
            return text.upper()
        
        tool_registry.register_function_as_tool(decorated_func)
        
        assert "decorated_register" in tool_registry.tools
        schema = tool_registry.get_tool_schema("decorated_register")
        assert schema.name == "decorated_register"


class TestSchemaGeneration:
    """Test automatic schema generation from function signatures."""
    
    def test_simple_function_schema(self, tool_registry):
        """Test schema generation for simple function."""
        def simple(text: str, count: int) -> str:
            return text * count
        
        tool_registry.register_function_as_tool(simple)
        schema = tool_registry.get_tool_schema("simple")
        
        properties = schema.input_schema["properties"]
        assert "text" in properties
        assert "count" in properties
        assert properties["text"]["type"] == "string"
        assert properties["count"]["type"] == "integer"
        assert schema.input_schema["required"] == ["text", "count"]
    
    def test_function_with_defaults_schema(self, tool_registry):
        """Test schema generation for function with default values."""
        def with_defaults(name: str, age: int = 25, active: bool = True) -> dict:
            return {"name": name, "age": age, "active": active}
        
        tool_registry.register_function_as_tool(with_defaults)
        schema = tool_registry.get_tool_schema("with_defaults")
        
        # Only parameters without defaults should be required
        assert schema.input_schema["required"] == ["name"]
        
        properties = schema.input_schema["properties"]
        assert properties["name"]["type"] == "string"
        assert properties["age"]["type"] == "integer"
        assert properties["active"]["type"] == "boolean"
    
    def test_complex_types_schema(self, tool_registry):
        """Test schema generation for complex types."""
        def complex_types(items: list, config: dict, rate: float) -> dict:
            return {"processed": len(items), "config": config, "rate": rate}
        
        tool_registry.register_function_as_tool(complex_types)
        schema = tool_registry.get_tool_schema("complex_types")
        
        properties = schema.input_schema["properties"]
        assert properties["items"]["type"] == "array"
        assert properties["config"]["type"] == "object"
        assert properties["rate"]["type"] == "number"


class TestErrorHandling:
    """Test error handling in the tool system."""
    
    @pytest.mark.asyncio
    async def test_tool_execution_error(self, tool_registry):
        """Test handling of tool execution errors."""
        def error_func():
            raise RuntimeError("Tool execution failed")
        
        tool_registry.register_function_as_tool(error_func)
        
        with pytest.raises(RuntimeError, match="Tool execution failed"):
            await tool_registry.execute_tool("error_func")
    
    def test_invalid_tool_registration(self, tool_registry):
        """Test registering invalid tools."""
        # This should work - registry should be flexible
        class InvalidTool:
            pass
        
        # Should not crash, but tool won't work properly
        try:
            tool_registry.register_tool_class(InvalidTool)
        except Exception:
            pass  # Expected to fail
    
    def test_schema_validation_edge_cases(self):
        """Test schema validation with edge cases."""
        tool = SimpleMCPTool()
        
        # Empty input should fail if required params exist
        with pytest.raises(ValueError):
            tool.validate_input()
        
        # Extra parameters should be allowed
        assert tool.validate_input(text="valid", extra_param="ignored") is True