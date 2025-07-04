# Architecture Overview

CogniFlow is designed as a modular, extensible framework that separates concerns across multiple layers, enabling cognitive intelligence and workflow automation. This document provides a comprehensive overview of the system architecture, component relationships, and design principles.

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Application Layer                           │
├─────────────────────────────────────────────────────────────────────┤
│  Conversation Management  │  Prompt Management  │  Tool System   │
├─────────────────────────────────────────────────────────────────────┤
│              Model Adapters & Integration Layer                    │
├─────────────────────────────────────────────────────────────────────┤
│                     Core Data Models                              │
├─────────────────────────────────────────────────────────────────────┤
│                  Storage & Persistence                            │
└─────────────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Application Layer
- `PromptConversationManager`: Enhanced conversation management with prompt integration
- `MCPConversationManager`: MCP tool integration  
- Application-specific controllers and services

### 2. Conversation Management
- `ConversationManager`: Core conversation operations
- `ConversationAdapter`: Model compatibility layer
- Linear message chains with response branching
- Hot-swapping between models mid-conversation

### 3. Prompt Management
- `TemplateManager`: Template CRUD and organization
- `TemplateEngine`: Variable substitution and rendering
- `PromptBuilder`: Dynamic prompt construction
- `TemplateStore`: Persistent template storage

### 4. Tool System
- `MCPToolRegistry`: Tool registration and management
- `IterativeToolExecutor`: Chain-based tool execution
- MCP compatibility with iterative tool chains
- Human approval workflows for sensitive operations

### 5. Model Integration Layer
- `ChatbotAdapter`: Abstract base for model adapters
- `AnthropicAdapter`: Claude model integration
- `OpenAIAdapter`: ChatGPT model integration
- Unified API across different model providers

### 6. Core Data Models
- `Conversation`, `Message`, `Response`: Core data structures
- `ToolUse`, `ToolResult`: Tool execution records
- Rich metadata support and JSON serialization

## Data Flow

### Conversation Flow
```
User Input → Message Creation → Prompt Building → Model Adapter → AI Response → Response Storage
```

### Tool Execution Flow  
```
Tool Request → Registry Lookup → Execution → Result Processing → Chain Detection
```

### Prompt Construction Flow
```
Base Template → Variable Substitution → Function Calls → Thinking Mode → Final Prompt
```

## Design Principles

### 1. Separation of Concerns
Each component has a single, well-defined responsibility

### 2. Extensibility  
Plugin architecture for easy addition of new models and tools

### 3. Backward Compatibility
Legacy tool support with gradual migration paths

### 4. Performance
Lazy loading, caching, and async support where beneficial

### 5. Safety and Security
Input validation, loop detection, and approval workflows

---

This architecture provides a solid foundation for building sophisticated conversational AI applications with cognitive intelligence and workflow automation capabilities.