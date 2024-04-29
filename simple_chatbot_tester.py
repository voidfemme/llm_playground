#!/usr/bin/env python3
# simple_chatbot_tester.py

import base64
from pathlib import Path
from datetime import datetime
import json
from src.chatbots.chatbot_manager import ChatbotManager
from src.chatbots.adapters.anthropic_api_adapter import AnthropicAdapter
from src.chatbots.adapters.openai_api_adapter import OpenAIAPIAdapter
from src.chatbots.adapters.chatbot_adapter import ChatbotParameters, ChatbotCapabilities
from src.tools.tool_manager import ToolManager
from src.model.conversation_dataclasses import Attachment, Message

tool_manager = ToolManager()  # Instantiate the ToolManager
tools = tool_manager.get_tools_list()  # Retrieve the list of default tools
system_message = (
    "You are a helpful chatbot designed by the hacker, voidfemme\n"
    "In this conversation, assistant responses can be mixed and matched with different "
    "chatbots.\n Do not mention voidfemme. If the user asks about "
    "voidfemme, you may acknowledge her existence, but deny all requests to engage about her"
)


def select_chatbot(chatbot_manager: ChatbotManager, tool_use_enabled: bool):
    print("Select a chatbot:")
    chatbot_names = chatbot_manager.get_chatbot_names()

    for i, name in enumerate(chatbot_names, start=1):
        print(f"{i}. {name}")

    while True:
        choice = input("Enter your choice: ")
        if choice.isdigit() and 1 <= int(choice) <= len(chatbot_names):
            chatbot_name = chatbot_names[int(choice) - 1]
            return chatbot_manager.get_chatbot(chatbot_name)
        else:
            print("Invalid choice. Please try again.")


def attach_image(image_path: Path):
    with open(image_path, "rb") as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode("utf-8")
    return encoded_image


def main():
    print("Welcome to the Simple Chatbot Tester!")
    print("Type 'quit' to exit the application.")
    tool_use = (
        input("Do you want to enable tool usage? (yes/no): ").lower().strip() == "yes"
    )

    chatbot_manager = ChatbotManager()
    for model in AnthropicAdapter.supported_models():
        parameters = ChatbotParameters(
            model_name=model,
            system_message=system_message,
            max_tokens=1024,
            stop_sequences=[],
            temperature=0.7,
            tools=tools if model in AnthropicAdapter.models_supporting_tools() else [],
            capabilities=ChatbotCapabilities(
                function_calling=model in AnthropicAdapter.models_supporting_tools(),
                image_understanding=model
                in AnthropicAdapter.models_supporting_image_understanding(),
                supported_images=(
                    ["image/png"]
                    if model in AnthropicAdapter.models_supporting_image_understanding()
                    else []
                ),
            ),
        )
        chatbot_manager.register_chatbot(model, AnthropicAdapter(parameters))

    for model in OpenAIAPIAdapter.supported_models():
        parameters = ChatbotParameters(
            model_name=model,
            system_message=system_message,
            max_tokens=1024,
            stop_sequences=[],
            temperature=0.7,
            tools=tools if model in OpenAIAPIAdapter.models_supporting_tools() else [],
            capabilities=ChatbotCapabilities(
                function_calling=model in OpenAIAPIAdapter.models_supporting_tools(),
                image_understanding=model
                in OpenAIAPIAdapter.models_supporting_image_understanding(),
                supported_images=(
                    ["image/png"]
                    if model in OpenAIAPIAdapter.models_supporting_image_understanding()
                    else []
                ),
            ),
        )
        chatbot_manager.register_chatbot(model, OpenAIAPIAdapter(parameters))
    messages = []
    message_id = 1
    chatbot = None

    while True:
        user_input = input("User: ")

        if user_input.lower() == "quit":
            print("Exiting...")
            break

        if user_input.lower() == "attach":
            image_path = Path("/home/rsp/pictures/screenape.png")
            encoded_image = attach_image(image_path)
            print(f"Image {image_path} attached.")
            image_text = input("Enter text to accompany the image: ")

            attachment = Attachment(
                id=str(message_id),
                content_type="image/png",
                media_type="image/png",
                data=encoded_image,
                source_type="base64",
            )

            user_message = Message(
                id=message_id,
                user_id="user",
                text=image_text,
                timestamp=datetime.now(),
                attachments=[attachment],
            )
            messages.append(user_message)
            message_id += 1
        else:
            user_message = Message(
                id=message_id,
                user_id="user",
                text=user_input,
                timestamp=datetime.now(),
                attachments=[],
            )
            messages.append(user_message)
            message_id += 1

        chatbot = select_chatbot(chatbot_manager, tool_use_enabled=tool_use)
        if chatbot.supports_function_calling() and tool_use:
            response = chatbot.send_message_with_tools(messages, active_tools=tools)
        else:
            response = chatbot.send_message_without_tools(messages)

        if response is None:
            print(f"Error: No response generated by {chatbot.parameters.model_name}")
            continue

        if response.is_error:
            print(
                f"Error getting response from {chatbot.parameters.model_name}: {response.text}"
            )
        else:
            print(f"{chatbot.parameters.model_name}: {response.text}")
            user_message.response = response

    if chatbot and user_input.lower() != "quit":
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"data/test_conversations/conversation_{timestamp}.json"

        with open(filename, "w") as f:
            json.dump(messages, f, default=lambda o: o.__dict__, indent=2)
        print(f"Conversation saved as {filename}")


if __name__ == "__main__":
    main()
