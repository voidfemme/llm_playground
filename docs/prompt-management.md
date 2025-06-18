# Prompt Management System

The Prompt Management System is a comprehensive framework for creating, managing, and executing dynamic prompts with advanced features like thinking modes, template variables, and conditional logic.

## 📋 Overview

The prompt management system consists of four main components:

1. **Template Manager**: Manages prompt templates and their lifecycle
2. **Template Engine**: Renders templates with variables and functions
3. **Prompt Builder**: Constructs complete prompts with thinking modes
4. **Template Store**: Handles persistent storage and backup

## 🎯 Core Concepts

### Prompt Templates

Prompt templates are reusable text patterns with variables and metadata:

```python
from chatbot_library.prompts import PromptTemplate

template = PromptTemplate(
    id="coding_assistant",
    name="Coding Assistant",
    description="Template for coding assistance",
    template="""You are an expert {language} programmer.
Task: {task}
Requirements: {requirements}
Focus on: {focus_areas}""",
    variables=["language", "task", "requirements", "focus_areas"],
    category="coding",
    tags=["programming", "development"]
)
```

### Thinking Modes

Thinking modes enable AI models to use structured reasoning patterns:

```python
from chatbot_library.prompts import ThinkingMode

# Available thinking modes
ThinkingMode.STEP_BY_STEP    # Systematic step-by-step analysis
ThinkingMode.ANALYTICAL      # Structured analytical thinking
ThinkingMode.PROS_CONS       # Advantage/disadvantage analysis
ThinkingMode.CREATIVE        # Creative and innovative thinking
ThinkingMode.CUSTOM          # User-defined thinking patterns
```

### Template Variables

Templates support dynamic content through variables:

```python
# Simple variables
"Hello {name}! Welcome to {platform}."

# Nested object access
"User {user.name} has role {user.role} in {organization.name}."

# Built-in functions
"Generated on {today()} at {time()}."
"Text length: {len(content)} characters."
```

## 🛠️ Template Manager

The Template Manager handles template CRUD operations and organization.

### Basic Operations

```python
from chatbot_library.prompts import TemplateManager

manager = TemplateManager()

# Create template
template = PromptTemplate(
    id="custom_template",
    name="Custom Template",
    description="A custom template",
    template="Custom content with {variable}",
    variables=["variable"]
)

# Add template
manager.add_template(template)

# Retrieve template
retrieved = manager.get_template("custom_template")

# Update template
manager.update_template("custom_template", 
                       description="Updated description")

# Delete template
manager.delete_template("custom_template")
```

### Organization and Search

```python
# Get templates by category
system_templates = manager.get_templates_by_category("system")
coding_templates = manager.get_templates_by_category("coding")

# Get templates by tag
tutorial_templates = manager.get_templates_by_tag("tutorial")

# Search templates
results = manager.search_templates("python coding")

# List all templates
all_templates = manager.list_templates()
```

### Template Import/Export

```python
# Export templates
manager.export_templates("my_templates.json", ["template1", "template2"])

# Import templates
imported_count = manager.import_templates("my_templates.json", overwrite=True)
```

## 🔧 Template Engine

The Template Engine renders templates with variables, functions, and logic.

### Basic Rendering

```python
from chatbot_library.prompts import TemplateEngine, TemplateContext

engine = TemplateEngine()

# Create context with variables
context = TemplateContext(variables={
    "name": "Alice",
    "task": "code review",
    "language": "Python"
})

# Render template
template_text = "Hello {name}! Your {language} {task} task is ready."
result = engine.render_template(template_text, context)
# Output: "Hello Alice! Your Python code review task is ready."
```

### Built-in Functions

```python
# Date and time functions
template = "Generated on {today()} at {now()}"

# String manipulation
template = "Name: {upper(name)} | Title: {title(job_title)}"

# List formatting
template = "Items: {format_list(items, 'bullet')}"
context = TemplateContext(variables={
    "items": ["apple", "banana", "cherry"]
})
# Output: "Items: • apple\n• banana\n• cherry"

# Conditional logic
template = "Status: {conditional(active, 'Online', 'Offline')}"

# Default values
template = "Welcome {default(name, 'Guest')}!"
```

### Advanced Features

