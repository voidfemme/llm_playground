import anthropic
import openai
from src.utils.file_logger import (
    LOG_FILE_PATH,
    log_function_call,
    log_variable,
    initialize_log_file,
)

initialize_log_file(LOG_FILE_PATH)


class Chatbot:
    @property
    def name(self) -> str:
        raise NotImplementedError("Subclass must implement the 'name' property")

    def get_message(self, messages: list) -> str | None:
        raise NotImplementedError("Subclass must implement the 'get_message' method")


class AnthropicChatbot(Chatbot):
    def __init__(self, client: anthropic.Anthropic):
        self.client = client

    @property
    def name(self):
        return "Anthropic Chatbot"

    def get_message(self, messages: list) -> str:
        log_function_call(
            log_file_path=LOG_FILE_PATH,
            function_name="AnthropicChatbot.get_message",
            messages=messages,
        )
        anthropic_message = self.client.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=1024,
            messages=messages,
        )
        log_variable(LOG_FILE_PATH, "anthropic_message", anthropic_message)

        if anthropic_message.content:
            return anthropic_message.content[0].text
        else:
            return "Error: Empty response from the Anthropic API"


class OpenAIChatbot(Chatbot):
    def __init__(self, client: openai.OpenAI):
        self.client = client

    @property
    def name(self):
        return "OpenAI Chatbot"

    def get_message(self, messages: list, personality: str | None = None) -> str | None:
        if personality is None:
            personality = "You are a helpful assistant."
        system_message = {"role": "system", "content": personality}
        openai_messages = [system_message] + messages

        try:
            completion = self.client.chat.completions.create(
                model="gpt-4",
                messages=openai_messages,  # type: ignore
            )
            return completion.choices[0].message.content
        except openai.APIError as e:
            print(f"OpenAI API Error: {e}")
            return None
