#!/usr/bin/env python3
"""
Test script for AI integration in Bitwarden Organizer.

This script demonstrates how to use the AI-powered features
without requiring a full Bitwarden export.
"""

import os
import json
from bitwarden_organizer.ai_config import AIConfig, AICategorizer

def test_ai_categorization():
    """Test AI categorization with sample data."""
    
    # Check if OpenAI API key is available
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY not found in environment")
        print("Please set the environment variable or create a .env file")
        return False
    
    try:
        # Load AI configuration
        ai_config = AIConfig.from_env()
        print(f"✅ AI configuration loaded successfully")
        print(f"   Model: {ai_config.model}")
        print(f"   Max tokens: {ai_config.max_tokens}")
        print(f"   Temperature: {ai_config.temperature}")
        
        # Create AI categorizer
        categorizer = AICategorizer(ai_config)
        print(f"✅ AI categorizer initialized")
        
        # Test data
        test_items = [
            {
                "name": "My Bank Account",
                "notes": "Personal banking account",
                "uris": ["https://mybank.com"]
            },
            {
                "name": "GitHub",
                "notes": "Code repository and development",
                "uris": ["https://github.com"]
            },
            {
                "name": "Netflix",
                "notes": "Streaming service",
                "uris": ["https://netflix.com"]
            }
        ]
        
        print(f"\n🧪 Testing AI categorization with {len(test_items)} items...")
        
        for i, item in enumerate(test_items, 1):
            print(f"\n--- Item {i}: {item['name']} ---")
            
            # Test categorization
            category = categorizer.categorize_item(
                item['name'], 
                item['notes'], 
                item['uris']
            )
            print(f"   Category: {category}")
            
            # Test name suggestion
            suggested_name = categorizer.suggest_name(
                item['name'], 
                item['notes'], 
                item['uris']
            )
            print(f"   Suggested name: {suggested_name}")
            
            # Test tag generation
            tags = categorizer.generate_tags(
                item['name'], 
                category, 
                item['notes'], 
                item['uris']
            )
            print(f"   Tags: {', '.join(sorted(tags))}")
        
        print(f"\n✅ AI integration test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ AI integration test failed: {e}")
        return False

def test_batch_processing():
    """Test AI batch processing."""
    
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY not found - skipping batch test")
        return False
    
    try:
        # Load AI configuration
        ai_config = AIConfig.from_env()
        categorizer = AICategorizer(ai_config)
        
        # Create test items in Bitwarden format
        test_items = [
            {
                "id": "1",
                "name": "Amazon",
                "notes": "Online shopping",
                "login": {
                    "uris": [{"uri": "https://amazon.com"}]
                }
            },
            {
                "id": "2", 
                "name": "LinkedIn",
                "notes": "Professional networking",
                "login": {
                    "uris": [{"uri": "https://linkedin.com"}]
                }
            }
        ]
        
        print(f"\n🧪 Testing AI batch processing...")
        processed_items = categorizer.batch_process(test_items, batch_size=2)
        
        print(f"✅ Processed {len(processed_items)} items")
        for item in processed_items:
            print(f"   {item['name']}: {item.get('notes', '')[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Batch processing test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Bitwarden Organizer - AI Integration Test")
    print("=" * 50)
    
    # Test basic AI functionality
    basic_success = test_ai_categorization()
    
    # Test batch processing
    batch_success = test_batch_processing()
    
    print("\n" + "=" * 50)
    if basic_success and batch_success:
        print("🎉 All tests passed! AI integration is working correctly.")
        print("\nNext steps:")
        print("1. Use 'bitwarden-organize --ai' to organize your exports")
        print("2. Adjust batch size with '--ai-batch-size' for performance")
        print("3. Customize AI model with '--ai-model' if needed")
    else:
        print("⚠️  Some tests failed. Check your OpenAI API configuration.")
        print("\nTroubleshooting:")
        print("1. Verify OPENAI_API_KEY is set correctly")
        print("2. Check your OpenAI account has sufficient credits")
        print("3. Ensure the API key has proper permissions")
