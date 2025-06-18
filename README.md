# 🧠 CogniFlow

A modern Python library for building sophisticated conversational AI applications with cognitive intelligence and workflow automation. Features advanced prompt management, thinking modes, tool integration, multiple LLM providers, hot-swapping models, semantic search, and more.

![Python](https://img.shields.io/badge/Python-3.8+-blue) ![License](https://img.shields.io/badge/License-MIT-green) ![Models](https://img.shields.io/badge/Models-Claude%20%7C%20GPT-purple)

## ✨ Key Features

### 🧠 Advanced AI Capabilities
- 🎯 **Prompt Management**: Dynamic templates with variables, functions, and conditional logic
- 🤔 **Thinking Modes**: Structured AI reasoning (step-by-step, analytical, pros/cons, creative)
- 🛠️ **Tool Integration**: MCP-compatible tools with iterative execution chains
- 🔄 **Model Hot-Swapping**: Switch between AI models mid-conversation

### 💡 Smart Features  
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

#### Basic Usage
```python
from src.chatbot_library.core.conversation_manager import ConversationManager
from src.chatbot_library.adapters.chatbot_adapter import ChatbotCapabilities

# Initialize with hot-swapping capabilities
manager = ConversationManager("data/conversations")

# Create conversation and get responses
conversation = manager.create_conversation("AI Discussion")
message = manager.add_message(conversation.id, "user", "Explain quantum computing")
response = manager.add_response_with_hotswap(
    conversation.id, 
    message.id,
    "claude-3-5-sonnet",
    api_function=your_api_call
)
```

#### Advanced Usage with Prompt Management
```python
from src.chatbot_library.core.prompt_conversation_manager import PromptConversationManager
from src.chatbot_library.prompts import ThinkingMode

# Initialize enhanced conversation manager
manager = PromptConversationManager("data/conversations")

# Create conversation with prompt template and thinking mode
conversation_id = manager.create_conversation_with_prompt(
    title="Code Review Assistant",
    system_template_id="system_coding",
    thinking_mode=ThinkingMode.ANALYTICAL,
    prompt_variables={"language": "Python", "focus": "security"}
)

# Add message with thinking mode
message = manager.add_message_with_thinking(
    conversation_id=conversation_id,
    user_id="developer",
    text="Review this function for security issues",
    thinking_mode=ThinkingMode.STEP_BY_STEP
)

# Execute tools with iterative chains
result = await manager.execute_tool_chain(
    initial_tool="analyze_code",
    initial_parameters={"code": code_snippet},
    conversation_id=conversation_id,
    max_iterations=5
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

### Prompt Management System
```python
# Create dynamic templates with variables and thinking modes
from src.chatbot_library.prompts import TemplateManager, PromptTemplate, ThinkingMode

manager = TemplateManager()
template = PromptTemplate(
    id="code_review",
    name="Code Review Assistant", 
    template="Review this {language} code for {focus_areas}: {code}",
    variables=["language", "focus_areas", "code"],
    category="coding"
)
manager.add_template(template)
```

### Thinking Modes
```python
# Enable structured AI reasoning
conversation_id = manager.create_conversation_with_prompt(
    title="Analysis Task",
    thinking_mode=ThinkingMode.STEP_BY_STEP  # or ANALYTICAL, PROS_CONS, CREATIVE
)
```

### Tool Integration & Iterative Execution
```python
# Chain multiple tools together automatically
result = await manager.execute_tool_chain(
    initial_tool="web_search",
    initial_parameters={"query": "latest AI research"},
    max_iterations=5  # Allow tools to call other tools
)
```

### Model Hot-Swapping
```python
# Switch models mid-conversation with automatic adaptation
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

## 📖 Documentation

### 📚 Complete Documentation
- **[Getting Started](docs/getting-started.md)**: Quick start guide with examples
- **[Architecture Overview](docs/architecture.md)**: System design and components
- **[Prompt Management](docs/prompt-management.md)**: Complete template system guide
- **[Documentation Index](docs/README.md)**: Full documentation structure

### 🔧 Technical Guides  
- **[Installation Guide](docs/installation.md)**: Detailed setup instructions
- **[Conversation Manager](docs/conversation_manager.md)**: Core functionality guide
- **[Chainlit UI Guide](docs/CHAINLIT_README.md)**: Web interface documentation
- **[Project Structure](PROJECT_STRUCTURE.md)**: File organization and cleanup
- **[Contributing](docs/contributing.md)**: Development guidelines

### 🎯 Key Features
- **Prompt Templates**: Dynamic prompts with variables, functions, and conditional logic
- **Thinking Modes**: Step-by-step, analytical, pros/cons, and creative reasoning patterns
- **Tool Integration**: MCP-compatible tools with iterative execution chains
- **Advanced Conversation Management**: Hot-swapping, branching, and semantic search

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact

- Email: rosemkatt@gmail.com
- Github: voidfemme
