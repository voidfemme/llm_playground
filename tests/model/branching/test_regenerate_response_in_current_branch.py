import unittest
from unittest.mock import MagicMock
from datetime import datetime
from src.model.conversation_dataclasses import Conversation, Branch, Message, Response
from src.model.branching import regenerate_response_in_current_branch
from src.utils.error_handling import MessageNotFoundError
from src.chatbots.chatbots import ChatbotContext


class TestRegenerateResponseInCurrentBranch(unittest.TestCase):

    def setUp(self):
        # Setup a conversation with a single branch and several messages
        self.chatbot_context = MagicMock(spec=ChatbotContext)
        self.messages_branch = [
            Message(
                id=0,
                user_id="user1",
                text="Hello",
                timestamp=datetime.now(),
                response=None,
            ),
            Message(
                id=1,
                user_id="user1",
                text="How are you?",
                timestamp=datetime.now(),
                response=None,
            ),
        ]
        self.branch = Branch(id=0, messages=self.messages_branch)
        self.conversation = Conversation(
            id="conv1", title="Test Conversation", branches=[self.branch]
        )

    def test_normal_response_regeneration(self):
        """Ensure a response is correctly regenerated for a message."""
        self.chatbot_context.get_message.return_value = "Regenerated response"
        branch, message = regenerate_response_in_current_branch(
            self.conversation, self.branch, 1, self.chatbot_context
        )
        self.assertEqual(message.response.text, "Regenerated response")
        self.assertEqual(message.id, 1)

    def test_non_existent_message(self):
        """Test behavior when the specified message ID does not exist."""
        with self.assertRaises(MessageNotFoundError):
            regenerate_response_in_current_branch(
                self.conversation, self.branch, 999, self.chatbot_context
            )

    def test_response_generation_failure(self):
        """Ensure the function handles cases where no response text is generated."""
        self.chatbot_context.get_message.return_value = (
            None  # Simulate failure to generate response
        )
        with self.assertRaises(RuntimeError):
            regenerate_response_in_current_branch(
                self.conversation, self.branch, 1, self.chatbot_context
            )


if __name__ == "__main__":
    unittest.main()
