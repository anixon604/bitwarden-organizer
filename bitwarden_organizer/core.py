"""
Core functionality for organizing Bitwarden exports.

This module contains the main logic for categorizing, tagging, and organizing
Bitwarden password exports.
"""

import copy
import datetime as dt
import json
import re
import uuid
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Set, Tuple
from urllib.parse import urlparse


@dataclass
class OrganizerConfig:
    """Configuration for the Bitwarden organizer."""

    dry_run: bool = False
    verbose: bool = False
    add_metadata: bool = True
    suggest_names: bool = True
    create_folders: bool = True
    add_tags: bool = True


# --- Classification rules ----------------------------------------------------

# Map domain substrings or regex patterns to (category, tags)
CATEGORY_RULES = [
    # Finance / Banking / Crypto
    (r"(paypal|stripe|wise|revolut|americanexpress|chase|barclays|hsbc|capitalone|bofa|coinbase|kraken|binance|ftx|monzo)",
     ("Finance", {"finance"})),
    # Social / Community
    (r"(facebook|instagram|twitter|x\.com|tiktok|snapchat|reddit|discord|slack)",
     ("Social", {"social"})),
    # Developer / Code / CI
    (r"(github|gitlab|bitbucket|docker|heroku|vercel|netlify|sentry|linear|atlassian)",
     ("Developer", {"dev"})),
    # Cloud / Infra
    (r"(aws\.amazon|azure|microsoftonline|gcp|cloud\.google|cloudflare|digitalocean|linode|vultr)",
     ("Cloud", {"cloud"})),
    # Email / Identity
    (r"(gmail|protonmail|fastmail|outlook|live\.com|yahoo)",
     ("Email", {"email"})),
    # Shopping
    (r"(amazon|ebay|aliexpress|walmart|target|bestbuy|newegg|etsy)",
     ("Shopping", {"shopping"})),
    # Government / Utilities
    (r"(gov\.|\.gov|hmrc|irs|uscis|ssa\.gov|dvla|uscourts)",
     ("Government/Utilities", {"gov"})),
    # Travel
    (r"(airbnb|booking|expedia|uber|lyft|delta|united|aa\.com|ryanair|easyjet)",
     ("Travel", {"travel"})),
    # Security
    (r"(yubico|duo|authy|1password|lastpass|bitwarden\.com)",
     ("Security", {"security"})),
]

# TLDs that need 3 labels to capture the registrable domain
THREE_LABEL_TLDS = {
    "co.uk", "gov.uk", "ac.uk",
    "com.au", "com.br", "com.mx", "com.tr",
    "co.jp", "co.nz", "co.za",
}

GENERIC_NAME_PATTERNS = (
    re.compile(r"^\s*(login|website|account)\s*$", re.I),
    re.compile(r"^\s*$"),
)


# --- Helpers -----------------------------------------------------------------

def gen_id() -> str:
    """Generate a new UUID for Bitwarden items."""
    return str(uuid.uuid4())


def is_org_export(data: Dict[str, Any]) -> bool:
    """Check if this is an organization export (has collections)."""
    return isinstance(data, dict) and "collections" in data


def parse_domains(item: Dict[str, Any]) -> List[str]:
    """Return list of normalized domains extracted from item.login.uris[*]."""
    domains = []
    login = item.get("login") or {}
    for u in (login.get("uris") or []):
        uri = (u or {}).get("uri")
        if not uri:
            continue
        host = None
        # Handle raw hosts or URLs
        if "://" in uri:
            try:
                host = urlparse(uri).netloc
            except Exception:
                host = None
        else:
            host = uri

        if host:
            # Normalize domain
            domain = host.lower().strip()
            if domain.startswith("www."):
                domain = domain[4:]
            if domain and domain not in domains:
                # Extract registrable domain
                registrable = get_registrable_domain(domain)
                if registrable and registrable not in domains:
                    domains.append(registrable)

    return domains


def get_registrable_domain(domain: str) -> str:
    """Extract the registrable domain from a full domain."""
    if not domain:
        return ""

    parts = domain.split(".")
    if len(parts) < 2:
        return domain

    # Handle special TLDs that need 3 labels
    if len(parts) >= 3 and ".".join(parts[-2:]) in THREE_LABEL_TLDS:
        return ".".join(parts[-3:])

    # Standard case: last 2 parts
    return ".".join(parts[-2:])


def suggest_item_name(item: Dict[str, Any], domains: List[str]) -> str:
    """Suggest a cleaner name for the item based on domains and content."""
    current_name = item.get("name", "").strip()

    # Skip if name is already good
    if current_name and not any(pattern.match(current_name) for pattern in GENERIC_NAME_PATTERNS):
        return current_name

    # Try to use the most relevant domain
    if domains:
        # Prefer domains with subdomains (more descriptive) over simple domains
        # Sort by: has subdomain (desc), then length, then alphabetical
        def domain_score(domain):
            parts = domain.split(".")
            has_subdomain = len(parts) > 2
            return (not has_subdomain, len(domain), domain)

        best_domain = min(domains, key=domain_score)
        # Use the registrable domain if it's different from the full domain
        registrable = get_registrable_domain(best_domain)
        if registrable and registrable != best_domain:
            return registrable.capitalize()
        return best_domain.capitalize()

    # Fallback to current name or generic
    if current_name and not any(pattern.match(current_name) for pattern in GENERIC_NAME_PATTERNS):
        return current_name
    return "Website"


