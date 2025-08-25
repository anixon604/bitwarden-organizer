#!/usr/bin/env python3
"""
Test script for the Bitwarden validation script.

This script creates sample input and output files to test the validation functionality.
"""

import json
import tempfile
import os
from pathlib import Path
from validate_bitwarden_export import BitwardenValidator


def create_sample_bitwarden_data():
    """Create sample Bitwarden export data."""

    # Sample input data (original export)
    input_data = {
        "encrypted": False,
        "folders": [],
        "items": [
            {
                "id": "1",
                "name": "GitHub",
                "type": 1,
                "login": {
                    "username": "user1",
                    "password": "pass123",
                    "uris": [{"uri": "https://github.com"}]
                },
                "notes": "GitHub account",
                "creationDate": "2024-01-01T00:00:00.000Z",
                "revisionDate": "2024-01-01T00:00:00.000Z"
            },
            {
                "id": "2",
                "name": "Gmail",
                "type": 1,
                "login": {
                    "username": "user2@gmail.com",
                    "password": "pass456",
                    "uris": [{"uri": "https://gmail.com"}]
                },
                "notes": "Personal email",
                "creationDate": "2024-01-01T00:00:00.000Z",
                "revisionDate": "2024-01-01T00:00:00.000Z"
            },
            {
                "id": "3",
                "name": "Bank Account",
                "type": 1,
                "login": {
                    "username": "user3",
                    "password": "pass789",
                    "uris": [{"uri": "https://mybank.com"}]
                },
                "notes": "Online banking",
                "creationDate": "2024-01-01T00:00:00.000Z",
                "revisionDate": "2024-01-01T00:00:00.000Z"
            }
        ]
    }

    # Sample output data (organized export)
    output_data = {
        "encrypted": False,
        "folders": [
            {
                "id": "folder1",
                "name": "Developer",
                "revisionDate": "2024-01-01T00:00:00.000Z"
            },
            {
                "id": "folder2",
                "name": "Email",
                "revisionDate": "2024-01-01T00:00:00.000Z"
            },
            {
                "id": "folder3",
                "name": "Finance",
                "revisionDate": "2024-01-01T00:00:00.000Z"
            }
        ],
        "items": [
            {
                "id": "1",
                "name": "GitHub - Development Platform",
                "type": 1,
                "folderId": "folder1",
                "login": {
                    "username": "user1",
                    "password": "pass123",
                    "uris": [{"uri": "https://github.com"}]
                },
                "notes": "GitHub account\n\nCategory: Developer\nTags: dev, code\nProcessed: 2024-01-01T00:00:00",
                "tags": ["dev", "code"],
                "creationDate": "2024-01-01T00:00:00.000Z",
                "revisionDate": "2024-01-01T00:00:00.000Z"
            },
            {
                "id": "2",
                "name": "Gmail - Personal Email",
                "type": 1,
                "folderId": "folder2",
                "login": {
                    "username": "user2@gmail.com",
                    "password": "pass456",
                    "uris": [{"uri": "https://gmail.com"}]
                },
                "notes": "Personal email\n\nCategory: Email\nTags: email, personal\nProcessed: 2024-01-01T00:00:00",
                "tags": ["email", "personal"],
                "creationDate": "2024-01-01T00:00:00.000Z",
                "revisionDate": "2024-01-01T00:00:00.000Z"
            },
            {
                "id": "3",
                "name": "Bank Account - Online Banking",
                "type": 1,
                "folderId": "folder3",
                "login": {
                    "username": "user3",
                    "password": "pass789",
                    "uris": [{"uri": "https://mybank.com"}]
                },
                "notes": "Online banking\n\nCategory: Finance\nTags: finance, banking\nProcessed: 2024-01-01T00:00:00",
                "tags": ["finance", "banking"],
                "creationDate": "2024-01-01T00:00:00.000Z",
                "revisionDate": "2024-01-01T00:00:00.000Z"
            }
        ]
    }

    return input_data, output_data


def test_validation():
    """Test the validation functionality."""

    print("🧪 Testing Bitwarden validation script...")
    print()

    # Create sample data
    input_data, output_data = create_sample_bitwarden_data()

    # Create temporary files
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(input_data, f, indent=2)
        input_file = f.name

    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(output_data, f, indent=2)
        output_file = f.name

    try:
        print(f"📁 Created temporary files:")
        print(f"   Input:  {input_file}")
        print(f"   Output: {output_file}")
        print()

        # Run validation
        validator = BitwardenValidator(input_file, output_file, verbose=True)
        success = validator.run_validation()

        print()
        print(f"🎯 Validation result: {'✅ PASSED' if success else '❌ FAILED'}")

        return success

    finally:
        # Clean up temporary files
        try:
            os.unlink(input_file)
            os.unlink(output_file)
            print(f"\n🧹 Cleaned up temporary files")
        except:
            pass


if __name__ == "__main__":
    test_validation()
