# src/model/conversation_manager.py
from abc import ABC, abstractmethod
import json
from typing import Any
import uuid
import logging
from datetime import datetime
from dataclasses import asdict
from pathlib import Path
from src.chatbots.adapters.chatbot_adapter import ChatbotAdapter
from src.chatbots.chatbot_manager import ChatbotManager
from src.model.conversation_dataclasses import (
    Attachment,
    Branch,
    Conversation,
    Message,
    Response,
    ToolResponse,
    ToolUse,
)

from src.model.conversation_utils import ConversationUtils
from src.model.conversation_store import ConversationStore
from src.tools.tool_manager import Tool, ToolManager
from src.utils.error_handling import (
    ChatbotNotFoundError,
    InvalidRequestError,
    ConversationNotFoundError,
    BranchNotFoundError,
    MessageNotFoundError,
    InvalidConversationDataError,
    SaveConversationError,
)
from src.utils.file_logger import (
    LOG_FILE_PATH,
    UI_LOG_FILE_PATH,
    log_function_call,
    log_variable,
    initialize_log_file,
)
from src.model.branching import (
    get_branch,
    get_messages_up_to_branch_point,
    regenerate_response_in_new_branch,
    regenerate_response_in_current_branch,
)


initialize_log_file(LOG_FILE_PATH)


