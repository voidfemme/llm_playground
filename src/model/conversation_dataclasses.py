from dataclasses import dataclass, field
from datetime import datetime
import uuid


@dataclass
class Attachment:
    id: str
    content_type: str
    media_type: str
    data: str
    source_type: str = "base64"
    detail: str = "auto"
    url: str = ""


@dataclass
class ToolUse:
    tool_name: str
    tool_input: dict
    tool_use_id: str


@dataclass
class ToolResponse:
    tool_use_id: str
    tool_result: str


@dataclass
class Response:
    id: str
    model: str
    text: str
    timestamp: datetime
    is_error: bool = False
    attachments: list[Attachment] = field(default_factory=list)
    tool_use: ToolUse | None = None


@dataclass
class Message:
    id: int
    user_id: str
    text: str
    timestamp: datetime
    branch_id: int
    attachments: list[Attachment] = field(default_factory=list)
    response: Response | None = None
    tool_response: ToolResponse | None = None
    parent_message_id: int | None = None


@dataclass
class Branch:
    id: int
    parent_branch_id: int | None = None
    parent_message_id: int | None = None
    messages: list[Message] = field(default_factory=list)

    def __eq__(self, __value) -> bool:
        if isinstance(__value, Branch):
            return (
                self.id == __value.id
                and self.parent_branch_id == __value.parent_branch_id
                and self.parent_message_id == __value.parent_message_id
                and self.messages == __value.messages
            )
        return False


@dataclass
class Conversation:
    id: str
    title: str
    branches: list[Branch] = field(default_factory=list)
