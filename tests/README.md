# 🧪 Test Suite - Enhanced Chatbot Library

Comprehensive test suite for the modernized chatbot library with MCP tool integration.

## 🚀 Quick Start

### Running All Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/chatbot_library --cov-report=html

# Run specific test categories
pytest -m unit          # Unit tests only
pytest -m integration   # Integration tests only
pytest -m "not slow"    # Skip slow tests
```

### Running Specific Test Files
```bash
# Conversation models
pytest tests/models/test_conversation.py

# MCP tool system
pytest tests/tools/test_mcp_tool_registry.py
pytest tests/tools/test_builtin_tools.py

# Integration tests
pytest tests/integration/
```

## 📁 Test Structure

```
tests/
├── conftest.py                          # Shared fixtures and configuration
├── pytest.ini                           # Pytest configuration
├── README.md                           # This file
│
├── models/                             # Data model tests
│   └── test_conversation.py         # Conversation structure tests
│
├── tools/                              # Tool system tests
│   ├── test_mcp_tool_registry.py       # MCP tool registry tests
│   └── test_builtin_tools.py           # Built-in tool tests
│
├── integration/                        # Integration tests
│   ├── test_conversation_manager_hotswap.py  # Hot-swapping tests
│   └── test_mcp_integration.py         # MCP integration tests
│
└── legacy/                             # Legacy test migration
    └── (old test files for reference)
```

## 🎯 Test Categories

### ✅ **Unit Tests** (`@pytest.mark.unit`)
- **Fast execution** (< 1 second each)
- **Isolated functionality**
- **No external dependencies**
- **Mock all I/O operations**

**Examples:**
- Data model validation
- Tool schema generation
- Utility functions
- Core business logic

### 🔗 **Integration Tests** (`@pytest.mark.integration`)
- **Cross-component functionality**
- **Database/file operations**
- **API integration** (with mocks)
- **End-to-end workflows**

**Examples:**
- Conversation manager operations
- Tool execution workflows
- Model hot-swapping
- Persistence and loading

### 🐌 **Slow Tests** (`@pytest.mark.slow`)
- **Performance testing**
- **Large data operations**
- **Complex scenarios**

### 🔑 **API Tests** (`@pytest.mark.requires_api`)
- **Require API keys**
- **External service calls**
- **Rate limiting considerations**

## 🧪 Test Implementation Patterns

### **Async Test Pattern**
```python
@pytest.mark.asyncio
async def test_async_operation(conversation_manager):
    """Test async operations properly."""
    result = await conversation_manager.execute_tool("test_tool", {})
    assert result.success is True
```

### **Fixture Usage Pattern**
```python
def test_with_fixtures(conversation_manager, sample_conversation):
    """Use pre-configured fixtures for consistent testing."""
    message = conversation_manager.add_message(
        sample_conversation.id, "user", "test"
    )
    assert message.conversation_id == sample_conversation.id
```

### **Mock Integration Pattern**
```python
@patch('requests.get')
async def test_external_api(mock_get, weather_tool):
    """Mock external dependencies properly."""
    mock_get.return_value.json.return_value = {"temp": 20}
    result = await weather_tool.execute("London, UK")
    assert result["temperature"] == 20
```

### **Error Testing Pattern**
```python
def test_error_handling(tool_registry):
    """Test error conditions explicitly."""
    with pytest.raises(ValueError, match="Expected error message"):
        tool_registry.execute_invalid_operation()
```

## 🛠️ Key Test Fixtures

### **Data Fixtures**
- `temp_data_dir`: Temporary directory for test data
- `sample_conversation`: Pre-built conversation with messages
- `sample_attachment`: Test image attachment
- `test_capabilities`: Various model capability configurations

### **Manager Fixtures**
- `conversation_manager`: Hot-swap conversation manager with test models
- `mcp_conversation_manager`: MCP-integrated manager with tools
- `tool_registry`: Clean tool registry for testing

### **Mock Fixtures**
- `mock_anthropic_client`: Mocked Anthropic API client
- `mock_openai_client`: Mocked OpenAI API client
- `mock_async_api_call`: Generic async API call mock

## 📊 What's Tested

### ✅ **Conversation Models**
- Dataclass structure and validation
- Serialization and deserialization
- JSON compatibility
- Relationship integrity
- Embedding support

### ✅ **MCP Tool System**
- Tool registration and discovery
- Schema generation and validation
- Function-to-tool conversion
- Decorator-based tool creation
- Async execution handling
- Error handling and recovery

### ✅ **Built-in Tools**
- Time tool (multiple formats)
- Calculator tool (safety and precision)
- Weather tool (API integration)
- Text analysis tools
- Base64 encoding/decoding

### ✅ **Hot-Swapping Manager**
- Model registration and capabilities
- Conversation creation and persistence
- Message and response handling
- Context adaptation for different models
- Statistics tracking
- Error handling

### ✅ **MCP Integration**
- Tool execution with conversation tracking
- Response generation with tool metadata
- Usage statistics and analytics
- Tool recommendation system
- Concurrent execution handling

## 🚨 Common Test Issues

### **Import Errors**
```bash
# Ensure src is in path
export PYTHONPATH="${PYTHONPATH}:src"
# Or use the conftest.py path insertion
```

### **Async Test Issues**
```python
# Use pytest-asyncio plugin
pip install pytest-asyncio

# Mark async tests properly
@pytest.mark.asyncio
async def test_async_function():
    pass
```

### **Missing Dependencies**
```bash
# Install test dependencies
pip install pytest pytest-asyncio pytest-mock pytest-cov
```

### **API Key Requirements**
```bash
# Set test API keys (for API tests only)
export ANTHROPIC_API_KEY="test_key"
export OPENAI_API_KEY="test_key"

# Or skip API tests
pytest -m "not requires_api"
```

## 📈 Test Coverage Goals

- **Unit Tests**: 90%+ coverage
- **Integration Tests**: Cover all major workflows
- **Error Paths**: Test all exception conditions
- **Edge Cases**: Boundary conditions and invalid inputs

### **Coverage Commands**
```bash
# Generate coverage report
pytest --cov=src/chatbot_library --cov-report=html

# View coverage in browser
open htmlcov/index.html

# Coverage with missing lines
pytest --cov=src/chatbot_library --cov-report=term-missing
```

## 🔄 Legacy Test Migration

The test suite has been completely modernized:

### **❌ Old Test Issues**
- Testing legacy V1 conversation structure
- No async test patterns
- Limited tool system coverage
- Broken import paths
- Outdated testing patterns

### **✅ New Test Features**
- Modern simplified conversation structure
- Comprehensive MCP tool testing
- Modern async/await patterns
- Proper fixture management
- Integration test coverage
- Performance and error testing

## 🎯 Running Specific Test Scenarios

### **Development Workflow**
```bash
# Quick unit tests during development
pytest -m unit --tb=line

# Integration tests before commit
pytest -m integration

# Full test suite before release
pytest --cov=src/chatbot_library
```

### **CI/CD Pipeline**
```bash
# Fast tests for pull requests
pytest -m "unit and not slow" --tb=short

# Full test suite for main branch
pytest --cov=src/chatbot_library --cov-fail-under=80
```

### **Local Development**
```bash
# Watch for changes and re-run tests
pytest-watch -- -m unit

# Debug failing tests
pytest -vvv -s --pdb tests/specific_test.py::test_function
```

The test suite ensures reliability, maintainability, and confidence in the modernized architecture! 🧪✨