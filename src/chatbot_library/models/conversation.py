"""
Modern conversation data model.

This uses a simplified linear message approach with response-level branching
for better maintainability and performance.
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any


@dataclass
class Attachment:
    """File or media attachment to a message."""
    id: str
    content_type: str
    media_type: str
    data: str
    source_type: str = "base64"
    detail: str = "auto"
    url: str = ""
    file_path: str = ""


@dataclass
class ToolUse:
    """Tool usage information."""
    tool_name: str
    tool_input: Dict[str, Any]
    tool_use_id: str


@dataclass
class ToolResult:
    """Result from tool execution."""
    tool_use_id: str
    tool_result: str


@dataclass
class Response:
    """
    AI response to a message.
    
    Multiple responses can exist for the same message (for regeneration/alternatives).
    """
    id: str  # UUID
    message_id: str  # UUID of parent message
    model: str  # Model used for generation
    text: str
    timestamp: datetime
    branch_name: Optional[str] = None  # "main", "alt-1", "creative", etc.
    is_error: bool = False
    attachments: List[Attachment] = field(default_factory=list)
    tool_use: Optional[ToolUse] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Ensure we have a UUID."""
        if not self.id:
            self.id = str(uuid.uuid4())


@dataclass
class Message:
    """
    A message in the conversation.
    
    Messages form a linear chain. Multiple responses can exist per message
    for regeneration or alternative response branches.
    """
    id: str  # UUID
    conversation_id: str  # UUID of parent conversation
    user_id: str
    text: str
    timestamp: datetime
    parent_message_id: Optional[str] = None  # UUID, for threading
    attachments: List[Attachment] = field(default_factory=list)
    responses: List[Response] = field(default_factory=list)
    tool_result: Optional[ToolResult] = None
    
    # Optional embedding support
    embedding: Optional[List[float]] = None
    embedding_model: Optional[str] = None
    embedding_timestamp: Optional[datetime] = None
    
    # Metadata for extensibility
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Ensure we have a UUID."""
        if not self.id:
            self.id = str(uuid.uuid4())
    
    def add_response(
        self, 
        model: str, 
        text: str, 
        branch_name: Optional[str] = None,
        **kwargs
    ) -> Response:
        """Add a response to this message."""
        response = Response(
            id=str(uuid.uuid4()),
            message_id=self.id,
            model=model,
            text=text,
            timestamp=datetime.now(),
            branch_name=branch_name,
            **kwargs
        )
        self.responses.append(response)
        return response
    
    def get_response(self, branch_name: Optional[str] = None) -> Optional[Response]:
        """Get a specific response by branch name, or the first/main response."""
        if not self.responses:
            return None
        
        if branch_name is None:
            # Return main response (no branch_name) or first response
            for response in self.responses:
                if response.branch_name is None:
                    return response
            return self.responses[0]
        
        # Find response with specific branch name
        for response in self.responses:
            if response.branch_name == branch_name:
                return response
        
        return None
    
    def get_all_branch_names(self) -> List[str]:
        """Get all unique branch names for this message's responses."""
        names = set()
        for response in self.responses:
            if response.branch_name:
                names.add(response.branch_name)
        return sorted(names)


