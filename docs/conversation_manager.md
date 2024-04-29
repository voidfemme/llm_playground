# ConversationManager

The `ConversationManager` class is the core component of the chatbot application. It handles the management of conversations, including creating, retrieving, updating, and deleting conversations. It also handles the generation of responses using the specified chatbot strategy.

## Responsibilities

The main responsibilities of the `ConversationManager` are:

- Loading and saving conversations from/to the data directory.
- Creating new conversations with unique IDs and titles.
- Retrieving conversations by their ID.
- Adding messages to a conversation branch and generating responses using the selected chatbot strategy.
- Regenerating responses for a specific message in a conversation branch.
- Deleting conversations.
- Renaming conversations.

## Usage

### Initialization

To initialize a `ConversationManager`, you need to provide the following parameters:

- `chatbot_manager`: An instance of the `ChatbotManager` class for managing chatbot strategies.
- `tool_manager`: An instance of the `ToolManager` class for managing tools used by the chatbot.
- `conversation_utils`: An instance of the `ConversationUtils` class for utility functions.
- `data_dir`: The directory where conversation data will be stored.

Example:

```python
conversation_manager = ConversationManager(
    chatbot_manager=chatbot_manager,
    tool_manager=tool_manager,
    conversation_utils=conversation_utils,
    data_dir="path/to/data/directory"
)
```

### Creating a Conversation

To create a new conversation, use the `create_conversation` method:

```python
conversation = conversation_manager.create_conversation(
    conversation_id="unique_id",
    title="Conversation Title"
)
```

### Retrieving a Conversation

To retrieve a conversation by its ID, use the `get_conversation` method:

```python
conversation = conversation_manager.get_conversation(conversation_id="conversation_id")
```

### Adding a Message

To add a message to the conversation branch and generate a response, use the `add_message`
method:

```python
message = conversation_manager.add_message(
    conversation_id="conversation_id",
    branch_id=branch_id,
    user_id="user_id",
    text="message text",
    current_chatbot="chatbot_strategy"
)
```

### Regenerating a Response

To regenerate the response for a specific message in a conversation branch, use the
`regenerate_response` method:

```python
branch, message = conversation_manager.regenerate_response(
    conversation_id="conversation_id",
    branch_id=branch_id,
    message_id=message_id,
    current_chatbot="chatbot_strategy"
)
```

### Deleting a Conversation

To delete a conversation, use the `delete_conversation` method:

```python
conversation_manager.delete_conversation(conversation_id="conversation_id")
```

### Renaming a Conversation

To rename a conversation, use the `rename_conversation` method:

```python
conversation_manager.rename_conversation(
    conversation_id="conversation_id",
    new_title="New Conversation Title"
)
```

### Error Handling

The `ConversationManager` raises specific exceptions for different error scenarios:

- `ConversationNotFoundError`: Raised when a conversation with the specified ID is not
  found.
- `BranchNotFoundError`: Raised when a branch with the specified ID is not found in a
  conversation.
- `MessageNotFoundError`: Raised when a message with the specified ID is not found in
  a branch.
- `InvalidConversationDataError`: Raised when the loaded conversation data is invalid
  or missing required fields.
- `SaveConversationError`: Raised when an error occurs while saving a conversation.

Make sure to handle these exceptions appropriately in your code.

### Logging

The `ConversationManager` logs various events and errors using the Python logging module.
The logs are stored in the `LOG_FILE_PATH` specified in the `file_logger.py` module.

You can view these log files to track the activity and troubleshoot any issues that may
occur during the execution of the chatbot application.
