#!/usr/bin/env python3
"""
Example script demonstrating how to use local models with Bitwarden Organizer.

This script shows different ways to configure and use local AI models
for organizing Bitwarden exports.
"""

import os
import sys
from pathlib import Path

# Add the parent directory to the path to import bitwarden_organizer
sys.path.insert(0, str(Path(__file__).parent.parent))

from bitwarden_organizer.ai_config import AIConfig, AICategorizer


def example_ollama_setup():
    """Example: Configure for Ollama local model."""
    print("=== Ollama Local Model Example ===")

    config = AIConfig(
        api_key="ollama",  # Ollama doesn't require real API keys
        model="llama-3.1-8b",
        base_url="http://localhost:11434/v1",
        temperature=0.1,
        max_tokens=1000
    )

    print(f"Model: {config.model}")
    print(f"Base URL: {config.base_url}")
    print(f"Temperature: {config.temperature}")

    # Initialize the AI categorizer
    try:
        categorizer = AICategorizer(config)
        print("✓ AI categorizer initialized successfully")
        return categorizer
    except Exception as e:
        print(f"✗ Failed to initialize: {e}")
        print("Make sure Ollama is running: ollama serve")
        return None


def example_localai_setup():
    """Example: Configure for LocalAI local model."""
    print("\n=== LocalAI Local Model Example ===")

    config = AIConfig(
        api_key="localai",
        model="llama-2-7b-chat",
        base_url="http://localhost:8080/v1",
        temperature=0.2,
        max_tokens=1500
    )

    print(f"Model: {config.model}")
    print(f"Base URL: {config.base_url}")
    print(f"Temperature: {config.temperature}")

    try:
        categorizer = AICategorizer(config)
        print("✓ AI categorizer initialized successfully")
        return categorizer
    except Exception as e:
        print(f"✗ Failed to initialize: {e}")
        print("Make sure LocalAI is running on port 8080")
        return None


def example_environment_variables():
    """Example: Configure using environment variables."""
    print("\n=== Environment Variables Example ===")

    # Set environment variables (in real usage, these would be in .env file)
    os.environ["OPENAI_API_KEY"] = "local"
    os.environ["OPENAI_BASE_URL"] = "http://localhost:11434/v1"
    os.environ["OPENAI_MODEL"] = "mistral:7b"
    os.environ["OPENAI_TEMPERATURE"] = "0.3"

    try:
        config = AIConfig.from_env()
        print(f"Model: {config.model}")
        print(f"Base URL: {config.base_url}")
        print(f"Temperature: {config.temperature}")

        categorizer = AICategorizer(config)
        print("✓ AI categorizer initialized successfully")

        # Clean up environment variables
        del os.environ["OPENAI_API_KEY"]
        del os.environ["OPENAI_BASE_URL"]
        del os.environ["OPENAI_MODEL"]
        del os.environ["OPENAI_TEMPERATURE"]

        return categorizer
    except Exception as e:
        print(f"✗ Failed to initialize: {e}")
        return None


def example_custom_endpoint():
    """Example: Configure for a custom OpenAI-compatible endpoint."""
    print("\n=== Custom Endpoint Example ===")

    config = AIConfig(
        api_key="your_custom_key",
        model="custom-model",
        base_url="https://your-custom-endpoint.com/v1",
        temperature=0.1,
        max_tokens=1000
    )

    print(f"Model: {config.model}")
    print(f"Base URL: {config.base_url}")
    print(f"Temperature: {config.temperature}")

    try:
        categorizer = AICategorizer(config)
        print("✓ AI categorizer initialized successfully")
        return categorizer
    except Exception as e:
        print(f"✗ Failed to initialize: {e}")
        return None


def test_categorization(categorizer, test_items):
    """Test categorization with sample items."""
    if not categorizer:
        return

    print(f"\n=== Testing Categorization with {categorizer.config.model} ===")

    for item in test_items:
        name = item["name"]
        description = item.get("description", "")
        uris = item.get("uris", [])

        try:
            category = categorizer.categorize_item(name, description, uris)
            print(f"'{name}' → {category}")
        except Exception as e:
            print(f"'{name}' → Error: {e}")


def main():
    """Main example function."""
    print("Bitwarden Organizer - Local Model Examples")
    print("=" * 50)

    # Sample test items
    test_items = [
        {"name": "GitHub", "description": "Code repository", "uris": ["https://github.com"]},
        {"name": "PayPal", "description": "Payment service", "uris": ["https://paypal.com"]},
        {"name": "Netflix", "description": "Streaming service", "uris": ["https://netflix.com"]},
    ]

    # Example 1: Ollama setup
    ollama_categorizer = example_ollama_setup()
    if ollama_categorizer:
        test_categorization(ollama_categorizer, test_items)

    # Example 2: LocalAI setup
    localai_categorizer = example_localai_setup()
    if localai_categorizer:
        test_categorization(localai_categorizer, test_items)

    # Example 3: Environment variables
    env_categorizer = example_environment_variables()
    if env_categorizer:
        test_categorization(env_categorizer, test_items)

    # Example 4: Custom endpoint
    custom_categorizer = example_custom_endpoint()
    if custom_categorizer:
        test_categorization(custom_categorizer, test_items)

    print("\n" + "=" * 50)
    print("Example Summary:")
    print("- Ollama: http://localhost:11434/v1")
    print("- LocalAI: http://localhost:8080/v1")
    print("- Environment variables: Use .env file")
    print("- Custom endpoints: Any OpenAI-compatible API")
    print("\nTo use with real data:")
    print("bitwarden-organize export.json --ai --ai-base-url http://localhost:11434/v1")


if __name__ == "__main__":
    main()
