#!/usr/bin/env python3
"""
Conversation pairs semantic search example.

Shows how embeddings are stored for complete message/response pairs
rather than individual messages, enabling semantic search of full exchanges.
"""

import sys
from pathlib import Path

# Add source to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def main():
    """Demo conversation pair embeddings and semantic search."""
    print("💬 Conversation Pairs Semantic Search")
    print("=" * 45)
    
    # Check embedding dependencies
    try:
        from sentence_transformers import SentenceTransformer
        print("✓ Embedding model available")
    except ImportError:
        print("❌ sentence-transformers not installed")
        print("   For full demo: pip install sentence-transformers")
        print("   Continuing with structure demo...")
    
    from chatbot_library.core.conversation_manager import ConversationManager
    from chatbot_library.models.conversation import Attachment, ToolUse
    
    # Create enhanced conversation manager for pairs
    data_dir = Path("data/conversation_pairs_demo")
    manager = ConversationManager(
        data_dir=data_dir,
        enable_embeddings=True
    )
    print(f"✓ Created pair-based conversation manager")
    print(f"  Data directory: {data_dir}")
    print(f"  Vector database: {manager.vector_db_path}")
    
    # Create sample conversations with diverse pair types
    print(f"\n📚 Creating sample conversation pairs...")
    
    # Conversation 1: Technical Q&A
    conv1 = manager.create_conversation("Python Programming Help")
    
    # Pair 1: Simple text exchange
    msg1_1 = manager.add_message(
        conversation_id=conv1.id,
        user_id="developer",
        text="How do I sort a list in Python?"
    )
    resp1_1 = manager.add_response(
        conversation_id=conv1.id,
        message_id=msg1_1.id,
        model="claude-3-sonnet",
        text="You can sort a list in Python using the sort() method for in-place sorting, or sorted() function for a new sorted list. Example: my_list.sort() or new_list = sorted(my_list)."
    )
    
    # Pair 2: Exchange with tool use
    msg1_2 = manager.add_message(
        conversation_id=conv1.id,
        user_id="developer",
        text="Can you show me the performance difference between sort() and sorted()?"
    )
    tool_use = ToolUse(
        tool_name="code_execution",
        tool_input={"code": "import timeit; # performance comparison code"},
        tool_use_id="perf_001"
    )
    resp1_2 = manager.add_response(
        conversation_id=conv1.id,
        message_id=msg1_2.id,
        model="claude-3-sonnet",
        text="Let me run a performance comparison for you. The sort() method is slightly faster since it modifies the list in-place, while sorted() creates a new list.",
        tool_use=tool_use
    )
    
    # Conversation 2: Data Science
    conv2 = manager.create_conversation("Data Analysis Questions")
    
    # Pair 3: Simple exchange
    msg2_1 = manager.add_message(
        conversation_id=conv2.id,
        user_id="analyst",
        text="What's the best way to handle missing data in pandas?"
    )
    resp2_1 = manager.add_response(
        conversation_id=conv2.id,
        message_id=msg2_1.id,
        model="gpt-4-turbo",
        text="For missing data in pandas, you have several options: dropna() to remove rows/columns with NaN, fillna() to replace with specific values, or interpolate() for numeric data. The choice depends on your data and analysis needs."
    )
    
    # Pair 4: Exchange with image
    image_attachment = Attachment(
        id="chart.png",
        content_type="image/png",
        media_type="image/png",
        data="iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg==",
        source_type="base64"
    )
    
    msg2_2 = manager.add_message(
        conversation_id=conv2.id,
        user_id="analyst",
        text="Can you analyze this data visualization and suggest improvements?",
        attachments=[image_attachment]
    )
    resp2_2 = manager.add_response(
        conversation_id=conv2.id,
        message_id=msg2_2.id,
        model="gpt-4o",
        text="Looking at your chart, I can see it's a simple visualization. To improve it, consider adding axis labels, a title, gridlines for easier reading, and perhaps using different colors to distinguish data categories better."
    )
    
    # Conversation 3: Different domain
    conv3 = manager.create_conversation("Cooking Tips")
    
    # Pair 5: Cooking exchange
    msg3_1 = manager.add_message(
        conversation_id=conv3.id,
        user_id="chef",
        text="What's the secret to perfectly fluffy pancakes?"
    )
    resp3_1 = manager.add_response(
        conversation_id=conv3.id,
        message_id=msg3_1.id,
        model="claude-3-sonnet",
        text="The key to fluffy pancakes is not overmixing the batter - mix just until combined with lumps remaining. Also, let the batter rest for 5 minutes, use fresh baking powder, and cook on medium heat with proper temperature control."
    )
    
    print(f"✓ Created {len([conv1, conv2, conv3])} conversations")
    print(f"✓ Added 5 message/response pairs with embeddings")
    
    # Show pair statistics
    print(f"\n📊 Conversation Pair Statistics:")
    stats = manager.get_conversation_pair_statistics()
    
    if "error" not in stats:
        print(f"  📄 Total pairs: {stats['total_pairs']}")
        print(f"  🕐 Recent pairs (24h): {stats['recent_pairs_24h']}")
        
        print(f"  🤖 Models used:")
        for model_stat in stats['models']:
            print(f"    • {model_stat['model']}: {model_stat['pairs']} pairs in {model_stat['conversations']} conversations")
        
        print(f"  🎯 Feature usage:")
        features = stats['features']
        print(f"    • With attachments: {features['pairs_with_attachments']}")
        print(f"    • With tool use: {features['pairs_with_tool_use']}")
        print(f"    • With both: {features['pairs_with_both']}")
        print(f"    • Text only: {features['text_only_pairs']}")
    else:
        print(f"  {stats['error']}")
    
    # Test semantic search for conversation pairs
    if manager.enable_embeddings:
        print(f"\n🔍 Semantic Search Examples:")
        print(f"-" * 40)
        
        # Search 1: Programming-related
        print(f"\n1. Searching for: 'python list sorting methods'")
        results = manager.semantic_search_conversation_pairs(
            query="python list sorting methods",
            limit=3,
            similarity_threshold=0.3
        )
        
        for i, result in enumerate(results, 1):
            print(f"   {i}. Similarity: {result['similarity']:.3f}")
            print(f"      User: {result['user_text'][:60]}...")
            print(f"      Assistant: {result['assistant_text'][:60]}...")
            print(f"      Model: {result['model']} | Pair: {result['pair_id']}")
            if result['has_tool_use']:
                print(f"      🔧 Used tools")
            if result['has_attachments']:
                print(f"      📎 Has attachments")
        
        # Search 2: Data analysis
        print(f"\n2. Searching for: 'data cleaning missing values'")
        results = manager.semantic_search_conversation_pairs(
            query="data cleaning missing values",
            limit=3,
            similarity_threshold=0.3
        )
        
        for i, result in enumerate(results, 1):
            print(f"   {i}. Similarity: {result['similarity']:.3f}")
            print(f"      User: {result['user_text'][:60]}...")
            print(f"      Assistant: {result['assistant_text'][:60]}...")
            print(f"      Model: {result['model']}")
        
        # Search 3: With filters
        print(f"\n3. Searching pairs with tool usage: 'performance comparison'")
        results = manager.semantic_search_conversation_pairs(
            query="performance comparison",
            has_tool_use=True,
            limit=3,
            similarity_threshold=0.2
        )
        
        for i, result in enumerate(results, 1):
            print(f"   {i}. Similarity: {result['similarity']:.3f}")
            print(f"      User: {result['user_text'][:60]}...")
            print(f"      Assistant: {result['assistant_text'][:60]}...")
            print(f"      🔧 Tool used: Yes")
        
        # Search 4: With attachments
        print(f"\n4. Searching pairs with images: 'chart visualization'")
        results = manager.semantic_search_conversation_pairs(
            query="chart visualization",
            has_attachments=True,
            limit=3,
            similarity_threshold=0.2
        )
        
        for i, result in enumerate(results, 1):
            print(f"   {i}. Similarity: {result['similarity']:.3f}")
            print(f"      User: {result['user_text'][:60]}...")
            print(f"      Assistant: {result['assistant_text'][:60]}...")
            print(f"      📎 Has attachments: Yes")
        
        # Find similar exchanges
        print(f"\n🔗 Finding Similar Exchanges:")
        print(f"-" * 40)
        
        similar = manager.find_similar_conversation_exchanges(
            conversation_id=conv1.id,
            message_id=msg1_1.id,
            response_id=resp1_1.id,
            limit=3
        )
        
        print(f"\nSimilar to Python sorting Q&A:")
        for i, sim in enumerate(similar, 1):
            print(f"  {i}. Similarity: {sim['similarity']:.3f}")
            print(f"     User: {sim['user_text'][:50]}...")
            print(f"     Assistant: {sim['assistant_text'][:50]}...")
            print(f"     From conversation: {sim['conversation_id'][:8]}...")
    
    else:
        print(f"\n⚠ Embeddings disabled - showing structure only")
    
    # Show database information
    print(f"\n💾 Database Storage:")
    if manager.vector_db_path.exists():
        size_kb = manager.vector_db_path.stat().st_size / 1024
        print(f"  📄 Vector database: {size_kb:.1f} KB")
        print(f"  🗂️  Stores complete conversation pairs")
        print(f"  🔍 Enables semantic search of full exchanges")
    
    # Show JSON storage for comparison
    json_files = list(data_dir.glob("*.json"))
    total_json_size = sum(f.stat().st_size for f in json_files) / 1024
    print(f"  📄 JSON conversations: {len(json_files)} files, {total_json_size:.1f} KB")
    
    print(f"\n✅ Conversation Pairs Demo Complete!")
    
    print(f"\n🎯 Key Features Demonstrated:")
    print(f"  ✓ Message/response pair embeddings (not separate)")
    print(f"  ✓ Combined text for complete exchange context")
    print(f"  ✓ Semantic search of full conversations")
    print(f"  ✓ Filtering by features (attachments, tools)")
    print(f"  ✓ Similar exchange discovery")
    print(f"  ✓ Detailed pair statistics")
    
    print(f"\n💡 Pair-based Embedding Benefits:")
    print(f"  • Search complete conversational context")
    print(f"  • Find similar Q&A exchanges")
    print(f"  • Preserve user-assistant relationship")
    print(f"  • Better semantic understanding")
    print(f"  • Reduced storage vs separate embeddings")
    
    print(f"\n🔍 Use Cases:")
    print(f"  • FAQ generation from conversations")
    print(f"  • Similar question/answer retrieval")
    print(f"  • Conversation quality analysis")
    print(f"  • Training data discovery")
    print(f"  • Context-aware response suggestions")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())