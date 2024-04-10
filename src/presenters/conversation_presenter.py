# src/presenters/conversation_presenter.py

from typing import TYPE_CHECKING
import uuid
from src.model.conversation_manager import Branch
from src.presenters.message_presenter import MessagePresenter
from src.utils.file_logger import (
    LOG_FILE_PATH,
    log_function_call,
    log_variable,
    log_to_file,
)

if TYPE_CHECKING:
    from src.views.conversation_list_view import ConversationListView
    from src.views.main_window_view import MainWindowView
    from src.model.conversation_manager import ConversationManager


class ConversationPresenter:
    def __init__(
        self,
        main_window: "MainWindowView",
        conversation_list_view: "ConversationListView | None",
        conversation_manager: "ConversationManager",
    ):
        self.main_window = main_window
        self.conversation_list_view = conversation_list_view
        self.conversation_manager = conversation_manager
        self.current_conversation = None
        self.current_branch = None

        if self.conversation_list_view:
            self.conversation_list_view.presenter = self

        self.message_presenter = MessagePresenter(self)
        self.main_window.set_message_presenter(self.message_presenter)
        self.main_window.new_conversation_requested.connect(
            self.create_new_conversation
        )
        self.main_window.delete_conversation_requested.connect(
            self.delete_current_conversation
        )

    def create_new_conversation(self) -> None:
        if self.conversation_list_view:
            conversation_title = "New Conversation"
            conversation = self.conversation_manager.create_conversation(
                str(uuid.uuid4()), conversation_title
            )
            default_branch = Branch(id="branch_1")
            conversation.branches.append(default_branch)
            self.conversation_list_view.add_conversation(conversation)
            self.current_conversation = conversation
            self.current_branch = conversation.branches[0]
            self.update_conversation_view(self.current_branch.id)

    def delete_current_conversation(self):
        if self.current_conversation and self.conversation_list_view:
            self.conversation_manager.delete_conversation(self.current_conversation.id)
            self.conversation_list_view.remove_conversation(self.current_conversation)
            self.current_conversation = None
            self.current_branch = None
            self.main_window.clear_message_widgets()

    def rename_current_conversation(self, new_title: str):
        if self.current_conversation and self.conversation_list_view:
            self.conversation_manager.rename_conversation(
                self.current_conversation.id, new_title
            )
            self.current_conversation.title = new_title
            self.conversation_list_view.update_conversation(self.current_conversation)
            self.conversation_list_view.refresh_conversations()

    def load_conversations(self):
        if self.conversation_list_view:
            self.conversation_manager.load_conversations()
            self.conversation_list_view.clear_conversations()
            for conversation in self.conversation_manager.conversations:
                self.conversation_list_view.add_conversation(conversation)
        else:
            pass

    def on_conversation_selected(self, conversation_id):
        self.current_conversation = self.conversation_manager.get_conversation(
            conversation_id
        )
        if self.current_conversation:
            self.current_branch = self.current_conversation.branches[
                0
            ]  # Select the first branch by default
            self.update_conversation_view(self.current_branch.id)

    def update_conversation_view(self, branch_id: str):
        log_function_call(
            LOG_FILE_PATH,
            "ConversationPresenter.update_conversation_view",
            branch_id=branch_id,
        )
        if self.current_conversation:
            log_variable(
                LOG_FILE_PATH, "current_conversation", self.current_conversation
            )

            self.current_branch = next(
                (
                    branch
                    for branch in self.current_conversation.branches
                    if branch.id == branch_id
                ),
                None,
            )
            log_variable(LOG_FILE_PATH, "current_branch", self.current_branch)

            if self.current_branch:
                self.main_window.clear_message_widgets()
                messages = self.current_branch.messages
                log_variable(LOG_FILE_PATH, "messages", messages)

                for message in messages:
                    log_variable(LOG_FILE_PATH, "message", message)
                    self.main_window.add_message_widget(
                        message, self.current_conversation.id, self.current_branch.id
                    )
            else:
                log_to_file(LOG_FILE_PATH, "No current conversation")
                pass

    def send_message(self, message_text: str):
        log_function_call(
            LOG_FILE_PATH,
            "ConversationPresenter.send_message",
            message_text=message_text,
        )
        if self.current_conversation and self.current_branch:
            response = self.conversation_manager.add_message(
                self.current_conversation.id,
                self.current_branch.id,
                "user",
                message_text,
            )
            self.main_window.clear_input_text()
            self.update_conversation_view(self.current_branch.id)
