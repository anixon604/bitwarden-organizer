#!/usr/bin/env python3
"""
Test script to demonstrate validation error scenarios.

This script creates sample data with intentional issues to show
how the validation script reports problems.
"""

import json
import tempfile
import os
from pathlib import Path
from validate_bitwarden_export import BitwardenValidator


def create_problematic_data():
    """Create sample data with intentional validation issues."""

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

    # Sample output data with PROBLEMS (missing item, modified data, lost notes)
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
                # NOTE: Notes were lost here!
                "tags": ["email", "personal"],
                "creationDate": "2024-01-01T00:00:00.000Z",
                "revisionDate": "2024-01-01T00:00:00.000Z"
            }
            # NOTE: Bank Account item is missing!
        ]
    }

    return input_data, output_data


def test_validation_errors():
    """Test the validation functionality with problematic data."""

    print("🧪 Testing Bitwarden validation script with ERROR scenarios...")
    print()

    # Create problematic data
    input_data, output_data = create_problematic_data()

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

        print("⚠️  This test data has INTENTIONAL problems:")
        print("   - Missing 1 item (Bank Account)")
        print("   - Lost notes for Gmail item")
        print("   - Item count mismatch (3 → 2)")
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
    test_validation_errors()
