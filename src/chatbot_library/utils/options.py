"""
Comprehensive functions for displaying available configuration options.

This module provides user-friendly functions to explore all available models,
tools, configuration options, and capabilities across the chatbot library.
"""

from typing import Dict, List, Any, Set, Optional, Tuple
from dataclasses import fields
import inspect

from ..adapters.anthropic_api_adapter import AnthropicAdapter
from ..adapters.openai_api_adapter import OpenAIAdapter
from ..adapters.demo_adapter import DemoAdapter
from ..models.conversation_dataclasses import ChatbotParameters
from ..tools.mcp_tool_registry import MCPToolRegistry
from ..tools.builtin_tools import BUILTIN_TOOLS
from ..config.configuration import ConfigurationManager


def get_all_models() -> Dict[str, List[str]]:
    """
    Get all available models organized by provider.
    
    Returns:
        Dictionary mapping provider names to lists of supported models.
        
    Example:
        >>> models = get_all_models()
        >>> print(models)
        {
            'anthropic': ['claude-3-opus-20240229', 'claude-3-sonnet-20240229'],
            'openai': ['gpt-4-turbo', 'gpt-3.5-turbo-0125'],
            'demo': ['demo-model']
        }
    """
    return {
        'anthropic': AnthropicAdapter.supported_models(),
        'openai': OpenAIAdapter.supported_models(),
        'demo': DemoAdapter.supported_models(),
    }


def get_models_by_capability() -> Dict[str, Dict[str, List[str]]]:
    """
    Get models organized by their capabilities.
    
    Returns:
        Dictionary mapping capability names to provider->models mapping.
        
    Example:
        >>> capabilities = get_models_by_capability()
        >>> print(capabilities['tools'])
        {
            'anthropic': ['claude-3-opus-20240229', 'claude-3-sonnet-20240229'],
            'openai': ['gpt-4-turbo', 'gpt-3.5-turbo-0125']
        }
    """
    return {
        'tools': {
            'anthropic': AnthropicAdapter.models_supporting_tools(),
            'openai': OpenAIAdapter.models_supporting_tools(),
            'demo': DemoAdapter.models_supporting_tools(),
        },
        'images': {
            'anthropic': AnthropicAdapter.models_supporting_image_understanding(),
            'openai': OpenAIAdapter.models_supporting_image_understanding(),
            'demo': DemoAdapter.models_supporting_image_understanding(),
        }
    }


def get_available_tools() -> Dict[str, Any]:
    """
    Get comprehensive information about available tools.
    
    Returns:
        Dictionary with tool information including builtin and registered tools.
        
    Example:
        >>> tools = get_available_tools()
        >>> print(tools['builtin'])
        ['time_tool', 'calculator_tool', 'weather_tool', 'text_analysis']
    """
    registry = MCPToolRegistry()
    
    return {
        'builtin': [tool.__name__ for tool in BUILTIN_TOOLS],
        'builtin_details': [
            {
                'name': tool.__name__,
                'description': getattr(tool, '__doc__', 'No description'),
                'parameters': _get_tool_parameters(tool)
            }
            for tool in BUILTIN_TOOLS
        ],
        'registered': list(registry.tools.keys()),
        'registered_details': [
            {
                'name': name,
                'description': tool.description,
                'parameters': tool.input_schema.get('properties', {}) if hasattr(tool, 'input_schema') else {}
            }
            for name, tool in registry.tools.items()
        ]
    }


def get_configuration_options() -> Dict[str, Any]:
    """
    Get all available configuration options and their details.
    
    Returns:
        Dictionary with configuration parameter details.
        
    Example:
        >>> config = get_configuration_options()
        >>> print(config['ChatbotParameters'])
        {
            'model_name': {'type': 'str', 'required': True},
            'temperature': {'type': 'float', 'default': 0.7}
        }
    """
    config_options = {}
    
    # ChatbotParameters configuration
    chatbot_fields = {}
    for field in fields(ChatbotParameters):
        field_info = {
            'type': field.type.__name__ if hasattr(field.type, '__name__') else str(field.type),
            'required': field.default == field.default_factory if field.default_factory != field.default_factory else field.default is None
        }
        if field.default != field.default_factory:
            field_info['default'] = field.default
        chatbot_fields[field.name] = field_info
    
    config_options['ChatbotParameters'] = chatbot_fields
    
    # Configuration Manager options
    try:
        config_manager = ConfigurationManager()
        config_options['ConfigurationManager'] = {
            'Available Methods': [
                method for method in dir(config_manager) 
                if not method.startswith('_') and callable(getattr(config_manager, method))
            ],
            'Configuration Files': ['config.yaml', '.env', 'logging_config.yaml']
        }
    except Exception as e:
        config_options['ConfigurationManager'] = {'error': str(e)}
    
    return config_options


