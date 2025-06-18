# Getting Started

This guide will help you set up and use CogniFlow for building conversational AI applications with cognitive intelligence and workflow automation, including prompt management, thinking modes, and tool integration.

## 🚀 Quick Start

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd llm_playground
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up environment variables**
```bash
# Copy environment template
cp .env.example .env

# Edit .env with your API keys
export OPENAI_API_KEY="your-openai-key"
export ANTHROPIC_API_KEY="your-anthropic-key"
export OPENWEATHER_API_KEY="your-weather-key"  # Optional for weather tools
```

### Basic Usage

#### Simple Conversation

```python
from chatbot_library.core.conversation_manager import ConversationManager

# Initialize conversation manager
manager = ConversationManager(data_dir="./conversations")

# Create a new conversation
conversation_id = manager.create_conversation("My First Chat")

# Add a message
message = manager.add_message(
    conversation_id=conversation_id,
    user_id="user1", 
    text="Hello! How are you?"
)

# Generate response (requires model setup - see below)
response = manager.generate_response(
    conversation_id=conversation_id,
    message_id=message.id,
    model="gpt-3.5-turbo"
)

print(response.text)
```

#### With Prompt Management and Thinking Modes

```python
from chatbot_library.core.prompt_conversation_manager import PromptConversationManager
from chatbot_library.prompts import ThinkingMode

# Initialize enhanced conversation manager
manager = PromptConversationManager(data_dir="./conversations")

# Create conversation with prompt configuration
conversation_id = manager.create_conversation_with_prompt(
    title="Coding Assistant Chat",
    system_template_id="system_coding",
    thinking_mode=ThinkingMode.STEP_BY_STEP,
    prompt_variables={"language": "Python", "experience": "intermediate"}
)

# Add message with thinking mode
message = manager.add_message_with_thinking(
    conversation_id=conversation_id,
    user_id="developer1",
    text="How do I implement a binary search algorithm?",
    thinking_mode=ThinkingMode.STEP_BY_STEP
)

print(f"Message created: {message.id}")
print(f"Thinking mode: {message.thinking_mode}")
```

## 🔧 Configuration

### Model Setup

#### OpenAI Models

```python
from chatbot_library.adapters.openai_api_adapter import OpenAIAdapter
from chatbot_library.adapters.chatbot_adapter import ChatbotParameters, ChatbotCapabilities

# Configure OpenAI model
openai_params = ChatbotParameters(
    model_name="gpt-4",
    display_name="GPT-4",
    system_message="You are a helpful assistant.",
    max_tokens=2000,
    stop_sequences=[],
    temperature=0.7,
    tools=[],
    capabilities=ChatbotCapabilities(
        function_calling=True,
        image_understanding=True,
        supported_images=["jpeg", "png", "gif", "webp"]
    ),
    # Prompt template support
    system_template_id="system_default",
    thinking_mode="none",
    enable_thinking_trace=True
)

# Create adapter
openai_adapter = OpenAIAdapter(openai_params, api_key="your-openai-key")

# Register with manager
manager.register_model("gpt-4", openai_adapter)
```

#### Anthropic Models

```python
from chatbot_library.adapters.anthropic_api_adapter import AnthropicAdapter

# Configure Claude model
claude_params = ChatbotParameters(
    model_name="claude-3-sonnet-20240229",
    display_name="Claude 3 Sonnet",
    system_message="You are Claude, a helpful AI assistant.",
    max_tokens=4000,
    stop_sequences=[],
    temperature=0.7,
    tools=[],
    capabilities=ChatbotCapabilities(
        function_calling=True,
        image_understanding=True,
        supported_images=["jpeg", "png", "gif", "webp"]
    ),
    # Enhanced with thinking mode support
    thinking_mode="analytical",
    enable_thinking_trace=True
)

# Create adapter
claude_adapter = AnthropicAdapter(claude_params, api_key="your-anthropic-key")

# Register with manager
manager.register_model("claude-3-sonnet", claude_adapter)
```

### Prompt Templates

#### Using Built-in Templates

