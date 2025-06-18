# 📚 Examples

This directory contains practical examples demonstrating different features of the Enhanced Chatbot Library.

## 🚀 Quick Start

### 1. Basic Usage
```bash
python basic_usage.py
```
Demonstrates the simplified conversation structure with linear messages and response-level branching.

### 2. Image Input Support
```bash
python image_input_example.py
```
Shows how to handle image inputs with vision-capable models and fallback descriptions.

### 3. Model Hot-Swapping
```bash
python hotswap_models_example.py
```
Demonstrates switching between models mid-conversation with automatic adaptation.

### 4. Semantic Search
```bash
python semantic_search_example.py
```
Shows conversation pair embeddings and semantic search functionality.

### 5. Multiple Response Branching
```bash
python multiple_responses_example.py
```
Demonstrates response-level branching with different models for the same message.

### 6. Conversation Pair Embeddings
```bash
python conversation_pairs_example.py
```
Shows how message/response pairs are embedded for semantic search.

### 7. MCP Server Integration
```bash
python mcp_server_example.py
```
Example of Model Context Protocol server implementation (future feature).

## 🎛️ Interactive UI

For a full interactive experience, use the Chainlit web interface:

```bash
# Working UI with interactive elements
chainlit run ../chainlit_ui_working.py

# Simple command-based UI
chainlit run ../chainlit_ui_simple.py
```

## 📋 Prerequisites

1. **Install Dependencies**:
   ```bash
   pip install -r ../requirements.txt
   ```

2. **Set Up API Keys** (`.env` file):
   ```bash
   ANTHROPIC_API_KEY=your_anthropic_key_here
   OPENAI_API_KEY=your_openai_key_here
   ```

3. **Optional: Install Chainlit**:
   ```bash
   pip install chainlit
   ```

## 🔧 Example Features

### Core Functionality
- ✅ **Modern Conversation Structure**: Simplified linear messages with response branching
- ✅ **Multiple AI Providers**: Anthropic Claude, OpenAI GPT, Demo models
- ✅ **Image Support**: Upload and analyze images with vision models
- ✅ **Model Hot-Swapping**: Switch models mid-conversation
- ✅ **Response Branching**: Multiple AI responses per user message

### Advanced Features
- ✅ **Semantic Search**: Find similar conversation exchanges
- ✅ **Conversation Adaptation**: Automatic model capability adaptation
- ✅ **Usage Analytics**: Track model performance and costs
- ✅ **Embedding Support**: Per-conversation-pair embeddings

### UI Features
- ✅ **Interactive Controls**: Dropdowns, sliders, settings panels
- ✅ **Real-time Settings**: Adjust parameters without page refresh
- ✅ **Visual Feedback**: Model capabilities, usage stats, suggestions
- ✅ **Action Buttons**: Per-message regeneration and alternatives

## 🎯 Next Steps

After running the examples:

1. **Explore the Library**: Check out `src/chatbot_library/` for implementation details
2. **Read Documentation**: See `docs/` for architecture and API documentation
3. **Try the Web UI**: Use the Chainlit interface for the best experience
4. **Build Your Own**: Use the examples as templates for your applications

## 🐛 Troubleshooting

- **Import Errors**: Ensure you're in the project root and have installed dependencies
- **API Errors**: Check your `.env` file has valid API keys
- **No Models Available**: Verify API keys are set correctly
- **Performance Issues**: Try demo models for testing without API costs

For more help, see the main README and documentation files.