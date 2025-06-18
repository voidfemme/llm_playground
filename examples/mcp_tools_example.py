"""
Example demonstrating the new MCP-compatible tool system.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add source to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from chatbot_library.core.mcp_integration import MCPConversationManager
from chatbot_library.tools.mcp_tool_registry import MCPTool, MCPToolSchema, mcp_tool_registry
from chatbot_library.tools.builtin_tools import register_builtin_tools


# Example of creating a custom MCP tool
class TextAnalysisTool(MCPTool):
    """Analyze text for various metrics."""
    
    def get_schema(self) -> MCPToolSchema:
        return MCPToolSchema(
            name="analyze_text",
            description="Analyze text for readability, sentiment, and other metrics",
            input_schema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "The text to analyze"
                    },
                    "metrics": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "enum": ["readability", "sentiment", "word_count", "complexity"]
                        },
                        "description": "Which metrics to calculate",
                        "default": ["word_count", "readability"]
                    }
                },
                "required": ["text"]
            },
            metadata={
                "category": "text_analysis",
                "cost": 0,
                "latency": "low"
            }
        )
    
    async def execute(self, text: str, metrics: list = None) -> dict:
        """Execute text analysis."""
        if metrics is None:
            metrics = ["word_count", "readability"]
        
        results = {}
        
        if "word_count" in metrics:
            results["word_count"] = len(text.split())
            results["character_count"] = len(text)
            results["sentence_count"] = text.count('.') + text.count('!') + text.count('?')
        
        if "readability" in metrics:
            # Simple readability score (Flesch-like approximation)
            words = len(text.split())
            sentences = max(1, text.count('.') + text.count('!') + text.count('?'))
            syllables = sum([self._count_syllables(word) for word in text.split()])
            
            if words > 0 and sentences > 0:
                avg_sentence_length = words / sentences
                avg_syllables_per_word = syllables / words
                readability_score = 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_syllables_per_word)
                results["readability_score"] = max(0, min(100, readability_score))
                results["reading_level"] = self._get_reading_level(readability_score)
        
        if "sentiment" in metrics:
            # Simple sentiment analysis (placeholder)
            positive_words = ["good", "great", "excellent", "amazing", "wonderful", "love", "best"]
            negative_words = ["bad", "terrible", "awful", "hate", "worst", "horrible", "sad"]
            
            text_lower = text.lower()
            positive_count = sum(1 for word in positive_words if word in text_lower)
            negative_count = sum(1 for word in negative_words if word in text_lower)
            
            if positive_count > negative_count:
                sentiment = "positive"
            elif negative_count > positive_count:
                sentiment = "negative"
            else:
                sentiment = "neutral"
            
            results["sentiment"] = sentiment
            results["sentiment_confidence"] = abs(positive_count - negative_count) / max(1, positive_count + negative_count)
        
        if "complexity" in metrics:
            words = text.split()
            long_words = [word for word in words if len(word) > 6]
            results["complexity_score"] = len(long_words) / max(1, len(words))
            results["avg_word_length"] = sum(len(word) for word in words) / max(1, len(words))
        
        return results
    
    def _count_syllables(self, word: str) -> int:
        """Simple syllable counting."""
        word = word.lower()
        vowels = "aeiouy"
        syllable_count = 0
        prev_was_vowel = False
        
        for char in word:
            if char in vowels:
                if not prev_was_vowel:
                    syllable_count += 1
                prev_was_vowel = True
            else:
                prev_was_vowel = False
        
        # Handle silent e
        if word.endswith('e') and syllable_count > 1:
            syllable_count -= 1
        
        return max(1, syllable_count)
    
    def _get_reading_level(self, score: float) -> str:
        """Convert readability score to reading level."""
        if score >= 90:
            return "Very Easy"
        elif score >= 80:
            return "Easy"
        elif score >= 70:
            return "Fairly Easy"
        elif score >= 60:
            return "Standard"
        elif score >= 50:
            return "Fairly Difficult"
        elif score >= 30:
            return "Difficult"
        else:
            return "Very Difficult"


async def main():
    """Demonstrate MCP tools usage."""
    print("🔧 MCP Tools Example")
    print("=" * 50)
    
    # Initialize conversation manager with MCP integration
    manager = MCPConversationManager("data/mcp_tools_demo")
    
    # Register our custom tool
    manager.tool_registry.register_tool(TextAnalysisTool())
    
    print(f"📋 Available tools: {len(manager.get_available_tools())}")
    
    # List all available tools
    print("\n🛠️ Available Tools:")
    for tool in manager.get_available_tools():
        print(f"  • {tool['name']}: {tool['description']}")
    
    print("\n" + "=" * 50)
    
    # Create a conversation
    conversation = manager.create_conversation("MCP Tools Demo")
    print(f"💬 Created conversation: {conversation.title}")
    
    # Example 1: Using built-in time tool
    print("\n⏰ Testing time tool...")
    time_result = await manager.execute_tool(
        "get_current_time", 
        {"format": "readable"},
        conversation.id
    )
    print(f"   Result: {time_result.result}")
    print(f"   Success: {time_result.success}")
    print(f"   Execution time: {time_result.execution_time:.3f}s")
    
    # Example 2: Using calculator tool
    print("\n🧮 Testing calculator tool...")
    calc_result = await manager.execute_tool(
        "calculate",
        {"expression": "2 + 3 * 4", "precision": 2},
        conversation.id
    )
    print(f"   Expression: {calc_result.result['expression']}")
    print(f"   Result: {calc_result.result['formatted_result']}")
    
    # Example 3: Using custom text analysis tool
    print("\n📝 Testing text analysis tool...")
    sample_text = "This is a wonderful example of text analysis. It's quite amazing how we can analyze text automatically!"
    
    analysis_result = await manager.execute_tool(
        "analyze_text",
        {
            "text": sample_text,
            "metrics": ["word_count", "readability", "sentiment"]
        },
        conversation.id
    )
    
    if analysis_result.success:
        result = analysis_result.result
        print(f"   Text: '{sample_text}'")
        print(f"   Word count: {result.get('word_count')}")
        print(f"   Readability score: {result.get('readability_score', 0):.1f}")
        print(f"   Reading level: {result.get('reading_level')}")
        print(f"   Sentiment: {result.get('sentiment')}")
    
    # Example 4: Text length tool (decorator-based)
    print("\n📏 Testing text length tool...")
    length_result = await manager.execute_tool(
        "text_length",
        {"text": "Hello, MCP tools!", "include_spaces": True},
        conversation.id
    )
    
    if length_result.success:
        result = length_result.result
        print(f"   Text: '{result['text']}'")
        print(f"   Characters: {result['character_count']}")
        print(f"   Words: {result['word_count']}")
    
    # Example 5: Get tool recommendations
    print("\n💡 Testing tool recommendations...")
    recommendations = await manager.get_tool_recommendations(
        conversation.id,
        "What time is it and can you calculate 15 * 7?"
    )
    
    print("   Recommended tools:")
    for rec in recommendations:
        print(f"     • {rec['tool_name']} (score: {rec['score']}, relevance: {rec['relevance']})")
    
    # Example 6: Simulate adding a message with tool usage
    print("\n📨 Testing message with tools...")
    message = manager.add_message(
        conversation.id,
        "user",
        "Please analyze this text and tell me the time: 'Machine learning is transforming the world.'"
    )
    
    # Simulate AI response that used tools
    response = await manager.add_response_with_tools(
        conversation.id,
        message.id,
        "demo-analytical",
        "I've analyzed your text and checked the current time. The text has 7 words with a neutral sentiment and standard readability. The current time is shown above.",
        tools_used=[
            {"name": "analyze_text", "parameters": {"text": "Machine learning is transforming the world.", "metrics": ["word_count", "sentiment", "readability"]}},
            {"name": "get_current_time", "parameters": {"format": "readable"}}
        ],
        branch_name="with_tools"
    )
    
    print(f"   Response: {response.text}")
    print(f"   Tools in metadata: {len(response.metadata.get('tools_executed', []))}")
    
    # Example 7: Get conversation tool usage statistics
    print("\n📊 Conversation tool usage statistics:")
    tool_stats = manager.get_conversation_tool_usage(conversation.id)
    print(f"   Total tool executions: {tool_stats['total_tool_executions']}")
    print(f"   Success rate: {tool_stats['success_rate']:.1%}")
    print(f"   Total execution time: {tool_stats['total_execution_time']:.3f}s")
    
    if tool_stats['tools']:
        print("   Per-tool stats:")
        for tool_name, stats in tool_stats['tools'].items():
            print(f"     • {tool_name}: {stats['count']} uses, {stats['total_time']:.3f}s total")
    
    print("\n✅ MCP Tools demo completed!")


if __name__ == "__main__":
    asyncio.run(main())