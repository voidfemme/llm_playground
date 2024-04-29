# src/presenters/conversation_presenter.py


from src.model.conversation_manager import ConversationManager
from src.model.branching import get_messages_up_to_branch_point


class ConversationPresenter:
    def __init__(self, conversation_manager: ConversationManager, ui):
        self.conversation_manager = conversation_manager
        self.ui = ui  # This is the main window or specific components of the UI
        self.load_conversations()

    def load_conversations(self):
        """Load conversations and update the UI accordingly"""
        self.conversation_manager.load_conversations()
        if hasattr(self.ui, "update_conversation_list"):
            self.ui.update_conversation_list(self.conversation_manager.conversations)

    def get_conversation(self, conversation_id):
        return self.conversation_manager.get_conversation(conversation_id)

    def get_conversations(self):
        return self.conversation_manager.conversations

    def get_messages(self, conversation_id, branch_id=0, message_id=None):
        conversation = self.conversation_manager.get_conversation(conversation_id)
        if message_id is None:
            message_id = max(
                message.id
                for branch in conversation.branches
                for message in branch.messages
            )
        messages = get_messages_up_to_branch_point(conversation, branch_id, message_id)
        return messages

    def send_message(self, conversation_id, text):
        """Send a new message to a conversation"""
        # Assume a default branch and user ID for simplicity
        message = self.conversation_manager.add_message(
            conversation_id,
            branch_id=0,
            user_id="user123",
            text=text,
            current_chatbot="openai",
        )
        self.ui.update_message_display(conversation_id, message)
        return message

    def select_conversation(self, conversation_id):
        """Select a conversation and display its messages"""
        conversation = self.conversation_manager.get_conversation(conversation_id)
        self.ui.display_conversation(conversation)
