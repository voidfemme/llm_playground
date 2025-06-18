# 📁 Project Structure

Clean, organized structure for the Enhanced Chatbot Library.

```
llm_playground/
├── 📄 README.md                     # Main project documentation
├── 📄 LICENSE                       # MIT License
├── 📄 CLAUDE.md                     # Claude Code assistant instructions
├── 📄 requirements.txt              # Python dependencies
├── 📄 setup.py                      # Package setup configuration
├── 📄 logging_config.yaml           # Logging configuration
├── 📄 chainlit.md                   # Chainlit welcome page
│
├── 🎛️ chainlit_ui_working.py        # Interactive Chainlit UI (recommended)
├── 🎛️ chainlit_ui_simple.py         # Simple command-based Chainlit UI
│
├── 📂 src/                          # Main library source code
│   └── chatbot_library/
│       ├── 📂 adapters/             # AI provider adapters
│       │   ├── anthropic_api_adapter.py
│       │   ├── openai_api_adapter.py
│       │   └── chatbot_adapter.py
│       ├── 📂 core/                 # Core conversation management
│       │   ├── conversation_manager_v2_hotswap.py  # Main manager (recommended)
│       │   ├── conversation_manager_v2_enhanced_pairs.py
│       │   ├── conversation_adapter.py
│       │   └── ...
│       ├── 📂 models/               # Data structures
│       │   ├── conversation_v2.py   # V2 simplified structure (recommended)
│       │   ├── conversation.py      # Legacy structure
│       │   └── ...
│       ├── 📂 tools/                # Tool/function calling support
│       ├── 📂 config/               # Configuration management
│       ├── 📂 mcp/                  # Model Context Protocol (future)
│       └── 📂 utils/                # Utilities and helpers
│
├── 📂 examples/                     # Usage examples
│   ├── 📄 README.md                # Examples documentation
│   ├── basic_usage_v2.py           # Basic library usage
│   ├── image_input_example.py      # Image handling
│   ├── hotswap_models_example.py   # Model switching
│   ├── semantic_search_example.py  # Search functionality
│   ├── multiple_responses_example.py
│   ├── conversation_pairs_example.py
│   └── mcp_server_example.py
│
├── 📂 tests/                        # Test suites
│   ├── chatbots/                   # Adapter tests
│   ├── model/                      # Data model tests
│   ├── tools/                      # Tool functionality tests
│   └── utils/                      # Utility tests
│
├── 📂 docs/                         # Documentation
│   ├── architecture.md             # System architecture
│   ├── conversation_manager.md     # Manager documentation
│   ├── installation.md             # Setup instructions
│   ├── contributing.md             # Contribution guidelines
│   ├── CHAINLIT_README.md          # Chainlit UI documentation
│   ├── CHAINLIT_WORKING_UI.md      # Interactive UI details
│   └── UI_COMPARISON.md            # UI comparison guide
│
└── 📂 data/                         # Runtime data storage
    ├── 📂 config/                   # Configuration files
    │   └── logging_config.yaml
    ├── 📂 logs/                     # Application logs
    └── 📂 chainlit_working/         # Chainlit conversation data
        └── *.json                   # Individual conversations
```

## 🎯 Key Components

### **Recommended Entry Points**
- **Interactive UI**: `chainlit_ui_working.py` - Full interactive experience
- **Library Usage**: `examples/basic_usage_v2.py` - Core library features
- **Documentation**: `docs/` directory - Architecture and guides

### **Core Library (`src/chatbot_library/`)**
- **`core/conversation_manager_v2_hotswap.py`**: Main conversation manager with model switching
- **`models/conversation_v2.py`**: Simplified data structures
- **`adapters/`**: AI provider integrations (Anthropic, OpenAI)
- **`tools/`**: Function calling and tool integration

### **User Interfaces**
- **`chainlit_ui_working.py`**: Interactive web UI with dropdowns, sliders, settings
- **`chainlit_ui_simple.py`**: Command-based web UI for simpler usage

### **Examples (`examples/`)**
- **`basic_usage_v2.py`**: Core functionality demonstration
- **`hotswap_models_example.py`**: Model switching capabilities
- **`image_input_example.py`**: Vision model integration
- **`semantic_search_example.py`**: Search and embeddings

## 🧹 Recent Cleanup

### **Removed Obsolete Files**
- ❌ Multiple duplicate test data directories
- ❌ Root-level test and analysis files
- ❌ Duplicate Chainlit UI implementations
- ❌ Outdated example files
- ❌ Duplicate logs and misc files

### **Consolidated Structure**
- ✅ Single working Chainlit UI implementation
- ✅ Organized documentation in `docs/`
- ✅ Streamlined examples with clear purpose
- ✅ Clean data storage structure

### **Maintained Backwards Compatibility**
- ✅ Legacy conversation structure still available
- ✅ All existing APIs functional
- ✅ Migration utilities available

## 🚀 Getting Started

1. **Install**: `pip install -r requirements.txt`
2. **Configure**: Set up `.env` with API keys
3. **Try Examples**: Start with `examples/basic_usage_v2.py`
4. **Use UI**: Run `chainlit run chainlit_ui_working.py`
5. **Read Docs**: Check `docs/` for detailed information

This structure prioritizes clarity, maintainability, and ease of use while preserving all functionality.