```python
# List available templates
templates = manager.get_available_templates()
print("System templates:", templates['system_templates'])
print("Thinking modes:", templates['thinking_modes'])

# Use built-in coding template
conversation_id = manager.create_conversation_with_prompt(
    title="Python Development",
    system_template_id="system_coding",
    thinking_mode=ThinkingMode.STEP_BY_STEP
)
```

#### Creating Custom Templates

```python
# Create a custom template
template_id = manager.create_custom_template(
    name="API Documentation Helper",
    description="Helps write clear API documentation",
    template="""You are a technical writing expert specializing in API documentation.

Task: Create documentation for the {api_type} API endpoint
Endpoint: {endpoint}
Method: {http_method}
Purpose: {purpose}

Include:
- Clear description
- Parameters and types
- Example requests/responses
- Error cases
- {additional_requirements}""",
    category="documentation",
    variables=["api_type", "endpoint", "http_method", "purpose", "additional_requirements"],
    tags=["api", "documentation", "technical_writing"]
)

# Test the template
result = manager.test_template(template_id, {
    "api_type": "REST",
    "endpoint": "/users/{id}",
    "http_method": "GET",
    "purpose": "Retrieve user information",
    "additional_requirements": "Rate limiting information"
})
print(result)
```

### Tool Integration

#### Basic Tool Setup

```python
from chatbot_library.core.mcp_integration import MCPConversationManager

# Initialize with tool support
manager = MCPConversationManager(data_dir="./conversations")

# List available tools
tools = manager.get_available_tools()
for tool in tools:
    print(f"Tool: {tool['name']} - {tool['description']}")

# Execute a tool
result = await manager.execute_tool(
    tool_name="calculate",
    parameters={"expression": "15 * 4 + 8"},
    conversation_id=conversation_id,
    message_id=message.id
)
print(f"Calculation result: {result.result}")
```

#### Iterative Tool Chains

```python
# Execute a tool chain
result = await manager.execute_tool_chain(
    initial_tool="analyze_and_search",
    initial_parameters={"text": "Calculate the fibonacci sequence for n=10"},
    conversation_id=conversation_id,
    message_id=message.id,
    max_iterations=5
)

print(f"Chain completed: {result.success}")
print(f"Total tools executed: {result.total_iterations}")
print(f"Final result: {result.final_result}")
```

## 🎯 Common Use Cases

### 1. Code Review Assistant

```python
# Set up for code review
conversation_id = manager.create_conversation_with_prompt(
    title="Code Review Session",
    system_template_id="system_coding",
    thinking_mode=ThinkingMode.ANALYTICAL,
    prompt_variables={
        "focus": "security and performance",
        "language": "Python",
        "review_depth": "thorough"
    }
)

# Add code for review
message = manager.add_message_with_thinking(
    conversation_id=conversation_id,
    user_id="developer",
    text="""Please review this function:

```python
def process_user_data(user_input):
    data = eval(user_input)  # Potential security issue
    result = []
    for item in data:
        result.append(item * 2)
    return result
```""",
    thinking_mode=ThinkingMode.ANALYTICAL
)
```

### 2. Research Assistant

```python
# Set up for research tasks
conversation_id = manager.create_conversation_with_prompt(
    title="Research Project",
    system_template_id="system_analysis", 
    thinking_mode=ThinkingMode.PROS_CONS,
    prompt_variables={
        "research_depth": "comprehensive",
        "citation_style": "APA",
        "audience": "academic"
    }
)

# Research query with thinking mode
message = manager.add_message_with_thinking(
    conversation_id=conversation_id,
    user_id="researcher",
    text="What are the advantages and disadvantages of microservices architecture?",
    thinking_mode=ThinkingMode.PROS_CONS
)
```

### 3. Creative Writing Assistant

```python
# Set up for creative tasks
conversation_id = manager.create_conversation_with_prompt(
    title="Creative Writing",
    thinking_mode=ThinkingMode.CREATIVE,
    prompt_variables={
        "genre": "science fiction",
        "tone": "optimistic",
        "target_audience": "young adult"
    }
)

# Creative writing prompt
message = manager.add_message_with_thinking(
    conversation_id=conversation_id,
    user_id="writer",
    text="Help me brainstorm ideas for a story about AI consciousness in the year 2080.",
    thinking_mode=ThinkingMode.CREATIVE
)
```