@dataclass
class Conversation:
    """
    A conversation containing a linear sequence of messages.
    
    Branching happens at the response level, not message level.
    This greatly simplifies the data model while retaining all functionality.
    """
    id: str  # UUID
    title: str
    messages: List[Message] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Ensure we have a UUID."""
        if not self.id:
            self.id = str(uuid.uuid4())
    
    def add_message(
        self, 
        user_id: str, 
        text: str, 
        parent_message_id: Optional[str] = None,
        **kwargs
    ) -> Message:
        """Add a new message to the conversation."""
        message = Message(
            id=str(uuid.uuid4()),
            conversation_id=self.id,
            user_id=user_id,
            text=text,
            timestamp=datetime.now(),
            parent_message_id=parent_message_id,
            **kwargs
        )
        self.messages.append(message)
        self.updated_at = datetime.now()
        return message
    
    def get_message(self, message_id: str) -> Optional[Message]:
        """Get a message by ID."""
        for message in self.messages:
            if message.id == message_id:
                return message
        return None
    
    def get_conversation_context(
        self, 
        up_to_message_id: Optional[str] = None,
        branch_name: Optional[str] = None
    ) -> List[Dict[str, str]]:
        """
        Get conversation context up to a specific message.
        
        Returns a list of {"role": "user"|"assistant", "content": "text"} dicts
        suitable for API calls.
        """
        context = []
        
        for message in self.messages:
            # Add user message
            context.append({
                "role": "user", 
                "content": message.text
            })
            
            # Add AI response (if exists)
            response = message.get_response(branch_name)
            if response:
                context.append({
                    "role": "assistant",
                    "content": response.text
                })
            
            # Stop if we've reached the target message
            if up_to_message_id and message.id == up_to_message_id:
                break
        
        return context
    
    def get_thread_from_message(self, message_id: str) -> List[Message]:
        """
        Get a thread starting from a specific message using parent_message_id.
        
        This enables threading/replies within the linear structure.
        """
        thread = []
        current_id = message_id
        
        while current_id:
            message = self.get_message(current_id)
            if not message:
                break
            thread.insert(0, message)  # Prepend to maintain order
            current_id = message.parent_message_id
        
        return thread
    
    def get_all_branches(self) -> Dict[str, int]:
        """Get all response branch names and their usage counts."""
        branches = {}
        for message in self.messages:
            for response in message.responses:
                if response.branch_name:
                    branches[response.branch_name] = branches.get(response.branch_name, 0) + 1
        return branches


def conversation_to_dict(conversation: Conversation) -> Dict[str, Any]:
    """Convert a Conversation to a JSON-serializable dictionary."""
    from dataclasses import asdict
    
    data = asdict(conversation)
    
    # Convert datetime objects to ISO strings
    if isinstance(data['created_at'], datetime):
        data['created_at'] = data['created_at'].isoformat()
    if isinstance(data['updated_at'], datetime):
        data['updated_at'] = data['updated_at'].isoformat()
    
    # Convert message timestamps
    for message_data in data['messages']:
        if isinstance(message_data['timestamp'], datetime):
            message_data['timestamp'] = message_data['timestamp'].isoformat()
        
        # Convert response timestamps
        for response_data in message_data['responses']:
            if isinstance(response_data['timestamp'], datetime):
                response_data['timestamp'] = response_data['timestamp'].isoformat()
    
    return data


def conversation_from_dict(data: Dict[str, Any]) -> Conversation:
    """Create a Conversation from a dictionary."""
    from dateutil.parser import parse as parse_datetime
    
    # Parse timestamps
    if 'created_at' in data and isinstance(data['created_at'], str):
        data['created_at'] = parse_datetime(data['created_at'])
    if 'updated_at' in data and isinstance(data['updated_at'], str):
        data['updated_at'] = parse_datetime(data['updated_at'])
    
    # Parse message data
    messages = []
    for message_data in data.get('messages', []):
        if 'timestamp' in message_data and isinstance(message_data['timestamp'], str):
            message_data['timestamp'] = parse_datetime(message_data['timestamp'])
        
        # Parse response data
        responses = []
        for response_data in message_data.get('responses', []):
            if 'timestamp' in response_data and isinstance(response_data['timestamp'], str):
                response_data['timestamp'] = parse_datetime(response_data['timestamp'])
            
            # Create Response object
            response = Response(**response_data)
            responses.append(response)
        
        # Create Message object
        message_data['responses'] = responses
        message = Message(**message_data)
        messages.append(message)
    
    # Create Conversation object
    data['messages'] = messages
    return Conversation(**data)


def create_conversation_pair_embedding(message: Message, response: Response) -> str:
    """
    Create a text representation suitable for embedding of a message/response pair.
    
    This combines the user message and AI response into a single text that can
    be embedded for semantic search and similarity matching.
    
    Args:
        message: The user message
        response: The AI response
    
    Returns:
        String suitable for embedding generation
    """
    # Combine user message and response with clear separation
    pair_text = f"User: {message.text}\n\nAssistant: {response.text}"
    
    # Add any attachment descriptions
    if message.attachments:
        attachment_descriptions = []
        for attachment in message.attachments:
            attachment_descriptions.append(f"[{attachment.content_type}]")
        pair_text += f"\n\nAttachments: {', '.join(attachment_descriptions)}"
    
    # Add tool usage information if present
    if response.tool_use:
        pair_text += f"\n\nTool used: {response.tool_use.tool_name}"
    
    return pair_text