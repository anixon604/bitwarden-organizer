"""
Tests for the core Bitwarden organizer functionality.
"""

import pytest
from bitwarden_organizer.core import (
    OrganizerConfig,
    organize_bitwarden_export,
    organize_item,
    categorize_item,
    parse_domains,
    suggest_item_name,
    gen_id,
    is_org_export,
)


class TestOrganizerConfig:
    """Test the OrganizerConfig dataclass."""

    def test_default_config(self):
        """Test default configuration values."""
        config = OrganizerConfig()
        assert config.dry_run is False
        assert config.verbose is False
        assert config.add_metadata is True
        assert config.suggest_names is True
        assert config.create_folders is True
        assert config.add_tags is True

    def test_custom_config(self):
        """Test custom configuration values."""
        config = OrganizerConfig(
            dry_run=True,
            verbose=True,
            add_metadata=False,
            suggest_names=False,
            create_folders=False,
            add_tags=False
        )
        assert config.dry_run is True
        assert config.verbose is True
        assert config.add_metadata is False
        assert config.suggest_names is False
        assert config.create_folders is False
        assert config.add_tags is False


class TestHelpers:
    """Test helper functions."""

    def test_gen_id(self):
        """Test UUID generation."""
        id1 = gen_id()
        id2 = gen_id()

        assert isinstance(id1, str)
        assert isinstance(id2, str)
        assert id1 != id2
        assert len(id1) > 0

    def test_is_org_export(self):
        """Test organization export detection."""
        # Personal vault
        personal_data = {"folders": [], "items": []}
        assert is_org_export(personal_data) is False

        # Organization vault
        org_data = {"collections": [], "items": []}
        assert is_org_export(org_data) is True

        # Empty data
        assert is_org_export({}) is False
        assert is_org_export(None) is False


class TestDomainParsing:
    """Test domain parsing functionality."""

    def test_parse_domains_from_urls(self):
        """Test parsing domains from URLs."""
        item = {
            "login": {
                "uris": [
                    {"uri": "https://example.com/login"},
                    {"uri": "https://www.test.org/api"},
                    {"uri": "ftp://old-site.net"}
                ]
            }
        }

        domains = parse_domains(item)
        assert "example.com" in domains
        assert "test.org" in domains
        assert "old-site.net" in domains

    def test_parse_domains_from_hosts(self):
        """Test parsing domains from raw hostnames."""
        item = {
            "login": {
                "uris": [
                    {"uri": "example.com"},
                    {"uri": "www.test.org"},
                    {"uri": "api.service.co.uk"}
                ]
            }
        }

        domains = parse_domains(item)
        assert "example.com" in domains
        assert "test.org" in domains
        assert "service.co.uk" in domains

    def test_parse_domains_empty(self):
        """Test parsing domains from item with no URIs."""
        item = {"login": {}}
        domains = parse_domains(item)
        assert domains == []

        item = {"login": {"uris": []}}
        domains = parse_domains(item)
        assert domains == []

    def test_parse_domains_normalization(self):
        """Test domain normalization (lowercase, no www)."""
        item = {
            "login": {
                "uris": [
                    {"uri": "https://WWW.EXAMPLE.COM"},
                    {"uri": "https://www.test.org"},
                    {"uri": "API.SERVICE.COM"}
                ]
            }
        }

        domains = parse_domains(item)
        assert "example.com" in domains
        assert "test.org" in domains
        assert "service.com" in domains


class TestCategorization:
    """Test item categorization."""

    def test_categorize_finance(self):
        """Test finance category detection."""
        domains = ["paypal.com", "stripe.com", "chase.com"]
        category, tags = categorize_item(domains)
        assert category == "Finance"
        assert "finance" in tags

    def test_categorize_social(self):
        """Test social category detection."""
        domains = ["facebook.com", "twitter.com", "instagram.com"]
        category, tags = categorize_item(domains)
        assert category == "Social"
        assert "social" in tags

    def test_categorize_developer(self):
        """Test developer category detection."""
        domains = ["github.com", "gitlab.com", "docker.com"]
        category, tags = categorize_item(domains)
        assert category == "Developer"
        assert "dev" in tags

    def test_categorize_default(self):
        """Test default category for unknown domains."""
        domains = ["unknown-site.com", "random.org"]
        category, tags = categorize_item(domains)
        assert category == "General"
        assert "general" in tags


