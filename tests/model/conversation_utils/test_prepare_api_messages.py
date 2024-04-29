import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime
from src.chatbots.chatbots import ChatbotContext
from src.model.conversation_dataclasses import Response, Message, Branch, Conversation
from src.model.conversation_store import ConversationStore
from src.model.conversation_utils import ConversationUtils


@unittest.skip("Disabling all tests in TestPrepareApiMessages temporarily")
class TestPrepareApiMessages(unittest.TestCase):
    def setUp(self):
        self.chatbot_context = MagicMock(spec=ChatbotContext)
        self.conversation_store = MagicMock(spec=ConversationStore)
        self.utils = ConversationUtils(self.chatbot_context, self.conversation_store)

        # Setup actual Conversation and Branch instances
        response = Response(
            id="resp1", model="model1", text="Hello", timestamp=datetime.now()
        )
        message1 = Message(
            id=0,
            user_id="user1",
            text="Hi",
            timestamp=datetime.now(),
            response=response,
        )
        message2 = Message(
            id=1, user_id="user1", text="How are you?", timestamp=datetime.now()
        )
        branch = Branch(id=0, messages=[message1, message2])
        conversation = Conversation(
            id="1", title="Test Conversation", branches=[branch]
        )
        self.conversation_store.get_conversation.return_value = conversation

    def test_prepare_api_messages_includes_correct_messages(self):
        messages = self.utils.prepare_api_messages("1", 0, 1, include_context=True)
        expected_messages = [
            {"role": "user", "content": "Hi"},
            {"role": "assistant", "content": "Hello"},
            {"role": "user", "content": "How are you?"},
        ]
        self.assertEqual(messages, expected_messages)
