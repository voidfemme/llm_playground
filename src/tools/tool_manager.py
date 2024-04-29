# src/chatbots/tools/tool_manager.py

from dataclasses import dataclass, field
import re
from typing import Any, Callable

from anthropic.types.beta.tools import ToolUseBlock
from src.tools.tools import generate_image, get_current_time, get_weather


@dataclass
class ToolSchema:
    fields: dict[str, dict[str, Any]] = field(default_factory=dict)

    def add_field(
        self, name: str, field_type: str, description: str, required: bool = False
    ) -> None:
        self.fields[name] = {
            "type": field_type,
            "description": description,
            "required": required,
        }

    def remove_field(self, name: str) -> None:
        self.fields.pop(name, None)

    def get_field(self, name: str) -> dict[str, Any] | None:
        return self.fields.get(name)

    def serialize(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {name: field for name, field in self.fields.items()},
            "required": [
                name
                for name, field in self.fields.items()
                if field.get("required", False)
            ],
        }


@dataclass
class Tool:
    """
    A dataclass representing a tool that can be used by the chatbot.

    Attributes:
        name (str): The name of the tool.
        description (str): A description of the tool.
        input_schema (dict[str, Any]): The schema defining the input parameters for the tool.
        function (Callable[..., Any]): The function associated with the tool.
        api_key (str, optional): The API key required for the tool, if applicable. Defaults to None.

    Methods:
        to_dict() -> dict[str, Any]: Converts the Tool instance to a dictionary representation.
        execute(**kwargs) -> Any: Executes the tool's function with the provided keyword arguments.
    """

    name: str
    description: str
    input_schema: ToolSchema
    function: Callable[..., Any]
    api_key: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self.input_schema.serialize(),
        }

    def execute(self, **kwargs) -> Any:
        return self.function(**kwargs)


