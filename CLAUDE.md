# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Testing
- Run all tests: `python -m pytest tests/`
- Run specific test: `python -m pytest tests/path/to/test_file.py`
- Run tests with verbose output: `python -m pytest tests/ -v`

### Code Quality
- Format code with Black: `python -m black .`
- Check code formatting: `python -m black --check .`

### Running Examples
- Simple chatbot tester: `python examples/simple_chatbot_tester.py`
- Chainlit web interface: `chainlit run examples/chainlit_app.py`
- MCP server: `python examples/mcp_server_example.py`

### Dependencies
- Install dependencies: `pip install -r requirements.txt`
- The library requires API keys for Anthropic and OpenAI services (set as environment variables)

## Architecture Overview

This is a Python library for building chatbot applications with support for multiple LLM providers (Anthropic Claude, OpenAI GPT), tools/function calling, conversation management, and Model Context Protocol (MCP) integration.

### Core Components

**ConversationManager** (`src/chatbot_library/core/conversation_manager.py`)
- Central orchestrator for conversation lifecycle
- Manages conversation creation, retrieval, updates, and deletion
- Handles message branching and response regeneration
- Integrates with ChatbotManager and ToolManager
- Persists conversations to JSON files in `data/conversations/`

**ChatbotManager** (`src/chatbot_library/core/chatbot_manager.py`)
- Registry for chatbot adapters (Anthropic, OpenAI)
- Provides unified interface for different LLM providers
- Handles chatbot-specific capabilities and parameters

**ToolManager** (`src/chatbot_library/tools/manager.py`)
- Manages custom tools that extend chatbot capabilities
- Supports tool registration, activation/deactivation, and execution
- Includes default tools: time, weather, image generation
- Tools can be saved to favorites and have custom schemas

**MCP Server/Client** (`src/chatbot_library/mcp/`)
- Full Model Context Protocol implementation
- Exposes chatbot library functionality as MCP server
- Connects to external MCP servers as client
- Supports tools, resources, and prompts over MCP

### Data Model

**Conversation Structure** (`src/chatbot_library/models/conversation.py`)
- `Conversation`: Contains branches, metadata, and conversation history
- `Branch`: Represents conversation paths for different response variations
- `Message`: User messages with optional attachments
- `Response`: Assistant responses with potential tool usage
- `ToolUse`/`ToolResult`: Tool invocation and execution results

### Library Usage Examples

**Chainlit Web Interface** (`examples/chainlit_app.py`)
- Modern web-based chat interface using Chainlit
- Real-time conversation with chatbot selection
- Tool management and settings configuration
- No custom UI development required

**Simple CLI Example** (`examples/simple_chatbot_tester.py`)
- Command-line interface for testing chatbot functionality
- Demonstrates basic library usage patterns
- Good starting point for understanding the API

**MCP Server Example** (`examples/mcp_server_example.py`)
- Exposes chatbot library as Model Context Protocol server
- Allows integration with MCP-compatible applications
- Supports tools, resources, and prompts over MCP protocol

### Key Features

**Conversation Branching** (`src/chatbot_library/models/branching.py`)
- Support for conversation branches allowing response variations
- Branch point navigation and message history reconstruction
- Response regeneration in current or new branches

**Multi-Provider Support** (`src/chatbot_library/adapters/`)
- Unified adapter pattern for different LLM providers
- Provider-specific capabilities (function calling, image understanding)
- Consistent interface regardless of underlying provider

**Tool Integration**
- Custom tool development with schema validation
- Tool execution sandboxing and result handling
- Built-in tools for common operations

**Model Context Protocol (MCP)**
- Full MCP server implementation for exposing library functionality
- MCP client for connecting to external MCP servers
- Standard protocol for tool, resource, and prompt sharing

### Configuration

**Logging** (`data/config/logging_config.yaml`)
- Uses logkontrol for structured logging
- Separate log files for different components
- Configurable log levels and output destinations

**Data Storage**
- Conversations stored as JSON in `data/conversations/`
- Tools and settings persisted to data directory
- Environment-based API key management

### Error Handling

Custom exceptions defined in `src/chatbot_library/utils/errors.py`:
- `ConversationNotFoundError`
- `BranchNotFoundError` 
- `MessageNotFoundError`
- `InvalidConversationDataError`
- `SaveConversationError`
- `ChatbotNotFoundError`

### Library Package Structure

```
src/chatbot_library/
├── __init__.py          # Main library exports
├── core/                # Core functionality
│   ├── chatbot_manager.py
│   └── conversation_manager.py
├── adapters/            # LLM provider adapters
│   ├── chatbot_adapter.py
│   ├── anthropic_api_adapter.py
│   └── openai_api_adapter.py  
├── models/              # Data models
│   ├── conversation.py
│   ├── branching.py
│   └── conversation_utils.py
├── tools/               # Tool management
│   ├── manager.py
│   └── tools.py
├── config/              # Configuration
│   └── settings_manager.py
├── utils/               # Utilities
│   └── errors.py
└── mcp/                 # Model Context Protocol
    ├── protocol.py
    ├── server.py
    └── client.py
```