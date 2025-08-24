"""
AI configuration and OpenAI integration for Bitwarden organizer.

This module handles OpenAI API configuration and provides AI-powered
categorization, naming, and tagging capabilities.
"""

import os
from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Tuple
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


@dataclass
class AIConfig:
    """Configuration for AI-powered features."""

    api_key: str
    model: str = "gpt-4o-mini"
    max_tokens: int = 1000
    temperature: float = 0.1
    enabled: bool = True
    base_url: str = "https://api.openai.com/v1"

    # Feature flags
    categorization_enabled: bool = True
    name_suggestion_enabled: bool = True
    tag_generation_enabled: bool = True

    @classmethod
    def from_env(cls) -> "AIConfig":
        """Create AI config from environment variables."""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")

        return cls(
            api_key=api_key,
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            max_tokens=int(os.getenv("OPENAI_MAX_TOKENS", "1000")),
            temperature=float(os.getenv("OPENAI_TEMPERATURE", "0.1")),
            base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
            enabled=os.getenv("AI_CATEGORIZATION_ENABLED", "true").lower() == "true",
            categorization_enabled=os.getenv("AI_CATEGORIZATION_ENABLED", "true").lower() == "true",
            name_suggestion_enabled=os.getenv("AI_NAME_SUGGESTION_ENABLED", "true").lower() == "true",
            tag_generation_enabled=os.getenv("AI_TAG_GENERATION_ENABLED", "true").lower() == "true",
        )


