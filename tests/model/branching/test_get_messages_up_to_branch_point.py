import unittest
from datetime import datetime
from src.model.conversation_dataclasses import Conversation, Branch, Message
from src.model.branching import get_messages_up_to_branch_point


class TestGetMessagesUpToBranchPoint(unittest.TestCase):
    def setUp(self):
        # Setup a conversation with multiple branches
        self.messages_branch0 = [
            Message(id=0, user_id="user1", text="Hello", timestamp=datetime.now()),
            Message(
                id=1, user_id="user1", text="How are you?", timestamp=datetime.now()
            ),
        ]
        self.messages_branch1 = [
            Message(id=0, user_id="user2", text="Hi", timestamp=datetime.now()),
            Message(id=1, user_id="user2", text="Goodbye", timestamp=datetime.now()),
        ]
        # Adding an empty branch with ID 3 and parent branch ID 1
        self.conversation = Conversation(
            id="conv1",
            title="Test Conversation",
            branches=[
                Branch(id=0, parent_branch_id=None, messages=self.messages_branch0),
                Branch(id=1, parent_branch_id=0, messages=self.messages_branch1),
                Branch(id=3, parent_branch_id=1, messages=[]),  # Empty branch
            ],
        )

    def test_single_branch_messages(self):
        """
        Ensure messages from a single branch are correctly returned up to a specified message ID.
        """
        messages = get_messages_up_to_branch_point(self.conversation, 0, 1)
        self.assertEqual(len(messages), 2)
        self.assertEqual(messages[0].text, "Hello")
        self.assertEqual(messages[1].text, "How are you?")

    def test_with_parent_branches(self):
        """Test collecting messages from both the branch and its parent."""
        messages = get_messages_up_to_branch_point(self.conversation, 1, 1)
        self.assertEqual(len(messages), 4)
        self.assertEqual(messages[0].text, "Hello")  # From parent branch
        self.assertEqual(messages[1].text, "How are you?")  # From parent branch
        self.assertEqual(messages[2].text, "Hi")  # From current branch
        self.assertEqual(messages[3].text, "Goodbye")  # From current branch

    def test_branch_with_no_parent(self):
        """Check function behavior when the branch has no parent."""
        messages = get_messages_up_to_branch_point(self.conversation, 0, 0)
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].text, "Hello")

    def test_empty_branch(self):
        """
        Test behavior with a branch that has no messages, including messages from all ancestor branches.
        """
        # Setup assumes branch 3 is an empty child of branch 1, which is a child of branch 0
        self.conversation.branches.append(Branch(id=3, parent_branch_id=1, messages=[]))
        messages = get_messages_up_to_branch_point(self.conversation, 3, 0)

        # Print messages for clarity in debugging
        print("Collected Messages:")
        for msg in messages:
            print(f"Message from Branch {msg.user_id}: {msg.text}")

        # Expecting messages from all ancestor branches (4 messages from branches 0 and 1)
        self.assertEqual(len(messages), 4, f"Expected 4 messages, got {len(messages)}")

    def test_message_id_beyond_current_messages(self):
        """Test behavior when message ID is beyond the last message's ID."""
        messages = get_messages_up_to_branch_point(self.conversation, 0, 10)
        self.assertEqual(
            len(messages), 2
        )  # It should return all messages despite the high message ID

    def test_loop_prevention(self):
        """Ensure no infinite loops occur if branches incorrectly reference each other."""
        # This test depends on the setup for potential loops, modify if your implementation risks
        # this.
        pass  # Implementation specific, shown as a placeholder


if __name__ == "__main__":
    unittest.main()
