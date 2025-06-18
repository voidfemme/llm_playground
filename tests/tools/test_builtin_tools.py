"""
Tests for built-in MCP tools.
"""

import pytest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime

from chatbot_library.tools.builtin_tools import (
    TimeTool, WeatherTool, CalculatorTool, 
    count_text_length, encode_base64, decode_base64,
    register_builtin_tools
)
from chatbot_library.tools.mcp_tool_registry import MCPToolRegistry


class TestTimeTool:
    """Test the TimeTool implementation."""
    
    @pytest.mark.asyncio
    async def test_default_time_format(self):
        """Test default readable time format."""
        tool = TimeTool()
        result = await tool.execute()
        
        # Should return readable format by default
        assert isinstance(result, str)
        assert len(result) > 10  # Should be a full datetime string
        # Check basic format (YYYY-MM-DD HH:MM:SS)
        parts = result.split()
        assert len(parts) == 2  # Date and time parts
        assert '-' in parts[0]  # Date has dashes
        assert ':' in parts[1]  # Time has colons
    
    @pytest.mark.asyncio
    async def test_iso_time_format(self):
        """Test ISO time format."""
        tool = TimeTool()
        result = await tool.execute(format="iso")
        
        assert isinstance(result, str)
        assert 'T' in result  # ISO format has T separator
    
    @pytest.mark.asyncio
    async def test_timestamp_format(self):
        """Test timestamp format."""
        tool = TimeTool()
        result = await tool.execute(format="timestamp")
        
        assert isinstance(result, str)
        assert result.isdigit()  # Should be numeric string
        
        # Should be reasonable timestamp (not too old or too far in future)
        timestamp = int(result)
        assert timestamp > 1600000000  # After 2020
        assert timestamp < 2000000000  # Before 2033
    
    def test_time_tool_schema(self):
        """Test TimeTool schema."""
        tool = TimeTool()
        schema = tool.get_schema()
        
        assert schema.name == "get_current_time"
        assert "time" in schema.description.lower()
        assert schema.input_schema["type"] == "object"
        
        properties = schema.input_schema["properties"]
        assert "format" in properties
        assert "timezone" in properties
        
        # Check enum values for format
        assert "iso" in properties["format"]["enum"]
        assert "readable" in properties["format"]["enum"]
        assert "timestamp" in properties["format"]["enum"]


class TestCalculatorTool:
    """Test the CalculatorTool implementation."""
    
    @pytest.mark.asyncio
    async def test_simple_calculation(self):
        """Test simple arithmetic."""
        tool = CalculatorTool()
        result = await tool.execute("2 + 3")
        
        assert result["result"] == 5.0
        assert result["expression"] == "2 + 3"
        assert result["formatted_result"] == "5.00"
    
    @pytest.mark.asyncio
    async def test_complex_calculation(self):
        """Test more complex arithmetic."""
        tool = CalculatorTool()
        result = await tool.execute("(10 + 5) * 2 - 8")
        
        assert result["result"] == 22.0
        assert result["expression"] == "(10 + 5) * 2 - 8"
    
    @pytest.mark.asyncio
    async def test_precision_control(self):
        """Test precision control."""
        tool = CalculatorTool()
        result = await tool.execute("22 / 7", precision=4)
        
        assert abs(result["result"] - 3.142857142857143) < 0.001
        assert result["formatted_result"] == "3.1429"
    
    @pytest.mark.asyncio
    async def test_zero_precision(self):
        """Test zero precision (integer result)."""
        tool = CalculatorTool()
        result = await tool.execute("22 / 7", precision=0)
        
        assert result["formatted_result"] == "3"
    
    @pytest.mark.asyncio
    async def test_division_by_zero(self):
        """Test division by zero handling."""
        tool = CalculatorTool()
        
        with pytest.raises(ValueError, match="Calculation error"):
            await tool.execute("5 / 0")
    
    @pytest.mark.asyncio
    async def test_invalid_expression(self):
        """Test invalid expression handling."""
        tool = CalculatorTool()
        
        with pytest.raises(ValueError, match="Invalid expression"):
            await tool.execute("import os")
    
    @pytest.mark.asyncio
    async def test_allowed_functions(self):
        """Test that allowed functions work."""
        tool = CalculatorTool()
        
        result = await tool.execute("abs(-5)")
        assert result["result"] == 5.0
        
        result = await tool.execute("max(3, 7, 2)")
        assert result["result"] == 7.0
        
        result = await tool.execute("pow(2, 3)")
        assert result["result"] == 8.0
    
    def test_calculator_tool_schema(self):
        """Test CalculatorTool schema."""
        tool = CalculatorTool()
        schema = tool.get_schema()
        
        assert schema.name == "calculate"
        assert "mathematical" in schema.description.lower()
        
        properties = schema.input_schema["properties"]
        assert "expression" in properties
        assert "precision" in properties
        assert properties["precision"]["minimum"] == 0
        assert properties["precision"]["maximum"] == 10


