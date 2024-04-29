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