### 4. Problem-Solving Assistant

```python
# Set up for problem solving
conversation_id = manager.create_conversation_with_prompt(
    title="Problem Solving",
    thinking_mode=ThinkingMode.STEP_BY_STEP,
    prompt_variables={
        "approach": "systematic",
        "detail_level": "comprehensive"
    }
)

# Problem-solving with step-by-step thinking
message = manager.add_message_with_thinking(
    conversation_id=conversation_id,
    user_id="student",
    text="I need to optimize my web application's database queries. It's running slowly with large datasets.",
    thinking_mode=ThinkingMode.STEP_BY_STEP
)
```

## 🔍 Monitoring and Analysis

### Conversation Analysis

```python
# Analyze conversation patterns
analysis = manager.analyze_conversation_prompts(conversation_id)
print(f"Total messages: {analysis['total_messages']}")
print(f"Thinking modes used: {analysis['thinking_modes_used']}")
print(f"Templates used: {analysis['templates_used']}")
print(f"Messages with thinking: {analysis['messages_with_thinking']}")
```

### Tool Usage Statistics

```python
# Get tool usage statistics
tool_stats = manager.get_conversation_tool_usage(conversation_id)
print(f"Total tool executions: {tool_stats['total_tool_executions']}")
print(f"Success rate: {tool_stats['success_rate']:.2%}")
print(f"Total execution time: {tool_stats['total_execution_time']:.2f}s")

# Iterative execution stats
iterative_stats = manager.get_iterative_execution_stats(conversation_id)
print(f"Iterative executions: {iterative_stats['total_iterative_executions']}")
print(f"Average tools per chain: {iterative_stats['average_tools_per_chain']}")
```

## 🛠️ Advanced Configuration

### Custom Thinking Templates

```python
from chatbot_library.prompts.template_manager import ThinkingTemplate

# Create custom thinking template
custom_thinking = ThinkingTemplate(
    thinking_style="decision_making",
    thinking_depth="deep",
    show_reasoning=True,
    reasoning_format="structured",
    confidence_scoring=True
)

# Add to manager
manager.template_manager.add_thinking_template("decision_analysis", custom_thinking)

# Use in conversation
conversation_id = manager.create_conversation_with_prompt(
    title="Decision Making",
    thinking_template_name="decision_analysis"
)
```

### Template Management

```python
# Backup templates
backup_name = manager.backup_templates()
print(f"Templates backed up as: {backup_name}")

# Update conversation prompt config
manager.update_conversation_prompt_config(
    conversation_id,
    system_template_id="system_analysis",
    thinking_mode="analytical",
    prompt_variables={"focus": "data-driven decisions"}
)

# Get conversation config
config = manager.get_conversation_prompt_config(conversation_id)
print(f"Current config: {config}")
```

## 🚨 Error Handling

### Common Issues and Solutions

#### Model Not Registered
```python
try:
    response = manager.generate_response(conversation_id, message_id, "unknown-model")
except ValueError as e:
    print(f"Model error: {e}")
    # Register the model first or use a different model
```

#### Template Not Found
```python
try:
    template_id = "nonexistent_template"
    result = manager.test_template(template_id, {})
except ValueError as e:
    print(f"Template error: {e}")
    # Check available templates with manager.get_available_templates()
```

#### Tool Execution Failure
```python
try:
    result = await manager.execute_tool("invalid_tool", {})
except Exception as e:
    print(f"Tool execution failed: {e}")
    # Check available tools and parameters
```

## 📚 Next Steps

Now that you have the basics working:

1. **Explore Advanced Features**: Check out the [Prompt Management](prompt-management.md) guide
2. **Learn About Tools**: Read the [Tool System](tool-system.md) documentation  
3. **Try Examples**: Run the examples in the `examples/` directory
4. **Customize**: Create your own templates and thinking modes
5. **Integrate**: Connect to your application or UI

For more detailed information, see the complete documentation in the `docs/` directory.