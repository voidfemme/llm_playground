#!/usr/bin/env python3
"""
Multiple responses embedding example.

Shows how pair embeddings are created when a message has multiple responses
(different branches), and how to search across different response variants.
"""

import sys
from pathlib import Path

# Add source to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def main():
    """Demo multiple response handling with pair embeddings."""
    print("🌿 Multiple Responses Embedding Example")
    print("=" * 50)
    
    from chatbot_library.core.conversation_manager import ConversationManager
    
    # Create conversation manager
    data_dir = Path("data/multiple_responses_demo")
    manager = ConversationManager(
        data_dir=data_dir,
        enable_embeddings=True
    )
    print(f"✓ Created conversation manager")
    
    # Create conversation
    conversation = manager.create_conversation("Multiple Response Styles Demo")
    print(f"✓ Created conversation: {conversation.title}")
    
    # Add a message that will get multiple responses
    print(f"\n📝 Adding message that will get multiple response styles...")
    
    message = manager.add_message(
        conversation_id=conversation.id,
        user_id="demo_user",
        text="Explain how machine learning works in simple terms."
    )
    print(f"✓ Added message: {message.text}")
    print(f"  Message ID: {message.id}")
    
    # Add multiple responses with different styles/models
    print(f"\n🤖 Adding multiple responses to the same message...")
    
    # Response 1: Technical/detailed (main branch)
    response1 = manager.add_response(
        conversation_id=conversation.id,
        message_id=message.id,
        model="claude-3-sonnet",
        text="Machine learning is a computational approach where algorithms learn patterns from data to make predictions or decisions. The system analyzes training data, identifies statistical relationships, and builds mathematical models that can generalize to new, unseen data. Key components include feature extraction, model selection, training processes, and validation techniques.",
        branch_name=None  # Main branch
    )
    print(f"✓ Response 1 (Technical): {response1.id}")
    print(f"  Model: {response1.model}")
    print(f"  Branch: {response1.branch_name or 'main'}")
    print(f"  Text: {response1.text[:80]}...")
    
    # Response 2: Simple/beginner-friendly
    response2 = manager.add_response(
        conversation_id=conversation.id,
        message_id=message.id,
        model="claude-3-haiku",
        text="Think of machine learning like teaching a computer to recognize patterns, just like how you learned to recognize cats vs dogs. You show the computer lots of examples, and it figures out the differences. Then when you show it a new picture, it can guess what it is based on what it learned.",
        branch_name="simple"
    )
    print(f"✓ Response 2 (Simple): {response2.id}")
    print(f"  Model: {response2.model}")
    print(f"  Branch: {response2.branch_name}")
    print(f"  Text: {response2.text[:80]}...")
    
    # Response 3: Creative/metaphorical
    response3 = manager.add_response(
        conversation_id=conversation.id,
        message_id=message.id,
        model="gpt-4-turbo",
        text="Machine learning is like having a really smart student who learns by example. Imagine showing this student thousands of photos of different weather patterns while telling them 'this is sunny, this is rainy, this is cloudy.' Eventually, the student becomes so good at spotting patterns that they can look at a new sky and predict the weather accurately.",
        branch_name="creative"
    )
    print(f"✓ Response 3 (Creative): {response3.id}")
    print(f"  Model: {response3.model}")
    print(f"  Branch: {response3.branch_name}")
    print(f"  Text: {response3.text[:80]}...")
    
    # Add another message to show the conversation continues
    message2 = manager.add_message(
        conversation_id=conversation.id,
        user_id="demo_user",
        text="Can you give me a practical example?"
    )
    
    # Add response to the follow-up (only one for now)
    response4 = manager.add_response(
        conversation_id=conversation.id,
        message_id=message2.id,
        model="claude-3-sonnet",
        text="A practical example is email spam detection. The system learns from thousands of emails labeled as 'spam' or 'not spam', identifying patterns like certain words, sender characteristics, or formatting. When a new email arrives, it uses these learned patterns to classify it automatically."
    )
    print(f"✓ Follow-up response: {response4.id}")
    
    # Show pair statistics
    print(f"\n📊 Conversation Pair Analysis:")
    stats = manager.get_conversation_pair_statistics()
    
    if "error" not in stats:
        print(f"  📄 Total pairs created: {stats['total_pairs']}")
        print(f"  🤖 Models used:")
        for model_stat in stats['models']:
            print(f"    • {model_stat['model']}: {model_stat['pairs']} pairs")
        
        # Check the database directly to show the pairs
        import sqlite3
        with sqlite3.connect(manager.vector_db_path) as conn:
            cursor = conn.execute("""
                SELECT id, message_id, response_id, model, branch_name, user_text, assistant_text
                FROM conversation_pair_embeddings 
                WHERE conversation_id = ?
                ORDER BY message_timestamp, response_timestamp
            """, (conversation.id,))
            
            print(f"\n🔗 Individual Pair Embeddings Created:")
            for i, row in enumerate(cursor.fetchall(), 1):
                pair_id, msg_id, resp_id, model, branch, user_text, assistant_text = row
                print(f"  {i}. Pair ID: {pair_id}")
                print(f"     Message: {msg_id}")
                print(f"     Response: {resp_id}")
                print(f"     Model: {model}")
                print(f"     Branch: {branch or 'main'}")
                print(f"     User: {user_text[:50]}...")
                print(f"     Assistant: {assistant_text[:50]}...")
                print()
    
    # Test semantic search across different response styles
    if manager.enable_embeddings:
        print(f"🔍 Semantic Search Across Response Styles:")
        print(f"-" * 50)
        
        # Search 1: Technical query
        print(f"\n1. Technical query: 'algorithms and statistical models'")
        results = manager.semantic_search_conversation_pairs(
            query="algorithms and statistical models",
            limit=5,
            similarity_threshold=0.2
        )
        
        for i, result in enumerate(results, 1):
            print(f"   {i}. Similarity: {result['similarity']:.3f} | Model: {result['model']} | Branch: {result['branch_name'] or 'main'}")
            print(f"      Assistant: {result['assistant_text'][:100]}...")
        
        # Search 2: Simple explanation query
        print(f"\n2. Simple explanation query: 'teaching patterns examples'")
        results = manager.semantic_search_conversation_pairs(
            query="teaching patterns examples",
            limit=5,
            similarity_threshold=0.2
        )
        
        for i, result in enumerate(results, 1):
            print(f"   {i}. Similarity: {result['similarity']:.3f} | Model: {result['model']} | Branch: {result['branch_name'] or 'main'}")
            print(f"      Assistant: {result['assistant_text'][:100]}...")
        
        # Search 3: Filter by specific branch
        print(f"\n3. Search only 'simple' branch responses:")
        results = manager.semantic_search_conversation_pairs(
            query="machine learning explanation",
            branch_name="simple",
            limit=5,
            similarity_threshold=0.1
        )
        
        for i, result in enumerate(results, 1):
            print(f"   {i}. Similarity: {result['similarity']:.3f} | Branch: {result['branch_name']}")
            print(f"      Assistant: {result['assistant_text'][:100]}...")
        
        # Search 4: Filter by model
        print(f"\n4. Search only Claude Haiku responses:")
        results = manager.semantic_search_conversation_pairs(
            query="learning patterns",
            model="claude-3-haiku",
            limit=5,
            similarity_threshold=0.1
        )
        
        for i, result in enumerate(results, 1):
            print(f"   {i}. Similarity: {result['similarity']:.3f} | Model: {result['model']}")
            print(f"      Assistant: {result['assistant_text'][:100]}...")
    
    # Show conversation context building
    print(f"\n📖 Conversation Context Building:")
    print(f"-" * 40)
    
    # Get context following main branch
    print(f"\nMain branch context:")
    main_context = conversation.get_conversation_context()
    for i, turn in enumerate(main_context, 1):
        role_emoji = "👤" if turn['role'] == 'user' else "🤖"
        print(f"  {i}. {role_emoji} {turn['role']}: {turn['content'][:60]}...")
    
    # Get context following simple branch
    print(f"\nSimple branch context:")
    simple_context = conversation.get_conversation_context(branch_name="simple")
    for i, turn in enumerate(simple_context, 1):
        role_emoji = "👤" if turn['role'] == 'user' else "🤖"
        print(f"  {i}. {role_emoji} {turn['role']}: {turn['content'][:60]}...")
    
    # Get context following creative branch
    print(f"\nCreative branch context:")
    creative_context = conversation.get_conversation_context(branch_name="creative")
    for i, turn in enumerate(creative_context, 1):
        role_emoji = "👤" if turn['role'] == 'user' else "🤖"
        print(f"  {i}. {role_emoji} {turn['role']}: {turn['content'][:60]}...")
    
    print(f"\n✅ Multiple Responses Demo Complete!")
    
    print(f"\n🎯 Key Insights:")
    print(f"  ✓ Each message/response pair gets its own embedding")
    print(f"  ✓ Multiple responses = multiple pair embeddings")
    print(f"  ✓ Can search across all response variants")
    print(f"  ✓ Can filter by branch name or model")
    print(f"  ✓ Conversation context follows specific branches")
    
    print(f"\n💡 Multiple Response Benefits:")
    print(f"  • Find best response style for query")
    print(f"  • Compare different model approaches")
    print(f"  • Search specific explanation types")
    print(f"  • Analyze response quality differences")
    print(f"  • Support different user skill levels")
    
    print(f"\n🔍 Search Capabilities:")
    print(f"  • Semantic search across all variants")
    print(f"  • Filter by response branch/style")
    print(f"  • Filter by model that generated response")
    print(f"  • Find similar explanations of same concept")
    print(f"  • Discover best-performing response patterns")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())