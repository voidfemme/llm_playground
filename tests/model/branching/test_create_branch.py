import unittest
from datetime import datetime
from src.model.conversation_dataclasses import Conversation, Branch, Message
from src.model.branching import create_branch
from src.utils.error_handling import InvalidRequestError, BranchNotFoundError


class TestCreateBranch(unittest.TestCase):

    def setUp(self):
        # Set up a basic conversation structure for use in tests
        self.conversation = Conversation(
            id="conv1",
            title="Test Conversation",
            branches=[
                Branch(
                    id=0,
                    messages=[
                        Message(
                            id=0,
                            user_id="user1",
                            text="Hello",
                            timestamp=datetime.now(),
                        )
                    ],
                )
            ],
        )

    def test_normal_branch_creation(self):
        """Test creating a new branch linked to an existing branch."""
        new_branch = create_branch(
            self.conversation, parent_branch_id=0, new_text="New branch text"
        )
        self.assertEqual(new_branch.id, 1)
        self.assertEqual(new_branch.parent_branch_id, 0)
        self.assertEqual(len(new_branch.messages), 1)
        self.assertEqual(new_branch.messages[0].text, "New branch text")

    def test_duplicate_initial_branch_creation(self):
        """Test error when creating a second initial branch."""
        with self.assertRaises(InvalidRequestError):
            create_branch(self.conversation, parent_branch_id=None)

    def test_non_existent_parent_branch(self):
        """Test creating a branch with a non-existent parent branch id."""
        with self.assertRaises(BranchNotFoundError):
            create_branch(self.conversation, parent_branch_id=999)

    def test_message_addition_on_branch_creation(self):
        """Test that a message is added to the branch if new_text is provided."""
        new_branch = create_branch(
            self.conversation, parent_branch_id=0, new_text="Test message"
        )
        self.assertEqual(len(new_branch.messages), 1)
        self.assertEqual(new_branch.messages[0].text, "Test message")


if __name__ == "__main__":
    unittest.main()
