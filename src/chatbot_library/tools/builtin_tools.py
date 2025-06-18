"""
Built-in MCP-compatible tools for the chatbot library.
"""

import asyncio
from datetime import datetime
from typing import Optional, Dict, Any
import json

try:
    import requests
except ImportError:
    requests = None

try:
    import openai
except ImportError:
    openai = None

from .mcp_tool_registry import MCPTool, MCPToolSchema, mcp_tool


class TimeTool(MCPTool):
    """Get current date and time."""
    
    def get_schema(self) -> MCPToolSchema:
        return MCPToolSchema(
            name="get_current_time",
            description="Get the current date and time in ISO format",
            input_schema={
                "type": "object",
                "properties": {
                    "timezone": {
                        "type": "string",
                        "description": "Timezone (optional, defaults to local)",
                        "default": "local"
                    },
                    "format": {
                        "type": "string", 
                        "description": "Time format (iso, readable, timestamp)",
                        "enum": ["iso", "readable", "timestamp"],
                        "default": "readable"
                    }
                },
                "required": []
            },
            metadata={
                "category": "datetime",
                "cost": 0,
                "latency": "low"
            }
        )
    
    async def execute(self, timezone: str = "local", format: str = "readable") -> str:
        """Execute the time tool."""
        now = datetime.now()
        
        if format == "iso":
            return now.isoformat()
        elif format == "timestamp":
            return str(int(now.timestamp()))
        else:  # readable
            return now.strftime("%Y-%m-%d %H:%M:%S")


class WeatherTool(MCPTool):
    """Get current weather for a location."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
    
    def get_schema(self) -> MCPToolSchema:
        return MCPToolSchema(
            name="get_weather",
            description="Get current weather information for a location",
            input_schema={
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "Location in format 'City, Country' (e.g., 'London, UK')"
                    },
                    "unit": {
                        "type": "string",
                        "description": "Temperature unit",
                        "enum": ["celsius", "fahrenheit"],
                        "default": "celsius"
                    }
                },
                "required": ["location"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "temperature": {"type": "number"},
                    "description": {"type": "string"},
                    "humidity": {"type": "number"},
                    "location": {"type": "string"}
                }
            },
            metadata={
                "category": "weather",
                "requires_api_key": True,
                "cost": 0.001,
                "latency": "medium"
            }
        )
    
    async def execute(self, location: str, unit: str = "celsius") -> Dict[str, Any]:
        """Execute the weather tool."""
        if not self.api_key:
            raise ValueError("Weather API key is required")
        
        if not requests:
            raise ValueError("requests library is required for weather tool")
        
        base_url = "http://api.openweathermap.org/data/2.5/weather"
        units = "imperial" if unit == "fahrenheit" else "metric"
        
        params = {
            "q": location,
            "appid": self.api_key,
            "units": units
        }
        
        try:
            # Use asyncio to make the request non-blocking
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None, 
                lambda: requests.get(base_url, params=params, timeout=10)
            )
            response.raise_for_status()
            
            data = response.json()
            
            return {
                "temperature": data["main"]["temp"],
                "description": data["weather"][0]["description"],
                "humidity": data["main"]["humidity"],
                "location": location,
                "unit": unit
            }
            
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Failed to fetch weather data: {e}")


class CalculatorTool(MCPTool):
    """Perform mathematical calculations."""
    
    def get_schema(self) -> MCPToolSchema:
        return MCPToolSchema(
            name="calculate",
            description="Perform mathematical calculations safely",
            input_schema={
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "Mathematical expression to evaluate (e.g., '2 + 3 * 4')"
                    },
                    "precision": {
                        "type": "integer",
                        "description": "Number of decimal places for the result",
                        "default": 2,
                        "minimum": 0,
                        "maximum": 10
                    }
                },
                "required": ["expression"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "result": {"type": "number"},
                    "expression": {"type": "string"},
                    "formatted_result": {"type": "string"}
                }
            },
            metadata={
                "category": "math",
                "cost": 0,
                "latency": "low"
            }
        )
    
    async def execute(self, expression: str, precision: int = 2) -> Dict[str, Any]:
        """Execute the calculator tool."""
        # Sanitize the expression to prevent code injection
        allowed_chars = set('0123456789+-*/.() ')
        allowed_functions = {'abs', 'round', 'min', 'max', 'pow'}
        
        # Basic sanitization
        sanitized = ''.join(c for c in expression if c in allowed_chars)
        
        if not sanitized.strip():
            raise ValueError("Invalid mathematical expression")
        
        try:
            # Use eval with restricted environment for safety
            allowed_names = {
                "__builtins__": {},
                "abs": abs,
                "round": round,
                "min": min,
                "max": max,
                "pow": pow
            }
            
            result = eval(sanitized, allowed_names, {})
            
            if not isinstance(result, (int, float)):
                raise ValueError("Expression must evaluate to a number")
            
            formatted_result = f"{result:.{precision}f}" if precision > 0 else str(int(result))
            
            return {
                "result": float(result),
                "expression": expression,
                "formatted_result": formatted_result
            }
            
        except (ValueError, ZeroDivisionError, OverflowError) as e:
            raise ValueError(f"Calculation error: {e}")
        except Exception as e:
            raise ValueError(f"Invalid expression: {e}")


# Example of using the decorator for simple functions
@mcp_tool(
    name="text_length",
    description="Count the number of characters in a text string",
    input_schema={
        "type": "object",
        "properties": {
            "text": {
                "type": "string",
                "description": "The text to count characters for"
            },
            "include_spaces": {
                "type": "boolean", 
                "description": "Whether to include spaces in the count",
                "default": True
            }
        },
        "required": ["text"]
    }
)
async def count_text_length(text: str, include_spaces: bool = True) -> Dict[str, Any]:
    """Count characters in text."""
    if include_spaces:
        count = len(text)
    else:
        count = len(text.replace(' ', ''))
    
    return {
        "text": text,
        "character_count": count,
        "include_spaces": include_spaces,
        "word_count": len(text.split())
    }


@mcp_tool(
    name="encode_base64",
    description="Encode text to base64 format"
)
async def encode_base64(text: str) -> str:
    """Encode text to base64."""
    import base64
    encoded_bytes = base64.b64encode(text.encode('utf-8'))
    return encoded_bytes.decode('utf-8')


@mcp_tool(
    name="decode_base64", 
    description="Decode base64 text to plain text"
)
async def decode_base64(encoded_text: str) -> str:
    """Decode base64 to text."""
    import base64
    try:
        decoded_bytes = base64.b64decode(encoded_text.encode('utf-8'))
        return decoded_bytes.decode('utf-8')
    except Exception as e:
        raise ValueError(f"Invalid base64 encoding: {e}")


# Tool factory for registering all built-in tools
def register_builtin_tools(registry, weather_api_key: Optional[str] = None):
    """Register all built-in tools with the registry."""
    
    # Register class-based tools
    registry.register_tool(TimeTool())
    registry.register_tool(CalculatorTool())
    
    if weather_api_key:
        registry.register_tool(WeatherTool(api_key=weather_api_key))
    
    # Function-based tools are automatically discovered if using discovery
    # Or manually register them:
    registry.register_function_as_tool(count_text_length)
    registry.register_function_as_tool(encode_base64)
    registry.register_function_as_tool(decode_base64)