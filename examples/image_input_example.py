#!/usr/bin/env python3
"""
Image input example for modern conversation system.
Shows how to handle image attachments with different LLM providers.
"""

import sys
import os
import base64
from pathlib import Path

# Add source to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def encode_image_to_base64(image_path: Path) -> str:
    """Encode image file to base64 string."""
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except Exception as e:
        print(f"Error encoding image: {e}")
        return ""

def call_anthropic_with_image(messages, model="claude-3-5-sonnet-20241022"):
    """Call Anthropic API with image support."""
    try:
        import anthropic
        client = anthropic.Anthropic()
        
        # Convert messages to Anthropic format with image support
        anthropic_messages = []
        system_msg = None
        
        for msg in messages:
            if msg["role"] == "system":
                system_msg = msg["content"]
            elif msg["role"] == "user":
                content = []
                
                # Add text if present
                if isinstance(msg["content"], str):
                    content.append({"type": "text", "text": msg["content"]})
                elif isinstance(msg["content"], list):
                    content = msg["content"]
                
                # Add images from attachments
                if "attachments" in msg:
                    for attachment in msg["attachments"]:
                        if attachment["media_type"].startswith("image/"):
                            content.append({
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": attachment["media_type"],
                                    "data": attachment["data"]
                                }
                            })
                
                anthropic_messages.append({
                    "role": "user",
                    "content": content
                })
            else:  # assistant
                anthropic_messages.append(msg)
        
        response = client.messages.create(
            model=model,
            max_tokens=300,
            temperature=0.7,
            system=system_msg or "You are a helpful assistant that can analyze images.",
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

def call_openai_with_image(messages, model="gpt-4o"):
    """Call OpenAI API with image support."""
    try:
        import openai
        client = openai.OpenAI()
        
        # Convert messages to OpenAI format with image support
        openai_messages = []
        
        for msg in messages:
            if msg["role"] in ["system", "assistant"]:
                openai_messages.append(msg)
            elif msg["role"] == "user":
                content = []
                
                # Add text if present
                if isinstance(msg["content"], str):
                    content.append({"type": "text", "text": msg["content"]})
                elif isinstance(msg["content"], list):
                    content = msg["content"]
                
                # Add images from attachments
                if "attachments" in msg:
                    for attachment in msg["attachments"]:
                        if attachment["media_type"].startswith("image/"):
                            content.append({
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:{attachment['media_type']};base64,{attachment['data']}",
                                    "detail": attachment.get("detail", "auto")
                                }
                            })
                
                openai_messages.append({
                    "role": "user",
                    "content": content
                })
        
        response = client.chat.completions.create(
            model=model,
            messages=openai_messages,
            max_tokens=300,
            temperature=0.7
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

def create_sample_image():
    """Create a simple sample image for testing."""
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        # Create a simple test image
        img = Image.new('RGB', (400, 200), color='lightblue')
        draw = ImageDraw.Draw(img)
        
        # Draw some text
        try:
            # Try to use a default font
            font = ImageFont.load_default()
        except:
            font = None
        
        draw.text((50, 80), "Hello from Chatbot Library!", fill='black', font=font)
        draw.rectangle([50, 120, 350, 150], outline='red', width=3)
        
        # Save the image
        sample_path = Path("data/sample_image.png")
        sample_path.parent.mkdir(parents=True, exist_ok=True)
        img.save(sample_path)
        
        return sample_path
    except ImportError:
        print("⚠ PIL not available, creating text-based 'image'")
        # Create a text file as a placeholder
        sample_path = Path("data/sample_image.txt")
        sample_path.parent.mkdir(parents=True, exist_ok=True)
        sample_path.write_text("This is a sample text file representing an image for testing.")
        return sample_path

def main():
    """Demo image input capabilities with modern conversation system."""
    print("🖼️  Image Input Example")
    print("=" * 35)
    
    from chatbot_library.core.conversation_manager import ConversationManager
    from chatbot_library.models.conversation import Attachment
    
    # Check available APIs
    apis_available = []
    
    if os.getenv("ANTHROPIC_API_KEY"):
        try:
            import anthropic
            apis_available.append(("anthropic", call_anthropic_with_image, "claude-3-5-sonnet-20241022"))
            print("✓ Anthropic Claude available (supports images)")
        except ImportError:
            print("⚠ anthropic package not installed")
    else:
        print("⚠ ANTHROPIC_API_KEY not set")
    
    if os.getenv("OPENAI_API_KEY"):
        try:
            import openai
            apis_available.append(("openai", call_openai_with_image, "gpt-4o"))
            print("✓ OpenAI GPT-4V available (supports images)")
        except ImportError:
            print("⚠ openai package not installed")
    else:
        print("⚠ OPENAI_API_KEY not set")
    
    if not apis_available:
        print("\n⚠ No vision-capable APIs available. Demonstrating structure only.")
        apis_available = [("demo", None, "demo-vision-model")]
    
    # Create or find a sample image
    print(f"\n🖼️  Preparing sample image...")
    sample_image_path = create_sample_image()
    print(f"✓ Sample image ready: {sample_image_path}")
    
    # Create conversation manager
    data_dir = Path("data/image_input_demo")
    manager = ConversationManager(data_dir=data_dir)
    print(f"✓ Created conversation manager")
    
    # Create conversation
    conversation = manager.create_conversation("Image Analysis Demo")
    print(f"✓ Created conversation: {conversation.title}")
    
    # Prepare image attachment
    if sample_image_path.suffix.lower() in ['.png', '.jpg', '.jpeg', '.gif', '.webp']:
        media_type = f"image/{sample_image_path.suffix[1:].lower()}"
        if media_type == "image/jpg":
            media_type = "image/jpeg"
    else:
        media_type = "text/plain"  # For our text placeholder
    
    image_data = ""
    if sample_image_path.exists():
        if media_type.startswith("image/"):
            image_data = encode_image_to_base64(sample_image_path)
        else:
            image_data = base64.b64encode(sample_image_path.read_bytes()).decode('utf-8')
    
    if not image_data:
        print("❌ Could not load image data")
        return 1
    
    # Create attachment object
    image_attachment = Attachment(
        id=str(Path(sample_image_path).name),
        content_type=media_type,
        media_type=media_type,
        data=image_data,
        source_type="base64",
        detail="auto",
        file_path=str(sample_image_path)
    )
    
    print(f"✓ Created image attachment: {len(image_data)} chars, {media_type}")
    
    # Add message with image
    message_text = "Can you analyze this image and tell me what you see?"
    
    message = manager.add_message(
        conversation_id=conversation.id,
        user_id="demo_user",
        text=message_text,
        attachments=[image_attachment]
    )
    
    print(f"\n📝 Added message with image attachment")
    print(f"  Text: {message_text}")
    print(f"  Attachment: {image_attachment.id} ({media_type})")
    
    # Test with available vision APIs
    for api_name, api_function, default_model in apis_available:
        print(f"\n🔍 Testing {api_name} vision analysis...")
        
        if api_function is None:
            # Demo mode - create mock response
            response = {
                "content": f"[Demo Mode] I can see this is a sample image created for testing the chatbot library's image input capabilities. The image appears to contain text and geometric shapes, demonstrating that the {api_name} vision model would be able to analyze visual content in conversations.",
                "model": default_model,
                "usage": {"input_tokens": 45, "output_tokens": 82}
            }
        else:
            # Build API message with image
            api_messages = [
                {
                    "role": "system",
                    "content": "You are a helpful assistant that can analyze images. Describe what you see in detail."
                },
                {
                    "role": "user",
                    "content": message_text,
                    "attachments": [
                        {
                            "id": image_attachment.id,
                            "media_type": image_attachment.media_type,
                            "data": image_attachment.data,
                            "detail": image_attachment.detail
                        }
                    ]
                }
            ]
            
            # Call API
            response = api_function(api_messages, default_model)
        
        if response and response.get("content"):
            # Add response to conversation
            ai_response = manager.add_response(
                conversation_id=conversation.id,
                message_id=message.id,
                model=response["model"],
                text=response["content"],
                branch_name=api_name,
                metadata={
                    "usage": response.get("usage", {}),
                    "api_provider": api_name,
                    "supports_vision": True,
                    "image_analyzed": True
                }
            )
            
            print(f"  📄 Response: {response['content'][:100]}...")
            print(f"  ✓ {api_name} vision analysis successful!")
            
            # Show usage if available
            usage = response.get("usage", {})
            if usage:
                print(f"  📊 Usage: {usage.get('input_tokens', 0)} in → {usage.get('output_tokens', 0)} out")
        else:
            print(f"  ❌ No response from {api_name}")
    
    # Show conversation state
    print(f"\n📊 Conversation Analysis:")
    conversation = manager.get_conversation(conversation.id)
    
    print(f"  📄 Messages: {len(conversation.messages)}")
    print(f"  🖼️  Messages with attachments: {sum(1 for msg in conversation.messages if msg.attachments)}")
    
    branches = conversation.get_all_branches()
    print(f"  🌿 Response branches: {list(branches.keys()) if branches else ['main']}")
    
    # Show conversation context
    print(f"\n📝 Conversation Context (Main Branch):")
    context = conversation.get_conversation_context()
    
    for i, turn in enumerate(context, 1):
        role_emoji = "👤" if turn['role'] == 'user' else "🤖"
        content_preview = turn['content'][:80] + "..." if len(turn['content']) > 80 else turn['content']
        print(f"  {i}. {role_emoji} {turn['role']}: {content_preview}")
        
        # Note attachments
        if 'attachments' in turn:
            for att in turn['attachments']:
                print(f"      📎 Attachment: {att['id']} ({att['media_type']})")
    
    # Show JSON storage
    print(f"\n💾 JSON Storage:")
    conversation_file = data_dir / f"{conversation.id}.json"
    if conversation_file.exists():
        size_kb = conversation_file.stat().st_size / 1024
        print(f"  📄 {conversation_file.name}: {size_kb:.1f} KB")
        print(f"  📦 Includes base64 image data in JSON")
    
    print(f"\n✅ Image Input Demo Complete!")
    
    print(f"\n🎯 Key Features Demonstrated:")
    print(f"  ✓ Image attachment support in modern structure")
    print(f"  ✓ Base64 encoding for image storage")
    print(f"  ✓ Vision API integration (Anthropic Claude, OpenAI GPT-4V)")
    print(f"  ✓ Image metadata preservation")
    print(f"  ✓ JSON serialization with image data")
    print(f"  ✓ Multiple vision model responses per image")
    
    print(f"\n🖼️  Supported Image Features:")
    print(f"  • Multiple formats: PNG, JPEG, GIF, WebP")
    print(f"  • Base64 encoding for storage")
    print(f"  • Metadata preservation (file path, media type)")
    print(f"  • Vision API integration ready")
    print(f"  • Response branching by vision model")
    
    print(f"\n🚀 Next Steps:")
    print(f"  • Add image preprocessing (resize, optimize)")
    print(f"  • Implement image embedding generation")
    print(f"  • Add image similarity search")
    print(f"  • Create Chainlit UI with image upload")
    print(f"  • Add drag-and-drop image support")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())