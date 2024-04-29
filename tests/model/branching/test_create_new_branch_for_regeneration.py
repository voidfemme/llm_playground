import unittest
from datetime import datetime
from src.model.conversation_dataclasses import Conversation, Branch, Message
from src.model.branching import create_new_branch_for_regeneration
from src.utils.error_handling import MessageNotFoundError


class TestCreateNewBranchForRegeneration(unittest.TestCase):

    def setUp(self):
        # Setup a conversation with a single branch containing multiple messages
        self.messages_branch0 = [
            Message(id=0, user_id="user1", text="Hello", timestamp=datetime.now()),
            Message(
                id=1, user_id="user1", text="How are you?", timestamp=datetime.now()
            ),
            Message(
                id=2, user_id="user1", text="Good morning", timestamp=datetime.now()
            ),
        ]
        self.conversation = Conversation(
            id="conv1",
            title="Test Conversation",
            branches=[Branch(id=0, messages=self.messages_branch0)],
        )

    def test_normal_branch_regeneration(self):
        """Ensure a new branch is correctly created from a specified message."""
        new_branch = create_new_branch_for_regeneration(self.conversation, 0, 1)
        self.assertIsNotNone(new_branch)
        self.assertEqual(len(new_branch.messages), 2)  # Including the message with id 1
        self.assertEqual(new_branch.messages[1].text, "How are you?")

    def test_non_existent_message(self):
        """Test behavior when the specified message ID does not exist."""
        with self.assertRaises(MessageNotFoundError):
            create_new_branch_for_regeneration(self.conversation, 0, 999)

    def test_message_and_branch_integrity(self):
        """Check that all messages up to the specified one are included in the new branch."""
        new_branch = create_new_branch_for_regeneration(self.conversation, 0, 2)
        self.assertEqual(len(new_branch.messages), 3)
        self.assertEqual(new_branch.messages[2].text, "Good morning")
        self.assertEqual(
            new_branch.messages[0].text, "Hello"
        )  # Verify order is maintained


if __name__ == "__main__":
    unittest.main()
