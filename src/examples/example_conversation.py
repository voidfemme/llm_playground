import os
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock

from src.chatbot_library.core.conversation_manager import ConversationManager
from src.chatbot_library.models.conversation import Branch, Conversation, Message, Response

# Mocks for dependencies
chatbot_manager = MagicMock()
tool_manager = MagicMock()
conversation_utils = MagicMock()
example_dir = "src/examples/"

conversation_manager = ConversationManager(
    chatbot_manager, tool_manager, conversation_utils, data_dir=Path(example_dir)
)


def create_message(
    id, user_id, branch_id, text, next_message_id=None, special_response_id=None
):
    responses = []
    if next_message_id:
        responses.append(
            Response(
                id=f"resp_{id}_to_{next_message_id}",
                model="model",
                text=f"Response from message {id} to {next_message_id}",
                child_message_id=next_message_id,
                timestamp=datetime.now(),
            )
        )
    if special_response_id:
        responses.append(
            Response(
                id=f"resp_{id}_to_{special_response_id}",
                model="model",
                text=f"Special response from message {id} to {special_response_id}",
                child_message_id=special_response_id,
                timestamp=datetime.now(),
            )
        )
    return Message(
        id=id,
        user_id=user_id,
        branch_id=branch_id,
        text=text,
        timestamp=datetime.now(),
        responses=responses,
    )


def create_branch(branch_id, start_message_id, num_messages, special_link_id=None):
    messages = []
    for i in range(num_messages):
        message_id = start_message_id + i
        next_message_id = start_message_id + i + 1 if i < num_messages - 1 else None
        special_response_id = special_link_id if i == 2 else None
        messages.append(
            create_message(
                id=message_id,
                user_id="user1",
                branch_id=branch_id,
                text=f"Message text {message_id}",
                next_message_id=next_message_id,
                special_response_id=special_response_id,
            )
        )
    return Branch(
        id=branch_id, parent_branch_id=None, parent_message_id=None, messages=messages
    )


def create_example_conversation():
    num_branches = 3
    messages_per_branch = 5
    branches = []
    for i in range(num_branches):
        special_link_id = (
            (i + 1) * messages_per_branch if i < num_branches - 1 else None
        )
        branches.append(
            create_branch(
                i, i * messages_per_branch, messages_per_branch, special_link_id
            )
        )
    return Conversation(id="test_id", title="Test Title", branches=branches)


def save_example_conversation():
    example_conversation = create_example_conversation()
    conversation_manager.save_conversation(example_conversation)
    print(
        "Saved conversation JSON file at:",
        os.path.join(example_dir, f"{example_conversation.id}.json"),
    )