def categorize_item(domains: List[str]) -> Tuple[str, Set[str]]:
    """Categorize item based on domain patterns and return (category, tags)."""
    all_tags = set()

    for domain in domains:
        for pattern, (category, tags) in CATEGORY_RULES:
            if re.search(pattern, domain, re.I):
                all_tags.update(tags)
                return category, all_tags

    # Default category
    return "General", {"general"}


def enhance_notes(item: Dict[str, Any], domains: List[str], category: str, tags: Set[str]) -> str:
    """Enhance item notes with metadata and tags."""
    current_notes = item.get("notes", "").strip()

    # Build metadata header
    metadata_lines = []

    if domains:
        metadata_lines.append(f"Domains: {', '.join(domains)}")

    if category:
        metadata_lines.append(f"Category: {category}")

    if tags:
        metadata_lines.append(f"Tags: {', '.join(sorted(tags))}")

    metadata_lines.append(f"Processed: {dt.datetime.now().isoformat()}")

    metadata_header = "\n".join(metadata_lines)

    # Combine with existing notes
    if current_notes:
        return f"{metadata_header}\n\n{current_notes}"
    else:
        return metadata_header


def find_or_create_folder(folders: List[Dict[str, Any]], name: str) -> str:
    """Find existing folder or create new one, return folder ID."""
    # Look for existing folder
    for folder in folders:
        if folder.get("name") == name:
            return folder["id"]

    # Create new folder
    folder_id = gen_id()
    new_folder = {
        "id": folder_id,
        "name": name,
        "revisionDate": dt.datetime.now().isoformat()
    }
    folders.append(new_folder)
    return folder_id


def find_or_create_collection(collections: List[Dict[str, Any]], name: str) -> str:
    """Find existing collection or create new one, return collection ID."""
    # Look for existing collection
    for collection in collections:
        if collection.get("name") == name:
            return collection["id"]

    # Create new collection
    collection_id = gen_id()
    new_collection = {
        "id": collection_id,
        "name": name,
        "revisionDate": dt.datetime.now().isoformat()
    }
    collections.append(new_collection)
    return collection_id


def organize_item(
    item: Dict[str, Any],
    folders: List[Dict[str, Any]],
    collections: List[Dict[str, Any]],
    config: OrganizerConfig,
    is_org_vault: bool = False
) -> Dict[str, Any]:
    """Organize a single Bitwarden item."""
    # Create a copy to avoid modifying original
    organized_item = copy.deepcopy(item)

    # Extract domains
    domains = parse_domains(item)

    if not domains:
        return organized_item

    # Categorize and tag
    category, tags = categorize_item(domains)

    # Suggest better name
    if config.suggest_names:
        suggested_name = suggest_item_name(item, domains)
        if suggested_name != item.get("name"):
            organized_item["name"] = suggested_name

    # Add tags as custom field
    if config.add_tags and tags:
        fields = organized_item.get("fields", [])
        # Check if labels field already exists
        labels_field = next((f for f in fields if f.get("name") == "labels"), None)
        if labels_field:
            labels_field["value"] = ", ".join(sorted(tags))
        else:
            labels_field = {
                "name": "labels",
                "value": ", ".join(sorted(tags)),
                "type": 0  # Text field
            }
            fields.append(labels_field)
        organized_item["fields"] = fields

    # Enhance notes
    if config.add_metadata:
        organized_item["notes"] = enhance_notes(item, domains, category, tags)

    # Handle folders (personal vaults) - only if not an organization vault
    if config.create_folders and not is_org_vault:
        folder_name = category
        folder_id = find_or_create_folder(folders, folder_name)
        organized_item["folderId"] = folder_id

    # Handle collections (organization vaults) - only if it is an organization vault
    if is_org_vault and config.create_folders:
        collection_name = category
        collection_id = find_or_create_collection(collections, collection_name)
        organized_item["collectionIds"] = [collection_id]

    return organized_item


def organize_bitwarden_export(
    data: Dict[str, Any],
    config: Optional[OrganizerConfig] = None
) -> Dict[str, Any]:
    """
    Organize a complete Bitwarden export.

    Args:
        data: The Bitwarden export data
        config: Configuration options for the organizer

    Returns:
        Organized Bitwarden export data

    Raises:
        ValueError: If the input data is invalid
    """
    if not isinstance(data, dict):
        raise ValueError("Input data must be a dictionary")

    if config is None:
        config = OrganizerConfig()

    # Create a copy to avoid modifying original
    organized_data = copy.deepcopy(data)

    # Get or create folders and collections
    folders = organized_data.get("folders", [])
    collections = organized_data.get("collections", [])
    items = organized_data.get("items", [])

    if not items:
        return organized_data

    # Determine if this is an organization vault
    is_org_vault = "collections" in organized_data

    # Process each item
    for i, item in enumerate(items):
        try:
            organized_items = organize_item(item, folders, collections, config, is_org_vault)
            items[i] = organized_items
        except Exception as e:
            if config.verbose:
                print(f"Warning: Failed to process item {i}: {e}")
            continue

    # Update the organized data
    organized_data["folders"] = folders
    organized_data["collections"] = collections
    organized_data["items"] = items

    return organized_data