def get_adapter_capabilities() -> Dict[str, Dict[str, Any]]:
    """
    Get detailed capabilities for each adapter.
    
    Returns:
        Dictionary mapping adapter names to their capabilities.
        
    Example:
        >>> capabilities = get_adapter_capabilities()
        >>> print(capabilities['anthropic']['supports_streaming'])
        False
    """
    adapters = {
        'anthropic': AnthropicAdapter,
        'openai': OpenAIAdapter,
        'demo': DemoAdapter
    }
    
    capabilities = {}
    for name, adapter_class in adapters.items():
        capabilities[name] = {
            'supported_models': adapter_class.supported_models(),
            'models_supporting_tools': adapter_class.models_supporting_tools(),
            'models_supporting_images': adapter_class.models_supporting_image_understanding(),
            'total_models': len(adapter_class.supported_models()),
            'tool_capable_models': len(adapter_class.models_supporting_tools()),
            'vision_capable_models': len(adapter_class.models_supporting_image_understanding()),
            'class_methods': [
                method for method in dir(adapter_class) 
                if not method.startswith('_') and callable(getattr(adapter_class, method))
            ]
        }
    
    return capabilities


def get_conversation_options() -> Dict[str, Any]:
    """
    Get available conversation management options.
    
    Returns:
        Dictionary with conversation-related configuration options.
    """
    return {
        'branching_strategies': [
            'response_level'  # Modern simplified system
        ],
        'storage_formats': [
            'json',
            'sqlite' # For semantic search
        ],
        'embedding_options': [
            'message_pair_embeddings',
            'conversation_embeddings',
            'semantic_search_ready'
        ],
        'conversation_manager_versions': [
            'ConversationManager'  # Current modern version
        ]
    }


def print_all_options() -> None:
    """
    Print a comprehensive overview of all available options.
    
    This function provides a user-friendly way to explore all configuration
    options, models, tools, and capabilities in the chatbot library.
    """
    print("🤖 Chatbot Library - Available Options")
    print("=" * 50)
    
    # Models
    print("\\n📋 Available Models by Provider:")
    models = get_all_models()
    for provider, model_list in models.items():
        print(f"  {provider.upper()}:")
        for model in model_list:
            print(f"    • {model}")
    
    # Capabilities
    print("\\n🔧 Models by Capability:")
    capabilities = get_models_by_capability()
    for capability, providers in capabilities.items():
        print(f"  {capability.upper()} Support:")
        for provider, model_list in providers.items():
            if model_list:
                print(f"    {provider}: {len(model_list)} models")
                for model in model_list[:3]:  # Show first 3
                    print(f"      • {model}")
                if len(model_list) > 3:
                    print(f"      ... and {len(model_list) - 3} more")
    
    # Tools
    print("\\n🛠️ Available Tools:")
    tools = get_available_tools()
    print(f"  Built-in Tools ({len(tools['builtin'])}):")
    for tool_info in tools['builtin_details']:
        print(f"    • {tool_info['name']}: {tool_info['description'][:50]}...")
    
    if tools['registered']:
        print(f"  Registered Tools ({len(tools['registered'])}):")
        for tool_info in tools['registered_details']:
            print(f"    • {tool_info['name']}: {tool_info['description'][:50]}...")
    
    # Configuration
    print("\\n⚙️ Configuration Options:")
    config = get_configuration_options()
    for section, options in config.items():
        print(f"  {section}:")
        if isinstance(options, dict) and 'error' not in options:
            for key, value in list(options.items())[:5]:  # Show first 5
                if isinstance(value, dict):
                    print(f"    • {key}: {value.get('type', 'unknown')}")
                else:
                    print(f"    • {key}: {value}")
    
    # Adapters
    print("\\n🔌 Adapter Capabilities:")
    adapter_caps = get_adapter_capabilities()
    for adapter, caps in adapter_caps.items():
        print(f"  {adapter.upper()}:")
        print(f"    • Total models: {caps['total_models']}")
        print(f"    • Tool support: {caps['tool_capable_models']}")
        print(f"    • Vision support: {caps['vision_capable_models']}")
    
    print("\\n💡 Usage Examples:")
    print("  # Get specific information")
    print("  from chatbot_library.utils.options import get_all_models")
    print("  models = get_all_models()")
    print("  ")
    print("  # Check tool capabilities")
    print("  from chatbot_library.utils.options import get_models_by_capability")
    print("  tool_models = get_models_by_capability()['tools']")
    print("  ")
    print("  # Explore available tools")
    print("  from chatbot_library.utils.options import get_available_tools")
    print("  tools = get_available_tools()")


