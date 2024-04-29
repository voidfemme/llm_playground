# src/model/branching.py

from datetime import datetime
from src.chatbots.adapters.chatbot_adapter import ChatbotAdapter
from src.model.conversation_dataclasses import Conversation, Branch, Message, Response
from src.utils.error_handling import (
    BranchNotFoundError,
    ConversationNotFoundError,
    InvalidRequestError,
    MessageNotFoundError,
)


def create_branch(
    conversation: Conversation,
    parent_branch_id: int | None = None,
    parent_message_id: int | None = None,
    new_text: str = "",
) -> Branch:
    """
    Creates a new branch in the conversation. If 'new_text' is provided, it also
    creates an initial message in this new branch.

    Args:
        conversation (Conversation): The conversation to which the branch will be added.
        parent_branch_id (int | None): The ID of the parent branch, or None if it is a root branch.
        parent_message_id (int | None): The ID of the parent message that triggers the new branch \
                creation.
        new_text (str): The text for the initial message in the new branch.

    Returns:
        Branch: The newly created branch.

    Raises:
        InvalidRequestError: If an initial branch is already present and a new initial branch is \
                attempted to be created.
        BranchNotFoundError: If the specified parent branch ID does not exist.
    """
    if parent_branch_id is None and any(
        branch.parent_branch_id is None for branch in conversation.branches
    ):
        raise InvalidRequestError(
            "Initial branch already exists, parent branch ID must be None for additional branches"
        )

    if parent_branch_id is not None and parent_branch_id not in [
        branch.id for branch in conversation.branches
    ]:
        raise BranchNotFoundError(
            f"Branch not found: {parent_branch_id} in conversation {conversation.id}"
        )

    branch_id = len(conversation.branches)
    branch = Branch(
        id=branch_id,
        parent_branch_id=parent_branch_id,
        parent_message_id=parent_message_id,
    )

    if new_text:
        message_id = sum(len(branch.messages) for branch in conversation.branches)
        message = Message(
            id=message_id,
            user_id="user",
            text=new_text,
            timestamp=datetime.now(),
            branch_id=branch_id,
        )
        branch.messages.append(message)

    conversation.branches.append(branch)
    return branch


def get_branch(conversation: Conversation, branch_id: int) -> Branch:
    """
    Retrieves a branch from the conversation based on its ID.

    Args:
        conversation (Conversation): The conversation from which to retrieve the branch.
        branch_id (int): The ID of the branch to retrieve.

    Returns:
        Branch: The branch corresponding to the given ID.

    Raises:
        BranchNotFoundError: If the branch with the specified ID does not exist.
    """
    if not conversation:
        raise ConversationNotFoundError(f"Conversation not found: {conversation.id}")

    for branch in conversation.branches:
        if branch.id == branch_id:
            return branch

    raise BranchNotFoundError(
        f"Branch not found: {branch_id} in conversation {conversation.id}"
    )


def get_messages_up_to_branch_point(
    conversation: Conversation, branch_id: int, message_id: int
) -> list[Message]:
    """
    Collects all messages up to a specified message ID in the given branch, including messages
    from all ancestor branches up to the specified point.

    Args:
        conversation (Conversation): The conversation containing the branches.
        branch_id (int): The ID of the branch where the message is located.
        message_id (int): The ID of the message up to which to collect messages.

    Returns:
        list[Message]: A list of messages up to the specified message point.
    """

    messages = []
    visited_branches = set()
    current_branch = get_branch(conversation, branch_id)

    while current_branch:
        if current_branch.id in visited_branches:
            break  # Prevents processing a branch more than once

        visited_branches.add(current_branch.id)

        # Filter messages based on the branch being the target branch or a parent branch
        if current_branch.id == branch_id:
            branch_messages = [
                message
                for message in current_branch.messages
                if message.id <= message_id
            ]
        else:
            branch_messages = current_branch.messages

        # Add current branch's messages before older (parent) messages
        messages = branch_messages + messages

        # Move to the parent branch if it exists
        if current_branch.parent_branch_id is not None:
            try:
                current_branch = get_branch(
                    conversation, current_branch.parent_branch_id
                )
            except BranchNotFoundError:
                break  # No parent found, stop the loop
        else:
            break  # No more parents to process

    return messages


