from datetime import datetime
import json
import openai
from src.utils.error_handling import ModelNotSupportedError
from src.chatbots.adapters.chatbot_adapter import ChatbotAdapter, ChatbotParameters
from src.model.conversation_dataclasses import Message, Response, ToolResponse
from src.tools.tool_manager import Tool
from src.utils.file_logger import (
    CHATBOT_LOG_FILE_PATH,
    log_function_call,
    log_json_content,
    log_variable,
)


class OpenAIAPIAdapter(ChatbotAdapter):
    def __init__(self, parameters: ChatbotParameters) -> None:
        super().__init__(parameters)
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
            log_json_content(
                CHATBOT_LOG_FILE_PATH, [tool.to_dict() for tool in active_tools]
            )
            openai_response = self.client.chat.completions.create(
                model=self.parameters.model_name,
                messages=api_messages,  # type: ignore
                tools=tool_schema,  # type: ignore
                stop=self.parameters.stop_sequences,
                temperature=self.parameters.temperature,
            )
        except Exception as e:
            log_variable(CHATBOT_LOG_FILE_PATH, "Exception", str(e))
            status_code = getattr(e, "status_code", None)
            error_message = str(e)
            return self._get_api_error_response(status_code, error_message)

        # Check if the API response indicates a tool use
        response_message = openai_response.choices[0].message
        tool_calls = response_message.tool_calls

        if tool_calls:
            available_functions = {tool.name: tool.function for tool in active_tools}

            if response_message.content:
                # Append the initial response message to the messages list
                messages.append(
                    Message(
                        id=len(messages) + 1,
                        user_id="assistant",
                        text=response_message.content,
                        timestamp=datetime.now(),
                        response=Response(
                            id=openai_response.id,
                            model=openai_response.model,
                            text=response_message.content,
                            timestamp=datetime.now(),
                        ),
                    )
                )

            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_to_call = available_functions[function_name]
                function_args = json.loads(tool_call.function.arguments)
                function_response = function_to_call(**function_args)

                # Append the tool response message to the messages list
                messages.append(
                    Message(
                        id=len(messages) + 1,
                        user_id="system",
                        text="",
                        timestamp=datetime.now(),
                        tool_response=ToolResponse(
                            tool_use_id=tool_call.id,
                            tool_result=function_response,
                        ),
                    )
                )

            openai_response = self.client.chat.completions.create(
                model=self.parameters.model_name,
                messages=self._prepare_api_messages(messages),  # type: ignore
            )  # get a new response from the model where it can see the function response

        if openai_response.choices[0].message.content:
            return Response(
                id=openai_response.id,
                model=openai_response.model,
                text=openai_response.choices[0].message.content,
                timestamp=datetime.now(),
            )
        else:
            log_variable(CHATBOT_LOG_FILE_PATH, "Empty response", openai_response)
            return Response(
                id=openai_response.id,
                model=openai_response.model,
                text="Error: Empty response from model",
                timestamp=datetime.now(),
                is_error=True,
            )

    def send_message_without_tools(self, messages: list[Message]) -> Response:
        log_function_call(
            CHATBOT_LOG_FILE_PATH,
            "OpenAIAPIAdapter.send_message_without_tools",
            messages=messages,
        )
        if self.parameters.model_name not in self.supported_models():
            supported_models = ", ".join(self.supported_models())
            raise ModelNotSupportedError(
                f"Model '{self.parameters.model_name}' is not supported by OpenAIAPIAdapter.\n"
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
                log_variable(CHATBOT_LOG_FILE_PATH, "Empty response", openai_message)
                return Response(
                    id=openai_message.id,
                    model=openai_message.model,
                    text="Error: Empty response from model",
                    timestamp=datetime.now(),
                    is_error=True,
                )
        except Exception as e:
            log_variable(CHATBOT_LOG_FILE_PATH, "Exception", str(e))
            status_code = getattr(e, "status_code", None)
            error_message = str(e)
            return self._get_api_error_response(status_code, error_message)

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
        log_function_call(
            CHATBOT_LOG_FILE_PATH,
            "OpenAIAPIAdapter._prepare_api_messages",
            messages=messages,
        )
        api_messages = []
        for message in messages:
            if not message.attachments and not message.tool_response:
                if isinstance(message.text, str) and message.text.strip():
                    api_messages.append(
                        {
                            "role": "user",
                            "content": [{"type": "text", "text": message.text}],
                        }
                    )
                if message.response and not message.response.tool_use:
                    if (
                        isinstance(message.response.text, str)
                        and message.response.text.strip()
                    ):
                        api_messages.append(
                            {"role": "assistant", "content": message.response.text}
                        )
            else:
                content = []
                if isinstance(message.text, str) and message.text.strip():
                    content.append({"type": "text", "text": message.text})
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
                if content:
                    api_messages.append({"role": "user", "content": content})

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
                            "Invalid attachment format. Each attachment must be a dictionary with a 'type' field."
                        )

                    if item["type"] == "text" and "text" not in item:
                        raise ValueError(
                            "Invalid text attachment format. Text attachment must have a 'text' field."
                        )

                    if item["type"] != "text" and item["type"] not in item:
                        raise ValueError(
                            f"Invalid attachment format. Attachment of type '{item['type']}' must have a corresponding field."
                        )

        if api_messages and api_messages[-1]["role"] != "user":
            raise ValueError("The last message must be from the user.")

    def _get_api_error_response(self, status_code, error_message: str) -> Response:
        log_function_call(
            CHATBOT_LOG_FILE_PATH,
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
