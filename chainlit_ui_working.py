"""
Working Chainlit UI with proper interactive elements.
Uses correct Chainlit syntax for chat settings and input widgets.
"""

import chainlit as cl
from chainlit.input_widget import Select, Slider, Switch
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
    data_dir = Path("data/chainlit_working")
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
        
        conversation_manager.register_model(
            "gpt-4-turbo",
            ChatbotCapabilities(
                function_calling=True,
                image_understanding=False,
                supported_images=[]
            ),
            {"provider": "openai", "context_limit": 128000, "cost": "medium"}
        )
    
    # Add demo models for testing
    conversation_manager.register_model(
        "demo-creative",
        ChatbotCapabilities(
            function_calling=False,
            image_understanding=False,
            supported_images=[]
        ),
        {"provider": "demo", "context_limit": 4000, "cost": "free"}
    )
    
    conversation_manager.register_model(
        "demo-analytical",
        ChatbotCapabilities(
            function_calling=True,
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
            if "creative" in model_name:
                demo_response = f"🎨 *Creative Response* (temp={temperature}): Here's an imaginative take on your question: '{messages[-1]['content'][:50]}...' [This would be a more creative, artistic response from the creative demo model]"
            else:
                demo_response = f"📊 *Analytical Response* (temp={temperature}): Based on systematic analysis of your query '{messages[-1]['content'][:50]}...', here are the key points... [This would be a more structured, analytical response from the analytical demo model]"
            
            return {
                "content": demo_response,
                "model": model_name,
                "usage": {"input_tokens": 50, "output_tokens": max_tokens // 20}
            }
    except Exception as e:
        await cl.Message(content=f"❌ Error calling {model_name}: {str(e)}").send()
        return None

async def call_anthropic_api(messages: List[Dict], model: str, temperature: float, max_tokens: int) -> Optional[Dict]:
    """Call Anthropic API."""
    try:
        import anthropic
        
        # Initialize client with explicit parameters to avoid any proxy issues
        client = anthropic.Anthropic(
            api_key=os.getenv("ANTHROPIC_API_KEY")
        )
        
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
        
        # Initialize client with explicit API key
        client = openai.OpenAI(
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
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
    """Initialize the chat session with interactive settings."""
    global conversation_manager, current_conversation_id
    
    # Initialize manager if not done
    if conversation_manager is None:
        init_conversation_manager()
    
    # Welcome message
    await cl.Message(
        content="""# 🤖 Enhanced Chatbot Library - Interactive UI

Welcome! This interface provides interactive controls for:
- **🎛️ Model Selection**: Choose AI models with different capabilities
- **⚙️ Parameter Control**: Adjust temperature and response length  
- **💬 Conversation Management**: Create and manage conversations
- **🔄 Hot-swapping**: Switch models mid-conversation

Use the **Settings** panel (⚙️ icon) to configure your preferences."""
    ).send()
    
    # Get conversation list for dropdown
    conversations = conversation_manager.get_conversation_list()
    conv_options = ["🆕 New Conversation"]
    
    for conv in conversations[-10:]:  # Show last 10
        title = conv['title'][:30] + "..." if len(conv['title']) > 30 else conv['title']
        conv_options.append(f"💬 {title} ({conv['message_count']} msgs)")
    
    # Create model options with capability info
    model_options = []
    for model_name, model_info in available_models.items():
        caps = model_info["capabilities"]
        cost = model_info.get("cost", "unknown")
        
        features = []
        if caps.image_understanding:
            features.append("📸")
        if caps.function_calling:
            features.append("🔧")
        
        feature_str = " " + " ".join(features) if features else ""
        model_options.append(f"{model_name} ({cost}){feature_str}")
    
    # Set up chat settings with all controls
    settings = await cl.ChatSettings(
        [
            Select(
                id="model",
                label="🤖 AI Model",
                values=model_options,
                initial_index=0,
            ),
            Select(
                id="conversation",
                label="💬 Conversation",
                values=conv_options,
                initial_index=0,
            ),
            Slider(
                id="temperature",
                label="🌡️ Temperature",
                initial=0.7,
                min=0.0,
                max=2.0,
                step=0.1,
            ),
            Slider(
                id="max_tokens",
                label="📝 Max Tokens",
                initial=1000,
                min=100,
                max=2000,
                step=100,
            ),
            Switch(
                id="show_usage",
                label="📊 Show Token Usage",
                initial=True,
            ),
            Switch(
                id="auto_suggest",
                label="💡 Auto-suggest Models",
                initial=True,
            ),
        ]
    ).send()
    
    # Store initial settings
    model_name = list(available_models.keys())[0]  # Default to first model
    cl.user_session.set("selected_model", model_name)
    cl.user_session.set("temperature", 0.7)
    cl.user_session.set("max_tokens", 1000)
    cl.user_session.set("show_usage", True)
    cl.user_session.set("auto_suggest", True)
    cl.user_session.set("conversation_index", 0)
    
    # Create initial conversation
    conversation = conversation_manager.create_conversation("New Chat Session")
    current_conversation_id = conversation.id
    
    # Show model info
    await show_current_model_info(model_name)

@cl.on_settings_update
async def on_settings_update(settings):
    """Handle settings updates from the UI."""
    global current_conversation_id
    
    # Extract model name from the formatted string
    model_selection = settings["model"]
    model_name = model_selection.split(" (")[0]  # Extract name before " ("
    
    # Extract conversation selection
    conv_selection = settings["conversation"]
    
    # Update session settings
    cl.user_session.set("selected_model", model_name)
    cl.user_session.set("temperature", settings["temperature"])
    cl.user_session.set("max_tokens", settings["max_tokens"])
    cl.user_session.set("show_usage", settings["show_usage"])
    cl.user_session.set("auto_suggest", settings["auto_suggest"])
    
    # Handle conversation change
    if conv_selection.startswith("🆕"):
        # Create new conversation
        conversation = conversation_manager.create_conversation(f"Chat {uuid.uuid4().hex[:8]}")
        current_conversation_id = conversation.id
        await cl.Message(content=f"✅ Created new conversation: {conversation.title}").send()
    elif conv_selection.startswith("💬"):
        # Load existing conversation (this would need more implementation)
        await cl.Message(content=f"📂 Conversation switching: {conv_selection}").send()
    
    # Show model change confirmation
    await cl.Message(content=f"✅ Settings updated! Using **{model_name}** with temperature {settings['temperature']}").send()
    
    # Show model info for new selection
    await show_current_model_info(model_name)

async def show_current_model_info(model_name: str):
    """Display information about the currently selected model."""
    if model_name in available_models:
        model_info = available_models[model_name]
        caps = model_info["capabilities"]
        
        # Create capability badges
        capability_badges = []
        if caps.image_understanding:
            capability_badges.append("📸 **Images**")
        if caps.function_calling:
            capability_badges.append("🔧 **Tools**")
        if not capability_badges:
            capability_badges.append("💬 **Text Only**")
        
        info_msg = f"""🤖 **Current Model: {model_name}**

**Provider:** {model_info.get('provider', 'unknown').title()}
**Cost:** {model_info.get('cost', 'unknown').title()}
**Capabilities:** {' • '.join(capability_badges)}
**Context:** {model_info.get('context_limit', 0):,} tokens

Ready to chat! 🚀"""
        
        await cl.Message(content=info_msg).send()

@cl.on_message
async def on_message(message: cl.Message):
    """Handle incoming messages."""
    global current_conversation_id
    
    # Get current settings
    selected_model = cl.user_session.get("selected_model")
    temperature = cl.user_session.get("temperature", 0.7)
    max_tokens = cl.user_session.get("max_tokens", 1000)
    show_usage = cl.user_session.get("show_usage", True)
    auto_suggest = cl.user_session.get("auto_suggest", True)
    
    # Ensure we have a conversation
    if not current_conversation_id:
        conversation = conversation_manager.create_conversation("New Chat")
        current_conversation_id = conversation.id
    
    # Handle images
    attachments = []
    if message.elements:
        for element in message.elements:
            if isinstance(element, cl.Image):
                import base64
                image_data = base64.b64encode(element.content).decode('utf-8')
                
                attachment = Attachment(
                    id=element.name,
                    content_type=element.mime,
                    media_type=element.mime,
                    data=image_data,
                    source_type="base64"
                )
                attachments.append(attachment)
    
    # Add message to conversation
    user_message = conversation_manager.add_message(
        conversation_id=current_conversation_id,
        user_id="ui_user",
        text=message.content,
        attachments=attachments
    )
    
    # Show processing indicator
    model_info = available_models.get(selected_model, {})
    cost = model_info.get("cost", "unknown")
    
    async with cl.Step(name=f"🤖 {selected_model} ({cost})", type="llm") as step:
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
                
                # Prepare response message
                response_content = response_data["content"]
                
                # Add usage info if enabled
                if show_usage:
                    usage = response_data.get("usage", {})
                    if usage:
                        response_content += f"\n\n*📊 {usage.get('input_tokens', 0)} → {usage.get('output_tokens', 0)} tokens*"
                
                # Create response actions
                actions = [
                    cl.Action(name="regenerate", value=f"regen_{user_message.id}", label="🔄 Regenerate"),
                    cl.Action(name="try_alternative", value=f"alt_{user_message.id}", label="🎭 Alternative Model"),
                ]
                
                # Check if we have multiple responses (branches)
                if len(user_message.responses) > 1:
                    actions.append(cl.Action(name="show_branches", value=f"branches_{user_message.id}", label="🌿 View Branches"))
                
                await cl.Message(content=response_content, actions=actions).send()
                
                # Auto-suggest alternative models if enabled
                if auto_suggest and len(conversation_manager.get_conversation(current_conversation_id).messages) > 1:
                    await suggest_alternative_models()
                
            else:
                step.output = "Failed to get response"
                await cl.Message(content="❌ Failed to get response from the model.").send()
                
        except Exception as e:
            step.output = f"Error: {str(e)}"
            await cl.Message(content=f"❌ Error: {str(e)}").send()

@cl.action_callback("regenerate")
async def on_regenerate(action):
    """Regenerate the last response with current settings."""
    message_id = action.value.split('_')[1]
    selected_model = cl.user_session.get("selected_model")
    
    await cl.Message(content=f"🔄 Regenerating response with **{selected_model}**...").send()

@cl.action_callback("try_alternative")
async def on_try_alternative(action):
    """Suggest alternative models for the response."""
    message_id = action.value.split('_')[1]
    selected_model = cl.user_session.get("selected_model")
    
    # Get alternative models
    alternatives = [name for name in available_models.keys() if name != selected_model]
    
    if alternatives:
        alt_list = []
        for alt_name in alternatives[:3]:  # Show top 3
            model_info = available_models[alt_name]
            cost = model_info.get("cost", "unknown")
            alt_list.append(f"• **{alt_name}** ({cost})")
        
        await cl.Message(
            content=f"🎭 **Alternative Models:**\n\n{chr(10).join(alt_list)}\n\nUse the Settings panel to switch models.",
            actions=[cl.Action(name="open_settings", value="settings", label="⚙️ Open Settings")]
        ).send()
    else:
        await cl.Message(content="No alternative models available.").send()

@cl.action_callback("show_branches")
async def on_show_branches(action):
    """Show all response branches for a message."""
    message_id = action.value.split('_')[1]
    
    conversation = conversation_manager.get_conversation(current_conversation_id)
    if conversation:
        target_message = None
        for msg in conversation.messages:
            if msg.id == message_id:
                target_message = msg
                break
        
        if target_message and target_message.responses:
            branch_msg = "🌿 **Response Branches:**\n\n"
            
            for i, response in enumerate(target_message.responses, 1):
                branch_name = response.branch_name or "main"
                branch_msg += f"**{i}. {branch_name}** ({response.model})\n"
                branch_msg += f"{response.text[:100]}...\n\n"
            
            await cl.Message(content=branch_msg).send()

async def suggest_alternative_models():
    """Suggest better models based on conversation analysis."""
    try:
        recommendations = conversation_manager.get_model_recommendations(current_conversation_id)
        current_model = cl.user_session.get("selected_model")
        
        alternatives = [r for r in recommendations[:2] if r["name"] != current_model]
        
        if alternatives:
            suggest_msg = "💡 **Model Suggestions:**\n\n"
            
            for alt in alternatives:
                score = alt["compatibility_score"]
                model_info = available_models.get(alt["name"], {})
                cost = model_info.get("cost", "unknown")
                
                recommend_icon = "✅" if alt.get("recommended") else "💡"
                suggest_msg += f"{recommend_icon} **{alt['name']}** ({cost}) - Score: {score:.2f}\n"
            
            suggest_msg += "\nChange models in the Settings panel (⚙️)."
            
            await cl.Message(content=suggest_msg).send()
    
    except Exception as e:
        # Don't show errors for suggestions
        pass

if __name__ == "__main__":
    print("🌐 Starting Working Chainlit UI...")
    print("🎛️ Features: Chat Settings, Model Selection, Interactive Controls")
    print("⚙️ Use the Settings panel to configure your experience")
    print("🚀 Open your browser to localhost:8000")
    
    os.environ.setdefault("CHAINLIT_HOST", "localhost")
    os.environ.setdefault("CHAINLIT_PORT", "8000")