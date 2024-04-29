import unittest
from datetime import datetime
from src.model.conversation_dataclasses import Conversation, Branch, Message
from src.model.branching import get_branch
from src.utils.error_handling import BranchNotFoundError


class TestGetBranch(unittest.TestCase):

    def setUp(self):
        # Set up a conversation with multiple branches for comprehensive testing
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
                ),
                Branch(
                    id=1,
                    messages=[
                        Message(
                            id=1,
                            user_id="user2",
                            text="Hi there",
                            timestamp=datetime.now(),
                        )
                    ],
                ),
                Branch(
                    id=2,
                    messages=[
                        Message(
                            id=2,
                            user_id="user3",
                            text="Goodbye",
                            timestamp=datetime.now(),
                        )
                    ],
                ),
            ],
        )

    def test_normal_branch_retrieval(self):
        """Test retrieving an existing branch by ID."""
        branch = get_branch(self.conversation, 1)
        self.assertIsNotNone(branch)
        self.assertEqual(branch.id, 1)
        self.assertEqual(branch.messages[0].text, "Hi there")

    def test_non_existent_branch(self):
        """Test the response when the branch does not exist."""
        with self.assertRaises(BranchNotFoundError):
            get_branch(self.conversation, 999)

    def test_with_multiple_branches(self):
        """Ensure the correct branch is retrieved in a conversation with multiple branches."""
        branch = get_branch(self.conversation, 2)
        self.assertEqual(branch.id, 2)
        self.assertEqual(len(branch.messages), 1)
        self.assertEqual(branch.messages[0].text, "Goodbye")

    def test_error_handling(self):
        """Test that BranchNotFoundError is raised for an invalid branch ID."""
        with self.assertRaises(BranchNotFoundError):
            get_branch(self.conversation, 3)  # ID 3 does not exist in the setup


if __name__ == "__main__":
    unittest.main()
