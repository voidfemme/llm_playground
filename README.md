# Project Title

A multi-modal, tool-enabled language model interface with built-in tools.

## Table of Contents

- [Features](#features)
- [License](#license)
- [Contact](#contact)

## Features

- Conversation Management:
  - Create new conversations with unique IDs and titles
  - Load and save conversations from/to a data directory
  - Retrieve conversations by their ID
  - Delete conversations
  - Rename conversations
- Message Handling:
  - Add messages to a conversation branch
  - Generate responses using the selected chatbot strategy
  - Regenerate responses for a specific message in a conversation branch
- Branching:
  - Create new branches in a conversation
  - Retrieve branches from a conversation based on their ID
  - Get messages up to a specified branch point, including messages from ancestor branches
  - Create a new branch for regenerating a response, copying messages up to a specified point
  - Regenerate responses in the current branch or a new branch
- Tool Management:
  - Register and manage custom tools that can be used by the chatbot
  - Add tools to favorites and activate/deactivate tools
  - Execute tools with specified input parameters
  - Process tool usage requests from the chatbot and generate tool result messages
  - Load default tools such as getting the current time, weather, and generating images
- Chatbot Integration:
  - Support for different chatbot adapters (e.g., Anthropic, OpenAI)
  - Send messages to the chatbot with or without active tools
  - Retrieve supported models, models supporting function calling, and models supporting image understanding
  - Check if the chatbot supports function calling and image understanding
  - Retrieve the list of supported image types by the chatbot
- User Interface (based on the generated UI code):
  - Tab-based interface with "Chat" and "Tools" tabs
  - Conversation List:
    - Display a list of conversations
    - Select a conversation to view its messages
  - Message Area:
    - Display messages in a scrollable area
    - Send new messages using a text input field
    - Select the chatbot strategy from a dropdown menu
  - Active Tools:
    - Display a list of active tools
  - Saved Tools:
    - Display a list of saved tools
    - View and edit tool details (name, description, input schema, function code, API key)
    - Add and remove input schema fields
    - Save and edit tools
  - Menu Bar:
    - File menu with options to create a new conversation, create a new tool, and access settings

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact

- Email: rosemkatt@gmail.com
- Github: voidfemme