class ToolManager:
    def __init__(self):
        self.tools: dict[str, Tool] = {}
        self.favorites: set[str] = set()
        self.active_tools: set[str] = set()
        self.load_default_tools()

    def add_to_favorites(self, tool_name: str) -> None:
        """Adds a tool to the list of favorites"""
        if tool_name in self.tools:
            self.favorites.add(tool_name)
        else:
            raise ValueError(f"Tool not found: {tool_name}")

    def remove_from_favorites(self, tool_name: str) -> None:
        """Removes a tool from the list of favorites."""
        self.favorites.discard(tool_name)

    def activate_tool(self, tool_name: str) -> None:
        """Activates a tool for use."""
        if len(self.active_tools) >= 10:
            raise Exception("Maximum number of active tools reached.")
        if tool_name in self.tools:
            self.active_tools.add(tool_name)
        else:
            raise ValueError(f"Tool not found: {tool_name}")

    def deactivate_tool(self, tool_name: str) -> None:
        """Deactivates a tool."""
        self.active_tools.discard(tool_name)

    def get_favorites(self) -> list[Tool]:
        """Returns a list of favorite tools."""
        return [self.tools[name] for name in self.favorites if name in self.tools]

    def get_active_tools(self) -> list[Tool]:
        """Returns a list of active tools."""
        return [self.tools[name] for name in self.active_tools if name in self.tools]

    def register_tool(self, tool: Tool) -> None:
        # Include parameters for generating the full schema required by my chatbots
        if not self._is_valid_tool_name(tool.name):
            raise ValueError(
                f"Invalid tool name: {tool.name}. "
                "Tool name must match the regex ^[a-zA-Z0-9_-]{{1,64}}$"
            )
        self.tools[tool.name] = tool

    def get_tool(self, name: str) -> Tool:
        tool = self.tools.get(name)
        if not tool:
            raise ValueError(f"Tool not found: {name}")
        return tool

    def execute_tool(self, name: str, **kwargs) -> Any:
        tool = self.get_tool(name)
        if tool.api_key:
            kwargs["api_key"] = tool.api_key
        return tool.execute(**kwargs)

    def get_tools_schema(self) -> list[dict[str, Any]]:
        return [tool.to_dict() for tool in self.tools.values()]

    def get_tools_list(self) -> list[Tool]:
        """
        Returns a list of tool dictionaries.

        Returns:
            list[dict[str, Any]]: A list of tool dictionaries
        """
        return list(self.tools.values())

    def process_tool_use(self, tool_use_block: ToolUseBlock) -> dict[str, Any]:
        """
        Process a tool use request from the chatbot.
        Args:
            tool_use_block: The ToolUseBlock object representing the tool use request from \
                    Anthropic.

        Returns:
            A dictionary representing the tool result messasge to be appneded to the conversation \
                    history.
        """
        tool_name = tool_use_block.name
        tool_input = tool_use_block.input
        tool_use_id = tool_use_block.id

        try:
            # Execute the specified tool using the ToolManager
            tool_result = self.execute_tool(tool_name, **tool_input)  # type: ignore

            # Create the tool result message
            return {
                "role": "user",
                "content": [
                    {
                        "type": "tool_result",
                        "tool_use_id": tool_use_id,
                        "content": tool_result,
                    }
                ],
            }
        except Exception as e:
            error_message = f"Error executing tool '{tool_name}': {str(e)}"
            return {
                "role": "user",
                "content": [
                    {
                        "type": "tool_result",
                        "tool_use_id": tool_use_id,
                        "content": error_message,
                        "is_error": True,
                    }
                ],
            }

    def register_custom_tool(
        self,
        name: str,
        description: str,
        input_schema: dict[str, Any],
        function: Callable[..., Any],
        api_key: str | None = None,
    ) -> None:
        """
        Register a custom tool with the ToolManager.

        Args:
            name (str): The name of the custom tool.
            description (str): A description of the custom tool.
            input_schema (dict[str, Any]): The schema defining the input parameters for the custom \
                    tool.
            function (Callable[..., Any]): The function associated with the custom tool.
            api_key (str, optional): The API key required for the custom tool, if applicable. \
                Defaults to None.
        """
        tool_schema = ToolSchema()
        for field_name, field_info in input_schema.items():
            tool_schema.add_field(
                field_name,
                field_info["type"],
                field_info["description"],
                field_info.get("required", False),
            )

        custom_tool = Tool(
            name=name,
            description=description,
            input_schema=tool_schema,
            function=function,
            api_key=api_key,
        )
        self.register_tool(custom_tool)

    @staticmethod
    def _is_valid_tool_name(name: str) -> bool:
        return bool(re.match(r"^[a-zA-Z0-9_-]{1,64}$", name))

    def load_default_tools(self):
        get_current_time_schema = ToolSchema()
        get_weather_schema = ToolSchema()
        generate_image_schema = ToolSchema()

        get_weather_schema.add_field(
            "location",
            "string",
            "The location of the format 'City, Country Code' (e.g., 'London, UK')",
            required=True,
        )
        get_weather_schema.add_field(
            "unit",
            "string",
            "The unit of temperature, either 'celsius' or 'fahrenheit'",
            required=False,
        )

        generate_image_schema.add_field(
            "model",
            "string",
            "The DALL-E model to use, either 'dall-e-2' or 'dall-e-3'",
            required=True,
        )
        generate_image_schema.add_field(
            "prompt",
            "string",
            "The text prompt describing the desired image",
            required=True,
        )
        generate_image_schema.add_field(
            "size",
            "string",
            "The dimensions of the generated image (e.g. '1024x1024', '1024x1792', '1792x1024')",
            required=False,
        )
        generate_image_schema.add_field(
            "quality",
            "string",
            "The quality of the generated image, either 'standard' or 'hd' (DALL-E 3 only)",
            required=False,
        )
        generate_image_schema.add_field(
            "n",
            "integer",
            "The number of images to generate(1 to 10)",
            required=False,
        )

        default_tools = [
            Tool(
                name="get_current_time",
                description=get_current_time.__doc__,  # type: ignore
                input_schema=get_current_time_schema,
                function=get_current_time,
            ),
            Tool(
                name="get_weather",
                description=get_weather.__doc__,  # type: ignore
                input_schema=get_weather_schema,
                function=get_weather,
            ),
            Tool(
                name="generate_image",
                description=generate_image.__doc__,  # type: ignore
                input_schema=generate_image_schema,
                function=generate_image,
            ),
        ]

        for tool in default_tools:
            self.register_tool(tool)
