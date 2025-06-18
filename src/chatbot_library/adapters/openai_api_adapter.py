from datetime import datetime
import json
import openai
from ..utils.errors import ModelNotSupportedError, InvalidMessageError
from .chatbot_adapter import ChatbotAdapter, ChatbotParameters
from ..models.conversation_dataclasses import Message, Response, ToolResult
from ..tools.compatibility import Tool
from ..utils.logging import (
    get_logger,
    log_function_call,
    log_json_content,
    log_message,
    log_variable,
    log_api_call,
    log_error
)


class OpenAIAdapter(ChatbotAdapter):
    def __init__(self, parameters: ChatbotParameters) -> None:
        super().__init__(parameters)
        self.logger = get_logger(self.__class__.__name__.lower())
        self.client = openai.OpenAI()

    @staticmethod
    def supported_models() -> list[str]:
        return [
            "gpt-4-turbo",
            "gpt-4-turbo-2024-04-09",
            "gpt-4-turbo-preview",
            "gpt-4-turbo-0125-preview",
            "gpt-4-1106-preview",
            "gpt-3.5-turbo-0125",
            "gpt-3.5-turbo-1106",
        ]

    @staticmethod
    def models_supporting_tools() -> list[str]:
        return [
            "gpt-4-turbo",
            "gpt-4-turbo-2024-04-09",
            "gpt-4-turbo-preview",
            "gpt-4-turbo-0125-preview",
            "gpt-4-1106-preview",
            "gpt-3.5-turbo-0125",
            "gpt-3.5-turbo-1106",
        ]

    @staticmethod
    def models_supporting_image_understanding() -> list[str]:
        return [
            "gpt-4-turbo",
            "gpt-4-turbo-2024-04-09",
            "gpt-4-turbo-preview",
            "gpt-4-turbo-0125-preview",
        ]

    def send_message_with_tools(
        self, messages: list[Message], active_tools: list[Tool]
    ) -> Response:
        log_function_call(self.logger, 
            
            "OpenAIAdapter.send_message_with_tools",
            number_of_messages=len(messages),
            active_tools=active_tools,
        )

        if not active_tools:
            raise ValueError(
                "active_tools cannot be empty when calling send_message_with_tools"
            )
        current_branch_id = self._get_current_branch_id(messages)
        if self.parameters.model_name not in self.models_supporting_tools():
            supported_models = ", ".join(self.models_supporting_tools())
            raise ModelNotSupportedError(
                f"Model {self.parameters.model_name} not supported with openai function calling\n",
                f"Models that support function calling: {supported_models}",
            )

        # Prepare the API messages and tool schema
        api_messages = self._prepare_api_messages(messages)
        tool_schema = self._prepare_tool_schema(active_tools)

        try:
            log_json_content(self.logger,  [tool.to_dict() for tool in active_tools])
            openai_response = self.client.chat.completions.create(
                model=self.parameters.model_name,
                messages=api_messages,  # type: ignore
                tools=tool_schema,  # type: ignore
                stop=self.parameters.stop_sequences,
                temperature=self.parameters.temperature,
            )
        except Exception as e:
            log_variable(self.logger, "Exception", str(e))
            status_code = getattr(e, "status_code", None)
            error_message = str(e)
            return self._get_api_error_response(status_code, error_message)

        # Check if the API response indicates a tool use
        response_message = openai_response.choices[0].message
        tool_calls = response_message.tool_calls

        last_message = None
        if tool_calls:
            available_functions = {tool.name: tool.function for tool in active_tools}

            if response_message.content:
                # Append the initial response message to the last message's responses list
                last_message = messages[-1]
                last_message.responses.append(
                    Response(
                        id=openai_response.id,
                        model=openai_response.model,
                        text=response_message.content,
                        timestamp=datetime.now(),
                    )
                )

            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_to_call = available_functions[function_name]
                function_args = json.loads(tool_call.function.arguments)
                function_response = function_to_call(**function_args)

                # Append the tool response message to the messages list
                tool_result_message = Message(
                    id=len(messages) + 1,
                    user_id="system",
                    text="",
                    timestamp=datetime.now(),
                    branch_id=current_branch_id,
                    tool_result=ToolResult(
                        tool_use_id=tool_call.id,
                        tool_result=function_response,
                    ),
                )
                messages.append(tool_result_message)

                # Update the child_message_id of the last response in the previous message
                if last_message and last_message.responses:
                    last_message.responses[-1].child_message_id = tool_result_message.id

            openai_response = self.client.chat.completions.create(
                model=self.parameters.model_name,
                messages=self._prepare_api_messages(messages),  # type: ignore
            )  # get a new response from the model where it can see the function response

        if openai_response.choices[0].message.content:
            # Append the final response to the last message's responses list
            if last_message:
                last_message.responses.append(
                    Response(
                        id=openai_response.id,
                        model=openai_response.model,
                        text=openai_response.choices[0].message.content,
                        timestamp=datetime.now(),
                    )
                )
            else:
                last_message = messages[-1]
                last_message.responses.append(
                    Response(
                        id=openai_response.id,
                        model=openai_response.model,
                        text=openai_response.choices[0].message.content,
                        timestamp=datetime.now(),
                    )
                )
            return last_message.responses[-1]
        else:
            log_variable(self.logger, "Empty response", openai_response)
            return Response(
                id=openai_response.id,
                model=openai_response.model,
                text="Error: Empty response from model",
                timestamp=datetime.now(),
                is_error=True,
            )

    def send_message_without_tools(self, messages: list[Message]) -> Response:
        log_function_call(self.logger, 
            
            "OpenAIAdapter.send_message_without_tools",
            messages=messages,
        )
        if self.parameters.model_name not in self.supported_models():
            supported_models = ", ".join(self.supported_models())
            raise ModelNotSupportedError(
                f"Model '{self.parameters.model_name}' is not supported by OpenAIAdapter.\n"
                f"Currently supported models: {supported_models}"
            )

        # Prepare the api messages
        api_messages = self._prepare_api_messages(messages)

        # Set the system prompt
        api_messages.insert(
            0, {"role": "system", "content": self.parameters.system_message}
        )

        # Send the request and return a Response object
        try:
            openai_message = self.client.chat.completions.create(
                model=self.parameters.model_name,
                messages=api_messages,  # type: ignore
                stop=self.parameters.stop_sequences,
                temperature=self.parameters.temperature,
            )
            if openai_message.choices[0].message.content:
                return Response(
                    id=openai_message.id,
                    model=openai_message.model,
                    text=openai_message.choices[0].message.content,
                    timestamp=datetime.now(),
                )
            else:
                log_variable(self.logger, "Empty response", openai_message)
                return Response(
                    id=openai_message.id,
                    model=openai_message.model,
                    text="Error: Empty response from model",
                    timestamp=datetime.now(),
                    is_error=True,
                )
        except InvalidMessageError as e:
            log_json_content(self.logger,  e.json_content)
        except Exception as e:
            log_variable(self.logger, "Exception", str(e))
            status_code = getattr(e, "status_code", None)
            error_message = str(e)
            return self._get_api_error_response(status_code, error_message)

    def _get_current_branch_id(self, messages: list[Message]) -> int:
        return messages[-1].branch_id

    def _prepare_tool_schema(self, tools: list[Tool]) -> list[dict]:
        tool_schema = []
        for tool in tools:
            parameters = {}
            required_fields = []

            for field_name, field_info in tool.input_schema.fields.items():
                parameter = {
                    "type": field_info["type"],
                    "description": field_info["description"],
                }
                if "enum" in field_info:
                    parameter["enum"] = field_info["enum"]
                parameters[field_name] = parameter
                if field_info.get("required"):
                    required_fields.append(field_name)

            tool_schema.append(
                {
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": {
                            "type": "object",
                            "properties": parameters,
                            "required": required_fields,
                        },
                    },
                }
            )

        return tool_schema

    def _prepare_api_messages(
        self, messages: list[Message], verify: bool = True
    ) -> list[dict]:
        """
        Prepares API messages for the OpenAI API by converting a list of Message objects
        to a list of dictionaries, handling both cases with and without tools.

        This method iterates over the provided list of messages and constructs a list of
        dictionaries compatible with the OpenAI API's expected format. It handles user messages,
        assistant responses, and attachments. The conversation is treated as a
        directed acyclic graph (DAG), where each message can have multiple child messages.

        Args:
            messages: A list of Message objects to be converted to API messages.
            verify: A boolean indicating whether to verify the constructed API messages.

        Returns:
            A list of dictionaries representing the API messages, compatible with the OpenAI
            API's expected format.
        """

        log_function_call(self.logger, 
            
            "OpenAIAdapter._prepare_api_messages",
            messages=messages,
        )
        api_messages = []
        last_appended_role = ""
        processed_messages = set()

        def process_message(message: Message, last_appended_role: str) -> str:
            if message.id in processed_messages:
                return last_appended_role
            processed_messages.add(message.id)

            # Check if the message has no attachments and no tool response
            if not message.attachments and not message.tool_result:
                # Append the user message to api_messages if the text is a non-empty string
                # and the last appended role is not "user"
                if (
                    isinstance(message.text, str)
                    and message.text.strip()
                    and last_appended_role != "user"
                ):
                    api_messages.append(
                        {
                            "role": "user",
                            "content": [{"type": "text", "text": message.text}],
                        }
                    )
                    last_appended_role = "user"

                for response in message.responses:
                    # Append the response to api_messages if it has no tool use,
                    # its text is a non-empty string, and the last appended role is not "assistant"
                    if (
                        not response.tool_use
                        and isinstance(response.text, str)
                        and response.text.strip()
                        and last_appended_role != "assistant"
                    ):
                        api_messages.append(
                            {"role": "assistant", "content": response.text}
                        )
                        last_appended_role = "assistant"

                    # Recursively process the child message of the response
                    child_message = next(
                        (m for m in messages if m.id == response.child_message_id), None
                    )
                    if child_message:
                        last_appended_role = process_message(
                            child_message, last_appended_role
                        )
            else:
                # Create a content list for messages with attachments or tool responses
                content = []

                # Append the message text to content if it's a non-empty string
                if isinstance(message.text, str) and message.text.strip():
                    content.append({"type": "text", "text": message.text})

                # Append base64-encoded attachments to content
                for attachment in message.attachments:
                    if attachment.source_type == "base64":
                        content.append(
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:{attachment.media_type};base64,{attachment.data}"
                                },
                            }
                        )

                # Append the content to api_messages if it's not empty and the last appended role
                # is not "user"
                if content and last_appended_role != "user":
                    api_messages.append({"role": "user", "content": content})
                    last_appended_role = "user"

            return last_appended_role

        for message in messages:
            last_appended_role = process_message(message, last_appended_role)

        # Verify the constructed api_messages if the verify flag is set to True
        if verify:
            self._verify_api_messages(api_messages)

        return api_messages

    def _verify_api_messages(self, api_messages: list[dict]):
        last_role = None
        for message in api_messages:
            if "role" not in message or "content" not in message:
                raise ValueError(
                    "Invalid message format. Each message must have 'role' and 'content' fields."
                )

            if message["role"] not in ["user", "assistant"]:
                raise ValueError(
                    f"Invalid role: {message['role']}. Role must be either 'user' or 'assistant'."
                )

            if message["role"] == last_role:
                raise ValueError(
                    f"Consecutive messages with the same role: {message['role']}"
                )

            last_role = message["role"]

            if not isinstance(message["content"], (str, list)):
                raise ValueError(
                    "Invalid content format. Content must be either a string or a list."
                )

            if isinstance(message["content"], list):
                for item in message["content"]:
                    if not isinstance(item, dict) or "type" not in item:
                        raise ValueError(
                            "Invalid attachment format. Each attachment must be a dictionary with "
                            "a 'type' field."
                        )

                    if item["type"] == "text" and "text" not in item:
                        raise ValueError(
                            "Invalid text attachment format. Text attachment must have "
                            "a 'text' field."
                        )

                    if item["type"] != "text" and item["type"] not in item:
                        raise ValueError(
                            f"Invalid attachment format. Attachment of type '{item['type']}' "
                            "must have a corresponding field."
                        )

        if api_messages and api_messages[-1]["role"] != "user":
            offending_json = json.dumps(api_messages, indent=2)
            raise InvalidMessageError(
                "The last message must be from the user.", offending_json
            )

    def _get_api_error_response(self, status_code, error_message: str) -> Response:
        log_function_call(self.logger, 
            
            "ChatGPT4Turbo._get_api_error_response",
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
        else:
            log_variable(self.logger, "Unexpected error", error_message)
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
