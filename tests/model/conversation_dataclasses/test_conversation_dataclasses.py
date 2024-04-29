import unittest
from datetime import datetime
from src.model.conversation_dataclasses import (
    Attachment,
    ToolUsage,
    Response,
    Message,
    Branch,
    Conversation,
)


class TestDataclasses(unittest.TestCase):
    def setUp(self):
        self.attachment = Attachment(
            id="1",
            content_type="image/jpeg",
            media_type="image",
            data="base64_encoded_data",
            source_type="base64",
            detail="auto",
            url="http://example.com/image.jpg",
        )
        self.tool_usage = ToolUsage(
            tool_name="example_tool",
            parameters={"param1": "value1", "param2": "value2"},
            timestamp=datetime(2023, 6, 8, 12, 0, 0),
            result="Tool executed successfully",
        )
        self.response = Response(
            id="1",
            model="gpt-3",
            text="This is a response",
            timestamp=datetime(2023, 6, 8, 12, 0, 0),
            is_error=False,
            attachments=[self.attachment],
            tool_use=[self.tool_usage],
            tool_result=None,
        )
        self.message = Message(
            id=1,
            user_id="user1",
            text="This is a message",
            timestamp=datetime(2023, 6, 8, 12, 0, 0),
            attachments=[self.attachment],
            response=self.response,
            tool_usage=None,
        )
        self.branch = Branch(
            id=1, parent_branch_id=None, parent_message_id=None, messages=[self.message]
        )
        self.conversation = Conversation(
            id="conversation1", title="Test Conversation", branches=[self.branch]
        )

    def test_attachment(self):
        self.assertEqual(self.attachment.id, "1")
        self.assertEqual(self.attachment.content_type, "image/jpeg")
        self.assertEqual(self.attachment.media_type, "image")
        self.assertEqual(self.attachment.data, "base64_encoded_data")
        self.assertEqual(self.attachment.source_type, "base64")
        self.assertEqual(self.attachment.detail, "auto")
        self.assertEqual(self.attachment.url, "http://example.com/image.jpg")

    def test_tool_usage(self):
        self.assertEqual(self.tool_usage.tool_name, "example_tool")
        self.assertEqual(
            self.tool_usage.parameters, {"param1": "value1", "param2": "value2"}
        )
        self.assertEqual(self.tool_usage.timestamp, datetime(2023, 6, 8, 12, 0, 0))
        self.assertEqual(self.tool_usage.result, "Tool executed successfully")

    def test_response(self):
        self.assertEqual(self.response.id, "1")
        self.assertEqual(self.response.model, "gpt-3")
        self.assertEqual(self.response.text, "This is a response")
        self.assertEqual(self.response.timestamp, datetime(2023, 6, 8, 12, 0, 0))
        self.assertFalse(self.response.is_error)
        self.assertEqual(len(self.response.attachments), 1)
        self.assertEqual(self.response.attachments[0], self.attachment)
        self.assertEqual(len(self.response.tool_use), 1)
        self.assertEqual(self.response.tool_use[0], self.tool_usage)
        self.assertIsNone(self.response.tool_result)

    def test_message(self):
        self.assertEqual(self.message.id, 1)
        self.assertEqual(self.message.user_id, "user1")
        self.assertEqual(self.message.text, "This is a message")
        self.assertEqual(self.message.timestamp, datetime(2023, 6, 8, 12, 0, 0))
        self.assertEqual(len(self.message.attachments), 1)
        self.assertEqual(self.message.attachments[0], self.attachment)
        self.assertEqual(self.message.response, self.response)
        self.assertIsNone(self.message.tool_usage)

    def test_branch(self):
        self.assertEqual(self.branch.id, 1)
        self.assertIsNone(self.branch.parent_branch_id)
        self.assertIsNone(self.branch.parent_message_id)
        self.assertEqual(len(self.branch.messages), 1)
        self.assertEqual(self.branch.messages[0], self.message)

    def test_branch_equality(self):
        branch_copy = Branch(
            id=1, parent_branch_id=None, parent_message_id=None, messages=[self.message]
        )
        self.assertEqual(self.branch, branch_copy)
        self.assertNotEqual(self.branch, self.message)

    def test_conversation(self):
        self.assertEqual(self.conversation.id, "conversation1")
        self.assertEqual(self.conversation.title, "Test Conversation")
        self.assertEqual(len(self.conversation.branches), 1)
        self.assertEqual(self.conversation.branches[0], self.branch)


if __name__ == "__main__":
    unittest.main()
