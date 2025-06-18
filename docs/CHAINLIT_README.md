# 🌐 Chainlit UI for Enhanced Chatbot Library

A modern web interface for the enhanced conversation library with hot-swapping models, semantic search, and advanced conversation management.

![Chainlit UI Features](https://img.shields.io/badge/Features-Hot--swapping%20%7C%20Semantic%20Search%20%7C%20Images-blue)

## 🎯 Features

### 💬 **Conversation Management**
- Create and manage multiple conversations
- Load existing conversations with full history
- Conversation selection and switching
- Real-time conversation statistics

### 🔄 **Model Hot-Swapping**
- Switch between AI models mid-conversation
- Support for Anthropic Claude, OpenAI GPT, and demo models
- Automatic conversation adaptation for model capabilities
- Model compatibility analysis and recommendations

### 🖼️ **Image Support**
- Upload and analyze images with vision models
- Automatic fallback to descriptions for non-vision models
- Support for PNG, JPEG, GIF, WebP formats
- Image metadata preservation

### 🔍 **Semantic Search**
- Search across all conversations semantically
- Find similar conversation exchanges
- Filter by features (images, tools, models)
- Conversation pair embeddings

### 🧠 **Intelligent Features**
- Model capability awareness
- Context adaptation for different models
- Response branching and alternative generations
- Usage tracking and success rate analytics

## 🚀 Quick Start

### 1. Install Dependencies
```bash
# Install the library dependencies
pip install -r requirements.txt

# Install Chainlit
pip install chainlit
```

### 2. Set Up API Keys
Create a `.env` file with your API keys:
```bash
ANTHROPIC_API_KEY=your_anthropic_key_here
OPENAI_API_KEY=your_openai_key_here
```

### 3. Run the Interface
```bash
chainlit run chainlit_app.py
```

### 4. Open Your Browser
Navigate to `http://localhost:8000` to access the UI.

## 🎮 Usage Guide

### Getting Started
1. **Welcome Screen**: Choose to create a new conversation or load existing ones
2. **Model Selection**: Pick your preferred AI model (capabilities shown)
3. **Start Chatting**: Type messages and get responses
4. **Switch Models**: Use `/model <name>` to change models mid-conversation

### Commands
- `/model [name]` - Switch AI model or show current
- `/branch` - Show response branches for last message  
- `/help` - Show available commands

### Available Models
The UI automatically detects and registers available models based on your API keys:

#### Anthropic Models
- **claude-3-5-sonnet** (medium cost): 📸 Images + 🔧 Tools
- **claude-3-haiku** (low cost): 📸 Images

#### OpenAI Models  
- **gpt-4o** (high cost): 📸 Images + 🔧 Tools
- **gpt-4-turbo** (medium cost): 🔧 Tools

#### Demo Models
- **demo-basic** (free): 💬 Text only

### Image Upload
1. Click the attachment button or drag images into the chat
2. Supported formats: PNG, JPEG, GIF, WebP
3. Vision models will analyze images; others get text descriptions
4. Images are stored with full metadata in conversations

### Conversation Features
- **Response Branching**: Multiple AI responses per message
- **Context Adaptation**: Conversations adapt to model capabilities
- **Semantic Search**: Find relevant conversations and exchanges
- **Statistics**: Track model usage and success rates

## 🏗️ Architecture

### Core Components

#### ConversationManagerV2HotSwap
- Manages conversations with hot-swapping capabilities
- Model registration and capability tracking
- Context adaptation for different models
- Usage statistics and analytics

#### ConversationAdapter
- Intelligent conversation transformation
- Handles images, tools, and context limits
- Model compatibility analysis
- Alternative model suggestions

#### Model Registry
- Tracks available models and their capabilities
- Capability-based routing and recommendations
- Usage statistics and success rates
- Cost and performance optimization

### Data Flow
1. **User Input** → Chainlit interface
2. **Model Selection** → Capability analysis
3. **Context Adaptation** → Model-specific formatting
4. **API Call** → Anthropic/OpenAI/Demo
5. **Response Storage** → JSON + Vector database
6. **UI Update** → Real-time display

## 🔧 Configuration

### Model Configuration
Models are automatically registered based on available API keys. You can modify model settings in `chainlit_app.py`:

```python
conversation_manager.register_model(
    "custom-model",
    ChatbotCapabilities(
        function_calling=True,
        image_understanding=False,
        supported_images=[]
    ),
    {"provider": "custom", "context_limit": 4000, "cost": "low"}
)
```

### UI Customization
- Modify welcome messages and help text
- Add custom actions and commands
- Configure model display preferences
- Customize conversation selection interface

## 📊 Features in Detail

### Hot-Swapping Models
```python
# Switch models mid-conversation
/model claude-3-haiku    # Switch to faster, cheaper model
/model gpt-4o           # Switch to vision-capable model
```

### Semantic Search
- Search: "machine learning algorithms"
- Filters: Images, tools, specific models
- Results: Ranked by similarity with context

### Response Branching
- Same message → Multiple AI responses
- Compare different models' approaches
- Follow specific conversation branches
- Analyze response quality differences

### Image Analysis
- Upload image → Automatic model selection
- Vision models: Direct analysis
- Text models: Description-based responses
- Metadata preservation and search

## 🤝 Contributing

### Adding New Models
1. Implement model adapter in `src/chatbot_library/adapters/`
2. Register model with capabilities in `chainlit_app.py`
3. Add API calling function
4. Test with conversation adaptation

### Custom Features
- Add new commands in `handle_command()`
- Implement custom actions with `@cl.action_callback`
- Extend conversation analysis features
- Add new visualization components

## 📈 Analytics and Monitoring

### Usage Statistics
- Model usage frequency and success rates
- Conversation length and complexity metrics
- Response quality and user satisfaction
- Cost optimization recommendations

### Performance Metrics
- Response times by model
- Context adaptation efficiency
- Semantic search accuracy
- Hot-swap success rates

## 🔒 Security and Privacy

### Data Storage
- Conversations stored locally in JSON format
- Vector embeddings in SQLite database
- No data sent to external services except chosen AI providers
- Full control over conversation data

### API Key Management
- Keys stored in environment variables
- No logging or persistence of sensitive data
- Secure API communication with HTTPS
- Rate limiting and error handling

## 🐛 Troubleshooting

### Common Issues
1. **No models available**: Check API keys in `.env` file
2. **Import errors**: Ensure all dependencies installed
3. **Slow responses**: Check internet connection and API quotas
4. **Image upload fails**: Verify image format and size limits

### Debug Mode
```bash
# Run with debug logging
CHAINLIT_DEBUG=true chainlit run chainlit_app.py
```

### Support
- Check console output for error messages
- Verify API key permissions and quotas
- Review conversation manager logs
- Test with demo models first

## 🎉 What's Next?

### Planned Features
- [ ] Tool/function calling integration
- [ ] Advanced conversation analytics
- [ ] Bulk conversation operations
- [ ] Export/import functionality
- [ ] Conversation templates
- [ ] Multi-user support
- [ ] Real-time collaboration
- [ ] Advanced semantic search filters

### Integration Opportunities
- Model Context Protocol (MCP) server support
- LangChain/LlamaIndex integration
- Vector database alternatives (Qdrant, Chroma)
- Enterprise authentication systems
- Cloud deployment options

---

**Built with ❤️ using Chainlit and the Enhanced Chatbot Library**

For more information about the underlying library, see the main README and documentation files.