def create_new_branch_for_regeneration(
    conversation: Conversation, branch_id: int, message_id: int
) -> Branch:
    """
    Creates a new branch for the purpose of regenerating a response, copying messages
    up to the specified message ID from the specified branch.

    Args:
        conversation (Conversation): The conversation to which the new branch will be added.
        branch_id (int): The ID of the existing branch.
        message_id (int): The ID of the message to regenerate.

    Returns:
        Branch: The newly created branch with messages up to the specified message.

    Raises:
        MessageNotFoundError: If the original message cannot be found.
    """

    original_message = next(
        (
            message
            for message in conversation.branches[branch_id].messages
            if message.id == message_id
        ),
        None,
    )

    if original_message:
        new_branch = create_branch(
            conversation, branch_id, message_id, new_text=original_message.text
        )
        messages = get_messages_up_to_branch_point(conversation, branch_id, message_id)
        new_branch.messages = messages
        return new_branch
    else:
        raise MessageNotFoundError(
            f"Original message not found: {message_id} in branch {branch_id} of \
                    conversation {conversation.id}"
        )


def regenerate_response_in_current_branch(
    conversation: Conversation,
    branch: Branch,
    message_id: int,
    chatbot: ChatbotAdapter,
) -> tuple[Branch, Message]:
    """
    Regenerates a response for a specific message in the current branch, updating the message's
    response based on a new interaction or context.

    Args:
        conversation (Conversation): The conversation containing the branch and message.
        branch (Branch): The branch containing the message.
        message_id (int): The ID of the message to regenerate the response for.
        chatbot (ChatbotAdapter): The chatbot adapter used to generate the response.

    Returns:
        tuple[Branch, Message]: The branch and the message with the updated response.

    Raises:
        MessageNotFoundError: If no message with the given ID exists in the branch.
        Exception: If an error occurs during response generation.
    """
    message = next(
        (message for message in branch.messages if message.id == message_id),
        None,
    )
    if not message:
        raise MessageNotFoundError(
            f"Message not found: {message_id} in branch {branch.id} of "
            f"conversation {conversation.id}"
        )

    messages = get_messages_up_to_branch_point(conversation, branch.id, message_id)

    if chatbot.supports_function_calling():
        response = chatbot.send_message_with_tools(messages, chatbot.parameters.tools)
    else:
        response = chatbot.send_message_without_tools(messages)

    if response.is_error:
        raise Exception(f"Error generating response: {response.text}")

    message.response = response

    return branch, message


def regenerate_response_in_new_branch(
    conversation: Conversation,
    branch: Branch,
    message_id: int,
    chatbot: ChatbotAdapter,
) -> tuple[Branch, Message]:
    """
    Regenerates a response for a specific message by creating a new branch and then generating
    a new response based on the messages up to that point.

    Args:
        conversation (Conversation): The conversation containing the branch.
        branch (Branch): The branch from which a new branch will be created.
        message_id (int): The message ID for which to regenerate a response.
        chatbot (ChatbotAdapter): The chatbot adapter used to generate the new response.

    Returns:
        tuple[Branch, Message]: The newly created branch and the message with the new response.

    Raises:
        MessageNotFoundError: If the message cannot be found in the original branch.
        Exception: If an error occurs during response generation.
    """
    new_branch = create_new_branch_for_regeneration(conversation, branch.id, message_id)
    message = next(
        (message for message in new_branch.messages if message.id == message_id),
        None,
    )
    if not message:
        raise MessageNotFoundError(
            f"Message not found: {message_id} in new branch of conversation {conversation.id}"
        )

    messages = get_messages_up_to_branch_point(conversation, new_branch.id, message_id)

    if chatbot.supports_function_calling():
        response = chatbot.send_message_with_tools(messages, chatbot.parameters.tools)
    else:
        response = chatbot.send_message_without_tools(messages)

    if response.is_error:
        raise Exception(f"Error generating response: {response.text}")

    message.response = response

    return new_branch, message
