"""
Simplified Chainlit UI that avoids payload issues and fixes API problems.
"""

import chainlit as cl
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
import asyncio
import uuid

# Add source to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from chatbot_library.core.conversation_manager_v2_hotswap import ConversationManagerV2HotSwap
from chatbot_library.adapters.chatbot_adapter import ChatbotCapabilities
from chatbot_library.models.conversation_v2 import Attachment

# Global manager instance
conversation_manager: Optional[ConversationManagerV2HotSwap] = None
current_conversation_id: Optional[str] = None
available_models = {}

def init_conversation_manager():
    """Initialize the conversation manager with models."""
    global conversation_manager, available_models
    
    # Use data directory
    data_dir = Path("data/chainlit_simple")
    conversation_manager = ConversationManagerV2HotSwap(data_dir)
    
    # Register available models based on API keys
    if os.getenv("ANTHROPIC_API_KEY"):
        conversation_manager.register_model(
            "claude-3-5-sonnet",
            ChatbotCapabilities(
                function_calling=True,
                image_understanding=True,
                supported_images=["image/png", "image/jpeg", "image/gif", "image/webp"]
            ),
            {"provider": "anthropic", "context_limit": 200000, "cost": "medium"}
        )
        
        conversation_manager.register_model(
            "claude-3-haiku",
            ChatbotCapabilities(
                function_calling=False,
                image_understanding=True,
                supported_images=["image/png", "image/jpeg", "image/gif", "image/webp"]
            ),
            {"provider": "anthropic", "context_limit": 200000, "cost": "low"}
        )
    
    if os.getenv("OPENAI_API_KEY"):
        conversation_manager.register_model(
            "gpt-4o",
            ChatbotCapabilities(
                function_calling=True,
                image_understanding=True,
                supported_images=["image/png", "image/jpeg", "image/gif", "image/webp"]
            ),
            {"provider": "openai", "context_limit": 128000, "cost": "high"}
        )
    
    # Add demo models
    conversation_manager.register_model(
        "demo-creative",
        ChatbotCapabilities(
            function_calling=False,
            image_understanding=False,
            supported_images=[]
        ),
        {"provider": "demo", "context_limit": 4000, "cost": "free"}
    )
    
    available_models = {
        model["name"]: model for model in conversation_manager.get_available_models()
    }

async def call_model_api(messages: List[Dict], model_name: str, temperature: float = 0.7, max_tokens: int = 1000) -> Optional[Dict]:
    """Call the appropriate model API."""
    try:
        if model_name.startswith("claude-"):
            return await call_anthropic_api(messages, model_name, temperature, max_tokens)
        elif model_name.startswith("gpt-"):
            return await call_openai_api(messages, model_name, temperature, max_tokens)
        else:
            # Demo model
            demo_response = f"🎨 Demo response from {model_name}: {messages[-1]['content'][:100]}..."
            return {
                "content": demo_response,
                "model": model_name,
                "usage": {"input_tokens": 50, "output_tokens": 30}
            }
    except Exception as e:
        await cl.Message(content=f"❌ Error calling {model_name}: {str(e)}").send()
        return None

async def call_anthropic_api(messages: List[Dict], model: str, temperature: float, max_tokens: int) -> Optional[Dict]:
    """Call Anthropic API with fixed initialization."""
    try:
        # Clear any potential proxy settings that might interfere
        import anthropic
        
        # Create client with minimal configuration
        client = anthropic.Anthropic()
        
        # Convert messages to Anthropic format
        system_msg = None
        anthropic_messages = []
        
        for msg in messages:
            if msg["role"] == "system":
                system_msg = msg["content"]
            elif msg["role"] in ["user", "assistant"]:
                anthropic_messages.append({"role": msg["role"], "content": msg["content"]})
        
        response = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system_msg or "You are a helpful assistant.",
            messages=anthropic_messages
        )
        
        return {
            "content": response.content[0].text,
            "model": model,
            "usage": {
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens
            }
        }
    except Exception as e:
        print(f"Anthropic API error: {e}")
        return None

async def call_openai_api(messages: List[Dict], model: str, temperature: float, max_tokens: int) -> Optional[Dict]:
    """Call OpenAI API."""
    try:
        import openai
        client = openai.OpenAI()
        
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        return {
            "content": response.choices[0].message.content,
            "model": model,
            "usage": {
                "input_tokens": response.usage.prompt_tokens,
                "output_tokens": response.usage.completion_tokens
            }
        }
    except Exception as e:
        print(f"OpenAI API error: {e}")
        return None

@cl.on_chat_start
async def on_chat_start():
    """Initialize the chat session."""
    global conversation_manager, current_conversation_id
    
    # Initialize manager if not done
    if conversation_manager is None:
        init_conversation_manager()
    
    # Set default model
    default_model = list(available_models.keys())[0] if available_models else "demo-creative"
    cl.user_session.set("selected_model", default_model)
    cl.user_session.set("temperature", 0.7)
    cl.user_session.set("max_tokens", 1000)
    
    # Create initial conversation
    conversation = conversation_manager.create_conversation("Chat Session")
    current_conversation_id = conversation.id
    
    # Simple welcome message
    welcome_msg = f"""# 🤖 Chatbot Library - Simple UI

**Current Model:** {default_model}
**Available Models:** {len(available_models)}

**Commands:**
- `/model <name>` - Switch AI model
- `/models` - List available models
- `/help` - Show this help

Ready to chat! 🚀"""
    
    await cl.Message(content=welcome_msg).send()

