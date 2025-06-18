#!/usr/bin/env python3
"""
Basic usage example using the new simplified conversation structure.
"""

import os
import sys
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def main():
    """Demonstrate basic library usage with the simplified structure."""
    
    print("🤖 Chatbot Library - Basic Usage Example")
    print("=" * 55)
    
    from chatbot_library.core.conversation_manager import ConversationManager
    
    # Set up data directory
    data_dir = Path("data/basic_usage")
    data_dir.mkdir(parents=True, exist_ok=True)
    
    # Initialize the conversation manager
    conversation_manager = ConversationManager(data_dir=data_dir)
    print(f"✓ Created conversation manager")
    print(f"  Data directory: {data_dir}")
    
    # Create a conversation
    print("\\n💬 Creating a new conversation...")
    conversation = conversation_manager.create_conversation("Basic Usage Demo")
    print(f"✓ Created conversation: {conversation.title}")
    print(f"  ID: {conversation.id}")
    
    # Add first message
    print("\\n📝 Adding messages...")
    message1 = conversation_manager.add_message(
        conversation_id=conversation.id,
        user_id="demo_user",
        text="What are the main features of this chatbot library?"
    )
    print(f"✓ Added user message: {message1.text}")
    
    # Add response (simulated - in real usage this would come from chatbot adapter)
    response1 = conversation_manager.add_response(
        conversation_id=conversation.id,
        message_id=message1.id,
        model="claude-3-sonnet",
        text="This chatbot library provides several key features:\\n\\n1. **Multi-provider Support**: Works with Anthropic Claude, OpenAI GPT, and other LLM providers\\n2. **Conversation Management**: Linear message structure with response-level branching\\n3. **Tool Integration**: Function calling and custom tool support\\n4. **MCP Protocol**: Model Context Protocol server and client implementation\\n5. **Embedding Support**: Built-in vector storage for semantic search\\n6. **Clean API**: Simple, intuitive interface for conversation management"
    )
    print(f"✓ Added AI response: {response1.text[:100]}...")
    
    # Add alternative response (regeneration example)
    alt_response = conversation_manager.add_response(
        conversation_id=conversation.id,
        message_id=message1.id,
        model="gpt-4-turbo",
        text="The library offers these core capabilities:\\n\\n• **Universal LLM Interface**: Unified API for different AI providers\\n• **Smart Conversation Flow**: Linear messages with response alternatives\\n• **Advanced Tooling**: Custom function calling and tool management\\n• **Protocol Support**: Full MCP (Model Context Protocol) implementation\\n• **Vector Integration**: Ready for embedding-based features\\n• **Developer Friendly**: Clean, simple API design",
        branch_name="alternative"
    )
    print(f"✓ Added alternative response: {alt_response.text[:100]}...")
    
    # Add follow-up message
    message2 = conversation_manager.add_message(
        conversation_id=conversation.id,
        user_id="demo_user",
        text="How does the response branching work?"
    )
    
    response2 = conversation_manager.add_response(
        conversation_id=conversation.id,
        message_id=message2.id,
        model="claude-3-sonnet",
        text="Response branching is much simpler in this design:\\n\\n**How it works:**\\n- Each message can have multiple responses\\n- Responses are tagged with branch names (e.g., 'main', 'creative', 'concise')\\n- You can easily regenerate responses or try different models\\n- Context building supports any branch for API calls\\n\\n**Example:**\\n```python\\n# Main response\\nresponse1 = add_response(msg_id, text='Response A')\\n\\n# Alternative response\\nresponse2 = add_response(msg_id, text='Response B', branch_name='creative')\\n```\\n\\nThis eliminates the complexity of the old branching system while keeping all the functionality!"
    )
    print(f"✓ Added follow-up exchange")
    
    # Demonstrate conversation context building
    print("\\n📖 Conversation Context (Main Branch):")
    context = conversation.get_conversation_context()
    for i, turn in enumerate(context, 1):
        role_emoji = "👤" if turn['role'] == 'user' else "🤖"
        print(f"  {i}. {role_emoji} {turn['role']}: {turn['content'][:80]}...")
    
    print("\\n📖 Conversation Context (Alternative Branch):")
    alt_context = conversation.get_conversation_context(branch_name="alternative")
    for i, turn in enumerate(alt_context, 1):
        role_emoji = "👤" if turn['role'] == 'user' else "🤖"
        print(f"  {i}. {role_emoji} {turn['role']}: {turn['content'][:80]}...")
    
    # Show conversation statistics
    print("\\n📊 Conversation Statistics:")
    conversation = conversation_manager.get_conversation(conversation.id)
    branches = conversation.get_all_branches()
    
    print(f"  📄 Total messages: {len(conversation.messages)}")
    print(f"  🌿 Response branches: {branches}")
    print(f"  📅 Created: {conversation.created_at}")
    print(f"  🔄 Updated: {conversation.updated_at}")
    
    # Show all conversations
    print("\\n📋 All Conversations:")
    conv_list = conversation_manager.get_conversation_list()
    for conv_info in conv_list:
        print(f"  • {conv_info['title']}")
        print(f"    Messages: {conv_info['message_count']}, Branches: {conv_info['branch_count']}")
        print(f"    ID: {conv_info['id']}")
    
    print("\\n✅ Basic Usage Example Complete!")
    
    print("\\n🎯 Key Features Demonstrated:")
    print("  ✓ Simple conversation creation")
    print("  ✓ Linear message structure") 
    print("  ✓ Response-level branching")
    print("  ✓ Alternative response generation")
    print("  ✓ Context building for API calls")
    print("  ✓ Conversation persistence")
    print("  ✓ Statistics and analytics")
    
    print("\\n🚀 Next Steps:")
    print("  • Integrate with real chatbot adapters (Anthropic, OpenAI)")
    print("  • Add embedding support for semantic search")
    print("  • Connect to Chainlit for web UI")
    print("  • Set up MCP server for protocol integration")
    print("  • Add tool/function calling capabilities")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())