def get_example_configurations() -> Dict[str, Dict[str, Any]]:
    """
    Get example configurations for common use cases.
    
    Returns:
        Dictionary with example configurations for different scenarios.
    """
    return {
        'basic_text_chat': {
            'description': 'Simple text-based conversation',
            'model': 'claude-3-haiku-20240307',
            'provider': 'anthropic',
            'parameters': {
                'temperature': 0.7,
                'max_tokens': 1000,
                'system_message': 'You are a helpful assistant.'
            },
            'tools': False,
            'images': False
        },
        'advanced_tool_use': {
            'description': 'Conversation with tool capabilities',
            'model': 'claude-3-opus-20240229',
            'provider': 'anthropic',
            'parameters': {
                'temperature': 0.3,
                'max_tokens': 2000,
                'system_message': 'You are an advanced AI assistant with access to tools.'
            },
            'tools': ['time_tool', 'calculator_tool', 'weather_tool'],
            'images': False
        },
        'multimodal_analysis': {
            'description': 'Image understanding and analysis',
            'model': 'gpt-4-turbo',
            'provider': 'openai',
            'parameters': {
                'temperature': 0.5,
                'max_tokens': 1500,
                'system_message': 'You are an AI assistant capable of analyzing images and text.'
            },
            'tools': ['text_analysis'],
            'images': True
        },
        'development_assistant': {
            'description': 'Code-focused assistant with tools',
            'model': 'claude-3-sonnet-20240229',
            'provider': 'anthropic',
            'parameters': {
                'temperature': 0.2,
                'max_tokens': 3000,
                'system_message': 'You are a programming assistant focused on helping with code.'
            },
            'tools': ['text_analysis', 'calculator_tool'],
            'images': False
        }
    }


def _get_tool_parameters(tool_func) -> Dict[str, Any]:
    """Helper function to extract parameters from a tool function."""
    try:
        sig = inspect.signature(tool_func)
        params = {}
        for name, param in sig.parameters.items():
            param_info = {
                'type': param.annotation.__name__ if hasattr(param.annotation, '__name__') else str(param.annotation),
                'required': param.default == param.empty
            }
            if param.default != param.empty:
                param_info['default'] = param.default
            params[name] = param_info
        return params
    except Exception:
        return {}


# Quick access functions for common queries
def list_models(provider: Optional[str] = None) -> List[str]:
    """Quick function to list models, optionally filtered by provider."""
    if provider:
        all_models = get_all_models()
        return all_models.get(provider.lower(), [])
    else:
        all_models = get_all_models()
        return [model for models in all_models.values() for model in models]


def list_tools() -> List[str]:
    """Quick function to list all available tools."""
    tools = get_available_tools()
    return tools['builtin'] + tools['registered']


def find_models_with_capability(capability: str) -> Dict[str, List[str]]:
    """Find models that support a specific capability."""
    capabilities = get_models_by_capability()
    return capabilities.get(capability.lower(), {})


if __name__ == "__main__":
    # If run directly, print all options
    print_all_options()