class AICategorizer:
    """AI-powered categorizer using OpenAI."""

    def __init__(self, config: AIConfig):
        """Initialize AI categorizer with configuration."""
        self.config = config
        self.client = OpenAI(api_key=config.api_key)

        # Configure custom base URL for local models
        if config.base_url != "https://api.openai.com/v1":
            self.client.api_base = config.base_url
            print(f"Using custom OpenAI API base URL: {config.base_url}")

        # System prompts for different tasks
        self.categorization_prompt = """You are an expert at categorizing online accounts and services.
Given a website/service name and optional description, categorize it into one of these categories:
- Finance (banking, payments, crypto, investments)
- Social (social media, community, communication)
- Developer (coding, development tools, version control)
- Cloud (cloud services, hosting, infrastructure)
- Email (email services, communication)
- Shopping (e-commerce, retail, marketplaces)
- Government/Utilities (government services, utilities, official)
- Travel (travel booking, transportation, accommodation)
- Security (security tools, authentication, password managers)
- Entertainment (streaming, gaming, media)
- Education (learning platforms, courses, academic)
- Health (healthcare, fitness, medical)
- Business (business tools, productivity, professional)
- General (everything else)

Respond with ONLY the category name, nothing else."""

        self.naming_prompt = """You are an expert at creating clear, descriptive names for online accounts.
Given a website/service name and optional description, suggest a better name that is:
- Clear and descriptive
- Professional
- Easy to identify
- Not too generic (avoid "Website" or "Login")

Respond with ONLY the suggested name, nothing else."""

        self.tagging_prompt = """You are an expert at creating relevant tags for online accounts.
Given a website/service name, category, and optional description, suggest 3-5 relevant tags.
Tags should be:
- Short (1-3 words)
- Relevant to the service
- Useful for organization
- Lowercase, separated by commas

Respond with ONLY the tags, nothing else."""

    def categorize_item(self, name: str, description: str = "", uris: List[str] = None) -> str:
        """Use AI to categorize an item."""
        if not self.config.categorization_enabled:
            return "General"

        try:
            # Build context from URIs if available
            uri_context = ""
            if uris:
                domains = [uri.split("://")[-1].split("/")[0] if "://" in uri else uri
                          for uri in uris if uri]
                uri_context = f" Domains: {', '.join(domains)}"

            prompt = f"Name: {name}{uri_context}\nDescription: {description}\n\nCategory:"

            response = self.client.chat.completions.create(
                model=self.config.model,
                messages=[
                    {"role": "system", "content": self.categorization_prompt},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature
            )

            category = response.choices[0].message.content.strip()
            return category if category else "General"

        except Exception as e:
            print(f"AI categorization failed: {e}")
            return "General"

    def suggest_name(self, current_name: str, description: str = "", uris: List[str] = None) -> str:
        """Use AI to suggest a better name for an item."""
        if not self.config.name_suggestion_enabled:
            return current_name

        try:
            # Build context from URIs if available
            uri_context = ""
            if uris:
                domains = [uri.split("://")[-1].split("/")[0] if "://" in uri else uri
                          for uri in uris if uri]
                uri_context = f" Domains: {', '.join(domains)}"

            prompt = f"Current name: {current_name}{uri_context}\nDescription: {description}\n\nSuggested name:"

            response = self.client.chat.completions.create(
                model=self.config.model,
                messages=[
                    {"role": "system", "content": self.naming_prompt},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature
            )

            suggested_name = response.choices[0].message.content.strip()
            return suggested_name if suggested_name else current_name

        except Exception as e:
            print(f"AI name suggestion failed: {e}")
            return current_name

    def generate_tags(self, name: str, category: str, description: str = "", uris: List[str] = None) -> Set[str]:
        """Use AI to generate relevant tags for an item."""
        if not self.config.tag_generation_enabled:
            return {category.lower()}

        try:
            # Build context from URIs if available
            uri_context = ""
            if uris:
                domains = [uri.split("://")[-1].split("/")[0] if "://" in uri else uri
                          for uri in uris if uri]
                uri_context = f" Domains: {', '.join(domains)}"

            prompt = f"Name: {name}\nCategory: {category}{uri_context}\nDescription: {description}\n\nTags:"

            response = self.client.chat.completions.create(
                model=self.config.model,
                messages=[
                    {"role": "system", "content": self.tagging_prompt},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature
            )

            tags_text = response.choices[0].message.content.strip()
            if tags_text:
                tags = {tag.strip().lower() for tag in tags_text.split(",")}
                tags.add(category.lower())  # Always include category as a tag
                return tags
            else:
                return {category.lower()}

        except Exception as e:
            print(f"AI tag generation failed: {e}")
            return {category.lower()}

    def batch_process(self, items: List[Dict], batch_size: int = 10) -> List[Dict]:
        """Process items in batches to optimize API usage."""
        processed_items = []

        for i in range(0, len(items), batch_size):
            batch = items[i:i + batch_size]
            print(f"Processing AI batch {i//batch_size + 1}/{(len(items) + batch_size - 1)//batch_size}")

            for item in batch:
                try:
                    # Extract item information
                    name = item.get("name", "")
                    description = item.get("notes", "")
                    uris = []
                    if item.get("login") and item.get("login", {}).get("uris"):
                        uris = [uri.get("uri", "") for uri in item["login"]["uris"] if uri.get("uri")]

                    # Use AI for categorization
                    category = self.categorize_item(name, description, uris)

                    # Use AI for name suggestion
                    suggested_name = self.suggest_name(name, description, uris)

                    # Use AI for tag generation
                    tags = self.generate_tags(name, category, description, uris)

                    # Update item with AI suggestions
                    processed_item = item.copy()
                    if suggested_name != name:
                        processed_item["name"] = suggested_name

                    # Add AI metadata
                    if "notes" not in processed_item:
                        processed_item["notes"] = ""

                    ai_metadata = f"AI Category: {category}\nAI Tags: {', '.join(sorted(tags))}\n"
                    processed_item["notes"] = f"{ai_metadata}\n{processed_item['notes']}".strip()

                    # Add tags as custom fields
                    if tags:
                        fields = processed_item.get("fields", [])
                        labels_field = next((f for f in fields if f.get("name") == "ai_labels"), None)
                        if labels_field:
                            labels_field["value"] = ", ".join(sorted(tags))
                        else:
                            labels_field = {
                                "name": "ai_labels",
                                "value": ", ".join(sorted(tags)),
                                "type": 0  # Text field
                            }
                            fields.append(labels_field)
                        processed_item["fields"] = fields

                    processed_items.append(processed_item)

                except Exception as e:
                    print(f"Failed to process item {item.get('name', 'Unknown')}: {e}")
                    processed_items.append(item)  # Keep original item on failure

        return processed_items
