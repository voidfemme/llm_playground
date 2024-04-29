import logging
from src.chatbots.chatbot_manager import ChatbotManager
from src.model.branching import get_messages_up_to_branch_point
from src.model.conversation_store import ConversationStore
from src.model.conversation_dataclasses import Message, Response
from src.utils.error_handling import BranchNotFoundError, ConversationStoreNotFoundError
from src.utils.file_logger import log_function_call, log_variable, LOG_FILE_PATH


CHATBOT_SYSTEM_MESSAGE = "You are a helpful assistant, developed by voidfemme."


class ConversationUtils:
    def __init__(
        self,
        chatbot_manager: ChatbotManager,
        conversation_store: ConversationStore | None,
    ) -> None:
        self.chatbot_manager = chatbot_manager
        self.conversation_store = conversation_store

    def prepare_api_messages(
        self,
        conversation_id: str,
        branch_id: int,
        message_id: int,
        include_context: bool = False,
    ) -> list[Message]:
        log_function_call(
            LOG_FILE_PATH,
            "ConversationUtils.prepare_api_messages",
            conversation_id=conversation_id,
            branch_id=branch_id,
            message_id=message_id,
            include_context=include_context,
        )
        if self.conversation_store:
            messages = []
            conversation = self.conversation_store.get_conversation(conversation_id)
            log_variable(
                LOG_FILE_PATH, "conversation in prepare_api_messages", conversation
            )
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
                        f"Branch not found: {branch_id} in conversation "
                        f"{conversation_id}: {conversation.title}"
                    )
                messages = get_messages_up_to_branch_point(
                    conversation, branch_id, message_id
                )
                log_variable(
                    LOG_FILE_PATH, "messages in prepare_api_messages", messages
                )
                if include_context:
                    context_messages = self.get_context_messages(
                        conversation_id, branch_id, message_id
                    )
                    messages = context_messages + messages
            return messages
        else:
            raise ConversationStoreNotFoundError(
                "Could not prepare api messages, ConversationStore not initialized."
            )

    def get_context_messages(
        self,
        conversation_id: str,
        branch_id: int,
        message_id: int,
        num_context_messages: int = 5,
    ) -> list[Message]:
        if self.conversation_store:
            try:
                conversation = self.conversation_store.get_conversation(conversation_id)
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
                        message
                        for message in branch.messages
                        if message.id < message_id
                    ]
                    context_messages = messages[-num_context_messages:]
                    return context_messages
                return []
            except Exception as e:
                logging.error(f"Error getting context messages: {str(e)}")
                raise
        else:
            raise ConversationStoreNotFoundError(
                "Could not get context messages, ConversationStore not initialized."
            )

    def get_response_from_chatbot(
        self, conversation_id: str, branch_id: int, message_id: int, chatbot_name: str
    ) -> Response:
        log_function_call(
            LOG_FILE_PATH,
            "ConversationUtils.get_response_from_chatbot",
            conversation_id=conversation_id,
            branch_id=branch_id,
            message_id=message_id,
        )
        try:
            messages = self.prepare_api_messages(conversation_id, branch_id, message_id)
            chatbot = self.chatbot_manager.get_chatbot(chatbot_name)
            response = chatbot.send_message_without_tools(messages)
            log_variable(LOG_FILE_PATH, "response", response)
            return response
        except Exception as e:
            logging.error(f"Error getting response from chatbot: {str(e)}")
            raise