class ConversationManager(ConversationStore):
    """
    A class for managing conversations and their associated branches and messages.

    The ConversationManager class provides methods for creating, retrieving, updating,
    and deleting conversations. It also handles the generation of responses using a
    specified chatbot strategy.

    Attributes:
        chatbot_context (ChatbotContext): The context of the chatbot used for generating responses.
        data_dir (Path): The directory where conversation data is stored.
        conversations (list[Conversation]): A list of managed conversations.
        branch_counter (int): A counter for generating unique branch IDs.
        message_counter (int): A counter for generating unique message IDs.
        conversation_utils (ConversationUtils): An instance of the ConversationUtils class for \
                utility functions.
        tool_manager (ToolManager): The tool manager to be used for the chatbot to call functions

    Methods:
        load_conversations(): Loads conversations from the data directory.
        save_conversation(conversation: Conversation): Saves a conversation to the data directory.
        create_conversation(conversation_id: str, title: str) -> Conversation: Creates a new \
                conversation.
        get_conversation(conversation_id: str) -> Conversation: Retrieves a conversation by its ID.
        add_message(...) -> Message: Adds a message to a conversation branch and generates a \
                response.
        regenerate_response(...) -> tuple[Branch, Message]: Regenerates the response for a message \
                in a branch.
        delete_conversation(conversation_id: str): Deletes a conversation.
        rename_conversation(conversation_id: str, new_title: str): Renames a conversation.
    """

    def __init__(
        self,
        chatbot_manager: ChatbotManager,
        tool_manager: ToolManager,
        conversation_utils: ConversationUtils,
        data_dir: Path,
    ) -> None:
        self.data_dir = Path(data_dir)
        self.chatbot_manager = chatbot_manager
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.conversations: list[Conversation] = []
        self.branch_counter: int = 0
        self.message_counter: int = 0
        self.tool_manager = tool_manager
        self.conversation_utils = conversation_utils
        self.current_chatbot = None
        logging.info(f"ConversationManager initialized with data directory: {data_dir}")

    def load_conversations(self):
        try:
            logging.info("Loading conversations from data directory...")
            self.conversations.clear()
            for file_path in self.data_dir.rglob("*.json"):
                with file_path.open("r") as file:
                    try:
                        data = json.load(file)
                        branches = [
                            self._deserialize_branch(branch_data)
                            for branch_data in data.get("branches", [])
                        ]
                        logging.debug(f"Loaded branches: {branches}")
                        conversation = Conversation(
                            id=data["id"], title=data["title"], branches=branches
                        )
                        self.conversations.append(conversation)
                    except (KeyError, ValueError) as e:
                        raise InvalidConversationDataError(
                            f"Invalid conversation data in file {file_path}: {str(e)}"
                        )
            logging.info(f"Loaded {len(self.conversations)} conversations.")
        except Exception as e:
            logging.error(f"Error loading conversations: {str(e)}")
            raise

    def save_conversation(self, conversation: Conversation):
        try:
            file_path = self.data_dir / f"{conversation.id}.json"

            # Assign unique IDs to the branches
            branch_id_map = {}
            for i, branch in enumerate(conversation.branches):
                branch_id_map[branch.id] = i
                branch.id = i

            conversation_data = {
                "id": conversation.id,
                "title": conversation.title,
                "branches": [
                    {
                        "id": branch.id,
                        "parent_branch_id": branch_id_map.get(branch.parent_branch_id),
                        "parent_message_id": branch.parent_message_id,
                        "messages": [
                            {
                                "id": message.id,
                                "user_id": message.user_id,
                                "text": message.text,
                                "timestamp": message.timestamp,
                                "attachments": [
                                    asdict(attachment)
                                    for attachment in message.attachments
                                ],
                                "response": (
                                    asdict(message.response)
                                    if message.response
                                    else None
                                ),
                            }
                            for message in branch.messages
                        ],
                    }
                    for branch in conversation.branches
                ],
            }

            # Check if the conversation data has the expected structure
            if not conversation_data["branches"]:
                raise SaveConversationError(
                    "Conversation has no branches", "NO_BRANCHES"
                )

            # Write the conversation data to the JSON file
            with file_path.open("w") as file:
                json.dump(conversation_data, file, default=str, indent=2)
            logging.info(f"Conversation saved: {conversation.id}")
        except OSError as e:
            logging.error(f"Error writing conversation file: {str(e)}")
            raise SaveConversationError(
                f"Error writing conversation file: {str(e)}", "FILE_WRITE_ERROR"
            )
        except SaveConversationError as e:
            logging.error(str(e))
            raise
        except Exception as e:
            # create a SaveConversationError to propagate
            logging.error(f"Error saving conversation: {str(e)}")
            raise SaveConversationError(
                f"Unexpected error: {str(e)}", "UNEXPECTED_ERROR"
            )

    def create_conversation(self, conversation_id: str, title: str) -> Conversation:
        try:
            if not conversation_id:
                conversation_id = str(uuid.uuid4())
            elif any(
                conversation.id == conversation_id
                for conversation in self.conversations
            ):
                raise InvalidRequestError(
                    f"Conversation with ID '{conversation_id}' already exists"
                )

            if not title:
                raise InvalidRequestError("Conversation title cannot be empty")

            # Create the conversation instance
            conversation = Conversation(id=conversation_id, title=title)

            # Create a default branch
            default_branch = Branch(id=0, parent_branch_id=None, messages=[])
            conversation.branches.append(default_branch)

            # Add the conversation to the list of managed conversations
            self.conversations.append(conversation)
            logging.info(f"New conversation created: {conversation_id}")

            return conversation
        except InvalidRequestError as e:
            logging.error(str(e))
            raise
        except Exception as e:
            logging.error(f"Error creating conversation: {str(e)}")
            raise

    def get_conversation(self, conversation_id: str) -> Conversation:
        log_function_call(
            LOG_FILE_PATH,
            "ConversationManager.get_conversation",
            conversation_id=conversation_id,
        )
        for conversation in self.conversations:
            if conversation.id == conversation_id:
                logging.info(f"Retrieved conversation: {conversation_id}")
                return conversation
        raise ConversationNotFoundError(f"Conversation not found: {conversation_id}")

    def add_message(
        self,
        conversation_id: str,
        branch_id: int,
        user_id: str,
        text: str,
        current_chatbot: str,
        parent_message_id: int | None = None,
        attachments: list[Attachment] | None = None,
        include_context: bool = False,
        prompt_template: str = "",
        tools: list[Tool] | None = None,
    ) -> Message:
        try:
            conversation = self.get_conversation(conversation_id)

            if conversation:
                branch_dict = {branch.id: branch for branch in conversation.branches}
                branch = branch_dict.get(branch_id)

                if not branch:
                    raise BranchNotFoundError(
                        f"Branch not found: {branch_id} in conversation {conversation_id}"
                    )

                message = Message(
                    id=self.message_counter,
                    user_id=user_id,
                    text=text,
                    timestamp=datetime.now(),
                    branch_id=branch_id,
                    attachments=attachments or [],
                    parent_message_id=parent_message_id,
                )
                self.message_counter += 1
                branch.messages.append(message)

                chatbot = self.chatbot_manager.get_chatbot(current_chatbot)

                if tools and chatbot.supports_function_calling():
                    response = chatbot.send_message_with_tools(
                        self.conversation_utils.prepare_api_messages(
                            conversation_id, branch_id, message.id, include_context
                        ),
                        tools,
                    )
                else:
                    response = chatbot.send_message_without_tools(
                        self.conversation_utils.prepare_api_messages(
                            conversation_id, branch_id, message.id, include_context
                        )
                    )

                if response.is_error:
                    logging.error(f"Error generating response: {response.text}")
                    raise Exception(response.text)

                message.response = response

                logging.info(
                    f"Response generated for message {message.id} in conversation "
                    f"{conversation_id}, branch {branch_id}"
                )

                self.save_conversation(conversation)
                logging.info(
                    f"Message added to conversation {conversation_id}, branch {branch_id}"
                )
                return message
            else:
                raise ConversationNotFoundError(
                    f"Conversation not found: {conversation_id}"
                )
        except Exception as e:
            logging.error(f"Error adding message: {str(e)}")
            raise

    def regenerate_response(
        self,
        conversation_id: str,
        branch_id: int,
        message_id: int,
        current_chatbot: str,
    ) -> tuple[Branch, Message]:
        """
        Regenerate the response for a given message in a conversation branch.

        Args:
            conversation_id (str): The ID of the conversation
            branch_id (int): The ID of the branch
            message_id (int): The ID of the message for which the response needs to be regenerated.
            chatbot_strategy (str): The chatbot strategy to use for regenerating the response.

        Returns:
            tuple[Branch, Message]: A tuple containing the updated branch and the new message
            object if regeneration is successful, or raises an error if unsuccessful
            occurs during regeneration.

        Raises:
            ConversationNotFoundError: If the conversation with the given ID is not found.
            BranchNotFoundError: If the branch with the given ID is not found in the conversation.
            MessageNotFoundError: If the message with the given ID is not found in the branch.
        """
        log_function_call(
            LOG_FILE_PATH,
            "ConversationManager.regenerate_response",
            conversation_id=conversation_id,
            branch_id=branch_id,
            message_id=message_id,
            current_chatbot=current_chatbot,
        )

        # Get the conversation object
        conversation = self.get_conversation(conversation_id)
        if not conversation:
            raise ConversationNotFoundError(
                f"Conversation not found: {conversation_id}"
            )

        # Get the branch object
        branch = get_branch(conversation, branch_id)
        log_variable(LOG_FILE_PATH, "branch", branch)

        # Get the messages up to the specified message ID
        messages = get_messages_up_to_branch_point(conversation, branch_id, message_id)
        if not messages:
            raise MessageNotFoundError(
                f"Message not found: {message_id} in branch {branch_id} of "
                f"conversation {conversation_id}"
            )

        # Get the chatbot based on the provided strategy
        chatbot = self.chatbot_manager.get_chatbot(current_chatbot)

        # Regenerate the response in the current branch if the message is the last one
        if len(messages) == len(branch.messages):
            new_branch, new_message = regenerate_response_in_current_branch(
                conversation, branch, message_id, chatbot
            )
            return new_branch, new_message
        else:
            # Regenerate the response in a new branch if the message is not the last one
            new_branch, new_message = regenerate_response_in_new_branch(
                conversation, branch, message_id, chatbot
            )
            return new_branch, new_message

    def delete_conversation(self, conversation_id: str) -> None:
        try:
            conversation = self.get_conversation(conversation_id)
            if conversation:
                self.conversations.remove(conversation)
                file_path = self.data_dir / f"{conversation.id}.json"
                if file_path.exists():
                    file_path.unlink()
                logging.info(f"Conversation deleted: {conversation_id}")
        except ConversationNotFoundError as e:
            logging.error(str(e))
            raise
        except Exception as e:
            logging.error(f"Error deleting conversation: {str(e)}")
            raise

    def rename_conversation(self, conversation_id: str, new_title: str) -> None:
        log_function_call(
            UI_LOG_FILE_PATH,
            "ConversationManager.rename_conversation",
            conversation_id=conversation_id,
            new_title=new_title,
        )
        try:
            conversation = self.get_conversation(conversation_id)
            if conversation:
                conversation.title = new_title
                self.save_conversation(conversation)
                logging.info(
                    f"Conversation renamed in backend: {conversation_id}, New title: {new_title}"
                )
        except ConversationNotFoundError as e:
            logging.error(str(e))
            raise
        except Exception as e:
            logging.error(f"Error renaming conversation: {str(e)}")

    def set_current_chatbot(self, chatbot_strategy: str) -> None:
        """
        Set the current chatbot based on the provided chatbot strategy.

        Args:
            chatbot_strategy (str): The chatbot strategy to set as the current chatbot.

        Raises:
            ValueError: If the provided chatbot strategy is not available.
        """
        if chatbot_strategy not in self.chatbot_manager.get_chatbot_names():
            raise ValueError(f"Chatbot strategy '{chatbot_strategy}' is not available.")
        self.current_chatbot = chatbot_strategy

    def get_current_chatbot(self) -> ChatbotAdapter:
        """
        Get the current chatbot.

        Returns:
            ChatbotAdapter: The current chatbot adapter.
        """
        if self.current_chatbot:
            return self.chatbot_manager.get_chatbot(self.current_chatbot)
        else:
            raise ChatbotNotFoundError(
                "No current chatbot is set in the conversation manager"
            )

    def get_chatbot_names(self) -> list[str]:
        """
        Get a list of available chatbot strategies.

        Returns:
            list[str]: A list of available chatbot strategies.
        """
        return self.chatbot_manager.get_chatbot_names()

    def get_chatbots_supporting_function_calling(self) -> list[str]:
        """
        Get a list of chatbot strategies that support function calling.

        Returns:
            list[str]: A list of chatbot strategies that support function calling.
        """
        return [
            chatbot
            for chatbot in self.chatbot_manager.get_chatbot_names()
            if self.chatbot_manager.get_chatbot(chatbot).supports_function_calling()
        ]

    def get_chatbots_supporting_image_understanding(self) -> list[str]:
        """
        Get a list of chatbot strategies that support image understanding.

        Returns:
            list[str]: A list of chatbot strategies that support image understanding.
        """
        return [
            chatbot
            for chatbot in self.chatbot_manager.get_chatbot_names()
            if self.chatbot_manager.get_chatbot(chatbot).supports_image_understanding()
        ]

    def _deserialize_branch(self, branch_data):
        return Branch(
            id=branch_data["id"],
            parent_branch_id=branch_data.get("parent_branch_id"),
            parent_message_id=branch_data.get("parent_message_id"),
            messages=[
                self._deserialize_message(message_data)
                for message_data in branch_data.get("messages", [])
            ],
        )

    def _deserialize_message(self, message_data):
        return Message(
            id=message_data["id"],
            user_id=message_data["user_id"],
            text=message_data["text"],
            timestamp=datetime.fromisoformat(message_data["timestamp"]),
            branch_id=message_data["branch_id"],
            attachments=[
                self._deserialize_attachment(attachment_data)
                for attachment_data in message_data.get("attachments", [])
            ],
            response=self._deserialize_response(message_data.get("response")),
            tool_response=self._deserialize_tool_response(
                message_data.get("tool_response")
            ),
        )

    def _deserialize_attachment(self, attachment_data):
        return Attachment(
            id=attachment_data["id"],
            content_type=attachment_data["content_type"],
            media_type=attachment_data["media_type"],
            data=attachment_data["data"],
            source_type=attachment_data.get("source_type", "base64"),
            detail=attachment_data.get("detail", "auto"),
            url=attachment_data.get("url", ""),
        )

    def _deserialize_response(self, response_data):
        if response_data:
            return Response(
                id=response_data["id"],
                model=response_data["model"],
                text=response_data["text"],
                timestamp=datetime.fromisoformat(response_data["timestamp"]),
                is_error=response_data.get("is_error", False),
                attachments=[
                    self._deserialize_attachment(attachment_data)
                    for attachment_data in response_data.get("attachments", [])
                ],
                tool_use=self._deserialize_tool_use(response_data.get("tool_use")),
            )
        return None

    def _deserialize_tool_use(self, tool_use_data):
        if tool_use_data:
            return ToolUse(
                tool_name=tool_use_data["tool_name"],
                tool_input=tool_use_data["tool_input"],
                tool_use_id=tool_use_data["tool_use_id"],
            )
        return None

    def _deserialize_tool_response(self, tool_response_data):
        if tool_response_data:
            return ToolResponse(
                tool_use_id=tool_response_data["tool_use_id"],
                tool_result=tool_response_data["tool_result"],
            )
        return None
