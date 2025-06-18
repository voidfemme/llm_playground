"""
Example MCP server using the chatbot library.
Run with: python examples/mcp_server_example.py
"""

import asyncio
import sys
from pathlib import Path

from src.chatbot_library import ChatbotManager, ToolManager
from src.chatbot_library.adapters import AnthropicAdapter, OpenAIAdapter
from src.chatbot_library.mcp import MCPServer


async def main():
    """Run MCP server example."""
    
    # Initialize chatbot library components
    chatbot_manager = ChatbotManager()
    tool_manager = ToolManager()
    
    # Register chatbot adapters
    try:
        anthropic_adapter = AnthropicAdapter()
        chatbot_manager.register_chatbot("anthropic", anthropic_adapter)
        print("✓ Registered Anthropic adapter")
    except Exception as e:
        print(f"⚠ Could not register Anthropic adapter: {e}")
    
    try:
        openai_adapter = OpenAIAdapter()
        chatbot_manager.register_chatbot("openai", openai_adapter)
        print("✓ Registered OpenAI adapter")
    except Exception as e:
        print(f"⚠ Could not register OpenAI adapter: {e}")
    
    # Load default tools
    tool_manager.load_default_tools()
    print("✓ Loaded default tools")
    
    # Create MCP server
    mcp_server = MCPServer(
        chatbot_manager=chatbot_manager,
        tool_manager=tool_manager,
        name="chatbot-library-mcp-server",
        version="1.0.0"
    )
    
    print("🚀 MCP Server started")
    print("Available capabilities:")
    print("  - Tools:", len(tool_manager.get_tools_list()))
    print("  - Chatbots:", len(chatbot_manager.get_chatbot_names()))
    print("  - Resources: Chatbot model information")
    print("  - Prompts: Chat and summarize prompts")
    print()
    print("Listening for MCP messages on stdin...")
    print("Send JSON-RPC messages to interact with the server.")
    print("Example initialize message:")
    print('{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "test-client", "version": "1.0.0"}}}')
    print()
    
    # Simple stdio-based server loop
    try:
        while True:
            try:
                # Read message from stdin
                line = await asyncio.get_event_loop().run_in_executor(
                    None, sys.stdin.readline
                )
                
                if not line:
                    break
                
                line = line.strip()
                if not line:
                    continue
                
                # Handle message
                response = await mcp_server.handle_message(line)
                
                if response:
                    print(response, flush=True)
                    
            except KeyboardInterrupt:
                print("\n👋 Shutting down MCP server...")
                break
            except Exception as e:
                print(f"Error: {e}", file=sys.stderr)
                
    except Exception as e:
        print(f"Server error: {e}", file=sys.stderr)
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))