#### Conditional Blocks
```python
template = """
{if user.premium}
Premium features available:
- Advanced analytics
- Priority support
{endif}
"""
```

#### Loops
```python
template = """
Team members:
{for member in team}
- {member.name} ({member.role})
{endfor}
"""
```

#### Custom Functions
```python
def calculate_score(points, max_points):
    return round((points / max_points) * 100, 1)

engine.register_function("score", calculate_score)

template = "Your score: {score(points, max_points)}%"
```

## 🧠 Thinking Modes

Thinking modes provide structured reasoning patterns for AI models.

### Built-in Thinking Templates

```python
from chatbot_library.prompts import ThinkingTemplate

# Step-by-step thinking
step_template = ThinkingTemplate(
    thinking_style="step_by_step",
    thinking_depth="deep",
    show_reasoning=True,
    reasoning_format="structured"
)

# Creative thinking
creative_template = ThinkingTemplate(
    thinking_style="creative",
    thinking_depth="medium",
    show_reasoning=True,
    reasoning_format="natural"
)

# Generate thinking prompt
thinking_prompt = step_template.to_thinking_prompt()
```

### Custom Thinking Templates

```python
# Create custom thinking template
custom_thinking = ThinkingTemplate(
    thinking_style="pros_cons",
    thinking_depth="deep",
    show_reasoning=True,
    reasoning_format="structured",
    confidence_scoring=True
)

# Add to manager
manager.add_thinking_template("detailed_analysis", custom_thinking)
```

## 🏗️ Prompt Builder

The Prompt Builder creates complete prompts with system messages, thinking modes, and context integration.

### Basic Prompt Building

```python
from chatbot_library.prompts import PromptBuilder, PromptConfiguration

builder = PromptBuilder(template_manager, template_engine)

# Create configuration
config = PromptConfiguration(
    system_template_id="coding_assistant",
    thinking_mode=ThinkingMode.STEP_BY_STEP,
    variables={"language": "Python", "focus": "performance"}
)

# Build prompt
built_prompt = builder.build_prompt(
    user_message="How do I optimize this function?",
    config=config
)

# Access components
print(built_prompt.system_message)
print(built_prompt.user_message)
print(built_prompt.thinking_instructions)
```

### Task-Specific Configurations

```python
# Pre-configured for coding tasks
coding_config = builder.create_config_for_task("coding")

# Pre-configured for analysis
analysis_config = builder.create_config_for_task("analysis")

# Pre-configured for creative tasks
creative_config = builder.create_config_for_task("creative")
```

### Advanced Configuration

```python
config = PromptConfiguration(
    system_template_id="advanced_assistant",
    thinking_mode=ThinkingMode.ANALYTICAL,
    thinking_template_name="deep_analysis",
    include_conversation_summary=True,
    include_user_context=True,
    custom_instructions="Focus on practical solutions.",
    variables={
        "expertise_level": "expert",
        "response_style": "detailed",
        "include_examples": True
    }
)
```

### Context Integration

```python
# Conversation context
conversation_context = {
    "message_count": 5,
    "topics": ["Python", "optimization", "performance"],
    "last_model": "gpt-4",
    "duration": "15 minutes"
}

# User context
user_context = {
    "name": "Alice",
    "role": "senior_developer",
    "experience": "5 years",
    "preferences": ["detailed_explanations", "code_examples"]
}

# Build with context
built_prompt = builder.build_prompt(
    user_message="Help me optimize this code",
    config=config,
    conversation_context=conversation_context,
    user_context=user_context
)
```

## 💾 Template Store

The Template Store handles persistent storage, backup, and synchronization.

### Storage Operations

```python
from chatbot_library.prompts import TemplateStore

store = TemplateStore("/path/to/templates")

# Save template
store.save_template(template)

# Load template
loaded = store.load_template("template_id")

# Delete template
store.delete_template("template_id")

# List all templates
template_ids = store.list_templates()
```

### Collections

```python
# Save template collection
templates = [template1, template2, template3]
metadata = {"author": "team", "version": "1.0", "purpose": "coding"}
store.save_template_collection("coding_templates", templates, metadata)

# Load collection
loaded_templates = store.load_template_collection("coding_templates")

# List collections
collections = store.list_collections()
```

### Backup and Restore

