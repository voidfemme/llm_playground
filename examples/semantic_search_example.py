#!/usr/bin/env python3
"""
Semantic search example using the enhanced conversation manager.
"""

import sys
import os
from pathlib import Path

# Add source to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def main():
    """Demo of semantic search capabilities."""
    print("🔍 Semantic Search Example")
    print("=" * 35)
    
    from chatbot_library.core.conversation_manager import ConversationManager
    
    # Check if embedding dependencies are available
    try:
        from sentence_transformers import SentenceTransformer
        embeddings_available = True
        print("✓ Embedding model available")
    except ImportError:
        embeddings_available = False
        print("❌ sentence-transformers not installed")
        print("   Install with: pip install sentence-transformers")
        return 1
    
    # Create enhanced conversation manager
    data_dir = Path("data/semantic_search_demo")
    manager = ConversationManager(
        data_dir=data_dir,
        enable_embeddings=True
    )
    print(f"✓ Created enhanced conversation manager")
    print(f"  Data directory: {data_dir}")
    print(f"  Vector database: {manager.vector_db_path}")
    
    # Create sample conversations with diverse topics
    print(f"\n📚 Creating sample conversations...")
    
    # Conversation 1: Programming
    conv1 = manager.create_conversation("Python Programming Discussion")
    msg1_1 = manager.add_message(
        conversation_id=conv1.id,
        user_id="developer",
        text="How do I implement a binary search algorithm in Python?"
    )
    resp1_1 = manager.add_response(
        conversation_id=conv1.id,
        message_id=msg1_1.id,
        model="claude-3-sonnet",
        text="Here's a clean implementation of binary search in Python:\\n\\ndef binary_search(arr, target):\\n    left, right = 0, len(arr) - 1\\n    while left <= right:\\n        mid = (left + right) // 2\\n        if arr[mid] == target:\\n            return mid\\n        elif arr[mid] < target:\\n            left = mid + 1\\n        else:\\n            right = mid - 1\\n    return -1\\n\\nThis algorithm has O(log n) time complexity."
    )
    
    msg1_2 = manager.add_message(
        conversation_id=conv1.id,
        user_id="developer",
        text="What about recursive implementation of binary search?"
    )
    resp1_2 = manager.add_response(
        conversation_id=conv1.id,
        message_id=msg1_2.id,
        model="claude-3-sonnet",
        text="Here's the recursive version:\\n\\ndef binary_search_recursive(arr, target, left=0, right=None):\\n    if right is None:\\n        right = len(arr) - 1\\n    \\n    if left > right:\\n        return -1\\n    \\n    mid = (left + right) // 2\\n    if arr[mid] == target:\\n        return mid\\n    elif arr[mid] < target:\\n        return binary_search_recursive(arr, target, mid + 1, right)\\n    else:\\n        return binary_search_recursive(arr, target, left, mid - 1)"
    )
    
    # Conversation 2: Machine Learning
    conv2 = manager.create_conversation("Machine Learning Basics")
    msg2_1 = manager.add_message(
        conversation_id=conv2.id,
        user_id="student",
        text="Can you explain what neural networks are and how they work?"
    )
    resp2_1 = manager.add_response(
        conversation_id=conv2.id,
        message_id=msg2_1.id,
        model="gpt-4-turbo",
        text="Neural networks are computational models inspired by biological neural networks. They consist of interconnected nodes (neurons) organized in layers. Each connection has a weight, and neurons apply activation functions to weighted inputs. Through training with backpropagation, the network learns to map inputs to desired outputs by adjusting these weights."
    )
    
    msg2_2 = manager.add_message(
        conversation_id=conv2.id,
        user_id="student", 
        text="What's the difference between supervised and unsupervised learning?"
    )
    resp2_2 = manager.add_response(
        conversation_id=conv2.id,
        message_id=msg2_2.id,
        model="gpt-4-turbo",
        text="Supervised learning uses labeled training data to learn mappings from inputs to outputs (like classification or regression). Unsupervised learning finds patterns in data without labels, such as clustering similar data points or reducing dimensionality. Semi-supervised learning combines both approaches."
    )
    
    # Conversation 3: Cooking
    conv3 = manager.create_conversation("Italian Cooking Tips")
    msg3_1 = manager.add_message(
        conversation_id=conv3.id,
        user_id="chef",
        text="What's the secret to making perfect pasta?"
    )
    resp3_1 = manager.add_response(
        conversation_id=conv3.id,
        message_id=msg3_1.id,
        model="claude-3-sonnet",
        text="The key to perfect pasta is using plenty of salted water (1 liter per 100g pasta), cooking al dente (slightly firm to the bite), and reserving pasta water to help bind the sauce. Always finish cooking the pasta in the sauce for the last 1-2 minutes to marry the flavors."
    )
    
    # Conversation 4: Data Structures
    conv4 = manager.create_conversation("Data Structures and Algorithms")
    msg4_1 = manager.add_message(
        conversation_id=conv4.id,
        user_id="student",
        text="How do hash tables work and why are they so efficient?"
    )
    resp4_1 = manager.add_response(
        conversation_id=conv4.id,
        message_id=msg4_1.id,
        model="claude-3-sonnet",
        text="Hash tables use a hash function to map keys to array indices, enabling O(1) average-case lookup, insertion, and deletion. The hash function distributes keys uniformly across the array. Collisions are handled through techniques like chaining (linked lists) or open addressing (probing). This makes hash tables extremely efficient for key-value operations."
    )
    
    print(f"✓ Created {len([conv1, conv2, conv3, conv4])} sample conversations")
    print(f"✓ Added {sum(len(conv.messages) for conv in [conv1, conv2, conv3, conv4])} messages with embeddings")
    
    # Demonstrate semantic search
    print(f"\n🔍 Semantic Search Examples:")
    print(f"-" * 40)
    
    # Search 1: Algorithm-related
    print(f"\n1. Searching for: 'algorithm implementation'")
    results = manager.semantic_search_messages(
        query="algorithm implementation",
        limit=3,
        similarity_threshold=0.3
    )
    
    for i, result in enumerate(results, 1):
        print(f"   {i}. Similarity: {result['similarity']:.3f}")
        print(f"      Text: {result['text'][:80]}...")
        print(f"      From: {result['conversation_id'][:8]}... ({result['user_id']})")
    
    # Search 2: Learning-related
    print(f"\n2. Searching for: 'learning patterns data'")
    results = manager.semantic_search_messages(
        query="learning patterns data",
        limit=3,
        similarity_threshold=0.3
    )
    
    for i, result in enumerate(results, 1):
        print(f"   {i}. Similarity: {result['similarity']:.3f}")
        print(f"      Text: {result['text'][:80]}...")
        print(f"      From: {result['conversation_id'][:8]}... ({result['user_id']})")
    
    # Search 3: Response search
    print(f"\n3. Searching responses for: 'efficient performance'")
    response_results = manager.semantic_search_responses(
        query="efficient performance",
        limit=3,
        similarity_threshold=0.3
    )
    
    for i, result in enumerate(response_results, 1):
        print(f"   {i}. Similarity: {result['similarity']:.3f}")
        print(f"      Text: {result['text'][:80]}...")
        print(f"      Model: {result['model']} | Branch: {result['branch_name'] or 'main'}")
    
    # Find similar conversations
    print(f"\n🌐 Finding Similar Conversations:")
    print(f"-" * 40)
    
    similar_convs = manager.find_similar_conversations(
        conversation_id=conv1.id,  # Programming conversation
        limit=3,
        similarity_threshold=0.4
    )
    
    print(f"\\nConversations similar to '{conv1.title}':")
    for i, conv in enumerate(similar_convs, 1):
        print(f"   {i}. {conv['title']}")
        print(f"      Similarity: {conv['similarity']:.3f}")
        print(f"      Messages: {conv['message_count']} | Matches: {conv['matching_messages']}")
    
    # Extract conversation topics
    print(f"\n🏷️  Conversation Topics:")
    print(f"-" * 40)
    
    for conv in [conv1, conv2, conv3, conv4]:
        topics = manager.get_conversation_topics(conv.id, num_topics=3)
        print(f"\\n'{conv.title}': {', '.join(topics) if topics else 'No topics found'}")
    
    # Show database statistics
    print(f"\n📊 Vector Database Statistics:")
    print(f"-" * 40)
    
    import sqlite3
    with sqlite3.connect(manager.vector_db_path) as conn:
        msg_count = conn.execute("SELECT COUNT(*) FROM message_embeddings").fetchone()[0]
        resp_count = conn.execute("SELECT COUNT(*) FROM response_embeddings").fetchone()[0]
        
        print(f"  📝 Message embeddings: {msg_count}")
        print(f"  🤖 Response embeddings: {resp_count}")
        print(f"  📁 Vector database size: {manager.vector_db_path.stat().st_size / 1024:.1f} KB")
    
    # Show conversation storage
    conv_list = manager.get_conversation_list()
    print(f"  💾 JSON conversations: {len(conv_list)}")
    
    print(f"\n✅ Semantic Search Demo Complete!")
    
    print(f"\n🎯 Key Features Demonstrated:")
    print(f"  ✓ Automatic embedding generation")
    print(f"  ✓ Hybrid storage (JSON + SQLite)")
    print(f"  ✓ Message semantic search")
    print(f"  ✓ Response semantic search")
    print(f"  ✓ Similar conversation discovery")
    print(f"  ✓ Topic extraction")
    print(f"  ✓ Cosine similarity calculations")
    
    print(f"\n🚀 Next Steps:")
    print(f"  • Install sqlite-vec for optimized vector search")
    print(f"  • Add more advanced topic modeling")
    print(f"  • Implement conversation clustering")
    print(f"  • Create embeddings for existing conversations")
    print(f"  • Add hybrid search (semantic + keyword)")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())