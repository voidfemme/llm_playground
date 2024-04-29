from datetime import datetime
import unittest
from unittest.mock import MagicMock, patch
from src.model.conversation_dataclasses import Branch, Conversation, Message, Response
from src.model.conversation_utils import ConversationUtils
from src.model.conversation_store import ConversationStore
from src.chatbots.chatbots import ChatbotContext


@unittest.skip("Disabling all tests in TestGetMessagesForApi temporarily")
class TestGetMessagesForApi(unittest.TestCase):
    def setUp(self):
        self.chatbot_context = MagicMock(spec=ChatbotContext)
        self.conversation_store = MagicMock(spec=ConversationStore)
        self.conversation_utils = ConversationUtils(
            self.chatbot_context, self.conversation_store
        )

    def test_valid_input(self):
        # Setup test data
        response = Response(
            id="1", model="model1", text="Hello, world!", timestamp=datetime.now()
        )
        message1 = Message(
            id=0,
            user_id="user1",
            text="Hi there",
            timestamp=datetime.now(),
            response=response,
        )
        message2 = Message(
            id=1, user_id="user1", text="How are you", timestamp=datetime.now()
        )
        branch0 = Branch(id=0, messages=[message1, message2])
        branch1 = Branch(
            id=1,
            parent_branch_id=0,
            parent_message_id=0,
            messages=[
                Message(
                    id=0, user_id="user3", text="Good day", timestamp=datetime.now()
                )
            ],
        )
        conversation = Conversation(
            id="conv1", title="Test Conversation", branches=[branch0, branch1]
        )

        # Mock the conversation store to return this conversation
        self.conversation_store.get_conversation.return_value = conversation

        # Call the function under test
        api_messages = self.conversation_utils.get_messages_for_api(
            "conv1", 0, 1, include_context=True
        )

        # Assertions to check if the result is as expected
        expected_messages = [
            {"role": "user", "content": "Hi there"},
            {"role": "assistant", "content": "Hello, world!"},
        ]
        self.assertEqual(api_messages, expected_messages)

    def test_invalid_conversation_id(self):
        # Implement a test where the conversation ID does not exist
        pass

    def test_logging_is_called(self):
        # Test that logging is called correctly
        pass

    def test_branch_not_found_error(self):
        # Test handling of BranchNotFoundError
        pass

    def test_error_handling(self):
        # Test that other errors are logged and re-raised
        pass


if __name__ == "__main__":
    unittest.main()
