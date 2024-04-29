from datetime import datetime
from typing import Any
import anthropic
from anthropic.types.beta.tools import ToolsBetaMessage
from src.chatbots.adapters.chatbot_adapter import ChatbotAdapter, ChatbotParameters
from src.model.conversation_dataclasses import Message, Response, ToolResponse, ToolUse
from src.tools.tool_manager import Tool
from src.utils.error_handling import InvalidMessageError, ModelNotSupportedError
from src.utils.file_logger import (
    CHATBOT_LOG_FILE_PATH,
    log_function_call,
    log_json_content,
    log_to_file,
    log_variable,
)


class AnthropicAdapter(ChatbotAdapter):
    def __init__(self, parameters: ChatbotParameters) -> None:
        super().__init__(parameters)
        self.client = anthropic.Anthropic()

    @staticmethod
    def supported_models() -> list[str]:
        return [
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307",
        ]

    @staticmethod
    def models_supporting_tools() -> list[str]:
        return [
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
        ]

    @staticmethod
    def models_supporting_image_understanding() -> list[str]:
        return [
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307",
        ]

    def send_message_with_tools(
        self, messages: list[Message], active_tools: list[Tool]
    ) -> Response:
        log_function_call(
            CHATBOT_LOG_FILE_PATH,
            "AnthropicAdapter.send_message_with_tools",
            messages=messages,
            active_tools=active_tools,
        )
        if self.parameters.model_name not in self.models_supporting_tools():
            supported_models = ", ".join(self.models_supporting_tools())
            raise ModelNotSupportedError(
                f"Model {self.parameters.model_name} does not support function calling.\n"
                f"Models that support function calling: {supported_models}"
            )
        api_messages = self._prepare_api_messages(messages)
        tools_schema = self._prepare_tool_schema(active_tools)

        try:
            log_json_content(
                CHATBOT_LOG_FILE_PATH, [tool.to_dict() for tool in active_tools]
            )
            anthropic_message = self.client.beta.tools.messages.create(
                model=self.parameters.model_name,
                system=self.parameters.system_message,
                max_tokens=self.parameters.max_tokens,
                tools=tools_schema,  # type: ignore
                messages=api_messages,  # type: ignore
                stop_sequences=self.parameters.stop_sequences,
                temperature=self.parameters.temperature,
            )

        except RuntimeError as e:
            # Handle API request errors and return an appropriate error response
            status_code = getattr(e, "status_code", None)
            error_message = str(e)
            return self._get_api_error_response(status_code, error_message)

        # Check if the API response indicates a tool use
        if anthropic_message.stop_reason == "tool_use":
            try:
                # Handle the tool activation, append the tool use/result and make a subsequent API
                # request
                self._handle_tool_activation(
                    tool_use_message=anthropic_message,
                    tools=active_tools,
                    messages=messages,
                )
                api_messages = self._prepare_api_messages(messages)
                anthropic_message = self.client.beta.tools.messages.create(
                    model=self.parameters.model_name,
                    system=self.parameters.system_message,
                    max_tokens=self.parameters.max_tokens,
                    tools=tools_schema,  # type: ignore
                    messages=api_messages,  # type: ignore
                    stop_sequences=self.parameters.stop_sequences,
                    temperature=self.parameters.temperature,
                )
            except (ValueError, RuntimeError) as e:
                log_variable(
                    CHATBOT_LOG_FILE_PATH, "Error during tool activation", str(e)
                )
                return self._get_api_error_response(None, str(e))

        # Check if the final API response contains valid content
        if anthropic_message.content and anthropic_message.content[0].text:  # type: ignore
            return Response(
                id=anthropic_message.id,
                model=anthropic_message.model,
                text=anthropic_message.content[0].text,  # type: ignore
                timestamp=datetime.now(),
            )
        else:
            log_to_file(CHATBOT_LOG_FILE_PATH, "Empty or missing response content.")
            return Response(
                id=anthropic_message.id,
                model=anthropic_message.model,
                text="No valid response generated.",
                timestamp=datetime.now(),
                is_error=True,
            )

    def send_message_without_tools(self, messages: list[Message]) -> Response:
        log_function_call(
            CHATBOT_LOG_FILE_PATH,
            "AnthropicAdapter.send_message_without_tools",
            messages=messages,
        )
        if self.parameters.model_name not in self.supported_models():
            supported_models = ", ".join(self.supported_models())
            raise ModelNotSupportedError(
                f"Model '{self.parameters.model_name}' not supported by AnthropicAdapter.\n"
                f"Supported models: {supported_models}"
            )

        api_messages = self._prepare_api_messages(messages)
        log_json_content(CHATBOT_LOG_FILE_PATH, api_messages)

        try:
            # Perform the API request to send messages and get a Response
            anthropic_message = self.client.messages.create(
                model=self.parameters.model_name,
                system=self.parameters.system_message,
                max_tokens=self.parameters.max_tokens,
                messages=api_messages,  # type: ignore
                stop_sequences=self.parameters.stop_sequences,
                temperature=self.parameters.temperature,
            )
            log_variable(CHATBOT_LOG_FILE_PATH, "anthropic_message", anthropic_message)

            # Check if the response contains text and return accordingly
            if anthropic_message.content[0].text:
                return Response(
                    id=anthropic_message.id,
                    model=anthropic_message.model,
                    text=anthropic_message.content[0].text,
                    timestamp=datetime.now(),
                )
            else:
                # Log and handle empty respoinses from the API
                log_variable(CHATBOT_LOG_FILE_PATH, "Empty Response", anthropic_message)
                return Response(
                    id=anthropic_message.id,
                    model=anthropic_message.model,
                    text="Error: Empty response from model",
                    timestamp=datetime.now(),
                    is_error=True,
                )
        except Exception as e:
            log_variable(CHATBOT_LOG_FILE_PATH, "Exception", str(e))
            status_code = getattr(e, "status_code", None)
            error_message = str(e)
            return self._get_api_error_response(status_code, error_message)

    def _handle_tool_activation(
        self,
        tool_use_message: ToolsBetaMessage,
        tools: list[Tool],
        messages: list[Message],
    ) -> None:
        tool_use_block = tool_use_message.content[-1]  # Add comment to explain this
        tool_name = tool_use_block.name  # type: ignore
        tool_input = tool_use_block.input  # type: ignore
        tool_use_id = tool_use_block.id  # type: ignore

        # Find the corresponding tool in the list of tools
        tool = next((tool for tool in tools if tool.name == tool_name), None)
        if not tool:
            error_message = f"Tool '{tool_name}' not found."
            log_to_file(CHATBOT_LOG_FILE_PATH, error_message)
            raise ValueError(error_message)

        try:
            # Execute the tool with the provided input
            tool_result = tool.execute(**tool_input)  # type: ignore

            # Create a ToolUse object representing the tool activation
            tool_use = ToolUse(
                tool_name=tool_name, tool_input=tool_input, tool_use_id=tool_use_id  # type: ignore
            )

            # Append the tool response to the conversation history
            self._append_tool_response(
                messages, tool_result, tool_use, tool_use_message
            )
        except Exception as e:
            log_to_file(
                CHATBOT_LOG_FILE_PATH,
                f"An error occurred while handling tool activation: {str(e)}",
            )

    def _append_tool_response(
        self,
        messages: list[Message],
        tool_result: Any,
        tool_use: ToolUse,
        tool_use_message: ToolsBetaMessage,
    ):
        # Update the last user message with the tool use information
        last_user_message = messages[-1]
        last_user_message.response = Response(
            id=tool_use_message.id,
            model=tool_use_message.model,
            text=tool_use_message.content[0].text,  # type: ignore
            timestamp=datetime.now(),
            tool_use=tool_use,
        )

        # Create a new message for the tool result
        tool_response = ToolResponse(
            tool_use_id=tool_use.tool_use_id, tool_result=tool_result
        )
        new_message_id = max((message.id for message in messages), default=0)
        new_message = Message(
            id=new_message_id + 1,
            user_id="system",
            text="",  # Empty text since it's a system message for tool result
            timestamp=datetime.now(),
            tool_response=tool_response,
        )
        messages.append(new_message)

    def _prepare_tool_schema(self, tools: list[Tool]) -> list[dict]:
        log_function_call(
            CHATBOT_LOG_FILE_PATH, "AnthropicAdapter._prepare_tool_schema", tools=tools
        )
        tools_schema = []
        for tool in tools:
            properties = {}
            required_fields = []
            for field_name, field_info in tool.input_schema.fields.items():
                property_schema = {
                    "type": field_info["type"],
                    "description": field_info["description"],
                }
                if "enum" in field_info:
                    property_schema["enum"] = field_info["enum"]
                properties[field_name] = property_schema
                if field_info.get("required"):
                    required_fields.append(field_name)

            tools_schema.append(
                {
                    "name": tool.name,
                    "description": tool.description,
                    "input_schema": {
                        "type": "object",
                        "properties": properties,
                        "required": required_fields,
                    },
                }
            )

        return tools_schema

    def _prepare_api_messages(
        self, messages: list[Message], verify: bool = True
    ) -> list[dict]:
        """
        Prepares API messages for the Anthropic API by converting a list of Message objects
        to a list of dictionaries, handling both cases with and without tools.

        This method iterates over the provided list of messages and constructs a list of
        dictionaries compatible with the Anthropic API's expected format. It handles user messages,
        assistant responses, tool usage, and tool results. If any Response object has is_error set
        to True, an error is raised.

        Args:
            messages: A list of Message objects to be converted to API messages.
            verify: A boolean indicating whether to verify the constructed API messages.

        Returns:
            A list of dictionaries representing the API messages, compatible with the Anthropic
            API's expected format.

        Raises:
            ValueError: If any Response object has is_error set to True.
            InvalidMessageError: If the constructed API messages fail the verification.
        """

        log_function_call(
            CHATBOT_LOG_FILE_PATH,
            "Claude3Opus.prepare_api_messages",
            messages=messages,
        )
        api_messages = []
        last_role = None

        for message in messages:
            if isinstance(message, dict):
                if "role" in message and "content" in message:
                    if message["role"] != last_role:
                        api_messages.append(message)
                        last_role = message["role"]
            elif isinstance(message, Message):
                content = []

                if isinstance(message.text, str) and message.text.strip():
                    content.append({"type": "text", "text": message.text})

                for attachment in message.attachments:
                    content.append(
                        {
                            "type": "image",
                            "source": {
                                "type": attachment.source_type,
                                "media_type": attachment.media_type,
                                "data": attachment.data,
                            },
                        }
                    )

                if content:
                    if last_role != "user":
                        api_messages.append({"role": "user", "content": content})
                        last_role = "user"

                if message.response:
                    if message.response.is_error:
                        raise ValueError("Response object has is_error set to True.")

                    response_content = []

                    if (
                        isinstance(message.response.text, str)
                        and message.response.text.strip()
                    ):
                        response_content.append(
                            {"type": "text", "text": message.response.text}
                        )

                    for attachment in message.response.attachments:
                        response_content.append(
                            {
                                "type": "image",
                                "source": {
                                    "type": attachment.source_type,
                                    "media_type": attachment.media_type,
                                    "data": attachment.data,
                                },
                            }
                        )

                    if message.response.tool_use:
                        tool_use_message = self._prepare_tool_use_message(
                            tool_name=message.response.tool_use.tool_name,
                            tool_input=message.response.tool_use.tool_input,
                            tool_use_id=message.response.tool_use.tool_use_id,
                        )
                        api_messages.append(tool_use_message)
                    else:
                        if response_content:
                            if last_role != "assistant":
                                api_messages.append(
                                    {"role": "assistant", "content": response_content}
                                )
                                last_role = "assistant"

                if message.tool_response:
                    tool_result_message = self._prepare_tool_result_message(
                        tool_use_id=message.tool_response.tool_use_id,
                        tool_result=message.tool_response.tool_result,
                    )
                    api_messages.append(tool_result_message)

        # Verify the constructed API messages
        if verify:
            try:
                self._verify_api_messages(api_messages)
            except InvalidMessageError as e:
                log_json_content(CHATBOT_LOG_FILE_PATH, api_messages)
                log_variable(CHATBOT_LOG_FILE_PATH, "Invalid API messages", str(e))
                raise

        return api_messages

    def _prepare_tool_use_message(
        self, tool_name: str, tool_input: dict, tool_use_id: str
    ) -> dict:
        log_function_call(
            CHATBOT_LOG_FILE_PATH,
            "AnthropicAdapter._prepare_tool_use_message",
            tool_name=tool_name,
            tool_input=tool_input,
            tool_use_id=tool_use_id,
        )
        return {
            "role": "assistant",
            "content": [
                {
                    "type": "tool_use",
                    "id": tool_use_id,
                    "name": tool_name,
                    "input": tool_input,
                }
            ],
        }

    def _prepare_tool_result_message(self, tool_use_id, tool_result):
        """
        Prepares a tool result message dictionary for the Anthropic API.

        This method constructs a dictionary representing a tool result message, which includes the
        tool use ID and the result obtained from executing the tool. The message is structured in a
        format compatible with the Anthropic API.

        Args:
            tool_use_id: The unique identifier for the tool use instance.
            tool_result: The result obtained from executing the tool.

        Returns:
            A dictionary representing the tool result message, compatible with the Anthropic API's
            expected format.
        """

        log_function_call(
            CHATBOT_LOG_FILE_PATH,
            "AnthropicAdapter.prepare_tool_result_message",
            tool_use_id=tool_use_id,
            tool_result=tool_result,
        )
        return {
            "role": "user",
            "content": [
                {
                    "type": "tool_result",
                    "tool_use_id": tool_use_id,
                    "content": str(tool_result),
                }
            ],
        }

    def _verify_api_messages(self, api_messages: list[dict]):
        """
        Verifies the structure and content of API messages to ensure they adhere to the expected
        format.

        This method checks each message in the provided list of API messages to ensure they have the
        correct structure, alternate between "user" and "assistant" roles, and contain valid content
        based on their role and content type.

        Args:
            api_messages: A list of dictionaries representing the API messages to verify.

        Raises:
            InvalidMessageError: If any of the following conditions are not met:
                - The API messages list is not empty.
                - Each message has a 'role' and 'content' key.
                - The roles alternate between "user" and "assistant".
                - The last message is not from the assistant.
                - Message content is a non-empty list.
                - Each content block is a dictionary with a valid 'type' key.
                - Text content block has a non-empty 'text' key.
                - Image content block has 'source', 'media_type', and 'data' keys.
                - Tool use content block has 'id', 'name', and 'input' keys.
                - Tool result content block has 'tool_use_id' and 'content' keys.
        """

        log_function_call(
            CHATBOT_LOG_FILE_PATH,
            "Claude3Opus._verify_api_messages",
            api_messages=api_messages,
        )

        if not api_messages:
            raise InvalidMessageError("API messages list is empty.")

        expected_role = "user"
        for message in api_messages:
            if "role" not in message or "content" not in message:
                raise InvalidMessageError(
                    "API message is missing 'role' or 'content' key."
                )

            role = message["role"]
            content = message["content"]

            if role != expected_role:
                raise InvalidMessageError(
                    f"Unexpected role '{role}'. Expected '{expected_role}'."
                )

            if not isinstance(content, list) or not content:
                raise InvalidMessageError("Message content must be a non-empty list.")

            for content_block in content:
                if not isinstance(content_block, dict):
                    raise InvalidMessageError("Content block must be a dictionary.")

                if "type" not in content_block:
                    raise InvalidMessageError("Content block is missing 'type' key.")

                block_type = content_block["type"]
                if block_type not in ["text", "image", "tool_use", "tool_result"]:
                    raise InvalidMessageError(
                        f"Invalid content block type '{block_type}'."
                    )

                if block_type == "text":
                    if "text" not in content_block or not content_block["text"].strip():
                        raise InvalidMessageError(
                            "Text content block must have a non-empty 'text' key."
                        )
                elif block_type == "image":
                    if (
                        "source" not in content_block
                        or "media_type" not in content_block["source"]
                        or "data" not in content_block["source"]
                    ):
                        raise InvalidMessageError(
                            "Image content block is missing 'source', 'media_type', or 'data' key."
                        )
                elif block_type == "tool_use":
                    if (
                        "id" not in content_block
                        or "name" not in content_block
                        or "input" not in content_block
                    ):
                        raise InvalidMessageError(
                            "Tool use content block is missing 'id', 'name', or 'input' key."
                        )
                elif block_type == "tool_result":
                    if (
                        "tool_use_id" not in content_block
                        or "content" not in content_block
                    ):
                        raise InvalidMessageError(
                            "Tool result content block is missing 'tool_use_id' or 'content' key."
                        )

            expected_role = "assistant" if expected_role == "user" else "user"

        if api_messages[-1]["role"] == "assistant":
            raise InvalidMessageError("The last message cannot be from the assistant.")

    def _get_api_error_response(self, status_code: Any, error_message: str) -> Response:
        """
        Generates an appropriate error response based on the provided status code and error message.

        This method takes a status code and an error message as input and returns a Response object
        containing an error message corresponding to the status code. If the status code is not
        recognized, it logs the unexpected error and returns a generic error message.

        Args:
            status_code: An integer representing the HTTP status code of the error.
            error_message: A string containing the error message.

        Returns:
            A Response object with the generated error message, the current timestamp, and the
            is_error flag set to True.
        """

        log_function_call(
            CHATBOT_LOG_FILE_PATH,
            "Claude3Opus._get_api_error_response",
            status_code=status_code,
            error_message=error_message,
        )

        if status_code == 400:
            error_text = f"Error: Invalid request. {error_message}"
        elif status_code == 401:
            error_text = (
                "Error: Authentication failed. Please check your API credentials."
            )
        elif status_code == 403:
            error_text = (
                "Error: Insufficient permissions. "
                "Please check your API key permissions."
            )
        elif status_code == 404:
            error_text = "Error: The requested resource was not found."
        elif status_code == 429:
            error_text = "Error: API rate limit exceeded. Please try again later."
        elif status_code == 500:
            error_text = (
                "Error: An unexpected error occurred. "
                "Please try again later or contact support."
            )
        elif status_code == 529:
            error_text = (
                "Error: The API is temporarily overloaded. Please try again later."
            )
        else:
            # Log the unexpected error for further investigation
            log_variable(CHATBOT_LOG_FILE_PATH, "Unexpected error", error_message)
            error_text = (
                "I apologize for the inconvenience, but I encountered an unexpected error. "
                "Please try again later or contact support for assistance."
            )

        return Response(
            id="",
            model=self.parameters.model_name,
            text=error_text,
            timestamp=datetime.now(),
            is_error=True,
            attachments=[],
        )