class TestNameSuggestion:
    """Test name suggestion functionality."""

    def test_suggest_name_from_domain(self):
        """Test suggesting names from domains."""
        item = {"name": "login"}
        domains = ["example.com", "api.service.org"]

        suggested = suggest_item_name(item, domains)
        assert suggested == "Service.org"

    def test_suggest_name_keep_good_name(self):
        """Test keeping already good names."""
        item = {"name": "My Bank Account"}
        domains = ["bank.com"]

        suggested = suggest_item_name(item, domains)
        assert suggested == "My Bank Account"

    def test_suggest_name_generic_patterns(self):
        """Test replacing generic names."""
        generic_names = ["login", "website", "account", ""]
        domains = ["example.com"]

        for name in generic_names:
            item = {"name": name}
            suggested = suggest_item_name(item, domains)
            assert suggested == "Example.com"

    def test_suggest_name_no_domains(self):
        """Test name suggestion with no domains."""
        item = {"name": "login"}
        domains = []

        suggested = suggest_item_name(item, domains)
        assert suggested == "Website"


class TestItemOrganization:
    """Test individual item organization."""

    def test_organize_item_basic(self):
        """Test basic item organization."""
        item = {
            "id": "test-id",
            "name": "login",
            "login": {
                "uris": [{"uri": "https://github.com/login"}]
            },
            "notes": "Original notes"
        }

        folders = []
        collections = []
        config = OrganizerConfig()

        organized = organize_item(item, folders, collections, config)

        assert organized["name"] == "Github.com"
        assert "github.com" in organized["notes"]
        assert "Category: Developer" in organized["notes"]
        assert "dev" in organized["notes"]
        assert organized["folderId"] is not None
        assert len(folders) == 1
        assert folders[0]["name"] == "Developer"

    def test_organize_item_no_domains(self):
        """Test organizing item with no domains."""
        item = {
            "id": "test-id",
            "name": "No URL item",
            "notes": "No URLs here"
        }

        folders = []
        collections = []
        config = OrganizerConfig()

        organized = organize_item(item, folders, collections, config)

        # Should return unchanged item
        assert organized == item
        assert len(folders) == 0


class TestFullExportOrganization:
    """Test full export organization."""

    def test_organize_empty_export(self):
        """Test organizing empty export."""
        data = {"items": []}
        config = OrganizerConfig()

        result = organize_bitwarden_export(data, config)
        assert result == data

    def test_organize_personal_vault(self):
        """Test organizing personal vault export."""
        data = {
            "folders": [],
            "items": [
                {
                    "id": "item1",
                    "name": "login",
                    "login": {
                        "uris": [{"uri": "https://github.com"}]
                    }
                },
                {
                    "id": "item2",
                    "name": "website",
                    "login": {
                        "uris": [{"uri": "https://paypal.com"}]
                    }
                }
            ]
        }

        config = OrganizerConfig()
        result = organize_bitwarden_export(data, config)

        assert len(result["folders"]) == 2
        assert len(result["items"]) == 2

        # Check folders were created
        folder_names = [f["name"] for f in result["folders"]]
        assert "Developer" in folder_names
        assert "Finance" in folder_names

    def test_organize_org_vault(self):
        """Test organizing organization vault export."""
        data = {
            "collections": [],
            "items": [
                {
                    "id": "item1",
                    "name": "login",
                    "login": {
                        "uris": [{"uri": "https://github.com"}]
                    }
                }
            ]
        }

        config = OrganizerConfig()
        result = organize_bitwarden_export(data, config)

        assert len(result["collections"]) == 1
        assert result["collections"][0]["name"] == "Developer"
        assert result["items"][0]["collectionIds"] == [result["collections"][0]["id"]]

    def test_organize_invalid_input(self):
        """Test organizing with invalid input."""
        config = OrganizerConfig()

        with pytest.raises(ValueError):
            organize_bitwarden_export("not a dict", config)

        with pytest.raises(ValueError):
            organize_bitwarden_export(None, config)