class TestWeatherTool:
    """Test the WeatherTool implementation."""
    
    @pytest.mark.asyncio
    async def test_weather_without_api_key(self):
        """Test weather tool without API key."""
        tool = WeatherTool()
        
        with pytest.raises(ValueError, match="Weather API key is required"):
            await tool.execute("London, UK")
    
    @pytest.mark.asyncio
    @patch('requests.get')
    async def test_weather_success(self, mock_get):
        """Test successful weather API call."""
        # Mock the API response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "main": {"temp": 20.5, "humidity": 65},
            "weather": [{"description": "partly cloudy"}]
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        tool = WeatherTool(api_key="test_key")
        result = await tool.execute("London, UK")
        
        assert result["temperature"] == 20.5
        assert result["description"] == "partly cloudy"
        assert result["humidity"] == 65
        assert result["location"] == "London, UK"
        assert result["unit"] == "celsius"
    
    @pytest.mark.asyncio
    @patch('requests.get')
    async def test_weather_fahrenheit(self, mock_get):
        """Test weather in Fahrenheit."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "main": {"temp": 68.9, "humidity": 60},
            "weather": [{"description": "sunny"}]
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        tool = WeatherTool(api_key="test_key")
        result = await tool.execute("New York, US", unit="fahrenheit")
        
        assert result["temperature"] == 68.9
        assert result["unit"] == "fahrenheit"
    
    @pytest.mark.asyncio
    @patch('requests.get')
    async def test_weather_api_error(self, mock_get):
        """Test weather API error handling."""
        mock_get.side_effect = Exception("API Error")
        
        tool = WeatherTool(api_key="test_key")
        
        with pytest.raises(ValueError, match="Failed to fetch weather data"):
            await tool.execute("Invalid Location")
    
    def test_weather_tool_schema(self):
        """Test WeatherTool schema."""
        tool = WeatherTool(api_key="test")
        schema = tool.get_schema()
        
        assert schema.name == "get_weather"
        assert "weather" in schema.description.lower()
        
        properties = schema.input_schema["properties"]
        assert "location" in properties
        assert "unit" in properties
        assert "celsius" in properties["unit"]["enum"]
        assert "fahrenheit" in properties["unit"]["enum"]
        
        # Check output schema
        assert schema.output_schema is not None
        output_props = schema.output_schema["properties"]
        assert "temperature" in output_props
        assert "description" in output_props


class TestDecoratorBasedTools:
    """Test decorator-based tool functions."""
    
    @pytest.mark.asyncio
    async def test_count_text_length(self):
        """Test text length counting tool."""
        result = await count_text_length("Hello world")
        
        assert result["text"] == "Hello world"
        assert result["character_count"] == 11
        assert result["word_count"] == 2
        assert result["include_spaces"] is True
    
    @pytest.mark.asyncio
    async def test_count_text_length_no_spaces(self):
        """Test text length without spaces."""
        result = await count_text_length("Hello world!", include_spaces=False)
        
        assert result["character_count"] == 11  # Excluding space
        assert result["include_spaces"] is False
    
    @pytest.mark.asyncio
    async def test_encode_base64(self):
        """Test base64 encoding."""
        result = await encode_base64("Hello, World!")
        
        # Verify it's valid base64
        import base64
        decoded = base64.b64decode(result).decode('utf-8')
        assert decoded == "Hello, World!"
    
    @pytest.mark.asyncio
    async def test_decode_base64(self):
        """Test base64 decoding."""
        # Encode first
        encoded = await encode_base64("Test message")
        # Then decode
        decoded = await decode_base64(encoded)
        
        assert decoded == "Test message"
    
    @pytest.mark.asyncio
    async def test_decode_invalid_base64(self):
        """Test invalid base64 decoding."""
        with pytest.raises(ValueError, match="Invalid base64 encoding"):
            await decode_base64("invalid_base64!")


class TestBuiltinToolRegistration:
    """Test the registration of all built-in tools."""
    
    def test_register_builtin_tools_without_weather(self):
        """Test registering built-in tools without weather API key."""
        registry = MCPToolRegistry()
        register_builtin_tools(registry)
        
        tools = registry.list_tools()
        
        # Should have time and calculator tools
        assert "get_current_time" in tools
        assert "calculate" in tools
        
        # Should have decorator-based tools
        assert "text_length" in tools
        assert "encode_base64" in tools
        assert "decode_base64" in tools
        
        # Should not have weather tool without API key
        assert "get_weather" not in tools
    
    def test_register_builtin_tools_with_weather(self):
        """Test registering built-in tools with weather API key."""
        registry = MCPToolRegistry()
        register_builtin_tools(registry, weather_api_key="test_key")
        
        tools = registry.list_tools()
        
        # Should have all tools including weather
        assert "get_current_time" in tools
        assert "calculate" in tools
        assert "get_weather" in tools
        assert "text_length" in tools
    
    @pytest.mark.asyncio
    async def test_execute_builtin_tools(self):
        """Test executing built-in tools through registry."""
        registry = MCPToolRegistry()
        register_builtin_tools(registry)
        
        # Test time tool
        time_result = await registry.execute_tool("get_current_time")
        assert isinstance(time_result, str)
        
        # Test calculator
        calc_result = await registry.execute_tool("calculate", expression="5 + 3")
        assert calc_result["result"] == 8.0
        
        # Test text length
        text_result = await registry.execute_tool("text_length", text="test")
        assert text_result["character_count"] == 4


class TestToolMetadata:
    """Test tool metadata and categories."""
    
    def test_time_tool_metadata(self):
        """Test time tool metadata."""
        tool = TimeTool()
        schema = tool.get_schema()
        
        assert schema.metadata is not None
        assert schema.metadata["category"] == "datetime"
        assert schema.metadata["cost"] == 0
        assert schema.metadata["latency"] == "low"
    
    def test_calculator_tool_metadata(self):
        """Test calculator tool metadata."""
        tool = CalculatorTool()
        schema = tool.get_schema()
        
        assert schema.metadata["category"] == "math"
        assert schema.metadata["cost"] == 0
    
    def test_weather_tool_metadata(self):
        """Test weather tool metadata."""
        tool = WeatherTool(api_key="test")
        schema = tool.get_schema()
        
        assert schema.metadata["category"] == "weather"
        assert schema.metadata["requires_api_key"] is True
        assert schema.metadata["cost"] == 0.001


class TestAsyncToolExecution:
    """Test async behavior of tools."""
    
    @pytest.mark.asyncio
    async def test_concurrent_tool_execution(self):
        """Test running multiple tools concurrently."""
        time_tool = TimeTool()
        calc_tool = CalculatorTool()
        
        # Run tools concurrently
        results = await asyncio.gather(
            time_tool.execute(),
            calc_tool.execute("10 * 2"),
            calc_tool.execute("5 + 5")
        )
        
        assert len(results) == 3
        assert isinstance(results[0], str)  # Time result
        assert results[1]["result"] == 20.0  # Calc result 1
        assert results[2]["result"] == 10.0  # Calc result 2
    
    @pytest.mark.asyncio
    async def test_tool_execution_timing(self):
        """Test that tool execution is reasonably fast."""
        import time
        
        calc_tool = CalculatorTool()
        
        start_time = time.time()
        await calc_tool.execute("1 + 1")
        execution_time = time.time() - start_time
        
        # Should be very fast for simple calculation
        assert execution_time < 0.1  # Less than 100ms