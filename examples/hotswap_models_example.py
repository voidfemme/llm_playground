#!/usr/bin/env python3
"""
Hot-swapping models example with intelligent conversation adaptation.

Shows how to switch between models with different capabilities
(images, tools, context limits) in the same conversation.
"""

import sys
import os
from pathlib import Path

# Add source to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def main():
    """Demo hot-swapping models with different capabilities."""
    print("🔄 Hot-Swapping Models Example")
    print("=" * 40)
    
    from chatbot_library.core.conversation_manager import ConversationManager
    from chatbot_library.adapters.chatbot_adapter import ChatbotCapabilities
    from chatbot_library.models.conversation import Attachment
    
    # Create hot-swap enabled conversation manager
    data_dir = Path("data/hotswap_demo")
    manager = ConversationManager(data_dir=data_dir)
    print(f"✓ Created hot-swap conversation manager")
    
    # Register different model types with their capabilities
    print(f"\n🤖 Registering models with different capabilities...")
    
    # Vision model (supports images + tools)
    manager.register_model(
        "claude-3-5-sonnet",
        ChatbotCapabilities(
            function_calling=True,
            image_understanding=True,
            supported_images=["image/png", "image/jpeg", "image/gif", "image/webp"]
        ),
        {"provider": "anthropic", "context_limit": 200000}
    )
    
    # Tool-capable model (tools but no images)
    manager.register_model(
        "gpt-4-turbo",
        ChatbotCapabilities(
            function_calling=True,
            image_understanding=False,
            supported_images=[]
        ),
        {"provider": "openai", "context_limit": 128000}
    )
    
    # Basic text model (no tools, no images)
    manager.register_model(
        "claude-3-haiku",
        ChatbotCapabilities(
            function_calling=False,
            image_understanding=False,
            supported_images=[]
        ),
        {"provider": "anthropic", "context_limit": 200000}
    )
    
    # Vision-only model (images but no tools)
    manager.register_model(
        "gpt-4o",
        ChatbotCapabilities(
            function_calling=False,
            image_understanding=True,
            supported_images=["image/png", "image/jpeg", "image/gif", "image/webp"]
        ),
        {"provider": "openai", "context_limit": 128000}
    )
    
    print(f"✓ Registered {len(manager.get_available_models())} models")
    for model in manager.get_available_models():
        caps = model["capabilities"]
        print(f"  • {model['name']}: Tools={caps.function_calling}, Images={caps.image_understanding}")
    
    # Create conversation with mixed content
    print(f"\n💬 Creating conversation with mixed content...")
    conversation = manager.create_conversation("Hot-Swap Model Demo")
    
    # Add message with image (tests image handling)
    print(f"\n📸 Adding message with image...")
    sample_image = Attachment(
        id="test_image.png",
        content_type="image/png",
        media_type="image/png",
        data="iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg==",  # 1x1 red pixel
        source_type="base64"
    )
    
    image_message = manager.add_message(
        conversation_id=conversation.id,
        user_id="demo_user",
        text="Can you analyze this image and then search for related information?",
        attachments=[sample_image]
    )
    
    # Simulate tool use in response (tests tool handling)
    from chatbot_library.models.conversation import ToolUse
    tool_use = ToolUse(
        tool_name="web_search",
        tool_input={"query": "red pixel image analysis"},
        tool_use_id="search_001"
    )
    
    vision_response = manager.add_response(
        conversation_id=conversation.id,
        message_id=image_message.id,
        model="claude-3-5-sonnet",
        text="I can see this is a simple red pixel image. Let me search for more information about pixel-based images.",
        tool_use=tool_use,
        branch_name="vision_with_tools"
    )
    
    # Add follow-up message
    followup_message = manager.add_message(
        conversation_id=conversation.id,
        user_id="demo_user",
        text="Great! Now can you explain what you found in simple terms?"
    )
    
    print(f"✓ Created conversation with:")
    print(f"  • 2 user messages")
    print(f"  • 1 image attachment")
    print(f"  • 1 response with tool use")
    
    # Test model compatibility analysis
    print(f"\n🔍 Analyzing model compatibility...")
    
    models_to_test = ["claude-3-5-sonnet", "gpt-4-turbo", "claude-3-haiku", "gpt-4o"]
    
    for model in models_to_test:
        compat = manager.analyze_conversation_compatibility(conversation.id, model)
        print(f"\n{model}:")
        print(f"  Compatibility Score: {compat['compatibility_score']:.2f}")
        print(f"  Adaptations Needed: {len(compat.get('adaptations_needed', []))}")
        for adaptation in compat.get('adaptations_needed', []):
            print(f"    • {adaptation['type']}: {adaptation['description']}")
    
    # Get model recommendations
    print(f"\n💡 Model Recommendations for this conversation:")
    recommendations = manager.get_model_recommendations(conversation.id)
    
    for i, rec in enumerate(recommendations[:3], 1):
        print(f"  {i}. {rec['name']} (Score: {rec['compatibility_score']:.2f})")
        if rec.get('recommended'):
            print(f"     ✅ Recommended")
        else:
            print(f"     ⚠️  Needs adaptations")
    
    # Test getting adapted context for different models
    print(f"\n📝 Testing context adaptation for different models...")
    
    for model in ["claude-3-5-sonnet", "claude-3-haiku"]:
        print(f"\n--- Context for {model} ---")
        adapted_context = manager.get_conversation_context_for_model(
            conversation.id, 
            model
        )
        
        for i, turn in enumerate(adapted_context, 1):
            role_emoji = "👤" if turn['role'] == 'user' else "🤖"
            content_preview = turn['content'][:100] + "..." if len(turn['content']) > 100 else turn['content']
            print(f"  {i}. {role_emoji} {turn['role']}: {content_preview}")
            
            if 'original_attachments' in turn and turn['original_attachments'] > 0:
                print(f"      📎 Original attachments: {turn['original_attachments']}")
            if 'original_tool_use' in turn and turn['original_tool_use']:
                print(f"      🔧 Original tool use: Yes")
    
    # Simulate model switches
    print(f"\n🔄 Simulating model switches...")
    
    switches_to_test = [
        ("claude-3-5-sonnet", "claude-3-haiku"),  # Vision+Tools → Basic
        ("claude-3-haiku", "gpt-4o"),  # Basic → Vision only
        ("gpt-4o", "gpt-4-turbo")  # Vision → Tools
    ]
    
    for from_model, to_model in switches_to_test:
        print(f"\n{from_model} → {to_model}:")
        switch_analysis = manager.simulate_model_switch(
            conversation.id, 
            from_model, 
            to_model
        )
        
        analysis = switch_analysis["switch_analysis"]
        print(f"  Compatibility Change: {analysis['compatibility_change']:+.2f}")
        print(f"  Recommendation: {analysis['recommendation']}")
        
        if analysis["new_adaptations"]:
            print(f"  New Adaptations:")
            for adapt in analysis["new_adaptations"]:
                print(f"    + {adapt['type']}: {adapt['description']}")
        
        if analysis["removed_adaptations"]:
            print(f"  Removed Adaptations:")
            for adapt in analysis["removed_adaptations"]:
                print(f"    - {adapt['type']}: {adapt['description']}")
    
    # Show hot-swap statistics
    print(f"\n📊 Hot-Swap Statistics:")
    stats = manager.get_hotswap_statistics()
    
    print(f"  Total Models: {stats['total_models']}")
    print(f"  Total Usage: {stats['total_usage']}")
    
    for model_stat in stats['models']:
        caps = model_stat['capabilities']
        features = []
        if caps['images']:
            features.append("Images")
        if caps['tools']:
            features.append("Tools")
        feature_str = "+".join(features) if features else "Text-only"
        
        print(f"  • {model_stat['name']}: {feature_str}")
        print(f"    Usage: {model_stat['usage_count']} ({model_stat['usage_percentage']:.1f}%)")
        print(f"    Success Rate: {model_stat['success_rate']:.2f}")
    
    print(f"\n✅ Hot-Swapping Demo Complete!")
    
    print(f"\n🎯 Key Features Demonstrated:")
    print(f"  ✓ Model registration with capabilities")
    print(f"  ✓ Automatic conversation adaptation")
    print(f"  ✓ Compatibility analysis and scoring")
    print(f"  ✓ Model recommendations")
    print(f"  ✓ Context adaptation for different models")
    print(f"  ✓ Switch simulation and analysis")
    print(f"  ✓ Usage statistics and success tracking")
    
    print(f"\n🔄 Hot-Swapping Benefits:")
    print(f"  • Use best model for each task")
    print(f"  • Handle model capability differences")
    print(f"  • Maintain conversation continuity")
    print(f"  • Optimize cost vs capability")
    print(f"  • Fall back to simpler models when needed")
    
    print(f"\n🚀 Production Use Cases:")
    print(f"  • Cost optimization (use cheaper models when possible)")
    print(f"  • Capability routing (vision models for images)")
    print(f"  • Fallback strategies (when primary model fails)")
    print(f"  • A/B testing different models")
    print(f"  • Context length management")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())