@cl.on_message
async def on_message(message: cl.Message):
    """Handle incoming messages."""
    global current_conversation_id
    
    # Handle commands
    if message.content.startswith('/'):
        await handle_command(message.content)
        return
    
    # Get current settings
    selected_model = cl.user_session.get("selected_model", "demo-creative")
    temperature = cl.user_session.get("temperature", 0.7)
    max_tokens = cl.user_session.get("max_tokens", 1000)
    
    # Ensure we have a conversation
    if not current_conversation_id:
        conversation = conversation_manager.create_conversation("New Chat")
        current_conversation_id = conversation.id
    
    # Add message to conversation
    user_message = conversation_manager.add_message(
        conversation_id=current_conversation_id,
        user_id="ui_user",
        text=message.content,
        attachments=[]
    )
    
    # Show processing indicator
    async with cl.Step(name=f"🤖 {selected_model}", type="llm") as step:
        step.input = message.content
        
        try:
            # Get adapted context
            adapted_context = conversation_manager.get_conversation_context_for_model(
                current_conversation_id,
                selected_model,
                context_limit=20
            )
            
            # Add system message
            api_messages = [
                {"role": "system", "content": "You are a helpful AI assistant."}
            ] + adapted_context
            
            # Call model API
            response_data = await call_model_api(api_messages, selected_model, temperature, max_tokens)
            
            if response_data:
                # Add response to conversation
                ai_response = conversation_manager.add_response(
                    conversation_id=current_conversation_id,
                    message_id=user_message.id,
                    model=selected_model,
                    text=response_data["content"],
                    branch_name=selected_model,
                    metadata={
                        "temperature": temperature,
                        "max_tokens": max_tokens,
                        "usage": response_data.get("usage", {})
                    }
                )
                
                step.output = response_data["content"]
                
                # Show response with usage
                usage = response_data.get("usage", {})
                usage_info = ""
                if usage:
                    usage_info = f"\n\n*📊 {usage.get('input_tokens', 0)} → {usage.get('output_tokens', 0)} tokens*"
                
                # Create simple actions
                actions = [
                    cl.Action(name="regenerate", value=f"regen_{user_message.id}", label="🔄 Regenerate"),
                    cl.Action(name="models", value="show_models", label="🤖 Switch Model"),
                ]
                
                await cl.Message(
                    content=response_data["content"] + usage_info,
                    actions=actions
                ).send()
                
            else:
                step.output = "Failed to get response"
                await cl.Message(content="❌ Failed to get response from the model.").send()
                
        except Exception as e:
            step.output = f"Error: {str(e)}"
            await cl.Message(content=f"❌ Error: {str(e)}").send()

async def handle_command(command: str):
    """Handle user commands."""
    cmd_parts = command.split()
    cmd = cmd_parts[0].lower()
    
    if cmd == "/model":
        if len(cmd_parts) > 1:
            model_name = cmd_parts[1]
            if model_name in available_models:
                cl.user_session.set("selected_model", model_name)
                await cl.Message(content=f"✅ Switched to model: **{model_name}**").send()
            else:
                await cl.Message(content=f"❌ Model '{model_name}' not available. Use `/models` to see available models.").send()
        else:
            current_model = cl.user_session.get("selected_model", "unknown")
            await cl.Message(content=f"🤖 Current model: **{current_model}**").send()
    
    elif cmd == "/models":
        if available_models:
            models_list = "🤖 **Available Models:**\n\n"
            for model_name, model_info in available_models.items():
                caps = model_info["capabilities"]
                cost = model_info.get("cost", "unknown")
                
                features = []
                if caps.image_understanding:
                    features.append("📸")
                if caps.function_calling:
                    features.append("🔧")
                
                feature_str = " " + " ".join(features) if features else ""
                models_list += f"• **{model_name}** ({cost}){feature_str}\n"
            
            models_list += f"\nUse `/model <name>` to switch models."
            await cl.Message(content=models_list).send()
        else:
            await cl.Message(content="❌ No models available. Check your API keys.").send()
    
    elif cmd == "/help":
        help_msg = """🤖 **Available Commands:**

• `/model <name>` - Switch to a specific model
• `/model` - Show current model
• `/models` - List all available models
• `/help` - Show this help message

**Available Models:** Simply type the model name after `/model`
Examples:
- `/model claude-3-5-sonnet`
- `/model gpt-4o`
- `/model demo-creative`"""
        
        await cl.Message(content=help_msg).send()
    
    else:
        await cl.Message(content=f"❌ Unknown command: {cmd}. Use `/help` for available commands.").send()

@cl.action_callback("regenerate")
async def on_regenerate(action):
    """Regenerate the last response."""
    message_id = action.value.split('_')[1]
    selected_model = cl.user_session.get("selected_model")
    
    await cl.Message(content=f"🔄 Regenerating response with **{selected_model}**...").send()

@cl.action_callback("models")
async def on_show_models(action):
    """Show available models."""
    await handle_command("/models")

if __name__ == "__main__":
    print("🌐 Starting Simple Chainlit UI...")
    print("🎯 Features: Model switching, conversation management, API calls")
    print("📝 Commands: /model, /models, /help")
    print("🚀 Open your browser to localhost:8000")
    
    os.environ.setdefault("CHAINLIT_HOST", "localhost")
    os.environ.setdefault("CHAINLIT_PORT", "8000")