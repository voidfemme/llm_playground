# src/model/conversation_manager.py

import json
import uuid
import logging
from datetime import datetime
from dataclasses import dataclass, field, asdict
from pathlib import Path

from src.model.chatbots import Chatbot
from src.utils.error_handling import (
    APIError,
    InvalidRequestError,
    ConversationNotFoundError,
    BranchNotFoundError,
    MessageNotFoundError,
    InvalidConversationDataError,
)
from src.utils.file_logger import LOG_FILE_PATH, log_function_call, log_variable, initialize_log_file


initialize_log_file(LOG_FILE_PATH)


@dataclass
class Attachment:
    id: str
    type: str
    url: str


@dataclass
class Response:
    id: str
    model: str
    text: str
    timestamp: datetime
    attachments: list[Attachment] = field(default_factory=list)


@dataclass
class Message:
    id: str
    user_id: str
    text: str
    timestamp: datetime
    attachments: list[Attachment] = field(default_factory=list)
    response: Response | None = None


@dataclass
class Branch:
    id: str
    parent_branch_id: str | None = None
    messages: list[Message] = field(default_factory=list)


@dataclass
class Conversation:
    id: str
    title: str
    branches: list[Branch] = field(default_factory=list)


class ConversationManager:
    def __init__(self, chatbot: Chatbot, data_dir: str) -> None:
        self.chatbot = chatbot
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.conversations: list[Conversation] = []
        logging.info(f"ConversationManager initialized with data directory: {data_dir}")

    def load_conversations(self):
        try:
            logging.info("Loading conversations from data directory...")
            self.conversations.clear()
            for file_path in self.data_dir.glob("*.json"):
                with file_path.open("r") as file:
                    try:
                        data = json.load(file)
                        branches = [
                            Branch(
                                id=branch_data["id"],
                                parent_branch_id=branch_data.get("parent_branch_id"),
                                messages=[
                                    Message(
                                        id=message_data["id"],
                                        user_id=message_data["user_id"],
                                        text=message_data["text"],
                                        timestamp=message_data["timestamp"],
                                        attachments=message_data.get("attachments", []),
                                        response=self._create_response(
                                            message_data.get("response")
                                        ),
                                    )
                                    for message_data in branch_data.get("messages", [])
                                ],
                            )
                            for branch_data in data.get("branches", [])
                        ]
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
            conversation_data = {
                "id": conversation.id,
                "title": conversation.title,
                "branches": [
                    {
                        "id": branch.id,
                        "parent_branch_id": branch.parent_branch_id,
                        "messages": [
                            {
                                "id": message.id,
                                "user_id": message.user_id,
                                "text": message.text,
                                "timestamp": message.timestamp,
                                "attachments": message.attachments,
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
            with file_path.open("w") as file:
                json.dump(conversation_data, file, default=str, indent=2)
            logging.info(f"Conversation saved: {conversation.id}")
        except Exception as e:
            logging.error(f"Error saving conversation: {str(e)}")
            raise

    def create_conversation(self, conversation_id: str, title: str) -> Conversation:
        try:
            conversation_id = str(uuid.uuid4())
            conversation = Conversation(id=conversation_id, title=title)
            self.conversations.append(conversation)
            self.save_conversation(conversation)
            logging.info(f"New conversation created: {conversation_id}")
            return conversation
        except Exception as e:
            logging.error(f"Error creating conversation: {str(e)}")
            raise

    def get_conversation(self, conversation_id: str) -> Conversation | None:
        try:
            conversation = next(
                (conv for conv in self.conversations if conv.id == conversation_id),
                None,
            )
            if conversation:
                logging.info(f"Retrieved conversation: {conversation_id}")
            else:
                logging.warning(f"Conversation not found: {conversation_id}")
            return conversation
        except Exception as e:
            logging.error(f"Error retrieving conversation: {str(e)}")
            raise

    def add_message(
        self,
        conversation_id: str,
        branch_id: str,
        user_id: str,
        text: str,
        attachments: list[Attachment] | None = None,
        include_context: bool = True,
        prompt_template: str = "",
    ) -> Message | None:
        try:
            log_function_call(
                LOG_FILE_PATH,
                "ConversationManager.add_message",
                conversation_id=conversation_id,
                branch_id=branch_id,
                user_id=user_id,
                text=text,
                attachments=attachments,
                include_context=include_context,
                prompt_template=prompt_template,
            )

            conversation = self.get_conversation(conversation_id)
            log_variable(LOG_FILE_PATH, "conversation", conversation)

            if conversation:
                branch = next(
                    (
                        branch
                        for branch in conversation.branches
                        if branch.id == branch_id
                    ),
                    None,
                )
                log_variable(LOG_FILE_PATH, "branch", branch)
                if not branch:
                    branch = Branch(id=branch_id)
                    conversation.branches.append(branch)
                    log_variable(LOG_FILE_PATH, "new_branch", branch)

                message = Message(
                    id=f"msg_{len(branch.messages) + 1}",
                    user_id=user_id,
                    text=text,
                    timestamp=datetime.now(),
                    attachments=attachments or [],
                )
                branch.messages.append(message)
                log_variable(LOG_FILE_PATH, "message", message)

                api_messages = self._get_messages_for_api(
                    conversation_id,
                    branch_id,
                    message.id,
                    include_context=include_context,
                    prompt_template=prompt_template,
                )
                log_variable(LOG_FILE_PATH, "api_messages", api_messages)
                logging.debug(f"API messages: {api_messages}")
                try:
                    response_text = self.chatbot.get_message(api_messages)
                    log_variable(LOG_FILE_PATH, "response_text", response_text)
                except APIError as e:
                    logging.error(f"API error: {str(e)}")
                    raise
                except Exception as e:
                    logging.error(f"Error generating response: {str(e)}")
                    raise

                if response_text:
                    response = Response(
                        id=f"resp_{len(branch.messages)}",
                        model=self.chatbot.name,
                        text=response_text,
                        timestamp=datetime.now(),
                    )
                    message.response = response
                    log_variable(LOG_FILE_PATH, "response", response)

                    logging.info(
                        f"Response generated for message {message.id} in conversation {conversation_id}, branch {branch_id}"
                    )
                else:
                    logging.warning(
                        f"No response generated for message {message.id} in conversation {conversation_id}, branch {branch_id}"
                    )

                self.save_conversation(conversation)
                logging.info(
                    f"Message added to conversation {conversation_id}, branch {branch_id}"
                )
                return message
        except Exception as e:
            logging.error(f"Error adding message: {str(e)}")
            raise

    def create_branch(
        self, conversation_id: str, parent_branch_id: str | None = None
    ) -> Branch | None:
        try:
            conversation = self.get_conversation(conversation_id)
            if conversation:
                branch_id = f"branch_{len(conversation.branches) + 1}"
                branch = Branch(id=branch_id, parent_branch_id=parent_branch_id)
                conversation.branches.append(branch)
                self.save_conversation(conversation)
                logging.info(
                    f"New branch created in conversation {conversation_id}: {branch_id}"
                )
                return branch
        except Exception as e:
            logging.error(f"Error creating branch: {str(e)}")
            raise

    def regenerate_response(
        self,
        conversation_id: str,
        branch_id: str,
        message_id: str,
    ) -> tuple[Branch, Message | None] | None:
        try:
            conversation = self.get_conversation(conversation_id)
            if conversation:
                branch = next(
                    (
                        branch
                        for branch in conversation.branches
                        if branch.id == branch_id
                    ),
                    None,
                )
                if not branch:
                    raise BranchNotFoundError(
                        f"Branch not found: {branch_id} in conversation {conversation_id}"
                    )
                messages = [
                    message for message in branch.messages if message.id <= message_id
                ]
                if len(messages) == len(branch.messages):
                    # If the selected message is the last message in the branch,
                    # regenerate the response in the current branch
                    try:
                        response_text = self.chatbot.get_message(
                            self._get_messages_for_api(
                                conversation_id, branch_id, message_id
                            )
                        )
                    except APIError as e:
                        logging.error(f"API error: {str(e)}")
                        raise
                    except Exception as e:
                        logging.error(f"Error regenerating response: {str(e)}")
                        raise

                    if response_text:
                        message = next(
                            (
                                message
                                for message in branch.messages
                                if message.id == message_id
                            ),
                            None,
                        )
                        if not message:
                            raise MessageNotFoundError(
                                f"Message not found: {message_id} in branch {branch_id} of conversation {conversation_id}"
                            )

                        response = Response(
                            id=f"resp_{len(branch.messages)}",
                            model=self.chatbot.name,
                            text=response_text,
                            timestamp=datetime.now(),
                        )
                        message.response = response
                        self.save_conversation(conversation)
                        logging.info(
                            f"Response regenerated for message {message_id} in conversation {conversation_id}, branch {branch_id}"
                        )
                        return branch, message

                else:
                    # If the selected message is not the last message in the branch,
                    # create a new branch and generate the response
                    new_branch = self.create_branch(conversation_id, branch_id)
                    if new_branch:
                        new_branch.messages = messages

                    try:
                        response_text = self.chatbot.get_message(
                            self._get_messages_for_api(
                                conversation_id, branch_id, message_id
                            )
                        )
                    except APIError as e:
                        logging.error(f"API error: {str(e)}")
                        raise
                    except Exception as e:
                        logging.error(f"Error regenerating response: {str(e)}")
                        raise

                    if response_text and new_branch:
                        message = next(
                            (
                                message
                                for message in new_branch.messages
                                if message.id == message_id
                            ),
                            None,
                        )
                        if not message:
                            raise MessageNotFoundError(
                                f"Message not found: {message_id} in new branch of conversation {conversation_id}"
                            )
                        response = Response(
                            id=f"resp_{len(new_branch.messages)}",
                            model=self.chatbot.name,
                            text=response_text,
                            timestamp=datetime.now(),
                        )
                        message.response = response
                        self.save_conversation(conversation)
                        logging.info(
                            f"Response regenerated for message {message_id} in conversation {conversation_id}, branch {branch_id}"
                        )
                        return new_branch, message

            logging.warning(
                f"Failed to regenerate response for message {message_id} in conversation {conversation_id}, branch {branch_id}"
            )
            return None
        except Exception as e:
            logging.error(f"Error regenerating response: {str(e)}")
            raise

    def delete_conversation(self, conversation_id: str) -> None:
        try:
            conversation = self.get_conversation(conversation_id)
            if conversation:
                self.conversations.remove(conversation)
                file_path = self.data_dir / f"{conversation.id}.json"
                if file_path.exists():
                    file_path.unlink()
                logging.info(f"Conversation deleted: {conversation_id}")
        except ConversationNotFoundError:
            logging.warning(f"Conversation not found: {conversation_id}")
        except Exception as e:
            logging.error(f"Error deleting conversation: {str(e)}")
            raise

    def rename_conversation(self, conversation_id: str, new_title: str) -> None:
        try:
            conversation = self.get_conversation(conversation_id)
            if conversation:
                conversation.title = new_title
                self.save_conversation(conversation)
                logging.info(f"Conversation renamed: {conversation_id}")
        except ConversationNotFoundError:
            logging.warning(f"Conversation not found: {conversation_id}")
        except Exception as e:
            logging.error(f"Error renaming conversation: {str(e)}")

    """
    Internal functions
    """

    def _get_messages_for_api(
        self,
        conversation_id: str,
        branch_id: str,
        message_id: str,
        include_context: bool = True,
        prompt_template: str = "",
    ) -> list[dict] | None:
        try:
            api_messages = []
            conversation = self.get_conversation(conversation_id)
            if conversation:
                logging.debug(f"Found conversation: {conversation_id}")
                branch = next(
                    (
                        branch
                        for branch in conversation.branches
                        if branch.id == branch_id
                    ),
                    None,
                )
                if not branch:
                    raise BranchNotFoundError(
                        f"Branch not found: {branch_id} in conversation {conversation_id}"
                    )
                logging.debug(
                    f"Found branch: {branch_id} in conversation {conversation_id}"
                )
                messages = [
                    message for message in branch.messages if message.id <= message_id
                ]
                logging.debug(f"Selected messages: {messages}")
                if include_context:
                    context_messages = self._get_context_messages(
                        conversation_id, branch_id, message_id
                    )
                    logging.debug(f"Including context messages: {context_messages}")
                    api_messages.extend(context_messages)
                for message in messages:
                    if isinstance(message.text, str) and message.text.strip():
                        if not api_messages or api_messages[-1]["role"] != "user":
                            api_messages.append(
                                {"role": "user", "content": message.text}
                            )
                            logging.debug(f"Added user message: {message.text}")
                        if message.response:
                            if (
                                isinstance(message.response.text, str)
                                and message.response.text.strip()
                            ):
                                if (
                                    not api_messages
                                    or api_messages[-1]["role"] != "assistant"
                                ):
                                    api_messages.append(
                                        {
                                            "role": "assistant",
                                            "content": message.response.text,
                                        }
                                    )
                                    logging.debug(
                                        f"Added assistant response: {message.response.text}"
                                    )
                    else:
                        logging.warning(
                            f"Skipping invalid message content: {message.text}"
                        )
                if prompt_template:
                    api_messages.append({"role": "system", "content": prompt_template})
                    logging.debug(f"Added prompt template: {prompt_template}")
            else:
                logging.warning(f"Conversation not found: {conversation_id}")
            logging.debug(f"API messages: {api_messages}")
            return api_messages
        except BranchNotFoundError as e:
            logging.error(f"Branch not found error: {str(e)}")
            raise
        except Exception as e:
            logging.error(f"Error getting messages for API: {str(e)}")
            raise

    def _get_context_messages(
        self,
        conversation_id: str,
        branch_id: str,
        message_id: str,
        num_context_messages: int = 5,
    ) -> list[dict]:
        try:
            conversation = self.get_conversation(conversation_id)
            if conversation:
                branch = next(
                    (
                        branch
                        for branch in conversation.branches
                        if branch.id == branch_id
                    ),
                    None,
                )
                if not branch:
                    raise BranchNotFoundError(
                        f"Branch not found: {branch_id}, in conversation {conversation_id}"
                    )
                messages = [
                    message for message in branch.messages if message.id < message_id
                ]
                context_messages = messages[-num_context_messages:]
                api_messages = []
                for message in context_messages:
                    if not api_messages or api_messages[-1]["role"] != "user":
                        api_messages.append({"role": "user", "content": message.text})
                    if message.response:
                        if not api_messages or api_messages[-1]["role"] != "assistant":
                            api_messages.append(
                                {"role": "assistant", "content": message.response.text}
                            )
                return api_messages
            return []
        except Exception as e:
            logging.error(f"Error getting context messages: {str(e)}")
            raise

    def _parse_response(self, response_data) -> Response | None:
        try:
            if isinstance(response_data, str):
                return json.loads(response_data)
            return response_data
        except json.JSONDecodeError as e:
            logging.error(f"Error parsing response: {str(e)}")
            raise InvalidRequestError(f"Invalid response data: {response_data}")

    def _create_response(self, response_data) -> Response:
        logging.info(
            f"Creating response with response_data: {response_data}. response_data type: {type(response_data)}"
        )
        try:
            if response_data:
                parsed_data = self._parse_response(response_data)
                if parsed_data:
                    return Response(
                        id=parsed_data.get("id", ""),  # type: ignore
                        model=parsed_data.get("model", ""),  # type: ignore
                        text=parsed_data.get("text", ""),  # type: ignore
                        timestamp=parsed_data.get("timestamp", ""),  # type: ignore
                        attachments=parsed_data.get("attachments", []),  # type: ignore
                    )
                else:
                    return Response(
                        id="",
                        model="",
                        text=str(response_data),
                        timestamp=datetime.now(),
                        attachments=[],
                    )
            else:
                return Response(
                    id="",
                    model="",
                    text="",
                    timestamp=datetime.now(),
                    attachments=[],
                )
        except Exception as e:
            logging.error(f"Error creating response: {str(e)}")
            raise