```python
# Create backup
backup_name = store.create_backup("manual_backup_v1")

# List backups
backups = store.list_backups()

# Restore backup
store.restore_backup(backup_name, overwrite=True)

# Cleanup old backups (keep 5 most recent)
store.cleanup_old_backups(keep_count=5)
```

### Synchronization

```python
# Sync from template manager to store
synced_count = store.sync_from_template_manager(manager)

# Sync from store to template manager
loaded_count = store.sync_to_template_manager(manager, overwrite=False)
```

## 🔍 Best Practices

### Template Design

1. **Use descriptive names and IDs**
```python
# Good
id="python_code_review_template"
name="Python Code Review Assistant"

# Bad
id="template1"
name="Template"
```

2. **Include comprehensive metadata**
```python
template = PromptTemplate(
    id="data_analysis_assistant",
    name="Data Analysis Assistant",
    description="Helps with data analysis tasks including statistics, visualization, and interpretation",
    template="...",
    variables=["dataset_type", "analysis_goal", "tools"],
    category="data_science",
    tags=["analysis", "statistics", "visualization", "python", "pandas"]
)
```

3. **Design for reusability**
```python
# Flexible template with multiple variables
template = """
You are a {role} specializing in {domain}.
Task: {task_description}
Context: {context}
Requirements: {requirements}
Output format: {output_format}
"""
```

### Variable Naming

1. **Use clear, descriptive names**
```python
# Good
variables = ["user_name", "task_type", "difficulty_level", "output_format"]

# Bad
variables = ["name", "type", "level", "format"]
```

2. **Group related variables**
```python
# Good structure
variables = [
    "user_name", "user_role", "user_experience",
    "task_type", "task_priority", "task_deadline",
    "project_name", "project_phase"
]
```

### Thinking Mode Selection

Choose appropriate thinking modes for different tasks:

- **STEP_BY_STEP**: Problem-solving, tutorials, debugging
- **ANALYTICAL**: Research, analysis, complex reasoning
- **PROS_CONS**: Decision-making, comparisons, evaluations
- **CREATIVE**: Brainstorming, design, innovation
- **CUSTOM**: Specialized reasoning patterns

### Performance Tips

1. **Cache frequently used templates**
2. **Use template collections for related templates**
3. **Minimize variable complexity in templates**
4. **Regular cleanup of unused templates**

### Security Considerations

1. **Validate template variables**
2. **Sanitize user input in templates**
3. **Review custom template functions**
4. **Backup templates regularly**

## 📊 Examples

### Complete Example: Code Review Assistant

```python
from chatbot_library.prompts import (
    TemplateManager, TemplateEngine, PromptBuilder,
    PromptTemplate, PromptConfiguration, ThinkingMode
)

# 1. Create template
code_review_template = PromptTemplate(
    id="code_review_assistant",
    name="Code Review Assistant",
    description="Comprehensive code review with best practices",
    template="""You are an expert {language} code reviewer.

Review the following code for:
- Code quality and readability
- Performance optimizations
- Security vulnerabilities
- Best practices adherence
- {additional_criteria}

Code to review:
```{language}
{code}
```

Provide structured feedback with specific suggestions.""",
    variables=["language", "code", "additional_criteria"],
    category="coding",
    tags=["code_review", "quality", "best_practices"]
)

# 2. Set up components
manager = TemplateManager()
engine = TemplateEngine()
builder = PromptBuilder(manager, engine)

# 3. Add template
manager.add_template(code_review_template)

# 4. Create configuration
config = PromptConfiguration(
    system_template_id="code_review_assistant",
    thinking_mode=ThinkingMode.ANALYTICAL,
    variables={
        "language": "Python",
        "code": "def calculate_sum(numbers):\n    return sum(numbers)",
        "additional_criteria": "Error handling and input validation"
    }
)

# 5. Build prompt
built_prompt = builder.build_prompt(
    user_message="Please review this function for production use.",
    config=config
)

# 6. Use the built prompt
print("System Message:")
print(built_prompt.system_message)
print("\nThinking Instructions:")
print(built_prompt.thinking_instructions)
print("\nUser Message:")
print(built_prompt.user_message)
```

This comprehensive prompt management system provides powerful tools for creating dynamic, context-aware prompts that enhance AI model performance and reasoning capabilities.