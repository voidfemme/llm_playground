# 🤖 Enhanced Chatbot Library

A modern Python library for building advanced chatbot applications with support for multiple LLM providers, hot-swapping models, semantic search, image understanding, and interactive web interfaces.

![Python](https://img.shields.io/badge/Python-3.8+-blue) ![License](https://img.shields.io/badge/License-MIT-green) ![Models](https://img.shields.io/badge/Models-Claude%20%7C%20GPT-purple)

## ✨ Key Features

- 🔄 **Model Hot-Swapping**: Switch between AI models mid-conversation
- 🖼️ **Image Understanding**: Upload and analyze images with vision models  
- 🔍 **Semantic Search**: Find similar conversations with embedding-based search
- 🌿 **Response Branching**: Multiple AI responses per message with different models
- 🎛️ **Interactive UI**: Web interface with dropdowns, sliders, and real-time controls
- 📊 **Usage Analytics**: Track model performance, costs, and success rates

## 🚀 Quick Start

### 1. Installation

```bash
pip install -r requirements.txt
```

### 2. Set Up API Keys

Create a `.env` file:
```bash
ANTHROPIC_API_KEY=your_anthropic_key_here
OPENAI_API_KEY=your_openai_key_here
```

### 3. Try the Interactive UI

```bash
# Full interactive web interface (recommended)
chainlit run chainlit_ui_working.py

# Simple command-based interface
chainlit run chainlit_ui_simple.py
```

### 4. Use the Library Directly

```python
from src.chatbot_library.core.conversation_manager import ConversationManager
from src.chatbot_library.adapters.chatbot_adapter import ChatbotCapabilities

# Initialize with hot-swapping capabilities
manager = ConversationManager("data/conversations")

# Register models with different capabilities
manager.register_model(
    "claude-3-5-sonnet",
    ChatbotCapabilities(
        function_calling=True,
        image_understanding=True,
        supported_images=["image/png", "image/jpeg"]
    ),
    {"provider": "anthropic", "cost": "medium"}
)

# Create conversation and get responses
conversation = manager.create_conversation("AI Discussion")
message = manager.add_message(conversation.id, "user", "Explain quantum computing")
response = manager.add_response_with_hotswap(
    conversation.id, 
    message.id,
    "claude-3-5-sonnet",
    api_function=your_api_call
)

# Switch models mid-conversation
response2 = manager.add_response_with_hotswap(
    conversation.id,
    message.id, 
    "gpt-4o",
    api_function=your_api_call,
    branch_name="gpt_alternative"
)
```

## 📚 Examples

The `examples/` directory contains practical demonstrations of all library features:

```bash
# Modern simplified structure with linear messages and response branching
python examples/basic_usage.py

# Image understanding with vision models and fallback descriptions  
python examples/image_input_example.py

# Model hot-swapping with automatic conversation adaptation
python examples/hotswap_models_example.py

# Semantic search across conversation pairs
python examples/semantic_search_example.py

# Multiple AI responses per message with different models
python examples/multiple_responses_example.py

# Conversation pair embeddings for enhanced search
python examples/conversation_pairs_example.py

# Model Context Protocol server (future feature)
python examples/mcp_server_example.py
```

## 🎛️ Interactive Web Interface

The Chainlit web interface provides the best user experience:

```bash
# Recommended: Full interactive UI with dropdowns, sliders, settings
chainlit run chainlit_ui_working.py

# Alternative: Simple command-based interface
chainlit run chainlit_ui_simple.py
```

**Features:**
- 🎚️ Real-time parameter adjustment (temperature, tokens)
- 🤖 Visual model selection with capability indicators
- 💬 Conversation management and switching
- 🔄 Per-message regeneration and alternatives
- 📊 Usage statistics and cost tracking
- 🖼️ Drag-and-drop image upload
- 💡 Smart model recommendations

## 🏗️ Architecture

### Core Components

- **`conversation_manager.py`**: Main manager with model switching
- **`conversation.py`**: Simplified linear message structure with response branching
- **`conversation_adapter.py`**: Intelligent model capability adaptation
- **`chatbot_adapter.py`**: Universal interface for AI providers

### Data Structure

```python
Conversation
├── messages: List[Message]          # Linear message sequence
    ├── Message
    │   ├── text: str                # User input
    │   ├── attachments: List[Attachment]  # Images, files
    │   └── responses: List[Response]      # AI responses (branching)
    └── Response
        ├── text: str                # AI response text
        ├── model: str               # Model used
        ├── branch_name: str         # Branch identifier
        └── metadata: Dict           # Usage stats, parameters
```

## 🔧 Advanced Features

### Model Hot-Swapping
```python
# Automatically adapts conversations for different model capabilities
manager.add_response_with_hotswap(
    conversation_id, message_id, "gpt-4o",
    api_function, branch_name="vision_analysis"
)
```

### Semantic Search
```python
# Find similar conversation exchanges
results = manager.search_similar_conversations(
    "machine learning algorithms", limit=5
)
```

### Image Understanding
```python
# Upload images with automatic model routing
attachment = Attachment(
    content_type="image/png",
    data=base64_image_data,
    source_type="base64"
)
```

## 📖 Documentation

- **[Installation Guide](docs/installation.md)**: Detailed setup instructions
- **[Architecture Overview](docs/architecture.md)**: System design and components  
- **[Conversation Manager](docs/conversation_manager.md)**: Core functionality guide
- **[Chainlit UI Guide](docs/CHAINLIT_README.md)**: Web interface documentation
- **[Project Structure](PROJECT_STRUCTURE.md)**: File organization and cleanup
- **[Contributing](docs/contributing.md)**: Development guidelines

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact

- Email: rosemkatt@gmail.com
- Github: voidfemme
